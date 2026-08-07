import os
import json
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple

from src.data.paths import DATASET_PATHS, SUPPORTED_IMAGE_EXTENSIONS
from src.data.deduplication import compute_file_sha256
from src.data.taxonomy import CanonicalPlant, TaxonomyMapping, MappingStatus
from src.data.taxonomy_review import atomic_json_write

@dataclass
class SourceReference:
    dataset_id: str
    original_class_name: str
    source_file_path: str
    source_file_name: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class CanonicalDatasetRecord:
    record_id: str
    taxonomy_version: str
    canonical_plant_id: str
    canonical_name: str
    health_condition: str  # Healthy, Unhealthy, Unknown
    sha256: str
    file_extension: str
    scientific_name: Optional[str] = None
    source_references: List[SourceReference] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["source_references"] = [s.to_dict() for s in self.source_references]
        return d

class CanonicalDatasetBuilder:
    """
    Manifest-First Canonical Dataset Builder for Dravya AI.
    Generates audit-traceable dataset manifests, readiness reports, and statistics from
    APPROVED taxonomy mappings without modifying or copying raw dataset files.
    """

    def __init__(self, version: str = "v1", reports_dir: str = r"C:\Dravya-AI-Engine\reports\dataset_analysis", dataset_roots: Optional[Dict[str, Path]] = None):
        self.version = version
        self.reports_dir = Path(reports_dir)
        self.dataset_roots = dataset_roots if dataset_roots is not None else DATASET_PATHS
        self.plants: Dict[str, CanonicalPlant] = {}
        self.mappings: List[TaxonomyMapping] = []
        self.records: List[CanonicalDatasetRecord] = []
        self.statistics: Dict[str, Any] = {}
        self.validation_report: Dict[str, Any] = {}

    def load_inputs(self, taxonomy_json_path: Optional[str] = None, mapping_json_path: Optional[str] = None) -> None:
        """
        Loads canonical plants and review mappings from reports directory.
        """
        self.plants = {}
        self.mappings = []

        tax_path = Path(taxonomy_json_path) if taxonomy_json_path else self.reports_dir / f"canonical_taxonomy_{self.version}.json"
        
        if mapping_json_path:
            map_path = Path(mapping_json_path)
        else:
            rev_path = self.reports_dir / f"taxonomy_review_{self.version}.json"
            map_path = rev_path if rev_path.exists() else self.reports_dir / f"taxonomy_mapping_review_{self.version}.json"

        if not tax_path.exists():
            raise FileNotFoundError(f"Canonical taxonomy file not found at: {tax_path}")
        if not map_path.exists():
            raise FileNotFoundError(f"Taxonomy mapping review file not found at: {map_path}")

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
                self.mappings.append(TaxonomyMapping(**m_dict))

    def build_manifest(self, precomputed_hashes: Optional[Dict[str, str]] = None) -> Tuple[List[CanonicalDatasetRecord], Dict[str, Any]]:
        """
        Filters APPROVED mappings and builds canonical dataset records with duplicate SHA-256 consolidation.
        """
        approved_mappings = [m for m in self.mappings if m.mapping_status == MappingStatus.APPROVED]

        if len(approved_mappings) == 0:
            self.records = []
            self.statistics = {
                "status": "BLOCKED",
                "reason": "NO_APPROVED_MAPPINGS",
                "taxonomy_version": self.version,
                "total_approved_mappings": 0,
                "total_unreviewed_mappings": sum(1 for m in self.mappings if m.mapping_status == MappingStatus.UNREVIEWED),
                "total_needs_review_mappings": sum(1 for m in self.mappings if m.mapping_status == MappingStatus.NEEDS_REVIEW),
                "total_rejected_mappings": sum(1 for m in self.mappings if m.mapping_status == MappingStatus.REJECTED),
                "total_canonical_records": 0,
                "unique_images": 0,
                "total_canonical_plants": 0,
                "healthy_count": 0,
                "unhealthy_count": 0,
                "unknown_condition_count": 0,
                "raw_files_scanned": 0,
                "duplicate_consolidation_count": 0,
                "per_plant_counts": {},
                "per_source_counts": {}
            }
            self.validation_report = {
                "is_valid": True,
                "status": "BLOCKED",
                "reason": "NO_APPROVED_MAPPINGS",
                "total_records": 0,
                "errors_count": 0,
                "errors": []
            }
            return self.records, self.statistics

        sha_to_record: Dict[str, CanonicalDatasetRecord] = {}
        raw_files_count = 0

        for m in approved_mappings:
            approved_pid = m.approved_canonical_plant_id
            if not approved_pid or approved_pid not in self.plants:
                raise ValueError(f"Approved mapping '{m.mapping_id}' points to missing or invalid canonical_plant_id '{approved_pid}'.")

            plant = self.plants[approved_pid]
            dataset_root = self.dataset_roots.get(m.source_dataset)
            if not dataset_root or not Path(dataset_root).exists():
                raise FileNotFoundError(f"Source dataset root path for '{m.source_dataset}' not found or not registered.")

            class_dir = Path(dataset_root) / m.original_class_name
            if not class_dir.exists():
                continue

            for root, _, files in os.walk(class_dir):
                for fname in sorted(files):
                    ext = os.path.splitext(fname)[1].lower()
                    if ext not in SUPPORTED_IMAGE_EXTENSIONS:
                        continue

                    raw_files_count += 1
                    file_path = Path(root) / fname
                    rel_path_str = str(file_path)

                    if precomputed_hashes and rel_path_str in precomputed_hashes:
                        file_sha = precomputed_hashes[rel_path_str]
                    else:
                        file_sha = compute_file_sha256(file_path)

                    src_ref = SourceReference(
                        dataset_id=m.source_dataset,
                        original_class_name=m.original_class_name,
                        source_file_path=rel_path_str,
                        source_file_name=fname
                    )

                    if file_sha in sha_to_record:
                        existing_rec = sha_to_record[file_sha]
                        if src_ref not in existing_rec.source_references:
                            existing_rec.source_references.append(src_ref)
                    else:
                        rec_id = f"rec_{self.version}_{len(sha_to_record) + 1:06d}"
                        rec = CanonicalDatasetRecord(
                            record_id=rec_id,
                            taxonomy_version=self.version,
                            canonical_plant_id=approved_pid,
                            canonical_name=plant.canonical_name,
                            scientific_name=plant.scientific_name,
                            health_condition=m.health_condition,
                            sha256=file_sha,
                            file_extension=ext,
                            source_references=[src_ref]
                        )
                        sha_to_record[file_sha] = rec

        self.records = list(sha_to_record.values())

        per_plant: Dict[str, int] = {}
        per_source: Dict[str, int] = {}
        healthy_cnt = 0
        unhealthy_cnt = 0
        unknown_cnt = 0

        for r in self.records:
            per_plant[r.canonical_plant_id] = per_plant.get(r.canonical_plant_id, 0) + 1
            if r.health_condition == "Healthy":
                healthy_cnt += 1
            elif r.health_condition == "Unhealthy":
                unhealthy_cnt += 1
            else:
                unknown_cnt += 1

            for s in r.source_references:
                per_source[s.dataset_id] = per_source.get(s.dataset_id, 0) + 1

        self.statistics = {
            "status": "SUCCESS",
            "reason": "APPROVED_MAPPINGS_PROCESSED",
            "taxonomy_version": self.version,
            "total_approved_mappings": len(approved_mappings),
            "total_canonical_records": len(self.records),
            "unique_images": len(sha_to_record),
            "total_canonical_plants": len(per_plant),
            "healthy_count": healthy_cnt,
            "unhealthy_count": unhealthy_cnt,
            "unknown_condition_count": unknown_cnt,
            "raw_files_scanned": raw_files_count,
            "duplicate_consolidation_count": raw_files_count - len(self.records),
            "per_plant_counts": per_plant,
            "per_source_counts": per_source
        }

        self.validation_report = self.validate_manifest()
        return self.records, self.statistics

    def generate_readiness_report(self) -> Dict[str, Any]:
        """
        Generates a dry-run readiness report describing the builder state and what WOULD be built.
        Exports artifact to reports/dataset_analysis/canonical_dataset_readiness_v1.json.
        """
        app_count = sum(1 for m in self.mappings if m.mapping_status == MappingStatus.APPROVED)
        unrev_count = sum(1 for m in self.mappings if m.mapping_status == MappingStatus.UNREVIEWED)
        needs_count = sum(1 for m in self.mappings if m.mapping_status == MappingStatus.NEEDS_REVIEW)
        rej_count = sum(1 for m in self.mappings if m.mapping_status == MappingStatus.REJECTED)

        readiness_status = "BLOCKED" if app_count == 0 else "READY"
        status_reason = "NO_APPROVED_MAPPINGS" if app_count == 0 else "APPROVED_MAPPINGS_AVAILABLE"

        report = {
            "taxonomy_version": self.version,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "builder_readiness_status": readiness_status,
            "status_reason": status_reason,
            "total_mappings": len(self.mappings),
            "approved_mappings": app_count,
            "unreviewed_mappings": unrev_count,
            "needs_review_mappings": needs_count,
            "rejected_mappings": rej_count,
            "excluded_mappings_by_status": {
                "UNREVIEWED": unrev_count,
                "NEEDS_REVIEW": needs_count,
                "REJECTED": rej_count
            },
            "eligible_canonical_records": self.statistics.get("total_canonical_records", 0),
            "source_files_would_be_included": self.statistics.get("raw_files_scanned", 0),
            "sha256_duplicate_groups_would_be_consolidated": self.statistics.get("duplicate_consolidation_count", 0),
            "canonical_plants_represented": self.statistics.get("total_canonical_plants", 0),
            "health_condition_distribution": {
                "Healthy": self.statistics.get("healthy_count", 0),
                "Unhealthy": self.statistics.get("unhealthy_count", 0),
                "Unknown": self.statistics.get("unknown_condition_count", 0)
            },
            "missing_source_files_count": self.validation_report.get("errors_count", 0),
            "sha256_mismatch_risks_count": sum(1 for err in self.validation_report.get("errors", []) if "SHA-256 mismatch" in err),
            "invalid_canonical_ids_count": sum(1 for err in self.validation_report.get("errors", []) if "unknown canonical_plant_id" in err)
        }

        readiness_path = self.reports_dir / f"canonical_dataset_readiness_{self.version}.json"
        atomic_json_write(readiness_path, report)
        return report

    def validate_manifest(self) -> Dict[str, Any]:
        """
        Validates canonical dataset records for integrity, missing files, SHA matches, and provenance.
        """
        errors = []
        if self.statistics.get("status") == "BLOCKED":
            return {
                "is_valid": True,
                "status": "BLOCKED",
                "reason": "NO_APPROVED_MAPPINGS",
                "total_records": 0,
                "errors_count": 0,
                "errors": []
            }

        seen_shas = set()
        for r in self.records:
            if r.sha256 in seen_shas:
                errors.append(f"Duplicate canonical record for SHA-256: {r.sha256}")
            seen_shas.add(r.sha256)

            if r.canonical_plant_id not in self.plants:
                errors.append(f"Record '{r.record_id}' references unknown canonical_plant_id: '{r.canonical_plant_id}'")

            if not r.source_references or len(r.source_references) == 0:
                errors.append(f"Record '{r.record_id}' has missing source references.")

            for s in r.source_references:
                sp = Path(s.source_file_path)
                if not sp.exists():
                    errors.append(f"Record '{r.record_id}' references missing source file: '{s.source_file_path}'")
                else:
                    actual_sha = compute_file_sha256(sp)
                    if actual_sha != r.sha256:
                        errors.append(f"Record '{r.record_id}' SHA-256 mismatch for file '{s.source_file_path}': expected {r.sha256}, got {actual_sha}")

        return {
            "is_valid": len(errors) == 0,
            "status": "SUCCESS" if len(errors) == 0 else "INVALID",
            "total_records": len(self.records),
            "errors_count": len(errors),
            "errors": errors
        }

    def export_artifacts(self) -> Dict[str, Path]:
        """
        Exports versioned canonical_dataset_manifest_v1.json, statistics, validation, and readiness reports using atomic writes.
        """
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        manifest_path = self.reports_dir / f"canonical_dataset_manifest_{self.version}.json"
        stats_path = self.reports_dir / f"canonical_dataset_statistics_{self.version}.json"
        val_path = self.reports_dir / f"canonical_dataset_validation_{self.version}.json"
        readiness_path = self.reports_dir / f"canonical_dataset_readiness_{self.version}.json"

        recs_list = [r.to_dict() for r in self.records]

        # 1. Manifest JSON (Atomic)
        atomic_json_write(manifest_path, {
            "taxonomy_version": self.version,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "status": self.statistics.get("status", "BLOCKED"),
            "reason": self.statistics.get("reason", "NO_APPROVED_MAPPINGS"),
            "total_records": len(recs_list),
            "records": recs_list
        })

        # 2. Statistics JSON (Atomic)
        atomic_json_write(stats_path, self.statistics)

        # 3. Validation JSON (Atomic)
        atomic_json_write(val_path, self.validation_report)

        # 4. Readiness Report JSON (Atomic)
        self.generate_readiness_report()

        return {
            "manifest_json": manifest_path,
            "statistics_json": stats_path,
            "validation_json": val_path,
            "readiness_json": readiness_path
        }

    def format_terminal_summary(self) -> str:
        s = self.statistics
        val = self.validation_report
        lines = [
            "==========================================================================",
            f"       DRAVYA AI CANONICAL DATASET BUILDER SUMMARY ({self.version})       ",
            "==========================================================================",
            f"Taxonomy Version:                    {self.version}",
            f"Builder Status:                      {s.get('status', 'BLOCKED')}",
            f"Status Reason:                       {s.get('reason', 'NO_APPROVED_MAPPINGS')}",
            f"Total Approved Mappings:             {s.get('total_approved_mappings', 0)}",
            f"Total Canonical Records Generated:   {s.get('total_canonical_records', 0)}",
            f"Unique Images (SHA-256):            {s.get('unique_images', 0)}",
            f"Canonical Plants Represented:       {s.get('total_canonical_plants', 0)}",
            f"  - Healthy Images:                  {s.get('healthy_count', 0)}",
            f"  - Unhealthy Images:                {s.get('unhealthy_count', 0)}",
            f"  - Unknown Health Images:           {s.get('unknown_condition_count', 0)}",
            f"Raw Source Files Scanned:            {s.get('raw_files_scanned', 0)}",
            f"Duplicate Consolidation Count:       {s.get('duplicate_consolidation_count', 0)}",
            "--------------------------------------------------------------------------",
            f"Validation Status:                   {'PASSED (100% VALID)' if val.get('is_valid') else 'FAILED'}",
            f"Validation Errors Count:             {val.get('errors_count', 0)}",
            "=========================================================================="
        ]
        return "\n".join(lines)
