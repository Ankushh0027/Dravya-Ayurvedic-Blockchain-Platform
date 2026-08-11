import json
import pytest
from pathlib import Path

from src.models.config import ModelConfig
from src.models.version_manager import ModelVersionManager
from src.models.plant_classifier import PlantClassifier
from src.training.trainer import ModelTrainer
from src.training.dataset import DravyaDataset, get_transforms
from torch.utils.data import DataLoader


@pytest.fixture
def temp_models_dir(tmp_path):
    models_dir = tmp_path / "models"
    models_dir.mkdir()
    return models_dir


def test_version_manager_lifecycle(temp_models_dir):
    vm = ModelVersionManager(models_dir=temp_models_dir)

    # 1. Create dummy version metadata
    v1_dir = temp_models_dir / "v1"
    v1_dir.mkdir()
    meta_v1 = {
        "version": "v1",
        "architecture": "efficientnet_b0",
        "epochs": 5,
        "created_at": "2026-08-08T00:00:00Z",
        "val_metrics": {"accuracy": 0.85, "f1_score": 0.84, "loss": 0.35},
    }
    with open(v1_dir / "model_metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta_v1, f)
    (v1_dir / "best_model.pth").write_text("dummy_weights")

    v2_dir = temp_models_dir / "v2"
    v2_dir.mkdir()
    meta_v2 = {
        "version": "v2",
        "architecture": "efficientnet_b0",
        "epochs": 10,
        "created_at": "2026-08-08T01:00:00Z",
        "val_metrics": {"accuracy": 0.92, "f1_score": 0.91, "loss": 0.22},
    }
    with open(v2_dir / "model_metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta_v2, f)
    (v2_dir / "best_model.pth").write_text("dummy_weights_v2")

    # 2. List versions
    versions = vm.list_versions()
    assert len(versions) == 2
    v_names = [v["version"] for v in versions]
    assert "v1" in v_names
    assert "v2" in v_names

    # 3. Active version promotion & retrieval
    vm.set_active_version("v1")
    assert vm.get_active_version() == "v1"

    vm.set_active_version("v2")
    assert vm.get_active_version() == "v2"

    # 4. Version comparison
    comp = vm.compare_versions("v1", "v2")
    assert comp["comparison"]["accuracy_diff"] == 0.07
    assert comp["comparison"]["f1_score_diff"] == 0.07
    assert comp["comparison"]["loss_diff"] == -0.13

    # 5. Rollback
    rolled_back = vm.rollback("v1")
    assert rolled_back == "v1"
    assert vm.get_active_version() == "v1"
