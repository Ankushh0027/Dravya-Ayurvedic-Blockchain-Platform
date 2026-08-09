import os
import sys
import json
import csv
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple

try:
    from PIL import Image
except ImportError:
    Image = None

PROJECT_ROOT = Path(r"C:\Dravya\Dravya-Ayurvedic-Blockchain-Platform\AI-Engine")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.combined_inventory_v2 import CombinedInventoryAnalyzer
from src.data.candidate_manifest_v2 import CandidateManifestGeneratorV2

REPORTS_DIR = PROJECT_ROOT / "reports" / "dataset_analysis"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

RAW_DATASETS = {
    "CIMPd": Path(r"C:\Datasets\CIMPd"),
    "Kaggle": Path(r"C:\Datasets\Kaggle"),
    "Hugging_Face": Path(r"C:\Datasets\Hugging_Face"),
}

SUPPORTED_EXTENSIONS: Set[str] = {
    ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"
}

def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def get_or_generate_candidate_manifest(cand_file: Path) -> Dict[str, Any]:
    """
    Loads candidate_training_classes_v2.json. If missing or structurally invalid,
    regenerates the authoritative taxonomy manifest programmatically.
    """
    is_valid_manifest = False
    if cand_file.exists():
        try:
            with open(cand_file, "r", encoding="utf-8") as f:
                cand_data = json.load(f)
            cand_classes = cand_data.get("candidate_classes", [])
            approved = [c for c in cand_classes if c.get("approval_status") == "APPROVED"]
            # Validate non-empty approved candidates and structural integrity
            if len(approved) > 0 and len(cand_classes) >= len(approved):
                # Verify uniqueness of class IDs and species names
                class_ids = [c.get("class_id") for c in approved]
                species_names = [c.get("canonical_species_name") for c in approved]
                if len(class_ids) == len(set(class_ids)) and len(species_names) == len(set(species_names)):
                    is_valid_manifest = True
        except Exception:
            is_valid_manifest = False

    if not is_valid_manifest:
        print("Regenerating authoritative candidate training manifest (v2)...")
        comb_inv_file = REPORTS_DIR / "combined_species_inventory_v2.json"
        
        run_combined = True
        if comb_inv_file.exists():
            try:
                with open(comb_inv_file, "r", encoding="utf-8") as f:
                    c_data = json.load(f)
                if "candidate_species_inventory" in c_data and len(c_data["candidate_species_inventory"]) > 0:
                    run_combined = False
            except Exception:
                run_combined = True

        if run_combined:
            print("Running CombinedInventoryAnalyzer to build full species inventory...")
            analyzer = CombinedInventoryAnalyzer(dataset_paths=RAW_DATASETS, reports_dir=REPORTS_DIR)
            phase1 = analyzer.run_phase1_inventory()
            mapping_recs, cand_species = analyzer.run_phase2_harmonization(phase1)
            stats = analyzer.run_phase3_statistics(phase1, cand_species)
            analyzer.generate_reports(phase1, mapping_recs, cand_species, stats)

        generator = CandidateManifestGeneratorV2(reports_dir=REPORTS_DIR)
        inv_data = generator.load_combined_inventory()
        conflicts = generator.analyze_taxonomy_conflicts(inv_data)
        low_data = generator.analyze_low_data_species(inv_data.get("candidate_species_inventory", []))
        cand_man, rev_man, stats_sum = generator.build_candidate_and_review_manifests(inv_data, conflicts)
        generator.export_manifests_and_report(cand_man, rev_man, conflicts, low_data, stats_sum)

        with open(cand_file, "r", encoding="utf-8") as f:
            cand_data = json.load(f)

    return cand_data

