from typing import Optional
from pydantic import BaseModel

class ChangeDetectionResponse(BaseModel):
    success: bool = True
    count_baseline: int
    count_monitoring: int
    tree_delta: int
    percent_delta: float
    alert_level: str  # "CRITICAL_ALERT", "WARNING", "STABLE"
    alert_message: str
    baseline_annotated: str    # Base64 data URL
    monitoring_annotated: str  # Base64 data URL
