import os
import sys
import argparse
from pathlib import Path

sys.path.insert(0, os.path.abspath(r"C:\Dravya-AI-Engine"))

from src.data.quality_gate import DatasetQualityGate, QualityGateStatus

def main():
    parser = argparse.ArgumentParser(description="Dravya AI Canonical Dataset Quality Gate CLI")
    parser.add_argument("--version", type=str, default="v1", help="Taxonomy / dataset version (default: v1)")
    parser.add_argument("--validate", action="store_true", help="Run full Quality Gate checks")
    parser.add_argument("--summary", action="store_true", help="Print human-readable Quality Gate summary")
    parser.add_argument("--min-samples-per-class", type=int, default=5, help="Minimum required image samples per canonical plant class")
    parser.add_argument("--fail-on-warning", action="store_true", help="Treat quality warnings as FAIL status")

    args = parser.parse_args()

    print(f"Executing Canonical Dataset Quality Gate (Version: {args.version})...")
    gate = DatasetQualityGate(
        version=args.version,
        min_samples_per_class=args.min_samples_per_class,
        fail_on_warning=args.fail_on_warning
    )

    result = gate.evaluate_quality_gate()
    artifacts = gate.export_artifacts(result)

    if args.summary or not args.validate:
        summary_str = gate.format_terminal_summary(result)
        print("\n" + summary_str)
        print("\nGenerated Quality Gate Artifacts:")
        print(f" - Full Quality Report JSON:   {artifacts['report_json']}")
        print(f" - Quality Summary JSON:       {artifacts['summary_json']}")

    if result.status == QualityGateStatus.FAIL:
        print("\n[ERROR] Quality Gate Validation Failed!")
        for err in result.errors:
            print(f" - {err}")
        sys.exit(1)
    elif result.status == QualityGateStatus.BLOCKED:
        print(f"\n[INFO] Quality Gate is BLOCKED ({result.reason}). No approved taxonomy mappings exist.")

if __name__ == "__main__":
    main()
