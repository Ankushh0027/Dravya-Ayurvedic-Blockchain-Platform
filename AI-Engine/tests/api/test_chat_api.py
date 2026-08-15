"""
FastAPI E2E Tests for Dravya AI Assistant POST /chat endpoint.
"""
import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.api.dependencies import get_batch_manager_dependency
from src.batch import BatchCreate, BatchManager

app = create_app()
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_batches():
    manager = get_batch_manager_dependency()
    manager.clear()

    # Create test batches
    b1 = manager.create_batch(
        BatchCreate(
            herb_species="Ashwagandha",
            farmer_id="F001",
            farmer_name="Ramesh Kumar",
            quantity=150.0,
            quantity_unit="kg",
            harvest_date="2026-08-10",
        ),
        nonce="CHATTEST1",
    )
    b2 = manager.create_batch(
        BatchCreate(
            herb_species="Tulsi",
            farmer_id="F002",
            farmer_name="Suresh Singh",
            quantity=75.0,
            quantity_unit="kg",
            harvest_date="2026-08-11",
        ),
        nonce="CHATTEST2",
    )
    yield b1.batch_id, b2.batch_id
    manager.clear()


def test_post_chat_english_herb_quantity():
    response = client.post(
        "/chat",
        json={"message": "How much Ashwagandha do we have?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["intent"] == "herb_summary"
    assert data["tool_used"] == "get_herb_summary"
    assert data["data"]["total_quantity"] == 150.0


def test_post_chat_hinglish_herb_quantity():
    response = client.post(
        "/chat",
        json={"message": "Ashwagandha ki total quantity kitni hai?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "herb_summary"
    assert data["tool_used"] == "get_herb_summary"
    assert "150.00 kg" in data["answer"] or "150" in data["answer"]


def test_post_chat_farmer_inventory():
    response = client.post(
        "/chat",
        json={"message": "F001 ke paas kya hai?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] in ["farmer_batches", "farmer_summary"]
    assert "F001" in data["answer"]


def test_post_chat_batch_details(setup_test_batches):
    b1_id, _ = setup_test_batches
    response = client.post(
        "/chat",
        json={"message": f"Give me details of batch {b1_id}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "batch"
    assert data["tool_used"] == "get_batch"
    assert data["data"]["batch_id"] == b1_id
    assert data["data"]["herb_species"] == "Ashwagandha"


def test_post_chat_batch_traceability(setup_test_batches):
    b1_id, _ = setup_test_batches
    response = client.post(
        "/chat",
        json={"message": f"Show me the traceability information for batch {b1_id}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "batch_traceability"
    assert data["tool_used"] == "get_batch_traceability"
    assert "payload_hash" in data["data"]


def test_post_chat_total_inventory():
    response = client.post(
        "/chat",
        json={"message": "System me total kitni herbs hain?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "inventory_summary"
    assert data["tool_used"] == "get_inventory_summary"
    assert data["data"]["total_batches"] == 2
    assert data["data"]["total_quantity_kg"] == 225.0


def test_post_chat_unknown_batch():
    response = client.post(
        "/chat",
        json={"message": "Give me details of batch DOES-NOT-EXIST"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] in ["batch", "conversational"]
    if data["data"] and "found" in data["data"]:
        assert data["data"]["found"] is False
    assert "nahi" in data["answer"].lower() or "not found" in data["answer"].lower() or "assistant" in data["answer"].lower()


def test_post_chat_empty_message_validation():
    response = client.post(
        "/chat",
        json={"message": "   "},
    )
    assert response.status_code == 422 or response.status_code == 400
