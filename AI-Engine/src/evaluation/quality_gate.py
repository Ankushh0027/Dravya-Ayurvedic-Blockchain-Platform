import json
import math
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from src.data.paths import load_config


class ModelQualityGate:
    """
    Production Model Quality Gate for Dravya AI Engine.
    Validates evaluation results against configurable quality thresholds
    (accuracy, macro F1, precision, recall, confusion matrix dimensions, NaN safety)
    before allowing a candidate model version to be promoted to production active state.
    """

    def __init__(
        self,
        min_accuracy: Optional[float] = None,
        min_macro_f1: Optional[float] = None,
        min_precision: Optional[float] = None,
        min_recall: Optional[float] = None,
        require_all_classes: Optional[bool] = None,
        config_path: Optional[Union[str, Path]] = None,
    ):
        yaml_config = load_config()
        gate_config = yaml_config.get("evaluation", {}).get("quality_gate", {})

        self.min_accuracy = (
            min_accuracy
            if min_accuracy is not None
            else float(gate_config.get("min_accuracy", 0.70))
        )
        self.min_macro_f1 = (
            min_macro_f1
            if min_macro_f1 is not None
            else float(gate_config.get("min_macro_f1", 0.70))
        )
        self.min_precision = (
            min_precision
            if min_precision is not None
            else float(gate_config.get("min_precision", 0.70))
        )
        self.min_recall = (
            min_recall
            if min_recall is not None
            else float(gate_config.get("min_recall", 0.70))
        )
        self.require_all_classes = (
            require_all_classes
            if require_all_classes is not None
            else bool(gate_config.get("require_all_classes", True))
        )

    def validate(
        self,
        evaluation_result: Union[Dict[str, Any], str, Path],
        model_version: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Validates evaluation results against quality thresholds and schema invariants.
        Returns a structured dictionary with passed boolean, individual check statuses,
        and list of failed check names.
        """
        checks: Dict[str, bool] = {
            "artifact_exists": False,
            "version_matches": False,
            "total_samples_valid": False,
            "accuracy_passed": False,
            "macro_f1_passed": False,
            "precision_passed": False,
            "recall_passed": False,
            "confusion_matrix_valid": False,
            "classes_evaluated_valid": False,
            "no_nan_values": False,
            "metadata_consistent": False,
        }

        data: Dict[str, Any] = {}

        # 1. Check Artifact Existence / Loading
        if isinstance(evaluation_result, (str, Path)):
            artifact_path = Path(evaluation_result)
            if artifact_path.exists():
                try:
                    with open(artifact_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    checks["artifact_exists"] = True
                except Exception:
                    checks["artifact_exists"] = False
            else:
                checks["artifact_exists"] = False
        elif isinstance(evaluation_result, dict):
            data = evaluation_result
            checks["artifact_exists"] = True

        if not checks["artifact_exists"]:
            failed_checks = [k for k, v in checks.items() if not v]
            return {
                "passed": False,
                "model_version": model_version or "UNKNOWN",
                "thresholds": self._get_thresholds_dict(),
                "checks": checks,
                "failed_checks": failed_checks,
                "metrics": {},
                "reason": "Evaluation artifact missing or unreadable.",
            }

        eval_version = data.get("model_version", "")
        target_version = model_version or eval_version

        # 2. Check Version Matching
        if model_version is not None:
            checks["version_matches"] = (eval_version == model_version)
        else:
            checks["version_matches"] = bool(eval_version)

        # 3. Check Total Samples
        total_samples = data.get("total_evaluated_samples", 0)
        checks["total_samples_valid"] = isinstance(total_samples, int) and total_samples > 0

        # Extract metrics
        metrics = data.get("metrics", {})
        accuracy = metrics.get("accuracy")
        f1_score = metrics.get("f1_score")
        precision = metrics.get("precision")
        recall = metrics.get("recall")

        # 4. Check Accuracy
        if isinstance(accuracy, (int, float)) and not math.isnan(accuracy):
            checks["accuracy_passed"] = (accuracy >= self.min_accuracy)

        # 5. Check Macro F1
        if isinstance(f1_score, (int, float)) and not math.isnan(f1_score):
            checks["macro_f1_passed"] = (f1_score >= self.min_macro_f1)

        # 6. Check Precision
        if isinstance(precision, (int, float)) and not math.isnan(precision):
            checks["precision_passed"] = (precision >= self.min_precision)

        # 7. Check Recall
        if isinstance(recall, (int, float)) and not math.isnan(recall):
            checks["recall_passed"] = (recall >= self.min_recall)

        num_classes = data.get("num_classes", 0)

        # 8. Check Confusion Matrix Dimensions
        cm = metrics.get("confusion_matrix", [])
        if isinstance(cm, list) and len(cm) == num_classes and num_classes > 0:
            row_valid = all(isinstance(row, list) and len(row) == num_classes for row in cm)
            checks["confusion_matrix_valid"] = row_valid
        else:
            checks["confusion_matrix_valid"] = False

        # 9. Check Class Coverage
        per_class_f1 = metrics.get("per_class_f1", [])
        if self.require_all_classes:
            checks["classes_evaluated_valid"] = (
                isinstance(per_class_f1, list)
                and len(per_class_f1) == num_classes
                and num_classes > 0
            )
        else:
            checks["classes_evaluated_valid"] = True

        # 10. Check NaN / Infinite Values Safety
        val_list = [accuracy, f1_score, precision, recall]
        if isinstance(per_class_f1, list):
            val_list.extend(per_class_f1)

        all_valid_numbers = True
        for v in val_list:
            if not isinstance(v, (int, float)) or math.isnan(v) or math.isinf(v) or v < 0.0 or v > 1.0:
                all_valid_numbers = False
                break
        checks["no_nan_values"] = all_valid_numbers

        # 11. Check Metadata Consistency
        arch = data.get("architecture")
        checks["metadata_consistent"] = (
            isinstance(num_classes, int)
            and num_classes > 0
            and isinstance(arch, str)
            and len(arch.strip()) > 0
        )

        all_passed = all(checks.values())
        failed_checks = [k for k, v in checks.items() if not v]

        return {
            "passed": all_passed,
            "model_version": target_version,
            "thresholds": self._get_thresholds_dict(),
            "checks": checks,
            "failed_checks": failed_checks,
            "metrics": metrics,
            "evaluated_at": data.get("evaluated_at"),
        }

    def _get_thresholds_dict(self) -> Dict[str, Any]:
        return {
            "min_accuracy": self.min_accuracy,
            "min_macro_f1": self.min_macro_f1,
            "min_precision": self.min_precision,
            "min_recall": self.min_recall,
            "require_all_classes": self.require_all_classes,
        }
