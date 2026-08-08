import pytest


def test_predict_endpoint_success(client, synthetic_png_bytes):
    response = client.post(
        "/predict",
        files={"file": ("test_plant.png", synthetic_png_bytes, "image/png")},
    )

    assert response.status_code == 200

    data = response.json()
    assert "model_version" in data
    assert "predicted_class" in data
    assert "confidence" in data
    assert "top_k" in data

    assert data["model_version"] == "v1-api-test"
    assert data["predicted_class"] in ["Saraca asoca", "Clerodendrum splendens"]
    assert 0.0 <= data["confidence"] <= 1.0
    assert len(data["top_k"]) == 2

    # Top-k items schema
    top1 = data["top_k"][0]
    top2 = data["top_k"][1]
    assert "class_name" in top1
    assert "confidence" in top1
    assert top1["confidence"] >= top2["confidence"]


def test_predict_endpoint_success_with_image_field_name(client, synthetic_png_bytes):
    response = client.post(
        "/predict",
        files={"image": ("test_plant.png", synthetic_png_bytes, "image/png")},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["model_version"] == "v1-api-test"
    assert data["predicted_class"] in ["Saraca asoca", "Clerodendrum splendens"]
    assert len(data["top_k"]) == 2

