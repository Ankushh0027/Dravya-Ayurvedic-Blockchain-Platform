import os
import json
import csv
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

def parse_class_name(dataset_id: str, original_class_name: str) -> Dict[str, Any]:
    """
    Parses class folder names to extract plant candidates, health conditions,
    common names, scientific names, and normalized representations.
    Preserves original class names intact.
    """
    # Extract leaf directory name if path contains folder separators
    normalized_path_str = original_class_name.replace("/", os.sep).replace("\\", os.sep)
    leaf_folder_name = os.path.basename(normalized_path_str)

    health_condition = "Unknown"
    plant_name_raw = leaf_folder_name

    # CIMPd health condition suffix parsing (.H, .U, ,U)
    if dataset_id == "CIMPd" or leaf_folder_name.endswith(".H") or leaf_folder_name.endswith(".U") or leaf_folder_name.endswith(",U"):
        if leaf_folder_name.endswith(".H"):
            health_condition = "Healthy"
            plant_name_raw = leaf_folder_name[:-2]
        elif leaf_folder_name.endswith(".U") or leaf_folder_name.endswith(",U"):
            health_condition = "Unhealthy"
            plant_name_raw = leaf_folder_name[:-2]

    common_name_candidate = plant_name_raw
    scientific_name_candidate = None

    # Try extracting binomial scientific name (e.g. Aloevera-Aloe barbadensis)
    for sep in ["-", "_"]:
        if sep in plant_name_raw:
            parts = [p.strip() for p in plant_name_raw.split(sep) if p.strip()]
            if len(parts) >= 2:
                second_part = parts[1]
                words = second_part.split()
                if len(words) >= 2 and words[0][0].isupper():
                    common_name_candidate = parts[0]
                    scientific_name_candidate = second_part
                    break

    def normalize_str(s: Optional[str]) -> str:
        if not s:
            return ""
        cleaned = s.lower().replace("_", " ").replace("-", " ").replace(".", " ").replace(",", " ")
        return " ".join(cleaned.split())

    normalized_common = normalize_str(common_name_candidate)
    normalized_scientific = normalize_str(scientific_name_candidate) if scientific_name_candidate else ""
    normalized_full = normalize_str(plant_name_raw)

    return {
        "dataset_id": dataset_id,
        "original_class_name": original_class_name,
        "leaf_folder_name": leaf_folder_name,
        "health_condition": health_condition,
        "plant_name_candidate": plant_name_raw,
        "common_name_candidate": common_name_candidate,
        "scientific_name_candidate": scientific_name_candidate,
        "normalized_common": normalized_common,
        "normalized_scientific": normalized_scientific,
        "normalized_full": normalized_full
    }

