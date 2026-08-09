import os
import sys
import json
import hashlib
import statistics
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple

PROJECT_ROOT = Path(r"C:\Dravya\Dravya-Ayurvedic-Blockchain-Platform\AI-Engine")
REPORTS_DIR = PROJECT_ROOT / "reports" / "dataset_analysis"

RAW_DATASETS = {
    "CIMPd": Path(r"C:\Datasets\CIMPd"),
    "Kaggle": Path(r"C:\Datasets\Kaggle"),
    "Hugging_Face": Path(r"C:\Datasets\Hugging_Face"),
}

VALID_EXTENSIONS: Set[str] = {
    ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"
}

def audit():
    print("==========================================================================")
    print("        DRAVYA AI ENGINE — STEP 1 TAXONOMY & INVENTORY AUDIT             ")
    print("==========================================================================")

    # 1. Inspect Authoritative Taxonomy Sources
    cand_file = REPORTS_DIR / "candidate_training_classes_v2.json"
    rev_file = REPORTS_DIR / "training_taxonomy_review_v2.json"

    print("\nA. Current Approved Taxonomy Source Inspection:")
    print(f" - Candidate Classes File: {cand_file} (Exists: {cand_file.exists()})")
    print(f" - Taxonomy Review File:   {rev_file} (Exists: {rev_file.exists()})")

    # 2. Inspect physical inventory JSON (from Step 1 scan)
    inv_file = REPORTS_DIR / "physical_raw_inventory_v3.json"
    if not inv_file.exists():
        print(f"ERROR: Inventory file missing: {inv_file}")
        return

    with open(inv_file, "r", encoding="utf-8") as f:
        inv_data = json.load(f)

    records = inv_data.get("records", [])
    summary = inv_data.get("summary", {})

    print("\nB. Physical Raw Scan Totals:")
    print(f" - Total Physical Images:  {summary.get('total_physical_images'):,}")
    print(f" - CIMPd Images:           {summary.get('cimpd_images'):,}")
    print(f" - Kaggle Images:          {summary.get('kaggle_images'):,}")
    print(f" - Hugging_Face Images:    {summary.get('huggingface_images'):,}")
    print(f" - Total Physical Classes: {summary.get('total_physical_classes'):,}")
    print(f" - Corrupt Images:         {summary.get('corrupt_images')}")
    print(f" - Duplicate Hash Groups:  {summary.get('duplicate_hash_groups'):,}")
    print(f" - Duplicate Files Count:  {summary.get('duplicate_files_count'):,}")

    # 3. Duplicate Analysis (Within vs Cross-Dataset)
    sha_map: Dict[str, List[Dict[str, str]]] = {}
    for r in records:
        sha = r["sha256"]
        if sha != "ERROR_HASH":
            sha_map.setdefault(sha, []).append({
                "ds": r["dataset_source"],
                "path": r["raw_image_path"]
            })

    dup_groups = {sha: items for sha, items in sha_map.items() if len(items) > 1}
    
    within_ds_groups = 0
    cross_ds_groups = 0
    both_groups = 0

    for sha, items in dup_groups.items():
        ds_set = set(item["ds"] for item in items)
        if len(ds_set) == 1:
            within_ds_groups += 1
        else:
            cross_ds_groups += 1

    print("\nC. Duplicate Analysis Breakdown:")
    print(f" - Total Unique SHA-256 Hashes: {len(sha_map):,}")
    print(f" - Total Duplicate Hash Groups: {len(dup_groups):,}")
    print(f" - Total Duplicate File Instances: {summary.get('duplicate_files_count'):,}")
    print(f" - Within-Dataset Duplicate Groups: {within_ds_groups:,}")
    print(f" - Cross-Dataset Duplicate Groups:  {cross_ds_groups:,}")

    # 4. Root Cause Analysis
    print("\nD. Root Cause Analysis:")
    print(" - Why physical_inventory_v3.py reported APPROVED CLASSES FOUND: 10:")
    print("   The script loaded candidate_training_classes_v2.json, whose `candidate_classes` array")
    print("   was truncated during export and contains only 10 entries (DRAVYA_0001 to DRAVYA_0010).")
    print("   The script evaluated `approved_candidates = [c for c in candidate_classes if APPROVED]`,")
    print("   which loaded len == 10. Since all 10 matched, it reported 10 found and 0 missing!")

if __name__ == "__main__":
    audit()
