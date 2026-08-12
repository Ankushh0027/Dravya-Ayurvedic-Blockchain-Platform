"""
Pydantic schemas and domain models for Dravya AI Engine Batch Management.
"""
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class VerificationStatus(str, Enum):
    """Status enumeration for batch verification."""
    AI_PREDICTED = "AI_PREDICTED"
    AI_CONFIRMED = "AI_CONFIRMED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    FIELD_VERIFIED = "FIELD_VERIFIED"
    REJECTED = "REJECTED"


class AIPredictionDetails(BaseModel):
    """AI prediction details associated with a batch."""
    predicted_class: str = Field(..., description="Herb class name predicted by model")
    canonical_species: str = Field(..., description="Resolved canonical species name")
    scientific_name: Optional[str] = Field(default=None, description="Botanical scientific name")
    confidence: float = Field(..., description="Model confidence score between 0.0 and 1.0")
    model_version: str = Field(..., description="Trained model version identifier")
    class_id: Optional[str] = Field(default=None, description="Canonical class identifier code")


class BatchCreate(BaseModel):
    """Schema for requesting batch creation."""
    herb_species: str = Field(..., description="Herb species name (common or canonical)")
    farmer_id: str = Field(..., description="Unique farmer reference identifier")
    quantity: float = Field(..., gt=0, description="Herb quantity value (> 0)")
    quantity_unit: str = Field(default="kg", description="Unit of measurement (kg, g, tonne, etc.)")
    harvest_date: str = Field(..., description="Harvest date in YYYY-MM-DD format")
    farmer_name: Optional[str] = Field(default=None, description="Optional farmer display name")
    source: Optional[str] = Field(default="MANUAL", description="Batch data source (e.g. AI_CAMERA, FARMER_PORTAL)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional arbitrary batch metadata")


class Batch(BaseModel):
    """Complete domain model representing an Ayurvedic herb batch."""
    batch_id: str = Field(..., description="Unique, deterministic batch identifier")
    herb_species: str = Field(..., description="Common or requested herb species name")
    canonical_species: str = Field(..., description="Resolved canonical species name")
    scientific_name: Optional[str] = Field(default=None, description="Botanical scientific name")
    farmer_id: str = Field(..., description="Unique farmer identifier")
    farmer_name: Optional[str] = Field(default=None, description="Optional farmer display name")
    quantity: float = Field(..., description="Normalized quantity in canonical unit (kg)")
    quantity_unit: str = Field(default="kg", description="Canonical unit of measurement (kg)")
    original_quantity: float = Field(..., description="Originally submitted quantity value")
    original_unit: str = Field(..., description="Originally submitted quantity unit")
    harvest_date: str = Field(..., description="Harvest date in YYYY-MM-DD format")
    creation_timestamp: str = Field(..., description="ISO 8601 creation timestamp")
    source: str = Field(default="AI_CAMERA", description="Batch data source")
    ai_prediction: Optional[AIPredictionDetails] = Field(default=None, description="Model prediction details if AI-identified")
    verification_status: VerificationStatus = Field(default=VerificationStatus.AI_PREDICTED, description="Batch verification status")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional structured metadata")


class HerbSummary(BaseModel):
    """Aggregated metrics summary for a specific herb species."""
    herb: str = Field(..., description="Herb common name")
    canonical_species: str = Field(..., description="Canonical botanical species name")
    total_batches: int = Field(..., description="Total number of batches for this herb")
    total_quantity: float = Field(..., description="Aggregated total quantity in kg")
    quantity_unit: str = Field(default="kg", description="Aggregation quantity unit")
    farmers_count: int = Field(..., description="Number of unique farmers supplying this herb")
    farmers: List[str] = Field(default_factory=list, description="List of unique farmer IDs")
    verification_breakdown: Dict[str, int] = Field(default_factory=dict, description="Counts by verification status")


class FarmerSummary(BaseModel):
    """Aggregated metrics summary for a specific farmer."""
    farmer_id: str = Field(..., description="Farmer identifier")
    farmer_name: Optional[str] = Field(default=None, description="Farmer display name")
    total_batches: int = Field(..., description="Total batches registered by farmer")
    total_quantity: float = Field(..., description="Total aggregated quantity supplied in kg")
    quantity_unit: str = Field(default="kg", description="Aggregation quantity unit")
    herbs_supplied: List[str] = Field(default_factory=list, description="List of unique canonical herbs supplied")
    batches_by_herb: Dict[str, List[str]] = Field(default_factory=dict, description="Map of canonical herb name to list of batch IDs")


class InventorySummary(BaseModel):
    """Overall inventory metrics summary across all herbs and farmers."""
    total_batches: int = Field(..., description="Total batches across system")
    total_quantity_kg: float = Field(..., description="Total herb inventory weight in kg")
    quantity_unit: str = Field(default="kg", description="Canonical unit")
    unique_herbs_count: int = Field(..., description="Count of unique herb species in inventory")
    unique_farmers_count: int = Field(..., description="Count of unique farmers in inventory")
    herbs_summary: List[HerbSummary] = Field(default_factory=list, description="Herb-wise summaries")
    verification_breakdown: Dict[str, int] = Field(default_factory=dict, description="Counts by verification status across all batches")


class TraceabilityPayload(BaseModel):
    """Blockchain-ready structured traceability record."""
    batch_id: str = Field(..., description="Unique batch ID")
    herb: Dict[str, Optional[str]] = Field(..., description="Herb common, canonical, and scientific names")
    origin: Dict[str, Optional[str]] = Field(..., description="Origin details (farmer_id, farmer_name)")
    quantity: Dict[str, Any] = Field(..., description="Normalized and original quantity values and units")
    ai_verification: Optional[Dict[str, Any]] = Field(default=None, description="AI prediction results, confidence, model version")
    verification_status: str = Field(..., description="Current verification status")
    timestamps: Dict[str, str] = Field(..., description="Timestamps for harvest date and batch creation")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional traceability metadata")
    payload_hash: str = Field(..., description="SHA-256 integrity digest of the payload content")
