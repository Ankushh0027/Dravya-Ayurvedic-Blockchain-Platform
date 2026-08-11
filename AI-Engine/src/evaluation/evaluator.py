import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

import torch
from torch.utils.data import DataLoader

from src.data.paths import get_project_root, get_reports_dir, get_evaluation_reports_dir, get_dataset_paths
from src.data.taxonomy_review import atomic_json_write
from src.models.config import load_model_config
from src.models.plant_classifier import PlantClassifier
from src.models.version_manager import ModelVersionManager
from src.training.dataset import DravyaDataset, get_transforms, load_canonical_records
from src.training.metrics import compute_metrics


class ModelEvaluator:
    """
    Reproducible Production Model Evaluator for Dravya AI Engine.
    Loads versioned checkpoints, applies APPROVED-only dataset safety filters,
    runs deterministic batch inference preprocessing, calculates comprehensive evaluation metrics,
    and exports git-isolated evaluation result artifacts.
    """

    def __init__(
        self,
        version: str = "v1-smoke",
        checkpoint_name: str = "best_model.pth",
        manifest_path: Optional[Union[str, Path]] = None,
        models_dir: Optional[Union[str, Path]] = None,
        output_dir: Optional[Union[str, Path]] = None,
        device: Optional[str] = None,
        dataset_roots: Optional[Dict[str, Path]] = None,
    ):
        self.version = version
        self.checkpoint_name = checkpoint_name
        self.version_manager = ModelVersionManager(models_dir)
        self.version_dir = self.version_manager.get_version_dir(version)

        if not self.version_dir.exists():
            raise FileNotFoundError(
                f"Model version directory '{version}' not found at {self.version_dir}"
            )

        # 1. Load class mapping
        class_mapping_path = self.version_dir / "class_mapping.json"
        if not class_mapping_path.exists():
            raise FileNotFoundError(
                f"Class mapping file not found at {class_mapping_path}"
            )
        with open(class_mapping_path, "r", encoding="utf-8") as f:
            class_map_data = json.load(f)

        self.class_to_idx: Dict[str, int] = class_map_data.get("class_to_idx", {})
        self.idx_to_class: Dict[int, str] = {
            int(k): v for k, v in class_map_data.get("idx_to_class", {}).items()
        }
        self.num_classes = len(self.class_to_idx)

        # 2. Load model metadata & config
        meta_path = self.version_dir / "model_metadata.json"
        if meta_path.exists():
            with open(meta_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}

        self.architecture = self.metadata.get("architecture", "efficientnet_b0")
        self.image_size = self.metadata.get("config", {}).get("image_size", 224)
        self.random_seed = self.metadata.get("config", {}).get("random_seed", 42)

        # 3. Output directory setup
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = get_evaluation_reports_dir()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Device selection
        if device == "cuda" and torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif device == "cpu":
            self.device = torch.device("cpu")
        else:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # 4. Load model weights
        checkpoint_path = self.version_dir / checkpoint_name
        if not checkpoint_path.exists():
            checkpoint_path = self.version_dir / "latest_checkpoint.pth"

        if not checkpoint_path.exists():
            raise FileNotFoundError(
                f"No checkpoint found at {self.version_dir / checkpoint_name}"
            )

        self.model = PlantClassifier(
            num_classes=self.num_classes,
            architecture=self.architecture,
            pretrained=False,
        )
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        state_dict = checkpoint.get("model_state_dict", checkpoint)
        self.model.load_state_dict(state_dict)
        self.model.to(self.device)
        self.model.eval()

        # 5. Load canonical dataset manifest & enforce APPROVED-only filter
        if manifest_path is None:
            manifest_path = get_reports_dir() / "canonical_dataset_manifest_v1.json"
        self.manifest_path = Path(manifest_path)
        records = load_canonical_records(self.manifest_path)

        # Ingestion via DravyaDataset enforces mapping_status == APPROVED
        eval_transform = get_transforms(image_size=self.image_size, is_training=False)
        self.eval_dataset = DravyaDataset(
            records=records,
            transform=eval_transform,
            class_to_idx=self.class_to_idx,
            dataset_roots=dataset_roots,
        )

        self.eval_loader = DataLoader(
            self.eval_dataset,
            batch_size=16,
            shuffle=False,
            num_workers=0,
        )

    def evaluate(self) -> Dict[str, Any]:
        """
        Executes model evaluation pass over APPROVED canonical dataset records,
        calculates metrics, and exports artifact to reports/model_evaluation/.
        """
        start_time = time.time()
        self.model.eval()

        all_preds = []
        all_labels = []

        with torch.no_grad():
            for images, labels in self.eval_loader:
                images = images.to(self.device)
                labels = labels.to(self.device)

                outputs = self.model(images)
                preds = torch.argmax(outputs, dim=1)

                all_preds.extend(preds.cpu().numpy().tolist())
                all_labels.extend(labels.cpu().numpy().tolist())

        total_samples = len(all_labels)
        metrics = compute_metrics(
            y_true=all_labels,
            y_pred=all_preds,
            num_classes=self.num_classes,
        )

        elapsed = round(time.time() - start_time, 2)

        result = {
            "model_version": self.version,
            "architecture": self.architecture,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "checkpoint_name": self.checkpoint_name,
            "num_classes": self.num_classes,
            "total_evaluated_samples": total_samples,
            "random_seed": self.random_seed,
            "evaluation_time_seconds": elapsed,
            "metrics": metrics,
            "class_mapping": {
                "class_to_idx": self.class_to_idx,
                "idx_to_class": {str(k): v for k, v in self.idx_to_class.items()},
            },
            "dataset_manifest_path": str(self.manifest_path),
        }

        # Save evaluation report artifact JSON
        output_file = self.output_dir / f"{self.version}_evaluation.json"
        atomic_json_write(output_file, result)

        return result
