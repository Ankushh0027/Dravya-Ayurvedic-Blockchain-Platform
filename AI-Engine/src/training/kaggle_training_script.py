"""
Dravya AI Engine — Kaggle GPU Production Training Script
========================================================
Full PyTorch training loop designed for Kaggle GPU environments (P100 / T4 / TPU).
Loads materialized canonical dataset v1 (22,547 images across 94 approved classes).
Saves best model checkpoint, class mapping, and metadata to /kaggle/working/.
"""

import os
import sys
import json
import time
import math
import random
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

import numpy as np
from PIL import Image

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as T
import torchvision.models as models


def find_kaggle_dataset_root() -> Path:
    possible_roots = [
        Path("/kaggle/input/dravya-canonical-v1"),
        Path("/kaggle/input/dravya-canonical-dataset-v1"),
        Path("/kaggle/input/canonical-v1"),
        Path("/kaggle/input"),
        Path("./data/canonical/v1")
    ]
    for p in possible_roots:
        if (p / "manifests" / "manifest.json").exists():
            return p
        sub_manifests = list(p.glob("**/manifests/manifest.json"))
        if sub_manifests:
            return sub_manifests[0].parent.parent
    raise FileNotFoundError("Could not locate Kaggle input dataset with manifests/manifest.json!")


class KaggleDravyaDataset(Dataset):
    def __init__(self, records: List[Dict[str, Any]], root_dir: Path, class_to_idx: Dict[str, int], transform=None):
        self.records = records
        self.root_dir = root_dir
        self.class_to_idx = class_to_idx
        self.transform = transform

    def __len__(self):
        return len(self.records)

    def __getitem__(self, idx):
        rec = self.records[idx]
        cid = rec["canonical_class_id"]
        label = self.class_to_idx[cid]
        rel_path = rec["relative_canonical_path"]
        img_path = self.root_dir / rel_path

        try:
            img = Image.open(img_path).convert("RGB")
        except Exception:
            img = Image.new("RGB", (224, 224), color=(128, 128, 128))

        if self.transform:
            img = self.transform(img)

        return img, label


class EfficientNetPlantClassifier(nn.Module):
    def __init__(self, num_classes: int, pretrained: bool = True):
        super().__init__()
        weights = models.EfficientNet_B0_Weights.DEFAULT if pretrained else None
        self.backbone = models.efficientnet_b0(weights=weights)
        in_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(p=0.2, inplace=True),
            nn.Linear(in_features, num_classes)
        )

    def forward(self, x):
        return self.backbone(x)


