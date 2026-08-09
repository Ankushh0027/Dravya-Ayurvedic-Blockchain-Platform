from pathlib import Path
from typing import Dict, Any, Optional, Tuple, Union
from fastapi import HTTPException, status

from src.data.paths import load_config, get_project_root
from src.inference.predictor import PlantPredictor
from src.models.version_manager import ModelVersionManager


class PredictorDependencyManager:
    """
    Application-level Dependency & Lifecycle Manager for PlantPredictor.
    Prevents expensive model weight reloading on every HTTP request by caching
    the active PlantPredictor singleton while automatically invalidating cache
    if the promoted active model version changes.
    """

    def __init__(self):
        self._cached_predictor: Optional[PlantPredictor] = None
        self._cached_version: Optional[str] = None
        self._custom_models_dir: Optional[Path] = None

    def set_models_dir(self, models_dir: Optional[Union[str, Path]]) -> None:
        if models_dir:
            self._custom_models_dir = Path(models_dir)

    def get_version_manager(self) -> ModelVersionManager:
        return ModelVersionManager(models_dir=self._custom_models_dir)

    def get_active_version_id(self) -> Optional[str]:
        vm = self.get_version_manager()
        return vm.get_active_version()

    def get_predictor(self, force_reload: bool = False) -> Optional[PlantPredictor]:
        active_version = self.get_active_version_id()
        if not active_version:
            return None

        # Check if version directory & checkpoint exist
        vm = self.get_version_manager()
        v_dir = vm.get_version_dir(active_version)

        if not v_dir.exists():
            return None

        chk = v_dir / "best_model.pth"
        if not chk.exists():
            chk = v_dir / "latest_checkpoint.pth"
        if not chk.exists():
            return None

        # Cache hit check
        if (
            not force_reload
            and self._cached_predictor is not None
            and self._cached_version == active_version
        ):
            return self._cached_predictor

        # Load predictor instance
        try:
            predictor = PlantPredictor(
                version=active_version,
                checkpoint_name=chk.name,
                device="cpu",
                models_dir=self._custom_models_dir,
            )
            self._cached_predictor = predictor
            self._cached_version = active_version
            return predictor
        except Exception as e:
            import logging
            logging.exception(f"Failed to load PlantPredictor for version '{active_version}': {e}")
            return None

    def get_health_status(self) -> Tuple[str, Optional[str], bool]:
        """
        Lightweight health status check.
        Checks active model resolution and checkpoint availability without running inference.
        """
        active_version = self.get_active_version_id()
        if not active_version:
            return "degraded", None, False

        vm = self.get_version_manager()
        v_dir = vm.get_version_dir(active_version)

        if not v_dir.exists():
            return "degraded", active_version, False

        chk = v_dir / "best_model.pth"
        if not chk.exists():
            chk = v_dir / "latest_checkpoint.pth"

        if not chk.exists():
            return "degraded", active_version, False

        return "healthy", active_version, True

    def clear_cache(self) -> None:
        self._cached_predictor = None
        self._cached_version = None


# Global singleton manager instance
_predictor_manager = PredictorDependencyManager()


def get_predictor_manager() -> PredictorDependencyManager:
    return _predictor_manager


def get_predictor_dependency() -> PlantPredictor:
    """
    FastAPI dependency for injecting PlantPredictor into endpoints.
    Raises HTTP 503 if model predictor is unavailable.
    """
    manager = get_predictor_manager()
    predictor = manager.get_predictor()
    if predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model unavailable: No active model version promoted or checkpoint missing.",
        )
    return predictor