class ClassHarmonizationAnalyzer:
    """
    Analyzes apparent classes across datasets to detect taxonomy overlaps and generate
    review-oriented harmonization candidates without executing automatic merges.
    """

    def __init__(self, inventories: List[Dict[str, Any]]):
        self.inventories = inventories

    def analyze(self) -> Dict[str, Any]:
        parsed_entries: List[Dict[str, Any]] = []

        for inv in self.inventories:
            ds_id = inv.get("dataset_id", "")
            class_counts = inv.get("image_count_per_class", {})
            root_path = inv.get("root_path", "")

            for orig_class_name, img_count in class_counts.items():
                parsed = parse_class_name(ds_id, orig_class_name)
                parsed["image_count"] = img_count
                parsed["source_path"] = os.path.join(root_path, orig_class_name)
                parsed_entries.append(parsed)

        total_classes_analyzed = len(parsed_entries)

        # Detect candidate matches between classes of DIFFERENT datasets
        candidate_matches: List[Dict[str, Any]] = []
        strong_matches_count = 0
        uncertain_matches_count = 0
        cimpd_health_classes_count = sum(1 for e in parsed_entries if e["health_condition"] in ("Healthy", "Unhealthy"))

        # Map each entry index to list of candidate matches
        entry_matches_map: Dict[int, List[Dict[str, Any]]] = {i: [] for i in range(len(parsed_entries))}

        for i in range(len(parsed_entries)):
            entry_a = parsed_entries[i]
            for j in range(i + 1, len(parsed_entries)):
                entry_b = parsed_entries[j]

                # Compare across distinct datasets
                if entry_a["dataset_id"] == entry_b["dataset_id"]:
                    continue

                reason = None
                confidence = None

                norm_comm_a = entry_a["normalized_common"]
                norm_comm_b = entry_b["normalized_common"]
                norm_sci_a = entry_a["normalized_scientific"]
                norm_sci_b = entry_b["normalized_scientific"]
                norm_full_a = entry_a["normalized_full"]
                norm_full_b = entry_b["normalized_full"]

                # 1. Both common & scientific match
                if norm_sci_a and norm_sci_b and norm_sci_a == norm_sci_b and norm_comm_a == norm_comm_b:
                    reason = "common_and_scientific_name_match"
                    confidence = "HIGH"
                # 2. Scientific name match (scientific to scientific OR scientific to common/full)
                elif (norm_sci_a and norm_sci_b and norm_sci_a == norm_sci_b) or \
                     (norm_sci_a and (norm_sci_a == norm_comm_b or norm_sci_a == norm_full_b)) or \
                     (norm_sci_b and (norm_sci_b == norm_comm_a or norm_sci_b == norm_full_a)):
                    reason = "scientific_name_match"
                    confidence = "HIGH"
                # 3. CIMPd health suffix match
                elif (entry_a["dataset_id"] == "CIMPd" or entry_b["dataset_id"] == "CIMPd") and (norm_comm_a == norm_comm_b or norm_full_a == norm_full_b):
                    reason = "CIMPd_health_suffix_match"
                    confidence = "HIGH"
                # 4. Exact normalized name match
                elif norm_comm_a == norm_comm_b or norm_full_a == norm_full_b:
                    reason = "exact_normalized_name"
                    confidence = "HIGH"
                # 5. Common name match
                elif norm_comm_a and norm_comm_b and norm_comm_a == norm_comm_b:
                    reason = "common_name_match"
                    confidence = "HIGH"
                # 6. Possible name similarity (substring / minor variation)
                elif norm_comm_a and norm_comm_b and (norm_comm_a in norm_comm_b or norm_comm_b in norm_comm_a) and min(len(norm_comm_a), len(norm_comm_b)) >= 4:
                    reason = "possible_name_similarity"
                    confidence = "MEDIUM"


                if reason and confidence:
                    match_record = {
                        "dataset_a": entry_a["dataset_id"],
                        "class_a": entry_a["original_class_name"],
                        "dataset_b": entry_b["dataset_id"],
                        "class_b": entry_b["original_class_name"],
                        "candidate_reason": reason,
                        "confidence": confidence,
                        "review_status": "UNREVIEWED"
                    }
                    candidate_matches.append(match_record)

                    if confidence == "HIGH":
                        strong_matches_count += 1
                    else:
                        uncertain_matches_count += 1

                    # Attach match summaries to entry
                    entry_matches_map[i].append({
                        "target_dataset": entry_b["dataset_id"],
                        "target_class": entry_b["original_class_name"],
                        "reason": reason,
                        "confidence": confidence
                    })
                    entry_matches_map[j].append({
                        "target_dataset": entry_a["dataset_id"],
                        "target_class": entry_a["original_class_name"],
                        "reason": reason,
                        "confidence": confidence
                    })

        # Build proposed taxonomy review structure for ALL 331 classes
        class_entries = []
        for i, entry in enumerate(parsed_entries):
            class_entries.append({
                "source_dataset": entry["dataset_id"],
                "original_class_name": entry["original_class_name"],
                "image_count": entry["image_count"],
                "source_path": entry["source_path"],
                "canonical_plant_id": None,  # MUST remain null/None
                "canonical_common_name": entry["common_name_candidate"],
                "canonical_scientific_name": entry["scientific_name_candidate"],
                "health_condition": entry["health_condition"],
                "mapping_status": "UNREVIEWED",
                "evidence": f"Parsed candidate from {entry['dataset_id']} class name.",
                "review_notes": None,
                "candidate_matches": entry_matches_map[i]
            })

        scan_timestamp = datetime.now(timezone.utc).isoformat()

        return {
            "scan_timestamp": scan_timestamp,
            "datasets": [inv.get("dataset_id") for inv in self.inventories],
            "total_classes_analyzed": total_classes_analyzed,
            "candidate_matches_count": len(candidate_matches),
            "strong_matches_count": strong_matches_count,
            "uncertain_matches_count": uncertain_matches_count,
            "cimpd_health_classes_count": cimpd_health_classes_count,
            "candidate_matches": candidate_matches,
            "class_entries": class_entries
        }

    def export_reports(self, analysis_results: Dict[str, Any], output_dir: str = r"C:\Dravya-AI-Engine\reports\dataset_analysis") -> Dict[str, str]:
        os.makedirs(output_dir, exist_ok=True)
        csv_path = os.path.join(output_dir, "class_harmonization_candidates.csv")
        json_path = os.path.join(output_dir, "class_harmonization_analysis.json")

        # Export CSV candidates report
        fieldnames = ["dataset_a", "class_a", "dataset_b", "class_b", "candidate_reason", "confidence", "review_status"]
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for m in analysis_results.get("candidate_matches", []):
                writer.writerow(m)

        # Export JSON analysis structure
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)

        return {
            "csv_path": csv_path,
            "json_path": json_path
        }

    @staticmethod
    def format_terminal_summary(analysis_results: Dict[str, Any]) -> str:
        lines = [
            "==========================================================================",
            "        DRAVYA AI TAXONOMY / CLASS HARMONIZATION ANALYSIS SUMMARY         ",
            "==========================================================================",
            f"Datasets Analyzed:                   {', '.join(analysis_results.get('datasets', []))}",
            f"Total Apparent Classes Analyzed:     {analysis_results.get('total_classes_analyzed', 0)}",
            f"Total Overlap Candidate Matches:     {analysis_results.get('candidate_matches_count', 0)}",
            f"  - Strong Matches (HIGH):           {analysis_results.get('strong_matches_count', 0)}",
            f"  - Uncertain Matches (MEDIUM/LOW):   {analysis_results.get('uncertain_matches_count', 0)}",
            f"CIMPd Health-Condition Classes:      {analysis_results.get('cimpd_health_classes_count', 0)}",
            "=========================================================================="
        ]
        return "\n".join(lines)
