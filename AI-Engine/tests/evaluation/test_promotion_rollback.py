import json
import pytest
from pathlib import Path

from src.evaluation.quality_gate import ModelQualityGate
from src.evaluation.model_promotion import ModelPromotionService
from src.models.version_manager import ModelVersionManager


@pytest.fixture
def multi_version_setup(tmp_path):
    models_dir = tmp_path / "models"
    output_dir = tmp_path / "reports_eval"
    models_dir.mkdir()
    output_dir.mkdir()

    for v_name in ["v1", "v2", "v3"]:
        v_dir = models_dir / v_name
        v_dir.mkdir()
        (v_dir / "best_model.pth").write_text(f"{v_name}_weights")
        (v_dir / "class_mapping.json").write_text(json.dumps({"class_to_idx": {"A": 0}}))
        (v_dir / "model_metadata.json").write_text(json.dumps({"architecture": "efficientnet_b0"}))

        eval_data = {
            "model_version": v_name,
            "architecture": "efficientnet_b0",
            "num_classes": 1,
            "total_evaluated_samples": 50,
            "metrics": {
                "accuracy": 0.85,
                "precision": 0.85,
                "recall": 0.85,
                "f1_score": 0.85,
                "per_class_precision": [0.85],
                "per_class_recall": [0.85],
                "per_class_f1": [0.85],
                "confusion_matrix": [[50]],
            },
        }
        with open(output_dir / f"{v_name}_evaluation.json", "w", encoding="utf-8") as f:
            json.dump(eval_data, f)

    vm = ModelVersionManager(models_dir=models_dir)
    vm.set_active_version("v1")
    return models_dir, output_dir, vm


def test_promotion_preserves_previous_active_version(multi_version_setup):
    models_dir, output_dir, vm = multi_version_setup

    service = ModelPromotionService(
        models_dir=models_dir,
        output_dir=output_dir,
        quality_gate=ModelQualityGate(min_accuracy=0.70),
    )

    # 1. Promote v2 from v1
    res1 = service.promote_model("v2")
    assert res1["status"] == "PROMOTED"
    assert res1["previous_active_version"] == "v1"
    assert vm.get_active_version() == "v2"

    # Verify v1 weights and directory are intact
    assert (models_dir / "v1" / "best_model.pth").exists()

    # 2. Promote v3 from v2
    res2 = service.promote_model("v3")
    assert res2["status"] == "PROMOTED"
    assert res2["previous_active_version"] == "v2"
    assert vm.get_active_version() == "v3"


def test_rollback_after_promotion(multi_version_setup):
    models_dir, output_dir, vm = multi_version_setup

    service = ModelPromotionService(
        models_dir=models_dir,
        output_dir=output_dir,
        quality_gate=ModelQualityGate(min_accuracy=0.70),
    )

    # Promote v2
    service.promote_model("v2")
    assert vm.get_active_version() == "v2"

    # Rollback (should automatically pick previous version v1)
    res_roll = service.rollback_promotion()
    assert res_roll["status"] == "ROLLED_BACK"
    assert res_roll["active_version"] == "v1"
    assert vm.get_active_version() == "v1"


def test_explicit_rollback_target(multi_version_setup):
    models_dir, output_dir, vm = multi_version_setup

    service = ModelPromotionService(
        models_dir=models_dir,
        output_dir=output_dir,
        quality_gate=ModelQualityGate(min_accuracy=0.70),
    )

    service.promote_model("v2")
    service.promote_model("v3")
    assert vm.get_active_version() == "v3"

    # Rollback explicitly to v1
    res_roll = service.rollback_promotion(target_version="v1")
    assert res_roll["status"] == "ROLLED_BACK"
    assert res_roll["active_version"] == "v1"
    assert vm.get_active_version() == "v1"
