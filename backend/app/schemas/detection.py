from typing import List, Optional
from pydantic import BaseModel, Field

class BoundingBox(BaseModel):
    id: int
    label: str = "tree"
    confidence: float
    x1: int
    y1: int
    x2: int
    y2: int
    area_px: int

class DetectionResponse(BaseModel):
    success: bool = True
    tree_count: int
    avg_confidence: float
    canopy_density: str
    est_canopy_coverage_pct: float
    detections: List[BoundingBox]
    image_width: int
    image_height: int
    annotated_image: str  # Base64 data URL
    inference_mode: str = "Standard Full Canvas"
    slice_count: int = 1
