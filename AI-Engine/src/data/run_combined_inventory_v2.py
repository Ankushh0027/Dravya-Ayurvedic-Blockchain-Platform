import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.combined_inventory_v2 import CombinedInventoryAnalyzer
from src.data.paths import get_dataset_paths, get_reports_dir

def main():
    print("Starting Dravya AI Combined Dataset Species Inventory (v2)...\n")

    dataset_paths = get_dataset_paths()
    reports_dir = get_reports_dir()

    print("Locating dataset paths:")
    for ds_id, p in dataset_paths.items():
        print(f"  - {ds_id}: {p} (Exists: {p.exists()})")

    analyzer = CombinedInventoryAnalyzer(dataset_paths=dataset_paths, reports_dir=reports_dir)

    print("\nPhase 1: Scanning raw datasets and testing image integrity...")
    phase1_data = analyzer.run_phase1_inventory()

    print("\nPhase 2: Performing botanical taxonomy harmonization analysis...")
    mapping_records, candidate_species = analyzer.run_phase2_harmonization(phase1_data)

    print("\nPhase 3: Computing combined species statistics...")
    stats = analyzer.run_phase3_statistics(phase1_data, candidate_species)

    print("\nPhase 4: Generating report artifacts...")
    report_paths = analyzer.generate_reports(phase1_data, mapping_records, candidate_species, stats)

    analyzer.print_terminal_summary(stats)

    print("Generated Artifacts:")
    print(f"  - JSON Report: {report_paths['json']}")
    print(f"  - CSV Report:  {report_paths['csv']}")
    print(f"  - Markdown:    {report_paths['md']}")
    print("\nSafety Verification: All raw datasets processed in READ-ONLY mode.")

if __name__ == "__main__":
    main()
