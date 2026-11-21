import base64
import io
import cv2
import numpy as np
from PIL import Image

from backend.app.schemas.change import ChangeDetectionResponse
from backend.app.services.detector import tree_detector_service

class ChangeAnalysisService:
    def compare_images(
        self,
        baseline_bytes: bytes,
        monitoring_bytes: bytes,
        conf_thresh: float = 0.25,
        iou_thresh: float = 0.45
    ) -> ChangeDetectionResponse:
        res_baseline = tree_detector_service.detect(baseline_bytes, conf_thresh, iou_thresh)
        res_monitoring = tree_detector_service.detect(monitoring_bytes, conf_thresh, iou_thresh)

        c_base = res_baseline.tree_count
        c_mon = res_monitoring.tree_count

        delta = c_mon - c_base
        percent_delta = round(((c_mon - c_base) / c_base) * 100.0, 2) if c_base > 0 else 0.0

        if c_base > 0 and percent_delta <= -10.0:
            alert_level = "CRITICAL_ALERT"
            alert_msg = f"Severe deforestation detected: {abs(percent_delta)}% canopy reduction ({abs(delta)} trees lost)."
        elif c_base > 0 and percent_delta < 0.0:
            alert_level = "WARNING"
            alert_msg = f"Canopy decline observed: {abs(percent_delta)}% reduction ({abs(delta)} trees lost)."
        else:
            alert_level = "STABLE"
            alert_msg = f"Forest canopy stable or expanding: net change {delta:+d} trees ({percent_delta:+.1f}%)."

        return ChangeDetectionResponse(
            success=True,
            count_baseline=c_base,
            count_monitoring=c_mon,
            tree_delta=delta,
            percent_delta=percent_delta,
            alert_level=alert_level,
            alert_message=alert_msg,
            baseline_annotated=res_baseline.annotated_image,
            monitoring_annotated=res_monitoring.annotated_image
        )

change_service = ChangeAnalysisService()
