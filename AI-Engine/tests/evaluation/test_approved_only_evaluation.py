import json
import pytest

from src.models.config import ModelConfig
from src.models.plant_classifier import PlantClassifier
from src.training.trainer import ModelTrainer
from src.training.dataset import DravyaDataset
from src.evaluation.evaluator import ModelEvaluator
from torch.utils.data import DataLoader


def test_evaluator_rejects_unapproved_records(tmp_path):
    """
    Verifies that ModelEvaluator ingests ONLY APPROVED canonical dataset records,
    excluding UNREVIEWED, NEEDS_REVIEW, and REJECTED records automatically.
    """
    models_dir = tmp_path / "models"
    output_dir = tmp_path / "reports_eval"
    version_id = "v1-approved-test"

    # Training records (APPROVED)
    train_records = [
        {"canonical_name": "Saraca asoca", "mapping_status": "APPROVED", "sha256": "s1"},
        {"canonical_name": "Clerodendrum splendens", "mapping_status": "APPROVED", "sha256": "s2"},
    ]

    config = ModelConfig(models_dir=str(models_dir), model_version=version_id, epochs=1, batch_size=2)
    model = PlantClassifier(num_classes=2, pretrained=False)
    ds = DravyaDataset(records=train_records)
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

    # Manifest with APPROVED + UNREVIEWED + NEEDS_REVIEW + REJECTED
    mixed_records = [
        {"canonical_name": "Saraca asoca", "mapping_status": "APPROVED", "sha256": "s1"},
        {"canonical_name": "Clerodendrum splendens", "mapping_status": "APPROVED", "sha256": "s2"},
        {"canonical_name": "Unknown Plant A", "mapping_status": "UNREVIEWED", "sha256": "u1"},
        {"canonical_name": "Unknown Plant B", "mapping_status": "NEEDS_REVIEW", "sha256": "n1"},
        {"canonical_name": "Unknown Plant C", "mapping_status": "REJECTED", "sha256": "r1"},
    ]

    manifest_path = tmp_path / "mixed_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump({"status": "SUCCESS", "records": mixed_records}, f)

    evaluator = ModelEvaluator(
        version=version_id,
        manifest_path=manifest_path,
        models_dir=models_dir,
        output_dir=output_dir,
        device="cpu",
    )

    # Dataset size should be strictly 2 approved records
    assert len(evaluator.eval_dataset) == 2
    assert "Unknown Plant A" not in evaluator.eval_dataset.class_to_idx
    assert "Unknown Plant B" not in evaluator.eval_dataset.class_to_idx
    assert "Unknown Plant C" not in evaluator.eval_dataset.class_to_idx

    res = evaluator.evaluate()
    assert res["total_evaluated_samples"] == 2
