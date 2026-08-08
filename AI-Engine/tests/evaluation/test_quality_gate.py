import json
import pytest
from pathlib import Path

from src.evaluation.quality_gate import ModelQualityGate


@pytest.fixture
def passing_eval_result():
    return {
        "model_version": "v1",
        "architecture": "efficientnet_b0",
        "evaluated_at": "2026-08-08T00:00:00Z",
        "checkpoint_name": "best_model.pth",
        "num_classes": 2,
        "total_evaluated_samples": 100,
        "random_seed": 42,
        "metrics": {
            "accuracy": 0.85,
            "precision": 0.84,
            "recall": 0.83,
            "f1_score": 0.84,
            "per_class_precision": [0.85, 0.83],
            "per_class_recall": [0.84, 0.82],
            "per_class_f1": [0.845, 0.825],
            "confusion_matrix": [
                [42, 8],
                [7, 43],
            ],
        },
    }


def test_quality_gate_passing_model(passing_eval_result):
    gate = ModelQualityGate(
        min_accuracy=0.70,
        min_macro_f1=0.70,
        min_precision=0.70,
        min_recall=0.70,
        require_all_classes=True,
    )

    res = gate.validate(passing_eval_result, model_version="v1")

    assert res["passed"] is True
    assert res["model_version"] == "v1"
    assert len(res["failed_checks"]) == 0
    assert res["checks"]["accuracy_passed"] is True
    assert res["checks"]["macro_f1_passed"] is True
    assert res["checks"]["confusion_matrix_valid"] is True
    assert res["checks"]["no_nan_values"] is True


def test_quality_gate_custom_thresholds(passing_eval_result):
    # Set strict min_accuracy 0.90 (model has 0.85) -> should fail
    strict_gate = ModelQualityGate(min_accuracy=0.90)
    res_strict = strict_gate.validate(passing_eval_result, model_version="v1")

    assert res_strict["passed"] is False
    assert "accuracy_passed" in res_strict["failed_checks"]

    # Set lenient min_accuracy 0.50 -> should pass
    lenient_gate = ModelQualityGate(min_accuracy=0.50)
    res_lenient = lenient_gate.validate(passing_eval_result, model_version="v1")
    assert res_lenient["passed"] is True


def test_quality_gate_file_path_validation(tmp_path, passing_eval_result):
    eval_file = tmp_path / "v1_eval.json"
    with open(eval_file, "w", encoding="utf-8") as f:
        json.dump(passing_eval_result, f)

    gate = ModelQualityGate(min_accuracy=0.70, min_macro_f1=0.70)
    res = gate.validate(eval_file, model_version="v1")

    assert res["passed"] is True
    assert res["checks"]["artifact_exists"] is True
