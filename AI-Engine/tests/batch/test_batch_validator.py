"""
Tests for batch validation, unit conversion, and threshold evaluation.
"""
import pytest
from src.batch.batch_schema import VerificationStatus
from src.batch.batch_validator import (
    evaluate_verification_status,
    normalize_quantity,
    validate_batch_input,
)
from src.batch.exceptions import InvalidBatchError, InvalidQuantityError


def test_normalize_quantity_valid():
    qty_kg, unit = normalize_quantity(500, "kg")
    assert qty_kg == 500.0
    assert unit == "kg"

    qty_g, unit = normalize_quantity(500000, "g")
    assert qty_g == 500.0

    qty_quintal, unit = normalize_quantity(5, "quintal")
    assert qty_quintal == 500.0

    qty_tonne, unit = normalize_quantity(0.5, "tonne")
    assert qty_tonne == 500.0


def test_normalize_quantity_invalid():
    with pytest.raises(InvalidQuantityError):
        normalize_quantity(-10, "kg")

    with pytest.raises(InvalidQuantityError):
        normalize_quantity(0, "kg")

    with pytest.raises(InvalidQuantityError):
        normalize_quantity(100, "unsupported_unit")


def test_validate_batch_input():
    # Valid input passes without error
    validate_batch_input(
        herb_species="Ashwagandha",
        farmer_id="FARMER-001",
        quantity=500.0,
        quantity_unit="kg",
        harvest_date="2026-08-10",
    )

    with pytest.raises(InvalidBatchError):
        validate_batch_input("", "FARMER-001", 500.0, "kg", "2026-08-10")

    with pytest.raises(InvalidBatchError):
        validate_batch_input("Ashwagandha", "", 500.0, "kg", "2026-08-10")

    with pytest.raises(InvalidBatchError):
        validate_batch_input("Ashwagandha", "FARMER-001", 500.0, "kg", "invalid-date")


def test_evaluate_verification_status():
    assert evaluate_verification_status(0.95, 0.90, 0.70) == VerificationStatus.AI_CONFIRMED
    assert evaluate_verification_status(0.90, 0.90, 0.70) == VerificationStatus.AI_CONFIRMED
    assert evaluate_verification_status(0.85, 0.90, 0.70) == VerificationStatus.REVIEW_REQUIRED
    assert evaluate_verification_status(0.70, 0.90, 0.70) == VerificationStatus.REVIEW_REQUIRED
    assert evaluate_verification_status(0.65, 0.90, 0.70) == VerificationStatus.LOW_CONFIDENCE
