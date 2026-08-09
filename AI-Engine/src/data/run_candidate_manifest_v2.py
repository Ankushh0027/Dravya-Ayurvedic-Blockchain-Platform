import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.candidate_manifest_v2 import CandidateManifestGeneratorV2
from src.data.paths import get_reports_dir

def main():
    print("Starting Dravya AI Candidate Training Manifest Generator (v2)...\n")

    reports_dir = get_reports_dir()
    generator = CandidateManifestGeneratorV2(reports_dir=reports_dir)

    print("Step 1: Loading combined species inventory v2...")
    inventory_data = generator.load_combined_inventory()

    print("Step 2: Analyzing 11 taxonomy conflicts...")
    conflicts = generator.analyze_taxonomy_conflicts(inventory_data)

    print("Step 3: Analyzing 40 low-data species...")
    low_data = generator.analyze_low_data_species(inventory_data.get("candidate_species_inventory", []))

    print("Step 4 & 5: Building candidate class manifest and human review manifest...")
    candidate_manifest, review_manifest, stats_summary = generator.build_candidate_and_review_manifests(inventory_data, conflicts)

    print("Step 6: Generating output manifest artifacts and markdown feasibility report...")
    artifact_paths = generator.export_manifests_and_report(
        candidate_manifest,
        review_manifest,
        conflicts,
        low_data,
        stats_summary
    )

    print("Step 7: Final Readiness Check")
    generator.print_terminal_readiness_check(stats_summary)

    print("Generated Manifest Artifacts:")
    print(f"  - Candidate Classes JSON: {artifact_paths['candidate_json']}")
    print(f"  - Candidate Classes CSV:  {artifact_paths['candidate_csv']}")
    print(f"  - Human Review JSON:     {artifact_paths['review_json']}")
    print(f"  - Markdown Report:        {artifact_paths['report_md']}")
    print("\nSafety Affirmation: Raw datasets processed in READ-ONLY mode.")

if __name__ == "__main__":
    main()
