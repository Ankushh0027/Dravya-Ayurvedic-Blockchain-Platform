"""
Dravya AI Engine — Package Materialized Canonical Dataset V1 for Kaggle GPU Training
====================================================================================
Packages data/canonical/v1/ (22,547 canonical images, 94 approved classes, 
manifests, and metadata) into a Kaggle-ready ZIP archive:
  canonical_dataset_v1_kaggle.zip

Safety Status: RAW DATASETS REMAIN 100% UNTOUCHED & READ-ONLY.
"""

import os
import sys
import time
import zipfile
from pathlib import Path
from typing import Dict, Any, List

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_V1_DIR = PROJECT_ROOT / "data" / "canonical" / "v1"
OUTPUT_ZIP_PATH = PROJECT_ROOT / "canonical_dataset_v1_kaggle.zip"


def package_canonical_v1_for_kaggle():
    print("==========================================================================")
    print("      DRAVYA AI ENGINE — KAGGLE DATASET PACKAGING RUNNER (v1)             ")
    print("==========================================================================")

    if not CANONICAL_V1_DIR.exists():
        raise FileNotFoundError(f"Canonical v1 dataset directory not found at: {CANONICAL_V1_DIR}")

    manifest_path = CANONICAL_V1_DIR / "manifests" / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Canonical v1 manifest missing at: {manifest_path}")

    print(f"Canonical Dataset Source: {CANONICAL_V1_DIR}")
    print(f"Target Zip Output:       {OUTPUT_ZIP_PATH}")
    print("--------------------------------------------------------------------------")

    start_time = time.time()
    file_count = 0
    total_bytes = 0

    with zipfile.ZipFile(OUTPUT_ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(CANONICAL_V1_DIR):
            for f in files:
                abs_file_path = Path(root) / f
                rel_path = abs_file_path.relative_to(CANONICAL_V1_DIR)
                zf.write(abs_file_path, arcname=str(rel_path))
                file_count += 1
                total_bytes += abs_file_path.stat().st_size

    elapsed = round(time.time() - start_time, 2)
    zip_bytes = OUTPUT_ZIP_PATH.stat().st_size
    zip_mb = round(zip_bytes / (1024 * 1024), 2)
    zip_gb = round(zip_bytes / (1024 * 1024 * 1024), 3)

    print("Testing archive integrity...")
    with zipfile.ZipFile(OUTPUT_ZIP_PATH, "r") as zf:
        corrupt = zf.testzip()
        if corrupt is not None:
            raise RuntimeError(f"Zip archive integrity check failed! Corrupt file: {corrupt}")

    print("\n==========================================================================")
    print("             KAGGLE DATASET PACKAGING SUMMARY REPORT                      ")
    print("==========================================================================")
    print(f"ZIP ARCHIVE PATH:      {OUTPUT_ZIP_PATH}")
    print(f"TOTAL FILES PACKAGED:  {file_count:,}")
    print(f"UNCOMPRESSED SIZE:     {round(total_bytes / (1024 * 1024), 2):,} MB")
    print(f"COMPRESSED ZIP SIZE:   {zip_mb:,.2f} MB ({zip_gb:.3f} GB)")
    print(f"PACKAGING TIME:        {elapsed}s")
    print("ZIP INTEGRITY TEST:    PASS")
    print("==========================================================================")
    print("\nNext Steps for Kaggle:")
    print("1. Upload `canonical_dataset_v1_kaggle.zip` as a Kaggle Dataset (e.g. name: `dravya-canonical-v1`).")
    print("2. Run `notebooks/dravya_kaggle_gpu_training.ipynb` on Kaggle Notebooks with GPU (P100 / T4) enabled.")


if __name__ == "__main__":
    package_canonical_v1_for_kaggle()
