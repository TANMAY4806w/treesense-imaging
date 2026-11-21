from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from backend.app.schemas.canopy import CanopyResponse
from backend.app.services.spectral import spectral_service

router = APIRouter()

@router.post("/canopy", response_model=CanopyResponse, summary="Analyze vegetation density and spectral indices")
async def analyze_canopy(
    file: UploadFile = File(..., description="Aerial or drone imagery file"),
    method: str = Form("VARI", description="'VARI', 'GLI', 'ExG', or 'HSV'"),
    threshold: float = Form(0.05, description="Sensitivity threshold for the index")
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a valid image.")

    try:
        content = await file.read()
        response = spectral_service.analyze_canopy(
            image_bytes=content,
            method=method,
            threshold=threshold
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Spectral analysis failure: {str(e)}")
