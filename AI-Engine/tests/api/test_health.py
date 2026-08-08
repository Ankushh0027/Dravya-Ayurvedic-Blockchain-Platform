import pytest


def test_health_endpoint_success(client):
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "dravya-ai-engine"
    assert data["model_version"] == "v1-api-test"
    assert data["model_loaded"] is True


def test_health_endpoint_degraded_when_no_active_model(client, mock_active_model_setup):
    models_dir, _ = mock_active_model_setup
    active_pointer = models_dir / "active_model.json"
    if active_pointer.exists():
        active_pointer.unlink()

    from src.api.dependencies import get_predictor_manager
    get_predictor_manager().clear_cache()

    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "degraded"
    assert data["service"] == "dravya-ai-engine"
    assert data["model_version"] is None
    assert data["model_loaded"] is False
