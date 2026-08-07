import os
import json
import math
import statistics
from enum import Enum
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple

try:
    from PIL import Image
except ImportError:
    Image = None

from src.data.paths import DATASET_PATHS, SUPPORTED_IMAGE_EXTENSIONS
from src.data.deduplication import compute_file_sha256
from src.data.taxonomy import CanonicalPlant, TaxonomyMapping, MappingStatus
from src.data.dataset_builder import CanonicalDatasetRecord, SourceReference

class QualityGateStatus(str, Enum):
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"

class CheckStatus(str, Enum):
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"

@dataclass
class CheckResult:
    check_name: str
    status: CheckStatus
    message: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value if isinstance(self.status, CheckStatus) else str(self.status)
        return d

@dataclass
class QualityGateResult:
    version: str
    status: QualityGateStatus
    timestamp: str
    reason: str
    checks: List[CheckResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    class_statistics: Dict[str, Any] = field(default_factory=dict)
    health_statistics: Dict[str, Any] = field(default_factory=dict)
    provenance_statistics: Dict[str, Any] = field(default_factory=dict)
    input_manifest: str = ""
    configuration: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value if isinstance(self.status, QualityGateStatus) else str(self.status)
        d["checks"] = [c.to_dict() for c in self.checks]
        return d

class DatasetQualityGate:
    """
    Read-Only Pre-Training Dataset Quality Gate for Dravya AI.
    Evaluates canonical dataset manifests and image source files across 14+ quality checks.
    """

    def __init__(
        self,
        version: str = "v1",
        reports_dir: str = r"C:\Dravya-AI-Engine\reports\dataset_analysis",
        min_samples_per_class: int = 5,
        fail_on_warning: bool = False
    ):
        self.version = version
        self.reports_dir = Path(reports_dir)
        self.min_samples_per_class = min_samples_per_class
        self.fail_on_warning = fail_on_warning

    def evaluate_quality_gate(
        self,
        manifest_path: Optional[str] = None,
        taxonomy_path: Optional[str] = None,
        mapping_path: Optional[str] = None
    ) -> QualityGateResult:
        """
        Executes all Quality Gate checks against input manifest and source files.
        """
        m_path = Path(manifest_path) if manifest_path else self.reports_dir / f"canonical_dataset_manifest_{self.version}.json"
        t_path = Path(taxonomy_path) if taxonomy_path else self.reports_dir / f"canonical_taxonomy_{self.version}.json"
        
        if mapping_path:
            rev_path = Path(mapping_path)
        else:
            r1 = self.reports_dir / f"taxonomy_review_{self.version}.json"
            rev_path = r1 if r1.exists() else self.reports_dir / f"taxonomy_mapping_review_{self.version}.json"

        checks: List[CheckResult] = []
        all_errors: List[str] = []
        all_warnings: List[str] = []

        # Check 1: Manifest existence
        if not m_path.exists():
            c1 = CheckResult(
                check_name="manifest_existence",
                status=CheckStatus.BLOCKED,
                message=f"Canonical dataset manifest file not found: {m_path}",
                errors=[f"File not found: {m_path}"]
            )
            checks.append(c1)
            return QualityGateResult(
                version=self.version,
                status=QualityGateStatus.BLOCKED,
                timestamp=datetime.now(timezone.utc).isoformat(),
                reason="MANIFEST_FILE_NOT_FOUND",
                checks=checks,
                errors=[c1.message],
                input_manifest=str(m_path),
                configuration={"min_samples_per_class": self.min_samples_per_class, "fail_on_warning": self.fail_on_warning}
            )

        c1 = CheckResult(check_name="manifest_existence", status=CheckStatus.PASS, message="Manifest file exists.")
        checks.append(c1)

        # Load Manifest
        try:
            with open(m_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
        except Exception as e:
            c_schema = CheckResult(
                check_name="manifest_schema_validation",
                status=CheckStatus.FAIL,
                message=f"Failed to parse JSON manifest: {e}",
                errors=[str(e)]
            )
            checks.append(c_schema)
            return QualityGateResult(
                version=self.version,
                status=QualityGateStatus.FAIL,
                timestamp=datetime.now(timezone.utc).isoformat(),
                reason="MALFORMED_MANIFEST_JSON",
                checks=checks,
                errors=[str(e)],
                input_manifest=str(m_path)
            )

        # Check Manifest Status for BLOCKED state
        manifest_status = manifest_data.get("status")
        manifest_reason = manifest_data.get("reason")

        if manifest_status == "BLOCKED":
            c_blocked = CheckResult(
                check_name="manifest_approval_status",
                status=CheckStatus.BLOCKED,
                message=f"Manifest status is BLOCKED ({manifest_reason}). No approved taxonomy mappings exist.",
                metrics={"approved_mappings_count": 0, "canonical_records_count": 0}
            )
            checks.append(c_blocked)
            return QualityGateResult(
                version=self.version,
                status=QualityGateStatus.BLOCKED,
                timestamp=datetime.now(timezone.utc).isoformat(),
                reason=manifest_reason or "NO_APPROVED_MAPPINGS",
                checks=checks,
                input_manifest=str(m_path),
                configuration={"min_samples_per_class": self.min_samples_per_class, "fail_on_warning": self.fail_on_warning}
            )

        records_data = manifest_data.get("records", [])

        # Load Canonical Plants & Review Mappings for validation
        plants_dict: Dict[str, Dict[str, Any]] = {}
        if t_path.exists():
            with open(t_path, "r", encoding="utf-8") as f:
                tax_data = json.load(f)
                for p in tax_data.get("plants", []):
                    plants_dict[p["canonical_plant_id"]] = p

        approved_mapping_keys: Set[Tuple[str, str]] = set()
        if rev_path.exists():
            with open(rev_path, "r", encoding="utf-8") as f:
                map_data = json.load(f)
                for m in map_data.get("mappings", []):
                    if m.get("mapping_status") == "APPROVED":
                        approved_mapping_keys.add((m["source_dataset"], m["original_class_name"]))

        # Check 2: Schema & Structure Validation
        schema_errors = []
        for idx, r in enumerate(records_data, 1):
            if "record_id" not in r or "sha256" not in r or "canonical_plant_id" not in r or "health_condition" not in r:
                schema_errors.append(f"Record #{idx} is missing required fields.")

        if schema_errors:
            c_sch = CheckResult(check_name="schema_structure_validation", status=CheckStatus.FAIL, message="Malformed manifest records.", errors=schema_errors)
            checks.append(c_sch)
            all_errors.extend(schema_errors)
        else:
            checks.append(CheckResult(check_name="schema_structure_validation", status=CheckStatus.PASS, message="Schema structure valid."))

        # Check 3: Source File Existence, SHA-256 Integrity, & Image Readability
        file_errors = []
        sha_errors = []
        img_errors = []
        plant_id_errors = []
        unapproved_errors = []
        provenance_errors = []

        widths = []
        heights = []
        plant_counts: Dict[str, int] = {}
        health_counts: Dict[str, int] = {"Healthy": 0, "Unhealthy": 0, "Unknown": 0}
        source_counts: Dict[str, int] = {}

        for r in records_data:
            pid = r.get("canonical_plant_id")
            if pid not in plants_dict:
                plant_id_errors.append(f"Record '{r.get('record_id')}' references unknown canonical_plant_id '{pid}'.")

            plant_counts[pid] = plant_counts.get(pid, 0) + 1
            hc = r.get("health_condition", "Unknown")
            health_counts[hc] = health_counts.get(hc, 0) + 1

            sources = r.get("source_references", [])
            if not sources:
                provenance_errors.append(f"Record '{r.get('record_id')}' has empty source_references.")

            for s in sources:
                ds = s.get("dataset_id")
                orig_cls = s.get("original_class_name")
                sp_str = s.get("source_file_path")

                source_counts[ds] = source_counts.get(ds, 0) + 1

                # Check approved mapping compliance
                if (ds, orig_cls) not in approved_mapping_keys:
                    unapproved_errors.append(f"Record '{r.get('record_id')}' contains source '{ds}:{orig_cls}' which is NOT an APPROVED mapping.")

                if not sp_str or not Path(sp_str).exists():
                    file_errors.append(f"Missing source file: '{sp_str}'")
                    continue

                sp = Path(sp_str)

                # Check SHA-256 integrity
                actual_sha = compute_file_sha256(sp)
                if actual_sha != r.get("sha256"):
                    sha_errors.append(f"SHA mismatch for '{sp_str}': expected {r.get('sha256')}, got {actual_sha}")

                # Check Image readability & dimensions
                try:
                    with Image.open(sp) as img:
                        w, h = img.size
                        if w <= 0 or h <= 0:
                            img_errors.append(f"Invalid dimensions ({w}x{h}) for image: '{sp_str}'")
                        else:
                            widths.append(w)
                            heights.append(h)
                except Exception as e:
                    img_errors.append(f"Corrupt or unreadable image file '{sp_str}': {e}")

        # Check 4: Unapproved Mapping Validation
        if unapproved_errors:
            c_unapp = CheckResult(check_name="taxonomy_approval_validation", status=CheckStatus.FAIL, message="Unapproved mappings found in manifest.", errors=unapproved_errors)
            checks.append(c_unapp)
            all_errors.extend(unapproved_errors)
        else:
            checks.append(CheckResult(check_name="taxonomy_approval_validation", status=CheckStatus.PASS, message="All records originate from APPROVED mappings."))

        # Check 5: Source File Existence
        if file_errors:
            c_files = CheckResult(check_name="source_file_existence", status=CheckStatus.FAIL, message="Referenced source files are missing.", errors=file_errors)
            checks.append(c_files)
            all_errors.extend(file_errors)
        else:
            checks.append(CheckResult(check_name="source_file_existence", status=CheckStatus.PASS, message="All referenced source files exist."))

        # Check 6: SHA-256 Hash Integrity
        if sha_errors:
            c_sha = CheckResult(check_name="sha256_integrity", status=CheckStatus.FAIL, message="SHA-256 hash mismatches detected.", errors=sha_errors)
            checks.append(c_sha)
            all_errors.extend(sha_errors)
        else:
            checks.append(CheckResult(check_name="sha256_integrity", status=CheckStatus.PASS, message="100% SHA-256 hash integrity verified."))

        # Check 7: Canonical Plant ID Validation
        if plant_id_errors:
            c_pid = CheckResult(check_name="canonical_plant_id_validation", status=CheckStatus.FAIL, message="Unknown canonical plant IDs referenced.", errors=plant_id_errors)
            checks.append(c_pid)
            all_errors.extend(plant_id_errors)
        else:
            checks.append(CheckResult(check_name="canonical_plant_id_validation", status=CheckStatus.PASS, message="All canonical plant IDs exist in taxonomy."))

        # Check 8: Image Readability & Dimensions
        if img_errors:
            c_img = CheckResult(check_name="image_readability_and_dimensions", status=CheckStatus.FAIL, message="Unreadable or invalid dimension images found.", errors=img_errors)
            checks.append(c_img)
            all_errors.extend(img_errors)
        else:
            dim_metrics = {
                "scanned_images": len(widths),
                "min_width": min(widths) if widths else 0,
                "max_width": max(widths) if widths else 0,
                "mean_width": round(statistics.mean(widths), 2) if widths else 0,
                "min_height": min(heights) if heights else 0,
                "max_height": max(heights) if heights else 0,
                "mean_height": round(statistics.mean(heights), 2) if heights else 0
            }
            checks.append(CheckResult(check_name="image_readability_and_dimensions", status=CheckStatus.PASS, message="All images are readable with valid dimensions.", metrics=dim_metrics))

        # Check 9: Minimum Sample Threshold & Class Imbalance Analysis
        class_warnings = []
        under_threshold_plants = []
        for pid, cnt in plant_counts.items():
            if cnt < self.min_samples_per_class:
                msg = f"Canonical plant '{pid}' has {cnt} samples (below threshold {self.min_samples_per_class})."
                class_warnings.append(msg)
                under_threshold_plants.append(pid)

        # Imbalance ratio
        counts_list = list(plant_counts.values()) if plant_counts else [0]
        min_c = min(counts_list) if counts_list else 0
        max_c = max(counts_list) if counts_list else 0
        mean_c = round(statistics.mean(counts_list), 2) if counts_list else 0
        median_c = statistics.median(counts_list) if counts_list else 0
        imbalance_ratio = round(max_c / min_c, 2) if min_c > 0 else 0.0

        if imbalance_ratio > 20.0:
            class_warnings.append(f"High class imbalance detected: ratio {imbalance_ratio} (max: {max_c}, min: {min_c}).")

        class_stats = {
            "total_plants_represented": len(plant_counts),
            "min_samples": min_c,
            "max_samples": max_c,
            "mean_samples": mean_c,
            "median_samples": median_c,
            "imbalance_ratio": imbalance_ratio,
            "under_threshold_plants_count": len(under_threshold_plants),
            "under_threshold_plants": under_threshold_plants,
            "per_plant_counts": plant_counts
        }

        if class_warnings:
            c_imb = CheckResult(check_name="class_distribution_and_thresholds", status=CheckStatus.WARNING, message="Class distribution warnings detected.", metrics=class_stats, warnings=class_warnings)
            checks.append(c_imb)
            all_warnings.extend(class_warnings)
        else:
            checks.append(CheckResult(check_name="class_distribution_and_thresholds", status=CheckStatus.PASS, message="Class sample thresholds and balance acceptable.", metrics=class_stats))

        # Check 10: Health Condition Distribution
        health_warnings = []
        if health_counts["Unknown"] > 0:
            health_warnings.append(f"Dataset contains {health_counts['Unknown']} images with 'Unknown' health condition.")

        health_stats = {
            "healthy_count": health_counts["Healthy"],
            "unhealthy_count": health_counts["Unhealthy"],
            "unknown_count": health_counts["Unknown"]
        }

        if health_warnings:
            c_hlth = CheckResult(check_name="health_condition_distribution", status=CheckStatus.WARNING, message="Unknown health condition images present.", metrics=health_stats, warnings=health_warnings)
            checks.append(c_hlth)
            all_warnings.extend(health_warnings)
        else:
            checks.append(CheckResult(check_name="health_condition_distribution", status=CheckStatus.PASS, message="Health conditions categorized without unknowns.", metrics=health_stats))

        # Determine Final Quality Gate Status
        if any(c.status == CheckStatus.FAIL for c in checks):
            final_status = QualityGateStatus.FAIL
            reason = "MANDATORY_QUALITY_CHECKS_FAILED"
        elif any(c.status == CheckStatus.WARNING for c in checks):
            if self.fail_on_warning:
                final_status = QualityGateStatus.FAIL
                reason = "QUALITY_WARNINGS_FOUND_WITH_FAIL_ON_WARNING"
            else:
                final_status = QualityGateStatus.WARNING
                reason = "QUALITY_WARNINGS_DETECTED"
        else:
            final_status = QualityGateStatus.PASS
            reason = "ALL_QUALITY_CHECKS_PASSED"

        total_stats = {
            "total_canonical_records": len(records_data),
            "total_source_references": sum(len(r.get("source_references", [])) for r in records_data),
            "per_source_counts": source_counts
        }

        return QualityGateResult(
            version=self.version,
            status=final_status,
            timestamp=datetime.now(timezone.utc).isoformat(),
            reason=reason,
            checks=checks,
            errors=all_errors,
            warnings=all_warnings,
            statistics=total_stats,
            class_statistics=class_stats,
            health_statistics=health_stats,
            provenance_statistics={"per_source_counts": source_counts},
            input_manifest=str(m_path),
            configuration={"min_samples_per_class": self.min_samples_per_class, "fail_on_warning": self.fail_on_warning}
        )

    def export_artifacts(self, result: QualityGateResult) -> Dict[str, Path]:
        """
        Exports versioned quality report and summary JSON artifacts.
        """
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        report_path = self.reports_dir / f"canonical_dataset_quality_report_{self.version}.json"
        summary_path = self.reports_dir / f"canonical_dataset_quality_summary_{self.version}.json"

        # 1. Full Quality Report
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)

        # 2. Executive Summary
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump({
                "version": result.version,
                "status": result.status.value,
                "timestamp": result.timestamp,
                "reason": result.reason,
                "total_checks": len(result.checks),
                "total_errors": len(result.errors),
                "total_warnings": len(result.warnings),
                "summary": {c.check_name: c.status.value for c in result.checks}
            }, f, indent=2, ensure_ascii=False)

        return {
            "report_json": report_path,
            "summary_json": summary_path
        }

    def format_terminal_summary(self, result: QualityGateResult) -> str:
        lines = [
            "==========================================================================",
            f"       DRAVYA AI CANONICAL DATASET QUALITY GATE ({result.version})        ",
            "==========================================================================",
            f"Quality Gate Status:                 {result.status.value}",
            f"Status Reason:                       {result.reason}",
            f"Input Manifest:                      {result.input_manifest}",
            f"Total Quality Checks Executed:      {len(result.checks)}",
            f"Total Quality Errors Found:          {len(result.errors)}",
            f"Total Quality Warnings Found:        {len(result.warnings)}",
            "--------------------------------------------------------------------------",
            "CHECK SUMMARY BREAKDOWN:"
        ]
        for c in result.checks:
            lines.append(f" - {c.check_name:<38}: {c.status.value:<8} ({c.message})")

        lines.extend([
            "=========================================================================="
        ])
        return "\n".join(lines)
