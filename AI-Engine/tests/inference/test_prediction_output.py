import json
import pytest
from PIL import Image
import numpy as np
import torch

from src.models.config import ModelConfig
from src.models.plant_classifier import PlantClassifier
from src.training.trainer import ModelTrainer
from src.training.dataset import DravyaDataset
from src.inference.predictor import PlantPredictor
from torch.utils.data import DataLoader



@pytest.fixture
def trained_dummy_model(tmp_path):
    models_dir = tmp_path / "models"
    records = [
        {"canonical_name": "Clerodendrum splendens", "mapping_status": "APPROVED"},
        {"canonical_name": "Saraca asoca", "mapping_status": "APPROVED"},
    ]
    dataset = DravyaDataset(records=records)
    config = ModelConfig(models_dir=str(models_dir), model_version="v1-test", epochs=1, batch_size=2)

    model = PlantClassifier(num_classes=2, pretrained=False)
    loader = DataLoader(dataset, batch_size=2)

    trainer = ModelTrainer(
        model=model,
        config=config,
        class_to_idx=dataset.class_to_idx,
        idx_to_class=dataset.idx_to_class,
        train_loader=loader,
        val_loader=loader,
    )

    summary = trainer.train()
    return models_dir, "v1-test"


def test_plant_predictor_output_format(trained_dummy_model):
    models_dir, version = trained_dummy_model
    predictor = PlantPredictor(version=version, models_dir=models_dir, device="cpu")

    # Create synthetic test image
    arr = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
    test_img = Image.fromarray(arr)

    res = predictor.predict(test_img, top_k=2)

    assert "canonical_name" in res
    assert "confidence" in res
    assert "top_k" in res
    assert "model_version" in res
    assert "architecture" in res
    assert "num_classes" in res

    assert res["model_version"] == "v1-test"
    assert res["num_classes"] == 2
    assert len(res["top_k"]) == 2

    # Check confidence values format
    top_pred = res["top_k"][0]
    assert "canonical_name" in top_pred
    assert "confidence" in top_pred
    assert 0.0 <= top_pred["confidence"] <= 1.0

    # Top-k must be sorted descending by confidence
    assert res["top_k"][0]["confidence"] >= res["top_k"][1]["confidence"]


def test_v1_kaggle_taxonomy_mapping_resolution():
    """Verify that v1-kaggle loads all 82 taxonomy mappings and resolves DRAVYA_0022 correctly."""
    from src.data.paths import get_project_root
    v1_dir = get_project_root() / "models" / "v1-kaggle"
    if not (v1_dir / "best_model.pth").exists():
        pytest.skip("v1-kaggle weights not present in test environment")

    predictor = PlantPredictor(version="v1-kaggle", device="cpu")
    assert predictor.num_classes == 82
    assert len(predictor.taxonomy_map) >= 82

    # Check DRAVYA_0022 mapping
    info_0022 = predictor.taxonomy_map.get("DRAVYA_0022")
    assert info_0022 is not None
    assert info_0022["species_name"] == "Aloe vera"
    assert info_0022["scientific_name"] == "Aloe barbadensis"

    # Test predict method structure
    arr = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
    test_img = Image.fromarray(arr)
    res = predictor.predict(test_img, top_k=5)

    assert res["model_version"] == "v1-kaggle"
    assert res["class_id"] is not None
    assert res["species_name"] is not None
    # Species name should not be a raw class ID if mapped
    if res["class_id"] in predictor.taxonomy_map:
        assert res["species_name"] == predictor.taxonomy_map[res["class_id"]]["species_name"]
        assert res["scientific_name"] == predictor.taxonomy_map[res["class_id"]]["scientific_name"]


def test_taxonomy_missing_fallback(tmp_path):
    """Test that missing or unmapped classes fall back safely to raw class ID with scientific_name=None."""
    models_dir = tmp_path / "models"
    v_dir = models_dir / "v-test-unmapped"
    v_dir.mkdir(parents=True)

    # Save class mapping with an unknown class
    class_map = {
        "class_to_idx": {"DRAVYA_UNKNOWN_999": 0},
        "idx_to_class": {"0": "DRAVYA_UNKNOWN_999"},
    }
    with open(v_dir / "class_mapping.json", "w", encoding="utf-8") as f:
        json.dump(class_map, f)

    # Save dummy weights
    model = PlantClassifier(num_classes=1, pretrained=False)
    torch.save(model.state_dict(), v_dir / "best_model.pth")

    predictor = PlantPredictor(version="v-test-unmapped", models_dir=models_dir, device="cpu")
    arr = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
    test_img = Image.fromarray(arr)
    res = predictor.predict(test_img, top_k=1)

    assert res["class_id"] == "DRAVYA_UNKNOWN_999"
    assert res["species_name"] == "DRAVYA_UNKNOWN_999"
    assert res["scientific_name"] is None
