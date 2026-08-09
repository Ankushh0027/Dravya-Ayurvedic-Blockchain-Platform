import os
import sys
import json
import shutil
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple

PROJECT_ROOT = Path(r"C:\Dravya\Dravya-Ayurvedic-Blockchain-Platform\AI-Engine")
REPORTS_DIR = PROJECT_ROOT / "reports" / "dataset_analysis"
CANONICAL_V2_ROOT = PROJECT_ROOT / "datasets" / "final" / "canonical_v2"

# Raw dataset roots for verifying physical file existence
RAW_DATASET_ROOTS = {
    "CIMPd": Path(r"C:\Datasets\CIMPd"),
    "Kaggle": Path(r"C:\Datasets\Kaggle"),
    "Hugging_Face": Path(r"C:\Datasets\Hugging_Face"),
}

def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def materialize_canonical_v2():
    print("==========================================================================")
    print("      DRAVYA AI ENGINE — CANONICAL DATASET V2 MATERIALIZER ENGINE        ")
    print("==========================================================================")

    manifest_path = REPORTS_DIR / "canonical_dataset_manifest_v2.json"
    if not manifest_path.exists():
        manifest_path = CANONICAL_V2_ROOT / "manifest.json"

    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest missing at {manifest_path}")

    print(f"\n1. Loading Approved Manifest: {manifest_path}")
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    records = manifest_data.get("records", [])
    approved_records = [r for r in records if r.get("mapping_status") == "APPROVED"]

    print(f"-> Verified Approved Records in Manifest: {len(approved_records):,}")

    # Target Split Roots
    train_root = CANONICAL_V2_ROOT / "train"
    val_root = CANONICAL_V2_ROOT / "validation"
    test_root = CANONICAL_V2_ROOT / "test"

    train_root.mkdir(parents=True, exist_ok=True)
    val_root.mkdir(parents=True, exist_ok=True)
    test_root.mkdir(parents=True, exist_ok=True)

    # Copy manifest.json to canonical_v2 root if not present
    target_root_manifest = CANONICAL_V2_ROOT / "manifest.json"
    if not target_root_manifest.exists() or target_root_manifest != manifest_path:
        with open(target_root_manifest, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)

    print("\n2. Verifying Raw Source Images & Copying to Split Subdirectories...")
    start_time = time.time()

    train_count = 0
    val_count = 0
    test_count = 0
    missing_count = 0
    failed_copies = 0

    train_hashes: Set[str] = set()
    val_hashes: Set[str] = set()
    test_hashes: Set[str] = set()

    all_classes: Set[str] = set()

    for idx, r in enumerate(approved_records, start=1):
        raw_path_str = r.get("raw_image_path")
        raw_path = Path(raw_path_str) if raw_path_str else None

        # Fallback path resolution if raw path string is relative
        if not raw_path or not raw_path.exists():
            ds_id = r.get("source_dataset")
            src_class = r.get("source_class_name")
            orig_filename = Path(raw_path_str).name if raw_path_str else ""
            if ds_id in RAW_DATASET_ROOTS and src_class and orig_filename:
                candidate = RAW_DATASET_ROOTS[ds_id] / src_class / orig_filename
                if candidate.exists():
                    raw_path = candidate

        if not raw_path or not raw_path.exists():
            missing_count += 1
            print(f"Warning: Missing source image for record {r.get('record_id')}: {raw_path_str}")
            continue

        split_tag = str(r.get("split", "train")).lower()
        class_id = r.get("canonical_class_id", "DRAVYA_0001")
        all_classes.add(class_id)

        # Resolve target split folder
        if split_tag in ["train"]:
            target_split_dir = train_root / class_id
            target_hashes = train_hashes
            train_count += 1
        elif split_tag in ["val", "validation"]:
            target_split_dir = val_root / class_id
            target_hashes = val_hashes
            val_count += 1
        elif split_tag in ["test"]:
            target_split_dir = test_root / class_id
            target_hashes = test_hashes
            test_count += 1
        else:
            target_split_dir = train_root / class_id
            target_hashes = train_hashes
            train_count += 1

        target_split_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{r.get('record_id')}{raw_path.suffix.lower()}"
        target_file_path = target_split_dir / filename

        # Copy raw image to target split folder (Read-only on source)
        try:
            if not target_file_path.exists():
                shutil.copy2(raw_path, target_file_path)
            
            # Record SHA-256 for cross-split leakage check
            file_sha = r.get("sha256") or compute_sha256(target_file_path)
            target_hashes.add(file_sha)

        except Exception as e:
            failed_copies += 1
            print(f"Error copying {raw_path} to {target_file_path}: {e}")

        if idx % 5000 == 0 or idx == len(approved_records):
            print(f"-> Processed {idx:,} / {len(approved_records):,} records...")

    elapsed = round(time.time() - start_time, 2)

    # Check for cross-split SHA-256 leakage
    train_val_leakage = train_hashes.intersection(val_hashes)
    train_test_leakage = train_hashes.intersection(test_hashes)
    val_test_leakage = val_hashes.intersection(test_hashes)
    total_leakage = len(train_val_leakage) + len(train_test_leakage) + len(val_test_leakage)

    total_materialized = train_count + val_count + test_count

    print("\n==========================================================================")
    print("              MATERIALIZATION & INTEGRITY REPORT                         ")
    print("==========================================================================")
    print(f"TOTAL MATERIALIZED IMAGES: {total_materialized:,}")
    print(f"TRAIN:                     {train_count:,}")
    print(f"VALIDATION:                {val_count:,}")
    print(f"TEST:                      {test_count:,}")
    print(f"CLASSES:                   {len(all_classes)}")
    print(f"MISSING:                   {missing_count}")
    print(f"FAILED COPIES:             {failed_copies}")
    print(f"CROSS-SPLIT LEAKAGE:       {total_leakage}")
    print(f"ELAPSED TIME:              {elapsed}s")
    print("==========================================================================")

    print("\nFinal Directory Structure:")
    print(f"datasets/final/canonical_v2/")
    print(f"├── manifest.json")
    print(f"├── train/        ({train_count:,} images across {len(all_classes)} class folders)")
    print(f"├── validation/   ({val_count:,} images across {len(all_classes)} class folders)")
    print(f"└── test/         ({test_count:,} images across {len(all_classes)} class folders)")

if __name__ == "__main__":
    materialize_canonical_v2()
