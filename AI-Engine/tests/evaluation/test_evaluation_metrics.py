import numpy as np
import pytest

from src.training.metrics import compute_metrics


def test_compute_metrics_perfect_predictions():
    y_true = [0, 1, 0, 1, 2]
    y_pred = [0, 1, 0, 1, 2]
    num_classes = 3

    metrics = compute_metrics(y_true, y_pred, num_classes)

    assert metrics["accuracy"] == 1.0
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["f1_score"] == 1.0
    assert metrics["confusion_matrix"] == [
        [2, 0, 0],
        [0, 2, 0],
        [0, 0, 1],
    ]


def test_compute_metrics_imperfect_predictions():
    y_true = [0, 0, 1, 1]
    y_pred = [0, 1, 0, 1]
    num_classes = 2

    metrics = compute_metrics(y_true, y_pred, num_classes)

    assert metrics["accuracy"] == 0.5
    assert 0.0 <= metrics["precision"] <= 1.0
    assert 0.0 <= metrics["recall"] <= 1.0
    assert 0.0 <= metrics["f1_score"] <= 1.0
    assert metrics["confusion_matrix"] == [
        [1, 1],
        [1, 1],
    ]


def test_compute_metrics_empty_inputs():
    metrics = compute_metrics([], [], num_classes=2)
    assert metrics["accuracy"] == 0.0
    assert metrics["f1_score"] == 0.0
    assert metrics["confusion_matrix"] == []
