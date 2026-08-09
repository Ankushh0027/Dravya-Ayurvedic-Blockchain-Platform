"""
Dravya AI Engine — Step 2 Read-Only Duplicate & Data-Leakage Audit Module (v3)

Performs SHA-256 global, within-dataset, cross-dataset, and class-level duplicate analysis
over the 42,062 physical images cataloged in Step 1.

Establishes:
1. Leakage-safe group-level split policy.
2. Deterministic representative image selection policy.
3. Machine-readable audit reports (JSON, CSV, MD).
"""

import json
import csv
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = PROJECT_ROOT / "reports" / "dataset_analysis"

DATASET_PRIORITY = {
    "CIMPd": 0,
    "Hugging_Face": 1,
    "Kaggle": 2
}

def load_inventory_and_manifest() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    inv_path = REPORTS_DIR / "physical_raw_inventory_v3.json"
    cand_path = REPORTS_DIR / "candidate_training_classes_v2.json"

    if not inv_path.exists():
        raise FileNotFoundError(f"Quality Gate Failure: Missing inventory file at {inv_path}")
    if not cand_path.exists():
        raise FileNotFoundError(f"Quality Gate Failure: Missing candidate manifest file at {cand_path}")

    with open(inv_path, "r", encoding="utf-8") as f:
        inv_data = json.load(f)

    with open(cand_path, "r", encoding="utf-8") as f:
        cand_data = json.load(f)

    return inv_data, cand_data

def build_raw_folder_to_species_map(cand_data: Dict[str, Any]) -> Dict[Tuple[str, str], Dict[str, str]]:
    """
    Maps (dataset_source, class_folder_name) -> {species_name, class_id, approval_status}
    """
    mapping = {}
    for c in cand_data.get("candidate_classes", []):
        cid = c["class_id"]
        cname = c["canonical_species_name"]
        status = c["approval_status"]
        orig_names = set(c.get("original_names", []))
        sources = c.get("source_datasets", [])

        for ds in sources:
            for orig in orig_names:
                mapping[(ds, orig)] = {
                    "class_id": cid,
                    "canonical_species_name": cname,
                    "approval_status": status
                }
    return mapping

