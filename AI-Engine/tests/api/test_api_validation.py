import pytest


def test_predict_unsupported_file_type(client):
    response = client.post(
        "/predict",
        files={"file": ("document.txt", b"Hello text file content", "text/plain")},
    )

    assert response.status_code == 400
    data = response.json()
    assert "error" in data or "detail" in data
    assert "Unsupported file type" in str(data)


def test_predict_empty_file_upload(client):
    response = client.post(
        "/predict",
        files={"file": ("empty_image.png", b"", "image/png")},
    )

    assert response.status_code == 400
    data = response.json()
    assert "empty" in str(data).lower()


def test_predict_file_exceeds_max_size(client, monkeypatch):
    # Set max upload size to 10 bytes for test
    from src.api.routes import prediction
    monkeypatch.setattr(prediction, "_get_api_config", lambda: (prediction.DEFAULT_ALLOWED_CONTENT_TYPES, 10))

    response = client.post(
        "/predict",
        files={"file": ("large_image.png", b"01234567890123456789", "image/png")},
    )

    assert response.status_code == 413
    data = response.json()
    assert "exceeds" in str(data).lower()
