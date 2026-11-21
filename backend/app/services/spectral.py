import base64
import io
from typing import Dict, Any
import cv2
import numpy as np
from PIL import Image

from backend.app.schemas.canopy import CanopyResponse

class SpectralAnalyticsService:
    def analyze_canopy(
        self,
        image_bytes: bytes,
        method: str = "VARI",
        threshold: float = 0.05
    ) -> CanopyResponse:
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_np = np.array(pil_img)
        h, w = img_np.shape[:2]
        total_pixels = h * w

        # Normalization [0, 1]
        r = img_np[:, :, 0].astype(np.float32) / 255.0
        g = img_np[:, :, 1].astype(np.float32) / 255.0
        b = img_np[:, :, 2].astype(np.float32) / 255.0
        eps = 1e-6

        if method.upper() == "VARI":
            # Visible Atmospherically Resistant Index
            denom = g + r - b
            denom = np.where(np.abs(denom) < eps, eps, denom)
            idx_map = (g - r) / denom
            idx_map = np.clip(idx_map, -1.0, 1.0)
            mask = idx_map > threshold

        elif method.upper() == "GLI":
            # Green Leaf Index
            denom = 2 * g + r + b
            denom = np.where(denom < eps, eps, denom)
            idx_map = (2 * g - r - b) / denom
            idx_map = np.clip(idx_map, -1.0, 1.0)
            mask = idx_map > threshold

        elif method.upper() == "EXG":
            # Excess Green
            sum_rgb = r + g + b + eps
            rn, gn, bn = r / sum_rgb, g / sum_rgb, b / sum_rgb
            idx_map = 2 * gn - rn - bn
            mask = idx_map > threshold

        elif method.upper() == "HSV":
            hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)
            lower_green = np.array([30, int(threshold * 50), int(threshold * 40)])
            upper_green = np.array([90, 255, 255])
            mask = cv2.inRange(hsv, lower_green, upper_green) > 0
            idx_map = (hsv[:, :, 0].astype(np.float32) / 180.0)

        else:
            # Default Green Dominance
            mask = (g > (r * threshold)) & (g > (b * threshold))
            idx_map = g - np.maximum(r, b)

        vegetation_pixels = int(np.sum(mask))
        canopy_pct = round((vegetation_pixels / total_pixels) * 100.0, 2)
        barren_pct = round(100.0 - canopy_pct, 2)

        # Classification
        if canopy_pct > 60.0:
            classification = "Dense Forest Canopy"
        elif canopy_pct > 30.0:
            classification = "Moderate Vegetation Cover"
        else:
            classification = "Sparse / Degraded Cover"

        # Generate Heatmap
        norm_idx = cv2.normalize(idx_map, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        heatmap = cv2.applyColorMap(norm_idx, cv2.COLORMAP_SUMMER)

        # Generate Overlay
        overlay = img_np.copy()
        overlay[mask] = (overlay[mask] * 0.4 + np.array([0, 230, 80]) * 0.6).astype(np.uint8)

        # Base64 encodings
        _, buf_over = cv2.imencode(".jpg", cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
        overlay_b64 = f"data:image/jpeg;base64,{base64.b64encode(buf_over).decode('utf-8')}"

        _, buf_heat = cv2.imencode(".jpg", heatmap)
        heatmap_b64 = f"data:image/jpeg;base64,{base64.b64encode(buf_heat).decode('utf-8')}"

        telemetry: Dict[str, Any] = {
            "total_pixels": total_pixels,
            "vegetation_pixels": vegetation_pixels,
            "mean_index_val": round(float(np.mean(idx_map)), 4),
            "threshold_applied": threshold
        }

        return CanopyResponse(
            success=True,
            index_method=method.upper(),
            canopy_percentage=canopy_pct,
            barren_percentage=barren_pct,
            ecological_classification=classification,
            total_pixels=total_pixels,
            vegetation_pixels=vegetation_pixels,
            overlay_image=overlay_b64,
            heatmap_image=heatmap_b64,
            telemetry=telemetry
        )

spectral_service = SpectralAnalyticsService()
