import os
import json
import csv
from typing import List, Dict, Any

class ManifestGenerator:
    """
    Generates dataset inventory reports in JSON, CSV, and terminal summary formats.
    """

    def __init__(self, output_dir: str = r"C:\Dravya-AI-Engine\reports\dataset_analysis"):
        self.output_dir = os.path.abspath(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def export_json(self, inventories: List[Dict[str, Any]], filename: str = "dataset_inventory.json") -> str:
        """
        Exports machine-readable dataset inventory JSON file.
        """
        file_path = os.path.join(self.output_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({"inventories": inventories}, f, indent=2, ensure_ascii=False)
        return file_path

    def export_csv(self, inventories: List[Dict[str, Any]], filename: str = "class_distribution.csv") -> str:
        """
        Exports class distribution CSV file.
        """
        file_path = os.path.join(self.output_dir, filename)
        fieldnames = ["dataset_id", "class_name", "image_count"]

        with open(file_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for inv in inventories:
                dataset_id = inv.get("dataset_id", "")
                class_counts = inv.get("image_count_per_class", {})
                for class_name, count in sorted(class_counts.items()):
                    writer.writerow({
                        "dataset_id": dataset_id,
                        "class_name": class_name,
                        "image_count": count
                    })
        return file_path

    def format_terminal_summary(self, inventories: List[Dict[str, Any]]) -> str:
        """
        Formats human-readable inventory summary table and text.
        """
        lines = []
        lines.append("==========================================================================")
        lines.append("                   DRAVYA AI DATASET INVENTORY SUMMARY                   ")
        lines.append("==========================================================================")

        total_all_images = 0
        total_all_classes = 0

        for inv in inventories:
            ds_id = inv.get("dataset_id")
            root_path = inv.get("root_path")
            tot_imgs = inv.get("total_images", 0)
            tot_classes = inv.get("total_apparent_classes", 0)
            exts = inv.get("image_extensions", {})
            empty_dirs = len(inv.get("empty_class_directories", []))
            non_imgs = len(inv.get("non_image_files", []))
            archives = len(inv.get("archive_files", []))

            total_all_images += tot_imgs
            total_all_classes += tot_classes

            lines.append(f"\nDataset ID:            {ds_id}")
            lines.append(f"Root Path:             {root_path}")
            lines.append(f"Total Images:          {tot_imgs:,}")
            lines.append(f"Apparent Class Folders:{tot_classes}")
            lines.append(f"Image Extensions:      {dict(exts)}")
            lines.append(f"Empty Class Dirs:      {empty_dirs}")
            lines.append(f"Non-Image Files:       {non_imgs}")
            lines.append(f"Archive Files:         {archives}")
            lines.append(f"Scan Timestamp:        {inv.get('scan_timestamp')}")

        lines.append("--------------------------------------------------------------------------")
        lines.append(f"COMBINED TOTAL IMAGES:   {total_all_images:,}")
        lines.append(f"COMBINED TOTAL CLASSES:  {total_all_classes}")
        lines.append("==========================================================================")

        return "\n".join(lines)
