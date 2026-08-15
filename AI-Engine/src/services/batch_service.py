"""
High-level Service orchestration connecting PlantPredictor inference with Batch Management.
"""
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union
from PIL import Image

from src.batch import (
    AIPredictionDetails,
    Batch,
    BatchCreate,
    BatchManager,
    TraceabilityPayload,
)
from src.inference.predictor import PlantPredictor


class BatchService:
    """
    Service orchestrator handling end-to-end flow:
    Image → PlantPredictor → Canonical Species & Confidence → Batch Creation → Traceability Payload.
    """

    def __init__(
        self,
        predictor: Optional[PlantPredictor] = None,
        batch_manager: Optional[BatchManager] = None,
    ):
        self.predictor = predictor
        self.batch_manager = batch_manager or BatchManager()

    def set_predictor(self, predictor: PlantPredictor) -> None:
        self.predictor = predictor

    def create_batch_from_image(
        self,
        image_input: Union[str, Path, Image.Image, bytes],
        farmer_id: str,
        quantity: float,
        quantity_unit: str = "kg",
        harvest_date: str = "2026-08-10",
        farmer_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        nonce: Optional[str] = None,
    ) -> Tuple[Batch, TraceabilityPayload]:
        """
        Runs model inference on input image, resolves canonical species and confidence,
        creates a deterministic batch record, and builds a blockchain-ready traceability payload.
        """
        if self.predictor is None:
            raise RuntimeError("PlantPredictor is not configured in BatchService.")

        # 1. Run AI inference
        raw_res = self.predictor.predict(image_input, top_k=5)

        predicted_class = raw_res.get("species_name") or raw_res.get("canonical_name") or "Unknown"
        canonical_species = raw_res.get("canonical_name") or predicted_class
        scientific_name = raw_res.get("scientific_name")
        confidence = float(raw_res.get("confidence", 0.0))
        model_version = raw_res.get("model_version", self.predictor.version)
        class_id = raw_res.get("class_id")

        # 2. Build AI prediction details container
        ai_prediction = AIPredictionDetails(
            predicted_class=predicted_class,
            canonical_species=canonical_species,
            scientific_name=scientific_name,
            confidence=confidence,
            model_version=model_version,
            class_id=class_id,
        )

        # 3. Build BatchCreate model
        batch_data = BatchCreate(
            herb_species=predicted_class,
            farmer_id=farmer_id,
            quantity=quantity,
            quantity_unit=quantity_unit,
            harvest_date=harvest_date,
            farmer_name=farmer_name,
            source="AI_CAMERA",
            metadata=metadata or {},
        )

        # 4. Create batch in BatchManager
        batch = self.batch_manager.create_batch(
            batch_data=batch_data,
            canonical_species=canonical_species,
            scientific_name=scientific_name,
            ai_prediction=ai_prediction,
            nonce=nonce,
        )

        # 5. Build traceability payload
        payload = self.batch_manager.build_traceability_payload(batch.batch_id)

        return batch, payload
