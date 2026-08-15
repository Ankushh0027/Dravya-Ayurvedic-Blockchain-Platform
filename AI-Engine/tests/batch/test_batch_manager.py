"""
Tests for BatchManager repository operations and traceability payload generation.
"""
import pytest
from src.batch import (
    AIPredictionDetails,
    BatchCreate,
    BatchManager,
    BatchNotFoundError,
    DuplicateBatchError,
    VerificationStatus,
)


def test_batch_manager_create_and_get():
    manager = BatchManager()
    manager.clear()

    bc = BatchCreate(
        herb_species="Ashwagandha",
        farmer_id="FARMER-101",
        quantity=500.0,
        quantity_unit="kg",
        harvest_date="2026-08-10",
        farmer_name="Ramesh Kumar",
    )

    batch = manager.create_batch(bc, canonical_species="Withania somnifera")
    assert batch.batch_id.startswith("DRAVYA-ASH-20260810-")
    assert batch.herb_species == "Ashwagandha"
    assert batch.canonical_species == "Withania somnifera"
    assert batch.quantity == 500.0

    retrieved = manager.get_batch(batch.batch_id)
    assert retrieved.batch_id == batch.batch_id
    assert retrieved.farmer_name == "Ramesh Kumar"


def test_batch_manager_not_found():
    manager = BatchManager()
    manager.clear()

    with pytest.raises(BatchNotFoundError):
        manager.get_batch("NONEXISTENT-BATCH-ID")


def test_batch_manager_list_and_filter():
    manager = BatchManager()
    manager.clear()

    manager.create_batch(
        BatchCreate(
            herb_species="Ashwagandha",
            farmer_id="FARMER-101",
            quantity=500.0,
            quantity_unit="kg",
            harvest_date="2026-08-10",
        ),
        canonical_species="Withania somnifera",
    )

    manager.create_batch(
        BatchCreate(
            herb_species="Tulsi",
            farmer_id="FARMER-102",
            quantity=200.0,
            quantity_unit="kg",
            harvest_date="2026-08-10",
        ),
        canonical_species="Ocimum sanctum",
    )

    ash_list = manager.list_batches(herb_species="Ashwagandha")
    assert len(ash_list) == 1
    assert ash_list[0].herb_species == "Ashwagandha"

    farmer_102_list = manager.list_batches(farmer_id="FARMER-102")
    assert len(farmer_102_list) == 1
    assert farmer_102_list[0].herb_species == "Tulsi"


def test_build_traceability_payload():
    manager = BatchManager()
    manager.clear()

    ai = AIPredictionDetails(
        predicted_class="Ashwagandha",
        canonical_species="Withania somnifera",
        scientific_name="Withania somnifera",
        confidence=0.986,
        model_version="v1-kaggle",
        class_id="DRAVYA_0001",
    )

    batch = manager.create_batch(
        BatchCreate(
            herb_species="Ashwagandha",
            farmer_id="FARMER-101",
            quantity=500.0,
            quantity_unit="kg",
            harvest_date="2026-08-10",
        ),
        canonical_species="Withania somnifera",
        scientific_name="Withania somnifera",
        ai_prediction=ai,
        verification_status=VerificationStatus.AI_CONFIRMED,
    )

    payload = manager.build_traceability_payload(batch.batch_id)

    assert payload.batch_id == batch.batch_id
    assert payload.herb["common_name"] == "Ashwagandha"
    assert payload.herb["canonical_species"] == "Withania somnifera"
    assert payload.origin["farmer_id"] == "FARMER-101"
    assert payload.quantity["value"] == 500.0
    assert payload.quantity["unit"] == "kg"
    assert payload.ai_verification["confidence"] == 0.986
    assert payload.verification_status == "AI_CONFIRMED"
    assert len(payload.payload_hash) == 64  # SHA-256 hex string length
