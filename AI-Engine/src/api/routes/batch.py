"""
FastAPI Routes for Dravya AI Engine Batch Organization & Traceability.
"""
import io
from typing import List, Optional

from PIL import Image

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from src.api.dependencies import (
    get_batch_manager_dependency,
    get_batch_service_dependency,
)
from src.batch import (
    Batch,
    BatchCreate,
    BatchManager,
    BatchNotFoundError,
    FarmerSummary,
    HerbSummary,
    InvalidBatchError,
    InvalidQuantityError,
    InventorySummary,
    TraceabilityPayload,
)
from src.services.batch_service import BatchService

router = APIRouter(prefix="/batches", tags=["Batch Management & Traceability"])
inventory_router = APIRouter(prefix="/inventory", tags=["Inventory Analytics"])


@router.post("/create", response_model=Batch, status_code=status.HTTP_201_CREATED)
async def create_batch(
    payload: BatchCreate,
    manager: BatchManager = Depends(get_batch_manager_dependency),
):
    """
    Creates a new herb batch directly from metadata without an image.
    """
    try:
        return manager.create_batch(payload)
    except (InvalidQuantityError, InvalidBatchError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/create-from-image", status_code=status.HTTP_201_CREATED)
async def create_batch_from_image(
    file: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None),
    farmer_id: str = Form(...),
    quantity: float = Form(...),
    quantity_unit: str = Form("kg"),
    harvest_date: str = Form("2026-08-10"),
    farmer_name: Optional[str] = Form(None),
    service: BatchService = Depends(get_batch_service_dependency),
):
    """
    Uploads an image, runs AI herb identification, resolves canonical species and confidence,
    creates a unique Batch ID, and returns the Batch record alongside a blockchain-ready TraceabilityPayload.
    """
    upload_file = image or file
    if upload_file is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing image file payload. Upload file using form field 'file' or 'image'.",
        )

    try:
        contents = await upload_file.read()
        if not contents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty.",
            )
        pil_img = Image.open(io.BytesIO(contents)).convert("RGB")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or corrupted image file.",
        )

    try:
        batch, payload = service.create_batch_from_image(
            image_input=pil_img,
            farmer_id=farmer_id,
            quantity=quantity,
            quantity_unit=quantity_unit,
            harvest_date=harvest_date,
            farmer_name=farmer_name,
        )
        return {
            "batch": batch,
            "traceability_payload": payload,
        }
    except (InvalidQuantityError, InvalidBatchError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )


@router.get("/summary/herb/{herb_name}", response_model=HerbSummary)
async def get_herb_summary(
    herb_name: str,
    manager: BatchManager = Depends(get_batch_manager_dependency),
):
    """
    Returns aggregated metrics summary for a specific herb species across all batches.
    """
    return manager.get_herb_summary(herb_name)


@router.get("/summary/farmer/{farmer_id}", response_model=FarmerSummary)
async def get_farmer_summary(
    farmer_id: str,
    manager: BatchManager = Depends(get_batch_manager_dependency),
):
    """
    Returns aggregated metrics summary for a specific farmer identifier across all batches.
    """
    return manager.get_farmer_summary(farmer_id)


@router.get("/herb/{herb_name}", response_model=List[Batch])
async def get_batches_by_herb(
    herb_name: str,
    manager: BatchManager = Depends(get_batch_manager_dependency),
):
    """
    Lists all batches matching a specific herb species (common or canonical name).
    """
    return manager.list_batches(herb_species=herb_name)


@router.get("/farmer/{farmer_id}", response_model=List[Batch])
async def get_batches_by_farmer(
    farmer_id: str,
    manager: BatchManager = Depends(get_batch_manager_dependency),
):
    """
    Lists all batches supplied by a specific farmer.
    """
    return manager.list_batches(farmer_id=farmer_id)


@router.get("/{batch_id}", response_model=Batch)
async def get_batch_by_id(
    batch_id: str,
    manager: BatchManager = Depends(get_batch_manager_dependency),
):
    """
    Retrieves full batch details for a given unique batch_id.
    """
    try:
        return manager.get_batch(batch_id)
    except BatchNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch '{batch_id}' not found.",
        )


@router.get("/{batch_id}/traceability", response_model=TraceabilityPayload)
async def get_batch_traceability(
    batch_id: str,
    manager: BatchManager = Depends(get_batch_manager_dependency),
):
    """
    Returns a blockchain-ready, tamper-evident traceability payload for a batch.
    """
    try:
        return manager.build_traceability_payload(batch_id)
    except BatchNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch '{batch_id}' not found.",
        )


@inventory_router.get("/summary", response_model=InventorySummary)
async def get_inventory_summary(
    manager: BatchManager = Depends(get_batch_manager_dependency),
):
    """
    Returns overall inventory analytics across all herb species and farmers.
    """
    return manager.get_inventory_summary()
