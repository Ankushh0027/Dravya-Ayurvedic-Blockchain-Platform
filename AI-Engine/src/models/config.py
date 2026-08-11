import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, Any, Optional, Union

from src.data.paths import load_config, get_project_root, get_reports_dir


@dataclass
class ModelConfig:
    """
    Configuration parameters for model architecture, dataset loading,
    training hyperparameters, versioning, and execution device.
    """

    architecture: str = "efficientnet_b0"
    image_size: int = 224
    batch_size: int = 16
    epochs: int = 5
    learning_rate: float = 1e-3
    weight_decay: float = 1e-4
    validation_split: float = 0.2
    random_seed: int = 42
    model_version: str = "v1"
    device: str = "cpu"
    dataset_manifest_path: Optional[str] = None
    models_dir: Optional[str] = None

    def __post_init__(self):
        # Resolve dataset manifest path fallback
        if not self.dataset_manifest_path:
            manifest_file = get_reports_dir() / f"canonical_dataset_manifest_{self.model_version}.json"
            if not manifest_file.exists():
                manifest_file = get_reports_dir() / "canonical_dataset_manifest_v1.json"
            self.dataset_manifest_path = str(manifest_file)

        # Resolve models output directory fallback
        if not self.models_dir:
            config_dict = load_config()
            rel_models = config_dict.get("paths", {}).get("model_output", "models")
            models_path = Path(rel_models)
            if not models_path.is_absolute():
                models_path = get_project_root() / models_path
            self.models_dir = str(models_path.resolve())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def get_version_dir(self) -> Path:
        return Path(self.models_dir) / self.model_version


def load_model_config(
    config_path: Optional[Union[str, Path]] = None, **kwargs
) -> ModelConfig:
    """
    Loads model configuration combining defaults, config.yaml, and explicit overrides.
    """
    yaml_config = load_config()
    model_yaml = yaml_config.get("model", {})

    merged = {
        "architecture": model_yaml.get("architecture", "efficientnet_b0"),
        "image_size": int(model_yaml.get("image_size", 224)),
        "batch_size": int(model_yaml.get("batch_size", 16)),
        "epochs": int(model_yaml.get("epochs", 5)),
        "learning_rate": float(model_yaml.get("learning_rate", 0.001)),
        "validation_split": float(model_yaml.get("validation_split", 0.2)),
        "random_seed": int(model_yaml.get("random_seed", 42)),
        "model_version": str(model_yaml.get("model_version", "v1")),
        "device": str(model_yaml.get("device", "cpu")),
    }

    # Environment variable overrides
    if os.getenv("DRAVYA_MODEL_ARCH"):
        merged["architecture"] = os.getenv("DRAVYA_MODEL_ARCH")
    if os.getenv("DRAVYA_IMAGE_SIZE"):
        merged["image_size"] = int(os.getenv("DRAVYA_IMAGE_SIZE"))
    if os.getenv("DRAVYA_BATCH_SIZE"):
        merged["batch_size"] = int(os.getenv("DRAVYA_BATCH_SIZE"))
    if os.getenv("DRAVYA_EPOCHS"):
        merged["epochs"] = int(os.getenv("DRAVYA_EPOCHS"))
    if os.getenv("DRAVYA_LEARNING_RATE"):
        merged["learning_rate"] = float(os.getenv("DRAVYA_LEARNING_RATE"))
    if os.getenv("DRAVYA_VAL_SPLIT"):
        merged["validation_split"] = float(os.getenv("DRAVYA_VAL_SPLIT"))
    if os.getenv("DRAVYA_RANDOM_SEED"):
        merged["random_seed"] = int(os.getenv("DRAVYA_RANDOM_SEED"))
    if os.getenv("DRAVYA_MODEL_VERSION"):
        merged["model_version"] = os.getenv("DRAVYA_MODEL_VERSION")
    if os.getenv("DRAVYA_DEVICE"):
        merged["device"] = os.getenv("DRAVYA_DEVICE")

    # Explicit kwargs override
    for k, v in kwargs.items():
        if v is not None and hasattr(ModelConfig, k):
            merged[k] = v

    return ModelConfig(**merged)
