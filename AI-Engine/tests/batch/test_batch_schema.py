"""
Tests for Pydantic batch domain schemas in Dravya AI Engine.
"""
import pytest
from src.batch.batch_schema import (
    AIPredictionDetails,
    Batch,
    BatchCreate,
    VerificationStatus,
)


def test_batch_create_validation():
    bc = BatchCreate(
        herb_species="Ashwagandha",
        farmer_id="FARMER-100",
        quantity=500.0,
        quantity_unit="kg",
        harvest_date="2026-08-10",
    )
    assert bc.herb_species == "Ashwagandha"
    assert bc.farmer_id == "FARMER-100"
    assert bc.quantity == 500.0
    assert bc.quantity_unit == "kg"


def test_batch_domain_model():
    ai = AIPredictionDetails(
        predicted_class="Ashwagandha",
        canonical_species="Withania somnifera",
        scientific_name="Withania somnifera",
        confidence=0.986,
        model_version="v1-kaggle",
        class_id="DRAVYA_0001",
    )
    batch = Batch(
        batch_id="DRAVYA-ASH-20260810-A1B2C3",
        herb_species="Ashwagandha",
        canonical_species="Withania somnifera",
        scientific_name="Withania somnifera",
        farmer_id="FARMER-100",
        quantity=500.0,
        quantity_unit="kg",
        original_quantity=500.0,
        original_unit="kg",
        harvest_date="2026-08-10",
        creation_timestamp="2026-08-12T13:08:00Z",
        source="AI_CAMERA",
        ai_prediction=ai,
        verification_status=VerificationStatus.AI_CONFIRMED,
        metadata={},
    )

    assert batch.batch_id == "DRAVYA-ASH-20260810-A1B2C3"
    assert batch.ai_prediction.confidence == 0.986
    assert batch.verification_status == VerificationStatus.AI_CONFIRMED
