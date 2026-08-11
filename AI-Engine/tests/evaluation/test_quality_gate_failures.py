import math
import pytest
from pathlib import Path

from src.evaluation.quality_gate import ModelQualityGate


@pytest.fixture
def base_eval_dict():
    return {
        "model_version": "v1",
        "architecture": "efficientnet_b0",
        "num_classes": 2,
        "total_evaluated_samples": 50,
        "metrics": {
            "accuracy": 0.80,
            "precision": 0.80,
            "recall": 0.80,
            "f1_score": 0.80,
            "per_class_precision": [0.8, 0.8],
            "per_class_recall": [0.8, 0.8],
            "per_class_f1": [0.8, 0.8],
            "confusion_matrix": [[20, 5], [5, 20]],
        },
    }


def test_failure_missing_artifact(tmp_path):
    missing_file = tmp_path / "non_existent.json"
    gate = ModelQualityGate()
    res = gate.validate(missing_file, model_version="v1")

    assert res["passed"] is False
    assert "artifact_exists" in res["failed_checks"]


def test_failure_accuracy_below_threshold(base_eval_dict):
    base_eval_dict["metrics"]["accuracy"] = 0.50  # Threshold is 0.70
    gate = ModelQualityGate(min_accuracy=0.70)
    res = gate.validate(base_eval_dict, model_version="v1")

    assert res["passed"] is False
    assert "accuracy_passed" in res["failed_checks"]


def test_failure_f1_below_threshold(base_eval_dict):
    base_eval_dict["metrics"]["f1_score"] = 0.40  # Threshold is 0.70
    gate = ModelQualityGate(min_macro_f1=0.70)
    res = gate.validate(base_eval_dict, model_version="v1")

    assert res["passed"] is False
    assert "macro_f1_passed" in res["failed_checks"]


def test_failure_nan_metric_values(base_eval_dict):
    base_eval_dict["metrics"]["accuracy"] = float("nan")
    gate = ModelQualityGate()
    res = gate.validate(base_eval_dict, model_version="v1")

    assert res["passed"] is False
    assert "no_nan_values" in res["failed_checks"] or "accuracy_passed" in res["failed_checks"]


def test_failure_missing_class_coverage(base_eval_dict):
    # num_classes = 2, but per_class_f1 has only 1 item
    base_eval_dict["metrics"]["per_class_f1"] = [0.8]
    gate = ModelQualityGate(require_all_classes=True)
    res = gate.validate(base_eval_dict, model_version="v1")

    assert res["passed"] is False
    assert "classes_evaluated_valid" in res["failed_checks"]


def test_failure_confusion_matrix_dimension_mismatch(base_eval_dict):
    # num_classes = 2, but confusion_matrix is 3x3
    base_eval_dict["metrics"]["confusion_matrix"] = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    gate = ModelQualityGate()
    res = gate.validate(base_eval_dict, model_version="v1")

    assert res["passed"] is False
    assert "confusion_matrix_valid" in res["failed_checks"]


def test_failure_zero_evaluated_samples(base_eval_dict):
    base_eval_dict["total_evaluated_samples"] = 0
    gate = ModelQualityGate()
    res = gate.validate(base_eval_dict, model_version="v1")

    assert res["passed"] is False
    assert "total_samples_valid" in res["failed_checks"]
