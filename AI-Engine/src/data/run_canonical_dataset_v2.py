import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.canonical_dataset_v2 import CanonicalDatasetBuilderV2
from src.data.paths import get_reports_dir

def main():
    print("Starting Dravya AI Canonical Dataset V2 Build & Verification...\n")

    reports_dir = get_reports_dir()
    builder = CanonicalDatasetBuilderV2(version="v2", reports_dir=reports_dir)

    print("Step 1: Reading approved taxonomy review manifest...")
    approved_classes = builder.load_approved_classes()
    print(f"-> Loaded {len(approved_classes)} APPROVED classes (NEEDS_REVIEW and REJECTED excluded).")

    print("\nStep 2–6: Scanning source files, validating images, and building leakage-proof splits...")
    records, per_class_list, stats_summary = builder.build_canonical_dataset_v2(approved_classes)

    print("\nStep 7–9: Exporting manifests, statistics, validation reports, and markdown...")
    artifact_paths = builder.export_artifacts_and_reports(records, per_class_list, stats_summary)

    print("Step 10: Final Readiness Gate Summary")
    builder.print_terminal_readiness_gate(stats_summary)

    print("Generated Canonical V2 Reports:")
    print(f"  - Dataset Manifest: {artifact_paths['manifest_json']}")
    print(f"  - Statistics JSON:  {artifact_paths['stats_json']}")
    print(f"  - Statistics CSV:   {artifact_paths['stats_csv']}")
    print(f"  - Validation JSON:  {artifact_paths['val_json']}")
    print(f"  - Markdown Report:  {artifact_paths['report_md']}")
    print(f"  - Target Manifest:  {artifact_paths['target_manifest']}")
    print("\nSafety Affirmation: All raw datasets remain 100% READ-ONLY and untouched.")

if __name__ == "__main__":
    main()
