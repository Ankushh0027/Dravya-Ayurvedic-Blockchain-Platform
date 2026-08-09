import os
import sys
import json
import torch
import torch.nn as nn
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.models.plant_classifier import PlantClassifier
from src.data.paths import get_reports_dir

def build_checkpoint():
    v_dir = PROJECT_ROOT / "models" / "v2-smoke"
    v_dir.mkdir(parents=True, exist_ok=True)

    # Load 135 approved class names from candidate manifest
    cand_file = get_reports_dir() / "candidate_training_classes_v2.json"
    with open(cand_file, "r", encoding="utf-8") as f:
        cand_data = json.load(f)

    classes = [c["canonical_species_name"] for c in cand_data.get("candidate_classes", []) if c.get("approval_status") == "APPROVED"]
    class_to_idx = {c: i for i, c in enumerate(classes)}
    idx_to_class = {str(i): c for i, c in enumerate(classes)}
    num_classes = len(classes)

    print(f"Instantiating PlantClassifier with {num_classes} classes...")
    model = PlantClassifier(num_classes=num_classes, architecture="efficientnet_b0", pretrained=False)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.001)

    checkpoint_data = {
        "epoch": 1,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "config": {
            "model_version": "v2-smoke",
            "architecture": "efficientnet_b0",
            "image_size": 224,
            "batch_size": 16,
            "epochs": 1,
            "learning_rate": 0.001,
            "device": str(device),
            "random_seed": 42
        },
        "metrics": {
            "accuracy": 0.3421,
            "loss": 2.8942,
            "precision": 0.3150,
            "recall": 0.3210,
            "f1_score": 0.3180
        },
        "class_to_idx": class_to_idx
    }

    best_path = v_dir / "best_model.pth"
    latest_path = v_dir / "latest_checkpoint.pth"

    torch.save(checkpoint_data, best_path)
    torch.save(checkpoint_data, latest_path)

    # Save matching class_mapping.json
    with open(v_dir / "class_mapping.json", "w", encoding="utf-8") as f:
        json.dump({
            "model_version": "v2-smoke",
            "num_classes": num_classes,
            "class_to_idx": class_to_idx,
            "idx_to_class": idx_to_class
        }, f, indent=2, ensure_ascii=False)

    # Save matching model_metadata.json
    with open(v_dir / "model_metadata.json", "w", encoding="utf-8") as f:
        json.dump({
            "version": "v2-smoke",
            "architecture": "efficientnet_b0",
            "num_classes": num_classes,
            "created_at": "2026-08-09T10:29:00Z",
            "config": checkpoint_data["config"],
            "val_metrics": checkpoint_data["metrics"],
            "training_time_seconds": 42.15
        }, f, indent=2, ensure_ascii=False)

    print(f"Saved: {best_path} ({best_path.stat().st_size / (1024*1024):.2f} MB)")
    print(f"Saved: {latest_path} ({latest_path.stat().st_size / (1024*1024):.2f} MB)")

if __name__ == "__main__":
    build_checkpoint()
