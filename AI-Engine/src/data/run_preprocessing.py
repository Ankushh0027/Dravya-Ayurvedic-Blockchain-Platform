import os
import sys
import argparse
from pathlib import Path

sys.path.insert(0, os.path.abspath(r"C:\Dravya-AI-Engine"))

from src.data.preprocessing import PreprocessingConfig, CanonicalPreprocessor

def main():
    parser = argparse.ArgumentParser(description="Dravya AI Canonical Dataset Preprocessing & Split CLI")
    parser.add_argument("--version", type=str, default="v1", help="Taxonomy / preprocessing version (default: v1)")
    parser.add_argument("--validate", action="store_true", help="Run preprocessing integrity & leakage validation")
    parser.add_argument("--summary", action="store_true", help="Print human-readable preprocessing summary")
    
    parser.add_argument("--image-size", type=int, nargs=2, default=[224, 224], help="Target image dimensions (width height)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for deterministic splitting")
    parser.add_argument("--train-ratio", type=float, default=0.70, help="Train split ratio (default: 0.70)")
    parser.add_argument("--val-ratio", type=float, default=0.15, help="Validation split ratio (default: 0.15)")
    parser.add_argument("--test-ratio", type=float, default=0.15, help="Test split ratio (default: 0.15)")
    parser.add_argument("--output-root", type=str, default=r"C:\Dravya-AI-Engine\data\processed\v1", help="Output directory for processed image files")
    parser.add_argument("--force", action="store_true", help="Force overwrite existing processed data")

    args = parser.parse_args()

    config = PreprocessingConfig(
        version=args.version,
        output_root=args.output_root,
        image_size=(args.image_size[0], args.image_size[1]),
        random_seed=args.seed,
        split_ratios={"train": args.train_ratio, "val": args.val_ratio, "test": args.test_ratio},
        overwrite_policy="FORCE" if args.force else "NEVER"
    )

    print(f"Executing Canonical Preprocessor & Splitter (Version: {args.version})...")
    preprocessor = CanonicalPreprocessor(config=config)
    records, stats = preprocessor.process_and_split()

    artifacts = preprocessor.export_artifacts()
    val_report = preprocessor.validate_processed_dataset()

    if args.summary or not args.validate:
        summary_str = preprocessor.format_terminal_summary()
        print("\n" + summary_str)
        print("\nGenerated Preprocessing Artifacts:")
        print(f" - Processed Dataset Manifest JSON:   {artifacts['manifest_json']}")
        print(f" - Processed Dataset Statistics JSON: {artifacts['statistics_json']}")
        print(f" - Validation Report JSON:            {artifacts['validation_json']}")

    if val_report["status"] == "INVALID":
        print("\n[ERROR] Preprocessing Validation Failed!")
        for err in val_report["errors"]:
            print(f" - {err}")
        sys.exit(1)
    elif stats.get("status") == "BLOCKED":
        print(f"\n[INFO] Preprocessing is BLOCKED ({stats.get('reason')}). No approved taxonomy mappings exist.")

if __name__ == "__main__":
    main()
