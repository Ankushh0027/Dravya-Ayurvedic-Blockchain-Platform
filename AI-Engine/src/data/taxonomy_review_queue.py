import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from src.data.taxonomy import CanonicalPlant, TaxonomyMapping, MappingStatus
from src.data.taxonomy_review import TaxonomyReviewEngine, ReviewDecision, ReviewDecisionAction

@dataclass
class ReviewQueueItem:
    mapping_id: str
    source_dataset: str
    original_class_name: str
    normalized_name: str
    candidate_canonical_plant_id: Optional[str]
    candidate_canonical_name: Optional[str]
    health_condition: str
    confidence: str
    match_reason: str
    evidence: str
    current_mapping_status: str
    review_history: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class TaxonomyReviewQueue:
    """
    Production-grade Taxonomy Review Queue Engine for Dravya AI.
    Exposes filterable queue views, deterministic progress metrics, and review context for human audit.
    """
    def __init__(self, version: str = "v1", reports_dir: str = r"C:\Dravya-AI-Engine\reports\dataset_analysis"):
        self.version = version
        self.reports_dir = Path(reports_dir)
        self.engine = TaxonomyReviewEngine(version=self.version, reports_dir=str(self.reports_dir))
        self.items: List[ReviewQueueItem] = []
        self._load_queue()

    def _load_queue(self):
        self.engine.load_state()
        self.items = []

        # Build queue items in deterministic mapping_id order
        for m_id in sorted(self.engine.mappings.keys()):
            m = self.engine.mappings[m_id]
            
            # Lookup candidate plant details
            c_plant = self.engine.plants.get(m.candidate_canonical_plant_id) if m.candidate_canonical_plant_id else None
            c_name = c_plant.canonical_name if c_plant else None

            # Filter relevant audit history for this mapping
            m_history = [h.to_dict() for h in self.engine.history if h.mapping_id == m_id]

            status_str = m.mapping_status.value if isinstance(m.mapping_status, MappingStatus) else str(m.mapping_status)

            item = ReviewQueueItem(
                mapping_id=m.mapping_id,
                source_dataset=m.source_dataset,
                original_class_name=m.original_class_name,
                normalized_name=m.normalized_name,
                candidate_canonical_plant_id=m.candidate_canonical_plant_id,
                candidate_canonical_name=c_name,
                health_condition=m.health_condition,
                confidence=m.confidence,
                match_reason=m.match_reason,
                evidence=m.evidence or "",
                current_mapping_status=status_str,
                review_history=m_history
            )
            self.items.append(item)

    def reload(self):
        self._load_queue()

    def get_all(self) -> List[ReviewQueueItem]:
        return list(self.items)

    def get_unreviewed(self) -> List[ReviewQueueItem]:
        return [item for item in self.items if item.current_mapping_status == MappingStatus.UNREVIEWED.value]

    def get_needs_review(self) -> List[ReviewQueueItem]:
        return [item for item in self.items if item.current_mapping_status == MappingStatus.NEEDS_REVIEW.value]

    def get_pending(self) -> List[ReviewQueueItem]:
        return [item for item in self.items if item.current_mapping_status in (MappingStatus.UNREVIEWED.value, MappingStatus.NEEDS_REVIEW.value)]

    def get_by_dataset(self, dataset_id: str) -> List[ReviewQueueItem]:
        return [item for item in self.items if item.source_dataset.lower() == dataset_id.lower()]

    def get_by_status(self, status: str) -> List[ReviewQueueItem]:
        return [item for item in self.items if item.current_mapping_status.upper() == status.upper()]

    def get_by_mapping_id(self, mapping_id: str) -> Optional[ReviewQueueItem]:
        for item in self.items:
            if item.mapping_id == mapping_id:
                return item
        return None

    def get_next(self) -> Optional[ReviewQueueItem]:
        pending = self.get_pending()
        return pending[0] if pending else None

    def get_progress_summary(self) -> Dict[str, Any]:
        total = len(self.items)
        unreviewed = len(self.get_unreviewed())
        needs_review = len(self.get_needs_review())
        approved = sum(1 for item in self.items if item.current_mapping_status == MappingStatus.APPROVED.value)
        rejected = sum(1 for item in self.items if item.current_mapping_status == MappingStatus.REJECTED.value)

        reviewed = approved + rejected
        pending = unreviewed + needs_review

        progress_pct = (reviewed / total * 100.0) if total > 0 else 0.0
        approval_rate = (approved / reviewed * 100.0) if reviewed > 0 else 0.0
        rejection_rate = (rejected / reviewed * 100.0) if reviewed > 0 else 0.0

        by_dataset: Dict[str, Dict[str, int]] = {}
        for item in self.items:
            ds = item.source_dataset
            by_dataset.setdefault(ds, {"total": 0, "UNREVIEWED": 0, "NEEDS_REVIEW": 0, "APPROVED": 0, "REJECTED": 0})
            by_dataset[ds]["total"] += 1
            by_dataset[ds][item.current_mapping_status] = by_dataset[ds].get(item.current_mapping_status, 0) + 1

        by_health: Dict[str, Dict[str, int]] = {}
        for item in self.items:
            hc = item.health_condition
            by_health.setdefault(hc, {"total": 0, "UNREVIEWED": 0, "NEEDS_REVIEW": 0, "APPROVED": 0, "REJECTED": 0})
            by_health[hc]["total"] += 1
            by_health[hc][item.current_mapping_status] = by_health[hc].get(item.current_mapping_status, 0) + 1

        by_reviewer: Dict[str, Dict[str, int]] = {}
        for h in self.engine.history:
            rev_id = h.reviewer_id
            by_reviewer.setdefault(rev_id, {"total_decisions": 0, "APPROVED": 0, "REJECTED": 0, "NEEDS_REVIEW": 0})
            by_reviewer[rev_id]["total_decisions"] += 1
            act_str = h.decision.value if isinstance(h.decision, ReviewDecisionAction) else str(h.decision)
            by_reviewer[rev_id][act_str] = by_reviewer[rev_id].get(act_str, 0) + 1

        # Calculate candidate plant group metrics
        plant_to_statuses: Dict[str, List[str]] = {}
        for item in self.items:
            pid = item.candidate_canonical_plant_id or "UNMAPPED"
            plant_to_statuses.setdefault(pid, []).append(item.current_mapping_status)

        total_groups = len(plant_to_statuses)
        fully_reviewed_groups = sum(1 for st_list in plant_to_statuses.values() if all(s in (MappingStatus.APPROVED.value, MappingStatus.REJECTED.value) for s in st_list))
        pending_groups = total_groups - fully_reviewed_groups

        # Session Metrics
        from src.data.review_session import ReviewSessionManager
        sm = ReviewSessionManager(version=self.version, reports_dir=str(self.reports_dir))
        session_metrics = sm.get_summary_metrics()

        return {
            "taxonomy_version": self.version,
            "total_mappings": total,
            "counts_by_status": {
                "UNREVIEWED": unreviewed,
                "NEEDS_REVIEW": needs_review,
                "APPROVED": approved,
                "REJECTED": rejected
            },
            "counts_by_dataset": by_dataset,
            "counts_by_health_condition": by_health,
            "counts_by_reviewer": by_reviewer,
            "candidate_group_metrics": {
                "total_candidate_groups": total_groups,
                "fully_reviewed_groups": fully_reviewed_groups,
                "pending_groups": pending_groups
            },
            "active_sessions": session_metrics["active_sessions"],
            "paused_sessions": session_metrics["paused_sessions"],
            "completed_sessions": session_metrics["completed_sessions"],
            "abandoned_sessions": session_metrics["abandoned_sessions"],
            "progress_by_reviewer": session_metrics["progress_by_reviewer"],
            "reviewed_count": reviewed,
            "pending_count": pending,
            "progress_percent": round(progress_pct, 2),
            "approval_rate": round(approval_rate, 2),
            "rejection_rate": round(rejection_rate, 2),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

    def export_progress_report(self) -> Path:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        report_path = self.reports_dir / f"taxonomy_review_progress_{self.version}.json"
        summary_data = self.get_progress_summary()
        from src.data.taxonomy_review import atomic_json_write
        atomic_json_write(report_path, summary_data)
        return report_path

    def format_terminal_progress(self) -> str:
        s = self.get_progress_summary()
        c_status = s["counts_by_status"]

        lines = [
            "============================================================",
            f"DRAVYA AI TAXONOMY REVIEW PROGRESS ({self.version})",
            "============================================================",
            f"Total mappings:              {s['total_mappings']}",
            f"UNREVIEWED:                  {c_status['UNREVIEWED']}",
            f"NEEDS_REVIEW:               {c_status['NEEDS_REVIEW']}",
            f"APPROVED:                    {c_status['APPROVED']}",
            f"REJECTED:                    {c_status['REJECTED']}",
            "",
            f"Reviewed:                    {s['reviewed_count']} / {s['total_mappings']}",
            f"Progress:                    {s['progress_percent']:.2f}%",
            "",
            "By Dataset:"
        ]
        for ds, ds_counts in sorted(s["counts_by_dataset"].items()):
            lines.append(f"  {ds:<26}: Total: {ds_counts['total']:<4} | Appr: {ds_counts.get('APPROVED',0):<4} | Rej: {ds_counts.get('REJECTED',0):<4} | Pend: {ds_counts.get('UNREVIEWED',0)+ds_counts.get('NEEDS_REVIEW',0):<4}")

        lines.append("")
        lines.append("By Health:")
        for hc, hc_counts in sorted(s["counts_by_health_condition"].items()):
            lines.append(f"  {hc:<26}: Total: {hc_counts['total']:<4} | Appr: {hc_counts.get('APPROVED',0):<4} | Rej: {hc_counts.get('REJECTED',0):<4} | Pend: {hc_counts.get('UNREVIEWED',0)+hc_counts.get('NEEDS_REVIEW',0):<4}")

        lines.append("============================================================")
        return "\n".join(lines)
