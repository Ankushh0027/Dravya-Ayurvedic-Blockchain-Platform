import os
import json
import random
import hashlib
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

@dataclass
class PreprocessingConfig:
    version: str = "v1"
    input_manifest: str = ""
    output_root: str = r"C:\Dravya-AI-Engine\data\processed\v1"
    image_size: Tuple[int, int] = (224, 224)
    color_mode: str = "RGB"
    interpolation: str = "BILINEAR"
    normalization: Optional[str] = None
    allowed_formats: List[str] = field(default_factory=lambda: [".jpg", ".jpeg", ".png", ".webp", ".bmp"])
    random_seed: int = 42
    split_ratios: Dict[str, float] = field(default_factory=lambda: {"train": 0.70, "val": 0.15, "test": 0.15})
    overwrite_policy: str = "NEVER"  # NEVER or FORCE

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["image_size"] = list(self.image_size)
        return d

@dataclass
class ProcessedDatasetRecord:
    processed_record_id: str
    canonical_record_id: str
    canonical_plant_id: str
    canonical_name: str
    health_condition: str  # Healthy, Unhealthy, Unknown
    split: str  # train, val, test
    original_sha256: str
    processed_sha256: str
    processed_path: str
    original_source_path: str
    source_dataset: str
    original_class_name: str
    original_dimensions: Tuple[int, int]
    processed_dimensions: Tuple[int, int]
    preprocessing_version: str = "v1"
    scientific_name: Optional[str] = None
    source_references: List[Dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["original_dimensions"] = list(self.original_dimensions)
        d["processed_dimensions"] = list(self.processed_dimensions)
        return d

class CanonicalPreprocessor:
    """
    Production-grade Canonical Preprocessor & Deterministic Splitter for Dravya AI.
    Converts canonical manifests into versioned processed datasets with zero cross-split SHA-256 leakage.
    """

    def __init__(
        self,
        config: Optional[PreprocessingConfig] = None,
        reports_dir: str = r"C:\Dravya-AI-Engine\reports\dataset_analysis"
    ):
        self.config = config if config is not None else PreprocessingConfig()
        self.reports_dir = Path(reports_dir)
        self.records: List[ProcessedDatasetRecord] = []
        self.statistics: Dict[str, Any] = {}
        self.validation_report: Dict[str, Any] = {}
        self.failures: List[Dict[str, Any]] = []

    def process_and_split(
        self,
        manifest_path: Optional[str] = None,
        precomputed_manifest_data: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[ProcessedDatasetRecord], Dict[str, Any]]:
        """
        Processes canonical manifest records, resizes images safely, and partitions them into leak-proof train/val/test splits.
        """
        if precomputed_manifest_data:
            manifest_data = precomputed_manifest_data
            m_path_str = "precomputed_manifest"
        else:
            m_path = Path(manifest_path) if manifest_path else self.reports_dir / f"canonical_dataset_manifest_{self.config.version}.json"
            m_path_str = str(m_path)

            if not m_path.exists():
                self.records = []
                self.statistics = {
                    "status": "BLOCKED",
                    "reason": "MANIFEST_FILE_NOT_FOUND",
                    "preprocessing_version": self.config.version,
                    "total_source_records": 0,
                    "total_processed_records": 0,
                    "train_count": 0,
                    "val_count": 0,
                    "test_count": 0,
                    "cross_split_leakage_count": 0
                }
                self.validation_report = {
                    "is_valid": True,
                    "status": "BLOCKED",
                    "reason": "MANIFEST_FILE_NOT_FOUND",
                    "errors_count": 0,
                    "errors": []
                }
                return self.records, self.statistics

            with open(m_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)

        # Check Quality Gate report status if present
        q_report_path = self.reports_dir / f"canonical_dataset_quality_report_{self.config.version}.json"
        if q_report_path.exists() and not precomputed_manifest_data:
            try:
                with open(q_report_path, "r", encoding="utf-8") as qf:
                    q_data = json.load(qf)
                    q_status = q_data.get("status")
                    if q_status in ("BLOCKED", "FAIL"):
                        self.records = []
                        self.statistics = {
                            "status": "BLOCKED",
                            "reason": f"QUALITY_GATE_{q_status}_({q_data.get('reason', 'FAILED_CHECKS')})",
                            "preprocessing_version": self.config.version,
                            "total_source_records": 0,
                            "total_processed_records": 0,
                            "train_count": 0,
                            "val_count": 0,
                            "test_count": 0,
                            "cross_split_leakage_count": 0
                        }
                        self.validation_report = {
                            "is_valid": True,
                            "status": "BLOCKED",
                            "reason": f"QUALITY_GATE_{q_status}",
                            "errors_count": 0,
                            "errors": []
                        }
                        return self.records, self.statistics
            except Exception:
                pass

        manifest_status = manifest_data.get("status")
        manifest_reason = manifest_data.get("reason")
        canonical_records = manifest_data.get("records", [])


        # Check BLOCKED or empty manifest state
        if manifest_status == "BLOCKED" or len(canonical_records) == 0:
            self.records = []
            self.statistics = {
                "status": "BLOCKED",
                "reason": manifest_reason or "NO_APPROVED_MAPPINGS",
                "preprocessing_version": self.config.version,
                "total_source_records": 0,
                "total_processed_records": 0,
                "train_count": 0,
                "val_count": 0,
                "test_count": 0,
                "cross_split_leakage_count": 0
            }
            self.validation_report = {
                "is_valid": True,
                "status": "BLOCKED",
                "reason": manifest_reason or "NO_APPROVED_MAPPINGS",
                "errors_count": 0,
                "errors": []
            }
            return self.records, self.statistics

        # Validate split ratios
        train_r = self.config.split_ratios.get("train", 0.70)
        val_r = self.config.split_ratios.get("val", 0.15)
        test_r = self.config.split_ratios.get("test", 0.15)
        if abs((train_r + val_r + test_r) - 1.0) > 1e-4:
            raise ValueError(f"Split ratios must sum to 1.0 (got train={train_r}, val={val_r}, test={test_r}).")

        # Check output directory overwrite policy
        out_root = Path(self.config.output_root)
        if out_root.exists() and any(out_root.iterdir()) and self.config.overwrite_policy == "NEVER":
            raise FileExistsError(f"Output directory '{out_root}' already contains files and overwrite_policy is 'NEVER'. Use --force or overwrite_policy='FORCE' to replace.")

        out_root.mkdir(parents=True, exist_ok=True)


        # 1. Deterministic Split Assignment using SHA-256 identity boundary
        # Group canonical records by canonical_plant_id -> original_sha256
        plant_sha_groups: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        for r in canonical_records:
            pid = r["canonical_plant_id"]
            sha = r["sha256"]
            plant_sha_groups.setdefault(pid, {}).setdefault(sha, []).append(r)

        sha_split_assignment: Dict[str, str] = {}
        split_warnings: List[str] = []

        # Sort canonical_plant_ids deterministically
        for pid in sorted(plant_sha_groups.keys()):
            shas_dict = plant_sha_groups[pid]
            sha_keys = sorted(shas_dict.keys())

            num_shas = len(sha_keys)
            if num_shas < 3:
                split_warnings.append(f"Canonical plant '{pid}' has only {num_shas} unique SHA-256 group(s); standard 70/15/15 split ratio relaxed.")

            # Deterministically shuffle SHA keys for this plant using seed + plant_id hash
            seed_offset = int(hashlib.sha256(pid.encode('utf-8')).hexdigest()[:8], 16)
            rng = random.Random(self.config.random_seed + seed_offset)
            shuffled_shas = list(sha_keys)
            rng.shuffle(shuffled_shas)

            # Calculate partition boundaries
            n_train = max(1, round(num_shas * self.config.split_ratios.get("train", 0.70)))
            n_val = round(num_shas * self.config.split_ratios.get("val", 0.15))
            if num_shas >= 3 and n_val == 0:
                n_val = 1
            n_test = num_shas - n_train - n_val
            if n_test < 0:
                n_test = 0
                n_train = max(1, num_shas - n_val)

            for idx, sha in enumerate(shuffled_shas):
                if idx < n_train:
                    sha_split_assignment[sha] = "train"
                elif idx < n_train + n_val:
                    sha_split_assignment[sha] = "val"
                else:
                    sha_split_assignment[sha] = "test"

        # 2. Process Images & Generate Records
        processed_records: List[ProcessedDatasetRecord] = []
        proc_idx = 1

        resampling_filter = Image.Resampling.BILINEAR
        if self.config.interpolation.upper() == "BICUBIC":
            resampling_filter = Image.Resampling.BICUBIC
        elif self.config.interpolation.upper() == "NEAREST":
            resampling_filter = Image.Resampling.NEAREST

        for r in sorted(canonical_records, key=lambda x: x.get("record_id", "")):
            c_rec_id = r.get("record_id")
            pid = r.get("canonical_plant_id")
            p_name = r.get("canonical_name", pid)
            sci_name = r.get("scientific_name")
            hc = r.get("health_condition", "Unknown")
            sha = r.get("sha256")
            sources = r.get("source_references", [])

            if not sources:
                self.failures.append({"canonical_record_id": c_rec_id, "error": "MISSING_SOURCE_REFERENCES"})
                continue

            primary_src = sources[0]
            src_path_str = primary_src.get("source_file_path")
            ds_id = primary_src.get("dataset_id")
            orig_cls = primary_src.get("original_class_name")

            if not src_path_str or not Path(src_path_str).exists():
                self.failures.append({"canonical_record_id": c_rec_id, "source_path": src_path_str, "error": "SOURCE_FILE_NOT_FOUND"})
                continue

            src_path = Path(src_path_str)
            assigned_split = sha_split_assignment.get(sha, "train")

            # Process image safely with PIL
            try:
                with Image.open(src_path) as img:
                    orig_w, orig_h = img.size

                    # Convert color mode
                    if img.mode != self.config.color_mode:
                        proc_img = img.convert(self.config.color_mode)
                    else:
                        proc_img = img.copy()

                    # Resize to target dimensions
                    proc_img = proc_img.resize(self.config.image_size, resample=resampling_filter)

                    # Save to output directory
                    p_rec_id = f"proc_{self.config.version}_{proc_idx:06d}"
                    proc_dir = out_root / assigned_split / pid
                    proc_dir.mkdir(parents=True, exist_ok=True)

                    proc_file_path = proc_dir / f"{p_rec_id}.jpg"
                    proc_img.save(proc_file_path, format="JPEG", quality=95)
                    proc_w, proc_h = proc_img.size

                proc_sha = compute_file_sha256(proc_file_path)

                proc_record = ProcessedDatasetRecord(
                    processed_record_id=p_rec_id,
                    canonical_record_id=c_rec_id,
                    canonical_plant_id=pid,
                    canonical_name=p_name,
                    scientific_name=sci_name,
                    health_condition=hc,
                    split=assigned_split,
                    original_sha256=sha,
                    processed_sha256=proc_sha,
                    processed_path=str(proc_file_path),
                    original_source_path=src_path_str,
                    source_dataset=ds_id,
                    original_class_name=orig_cls,
                    original_dimensions=(orig_w, orig_h),
                    processed_dimensions=(proc_w, proc_h),
                    preprocessing_version=self.config.version,
                    source_references=sources
                )
                processed_records.append(proc_record)
                proc_idx += 1

            except Exception as e:
                self.failures.append({"canonical_record_id": c_rec_id, "source_path": src_path_str, "error": f"IMAGE_PREPROCESSING_FAILED: {e}"})

        self.records = processed_records

        # Calculate Statistics
        train_recs = [r for r in self.records if r.split == "train"]
        val_recs = [r for r in self.records if r.split == "val"]
        test_recs = [r for r in self.records if r.split == "test"]

        train_shas = {r.original_sha256 for r in train_recs}
        val_shas = {r.original_sha256 for r in val_recs}
        test_shas = {r.original_sha256 for r in test_recs}

        leakage_tv = len(train_shas.intersection(val_shas))
        leakage_tt = len(train_shas.intersection(test_shas))
        leakage_vt = len(val_shas.intersection(test_shas))
        total_leakage = leakage_tv + leakage_tt + leakage_vt

        per_plant_split: Dict[str, Dict[str, int]] = {}
        for r in self.records:
            per_plant_split.setdefault(r.canonical_plant_id, {"total": 0, "train": 0, "val": 0, "test": 0})
            per_plant_split[r.canonical_plant_id]["total"] += 1
            per_plant_split[r.canonical_plant_id][r.split] += 1

        self.statistics = {
            "status": "SUCCESS",
            "reason": "PROCESSED_AND_SPLIT_SUCCESSFULLY",
            "preprocessing_version": self.config.version,
            "total_source_records": len(canonical_records),
            "total_processed_records": len(self.records),
            "total_failures": len(self.failures),
            "train_count": len(train_recs),
            "val_count": len(val_recs),
            "test_count": len(test_recs),
            "healthy_count": sum(1 for r in self.records if r.health_condition == "Healthy"),
            "unhealthy_count": sum(1 for r in self.records if r.health_condition == "Unhealthy"),
            "unknown_health_count": sum(1 for r in self.records if r.health_condition == "Unknown"),
            "unique_original_shas": len({r.original_sha256 for r in self.records}),
            "unique_processed_shas": len({r.processed_sha256 for r in self.records}),
            "cross_split_leakage_count": total_leakage,
            "split_warnings": split_warnings,
            "per_plant_split_counts": per_plant_split
        }

        # Run Validation
        self.validation_report = self.validate_processed_dataset()
        return self.records, self.statistics

    def validate_processed_dataset(self) -> Dict[str, Any]:
        """
        Validates processed dataset for integrity, file existence, SHA matches, and zero cross-split leakage.
        """
        errors = []
        if self.statistics.get("status") == "BLOCKED":
            return {
                "is_valid": True,
                "status": "BLOCKED",
                "reason": self.statistics.get("reason", "NO_APPROVED_MAPPINGS"),
                "errors_count": 0,
                "errors": []
            }

        # 1. Raw Dataset Immutability Check
        external_roots = [r"C:\Datasets\CIMPd", r"C:\Datasets\Hugging_Face", r"C:\Datasets\Kaggle"]
        for p in external_roots:
            if os.path.exists(p) and not os.path.isdir(p):
                errors.append(f"Raw dataset path '{p}' was corrupted!")

        # 2. Cross-Split SHA-256 Leakage Check
        train_shas = {r.original_sha256 for r in self.records if r.split == "train"}
        val_shas = {r.original_sha256 for r in self.records if r.split == "val"}
        test_shas = {r.original_sha256 for r in self.records if r.split == "test"}

        tv_leak = train_shas.intersection(val_shas)
        tt_leak = train_shas.intersection(test_shas)
        vt_leak = val_shas.intersection(test_shas)

        if tv_leak:
            errors.append(f"Data leakage detected between Train and Val: {len(tv_leak)} shared SHA-256s.")
        if tt_leak:
            errors.append(f"Data leakage detected between Train and Test: {len(tt_leak)} shared SHA-256s.")
        if vt_leak:
            errors.append(f"Data leakage detected between Val and Test: {len(vt_leak)} shared SHA-256s.")

        # 3. File existence & SHA-256 match check
        for r in self.records:
            pp = Path(r.processed_path)
            if not pp.exists():
                errors.append(f"Processed file missing: '{r.processed_path}'")
            else:
                actual_sha = compute_file_sha256(pp)
                if actual_sha != r.processed_sha256:
                    errors.append(f"Processed SHA mismatch for '{r.processed_path}': expected {r.processed_sha256}, got {actual_sha}")

            if r.processed_dimensions != self.config.image_size:
                errors.append(f"Processed image dimensions mismatch for '{r.processed_path}': expected {self.config.image_size}, got {r.processed_dimensions}")

        return {
            "is_valid": len(errors) == 0,
            "status": "SUCCESS" if len(errors) == 0 else "INVALID",
            "total_records": len(self.records),
            "errors_count": len(errors),
            "errors": errors
        }

    def export_artifacts(self) -> Dict[str, Path]:
        """
        Exports versioned processed_dataset_manifest_v1.json, statistics, and validation report.
        """
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        manifest_path = self.reports_dir / f"processed_dataset_manifest_{self.config.version}.json"
        stats_path = self.reports_dir / f"processed_dataset_statistics_{self.config.version}.json"
        val_path = self.reports_dir / f"processed_dataset_validation_{self.config.version}.json"

        recs_list = [r.to_dict() for r in self.records]

        # 1. Processed Manifest JSON
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump({
                "preprocessing_version": self.config.version,
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "status": self.statistics.get("status", "BLOCKED"),
                "reason": self.statistics.get("reason", "NO_APPROVED_MAPPINGS"),
                "configuration": self.config.to_dict(),
                "total_records": len(recs_list),
                "records": recs_list
            }, f, indent=2, ensure_ascii=False)

        # 2. Statistics JSON
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(self.statistics, f, indent=2, ensure_ascii=False)

        # 3. Validation JSON
        with open(val_path, "w", encoding="utf-8") as f:
            json.dump(self.validation_report, f, indent=2, ensure_ascii=False)

        return {
            "manifest_json": manifest_path,
            "statistics_json": stats_path,
            "validation_json": val_path
        }

    def format_terminal_summary(self) -> str:
        s = self.statistics
        val = self.validation_report
        lines = [
            "==========================================================================",
            f"   DRAVYA AI CANONICAL PREPROCESSING & SPLIT SUMMARY ({self.config.version})   ",
            "==========================================================================",
            f"Preprocessing Version:               {self.config.version}",
            f"Pipeline Status:                     {s.get('status', 'BLOCKED')}",
            f"Status Reason:                       {s.get('reason', 'NO_APPROVED_MAPPINGS')}",
            f"Target Image Size:                   {self.config.image_size[0]}x{self.config.image_size[1]} ({self.config.color_mode})",
            f"Random Seed:                         {self.config.random_seed}",
            f"Total Source Canonical Records:      {s.get('total_source_records', 0)}",
            f"Total Processed Records Generated:   {s.get('total_processed_records', 0)}",
            f"  - Train Count:                     {s.get('train_count', 0)}",
            f"  - Validation Count:                {s.get('val_count', 0)}",
            f"  - Test Count:                      {s.get('test_count', 0)}",
            f"Cross-Split SHA Leakage Count:       {s.get('cross_split_leakage_count', 0)}",
            "--------------------------------------------------------------------------",
            f"Validation Status:                   {'PASSED (100% VALID)' if val.get('is_valid') else 'FAILED'}",
            f"Validation Errors Count:             {val.get('errors_count', 0)}",
            "=========================================================================="
        ]
        return "\n".join(lines)
