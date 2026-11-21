from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from backend.app.schemas.change import ChangeDetectionResponse
from backend.app.services.change_service import change_service

router = APIRouter()

@router.post("/change", response_model=ChangeDetectionResponse, summary="Compare bi-temporal imagery for canopy delta")
async def compare_temporal_images(
    baseline_file: UploadFile = File(..., description="Time A baseline image"),
    monitoring_file: UploadFile = File(..., description="Time B monitoring image"),
    confidence: float = Form(0.25, ge=0.01, le=0.99),
    iou: float = Form(0.45, ge=0.05, le=0.95)
):
    try:
        baseline_bytes = await baseline_file.read()
        monitoring_bytes = await monitoring_file.read()

        response = change_service.compare_images(
            baseline_bytes=baseline_bytes,
            monitoring_bytes=monitoring_bytes,
            conf_thresh=confidence,
            iou_thresh=iou
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Change detection error: {str(e)}")
