import os
import json
import uuid
from enum import Enum
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from src.data.taxonomy import CanonicalPlant, TaxonomyMapping, MappingStatus
from src.data.taxonomy_validator import TaxonomyValidator

def atomic_json_write(filepath: Path, data: Any) -> None:
    """
    Safely writes JSON data to a temporary file before atomically replacing the target file.
    Prevents corrupted or partial file writes upon unexpected process termination.
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    temp_path = filepath.with_suffix(filepath.suffix + ".tmp")
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    temp_path.replace(filepath)

class ReviewDecisionAction(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    NEEDS_REVIEW = "NEEDS_REVIEW"

@dataclass
class ReviewDecision:
    mapping_id: str
    taxonomy_version: str
    reviewer_id: str
    decision: ReviewDecisionAction
    previous_status: MappingStatus
    decision_id: str = field(default_factory=lambda: f"dec_{uuid.uuid4().hex[:10]}")
    candidate_canonical_plant_id: Optional[str] = None
    approved_canonical_plant_id: Optional[str] = None
    original_source_dataset: Optional[str] = None
    original_class_name: Optional[str] = None
    health_condition: Optional[str] = None
    new_status: Optional[str] = None
    review_reason: str = ""
    evidence: str = ""
    reviewed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["decision"] = self.decision.value if isinstance(self.decision, ReviewDecisionAction) else str(self.decision)
        d["previous_status"] = self.previous_status.value if isinstance(self.previous_status, MappingStatus) else str(self.previous_status)
        return d

class TaxonomyReviewEngine:
    """
    Production-grade human review engine for taxonomy mappings.
    Executes audit-logged review decisions (APPROVE, REJECT, NEEDS_REVIEW) with strict validation,
    append-only history tracking, and atomic state updates.
    """

    def __init__(self, version: str = "v1", reports_dir: str = r"C:\Dravya-AI-Engine\reports\dataset_analysis"):
        self.version = version
        self.reports_dir = Path(reports_dir)
        self.plants: Dict[str, CanonicalPlant] = {}
        self.mappings: Dict[str, TaxonomyMapping] = {}
        self.history: List[ReviewDecision] = []

    def load_state(self, taxonomy_json_path: Optional[str] = None, mappings_json_path: Optional[str] = None) -> None:
        """
        Loads canonical plants, taxonomy mappings, and audit history from reports directory.
        Detects and validates history records against malformed entries.
        """
        self.plants = {}
        self.mappings = {}
        self.history = []

        tax_path = Path(taxonomy_json_path) if taxonomy_json_path else self.reports_dir / f"canonical_taxonomy_{self.version}.json"
        
        if mappings_json_path:
            map_path = Path(mappings_json_path)
        else:
            rev_path = self.reports_dir / f"taxonomy_review_{self.version}.json"
            init_path = self.reports_dir / f"taxonomy_mapping_review_{self.version}.json"
            map_path = rev_path if rev_path.exists() else init_path

        hist_path = self.reports_dir / f"taxonomy_review_history_{self.version}.json"

        if not tax_path.exists():
            raise FileNotFoundError(f"Canonical taxonomy file not found: {tax_path}")
        if not map_path.exists():
            raise FileNotFoundError(f"Taxonomy mapping file not found: {map_path}")

        # 1. Load Canonical Plants
        with open(tax_path, "r", encoding="utf-8") as f:
            tax_data = json.load(f)
            for p_dict in tax_data.get("plants", []):
                plant = CanonicalPlant(**p_dict)
                self.plants[plant.canonical_plant_id] = plant

        # 2. Load Mappings
        with open(map_path, "r", encoding="utf-8") as f:
            map_data = json.load(f)
            for m_dict in map_data.get("mappings", []):
                m_dict["mapping_status"] = MappingStatus(m_dict["mapping_status"])
                mapping = TaxonomyMapping(**m_dict)
                self.mappings[mapping.mapping_id] = mapping

        # 3. Load Audit History if present, checking for malformed entries
        if hist_path.exists():
            with open(hist_path, "r", encoding="utf-8") as f:
                try:
                    hist_data = json.load(f)
                except Exception as e:
                    raise ValueError(f"Malformed audit history file '{hist_path}': JSON parse error: {e}")

                history_records = hist_data.get("history", [])
                for idx, h_dict in enumerate(history_records, 1):
                    # Check mandatory fields for history integrity
                    if not isinstance(h_dict, dict) or "mapping_id" not in h_dict or "reviewer_id" not in h_dict or "decision" not in h_dict:
                        raise ValueError(f"Malformed audit history entry at index {idx}: missing required fields.")
                    
                    try:
                        h_dict["decision"] = ReviewDecisionAction(h_dict["decision"])
                        h_dict["previous_status"] = MappingStatus(h_dict["previous_status"])
                    except Exception as e:
                        raise ValueError(f"Malformed audit history enum at index {idx}: {e}")

                    self.history.append(ReviewDecision(**h_dict))

    def apply_decision(self, decision: ReviewDecision) -> TaxonomyMapping:
        """
        Applies a review decision (APPROVE, REJECT, NEEDS_REVIEW) with strict validation.
        Logs decision to history log and updates mapping state safely.
        """
        if not decision.reviewer_id or not str(decision.reviewer_id).strip():
            raise ValueError("Review decision requires a non-empty reviewer_id.")

        reason_or_evidence = (decision.review_reason or decision.evidence or "").strip()
        if not reason_or_evidence:
            raise ValueError("Review decision requires a non-empty review_reason or evidence.")

        if decision.mapping_id not in self.mappings:
            raise KeyError(f"Mapping ID '{decision.mapping_id}' not found in review engine.")

        mapping = self.mappings[decision.mapping_id]

        # Populate decision metadata if missing
        decision.original_source_dataset = mapping.source_dataset
        decision.original_class_name = mapping.original_class_name
        decision.health_condition = mapping.health_condition
        decision.candidate_canonical_plant_id = mapping.candidate_canonical_plant_id

        # Preserve original class name, dataset, and health condition
        orig_class = mapping.original_class_name
        orig_dataset = mapping.source_dataset
        orig_health = mapping.health_condition

        act = decision.decision if isinstance(decision.decision, ReviewDecisionAction) else ReviewDecisionAction(decision.decision)

        if act == ReviewDecisionAction.APPROVE:
            approved_id = decision.approved_canonical_plant_id or decision.candidate_canonical_plant_id
            if not approved_id or not str(approved_id).strip():
                raise ValueError("APPROVE decision requires a valid non-empty approved_canonical_plant_id.")

            if approved_id not in self.plants:
                raise ValueError(f"Approved canonical plant ID '{approved_id}' does not exist in canonical taxonomy.")

            # Check for duplicate APPROVED mappings for same (source_dataset, original_class_name)
            for m_id, m in self.mappings.items():
                if m_id != mapping.mapping_id and m.source_dataset == orig_dataset and m.original_class_name == orig_class:
                    if m.mapping_status == MappingStatus.APPROVED:
                        raise ValueError(f"Duplicate APPROVED mapping prevented: '{orig_dataset}:{orig_class}' is already approved under mapping '{m_id}'.")

            mapping.mapping_status = MappingStatus.APPROVED
            mapping.approved_canonical_plant_id = approved_id
            mapping.reviewer = decision.reviewer_id
            mapping.reviewed_at = decision.reviewed_at
            mapping.evidence = reason_or_evidence
            decision.new_status = MappingStatus.APPROVED.value

        elif act == ReviewDecisionAction.REJECT:
            mapping.mapping_status = MappingStatus.REJECTED
            mapping.approved_canonical_plant_id = None
            mapping.reviewer = decision.reviewer_id
            mapping.reviewed_at = decision.reviewed_at
            mapping.evidence = reason_or_evidence
            decision.new_status = MappingStatus.REJECTED.value

        elif act == ReviewDecisionAction.NEEDS_REVIEW:
            mapping.mapping_status = MappingStatus.NEEDS_REVIEW
            mapping.approved_canonical_plant_id = None
            mapping.reviewer = decision.reviewer_id
            mapping.reviewed_at = decision.reviewed_at
            mapping.evidence = reason_or_evidence
            decision.new_status = MappingStatus.NEEDS_REVIEW.value

        # Assert preservation invariants
        assert mapping.original_class_name == orig_class, "Original class name was corrupted during review!"
        assert mapping.source_dataset == orig_dataset, "Source dataset was corrupted during review!"
        assert mapping.health_condition == orig_health, "Health condition was corrupted during review!"

        # Log decision to append-only history
        self.history.append(decision)
        return mapping

    def export_artifacts(self) -> Dict[str, Path]:
        """
        Exports latest taxonomy_review_v1.json, taxonomy_review_history_v1.json, and validation report
        using atomic file replacement for crash safety.
        """
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        review_json_path = self.reports_dir / f"taxonomy_review_{self.version}.json"
        history_json_path = self.reports_dir / f"taxonomy_review_history_{self.version}.json"
        val_json_path = self.reports_dir / "mapping_validation_report.json"

        mappings_list = [m.to_dict() for m in self.mappings.values()]
        history_list = [h.to_dict() for h in self.history]

        # 1. Latest Review State JSON (Atomic)
        atomic_json_write(review_json_path, {
            "taxonomy_version": self.version,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "total_mappings": len(mappings_list),
            "unreviewed_count": sum(1 for m in self.mappings.values() if m.mapping_status == MappingStatus.UNREVIEWED),
            "needs_review_count": sum(1 for m in self.mappings.values() if m.mapping_status == MappingStatus.NEEDS_REVIEW),
            "approved_count": sum(1 for m in self.mappings.values() if m.mapping_status == MappingStatus.APPROVED),
            "rejected_count": sum(1 for m in self.mappings.values() if m.mapping_status == MappingStatus.REJECTED),
            "mappings": mappings_list
        })

        # 2. Append-Only History Log JSON (Atomic)
        atomic_json_write(history_json_path, {
            "taxonomy_version": self.version,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "history_records_count": len(history_list),
            "history": history_list
        })

        # 3. System Validation Report (Atomic)
        val_report = TaxonomyValidator.validate_full_system(list(self.plants.values()), list(self.mappings.values()))
        atomic_json_write(val_json_path, val_report)

        return {
            "review_json": review_json_path,
            "history_json": history_json_path,
            "validation_json": val_json_path
        }

    def format_terminal_summary(self, val_report: Dict[str, Any]) -> str:
        approved_cnt = sum(1 for m in self.mappings.values() if m.mapping_status == MappingStatus.APPROVED)
        unreviewed_cnt = sum(1 for m in self.mappings.values() if m.mapping_status == MappingStatus.UNREVIEWED)
        needs_review_cnt = sum(1 for m in self.mappings.values() if m.mapping_status == MappingStatus.NEEDS_REVIEW)
        rejected_cnt = sum(1 for m in self.mappings.values() if m.mapping_status == MappingStatus.REJECTED)

        lines = [
            "==========================================================================",
            f"          DRAVYA AI TAXONOMY HUMAN REVIEW SUMMARY ({self.version})        ",
            "==========================================================================",
            f"Taxonomy Version:                    {self.version}",
            f"Total Mappings in System:            {len(self.mappings)}",
            f"Total Review Decision Log Entries:   {len(self.history)}",
            f"  - UNREVIEWED Mappings:             {unreviewed_cnt}",
            f"  - NEEDS_REVIEW Mappings:           {needs_review_cnt}",
            f"  - APPROVED Mappings:               {approved_cnt}",
            f"  - REJECTED Mappings:               {rejected_cnt}",
            "--------------------------------------------------------------------------",
            f"Validation Status:                   {'PASSED (100% VALID)' if val_report.get('is_valid') else 'FAILED'}",
            f"Validation Errors Count:             {val_report.get('errors_count', 0)}",
            "=========================================================================="
        ]
        return "\n".join(lines)
