import json
import pytest
from pathlib import Path

import torch
from src.models.config import ModelConfig
from src.models.plant_classifier import PlantClassifier
from src.training.trainer import ModelTrainer
from src.training.dataset import DravyaDataset
from src.evaluation.evaluator import ModelEvaluator
from torch.utils.data import DataLoader


@pytest.fixture
def mock_trained_version(tmp_path):
    """
    Creates a lightweight synthetic model version directory with checkpoints,
    class mapping, and model metadata for fast evaluation testing without large 48MB weight files.
    """
    models_dir = tmp_path / "models"
    output_dir = tmp_path / "reports_eval"
    version_id = "v1-eval-test"

    records = [
        {
            "record_id": "rec_001",
            "canonical_name": "Clerodendrum splendens",
            "mapping_status": "APPROVED",
            "sha256": "sha_001",
        },
        {
            "record_id": "rec_002",
            "canonical_name": "Saraca asoca",
            "mapping_status": "APPROVED",
            "sha256": "sha_002",
        },
    ]

    manifest_path = tmp_path / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "status": "SUCCESS",
                "records": records,
            },
            f,
        )

    dataset = DravyaDataset(records=records)
    config = ModelConfig(
        models_dir=str(models_dir),
        model_version=version_id,
        epochs=1,
        batch_size=2,
    )

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

    return models_dir, output_dir, version_id, manifest_path


def test_evaluator_execution_and_artifact_generation(mock_trained_version):
    models_dir, output_dir, version_id, manifest_path = mock_trained_version

    evaluator = ModelEvaluator(
        version=version_id,
        manifest_path=manifest_path,
        models_dir=models_dir,
        output_dir=output_dir,
        device="cpu",
    )

    res = evaluator.evaluate()

    assert res["model_version"] == version_id
    assert res["architecture"] == "efficientnet_b0"
    assert res["total_evaluated_samples"] == 2
    assert res["num_classes"] == 2
    assert "metrics" in res
    assert "accuracy" in res["metrics"]
    assert "f1_score" in res["metrics"]
    assert "confusion_matrix" in res["metrics"]

    artifact_file = output_dir / f"{version_id}_evaluation.json"
    assert artifact_file.exists()

    with open(artifact_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["model_version"] == version_id
    assert data["total_evaluated_samples"] == 2
