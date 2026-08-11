import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from src.data.paths import get_evaluation_reports_dir, get_project_root
from src.data.taxonomy_review import atomic_json_write
from src.evaluation.evaluator import ModelEvaluator
from src.evaluation.quality_gate import ModelQualityGate
from src.models.version_manager import ModelVersionManager


class ModelPromotionBlockedError(Exception):
    """Raised when model promotion is blocked due to quality gate failure."""
    pass


class ModelPromotionService:
    """
    Atomic Safe Model Promotion Service for Dravya AI Engine.
    Ensures a candidate model version MUST pass explicit ModelQualityGate thresholds
    before being set as the active production model version.
    Preserves previous active model state and maintains operational audit records.
    """

    def __init__(
        self,
        models_dir: Optional[Union[str, Path]] = None,
        output_dir: Optional[Union[str, Path]] = None,
        quality_gate: Optional[ModelQualityGate] = None,
    ):
        self.version_manager = ModelVersionManager(models_dir)
        self.quality_gate = quality_gate if quality_gate is not None else ModelQualityGate()

        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = get_evaluation_reports_dir()

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.promotion_audit_file = self.output_dir / "promotions.json"

    def promote_model(
        self,
        version: str,
        evaluation_result: Optional[Union[Dict[str, Any], str, Path]] = None,
        force: bool = False,
    ) -> Dict[str, Any]:
        """
        Promotes candidate model version to active status if it passes the Quality Gate.
        Returns structured promotion result dictionary.
        """
        previous_active = self.version_manager.get_active_version()

        # 1. Verify candidate model directory & artifacts exist
        v_dir = self.version_manager.get_version_dir(version)
        if not v_dir.exists():
            raise FileNotFoundError(f"Model version directory '{version}' not found at {v_dir}")

        # 2. Resolve evaluation result if not explicitly passed
        if evaluation_result is None:
            eval_artifact = self.output_dir / f"{version}_evaluation.json"
            if eval_artifact.exists():
                evaluation_result = eval_artifact
            else:
                # Run evaluator dynamically if artifact does not exist
                evaluator = ModelEvaluator(version=version, models_dir=self.version_manager.models_dir, output_dir=self.output_dir)
                evaluation_result = evaluator.evaluate()

        # 3. Validate against Quality Gate
        gate_res = self.quality_gate.validate(evaluation_result, model_version=version)

        # 4. Check if promotion is allowed
        if not gate_res["passed"] and not force:
            result = {
                "status": "BLOCKED",
                "reason": "QUALITY_GATE_FAILED",
                "candidate_version": version,
                "previous_active_version": previous_active,
                "failed_checks": gate_res["failed_checks"],
                "quality_gate": gate_res,
            }
            self._log_audit_event(result)
            return result

        # 5. Execute Atomic Promotion
        promoted_version = self.version_manager.set_active_version(version)

        result = {
            "status": "PROMOTED",
            "candidate_version": promoted_version,
            "previous_active_version": previous_active,
            "promoted_at": datetime.now(timezone.utc).isoformat(),
            "forced": force,
            "metrics": gate_res.get("metrics", {}),
            "quality_gate": gate_res,
        }

        self._log_audit_event(result)
        return result

    def rollback_promotion(self, target_version: Optional[str] = None) -> Dict[str, Any]:
        """
        Rolls back active model version to previous active model or explicit target version.
        """
        current_active = self.version_manager.get_active_version()

        if target_version is None:
            # Check audit history for previous active
            audit_history = self._get_audit_history()
            promotions = [e for e in audit_history if e.get("status") == "PROMOTED"]
            if promotions:
                last_promo = promotions[-1]
                target_version = last_promo.get("previous_active_version")

        if not target_version:
            raise ValueError("No target rollback version specified or found in promotion history.")

        rolled_back = self.version_manager.rollback(target_version)

        result = {
            "status": "ROLLED_BACK",
            "active_version": rolled_back,
            "previous_version": current_active,
            "rolled_back_at": datetime.now(timezone.utc).isoformat(),
        }

        self._log_audit_event(result)
        return result

    def _get_audit_history(self) -> List[Dict[str, Any]]:
        if self.promotion_audit_file.exists():
            try:
                with open(self.promotion_audit_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("promotions", [])
            except Exception:
                pass
        return []

    def _log_audit_event(self, event: Dict[str, Any]) -> None:
        history = self._get_audit_history()
        history.append(event)
        audit_data = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "total_events": len(history),
            "promotions": history,
        }
        atomic_json_write(self.promotion_audit_file, audit_data)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Dravya AI Engine - Model Quality Gate & Safe Promotion"
    )
    parser.add_argument(
        "--version",
        type=str,
        default="v1-smoke",
        help="Candidate model version tag to promote (default: v1-smoke)",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        help="Execution device for evaluation (default: cpu)",
    )
    parser.add_argument(
        "--models-dir",
        type=str,
        default=None,
        help="Directory containing model checkpoints",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory for evaluation/promotion artifacts",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Bypass quality gate and force promotion (not recommended)",
    )

    args = parser.parse_args()

    print("==========================================================================")
    print("      DRAVYA AI ENGINE - MODEL QUALITY GATE & SAFE PROMOTION              ")
    print("==========================================================================")

    service = ModelPromotionService(
        models_dir=args.models_dir,
        output_dir=args.output_dir,
    )

    print(f"Candidate Version:       {args.version}")
    print(f"Previous Active Version: {service.version_manager.get_active_version()}")
    print("Running Model Quality Gate validation...")

    res = service.promote_model(version=args.version, force=args.force)
    gate_res = res.get("quality_gate", {})
    checks = gate_res.get("checks", {})

    print("\n--------------------------------------------------------------------------")
    print("                      QUALITY GATE CHECKS SUMMARY                         ")
    print("--------------------------------------------------------------------------")
    for check_name, status in checks.items():
        symbol = "[PASS]" if status else "[FAIL]"
        print(f"  {symbol} {check_name:<30}")

    print("--------------------------------------------------------------------------")
    print(f"PROMOTION STATUS:       {res['status']}")
    print(f"NEW ACTIVE VERSION:     {service.version_manager.get_active_version()}")

    if res["status"] == "BLOCKED":
        print(f"FAILED CHECKS:          {res.get('failed_checks')}")
        print("==========================================================================")
        sys.exit(1)
    else:
        print("==========================================================================")


if __name__ == "__main__":
    main()
