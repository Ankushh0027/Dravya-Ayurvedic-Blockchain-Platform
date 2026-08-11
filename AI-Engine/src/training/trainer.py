import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from src.data.taxonomy_review import atomic_json_write
from src.models.config import ModelConfig
from src.models.plant_classifier import PlantClassifier
from src.models.version_manager import ModelVersionManager
from src.training.metrics import compute_metrics


class ModelTrainer:
    """
    Model Trainer Engine for Dravya AI Engine.
    Handles training/validation loops, metrics monitoring, checkpointing,
    class mapping persistence, and model version registration.
    """

    def __init__(
        self,
        model: PlantClassifier,
        config: ModelConfig,
        class_to_idx: Dict[str, int],
        idx_to_class: Dict[int, str],
        train_loader: DataLoader,
        val_loader: DataLoader,
    ):
        self.config = config
        self.class_to_idx = class_to_idx
        self.idx_to_class = idx_to_class
        self.train_loader = train_loader
        self.val_loader = val_loader

        # Device selection
        if config.device == "cuda" and torch.cuda.is_available():
            self.device = torch.device("cuda")
        else:
            self.device = torch.device("cpu")

        self.model = model.to(self.device)
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=config.learning_rate,
            weight_decay=config.weight_decay,
        )

        # Version Directory Setup
        self.version_manager = ModelVersionManager(config.models_dir)
        self.version_dir = self.version_manager.get_version_dir(config.model_version)
        self.version_dir.mkdir(parents=True, exist_ok=True)

        self.best_val_f1 = -1.0
        self.history: List[Dict[str, Any]] = []

    def train_epoch(self) -> Dict[str, float]:
        self.model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for images, labels in self.train_loader:
            images = images.to(self.device)
            labels = labels.to(self.device)

            self.optimizer.zero_grad()
            outputs = self.model(images)
            loss = self.criterion(outputs, labels)
            loss.backward()
            self.optimizer.step()

            running_loss += loss.item() * images.size(0)
            preds = torch.argmax(outputs, dim=1)
            correct += (preds == labels).sum().item()
            total += images.size(0)

        epoch_loss = running_loss / total if total > 0 else 0.0
        epoch_acc = correct / total if total > 0 else 0.0
        return {"loss": round(epoch_loss, 4), "accuracy": round(epoch_acc, 4)}

    def evaluate(self) -> Dict[str, Any]:
        self.model.eval()
        running_loss = 0.0
        all_preds = []
        all_labels = []

        with torch.no_grad():
            for images, labels in self.val_loader:
                images = images.to(self.device)
                labels = labels.to(self.device)

                outputs = self.model(images)
                loss = self.criterion(outputs, labels)

                running_loss += loss.item() * images.size(0)
                preds = torch.argmax(outputs, dim=1)

                all_preds.extend(preds.cpu().numpy().tolist())
                all_labels.extend(labels.cpu().numpy().tolist())

        total = len(all_labels)
        epoch_loss = running_loss / total if total > 0 else 0.0

        metrics = compute_metrics(
            y_true=all_labels,
            y_pred=all_preds,
            num_classes=self.model.num_classes,
        )
        metrics["loss"] = round(epoch_loss, 4)
        return metrics

    def train(self) -> Dict[str, Any]:

        start_time = time.time()
        print(f"Starting training run for version '{self.config.model_version}' on device '{self.device}'...")
        print(f"Architecture: {self.config.architecture}, Num Classes: {self.model.num_classes}, Epochs: {self.config.epochs}")

        # Save initial class mapping JSON
        self.save_class_mapping()

        best_metrics = {}

        for epoch in range(1, self.config.epochs + 1):
            train_res = self.train_epoch()
            val_res = self.evaluate()

            epoch_log = {
                "epoch": epoch,
                "train_loss": train_res["loss"],
                "train_acc": train_res["accuracy"],
                "val_loss": val_res["loss"],
                "val_acc": val_res["accuracy"],
                "val_f1": val_res["f1_score"],
            }
            self.history.append(epoch_log)

            print(
                f"Epoch [{epoch}/{self.config.epochs}] | "
                f"Train Loss: {train_res['loss']:.4f}, Train Acc: {train_res['accuracy']:.4f} | "
                f"Val Loss: {val_res['loss']:.4f}, Val Acc: {val_res['accuracy']:.4f}, Val F1: {val_res['f1_score']:.4f}"
            )

            # Checkpoint saving
            is_best = val_res["f1_score"] >= self.best_val_f1
            if is_best:
                self.best_val_f1 = val_res["f1_score"]
                best_metrics = val_res

            self.save_checkpoint(epoch=epoch, metrics=val_res, is_best=is_best)

        elapsed = round(time.time() - start_time, 2)
        summary = {
            "version": self.config.model_version,
            "architecture": self.config.architecture,
            "num_classes": self.model.num_classes,
            "epochs_completed": self.config.epochs,
            "training_time_seconds": elapsed,
            "best_val_f1": self.best_val_f1,
            "val_metrics": best_metrics or (self.history[-1] if self.history else {}),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        # Save metadata and promote active version
        self.save_metadata(summary)
        self.version_manager.set_active_version(self.config.model_version)

        return summary

    def save_class_mapping(self) -> None:
        mapping_file = self.version_dir / "class_mapping.json"
        data = {
            "model_version": self.config.model_version,
            "num_classes": len(self.class_to_idx),
            "class_to_idx": self.class_to_idx,
            "idx_to_class": {str(k): v for k, v in self.idx_to_class.items()},
        }
        atomic_json_write(mapping_file, data)

    def save_checkpoint(
        self, epoch: int, metrics: Dict[str, Any], is_best: bool = False
    ) -> Path:
        checkpoint_data = {
            "epoch": epoch,
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "config": self.config.to_dict(),
            "metrics": metrics,
            "class_to_idx": self.class_to_idx,
        }

        latest_path = self.version_dir / "latest_checkpoint.pth"
        torch.save(checkpoint_data, latest_path)

        if is_best:
            best_path = self.version_dir / "best_model.pth"
            torch.save(checkpoint_data, best_path)

        return latest_path

    def save_metadata(self, metadata: Dict[str, Any]) -> None:
        meta_file = self.version_dir / "model_metadata.json"
        metadata["history"] = self.history
        atomic_json_write(meta_file, metadata)
