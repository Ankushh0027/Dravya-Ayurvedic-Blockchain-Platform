import json
import pytest

from src.models.config import ModelConfig
from src.models.plant_classifier import PlantClassifier
from src.training.trainer import ModelTrainer
from src.training.dataset import DravyaDataset
from src.evaluation.evaluator import ModelEvaluator
from torch.utils.data import DataLoader


def test_evaluation_json_output_schema_and_values(tmp_path):
    models_dir = tmp_path / "models"
    output_dir = tmp_path / "reports_eval"
    version_id = "v1-schema-test"

    records = [
        {"canonical_name": "Aloe vera", "mapping_status": "APPROVED", "sha256": "a1"},
        {"canonical_name": "Neem", "mapping_status": "APPROVED", "sha256": "n1"},
    ]

    manifest_path = tmp_path / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump({"status": "SUCCESS", "records": records}, f)

    config = ModelConfig(models_dir=str(models_dir), model_version=version_id, epochs=1, batch_size=2)
    model = PlantClassifier(num_classes=2, pretrained=False)
    ds = DravyaDataset(records=records)
    loader = DataLoader(ds, batch_size=2)

    trainer = ModelTrainer(
        model=model,
        config=config,
        class_to_idx=ds.class_to_idx,
        idx_to_class=ds.idx_to_class,
        train_loader=loader,
        val_loader=loader,
    )
    trainer.train()

    evaluator = ModelEvaluator(
        version=version_id,
        manifest_path=manifest_path,
        models_dir=models_dir,
        output_dir=output_dir,
        device="cpu",
    )

    res = evaluator.evaluate()

    # Required Schema Checks
    required_keys = [
        "model_version",
        "architecture",
        "evaluated_at",
        "checkpoint_name",
        "num_classes",
        "total_evaluated_samples",
        "random_seed",
        "evaluation_time_seconds",
        "metrics",
        "class_mapping",
        "dataset_manifest_path",
    ]

    for key in required_keys:
        assert key in res, f"Missing required key '{key}' in evaluation output"

    metrics_keys = [
        "accuracy",
        "precision",
        "recall",
        "f1_score",
        "per_class_precision",
        "per_class_recall",
        "per_class_f1",
        "confusion_matrix",
    ]
    for m_key in metrics_keys:
        assert m_key in res["metrics"], f"Missing metric key '{m_key}' in evaluation metrics"

    # Schema Value Bounds Check
    assert res["model_version"] == version_id
    assert res["num_classes"] == 2
    assert res["total_evaluated_samples"] == 2
    assert 0.0 <= res["metrics"]["accuracy"] <= 1.0
    assert 0.0 <= res["metrics"]["f1_score"] <= 1.0
    assert len(res["metrics"]["confusion_matrix"]) == 2
