import os
import sys
import argparse
from pathlib import Path

sys.path.insert(0, os.path.abspath(r"C:\Dravya-AI-Engine"))

from src.data.taxonomy_manager import TaxonomyManager
from src.data.taxonomy_validator import TaxonomyValidator

def main():
    parser = argparse.ArgumentParser(description="Dravya AI Canonical Taxonomy Mapping & Review CLI")
    parser.add_argument("--version", type=str, default="v1", help="Taxonomy version tag (default: v1)")
    parser.add_argument("--input", type=str, default=None, help="Custom input harmonization JSON path")
    parser.add_argument("--validate", action="store_true", help="Run taxonomy integrity validation")
    parser.add_argument("--summary", action="store_true", help="Print human-readable summary")

    args = parser.parse_args()

    print(f"Executing Taxonomy Mapping Manager (Version: {args.version})...")
    mgr = TaxonomyManager(version=args.version)
    plants, mappings = mgr.build_from_harmonization_json(json_path=args.input)

    artifacts = mgr.export_artifacts()
    val_report = TaxonomyValidator.validate_full_system(plants, mappings)

    summary_str = mgr.format_terminal_summary(val_report)
    print("\n" + summary_str)

    print("\nGenerated Taxonomy Artifacts:")
    print(f" - Canonical Taxonomy JSON: {artifacts['taxonomy_json']}")
    print(f" - Mappings Review JSON:    {artifacts['mappings_json']}")
    print(f" - Validation Report JSON:  {artifacts['validation_json']}")

    if args.validate and not val_report["is_valid"]:
        print("\n[ERROR] Taxonomy Validation Failed!")
        for err in val_report["errors"]:
            print(f" - {err}")
        sys.exit(1)

if __name__ == "__main__":
    main()