def scan_physical_inventory():
    print("==========================================================================")
    print("    DRAVYA AI ENGINE — STEP 1 PHYSICAL FILE-LEVEL INVENTORY SCANNER       ")
    print("==========================================================================")

    start_time = time.time()

    all_records: List[Dict[str, Any]] = []
    dataset_counts: Dict[str, int] = {"CIMPd": 0, "Kaggle": 0, "Hugging_Face": 0}
    dataset_classes: Dict[str, Set[str]] = {"CIMPd": set(), "Kaggle": set(), "Hugging_Face": set()}
    
    sha_map: Dict[str, List[str]] = {}
    corrupt_files: List[Dict[str, Any]] = []
    empty_folders: List[str] = []

    total_physical_classes_set: Set[str] = set()

    for ds_name, ds_root in RAW_DATASETS.items():
        print(f"\nScanning Raw Dataset: {ds_name} ({ds_root})...")
        if not ds_root.exists():
            print(f" -> WARNING: Dataset root {ds_root} does not exist!")
            continue

        for root, dirs, files in os.walk(ds_root):
            rel_root = Path(root).relative_to(ds_root)
            parts = rel_root.parts

            # Check for empty folder
            if not dirs and not files:
                empty_folders.append(str(Path(root)))
                continue

            # Resolve class folder name & leaf folder name
            class_folder_name = str(rel_root) if parts else "ROOT"
            leaf_folder_name = parts[-1] if parts else "ROOT"

            valid_files_in_folder = 0
            for f in files:
                ext = Path(f).suffix.lower()
                if ext not in SUPPORTED_EXTENSIONS:
                    continue

                valid_files_in_folder += 1
                abs_path = Path(root) / f
                rel_path = abs_path.relative_to(ds_root)
                file_size = abs_path.stat().st_size

                # Compute SHA-256
                try:
                    file_sha = compute_sha256(abs_path)
                except Exception as e:
                    file_sha = "ERROR_HASH"

                # Verify PIL decodability & dimensions
                width, height, img_fmt, status = None, None, None, "VALID"
                if Image:
                    try:
                        with Image.open(abs_path) as img:
                            width, height = img.size
                            img_fmt = img.format
                            img.verify()
                    except Exception as e:
                        status = "CORRUPT"
                        corrupt_files.append({
                            "dataset_source": ds_name,
                            "raw_image_path": str(abs_path),
                            "error": str(e)
                        })

                rec = {
                    "dataset_source": ds_name,
                    "raw_image_path": str(abs_path),
                    "relative_path": str(rel_path),
                    "filename": f,
                    "extension": ext,
                    "class_folder_name": class_folder_name,
                    "leaf_folder_name": leaf_folder_name,
                    "file_size_bytes": file_size,
                    "sha256": file_sha,
                    "width": width,
                    "height": height,
                    "format": img_fmt,
                    "decodable_status": status
                }

                all_records.append(rec)
                dataset_counts[ds_name] += 1
                if class_folder_name != "ROOT":
                    dataset_classes[ds_name].add(class_folder_name)
                    total_physical_classes_set.add(f"{ds_name}:{class_folder_name}")

                if file_sha != "ERROR_HASH":
                    sha_map.setdefault(file_sha, []).append(str(abs_path))

            if len(all_records) % 5000 == 0 and len(all_records) > 0:
                print(f" -> Processed {len(all_records):,} physical image files so far...")

    total_images = len(all_records)
    total_corrupt = len(corrupt_files)
    
    # Calculate duplicate SHA-256 hash groups
    duplicate_hash_groups = {sha: paths for sha, paths in sha_map.items() if len(paths) > 1}
    duplicate_group_count = len(duplicate_hash_groups)
    duplicate_file_count = sum(len(paths) - 1 for paths in duplicate_hash_groups.values())

    print(f"\nCompleted Physical Scan in {round(time.time() - start_time, 2)}s.")
    print(f"Total Physical Images Found: {total_images:,}")

    # 2. Cross-check Discovered Classes against Dynamic Manifest
    cand_file = REPORTS_DIR / "candidate_training_classes_v2.json"
    cand_data = get_or_generate_candidate_manifest(cand_file)

    candidate_classes = cand_data.get("candidate_classes", [])
    approved_candidates = [c for c in candidate_classes if c.get("approval_status") == "APPROVED"]
    needs_review_candidates = [c for c in candidate_classes if c.get("approval_status") == "NEEDS_REVIEW"]
    rejected_candidates = [c for c in candidate_classes if c.get("approval_status") == "REJECTED"]

    # Manifest Integrity Validations
    if len(approved_candidates) == 0:
        raise ValueError("Taxonomy Validation Error: Candidate manifest contains 0 approved classes!")

    # Verify uniqueness of class IDs and species names
    approved_ids = [c["class_id"] for c in approved_candidates]
    approved_names = [c["canonical_species_name"] for c in approved_candidates]
    if len(approved_ids) != len(set(approved_ids)):
        raise ValueError("Taxonomy Validation Error: Duplicate approved class IDs detected in candidate manifest!")
    if len(approved_names) != len(set(approved_names)):
        raise ValueError("Taxonomy Validation Error: Duplicate canonical species names detected in candidate manifest!")

    # Separate NEEDS_REVIEW into low-data vs taxonomy conflict
    needs_review_low_data = [c for c in needs_review_candidates if c.get("total_images", 0) < 100 and "conflict" not in c.get("selection_reason", "").lower() and "vernacular" not in c.get("selection_reason", "").lower()]
    needs_review_taxonomy = [c for c in needs_review_candidates if c not in needs_review_low_data]

    approved_found = 0
    approved_missing = 0
    approved_sufficient = 0
    approved_insufficient = 0

    class_cross_check_list = []

    # Map discovered folders across datasets against all approved classes
    for c in approved_candidates:
        cid = c["class_id"]
        cname = c["canonical_species_name"]
        orig_names = c.get("original_names", [])
        target_sources = c.get("source_datasets", [])

        matching_records = []
        for rec in all_records:
            if rec["dataset_source"] in target_sources:
                c_folder = rec["class_folder_name"]
                l_folder = rec.get("leaf_folder_name", c_folder)
                if (c_folder in orig_names or 
                    l_folder in orig_names or 
                    any(c_folder == orig or c_folder.endswith(orig) or orig.endswith(c_folder) or orig.endswith(l_folder) for orig in orig_names)):
                    matching_records.append(rec)

        img_count = len(matching_records)
        if img_count > 0:
            approved_found += 1
            if img_count >= 100:
                approved_sufficient += 1
            else:
                approved_insufficient += 1
            class_cross_check_list.append({
                "class_id": cid,
                "species_name": cname,
                "status": "FOUND",
                "physical_image_count": img_count,
                "sufficient": img_count >= 100
            })
        else:
            approved_missing += 1
            class_cross_check_list.append({
                "class_id": cid,
                "species_name": cname,
                "status": "MISSING",
                "physical_image_count": 0,
                "sufficient": False
            })

    # 3. Export Machine-Readable Artifacts
    json_path = REPORTS_DIR / "physical_raw_inventory_v3.json"
    csv_path = REPORTS_DIR / "physical_raw_inventory_v3.csv"
    md_path = REPORTS_DIR / "physical_raw_inventory_v3.md"

    # Export JSON
    inventory_payload = {
        "metadata": {
            "title": "Dravya AI Engine — Physical Raw Dataset Inventory (Step 1)",
            "scanned_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "version": "v3"
        },
        "summary": {
            "total_physical_images": total_images,
            "cimpd_images": dataset_counts["CIMPd"],
            "kaggle_images": dataset_counts["Kaggle"],
            "huggingface_images": dataset_counts["Hugging_Face"],
            "total_physical_classes": len(total_physical_classes_set),
            "corrupt_images": total_corrupt,
            "duplicate_hash_groups": duplicate_group_count,
            "duplicate_files_count": duplicate_file_count,
            "approved_classes_expected": len(approved_candidates),
            "approved_classes_found": approved_found,
            "approved_classes_missing": approved_missing,
            "approved_classes_sufficient": approved_sufficient,
            "approved_classes_insufficient": approved_insufficient,
            "needs_review_low_data_count": len(needs_review_low_data),
            "needs_review_taxonomy_count": len(needs_review_taxonomy),
            "rejected_classes_count": len(rejected_candidates),
            "total_candidate_species": len(candidate_classes)
        },
        "records": all_records
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(inventory_payload, f, indent=2, ensure_ascii=False)

    # Export CSV
    fieldnames = [
        "dataset_source", "raw_image_path", "relative_path", "filename",
        "extension", "class_folder_name", "leaf_folder_name", "file_size_bytes", "sha256",
        "width", "height", "format", "decodable_status"
    ]
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_records)

    # Export Markdown Report
    md_lines = [
        "# Dravya AI Engine — Physical File-Level Raw Dataset Inventory (Step 1)",
        "",
        f"**Scanned At:** {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}  ",
        "**Safety Status:** Raw Datasets READ-ONLY & 100% Untouched  ",
        "",
        "---",
        "",
        "## Summary Totals",
        "",
        "| Metric | Count |",
        "|---|---|",
        f"| **TOTAL PHYSICAL IMAGES** | **{total_images:,}** |",
        f"| **CIMPd IMAGES** | **{dataset_counts['CIMPd']:,}** |",
        f"| **Kaggle IMAGES** | **{dataset_counts['Kaggle']:,}** |",
        f"| **Hugging_Face IMAGES** | **{dataset_counts['Hugging_Face']:,}** |",
        f"| **TOTAL PHYSICAL CLASSES** | **{len(total_physical_classes_set):,}** |",
        f"| **CORRUPT IMAGES** | **{total_corrupt}** |",
        f"| **DUPLICATE HASH GROUPS** | **{duplicate_group_count:,}** |",
        f"| **DUPLICATE FILES COUNT** | **{duplicate_file_count:,}** |",
        f"| **APPROVED CLASSES (DYNAMIC)** | **{approved_found} / {len(approved_candidates)}** |",
        f"| **APPROVED CLASSES MISSING** | **{approved_missing}** |",
        f"| **APPROVED CLASSES (>= 100 IMAGES)** | **{approved_sufficient}** |",
        f"| **APPROVED CLASSES (< 100 IMAGES)** | **{approved_insufficient}** |",
        f"| **NEEDS REVIEW (LOW DATA <100)** | **{len(needs_review_low_data)}** |",
        f"| **NEEDS REVIEW (TAXONOMY CONFLICTS)** | **{len(needs_review_taxonomy)}** |",
        f"| **REJECTED CLASSES** | **{len(rejected_candidates)}** |",
        f"| **TOTAL CANDIDATE SPECIES** | **{len(candidate_classes)}** |",
        "",
        "---",
        "",
        "## Machine-Readable Artifact Outputs",
        f"- **JSON Inventory:** `{json_path}`",
        f"- **CSV Inventory:** `{csv_path}`",
    ]

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    # Print Final Terminal Summary Block
    print("\n==========================================================================")
    print("            STEP 1 PHYSICAL RAW INVENTORY SUMMARY METRICS                 ")
    print("==========================================================================")
    print(f"TOTAL PHYSICAL IMAGES:       {total_images:,}")
    print(f"CIMPd IMAGES:                {dataset_counts['CIMPd']:,}")
    print(f"Kaggle IMAGES:               {dataset_counts['Kaggle']:,}")
    print(f"Hugging_Face IMAGES:         {dataset_counts['Hugging_Face']:,}")
    print(f"TOTAL PHYSICAL CLASSES:      {len(total_physical_classes_set):,}")
    print(f"CORRUPT IMAGES:              {total_corrupt}")
    print(f"DUPLICATE HASH GROUPS:       {duplicate_group_count:,}")
    print(f"APPROVED CLASSES (DYNAMIC):  {approved_found} / {len(approved_candidates)}")
    print(f"APPROVED CLASSES MISSING:    {approved_missing}")
    print(f"APPROVED CLASSES (>=100):    {approved_sufficient}")
    print(f"APPROVED CLASSES (<100):     {approved_insufficient}")
    print(f"NEEDS REVIEW (LOW DATA):     {len(needs_review_low_data)}")
    print(f"NEEDS REVIEW (TAXONOMY):     {len(needs_review_taxonomy)}")
    print(f"REJECTED CLASSES:            {len(rejected_candidates)}")
    print(f"TOTAL CANDIDATE SPECIES:     {len(candidate_classes)}")
    print("==========================================================================")
    print(f"\nArtifacts Written:")
    print(f" - JSON: {json_path}")
    print(f" - CSV:  {csv_path}")
    print(f" - MD:   {md_path}")

if __name__ == "__main__":
    scan_physical_inventory()

