"""
Tests for deterministic Batch ID generation in Dravya AI Engine.
"""
import pytest
from src.batch.batch_id import (
    extract_herb_prefix,
    format_harvest_date_digits,
    generate_batch_id,
)


def test_extract_herb_prefix():
    assert extract_herb_prefix("Ashwagandha") == "ASH"
    assert extract_herb_prefix("Tulsi") == "TUL"
    assert extract_herb_prefix("Aloe Vera") == "ALO"
    assert extract_herb_prefix("Neem") == "NEE"
    assert extract_herb_prefix("A") == "AXX"
    assert extract_herb_prefix("   ") == "HRB"


def test_format_harvest_date_digits():
    assert format_harvest_date_digits("2026-08-10") == "20260810"
    assert format_harvest_date_digits("2026/08/10") == "20260810"
    assert format_harvest_date_digits("20260810") == "20260810"

    with pytest.raises(ValueError):
        format_harvest_date_digits("invalid-date")


def test_generate_batch_id_determinism():
    id1 = generate_batch_id(
        herb_species="Ashwagandha",
        farmer_id="FARMER-001",
        harvest_date="2026-08-10",
        quantity_kg=500.0,
    )
    id2 = generate_batch_id(
        herb_species="Ashwagandha",
        farmer_id="FARMER-001",
        harvest_date="2026-08-10",
        quantity_kg=500.0,
    )
    assert id1 == id2
    assert id1.startswith("DRAVYA-ASH-20260810-")


def test_generate_batch_id_collision_resistance():
    id_farmer_a = generate_batch_id(
        herb_species="Ashwagandha",
        farmer_id="FARMER-001",
        harvest_date="2026-08-10",
        quantity_kg=500.0,
    )
    id_farmer_b = generate_batch_id(
        herb_species="Ashwagandha",
        farmer_id="FARMER-002",
        harvest_date="2026-08-10",
        quantity_kg=500.0,
    )
    id_different_qty = generate_batch_id(
        herb_species="Ashwagandha",
        farmer_id="FARMER-001",
        harvest_date="2026-08-10",
        quantity_kg=300.0,
    )

    assert id_farmer_a != id_farmer_b
    assert id_farmer_a != id_different_qty


def test_generate_batch_id_no_pii():
    farmer_pii_id = "FARMER-998877665544"
    batch_id = generate_batch_id(
        herb_species="Tulsi",
        farmer_id=farmer_pii_id,
        harvest_date="2026-08-10",
        quantity_kg=200.0,
    )
    assert "998877665544" not in batch_id
    assert batch_id.startswith("DRAVYA-TUL-20260810-")
