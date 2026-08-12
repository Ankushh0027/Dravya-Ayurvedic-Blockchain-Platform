"""
Batch Aggregation Service for Dravya AI Engine.
Groups and summarizes batches by canonical herb species, farmer, and total inventory metrics.
"""
from typing import Dict, List, Optional
from src.batch.batch_schema import (
    Batch,
    FarmerSummary,
    HerbSummary,
    InventorySummary,
)


class BatchAggregator:
    """
    Aggregation engine for computing real-time inventory statistics across batches.
    """

    @staticmethod
    def get_herb_summary(herb_species: str, batches: List[Batch]) -> HerbSummary:
        """
        Computes summary metrics for a given herb species (matching common or canonical species name).
        """
        herb_clean = herb_species.strip().lower()
        matching_batches = [
            b for b in batches
            if b.herb_species.strip().lower() == herb_clean or b.canonical_species.strip().lower() == herb_clean
        ]

        if not matching_batches:
            return HerbSummary(
                herb=herb_species,
                canonical_species=herb_species,
                total_batches=0,
                total_quantity=0.0,
                quantity_unit="kg",
                farmers_count=0,
                farmers=[],
                verification_breakdown={},
            )

        canonical_species = matching_batches[0].canonical_species
        total_quantity = round(sum(b.quantity for b in matching_batches), 4)

        unique_farmers = sorted(list(set(b.farmer_id for b in matching_batches)))

        verification_counts: Dict[str, int] = {}
        for b in matching_batches:
            status_str = b.verification_status.value if hasattr(b.verification_status, "value") else str(b.verification_status)
            verification_counts[status_str] = verification_counts.get(status_str, 0) + 1

        return HerbSummary(
            herb=matching_batches[0].herb_species,
            canonical_species=canonical_species,
            total_batches=len(matching_batches),
            total_quantity=total_quantity,
            quantity_unit="kg",
            farmers_count=len(unique_farmers),
            farmers=unique_farmers,
            verification_breakdown=verification_counts,
        )

    @staticmethod
    def get_farmer_summary(farmer_id: str, batches: List[Batch]) -> FarmerSummary:
        """
        Computes summary metrics for a specific farmer identifier.
        """
        farmer_clean = farmer_id.strip()
        matching_batches = [b for b in batches if b.farmer_id.strip() == farmer_clean]

        if not matching_batches:
            return FarmerSummary(
                farmer_id=farmer_id,
                farmer_name=None,
                total_batches=0,
                total_quantity=0.0,
                quantity_unit="kg",
                herbs_supplied=[],
                batches_by_herb={},
            )

        farmer_name = next((b.farmer_name for b in matching_batches if b.farmer_name), None)
        total_quantity = round(sum(b.quantity for b in matching_batches), 4)

        batches_by_herb: Dict[str, List[str]] = {}
        for b in matching_batches:
            key = b.canonical_species or b.herb_species
            if key not in batches_by_herb:
                batches_by_herb[key] = []
            batches_by_herb[key].append(b.batch_id)

        herbs_supplied = sorted(list(batches_by_herb.keys()))

        return FarmerSummary(
            farmer_id=farmer_id,
            farmer_name=farmer_name,
            total_batches=len(matching_batches),
            total_quantity=total_quantity,
            quantity_unit="kg",
            herbs_supplied=herbs_supplied,
            batches_by_herb=batches_by_herb,
        )

    @staticmethod
    def get_inventory_summary(batches: List[Batch]) -> InventorySummary:
        """
        Computes overall system inventory summary across all batches.
        """
        total_batches = len(batches)
        total_quantity = round(sum(b.quantity for b in batches), 4)

        # Unique canonical herbs
        herbs_map: Dict[str, List[Batch]] = {}
        unique_farmers: set = set()
        verification_counts: Dict[str, int] = {}

        for b in batches:
            herb_key = b.canonical_species or b.herb_species
            if herb_key not in herbs_map:
                herbs_map[herb_key] = []
            herbs_map[herb_key].append(b)

            unique_farmers.add(b.farmer_id)

            status_str = b.verification_status.value if hasattr(b.verification_status, "value") else str(b.verification_status)
            verification_counts[status_str] = verification_counts.get(status_str, 0) + 1

        herb_summaries = [
            BatchAggregator.get_herb_summary(herb_key, herb_batches)
            for herb_key, herb_batches in herbs_map.items()
        ]
        # Sort herb summaries by total quantity descending
        herb_summaries.sort(key=lambda s: s.total_quantity, reverse=True)

        return InventorySummary(
            total_batches=total_batches,
            total_quantity_kg=total_quantity,
            quantity_unit="kg",
            unique_herbs_count=len(herbs_map),
            unique_farmers_count=len(unique_farmers),
            herbs_summary=herb_summaries,
            verification_breakdown=verification_counts,
        )
