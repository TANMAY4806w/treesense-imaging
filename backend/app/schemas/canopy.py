from typing import Dict, Any
from pydantic import BaseModel

class CanopyResponse(BaseModel):
    success: bool = True
    index_method: str
    canopy_percentage: float
    barren_percentage: float
    ecological_classification: str
    total_pixels: int
    vegetation_pixels: int
    overlay_image: str  # Base64 data URL
    heatmap_image: str  # Base64 data URL
    telemetry: Dict[str, Any]
