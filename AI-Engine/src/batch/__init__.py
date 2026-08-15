"""
Dravya AI Engine Batch Management Module.
Exposes domain models, manager, aggregator, validator, and ID generator.
"""
from src.batch.batch_aggregator import BatchAggregator
from src.batch.batch_id import generate_batch_id
from src.batch.batch_manager import BatchManager
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
from src.batch.exceptions import (
    BatchException,
    BatchNotFoundError,
    DuplicateBatchError,
    InvalidBatchError,
    InvalidQuantityError,
    LowConfidencePredictionError,
    UnknownHerbError,
)

__all__ = [
    "Batch",
    "BatchCreate",
    "AIPredictionDetails",
    "VerificationStatus",
    "HerbSummary",
    "FarmerSummary",
    "InventorySummary",
    "TraceabilityPayload",
    "BatchManager",
    "BatchAggregator",
    "generate_batch_id",
    "normalize_quantity",
    "validate_batch_input",
    "evaluate_verification_status",
    "BatchException",
    "InvalidQuantityError",
    "UnknownHerbError",
    "InvalidBatchError",
    "BatchNotFoundError",
    "LowConfidencePredictionError",
    "DuplicateBatchError",
]
