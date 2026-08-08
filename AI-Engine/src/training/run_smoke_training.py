import argparse
import sys
from pathlib import Path

from src.models.config import load_model_config
from src.models.plant_classifier import PlantClassifier
from src.training.dataset import create_dataloaders
from src.training.trainer import ModelTrainer


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Dravya AI Engine - CPU Smoke Training Command"
    )
    parser.add_argument(
        "--version",
        type=str,
        default="v1-smoke",
        help="Model version tag (default: v1-smoke)",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=1,
        help="Number of training epochs (default: 1)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=4,
        help="Batch size (default: 4)",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        help="Execution device (default: cpu)",
    )
    parser.add_argument(
        "--architecture",
        type=str,
        default="efficientnet_b0",
        help="Model backbone architecture (default: efficientnet_b0)",
    )
    parser.add_argument(
        "--manifest-path",
        type=str,
        default=None,
        help="Path to canonical dataset manifest JSON",
    )
    args = parser.parse_args()

    print("==========================================================================")
    print("           DRAVYA AI ENGINE - CPU SMOKE TRAINING RUNNER                 ")
    print("==========================================================================")

    # 1. Load config
    config = load_model_config(
        model_version=args.version,
        epochs=args.epochs,
        batch_size=args.batch_size,
        device=args.device,
        architecture=args.architecture,
        dataset_manifest_path=args.manifest_path,
    )

    # 2. Create dataloaders from approved canonical dataset
    print(f"Loading canonical dataset manifest: {config.dataset_manifest_path}")
    train_loader, val_loader, class_to_idx, idx_to_class = create_dataloaders(
        config=config
    )
    num_classes = len(class_to_idx)
    print(f"Dataset successfully loaded. Approved classes: {num_classes}")

    # 3. Instantiate model
    print(f"Instantiating {config.architecture} plant classifier for {num_classes} classes...")
    model = PlantClassifier(
        num_classes=num_classes,
        architecture=config.architecture,
        pretrained=False,
    )

    # 4. Initialize Trainer and run training
    trainer = ModelTrainer(
        model=model,
        config=config,
        class_to_idx=class_to_idx,
        idx_to_class=idx_to_class,
        train_loader=train_loader,
        val_loader=val_loader,
    )

    summary = trainer.train()

    print("\n--------------------------------------------------------------------------")
    print("                     SMOKE TRAINING COMPLETED SUCCESSFULLY                ")
    print("--------------------------------------------------------------------------")
    print(f"Model Version:         {summary['version']}")
    print(f"Architecture:          {summary['architecture']}")
    print(f"Num Classes:           {summary['num_classes']}")
    print(f"Training Time (s):     {summary['training_time_seconds']}")
    print(f"Best Val Accuracy:     {summary['val_metrics'].get('accuracy', 0.0)}")
    print(f"Best Val F1-Score:     {summary['val_metrics'].get('f1_score', 0.0)}")
    print(f"Checkpoint Directory:  {trainer.version_dir}")
    print("==========================================================================")


if __name__ == "__main__":
    main()