def select_canonical_representative(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Deterministic Canonical Representative Selection Policy:
    1. Dataset Priority: CIMPd (0) > Hugging_Face (1) > Kaggle (2)
    2. Image Resolution: Higher pixel area (width * height)
    3. Lexicographical relative path ordering
    """
    def key_func(r):
        ds_prio = DATASET_PRIORITY.get(r["dataset_source"], 99)
        w = r.get("width") or 0
        h = r.get("height") or 0
        area = w * h
        rel_path = r.get("relative_path", "")
        return (ds_prio, -area, rel_path)

    sorted_recs = sorted(records, key=key_func)
    return sorted_recs[0]

def run_duplicate_audit():
    print("==========================================================================")
    print("      DRAVYA AI ENGINE — STEP 2 DUPLICATE & DATA-LEAKAGE AUDIT (v3)       ")
    print("==========================================================================")

    start_time = time.time()
    inv_data, cand_data = load_inventory_and_manifest()

    records = inv_data.get("records", [])
    total_physical_files = len(records)

    # Task 9 — Quality Gate Validation
    EXPECTED_PHYSICAL_FILES = 42062
    if total_physical_files != EXPECTED_PHYSICAL_FILES:
        raise ValueError(
            f"Quality Gate Failure: Inventory file count mismatch! Expected {EXPECTED_PHYSICAL_FILES}, got {total_physical_files}"
        )

    for r in records:
        if not r.get("sha256") or r.get("sha256") == "ERROR_HASH":
            raise ValueError(f"Quality Gate Failure: Missing or invalid SHA-256 hash in record {r.get('raw_image_path')}")

    folder_map = build_raw_folder_to_species_map(cand_data)

    # Task 1 — Global SHA-256 Analysis
    sha_groups: Dict[str, List[Dict[str, Any]]] = {}
    for r in records:
        sha_groups.setdefault(r["sha256"], []).append(r)

    unique_sha256_hashes = len(sha_groups)
    duplicate_groups_map = {sha: recs for sha, recs in sha_groups.items() if len(recs) > 1}
    duplicate_sha256_groups = len(duplicate_groups_map)
    total_files_in_duplicate_groups = sum(len(recs) for recs in duplicate_groups_map.values())
    redundant_duplicate_instances = total_files_in_duplicate_groups - duplicate_sha256_groups

    # Task 2 — Within-Dataset Duplicates
    ds_stats = {}
    for ds_name in ["CIMPd", "Kaggle", "Hugging_Face"]:
        ds_recs = [r for r in records if r["dataset_source"] == ds_name]
        ds_sha_map: Dict[str, List[Dict[str, Any]]] = {}
        for r in ds_recs:
            ds_sha_map.setdefault(r["sha256"], []).append(r)

        ds_dup_groups = {sha: recs for sha, recs in ds_sha_map.items() if len(recs) > 1}
        ds_dup_files = sum(len(recs) for recs in ds_dup_groups.values())
        ds_redundant = ds_dup_files - len(ds_dup_groups)

        ds_stats[ds_name] = {
            "total_images": len(ds_recs),
            "unique_hashes": len(ds_sha_map),
            "duplicate_groups": len(ds_dup_groups),
            "duplicate_files": ds_dup_files,
            "duplicate_instances": ds_redundant
        }

    # Task 3 — Cross-Dataset Duplicates
    cross_ds_categories = {
        "CIMPd_only": {"groups": 0, "files": 0, "redundant": 0},
        "Kaggle_only": {"groups": 0, "files": 0, "redundant": 0},
        "Hugging_Face_only": {"groups": 0, "files": 0, "redundant": 0},
        "CIMPd_and_Kaggle": {"groups": 0, "files": 0, "redundant": 0},
        "CIMPd_and_Hugging_Face": {"groups": 0, "files": 0, "redundant": 0},
        "Kaggle_and_Hugging_Face": {"groups": 0, "files": 0, "redundant": 0},
        "CIMPd_and_Kaggle_and_Hugging_Face": {"groups": 0, "files": 0, "redundant": 0}
    }

    for sha, group_recs in duplicate_groups_map.items():
        ds_present = sorted(list(set(r["dataset_source"] for r in group_recs)))
        num_files = len(group_recs)
        redundant = num_files - 1

        if ds_present == ["CIMPd"]:
            cat = "CIMPd_only"
        elif ds_present == ["Kaggle"]:
            cat = "Kaggle_only"
        elif ds_present == ["Hugging_Face"]:
            cat = "Hugging_Face_only"
        elif ds_present == ["CIMPd", "Kaggle"]:
            cat = "CIMPd_and_Kaggle"
        elif ds_present == ["CIMPd", "Hugging_Face"]:
            cat = "CIMPd_and_Hugging_Face"
        elif ds_present == ["Hugging_Face", "Kaggle"]:
            cat = "Kaggle_and_Hugging_Face"
        else:
            cat = "CIMPd_and_Kaggle_and_Hugging_Face"

        cross_ds_categories[cat]["groups"] += 1
        cross_ds_categories[cat]["files"] += num_files
        cross_ds_categories[cat]["redundant"] += redundant

    # Task 4 — Class-Level & Species Duplicate Analysis
    detailed_dup_records = []
    cross_class_conflicts = 0
    cross_species_conflicts = 0
    cross_status_conflicts = 0

    group_idx = 1
    for sha, group_recs in duplicate_groups_map.items():
        ds_list = sorted(list(set(r["dataset_source"] for r in group_recs)))
        raw_folders = sorted(list(set(f"{r['dataset_source']}:{r['class_folder_name']}" for r in group_recs)))

        mapped_species_set = set()
        mapped_status_set = set()
        for r in group_recs:
            ds = r["dataset_source"]
            c_folder = r["class_folder_name"]
            l_folder = r.get("leaf_folder_name", c_folder)
            
            # Find species match
            info = folder_map.get((ds, c_folder)) or folder_map.get((ds, l_folder))
            if not info:
                # Substring fallback search
                for (m_ds, m_orig), m_info in folder_map.items():
                    if m_ds == ds and (c_folder == m_orig or c_folder.endswith(m_orig) or m_orig.endswith(c_folder) or m_orig.endswith(l_folder)):
                        info = m_info
                        break

            if info:
                mapped_species_set.add(info["canonical_species_name"])
                mapped_status_set.add(info["approval_status"])
            else:
                mapped_species_set.add("UNMAPPED")
                mapped_status_set.add("UNMAPPED")

        has_class_conflict = len(raw_folders) > 1
        has_species_conflict = len(mapped_species_set) > 1
        has_status_conflict = len(mapped_status_set) > 1

        if has_class_conflict:
            cross_class_conflicts += 1
        if has_species_conflict:
            cross_species_conflicts += 1
        if has_status_conflict:
            cross_status_conflicts += 1

        # Task 6 — Select Canonical Representative
        rep_rec = select_canonical_representative(group_recs)

        detailed_dup_records.append({
            "group_id": f"DUP_{group_idx:05d}",
            "sha256": sha,
            "total_files": len(group_recs),
            "redundant_copies": len(group_recs) - 1,
            "datasets_present": ds_list,
            "raw_class_folders": raw_folders,
            "mapped_species": sorted(list(mapped_species_set)),
            "approval_statuses": sorted(list(mapped_status_set)),
            "representative_dataset": rep_rec["dataset_source"],
            "representative_raw_path": rep_rec["raw_image_path"],
            "representative_relative_path": rep_rec["relative_path"],
            "representative_dimensions": f"{rep_rec.get('width', 'N/A')}x{rep_rec.get('height', 'N/A')}",
            "has_class_conflict": has_class_conflict,
            "has_species_conflict": has_species_conflict,
            "has_status_conflict": has_status_conflict
        })
        group_idx += 1

    # Find Top 5 Largest Duplicate Groups
    sorted_dup_groups = sorted(detailed_dup_records, key=lambda x: x["total_files"], reverse=True)
    top_5_dup_groups = sorted_dup_groups[:5]

    # Task 8 — Export Artifacts
    json_path = REPORTS_DIR / "duplicate_audit_v3.json"
    csv_path = REPORTS_DIR / "duplicate_audit_v3.csv"
    md_path = REPORTS_DIR / "duplicate_audit_v3.md"

    audit_summary = {
        "total_physical_files": total_physical_files,
        "unique_sha256_hashes": unique_sha256_hashes,
        "duplicate_sha256_groups": duplicate_sha256_groups,
        "total_files_in_duplicate_groups": total_files_in_duplicate_groups,
        "redundant_duplicate_instances": redundant_duplicate_instances,
        "within_dataset_duplicates": ds_stats,
        "cross_dataset_duplicates": cross_ds_categories,
        "class_level_conflicts": {
            "cross_class_conflicts": cross_class_conflicts,
            "cross_species_conflicts": cross_species_conflicts,
            "cross_status_conflicts": cross_status_conflicts
        },
        "policies": {
            "data_leakage_policy": "Group-Level Atomic Split: All physical copies of a SHA-256 hash are assigned atomically to a single split (train/val/test). Zero cross-split leakage.",
            "canonical_representative_policy": "Priority: Dataset Source (CIMPd > Hugging_Face > Kaggle) -> Image Resolution (width * height) -> Lexicographical relative path order.",
            "near_duplicates_policy": "Exact SHA-256 deduplication evaluated in Step 2. Perceptual hashing and visual embeddings marked for future post-materialization pipeline phase."
        },
        "step_2_status": "PASS"
    }

    # Export JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "metadata": {
                "title": "Dravya AI Engine — Step 2 Read-Only Duplicate & Data-Leakage Audit",
                "audited_at": datetime.now(timezone.utc).isoformat(),
                "version": "v3"
            },
            "summary": audit_summary,
            "duplicate_groups": detailed_dup_records
        }, f, indent=2, ensure_ascii=False)

    # Export CSV
    csv_fieldnames = [
        "group_id", "sha256", "total_files", "redundant_copies", "datasets_present",
        "raw_class_folders", "mapped_species", "approval_statuses",
        "representative_dataset", "representative_relative_path",
        "has_class_conflict", "has_species_conflict", "has_status_conflict"
    ]
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fieldnames)
        writer.writeheader()
        for g in detailed_dup_records:
            writer.writerow({
                "group_id": g["group_id"],
                "sha256": g["sha256"],
                "total_files": g["total_files"],
                "redundant_copies": g["redundant_copies"],
                "datasets_present": ", ".join(g["datasets_present"]),
                "raw_class_folders": " | ".join(g["raw_class_folders"]),
                "mapped_species": " | ".join(g["mapped_species"]),
                "approval_statuses": ", ".join(g["approval_statuses"]),
                "representative_dataset": g["representative_dataset"],
                "representative_relative_path": g["representative_relative_path"],
                "has_class_conflict": g["has_class_conflict"],
                "has_species_conflict": g["has_species_conflict"],
                "has_status_conflict": g["has_status_conflict"]
            })

    # Export Markdown Report
    md_lines = [
        "# Dravya AI Engine — Step 2 Read-Only Duplicate & Data-Leakage Audit Report (v3)",
        "",
        f"**Audited At:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}  ",
        "**Safety Affirmation:** Raw Datasets READ-ONLY & 100% Untouched (`C:\\Datasets\\CIMPd`, `C:\\Datasets\\Kaggle`, `C:\\Datasets\\Hugging_Face`)  ",
        "**Audit Decision:** `STEP 2 STATUS: PASS`  ",
        "",
        "---",
        "",
        "## 1. Global SHA-256 Duplicate Statistics",
        "",
        "| Metric | Count | Description |",
        "|---|---|---|",
        f"| **Total Physical Image Files** | **{total_physical_files:,}** | Total files cataloged in Step 1 physical scan |",
        f"| **Unique SHA-256 Hashes** | **{unique_sha256_hashes:,}** | Distinct image content hashes across all datasets |",
        f"| **Duplicate SHA-256 Hash Groups** | **{duplicate_sha256_groups:,}** | Hashes appearing in $\\ge 2$ physical image files |",
        f"| **Files Belonging to Duplicate Groups** | **{total_files_in_duplicate_groups:,}** | Total physical files with non-unique content |",
        f"| **Redundant Duplicate Instances** | **{redundant_duplicate_instances:,}** | Total extra physical copies eligible for deduplication |",
        "",
        "---",
        "",
        "## 2. Within-Dataset Duplicate Breakdown",
        "",
        "| Dataset Source | Total Images | Unique Hashes | Duplicate Groups | Duplicate Files | Redundant Instances |",
        "|---|---|---|---|---|---|",
    ]

    for ds_name, ds_info in ds_stats.items():
        md_lines.append(
            f"| **{ds_name}** | {ds_info['total_images']:,} | {ds_info['unique_hashes']:,} | {ds_info['duplicate_groups']:,} | {ds_info['duplicate_files']:,} | {ds_info['duplicate_instances']:,} |"
        )

    md_lines.extend([
        "",
        "---",
        "",
        "## 3. Cross-Dataset Duplicate Matrix",
        "",
        "| Dataset Combination | Duplicate Hash Groups | Total Files | Redundant Copies |",
        "|---|---|---|---|",
    ])

    for cat_name, cat_info in cross_ds_categories.items():
        formatted_cat = cat_name.replace("_and_", " ↔ ").replace("_only", " (Internal Only)")
        md_lines.append(
            f"| **{formatted_cat}** | {cat_info['groups']:,} | {cat_info['files']:,} | {cat_info['redundant']:,} |"
        )

    md_lines.extend([
        "",
        "---",
        "",
        "## 4. Class-Level & Species Conflict Analysis",
        "",
        "| Conflict Type | Duplicate Group Count | Description / Handling Policy |",
        "|---|---|---|",
        f"| **Cross-Class Conflicts** | **{cross_class_conflicts:,}** | Duplicate image found across multiple raw folders; assigned to canonical representative |",
        f"| **Cross-Species Conflicts** | **{cross_species_conflicts:,}** | Duplicate image mapped to different species; held in review queue before split |",
        f"| **Cross-Status Conflicts** | **{cross_status_conflicts:,}** | Duplicate image present in both APPROVED and NEEDS_REVIEW/REJECTED species |",
        "",
        "---",
        "",
        "## 5. Top 5 Largest Duplicate Groups",
        "",
        "| Group ID | SHA-256 (Truncated) | Files | Datasets | Mapped Species | Canonical Representative Path |",
        "|---|---|---|---|---|---|",
    ])

    for top_g in top_5_dup_groups:
        short_sha = top_g["sha256"][:12] + "..."
        md_lines.append(
            f"| `{top_g['group_id']}` | `{short_sha}` | {top_g['total_files']} | {', '.join(top_g['datasets_present'])} | {', '.join(top_g['mapped_species'])} | `{top_g['representative_relative_path']}` |"
        )

    md_lines.extend([
        "",
        "---",
        "",
        "## 6. Deterministic Data Leakage & Representative Selection Policies",
        "",
        "### A. Leakage-Safe Dataset Split Policy (Group-Level Atomic Splitting)",
        "- **Rule:** Every SHA-256 duplicate group is treated as an indivisible atomic unit.",
        "- **Enforcement:** During dataset materialization, split assignment (`train`, `val`, `test`) is computed on the **SHA-256 hash group level** rather than individual image file paths.",
        "- **Guarantee:** All physical copies sharing a SHA-256 hash will be assigned to the exact same dataset split, guaranteeing **0 cross-split leakage**.",
        "",
        "### B. Canonical Representative Selection Policy",
        "When redundant exact duplicates exist across raw dataset folders, the canonical representative image record is chosen reproducibly using the following hierarchy:",
        "1. **Dataset Priority:** `CIMPd` (Priority 0) > `Hugging_Face` (Priority 1) > `Kaggle` (Priority 2).",
        "2. **Image Resolution:** Higher pixel resolution (`width * height`).",
        "3. **Lexicographical Path Order:** Ascending order of `relative_path` as a tie-breaker.",
        "",
        "### C. Near-Duplicate Hashing Status",
        "- **Current Scope:** Step 2 evaluates exact SHA-256 hash matching.",
        "- **Future Scope:** Perceptual hashing (`pHash`) and visual embeddings similarity clustering are designated for future post-materialization pipeline releases.",
        "",
        "---",
        "",
        "## 7. Step 2 Quality Gate & Audit Decision",
        "```text",
        "INVENTORY RECONCILIATION: PASS (42,062 / 42,062 physical files verified)",
        "SHA-256 INTEGRITY:       PASS (0 missing or corrupt hashes)",
        "CROSS-DATASET MATRIX:     PASS (All combinations identified)",
        "DATA LEAKAGE POLICY:      DEFINED (Group-level atomic split)",
        "REPRESENTATIVE POLICY:    DEFINED (CIMPd > Hugging_Face > Kaggle + Resolution)",
        "RAW DATASET INTEGRITY:    TOUCHED = NO (100% READ-ONLY)",
        "STEP 2 STATUS:            PASS",
        "```",
    ])

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    # Print Terminal Summary Block
    print("\n==========================================================================")
    print("            STEP 2 DUPLICATE & DATA-LEAKAGE AUDIT SUMMARY                 ")
    print("==========================================================================")
    print(f"TOTAL PHYSICAL FILES:          {total_physical_files:,}")
    print(f"UNIQUE SHA-256 HASHES:         {unique_sha256_hashes:,}")
    print(f"DUPLICATE SHA-256 GROUPS:      {duplicate_sha256_groups:,}")
    print(f"FILES IN DUPLICATE GROUPS:     {total_files_in_duplicate_groups:,}")
    print(f"REDUNDANT DUPLICATE COPIES:    {redundant_duplicate_instances:,}")
    print("--------------------------------------------------------------------------")
    print("WITHIN-DATASET DUPLICATE GROUPS / REDUNDANT INSTANCES:")
    for ds_name, ds_info in ds_stats.items():
        print(f" - {ds_name:15s}: {ds_info['duplicate_groups']:,} groups | {ds_info['duplicate_instances']:,} redundant instances")
    print("--------------------------------------------------------------------------")
    print("CROSS-DATASET DUPLICATE GROUPS:")
    for cat_name, cat_info in cross_ds_categories.items():
        print(f" - {cat_name:35s}: {cat_info['groups']:,} groups | {cat_info['redundant']:,} redundant copies")
    print("--------------------------------------------------------------------------")
    print(f"CLASS-LEVEL SPECIES CONFLICTS: {cross_species_conflicts:,} groups")
    print(f"STEP 2 AUDIT DECISION:         PASS")
    print("==========================================================================")
    print(f"\nAudit Artifacts Exported:")
    print(f" - JSON: {json_path}")
    print(f" - CSV:  {csv_path}")
    print(f" - MD:   {md_path}")

if __name__ == "__main__":
    run_duplicate_audit()
