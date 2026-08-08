from typing import List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Schema for GET /health endpoint response."""
    status: str = Field(..., example="healthy")
    service: str = Field(default="dravya-ai-engine", example="dravya-ai-engine")
    model_version: Optional[str] = Field(default=None, example="v1-smoke")
    model_loaded: bool = Field(default=False, example=True)


class TopKPrediction(BaseModel):
    """Schema for individual top-k prediction item."""
    class_name: str = Field(..., example="Saraca asoca")
    confidence: float = Field(..., example=0.94)


class PredictionResponse(BaseModel):
    """Schema for POST /predict endpoint response."""
    model_version: str = Field(..., example="v1-smoke")
    predicted_class: str = Field(..., example="Saraca asoca")
    confidence: float = Field(..., example=0.94)
    top_k: List[TopKPrediction] = Field(default_factory=list)


class ErrorDetail(BaseModel):
    """Schema for structured API error responses."""
    error: str = Field(..., example="Bad Request")
    detail: str = Field(..., example="Unsupported file type.")
