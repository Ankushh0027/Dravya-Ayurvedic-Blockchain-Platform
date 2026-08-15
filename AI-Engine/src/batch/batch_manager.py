"""
Thread-safe Repository and Management Service for Ayurvedic Herb Batches.
"""
from datetime import datetime, timezone
import hashlib
import json
import threading
from typing import Dict, List, Optional, Any

from src.batch.batch_aggregator import BatchAggregator
from src.batch.batch_id import generate_batch_id
from src.batch.batch_schema import (
    AIPredictionDetails,
    Batch,
    BatchCreate,
    FarmerSummary,
    HerbSummary,
    InventorySummary,
    TraceabilityPayload,
    VerificationStatus,
)
from src.batch.batch_validator import (
    evaluate_verification_status,
    normalize_quantity,
    validate_batch_input,
)
from src.batch.exceptions import BatchNotFoundError, DuplicateBatchError
from src.data.paths import load_config


class BatchManager:
    """
    In-memory batch management repository providing decoupled data operations,
    aggregations, and blockchain-ready traceability payload generation.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self._lock = threading.RLock()
        self._batches: Dict[str, Batch] = {}

        # Load config thresholds
        cfg = config or load_config()
        batch_cfg = cfg.get("batch", {})
        thresholds = batch_cfg.get("confidence_thresholds", {})
        self.confirmed_threshold = float(thresholds.get("confirmed", 0.90))
        self.review_threshold = float(thresholds.get("review_required", 0.70))
        self.id_prefix = str(batch_cfg.get("id_prefix", "DRAVYA"))

    def clear(self) -> None:
        """Clears all stored batches (useful for testing)."""
        with self._lock:
            self._batches.clear()

    def create_batch(
        self,
        batch_data: BatchCreate,
        canonical_species: Optional[str] = None,
        scientific_name: Optional[str] = None,
        ai_prediction: Optional[AIPredictionDetails] = None,
        verification_status: Optional[VerificationStatus] = None,
        nonce: Optional[str] = None,
    ) -> Batch:
        """
        Validates metadata, normalizes quantity, generates deterministic Batch ID,
        evaluates verification status, and persists batch.
        """
        validate_batch_input(
            herb_species=batch_data.herb_species,
            farmer_id=batch_data.farmer_id,
            quantity=batch_data.quantity,
            quantity_unit=batch_data.quantity_unit,
            harvest_date=batch_data.harvest_date,
        )

        normalized_kg, canonical_unit = normalize_quantity(
            batch_data.quantity, batch_data.quantity_unit
        )

        resolved_canonical = (
            canonical_species
            or (ai_prediction.canonical_species if ai_prediction else None)
            or batch_data.herb_species
        )

        resolved_scientific = (
            scientific_name
            or (ai_prediction.scientific_name if ai_prediction else None)
        )

        # Generate deterministic Batch ID
        batch_id = generate_batch_id(
            herb_species=batch_data.herb_species,
            farmer_id=batch_data.farmer_id,
            harvest_date=batch_data.harvest_date,
            quantity_kg=normalized_kg,
            prefix=self.id_prefix,
            nonce=nonce,
        )

        # Evaluate verification status if not explicitly provided
        if verification_status is None:
            if ai_prediction:
                verification_status = evaluate_verification_status(
                    confidence=ai_prediction.confidence,
                    confirmed_threshold=self.confirmed_threshold,
                    review_threshold=self.review_threshold,
                )
            else:
                verification_status = VerificationStatus.AI_PREDICTED

        creation_ts = datetime.now(timezone.utc).isoformat()

        batch = Batch(
            batch_id=batch_id,
            herb_species=batch_data.herb_species,
            canonical_species=resolved_canonical,
            scientific_name=resolved_scientific,
            farmer_id=batch_data.farmer_id,
            farmer_name=batch_data.farmer_name,
            quantity=normalized_kg,
            quantity_unit=canonical_unit,
            original_quantity=batch_data.quantity,
            original_unit=batch_data.quantity_unit,
            harvest_date=batch_data.harvest_date,
            creation_timestamp=creation_ts,
            source=batch_data.source or "MANUAL",
            ai_prediction=ai_prediction,
            verification_status=verification_status,
            metadata=batch_data.metadata or {},
        )

        return self.register_batch(batch)

    def register_batch(self, batch: Batch) -> Batch:
        """Registers and stores a Batch entity."""
        with self._lock:
            if batch.batch_id in self._batches:
                raise DuplicateBatchError(
                    f"Batch with ID '{batch.batch_id}' already exists in manager."
                )
            self._batches[batch.batch_id] = batch
            return batch

    def get_batch(self, batch_id: str) -> Batch:
        """Retrieves a batch by ID or raises BatchNotFoundError."""
        with self._lock:
            if batch_id not in self._batches:
                raise BatchNotFoundError(f"Batch '{batch_id}' not found.")
            return self._batches[batch_id]

    def list_batches(
        self,
        herb_species: Optional[str] = None,
        farmer_id: Optional[str] = None,
        verification_status: Optional[str] = None,
    ) -> List[Batch]:
        """Lists batches with optional filtering by herb species, farmer ID, or status."""
        with self._lock:
            result = list(self._batches.values())

            if herb_species:
                herb_clean = herb_species.strip().lower()
                result = [
                    b for b in result
                    if b.herb_species.strip().lower() == herb_clean or b.canonical_species.strip().lower() == herb_clean
                ]

            if farmer_id:
                farmer_clean = farmer_id.strip()
                result = [b for b in result if b.farmer_id.strip() == farmer_clean]

            if verification_status:
                status_clean = verification_status.strip().upper()
                result = [
                    b for b in result
                    if (b.verification_status.value if hasattr(b.verification_status, "value") else str(b.verification_status)).upper() == status_clean
                ]

            return result

    def get_herb_summary(self, herb_species: str) -> HerbSummary:
        """Returns aggregated summary metrics for a herb species."""
        with self._lock:
            all_batches = list(self._batches.values())
            return BatchAggregator.get_herb_summary(herb_species, all_batches)

    def get_farmer_summary(self, farmer_id: str) -> FarmerSummary:
        """Returns aggregated summary metrics for a farmer ID."""
        with self._lock:
            all_batches = list(self._batches.values())
            return BatchAggregator.get_farmer_summary(farmer_id, all_batches)

    def get_inventory_summary(self) -> InventorySummary:
        """Returns overall inventory summary metrics."""
        with self._lock:
            all_batches = list(self._batches.values())
            return BatchAggregator.get_inventory_summary(all_batches)

    def build_traceability_payload(self, batch_id: str) -> TraceabilityPayload:
        """
        Generates a blockchain-ready, tamper-evident traceability payload for a batch.
        """
        batch = self.get_batch(batch_id)

        status_str = (
            batch.verification_status.value
            if hasattr(batch.verification_status, "value")
            else str(batch.verification_status)
        )

        ai_verification_dict = None
        if batch.ai_prediction:
            ai_verification_dict = {
                "prediction": batch.ai_prediction.predicted_class,
                "canonical_species": batch.ai_prediction.canonical_species,
                "confidence": batch.ai_prediction.confidence,
                "model_version": batch.ai_prediction.model_version,
                "class_id": batch.ai_prediction.class_id,
            }

        raw_payload = {
            "batch_id": batch.batch_id,
            "herb": {
                "common_name": batch.herb_species,
                "canonical_species": batch.canonical_species,
                "scientific_name": batch.scientific_name,
            },
            "origin": {
                "farmer_id": batch.farmer_id,
                "farmer_name": batch.farmer_name,
            },
            "quantity": {
                "value": batch.quantity,
                "unit": batch.quantity_unit,
                "original_value": batch.original_quantity,
                "original_unit": batch.original_unit,
            },
            "ai_verification": ai_verification_dict,
            "verification_status": status_str,
            "timestamps": {
                "created_at": batch.creation_timestamp,
                "harvest_date": batch.harvest_date,
            },
            "metadata": batch.metadata,
        }

        # Compute SHA-256 digest of payload for tamper validation
        json_bytes = json.dumps(raw_payload, sort_keys=True).encode("utf-8")
        payload_hash = hashlib.sha256(json_bytes).hexdigest()

        return TraceabilityPayload(
            batch_id=batch.batch_id,
            herb=raw_payload["herb"],
            origin=raw_payload["origin"],
            quantity=raw_payload["quantity"],
            ai_verification=raw_payload["ai_verification"],
            verification_status=status_str,
            timestamps=raw_payload["timestamps"],
            metadata=raw_payload["metadata"],
            payload_hash=payload_hash,
        )
