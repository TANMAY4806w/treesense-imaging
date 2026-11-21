from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from backend.app.schemas.detection import DetectionResponse
from backend.app.services.detector import tree_detector_service

router = APIRouter()

@router.post("/detect", response_model=DetectionResponse, summary="Detect and count trees in aerial imagery (Supports SAHI Slicing)")
async def detect_trees(
    file: UploadFile = File(..., description="Aerial or drone imagery file (JPEG/PNG)"),
    confidence: float = Form(0.25, ge=0.01, le=0.99, description="Confidence threshold"),
    iou: float = Form(0.45, ge=0.05, le=0.95, description="IoU threshold for NMS"),
    engine: str = Form("auto", description="'auto', 'yolo', or 'onnx'"),
    use_sahi: bool = Form(True, description="Enable SAHI Sliced Tiling for high-res imagery"),
    slice_size: int = Form(512, ge=256, le=1024, description="Tile window dimension (px)"),
    overlap_ratio: float = Form(0.2, ge=0.05, le=0.5, description="Overlap ratio between adjacent slices")
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a valid image.")

    try:
        content = await file.read()
        response = tree_detector_service.detect(
            image_bytes=content,
            conf_thresh=confidence,
            iou_thresh=iou,
            engine=engine,
            use_sahi=use_sahi,
            slice_size=slice_size,
            overlap_ratio=overlap_ratio
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failure: {str(e)}")
