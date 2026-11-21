from typing import List, Tuple
from pydantic import BaseModel

class PathResponse(BaseModel):
    success: bool = True
    path_found: bool
    path_length_px: float
    total_cost: float
    elapsed_time_ms: float
    green_coverage_pct: float
    idle_coverage_pct: float
    waypoints: List[Tuple[int, int]]
    path_image: str  # Base64 data URL
