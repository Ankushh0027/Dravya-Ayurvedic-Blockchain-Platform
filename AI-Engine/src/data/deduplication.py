import os
import hashlib
import json
import csv
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from src.data.paths import SUPPORTED_IMAGE_EXTENSIONS

def compute_file_sha256(file_path: str, chunk_size: int = 131072) -> str:
    """
    Computes SHA-256 hash of a file by streaming binary content in chunks.
    Does not load entire file into memory.
    """
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            sha256.update(chunk)
    return sha256.hexdigest()

class ExactDuplicateDetector:
    """
    Scans dataset directories to identify exact duplicate images using chunked SHA-256 hashing.
    Distinguishes between within-dataset and cross-dataset duplicate groups.
    """

    def __init__(self, dataset_dict: Dict[str, str], chunk_size: int = 131072):
        """
        :param dataset_dict: Dictionary mapping dataset_id to absolute root path.
        :param chunk_size: Buffer chunk size for file reading in bytes (default 128KB).
        """
        self.dataset_dict = {ds_id: os.path.abspath(path) for ds_id, path in dataset_dict.items()}
        self.chunk_size = chunk_size

    def scan(self) -> Dict[str, Any]:

        """
        Scans all datasets, computes SHA-256 hashes, and identifies exact duplicates.
        """
        total_images_scanned = 0
        hash_to_files: Dict[str, List[Dict[str, str]]] = {}

        for dataset_id, root_path in self.dataset_dict.items():
            if not os.path.exists(root_path):
                raise FileNotFoundError(f"Dataset root path does not exist: {root_path}")

            for dirpath, _, filenames in os.walk(root_path):
                rel_dir = os.path.relpath(dirpath, root_path)
                class_name = rel_dir if rel_dir != "." else "root"

                for f in filenames:
                    ext = os.path.splitext(f)[1].lower()
                    if ext in SUPPORTED_IMAGE_EXTENSIONS:
                        abs_file_path = os.path.join(dirpath, f)
                        file_hash = compute_file_sha256(abs_file_path, chunk_size=self.chunk_size)
                        total_images_scanned += 1

                        file_info = {
                            "dataset_id": dataset_id,
                            "class_name": class_name,
                            "file_path": abs_file_path,
                            "file_name": f
                        }

                        if file_hash not in hash_to_files:
                            hash_to_files[file_hash] = []
                        hash_to_files[file_hash].append(file_info)

        # Identify duplicate groups (hashes with 2 or more files)
        duplicate_groups = []
        within_ds_groups_count = 0
        cross_ds_groups_count = 0
        within_ds_files_count = 0
        cross_ds_files_count = 0
        total_duplicate_files = 0

        group_idx = 1
        for sha256_hash, files in hash_to_files.items():
            if len(files) > 1:
                group_id = f"dup_group_{group_idx:05d}"
                datasets_involved = sorted(list(set(f["dataset_id"] for f in files)))
                is_cross_dataset = len(datasets_involved) > 1

                for f in files:
                    f["duplicate_group_id"] = group_id

                if is_cross_dataset:
                    cross_ds_groups_count += 1
                    cross_ds_files_count += len(files)
                else:
                    within_ds_groups_count += 1
                    within_ds_files_count += len(files)

                total_duplicate_files += len(files)

                group_data = {
                    "duplicate_group_id": group_id,
                    "sha256_hash": sha256_hash,
                    "is_cross_dataset": is_cross_dataset,
                    "datasets_involved": datasets_involved,
                    "file_count": len(files),
                    "files": files
                }
                duplicate_groups.append(group_data)
                group_idx += 1

        scan_timestamp = datetime.now(timezone.utc).isoformat()

        results = {
            "scan_timestamp": scan_timestamp,
            "datasets_scanned": list(self.dataset_dict.keys()),
            "total_images_scanned": total_images_scanned,
            "unique_hashes": len(hash_to_files),
            "duplicate_groups_count": len(duplicate_groups),
            "total_duplicate_files": total_duplicate_files,
            "within_dataset_duplicate_groups_count": within_ds_groups_count,
            "within_dataset_duplicate_files_count": within_ds_files_count,
            "cross_dataset_duplicate_groups_count": cross_ds_groups_count,
            "cross_dataset_duplicate_files_count": cross_ds_files_count,
            "duplicate_groups": duplicate_groups
        }
        return results

    def export_reports(self, scan_results: Dict[str, Any], output_dir: str = r"C:\Dravya-AI-Engine\reports\dataset_analysis") -> Dict[str, str]:
        """
        Exports duplicate analysis JSON and CSV reports.
        """
        os.makedirs(output_dir, exist_ok=True)
        json_path = os.path.join(output_dir, "duplicate_analysis.json")
        csv_path = os.path.join(output_dir, "exact_duplicates.csv")

        # Export JSON
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(scan_results, f, indent=2, ensure_ascii=False)

        # Export CSV
        fieldnames = ["hash", "file_path", "dataset_id", "class_name", "duplicate_group_id"]
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for group in scan_results.get("duplicate_groups", []):
                group_id = group["duplicate_group_id"]
                group_hash = group["sha256_hash"]
                for f_info in group["files"]:
                    writer.writerow({
                        "hash": group_hash,
                        "file_path": f_info["file_path"],
                        "dataset_id": f_info["dataset_id"],
                        "class_name": f_info["class_name"],
                        "duplicate_group_id": group_id
                    })

        return {
            "json_path": json_path,
            "csv_path": csv_path
        }

    @staticmethod
    def format_terminal_summary(scan_results: Dict[str, Any]) -> str:
        """
        Formats concise terminal summary string.
        """
        lines = [
            "==========================================================================",
            "             DRAVYA AI EXACT DUPLICATE DETECTION SUMMARY                 ",
            "==========================================================================",
            f"Datasets Scanned:                    {', '.join(scan_results.get('datasets_scanned', []))}",
            f"Total Images Scanned:                {scan_results.get('total_images_scanned', 0):,}",
            f"Unique SHA-256 Hashes:               {scan_results.get('unique_hashes', 0):,}",
            f"Total Duplicate Groups:              {scan_results.get('duplicate_groups_count', 0):,}",
            f"Total Exact Duplicate Files:         {scan_results.get('total_duplicate_files', 0):,}",
            f"Within-Dataset Duplicate Groups:     {scan_results.get('within_dataset_duplicate_groups_count', 0):,} ({scan_results.get('within_dataset_duplicate_files_count', 0):,} files)",
            f"Cross-Dataset Duplicate Groups:      {scan_results.get('cross_dataset_duplicate_groups_count', 0):,} ({scan_results.get('cross_dataset_duplicate_files_count', 0):,} files)",
            "=========================================================================="
        ]
        return "\n".join(lines)
