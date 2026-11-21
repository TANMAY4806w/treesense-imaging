from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from backend.app.schemas.pathfinding import PathResponse
from backend.app.services.pathfinder import pathfinder_service

router = APIRouter()

@router.post("/pathfind", response_model=PathResponse, summary="Compute optimal terrain trajectory across forest canopy")
async def compute_forest_path(
    file: UploadFile = File(..., description="Terrain or aerial image"),
    start_x: int = Form(50, description="Start X coordinate"),
    start_y: int = Form(50, description="Start Y coordinate"),
    end_x: int = Form(300, description="Target X coordinate"),
    end_y: int = Form(300, description="Target Y coordinate")
):
    try:
        content = await file.read()
        response = pathfinder_service.compute_optimal_path(
            image_bytes=content,
            start_pt=(start_x, start_y),
            end_pt=(end_x, end_y)
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pathfinding calculation error: {str(e)}")
