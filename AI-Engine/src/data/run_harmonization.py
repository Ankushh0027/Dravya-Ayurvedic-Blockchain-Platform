import os
import sys

sys.path.insert(0, os.path.abspath(r"C:\Dravya-AI-Engine"))

from src.data import DATASET_PATHS, InventoryScanner, ClassHarmonizationAnalyzer

def main():
    print("Starting Dravya AI Taxonomy / Class Harmonization Analysis...\n")

    inventories = []
    for ds_id, root_path in DATASET_PATHS.items():
        scanner = InventoryScanner(dataset_id=ds_id, root_path=root_path)
        inv = scanner.scan()
        inventories.append(inv)

    analyzer = ClassHarmonizationAnalyzer(inventories)
    results = analyzer.analyze()

    reports = analyzer.export_reports(results)
    summary_str = analyzer.format_terminal_summary(results)

    print(summary_str)
    print(f"\nGenerated Artifacts:")
    print(f" - Candidate CSV:  {reports['csv_path']}")
    print(f" - Analysis JSON:  {reports['json_path']}")

if __name__ == "__main__":
    main()
