"""
Tests for batch aggregation, herb-wise, farmer-wise, and total inventory metrics.
"""
from src.batch import Batch, VerificationStatus
from src.batch.batch_aggregator import BatchAggregator


def create_sample_batches():
    b1 = Batch(
        batch_id="DRAVYA-ASH-20260810-AAAAAA",
        herb_species="Ashwagandha",
        canonical_species="Withania somnifera",
        farmer_id="FARMER-A",
        farmer_name="Farmer Alice",
        quantity=500.0,
        quantity_unit="kg",
        original_quantity=500.0,
        original_unit="kg",
        harvest_date="2026-08-10",
        creation_timestamp="2026-08-12T10:00:00Z",
        source="AI_CAMERA",
        verification_status=VerificationStatus.AI_CONFIRMED,
    )
    b2 = Batch(
        batch_id="DRAVYA-ASH-20260810-BBBBBB",
        herb_species="Ashwagandha",
        canonical_species="Withania somnifera",
        farmer_id="FARMER-B",
        farmer_name="Farmer Bob",
        quantity=300.0,
        quantity_unit="kg",
        original_quantity=300.0,
        original_unit="kg",
        harvest_date="2026-08-10",
        creation_timestamp="2026-08-12T10:05:00Z",
        source="AI_CAMERA",
        verification_status=VerificationStatus.AI_CONFIRMED,
    )
    b3 = Batch(
        batch_id="DRAVYA-TUL-20260810-CCCCCC",
        herb_species="Tulsi",
        canonical_species="Ocimum sanctum",
        farmer_id="FARMER-A",
        farmer_name="Farmer Alice",
        quantity=200.0,
        quantity_unit="kg",
        original_quantity=200.0,
        original_unit="kg",
        harvest_date="2026-08-10",
        creation_timestamp="2026-08-12T10:10:00Z",
        source="AI_CAMERA",
        verification_status=VerificationStatus.REVIEW_REQUIRED,
    )
    return [b1, b2, b3]


def test_herb_summary_aggregation():
    batches = create_sample_batches()

    summary_ash = BatchAggregator.get_herb_summary("Ashwagandha", batches)
    assert summary_ash.herb == "Ashwagandha"
    assert summary_ash.canonical_species == "Withania somnifera"
    assert summary_ash.total_batches == 2
    assert summary_ash.total_quantity == 800.0
    assert summary_ash.farmers_count == 2
    assert summary_ash.farmers == ["FARMER-A", "FARMER-B"]

    summary_tulsi = BatchAggregator.get_herb_summary("Tulsi", batches)
    assert summary_tulsi.total_batches == 1
    assert summary_tulsi.total_quantity == 200.0
    assert summary_tulsi.farmers == ["FARMER-A"]


def test_farmer_summary_aggregation():
    batches = create_sample_batches()

    farmer_a = BatchAggregator.get_farmer_summary("FARMER-A", batches)
    assert farmer_a.farmer_id == "FARMER-A"
    assert farmer_a.farmer_name == "Farmer Alice"
    assert farmer_a.total_batches == 2
    assert farmer_a.total_quantity == 700.0
    assert "Withania somnifera" in farmer_a.herbs_supplied or "Ashwagandha" in farmer_a.herbs_supplied
    assert "Ocimum sanctum" in farmer_a.herbs_supplied or "Tulsi" in farmer_a.herbs_supplied


def test_inventory_summary_aggregation():
    batches = create_sample_batches()

    inventory = BatchAggregator.get_inventory_summary(batches)
    assert inventory.total_batches == 3
    assert inventory.total_quantity_kg == 1000.0
    assert inventory.unique_herbs_count == 2
    assert inventory.unique_farmers_count == 2
