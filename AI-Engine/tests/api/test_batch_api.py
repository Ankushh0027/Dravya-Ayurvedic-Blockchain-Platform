"""
Integration tests for FastAPI Batch & Inventory endpoints.
"""
import io
from PIL import Image
import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.api.dependencies import get_batch_manager_dependency
from src.batch import BatchManager

app = create_app()
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_batch_manager():
    manager = get_batch_manager_dependency()
    manager.clear()
    yield
    manager.clear()


def create_dummy_jpeg_bytes():
    buf = io.BytesIO()
    img = Image.new("RGB", (64, 64), color="green")
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_post_batches_create_api():
    payload = {
        "herb_species": "Ashwagandha",
        "farmer_id": "FARMER-API-1",
        "quantity": 500.0,
        "quantity_unit": "kg",
        "harvest_date": "2026-08-10",
        "farmer_name": "API Farmer",
    }
    response = client.post("/batches/create", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "batch_id" in data
    assert data["herb_species"] == "Ashwagandha"
    assert data["farmer_id"] == "FARMER-API-1"


def test_get_batch_by_id_and_traceability_api():
    # First create a batch
    create_res = client.post(
        "/batches/create",
        json={
            "herb_species": "Tulsi",
            "farmer_id": "FARMER-API-2",
            "quantity": 200.0,
            "quantity_unit": "kg",
            "harvest_date": "2026-08-10",
        },
    )
    assert create_res.status_code == 201
    batch_id = create_res.json()["batch_id"]

    # Get batch by ID
    get_res = client.get(f"/batches/{batch_id}")
    assert get_res.status_code == 200
    assert get_res.json()["batch_id"] == batch_id

    # Get traceability payload
    trace_res = client.get(f"/batches/{batch_id}/traceability")
    assert trace_res.status_code == 200
    trace_data = trace_res.json()
    assert trace_data["batch_id"] == batch_id
    assert "payload_hash" in trace_data


def test_get_batch_not_found_api():
    response = client.get("/batches/NONEXISTENT-ID")
    assert response.status_code == 404


def test_get_batch_summaries_and_inventory_api():
    client.post(
        "/batches/create",
        json={
            "herb_species": "Ashwagandha",
            "farmer_id": "FARMER-1",
            "quantity": 500.0,
            "quantity_unit": "kg",
            "harvest_date": "2026-08-10",
        },
    )
    client.post(
        "/batches/create",
        json={
            "herb_species": "Ashwagandha",
            "farmer_id": "FARMER-2",
            "quantity": 300.0,
            "quantity_unit": "kg",
            "harvest_date": "2026-08-10",
        },
    )

    # Herb summary
    h_res = client.get("/batches/summary/herb/Ashwagandha")
    assert h_res.status_code == 200
    h_data = h_res.json()
    assert h_data["total_batches"] == 2
    assert h_data["total_quantity"] == 800.0

    # Farmer summary
    f_res = client.get("/batches/summary/farmer/FARMER-1")
    assert f_res.status_code == 200
    f_data = f_res.json()
    assert f_data["total_batches"] == 1
    assert f_data["total_quantity"] == 500.0

    # Overall Inventory
    inv_res = client.get("/inventory/summary")
    assert inv_res.status_code == 200
    inv_data = inv_res.json()
    assert inv_data["total_batches"] == 2
    assert inv_data["total_quantity_kg"] == 800.0


def test_post_batches_create_from_image_api(monkeypatch):
    from src.api.dependencies import get_predictor_manager, PredictorDependencyManager
    from unittest.mock import MagicMock

    mock_predictor = MagicMock()
    mock_predictor.version = "v1-kaggle"
    mock_predictor.predict.return_value = {
        "class_id": "DRAVYA_0001",
        "species_name": "Ashwagandha",
        "canonical_name": "Withania somnifera",
        "scientific_name": "Withania somnifera",
        "confidence": 0.986,
        "model_version": "v1-kaggle",
    }

    # Patch predictor manager to return mock predictor
    mgr = get_predictor_manager()
    monkeypatch.setattr(mgr, "get_predictor", lambda force_reload=False: mock_predictor)

    img_bytes = create_dummy_jpeg_bytes()

    files = {"file": ("test.jpg", img_bytes, "image/jpeg")}
    data = {
        "farmer_id": "FARMER-IMG-1",
        "quantity": "500.0",
        "quantity_unit": "kg",
        "harvest_date": "2026-08-10",
        "farmer_name": "Image Farmer",
    }

    response = client.post("/batches/create-from-image", files=files, data=data)
    assert response.status_code == 201
    res_json = response.json()
    assert "batch" in res_json
    assert "traceability_payload" in res_json
    assert res_json["batch"]["herb_species"] == "Ashwagandha"
    assert res_json["batch"]["canonical_species"] == "Withania somnifera"
    assert res_json["batch"]["verification_status"] == "AI_CONFIRMED"
