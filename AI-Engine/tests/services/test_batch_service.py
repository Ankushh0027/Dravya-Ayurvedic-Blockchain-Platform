"""
Tests for BatchService orchestration combining PlantPredictor and BatchManager.
"""
from unittest.mock import MagicMock

import pytest
from PIL import Image

from src.batch import BatchManager, VerificationStatus
from src.services.batch_service import BatchService


def test_batch_service_create_from_image():
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

    manager = BatchManager()
    manager.clear()

    service = BatchService(predictor=mock_predictor, batch_manager=manager)

    # Create dummy image
    img = Image.new("RGB", (224, 224), color="green")

    batch, payload = service.create_batch_from_image(
        image_input=img,
        farmer_id="FARMER-88",
        quantity=500.0,
        quantity_unit="kg",
        harvest_date="2026-08-10",
        farmer_name="Sita Devi",
    )

    assert batch.batch_id.startswith("DRAVYA-ASH-20260810-")
    assert batch.herb_species == "Ashwagandha"
    assert batch.canonical_species == "Withania somnifera"
    assert batch.quantity == 500.0
    assert batch.verification_status == VerificationStatus.AI_CONFIRMED

    assert payload.batch_id == batch.batch_id
    assert payload.origin["farmer_id"] == "FARMER-88"
    assert payload.ai_verification["confidence"] == 0.986
