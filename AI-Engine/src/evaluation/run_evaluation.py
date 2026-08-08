import argparse
import sys
from pathlib import Path

from src.evaluation.evaluator import ModelEvaluator


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Dravya AI Engine - Model Evaluation Command"
    )
    parser.add_argument(
        "--version",
        type=str,
        default="v1-smoke",
        help="Model version tag to evaluate (default: v1-smoke)",
    )
    parser.add_argument(
        "--checkpoint-name",
        type=str,
        default="best_model.pth",
        help="Checkpoint filename to load (default: best_model.pth)",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        help="Execution device (default: cpu)",
    )
    parser.add_argument(
        "--manifest-path",
        type=str,
        default=None,
        help="Path to canonical dataset manifest JSON",
    )
    parser.add_argument(
        "--models-dir",
        type=str,
        default=None,
        help="Directory containing versioned model checkpoints",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory for evaluation JSON artifacts",
    )

    args = parser.parse_args()

    print("==========================================================================")
    print("           DRAVYA AI ENGINE - REPRODUCIBLE MODEL EVALUATION               ")
    print("==========================================================================")

    evaluator = ModelEvaluator(
        version=args.version,
        checkpoint_name=args.checkpoint_name,
        manifest_path=args.manifest_path,
        models_dir=args.models_dir,
        output_dir=args.output_dir,
        device=args.device,
    )

    print(f"Loaded Model Version:  {evaluator.version}")
    print(f"Backbone Architecture: {evaluator.architecture}")
    print(f"Canonical Manifest:    {evaluator.manifest_path}")
    print(f"Num Approved Classes:  {evaluator.num_classes}")
    print("Running evaluation pass over approved records...")

    res = evaluator.evaluate()
    metrics = res.get("metrics", {})

    print("\n--------------------------------------------------------------------------")
    print("                    MODEL EVALUATION SUMMARY RESULTS                      ")
    print("--------------------------------------------------------------------------")
    print(f"Evaluated Samples:     {res['total_evaluated_samples']}")
    print(f"Accuracy:              {metrics.get('accuracy', 0.0):.4f}")
    print(f"Macro Precision:       {metrics.get('precision', 0.0):.4f}")
    print(f"Macro Recall:          {metrics.get('recall', 0.0):.4f}")
    print(f"Macro F1-Score:        {metrics.get('f1_score', 0.0):.4f}")
    print(f"Evaluation Time (s):   {res['evaluation_time_seconds']}")
    print(f"Artifact Saved At:     {evaluator.output_dir / f'{evaluator.version}_evaluation.json'}")
    print("==========================================================================")


if __name__ == "__main__":
    main()
