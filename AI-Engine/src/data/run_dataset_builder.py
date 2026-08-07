import os
import sys
import argparse
from pathlib import Path

sys.path.insert(0, os.path.abspath(r"C:\Dravya-AI-Engine"))

from src.data.dataset_builder import CanonicalDatasetBuilder

def main():
    parser = argparse.ArgumentParser(description="Dravya AI Canonical Dataset Builder CLI (Manifest-First)")
    parser.add_argument("--version", type=str, default="v1", help="Taxonomy version (default: v1)")
    parser.add_argument("--dry-run", action="store_true", help="Execute dry-run without copying physical images")
    parser.add_argument("--validate", action="store_true", help="Run manifest integrity validation")
    parser.add_argument("--summary", action="store_true", help="Print human-readable summary")

    args = parser.parse_args()

    print(f"Executing Canonical Dataset Builder (Version: {args.version}, Dry-Run: True)...")
    builder = CanonicalDatasetBuilder(version=args.version)
    builder.load_inputs()
    records, stats = builder.build_manifest()

    artifacts = builder.export_artifacts()
    val_report = builder.validate_manifest()

    summary_str = builder.format_terminal_summary()
    print("\n" + summary_str)

    print("\nGenerated Dataset Artifacts:")
    print(f" - Canonical Dataset Manifest JSON:   {artifacts['manifest_json']}")
    print(f" - Canonical Dataset Statistics JSON: {artifacts['statistics_json']}")
    print(f" - Validation Report JSON:            {artifacts['validation_json']}")
    print(f" - Readiness Report JSON:             {artifacts['readiness_json']}")

    if args.validate and not val_report["is_valid"]:
        print("\n[ERROR] Dataset Manifest Validation Failed!")
        for err in val_report["errors"]:
            print(f" - {err}")
        sys.exit(1)

if __name__ == "__main__":
    main()
