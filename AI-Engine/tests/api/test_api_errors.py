import pytest


def test_predict_corrupted_image_returns_400(client):
    # Fake PNG header but corrupted body bytes
    corrupted_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDRcorrupted_garbage_bytes"
    response = client.post(
        "/predict",
        files={"file": ("corrupted.png", corrupted_bytes, "image/png")},
    )

    assert response.status_code == 400
    data = response.json()
    assert "Invalid or corrupted image" in str(data) or "corrupted" in str(data).lower()
    # Ensure no raw tracebacks or filesystem paths are leaked
    assert "Traceback" not in str(data)
    assert "C:\\" not in str(data)


def test_predict_model_unavailable_returns_503(client, mock_active_model_setup):
    models_dir, _ = mock_active_model_setup
    active_pointer = models_dir / "active_model.json"
    if active_pointer.exists():
        active_pointer.unlink()

    from src.api.dependencies import get_predictor_manager
    get_predictor_manager().clear_cache()

    dummy_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
    response = client.post(
        "/predict",
        files={"file": ("test.png", dummy_png, "image/png")},
    )

    assert response.status_code == 503
    data = response.json()
    assert "Model unavailable" in str(data)
    assert "Traceback" not in str(data)