def run_kaggle_gpu_training(epochs: int = 10, batch_size: int = 32, lr: float = 1e-3):
    print("==========================================================================")
    print("         DRAVYA AI ENGINE — KAGGLE GPU PRODUCTION MODEL TRAINING          ")
    print("==========================================================================")
    print("PyTorch Version:", torch.__version__)
    print("CUDA Available: ", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("GPU Device:     ", torch.cuda.get_device_name(0))

    dataset_root = find_kaggle_dataset_root()
    manifest_path = dataset_root / "manifests" / "manifest.json"
    print(f"Dataset Root:    {dataset_root}")
    print(f"Manifest Path:   {manifest_path}")

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    records = manifest_data.get("records", [])
    approved_records = [
        r for r in records
        if r.get("approval_status") == "APPROVED" or r.get("mapping_status") == "APPROVED" or "canonical_class_id" in r
    ]

    classes = sorted(list(set(r["canonical_class_id"] for r in approved_records)))
    class_to_idx = {c: i for i, c in enumerate(classes)}
    idx_to_class = {i: c for i, c in enumerate(classes)}
    num_classes = len(classes)

    print(f"Loaded {len(approved_records):,} records across {num_classes} canonical classes.")

    train_records = [r for r in approved_records if r.get("split") == "train"]
    val_records = [r for r in approved_records if r.get("split") == "val"]
    test_records = [r for r in approved_records if r.get("split") == "test"]

    mean = [0.485, 0.456, 0.406]
    std = [0.229, 0.224, 0.225]

    train_tf = T.Compose([
        T.Resize((224, 224)),
        T.RandomHorizontalFlip(p=0.5),
        T.RandomRotation(degrees=15),
        T.ColorJitter(brightness=0.1, contrast=0.1),
        T.ToTensor(),
        T.Normalize(mean=mean, std=std)
    ])

    eval_tf = T.Compose([
        T.Resize((224, 224)),
        T.CenterCrop(224),
        T.ToTensor(),
        T.Normalize(mean=mean, std=std)
    ])

    train_ds = KaggleDravyaDataset(train_records, dataset_root, class_to_idx, train_tf)
    val_ds = KaggleDravyaDataset(val_records, dataset_root, class_to_idx, eval_tf)
    test_ds = KaggleDravyaDataset(test_records, dataset_root, class_to_idx, eval_tf)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=4, pin_memory=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=4, pin_memory=True)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=4, pin_memory=True)

    print(f"Data splits -> Train: {len(train_ds):,}, Val: {len(val_ds):,}, Test: {len(test_ds):,}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = EfficientNetPlantClassifier(num_classes=num_classes, pretrained=True).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    scaler = torch.cuda.amp.GradScaler(enabled=torch.cuda.is_available())

    best_val_acc = 0.0
    output_dir = Path("/kaggle/working") if Path("/kaggle/working").exists() else Path("./models/v1-kaggle")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nStarting GPU Training ({epochs} Epochs)...")
    for epoch in range(1, epochs + 1):
        start_t = time.time()
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()

            with torch.cuda.amp.autocast(enabled=torch.cuda.is_available()):
                outputs = model(images)
                loss = criterion(outputs, labels)

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

            running_loss += loss.item() * images.size(0)
            _, preds = torch.max(outputs, 1)
            correct += torch.sum(preds == labels.data).item()
            total += labels.size(0)

        scheduler.step()
        train_loss = running_loss / total
        train_acc = correct / total

        # Validation Pass
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                with torch.cuda.amp.autocast(enabled=torch.cuda.is_available()):
                    outputs = model(images)
                    loss = criterion(outputs, labels)

                val_loss += loss.item() * images.size(0)
                _, preds = torch.max(outputs, 1)
                val_correct += torch.sum(preds == labels.data).item()
                val_total += labels.size(0)

        epoch_val_loss = val_loss / val_total
        epoch_val_acc = val_correct / val_total
        elapsed = time.time() - start_t

        print(f"Epoch [{epoch:02d}/{epochs:02d}] ({elapsed:.1f}s) | Train Loss: {train_loss:.4f}, Acc: {train_acc:.4f} | Val Loss: {epoch_val_loss:.4f}, Acc: {epoch_val_acc:.4f}")

        if epoch_val_acc > best_val_acc:
            best_val_acc = epoch_val_acc
            torch.save(model.state_dict(), output_dir / "best_model.pth")
            print(f"  -> Saved peak checkpoint best_model.pth (Val Acc: {best_val_acc:.4f})")

    # Export Metadata & Class Mapping
    with open(output_dir / "class_mapping.json", "w", encoding="utf-8") as f:
        json.dump({"class_to_idx": class_to_idx, "idx_to_class": idx_to_class}, f, indent=2)

    with open(output_dir / "model_metadata.json", "w", encoding="utf-8") as f:
        json.dump({
            "version": "v1-kaggle-gpu",
            "architecture": "efficientnet_b0",
            "num_classes": num_classes,
            "best_val_accuracy": best_val_acc,
            "epochs_trained": epochs,
            "device": str(device)
        }, f, indent=2)

    # Test Evaluation
    model.eval()
    test_loss = 0.0
    test_correct = 0
    test_total = 0

    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            with torch.cuda.amp.autocast(enabled=torch.cuda.is_available()):
                outputs = model(images)
                loss = criterion(outputs, labels)

            test_loss += loss.item() * images.size(0)
            _, preds = torch.max(outputs, 1)
            test_correct += torch.sum(preds == labels.data).item()
            test_total += labels.size(0)

    test_acc = test_correct / test_total
    print(f"\nFinal Test Split Evaluation: Accuracy = {test_acc:.4f} ({test_correct}/{test_total})")

    eval_report = {
        "model_version": "v1-kaggle-gpu",
        "total_test_samples": test_total,
        "correct_test_predictions": test_correct,
        "test_accuracy": test_acc,
        "best_val_accuracy": best_val_acc,
        "status": "PASS" if test_acc > 0.70 else "WARNING"
    }

    with open(output_dir / "evaluation_report.json", "w", encoding="utf-8") as f:
        json.dump(eval_report, f, indent=2)

    print("==========================================================================")
    print("           KAGGLE GPU TRAINING & EVALUATION COMPLETE                      ")
    print("==========================================================================")
    print(f"Artifacts exported to: {output_dir}")


if __name__ == "__main__":
    run_kaggle_gpu_training(epochs=10, batch_size=32)
