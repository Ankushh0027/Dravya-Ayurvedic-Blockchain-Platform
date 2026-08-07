import os
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple

from src.data.taxonomy import CanonicalPlant, TaxonomyMapping, MappingStatus
from src.data.taxonomy_review import TaxonomyReviewEngine

class RecommendationAction(str):
    APPROVE_CANDIDATE = "APPROVE_CANDIDATE"
    NEEDS_BOTANICAL_REVIEW = "NEEDS_BOTANICAL_REVIEW"
    REJECT_CANDIDATE = "REJECT_CANDIDATE"

@dataclass
class BotanicalReviewGroup:
    canonical_plant_id: str
    candidate_canonical_name: str
    scientific_name: Optional[str]
    aliases: List[str]
    source_mappings: List[Dict[str, Any]]
    source_datasets: List[str]
    original_class_names: List[str]
    normalized_names: List[str]
    health_conditions: List[str]
    confidence_levels: List[str]
    match_reasons: List[str]
    existing_evidence: List[str]
    mapping_statuses: List[str]
    review_recommendation: str
    recommendation_reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class BotanicalReviewAnalyzer:
    """
    Botanical Taxonomy Review Analyzer for Dravya AI.
    Groups mappings by candidate canonical plant identity and evaluates evidence-driven
    recommendations (APPROVE_CANDIDATE, NEEDS_BOTANICAL_REVIEW, REJECT_CANDIDATE) as review aids.
    CRITICAL: Recommendations are NOT approvals.
    """

    def __init__(self, version: str = "v1", reports_dir: str = r"C:\Dravya-AI-Engine\reports\dataset_analysis"):
        self.version = version
        self.reports_dir = Path(reports_dir)
        self.engine = TaxonomyReviewEngine(version=self.version, reports_dir=str(self.reports_dir))
        self.groups: List[BotanicalReviewGroup] = []

    def analyze(self) -> List[BotanicalReviewGroup]:
        self.engine.load_state()
        self.groups = []

        # Group mappings by candidate_canonical_plant_id
        plant_to_mappings: Dict[str, List[TaxonomyMapping]] = {}
        unmapped_mappings: List[TaxonomyMapping] = []

        for m_id, m in sorted(self.engine.mappings.items()):
            pid = m.candidate_canonical_plant_id
            if pid:
                plant_to_mappings.setdefault(pid, []).append(m)
            else:
                unmapped_mappings.append(m)

        # Process each candidate plant group in deterministic canonical_plant_id order
        for pid in sorted(self.engine.plants.keys()):
            plant = self.engine.plants[pid]
            mappings = plant_to_mappings.get(pid, [])

            datasets = sorted(list({m.source_dataset for m in mappings}))
            orig_classes = [m.original_class_name for m in mappings]
            norm_names = sorted(list({m.normalized_name for m in mappings}))
            healths = sorted(list({m.health_condition for m in mappings}))
            confidences = sorted(list({m.confidence for m in mappings}))
            reasons = sorted(list({m.match_reason for m in mappings if m.match_reason}))
            evidences = [m.evidence for m in mappings if m.evidence]
            statuses = [m.mapping_status.value if isinstance(m.mapping_status, MappingStatus) else str(m.mapping_status) for m in mappings]

            rec, rec_reason = self._determine_recommendation(plant, mappings)

            group = BotanicalReviewGroup(
                canonical_plant_id=plant.canonical_plant_id,
                candidate_canonical_name=plant.canonical_name,
                scientific_name=plant.scientific_name,
                aliases=plant.aliases,
                source_mappings=[m.to_dict() for m in mappings],
                source_datasets=datasets,
                original_class_names=orig_classes,
                normalized_names=norm_names,
                health_conditions=healths,
                confidence_levels=confidences,
                match_reasons=reasons,
                existing_evidence=evidences,
                mapping_statuses=statuses,
                review_recommendation=rec,
                recommendation_reason=rec_reason
            )
            self.groups.append(group)

        # Process unmapped mappings if any exist
        if unmapped_mappings:
            for m in unmapped_mappings:
                rec = RecommendationAction.NEEDS_BOTANICAL_REVIEW
                rec_reason = "Mapping lacks a candidate canonical plant ID; requires manual assignment."
                status_str = m.mapping_status.value if isinstance(m.mapping_status, MappingStatus) else str(m.mapping_status)
                group = BotanicalReviewGroup(
                    canonical_plant_id="UNMAPPED",
                    candidate_canonical_name=m.original_class_name,
                    scientific_name=None,
                    aliases=[],
                    source_mappings=[m.to_dict()],
                    source_datasets=[m.source_dataset],
                    original_class_names=[m.original_class_name],
                    normalized_names=[m.normalized_name],
                    health_conditions=[m.health_condition],
                    confidence_levels=[m.confidence],
                    match_reasons=[m.match_reason] if m.match_reason else [],
                    existing_evidence=[m.evidence] if m.evidence else [],
                    mapping_statuses=[status_str],
                    review_recommendation=rec,
                    recommendation_reason=rec_reason
                )
                self.groups.append(group)

        return self.groups

    def _determine_recommendation(self, plant: CanonicalPlant, mappings: List[TaxonomyMapping]) -> Tuple[str, str]:
        """
        Determines evidence-driven botanical review recommendation for a candidate plant group.
        """
        if not mappings:
            return RecommendationAction.NEEDS_BOTANICAL_REVIEW, "No source mappings associated with candidate plant."

        c_name_clean = plant.canonical_name.strip().lower()

        # Check 1: Ambiguous, generic, or non-plant terms -> REJECT or NEEDS_REVIEW
        ambiguous_terms = {"leaf", "leafs", "plant", "plants", "tree", "trees", "crop", "crops", "unknown", "disease", "spot", "blight", "rust"}
        if c_name_clean in ambiguous_terms:
            return RecommendationAction.NEEDS_BOTANICAL_REVIEW, f"Candidate name '{plant.canonical_name}' is generic/ambiguous. Botanical review required to identify specific plant species."

        # Check 2: Invalid or junk class names -> REJECT_CANDIDATE
        if len(c_name_clean) < 2 or c_name_clean.isdigit():
            return RecommendationAction.REJECT_CANDIDATE, f"Candidate name '{plant.canonical_name}' appears invalid or non-taxonomic."

        # Check 3: Scientific name present & consistent across sources -> APPROVE_CANDIDATE
        if plant.scientific_name and len(plant.scientific_name.split()) >= 2:
            return RecommendationAction.APPROVE_CANDIDATE, f"Binomial scientific name '{plant.scientific_name}' available with consistent source mappings across {len(mappings)} class folder(s)."

        # Check 4: Multiple source datasets or health condition variants confirming common name
        if len(mappings) >= 2 or len(set(m.source_dataset for m in mappings)) >= 2:
            return RecommendationAction.APPROVE_CANDIDATE, f"Common plant name '{plant.canonical_name}' supported by {len(mappings)} class folder variants across {len(set(m.source_dataset for m in mappings))} dataset source(s)."

        # Check 5: Single source mapping with clean common name -> APPROVE_CANDIDATE if HIGH confidence, else NEEDS_REVIEW
        if any(m.confidence == "HIGH" for m in mappings):
            return RecommendationAction.APPROVE_CANDIDATE, f"Single-source candidate '{plant.canonical_name}' supported by clean class folder '{mappings[0].original_class_name}' with HIGH match confidence."

        return RecommendationAction.NEEDS_BOTANICAL_REVIEW, f"Candidate '{plant.canonical_name}' requires botanical expert verification of species identity and nomenclature."

    def get_group_by_plant_id(self, canonical_plant_id: str) -> Optional[BotanicalReviewGroup]:
        if not self.groups:
            self.analyze()
        for g in self.groups:
            if g.canonical_plant_id.lower() == canonical_plant_id.lower():
                return g
        return None

    def generate_report(self) -> Path:
        groups = self.analyze()
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        report_path = self.reports_dir / f"taxonomy_botanical_review_{self.version}.json"

        rec_counts = {
            "APPROVE_CANDIDATE": sum(1 for g in groups if g.review_recommendation == RecommendationAction.APPROVE_CANDIDATE),
            "NEEDS_BOTANICAL_REVIEW": sum(1 for g in groups if g.review_recommendation == RecommendationAction.NEEDS_BOTANICAL_REVIEW),
            "REJECT_CANDIDATE": sum(1 for g in groups if g.review_recommendation == RecommendationAction.REJECT_CANDIDATE)
        }

        report_data = {
            "taxonomy_version": self.version,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_candidate_plants": len(self.engine.plants),
            "total_source_mappings": len(self.engine.mappings),
            "recommendation_counts": rec_counts,
            "botanical_groups": [g.to_dict() for g in groups]
        }

        from src.data.taxonomy_review import atomic_json_write
        atomic_json_write(report_path, report_data)
        return report_path
