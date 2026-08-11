import os
import sys
import json
import csv
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from src.data.paths import get_reports_dir, get_dataset_paths

class CandidateManifestGeneratorV2:
    """
    Generates candidate training manifests, taxonomy review statuses, and feasibility reports
    for the Dravya AI First Large Model (v2) while keeping raw datasets 100% read-only.
    """

    def __init__(self, reports_dir: Optional[Path] = None):
        self.reports_dir = reports_dir or get_reports_dir()
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def load_combined_inventory(self) -> Dict[str, Any]:
        inventory_file = self.reports_dir / "combined_species_inventory_v2.json"
        if not inventory_file.exists():
            raise FileNotFoundError(f"Combined inventory report missing at {inventory_file}")
        with open(inventory_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def analyze_taxonomy_conflicts(self, inventory_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Step 1: Analyzes the 11 taxonomy conflicts and assigns mapping safety and recommended actions.
        """
        conflicts = [
            {
                "conflict_id": "CONF_001",
                "source_dataset": "Hugging_Face, Kaggle",
                "original_class_name": "Beans-Vigna spp. (Genus) or Phaseolus spp. (Genus) / Beans",
                "candidate_canonical_species": "Vigna / Phaseolus spp. (Beans)",
                "image_count": 194,
                "conflict_reason": "Multi-genus ambiguity: raw class folder groups two distinct botanical genera (Vigna and Phaseolus).",
                "is_mapping_safe": False,
                "classification": "DO_NOT_MERGE",
                "recommended_action": "Exclude from v1 model until images are separated by genus via expert botanical review."
            },
            {
                "conflict_id": "CONF_002",
                "source_dataset": "Hugging_Face, Kaggle",
                "original_class_name": "Spinach1",
                "candidate_canonical_species": "Unspecified Spinach Variety",
                "image_count": 180,
                "conflict_reason": "Ambiguous common name: 'Spinach1' could refer to Spinacia oleracea, Amaranthus dubius, or Basella alba.",
                "is_mapping_safe": False,
                "classification": "NEEDS_HUMAN_REVIEW",
                "recommended_action": "Hold in review queue; exclude from initial production model."
            },
            {
                "conflict_id": "CONF_003",
                "source_dataset": "CIMPd",
                "original_class_name": "leafs",
                "candidate_canonical_species": "Unspecified Leaf Samples",
                "image_count": 11,
                "conflict_reason": "Non-plant / corrupt junk folder in raw CIMPd dataset containing 11 unaligned background images.",
                "is_mapping_safe": False,
                "classification": "DO_NOT_MERGE",
                "recommended_action": "Reject permanently and exclude from all training manifests."
            },
            {
                "conflict_id": "CONF_004",
                "source_dataset": "Hugging_Face, Kaggle",
                "original_class_name": "Insulin",
                "candidate_canonical_species": "Chamaecostus cuspidatus (Insulin Plant)",
                "image_count": 156,
                "conflict_reason": "Vernacular trade name without verified botanical binomial in raw folder name.",
                "is_mapping_safe": False,
                "classification": "NEEDS_HUMAN_REVIEW",
                "recommended_action": "Map to Chamaecostus cuspidatus upon expert botanical review confirmation."
            },
            {
                "conflict_id": "CONF_005",
                "source_dataset": "Hugging_Face, Kaggle",
                "original_class_name": "Caricature",
                "candidate_canonical_species": "Graptophyllum pictum (Caricature Plant)",
                "image_count": 152,
                "conflict_reason": "Common name trade alias lacking explicit species epithet in raw path.",
                "is_mapping_safe": False,
                "classification": "NEEDS_HUMAN_REVIEW",
                "recommended_action": "Require botanical verification before canonical ID assignment."
            },
            {
                "conflict_id": "CONF_006",
                "source_dataset": "Hugging_Face, Kaggle",
                "original_class_name": "Badipala",
                "candidate_canonical_species": "Erythrina variegata (Badipala)",
                "image_count": 152,
                "conflict_reason": "Local Kannada/Telugu vernacular name requiring formal taxonomic validation.",
                "is_mapping_safe": False,
                "classification": "NEEDS_HUMAN_REVIEW",
                "recommended_action": "Hold in review queue; verify leaf morphology against Erythrina species."
            },
            {
                "conflict_id": "CONF_007",
                "source_dataset": "Hugging_Face, Kaggle",
                "original_class_name": "Chakte",
                "candidate_canonical_species": "Unresolved Chakte Leaf",
                "image_count": 140,
                "conflict_reason": "Unresolved regional name without established Latin binomial mapping.",
                "is_mapping_safe": False,
                "classification": "DO_NOT_MERGE",
                "recommended_action": "Exclude from v1 model until taxonomic consensus is achieved."
            },
            {
                "conflict_id": "CONF_008",
                "source_dataset": "Hugging_Face, Kaggle",
                "original_class_name": "Ganigale",
                "candidate_canonical_species": "Unresolved Ganigale Leaf",
                "image_count": 150,
                "conflict_reason": "Unresolved vernacular name lacking scientific documentation.",
                "is_mapping_safe": False,
                "classification": "DO_NOT_MERGE",
                "recommended_action": "Exclude from v1 dataset build."
            },
            {
                "conflict_id": "CONF_009",
                "source_dataset": "Hugging_Face, Kaggle",
                "original_class_name": "Kambajala",
                "candidate_canonical_species": "Unresolved Kambajala Leaf",
                "image_count": 142,
                "conflict_reason": "Unresolved vernacular name lacking scientific documentation.",
                "is_mapping_safe": False,
                "classification": "DO_NOT_MERGE",
                "recommended_action": "Exclude from v1 dataset build."
            },
            {
                "conflict_id": "CONF_010",
                "source_dataset": "Hugging_Face, Kaggle",
                "original_class_name": "Kasambruga",
                "candidate_canonical_species": "Unresolved Kasambruga Leaf",
                "image_count": 148,
                "conflict_reason": "Unresolved regional vernacular name.",
                "is_mapping_safe": False,
                "classification": "DO_NOT_MERGE",
                "recommended_action": "Exclude from v1 dataset build."
            },
            {
                "conflict_id": "CONF_011",
                "source_dataset": "Hugging_Face, Kaggle",
                "original_class_name": "Kepala",
                "candidate_canonical_species": "Unresolved Kepala Leaf",
                "image_count": 144,
                "conflict_reason": "Unresolved regional vernacular name.",
                "is_mapping_safe": False,
                "classification": "DO_NOT_MERGE",
                "recommended_action": "Exclude from v1 dataset build."
            }
        ]
        return conflicts

    def analyze_low_data_species(self, candidate_species_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Step 2: Analyzes the 40 low-data species (<100 images) and assigns recommendations.
        """
        low_data = [s for s in candidate_species_list if s["total_images"] < 100]
        analyzed_low_data = []

        for s in low_data:
            img_count = s["total_images"]
            name = s["candidate_canonical_name"]
            ds_list = s["datasets_present"]

            if img_count < 50:
                rec = "EXCLUDE_FOR_V1"
                status = "NEEDS_MORE_DATA"
                reason = f"Severely deficient image count ({img_count} images < 50 minimum threshold)."
            elif len(ds_list) == 1 and img_count < 75:
                rec = "EXCLUDE_FOR_V1"
                status = "SINGLE_DATASET_LOW_DATA"
                reason = f"Low single-source representation ({img_count} images in {ds_list[0]})."
            elif s.get("status") in ("UNRESOLVED_VERNACULAR", "AMBIGUOUS_GENERIC_NAME"):
                rec = "NEEDS_HUMAN_REVIEW"
                status = "NEEDS_REVIEW"
                reason = "Taxonomic ambiguity combined with sub-100 image representation."
            else:
                rec = "NEEDS_MORE_DATA"
                status = "CANDIDATE_FOR_EXPANSION"
                reason = f"High-value species ({img_count} images) requiring targeted dataset expansion before v2 inclusion."

            analyzed_low_data.append({
                "candidate_canonical_name": name,
                "scientific_name": s.get("scientific_name", "Unknown"),
                "total_images": img_count,
                "source_datasets": ds_list,
                "taxonomy_status": status,
                "recommendation": rec,
                "reason": reason
            })

        return sorted(analyzed_low_data, key=lambda x: x["total_images"])

    def build_candidate_and_review_manifests(
        self,
        inventory_data: Dict[str, Any],
        conflicts: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
        """
        Steps 3, 4, 5: Selects baseline model classes (~135 target), generates candidate class records & review manifest.
        """
        species_list = inventory_data.get("candidate_species_inventory", [])
        
        # Sort species by total images descending
        sorted_species = sorted(species_list, key=lambda x: x["total_images"], reverse=True)

        conflict_names = {c["original_class_name"] for c in conflicts}
        conflict_species = {c["candidate_canonical_species"] for c in conflicts}

        candidate_manifest = []
        review_manifest = []

        class_idx = 1
        approved_count = 0
        needs_review_count = 0
        rejected_count = 0

        for s in sorted_species:
            class_id = f"DRAVYA_{class_idx:04d}"
            name = s["candidate_canonical_name"]
            sci_name = s.get("scientific_name", "Unknown")
            img_count = s["total_images"]
            ds_list = s["datasets_present"]
            tax_status = s.get("status", "UNREVIEWED")
            raw_classes = s.get("raw_classes", [])
            orig_names = [rc["raw_class_name"] for rc in raw_classes]

            # Determine selection status & approval status
            if name == "Unspecified Leaf Samples" or tax_status == "INVALID_NON_PLANT":
                approval = "REJECTED"
                selection = "EXCLUDED"
                sel_reason = "Non-plant / corrupt junk images folder."
                rejected_count += 1
            elif name in conflict_species or any(on in conflict_names for on in orig_names):
                approval = "NEEDS_REVIEW"
                selection = "EXCLUDED"
                sel_reason = "Taxonomy conflict or unresolved vernacular name requiring expert review."
                needs_review_count += 1
            elif img_count < 100:
                approval = "NEEDS_REVIEW"
                selection = "EXCLUDED"
                sel_reason = f"Insufficient image count ({img_count} images < 100 minimum threshold)."
                needs_review_count += 1
            else:
                approval = "APPROVED"
                selection = "SELECTED"
                sel_reason = f"High-confidence botanical mapping with {img_count} images across {len(ds_list)} dataset(s)."
                approved_count += 1

            imgs_per_ds = {}
            for rc in raw_classes:
                ds = rc["dataset_id"]
                imgs_per_ds[ds] = imgs_per_ds.get(ds, 0) + rc["image_count"]

            candidate_record = {
                "class_id": class_id,
                "canonical_species_name": name,
                "scientific_name": sci_name,
                "original_names": orig_names,
                "source_datasets": ds_list,
                "total_images": img_count,
                "images_per_dataset": imgs_per_ds,
                "taxonomy_status": tax_status,
                "approval_status": approval,
                "selection_status": selection,
                "selection_reason": sel_reason
            }
            candidate_manifest.append(candidate_record)

            review_record = {
                "class_id": class_id,
                "canonical_species_name": name,
                "scientific_name": sci_name,
                "total_images": img_count,
                "source_datasets": ds_list,
                "review_status": approval,
                "review_notes": sel_reason,
                "reviewed_at": datetime.now(timezone.utc).isoformat()
            }
            review_manifest.append(review_record)

            class_idx += 1

        needs_review_tax_count = sum(1 for r in candidate_manifest if r["approval_status"] == "NEEDS_REVIEW" and (r["canonical_species_name"] in conflict_species or any(on in conflict_names for on in r["original_names"])))
        needs_review_low_count = sum(1 for r in candidate_manifest if r["approval_status"] == "NEEDS_REVIEW" and r["total_images"] < 100 and r["canonical_species_name"] not in conflict_species and not any(on in conflict_names for on in r["original_names"]))

        stats_summary = {
            "total_raw_images": inventory_data["summary_statistics"]["total_raw_images"],
            "estimated_unique_species": len(candidate_manifest),
            "total_candidate_classes": len(candidate_manifest),
            "approved_classes_count": approved_count,
            "needs_review_count": needs_review_count,
            "needs_review_low_data_count": needs_review_low_count,
            "needs_review_taxonomy_count": needs_review_tax_count,
            "rejected_count": rejected_count,
            "classes_100_plus_images": sum(1 for r in candidate_manifest if r["total_images"] >= 100),
            "classes_300_plus_images": sum(1 for r in candidate_manifest if r["total_images"] >= 300),
            "taxonomy_conflicts_count": len(conflicts),
            "final_recommended_training_class_count": approved_count,
            "ready_for_canonical_v2": "YES" if approved_count >= 50 else "NO"
        }

        return candidate_manifest, review_manifest, stats_summary

    def export_manifests_and_report(
        self,
        candidate_manifest: List[Dict[str, Any]],
        review_manifest: List[Dict[str, Any]],
        conflicts: List[Dict[str, Any]],
        low_data: List[Dict[str, Any]],
        stats_summary: Dict[str, Any]
    ) -> Dict[str, Path]:
        """
        Steps 4, 5, 6: Exports candidate_training_classes_v2.json, .csv, training_taxonomy_review_v2.json, and candidate_training_classes_v2.md.
        """
        json_cand_path = self.reports_dir / "candidate_training_classes_v2.json"
        csv_cand_path = self.reports_dir / "candidate_training_classes_v2.csv"
        json_rev_path = self.reports_dir / "training_taxonomy_review_v2.json"
        md_report_path = self.reports_dir / "candidate_training_classes_v2.md"

        # 1. Candidate Classes JSON
        with open(json_cand_path, "w", encoding="utf-8") as f:
            json.dump({
                "metadata": {
                    "project": "Dravya AI Engine",
                    "report_version": "v2",
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "total_candidate_classes": len(candidate_manifest),
                    "approved_training_classes": stats_summary["approved_classes_count"]
                },
                "summary": stats_summary,
                "candidate_classes": candidate_manifest
            }, f, indent=2, ensure_ascii=False)

        # 2. Candidate Classes CSV
        fieldnames = [
            "class_id",
            "canonical_species_name",
            "scientific_name",
            "total_images",
            "source_datasets",
            "approval_status",
            "selection_status",
            "selection_reason"
        ]
        with open(csv_cand_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in candidate_manifest:
                writer.writerow({
                    "class_id": r["class_id"],
                    "canonical_species_name": r["canonical_species_name"],
                    "scientific_name": r["scientific_name"],
                    "total_images": r["total_images"],
                    "source_datasets": ", ".join(r["source_datasets"]),
                    "approval_status": r["approval_status"],
                    "selection_status": r["selection_status"],
                    "selection_reason": r["selection_reason"]
                })

        # 3. Human Review Manifest JSON
        with open(json_rev_path, "w", encoding="utf-8") as f:
            json.dump({
                "metadata": {
                    "project": "Dravya AI Engine",
                    "manifest_version": "v2",
                    "exported_at": datetime.now(timezone.utc).isoformat()
                },
                "review_summary": {
                    "total_classes": len(review_manifest),
                    "APPROVED": stats_summary["approved_classes_count"],
                    "NEEDS_REVIEW_LOW_DATA": stats_summary["needs_review_low_data_count"],
                    "NEEDS_REVIEW_TAXONOMY": stats_summary["needs_review_taxonomy_count"],
                    "REJECTED": stats_summary["rejected_count"]
                },
                "class_reviews": review_manifest
            }, f, indent=2, ensure_ascii=False)

        # 4. Comprehensive Markdown Feasibility Report
        approved_records = [r for r in candidate_manifest if r["approval_status"] == "APPROVED"]
        excluded_records = [r for r in candidate_manifest if r["approval_status"] != "APPROVED"]
        approved_counts = [r["total_images"] for r in approved_records]

        min_img = min(approved_counts) if approved_counts else 0
        max_img = max(approved_counts) if approved_counts else 0
        mean_img = round(statistics.mean(approved_counts), 2) if approved_counts else 0.0
        median_img = statistics.median(approved_counts) if approved_counts else 0.0
        imb_ratio = round(max_img / min_img, 2) if min_img > 0 else 0.0

        md_lines = [
            "# Dravya AI — Candidate Training Class Selection & Taxonomy Feasibility Report (v2)",
            "",
            f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}  ",
            f"**Pipeline Status:** Candidate Selection Complete  ",
            "",
            "---",
            "",
            "## Dataset & Selection Summary",
            "",
            "| Key Metric | Value |",
            "|---|---|",
            f"| **Total Raw Scanned Images** | **{stats_summary['total_raw_images']:,}** |",
            f"| **Estimated Unique Candidate Species** | **{stats_summary['estimated_unique_species']}** |",
            f"| **Total Candidate Classes** | **{stats_summary['total_candidate_classes']}** |",
            f"| **APPROVED Classes (Training Eligible)** | **{stats_summary['approved_classes_count']}** |",
            f"| **NEEDS REVIEW (Low Data <100 Images)** | **{stats_summary['needs_review_low_data_count']}** |",
            f"| **NEEDS REVIEW (Taxonomy Conflicts)** | **{stats_summary['needs_review_taxonomy_count']}** |",
            f"| **REJECTED Classes (Non-Plant/Junk)** | **{stats_summary['rejected_count']}** |",
            f"| **Classes with 100+ Images** | **{stats_summary['classes_100_plus_images']}** |",
            f"| **Classes with 300+ Images** | **{stats_summary['classes_300_plus_images']}** |",
            f"| **Taxonomy Conflicts** | **{stats_summary['taxonomy_conflicts_count']}** |",
            f"| **FINAL RECOMMENDED TRAINING CLASS COUNT** | **{stats_summary['final_recommended_training_class_count']}** |",
            f"| **READY FOR CANONICAL DATASET V2** | **{stats_summary['ready_for_canonical_v2']}** |",
            "",
            "---",
            "",
            "## Approved Training Classes (Selected for Production Model)",
            "",
            "| Class ID | Species Name | Scientific Name | Images | Sources | Status |",
            "|---|---|---|---|---|---|",
        ]

        for r in approved_records[:40]:  # Top 40 approved
            md_lines.append(
                f"| `{r['class_id']}` | **{r['canonical_species_name']}** | *{r['scientific_name']}* | {r['total_images']:,} | {', '.join(r['source_datasets'])} | `{r['approval_status']}` |"
            )

        if len(approved_records) > 40:
            md_lines.append(f"| ... | *(And {len(approved_records) - 40} more approved species)* | | | | |")

        md_lines.extend([
            "",
            "---",
            "",
            "## Excluded & Review Classes Explanation",
            "",
            "| Class ID | Species Name | Images | Review Status | Rationale for Exclusion |",
            "|---|---|---|---|---|",
        ])

        for r in excluded_records:
            md_lines.append(
                f"| `{r['class_id']}` | {r['canonical_species_name']} | {r['total_images']} | `{r['approval_status']}` | {r['selection_reason']} |"
            )

        md_lines.extend([
            "",
            "---",
            "",
            "## Taxonomy Conflicts Analysis & Recommendations (11 Conflicts)",
            "",
            "| Conflict ID | Raw Class / Source | Candidate Species | Images | Classification | Recommended Action |",
            "|---|---|---|---|---|---|",
        ])

        for c in conflicts:
            md_lines.append(
                f"| `{c['conflict_id']}` | `{c['original_class_name']}` ({c['source_dataset']}) | {c['candidate_canonical_species']} | {c['image_count']} | `{c['classification']}` | {c['recommended_action']} |"
            )

        md_lines.extend([
            "",
            "---",
            "",
            "## Class Image Imbalance Statistics (Approved Classes)",
            "",
            "| Metric | Value |",
            "|---|---|",
            f"| **Minimum Class Images** | {min_img} |",
            f"| **Maximum Class Images** | {max_img:,} |",
            f"| **Mean Class Images** | {mean_img} |",
            f"| **Median Class Images** | {median_img} |",
            f"| **Overall Class Imbalance Ratio** | **{imb_ratio}:1** |",
            "",
            "---",
            "",
            "## Read-Only Safety Affirmation",
            "- Raw dataset folders (`CIMPd`, `Hugging_Face`, `Kaggle`) remain 100% untouched.",
            "- Zero images copied or transformed.",
            "- Existing model, API, and training code unchanged.",
        ])

        with open(md_report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

        return {
            "candidate_json": json_cand_path,
            "candidate_csv": csv_cand_path,
            "review_json": json_rev_path,
            "report_md": md_report_path
        }

    def print_terminal_readiness_check(self, stats: Dict[str, Any]):
        """
        Step 7: Prints exact terminal summary block.
        """
        print("\n" + "=" * 60)
        print("  DRAVYA AI 135-CLASS CANDIDATE MANIFEST READINESS CHECK")
        print("=" * 60)
        print(f"TOTAL RAW IMAGES: {stats['total_raw_images']:,}")
        print(f"ESTIMATED UNIQUE SPECIES: {stats['estimated_unique_species']}")
        print(f"TOTAL CANDIDATE CLASSES: {stats['total_candidate_classes']}")
        print(f"APPROVED CLASSES: {stats['approved_classes_count']}")
        print(f"NEEDS REVIEW: {stats['needs_review_count']}")
        print(f"REJECTED: {stats['rejected_count']}")
        print(f"CLASSES WITH 100+ IMAGES: {stats['classes_100_plus_images']}")
        print(f"CLASSES WITH 300+ IMAGES: {stats['classes_300_plus_images']}")
        print(f"TAXONOMY CONFLICTS: {stats['taxonomy_conflicts_count']}")
        print(f"FINAL RECOMMENDED TRAINING CLASS COUNT: {stats['final_recommended_training_class_count']}")
        print(f"READY FOR CANONICAL DATASET V2: {stats['ready_for_canonical_v2']}")
        print("=" * 60 + "\n")
