import json
import pytest

from src.training.dataset import DravyaDataset
from src.training.trainer import ModelTrainer
from src.models.config import ModelConfig
from src.models.plant_classifier import PlantClassifier
from torch.utils.data import DataLoader


def test_dynamic_class_mapping_generation():
    records = [
        {"canonical_name": "Saraca asoca", "mapping_status": "APPROVED"},
        {"canonical_name": "Clerodendrum splendens", "mapping_status": "APPROVED"},
        {"canonical_name": "Aloe vera", "mapping_status": "APPROVED"},
    ]

    dataset = DravyaDataset(records=records)
    class_to_idx = dataset.class_to_idx
    idx_to_class = dataset.idx_to_class

    # Verify deterministic alphabetical sorting
    expected_classes = ["Aloe vera", "Clerodendrum splendens", "Saraca asoca"]
    assert list(class_to_idx.keys()) == expected_classes
    assert class_to_idx["Aloe vera"] == 0
    assert class_to_idx["Clerodendrum splendens"] == 1
    assert class_to_idx["Saraca asoca"] == 2

    assert idx_to_class[0] == "Aloe vera"
    assert idx_to_class[1] == "Clerodendrum splendens"
    assert idx_to_class[2] == "Saraca asoca"


def test_class_mapping_persistence(tmp_path):
    records = [
        {"canonical_name": "Saraca asoca", "mapping_status": "APPROVED"},
        {"canonical_name": "Aloe vera", "mapping_status": "APPROVED"},
    ]
    dataset = DravyaDataset(records=records)

    config = ModelConfig(models_dir=str(tmp_path / "models"), model_version="v1-test")
    model = PlantClassifier(num_classes=2, pretrained=False)
    loader = DataLoader(dataset, batch_size=1)

    trainer = ModelTrainer(
        model=model,
        config=config,
        class_to_idx=dataset.class_to_idx,
        idx_to_class=dataset.idx_to_class,
        train_loader=loader,
        val_loader=loader,
    )

    trainer.save_class_mapping()

    mapping_file = trainer.version_dir / "class_mapping.json"
    assert mapping_file.exists()

    with open(mapping_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["num_classes"] == 2
    assert data["class_to_idx"]["Aloe vera"] == 0
    assert data["class_to_idx"]["Saraca asoca"] == 1
    assert data["idx_to_class"]["0"] == "Aloe vera"
    assert data["idx_to_class"]["1"] == "Saraca asoca"
