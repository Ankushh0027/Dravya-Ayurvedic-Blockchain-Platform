import os
import sys

sys.path.insert(0, os.path.abspath(r"C:\Dravya-AI-Engine"))

from src.data import DATASET_PATHS, ExactDuplicateDetector

def main():
    print("Starting Dravya AI Exact Duplicate Detection Scan across all datasets...\n")
    print(f"Datasets: {list(DATASET_PATHS.keys())}")

    detector = ExactDuplicateDetector(dataset_dict=DATASET_PATHS)
    scan_results = detector.scan()

    reports = detector.export_reports(scan_results)
    summary_str = detector.format_terminal_summary(scan_results)

    print("\n" + summary_str)
    print(f"\nGenerated Artifacts:")
    print(f" - JSON Report: {reports['json_path']}")
    print(f" - CSV Report:  {reports['csv_path']}")

if __name__ == "__main__":
    main()
