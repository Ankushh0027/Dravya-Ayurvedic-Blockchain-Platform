import json
import pytest
from pathlib import Path

from src.evaluation.quality_gate import ModelQualityGate
from src.evaluation.model_promotion import ModelPromotionService
from src.models.version_manager import ModelVersionManager


@pytest.fixture
def mock_versions_setup(tmp_path):
    models_dir = tmp_path / "models"
    output_dir = tmp_path / "reports_eval"
    models_dir.mkdir()
    output_dir.mkdir()

    # Create v1 (previous active)
    v1_dir = models_dir / "v1"
    v1_dir.mkdir()
    (v1_dir / "best_model.pth").write_text("v1_weights")
    (v1_dir / "class_mapping.json").write_text(json.dumps({"class_to_idx": {"A": 0}}))
    (v1_dir / "model_metadata.json").write_text(json.dumps({"architecture": "efficientnet_b0"}))

    # Create v2 (candidate passing model)
    v2_dir = models_dir / "v2"
    v2_dir.mkdir()
    (v2_dir / "best_model.pth").write_text("v2_weights")
    (v2_dir / "class_mapping.json").write_text(json.dumps({"class_to_idx": {"A": 0, "B": 1}}))
    (v2_dir / "model_metadata.json").write_text(json.dumps({"architecture": "efficientnet_b0"}))

    eval_v2 = {
        "model_version": "v2",
        "architecture": "efficientnet_b0",
        "num_classes": 2,
        "total_evaluated_samples": 100,
        "metrics": {
            "accuracy": 0.85,
            "precision": 0.84,
            "recall": 0.83,
            "f1_score": 0.84,
            "per_class_precision": [0.85, 0.83],
            "per_class_recall": [0.84, 0.82],
            "per_class_f1": [0.845, 0.825],
            "confusion_matrix": [[42, 8], [7, 43]],
        },
    }
    with open(output_dir / "v2_evaluation.json", "w", encoding="utf-8") as f:
        json.dump(eval_v2, f)

    # Set v1 as active initially
    vm = ModelVersionManager(models_dir=models_dir)
    vm.set_active_version("v1")

    return models_dir, output_dir, vm


def test_successful_model_promotion(mock_versions_setup):
    models_dir, output_dir, vm = mock_versions_setup

    service = ModelPromotionService(
        models_dir=models_dir,
        output_dir=output_dir,
        quality_gate=ModelQualityGate(min_accuracy=0.70, min_macro_f1=0.70),
    )

    res = service.promote_model("v2")

    assert res["status"] == "PROMOTED"
    assert res["candidate_version"] == "v2"
    assert res["previous_active_version"] == "v1"
    assert vm.get_active_version() == "v2"

    # Audit log check
    audit_file = output_dir / "promotions.json"
    assert audit_file.exists()
    with open(audit_file, "r", encoding="utf-8") as f:
        audit_data = json.load(f)
    assert len(audit_data["promotions"]) >= 1
    assert audit_data["promotions"][-1]["status"] == "PROMOTED"


def test_blocked_promotion_on_quality_gate_failure(mock_versions_setup):
    models_dir, output_dir, vm = mock_versions_setup

    # Create v3 (failing candidate model with accuracy 0.40)
    v3_dir = models_dir / "v3"
    v3_dir.mkdir()
    (v3_dir / "best_model.pth").write_text("v3_weights")

    eval_v3 = {
        "model_version": "v3",
        "architecture": "efficientnet_b0",
        "num_classes": 2,
        "total_evaluated_samples": 100,
        "metrics": {
            "accuracy": 0.40,  # Below 0.70 threshold
            "precision": 0.40,
            "recall": 0.40,
            "f1_score": 0.40,
            "per_class_precision": [0.4, 0.4],
            "per_class_recall": [0.4, 0.4],
            "per_class_f1": [0.4, 0.4],
            "confusion_matrix": [[20, 30], [30, 20]],
        },
    }
    with open(output_dir / "v3_evaluation.json", "w", encoding="utf-8") as f:
        json.dump(eval_v3, f)

    service = ModelPromotionService(
        models_dir=models_dir,
        output_dir=output_dir,
        quality_gate=ModelQualityGate(min_accuracy=0.70, min_macro_f1=0.70),
    )

    res = service.promote_model("v3")

    assert res["status"] == "BLOCKED"
    assert res["reason"] == "QUALITY_GATE_FAILED"
    assert "accuracy_passed" in res["failed_checks"]
    # Active version must remain v1 (unmodified)
    assert vm.get_active_version() == "v1"
