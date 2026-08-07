import os
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple


from src.data.taxonomy import (
    CanonicalPlant,
    TaxonomyMapping,
    MappingStatus,
    generate_canonical_plant_id
)
from src.data.taxonomy_validator import TaxonomyValidator

class TaxonomyManager:
    """
    Manages versioned canonical taxonomy entities, human review mappings,
    and validation reports without performing automatic class merges.
    """

    def __init__(self, version: str = "v1", reports_dir: str = r"C:\Dravya-AI-Engine\reports\dataset_analysis"):
        self.version = version
        self.reports_dir = Path(reports_dir)
        self.plants: Dict[str, CanonicalPlant] = {}
        self.mappings: List[TaxonomyMapping] = []

    def build_from_harmonization_json(self, json_path: Optional[str] = None) -> Tuple[List[CanonicalPlant], List[TaxonomyMapping]]:
        """
        Builds initial canonical taxonomy and mapping records from class_harmonization_analysis.json.
        All mappings are initialized as UNREVIEWED or NEEDS_REVIEW.
        """
        if json_path is None:
            json_path = self.reports_dir / "class_harmonization_analysis.json"
        else:
            json_path = Path(json_path)

        if not json_path.exists():
            raise FileNotFoundError(f"Harmonization analysis JSON file not found at: {json_path}")

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        class_entries = data.get("class_entries", [])
        mapping_idx = 1

        for entry in class_entries:
            source_ds = entry["source_dataset"]
            orig_name = entry["original_class_name"]
            comm_name = entry.get("canonical_common_name") or orig_name
            sci_name = entry.get("canonical_scientific_name")
            health = entry.get("health_condition", "Unknown")

            # Generate candidate plant ID deterministically
            plant_name_for_id = comm_name
            candidate_plant_id = generate_canonical_plant_id(plant_name_for_id)

            # Add to candidate plants table if not present
            if candidate_plant_id not in self.plants:
                aliases = [comm_name]
                if sci_name and sci_name not in aliases:
                    aliases.append(sci_name)

                self.plants[candidate_plant_id] = CanonicalPlant(
                    canonical_plant_id=candidate_plant_id,
                    canonical_name=comm_name,
                    common_name=comm_name,
                    scientific_name=sci_name,
                    aliases=aliases,
                    taxonomy_version=self.version
                )

            # Determine initial review status:
            # If candidate matches exist from harmonization analysis, flag as NEEDS_REVIEW, else UNREVIEWED
            candidate_matches = entry.get("candidate_matches", [])
            initial_status = MappingStatus.NEEDS_REVIEW if len(candidate_matches) > 0 else MappingStatus.UNREVIEWED

            confidence = "HIGH" if any(m.get("confidence") == "HIGH" for m in candidate_matches) else ("MEDIUM" if len(candidate_matches) > 0 else "LOW")
            match_reason = candidate_matches[0].get("reason") if len(candidate_matches) > 0 else "initial_inventory_import"

            mapping_record = TaxonomyMapping(
                mapping_id=f"map_{self.version}_{mapping_idx:05d}",
                source_dataset=source_ds,
                original_class_name=orig_name,
                normalized_name=entry.get("canonical_common_name", orig_name).lower(),
                candidate_canonical_plant_id=candidate_plant_id,
                approved_canonical_plant_id=None,  # MUST BE NONE UNTIL HUMAN REVIEW!
                health_condition=health,
                confidence=confidence,
                mapping_status=initial_status,
                match_reason=match_reason,
                evidence=f"Extracted from harmonization analysis. {len(candidate_matches)} candidate overlap(s) detected.",
                reviewer=None,
                reviewed_at=None,
                mapping_version=self.version
            )
            self.mappings.append(mapping_record)
            mapping_idx += 1

        return list(self.plants.values()), self.mappings

    def export_artifacts(self) -> Dict[str, Path]:
        """
        Exports versioned canonical taxonomy, review mappings, and validation reports.
        """
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        taxonomy_json_path = self.reports_dir / f"canonical_taxonomy_{self.version}.json"
        mappings_json_path = self.reports_dir / f"taxonomy_mapping_review_{self.version}.json"
        validation_json_path = self.reports_dir / "mapping_validation_report.json"

        plants_list = [p.to_dict() for p in self.plants.values()]
        mappings_list = [m.to_dict() for m in self.mappings]

        # 1. Taxonomy JSON
        with open(taxonomy_json_path, "w", encoding="utf-8") as f:
            json.dump({
                "taxonomy_version": self.version,
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "total_canonical_plants": len(plants_list),
                "plants": plants_list
            }, f, indent=2, ensure_ascii=False)

        # 2. Mappings Review JSON
        with open(mappings_json_path, "w", encoding="utf-8") as f:
            json.dump({
                "mapping_version": self.version,
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "total_mappings": len(mappings_list),
                "unreviewed_count": sum(1 for m in self.mappings if m.mapping_status == MappingStatus.UNREVIEWED),
                "needs_review_count": sum(1 for m in self.mappings if m.mapping_status == MappingStatus.NEEDS_REVIEW),
                "approved_count": sum(1 for m in self.mappings if m.mapping_status == MappingStatus.APPROVED),
                "rejected_count": sum(1 for m in self.mappings if m.mapping_status == MappingStatus.REJECTED),
                "mappings": mappings_list
            }, f, indent=2, ensure_ascii=False)

        # 3. Validation Report
        val_report = TaxonomyValidator.validate_full_system(list(self.plants.values()), self.mappings)
        with open(validation_json_path, "w", encoding="utf-8") as f:
            json.dump(val_report, f, indent=2, ensure_ascii=False)

        return {
            "taxonomy_json": taxonomy_json_path,
            "mappings_json": mappings_json_path,
            "validation_json": validation_json_path
        }

    def format_terminal_summary(self, val_report: Dict[str, Any]) -> str:
        lines = [
            "==========================================================================",
            f"        DRAVYA AI CANONICAL TAXONOMY & REVIEW SUMMARY ({self.version})       ",
            "==========================================================================",
            f"Taxonomy Version:                    {self.version}",
            f"Total Canonical Plants (Candidate): {len(self.plants)}",
            f"Total Source Mappings:               {len(self.mappings)}",
            f"  - UNREVIEWED Mappings:             {val_report.get('unreviewed_mappings_count', 0)}",
            f"  - NEEDS_REVIEW Mappings:           {val_report.get('needs_review_mappings_count', 0)}",
            f"  - APPROVED Mappings:               {val_report.get('approved_mappings_count', 0)}",
            f"  - REJECTED Mappings:               {val_report.get('rejected_mappings_count', 0)}",
            "--------------------------------------------------------------------------",
            f"Validation Status:                   {'PASSED (100% VALID)' if val_report.get('is_valid') else 'FAILED'}",
            f"Validation Errors Count:             {val_report.get('errors_count', 0)}",
            "=========================================================================="
        ]
        return "\n".join(lines)
