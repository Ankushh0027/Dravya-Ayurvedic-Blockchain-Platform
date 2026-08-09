import io
from pathlib import Path
from typing import Optional, Set

from PIL import Image

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from src.api.dependencies import get_predictor_dependency
from src.api.schemas import PredictionResponse, TopKPrediction
from src.data.paths import load_config
from src.inference.predictor import PlantPredictor

router = APIRouter(tags=["Prediction"])

DEFAULT_ALLOWED_CONTENT_TYPES: Set[str] = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/bmp",
}
DEFAULT_MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB


def _get_api_config():
    config = load_config()
    api_cfg = config.get("api", {})
    allowed_types = set(api_cfg.get("allowed_content_types", DEFAULT_ALLOWED_CONTENT_TYPES))
    max_size = api_cfg.get("max_upload_size_bytes", DEFAULT_MAX_UPLOAD_SIZE)
    return allowed_types, max_size


@router.post("/predict", response_model=PredictionResponse)
async def predict_plant_image(
    file: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None),
    predictor: PlantPredictor = Depends(get_predictor_dependency),
):
    """
    Medicinal Plant Image Classification Endpoint for Dravya AI Engine.
    Accepts an uploaded plant image (using field name 'file' or 'image'), validates content type and integrity,
    runs model inference, and returns structured prediction results with top-k probabilities.
    """
    upload_file = image or file
    if upload_file is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing image file payload. Upload file using form field 'file' or 'image'.",
        )

    allowed_types, max_size = _get_api_config()

    # 1. Content-Type Header Validation
    content_type = (upload_file.content_type or "").lower().strip()
    if content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{content_type}'. Allowed types: {sorted(list(allowed_types))}",
        )

    # 2. Read contents & Validate size
    try:
        contents = await upload_file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to read uploaded file contents.",
        )


    if not contents or len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    if len(contents) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed limit of {max_size // (1024 * 1024)} MB.",
        )

    # 3. Image Integrity & Decoding Validation (Do not trust content-type or filename)
    try:
        pil_img = Image.open(io.BytesIO(contents))
        pil_img.verify()  # Verify integrity
        # Re-open after verify() as verify renders original handle unusable for loading
        pil_img = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or corrupted image file.",
        )

    # 4. Inference Execution
    try:
        raw_res = predictor.predict(pil_img, top_k=5)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal prediction failure occurred.",
        )

    top_k_list = [
        TopKPrediction(
            class_id=item.get("class_id"),
            class_name=item.get("species_name") or item.get("canonical_name") or item.get("class_name", "Unknown"),
            species_name=item.get("species_name") or item.get("canonical_name"),
            scientific_name=item.get("scientific_name"),
            confidence=item["confidence"],
        )
        for item in raw_res.get("top_k", [])
    ]

    class_id = raw_res.get("class_id")
    species_name = raw_res.get("species_name") or raw_res.get("canonical_name", "Unknown")
    scientific_name = raw_res.get("scientific_name")
    confidence = raw_res.get("confidence", 0.0)
    model_version = raw_res.get("model_version", predictor.version)

    return PredictionResponse(
        model_version=model_version,
        class_id=class_id,
        predicted_class=species_name,
        species_name=species_name,
        scientific_name=scientific_name,
        confidence=confidence,
        top_k=top_k_list,
    )
