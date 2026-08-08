from typing import Dict, Any, List, Union
import numpy as np


def compute_metrics(
    y_true: Union[List[int], np.ndarray],
    y_pred: Union[List[int], np.ndarray],
    num_classes: int,
) -> Dict[str, Any]:
    """
    Computes classification evaluation metrics: Accuracy, Per-Class Precision/Recall/F1,
    Macro Average F1, and Confusion Matrix.
    """
    y_true = np.array(y_true, dtype=int)
    y_pred = np.array(y_pred, dtype=int)

    total = len(y_true)
    if total == 0:
        return {
            "accuracy": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "confusion_matrix": [],
        }

    correct = int(np.sum(y_true == y_pred))
    accuracy = float(correct / total)

    cm = np.zeros((num_classes, num_classes), dtype=int)
    for t, p in zip(y_true, y_pred):
        if 0 <= t < num_classes and 0 <= p < num_classes:
            cm[t, p] += 1

    per_class_prec = []
    per_class_rec = []
    per_class_f1 = []

    for c in range(num_classes):
        tp = cm[c, c]
        fp = np.sum(cm[:, c]) - tp
        fn = np.sum(cm[c, :]) - tp

        prec = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
        rec = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        f1 = float(2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0

        per_class_prec.append(round(prec, 4))
        per_class_rec.append(round(rec, 4))
        per_class_f1.append(round(f1, 4))

    macro_prec = float(np.mean(per_class_prec)) if per_class_prec else 0.0
    macro_rec = float(np.mean(per_class_rec)) if per_class_rec else 0.0
    macro_f1 = float(np.mean(per_class_f1)) if per_class_f1 else 0.0

    return {
        "accuracy": round(accuracy, 4),
        "precision": round(macro_prec, 4),
        "recall": round(macro_rec, 4),
        "f1_score": round(macro_f1, 4),
        "per_class_precision": per_class_prec,
        "per_class_recall": per_class_rec,
        "per_class_f1": per_class_f1,
        "confusion_matrix": cm.tolist(),
    }
