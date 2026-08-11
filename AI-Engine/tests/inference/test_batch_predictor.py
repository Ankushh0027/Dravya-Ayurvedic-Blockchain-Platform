import json
import pytest
from pathlib import Path
from PIL import Image
import numpy as np

from src.models.config import ModelConfig
from src.models.plant_classifier import PlantClassifier
from src.training.trainer import ModelTrainer
from src.training.dataset import DravyaDataset
from src.inference.batch_predictor import BatchPlantPredictor
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

    trainer.train()
    return models_dir, "v1-test"


def test_batch_predictor_scan_and_predict(trained_dummy_model, tmp_path):
    models_dir, version = trained_dummy_model

    # Create dummy images
    img_dir = tmp_path / "test_images"
    img_dir.mkdir()

    img1_path = img_dir / "leaf1.jpg"
    img2_path = img_dir / "leaf2.png"

    arr1 = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
    arr2 = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)

    Image.fromarray(arr1).save(img1_path)
    Image.fromarray(arr2).save(img2_path)

    batch_pred = BatchPlantPredictor(version=version, models_dir=models_dir, device="cpu")
    files = batch_pred.scan_image_files(img_dir)
    assert len(files) == 2

    results = batch_pred.predict_batch(files, top_k=2, show_progress=False)
    assert len(results) == 2
    assert results[0]["status"] == "SUCCESS"
    assert results[1]["status"] == "SUCCESS"

    # Export JSON
    json_out = tmp_path / "results.json"
    batch_pred.export_results(results, json_out, format_type="json")
    assert json_out.exists()
    with open(json_out, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["total_images"] == 2
    assert len(data["results"]) == 2

    # Export CSV
    csv_out = tmp_path / "results.csv"
    batch_pred.export_results(results, csv_out, format_type="csv")
    assert csv_out.exists()
