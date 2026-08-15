"""
Quantity validation, unit conversion, and confidence threshold evaluation for batches.
"""
from typing import Dict, Tuple, Any, Optional
from src.batch.batch_schema import VerificationStatus
from src.batch.exceptions import InvalidQuantityError, InvalidBatchError
from src.batch.batch_id import format_harvest_date_digits

# Supported unit conversion factors to canonical kilogram (kg)
UNIT_CONVERSION_MAP: Dict[str, float] = {
    "kg": 1.0,
    "kilogram": 1.0,
    "kilograms": 1.0,
    "g": 0.001,
    "gram": 0.001,
    "grams": 0.001,
    "mg": 0.000001,
    "milligram": 0.000001,
    "milligrams": 0.000001,
    "quintal": 100.0,
    "quintals": 100.0,
    "q": 100.0,
    "tonne": 1000.0,
    "tonnes": 1000.0,
    "ton": 1000.0,
    "tons": 1000.0,
    "t": 1000.0,
    "lb": 0.45359237,
    "lbs": 0.45359237,
    "pound": 0.45359237,
    "pounds": 0.45359237,
}


def normalize_quantity(value: float, unit: str) -> Tuple[float, str]:
    """
    Validates quantity value (> 0) and unit of measurement, returning normalized quantity in kg.

    Returns:
    --------
    Tuple[normalized_quantity_kg, canonical_unit]
    """
    if value is None or value <= 0:
        raise InvalidQuantityError(f"Quantity must be greater than zero. Got: {value}")

    unit_clean = (unit or "").strip().lower()
    if unit_clean not in UNIT_CONVERSION_MAP:
        supported = sorted(list(set(UNIT_CONVERSION_MAP.keys())))
        raise InvalidQuantityError(
            f"Unsupported quantity unit '{unit}'. Supported units: {supported}"
        )

    factor = UNIT_CONVERSION_MAP[unit_clean]
    normalized_kg = round(float(value) * factor, 6)
    return normalized_kg, "kg"


def validate_batch_input(
    herb_species: str,
    farmer_id: str,
    quantity: float,
    quantity_unit: str,
    harvest_date: str,
) -> None:
    """
    Validates batch input parameters before processing or creation.
    """
    if not herb_species or not herb_species.strip():
        raise InvalidBatchError("Herb species name must be a non-empty string.")

    if not farmer_id or not farmer_id.strip():
        raise InvalidBatchError("Farmer ID must be a non-empty string.")

    normalize_quantity(quantity, quantity_unit)

    try:
        format_harvest_date_digits(harvest_date)
    except ValueError as e:
        raise InvalidBatchError(str(e))


def evaluate_verification_status(
    confidence: float,
    confirmed_threshold: float = 0.90,
    review_threshold: float = 0.70,
) -> VerificationStatus:
    """
    Evaluates AI prediction confidence score against configurable thresholds.
    """
    if confidence >= confirmed_threshold:
        return VerificationStatus.AI_CONFIRMED
    elif confidence >= review_threshold:
        return VerificationStatus.REVIEW_REQUIRED
    else:
        return VerificationStatus.LOW_CONFIDENCE
