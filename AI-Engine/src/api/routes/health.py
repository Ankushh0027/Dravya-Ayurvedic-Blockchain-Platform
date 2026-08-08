from fastapi import APIRouter
from src.api.dependencies import get_predictor_manager
from src.api.schemas import HealthResponse
from src.data.paths import load_config

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health_check():
    """
    Lightweight health check endpoint for Dravya AI Engine.
    Returns service health status and active model resolution without triggering model inference.
    """
    config = load_config()
    service_name = config.get("api", {}).get("service_name", "dravya-ai-engine")

    manager = get_predictor_manager()
    status_str, model_version, is_loaded = manager.get_health_status()

    return HealthResponse(
        status=status_str,
        service=service_name,
        model_version=model_version,
        model_loaded=is_loaded,
    )
