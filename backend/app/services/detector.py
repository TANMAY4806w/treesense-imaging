import base64
import io
import math
from pathlib import Path
from typing import Tuple, List, Optional
import cv2
import numpy as np
from PIL import Image

try:
    import onnxruntime as ort
except (ImportError, ModuleNotFoundError):
    ort = None

from backend.app.core.config import settings
from backend.app.schemas.detection import BoundingBox, DetectionResponse

class TreeDetectorService:
    def __init__(self):
        self._onnx_session = None
        self._init_models()

    def _init_models(self):
        if ort is not None and settings.DEFAULT_MODEL_ONNX.exists():
            try:
                # Set thread options for efficient edge CPU inference
                so = ort.SessionOptions()
                so.intra_op_num_threads = 2
                so.inter_op_num_threads = 1
                self._onnx_session = ort.InferenceSession(
                    str(settings.DEFAULT_MODEL_ONNX),
                    sess_options=so,
                    providers=["CPUExecutionProvider"]
                )
                print("[Detector] Loaded high-speed ONNX Runtime engine (FP16/FP32).")
            except Exception as e:
                print(f"[Detector] Failed to load ONNX: {e}")

    def detect(
        self,
        image_bytes: bytes,
        conf_thresh: float = 0.25,
        iou_thresh: float = 0.45,
        engine: str = "auto",
        use_sahi: bool = True,
        slice_size: int = 512,
        overlap_ratio: float = 0.2
    ) -> DetectionResponse:
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        w, h = pil_img.size
        img_np = np.array(pil_img)

        if self._onnx_session is None:
            # Attempt to re-initialize if session was not loaded
            self._init_models()
            if self._onnx_session is None:
                raise RuntimeError("ONNX Runtime inference session is unavailable. Verify models/best.onnx exists.")

        is_large_image = max(w, h) >= 640
        should_slice = use_sahi and is_large_image

        if should_slice:
            return self._detect_onnx_sliced(
                pil_img, img_np, w, h, conf_thresh, iou_thresh, slice_size, overlap_ratio
            )
        else:
            return self._detect_onnx_full(pil_img, img_np, w, h, conf_thresh, iou_thresh)

    def _generate_slices(
        self, w: int, h: int, slice_dim: int, overlap_ratio: float
    ) -> List[Tuple[int, int, int, int]]:
        step = max(64, int(slice_dim * (1.0 - overlap_ratio)))
        slices = []
        y = 0
        while y < h:
            x = 0
            y2 = min(y + slice_dim, h)
            y1 = max(0, y2 - slice_dim) if (y2 == h and y > 0) else y
            while x < w:
                x2 = min(x + slice_dim, w)
                x1 = max(0, x2 - slice_dim) if (x2 == w and x > 0) else x
                slices.append((x1, y1, x2, y2))
                if x2 >= w:
                    break
                x += step
            if y2 >= h:
                break
            y += step
        return slices

    def _detect_onnx_sliced(
        self,
        pil_img: Image.Image,
        img_np: np.ndarray,
        w: int,
        h: int,
        conf_thresh: float,
        iou_thresh: float,
        slice_size: int,
        overlap_ratio: float
    ) -> DetectionResponse:
        slice_dim = min(slice_size, max(w, h))
        slices = self._generate_slices(w, h, slice_dim, overlap_ratio)

        all_boxes: List[List[int]] = []
        all_confs: List[float] = []

        input_name = self._onnx_session.get_inputs()[0].name

        for (sx1, sy1, sx2, sy2) in slices:
            patch = pil_img.crop((sx1, sy1, sx2, sy2))
            pw, ph = patch.size
            if pw < 10 or ph < 10:
                continue

            resized = patch.resize((640, 640))
            input_arr = np.array(resized, dtype=np.float32) / 255.0
            input_arr = np.transpose(input_arr, (2, 0, 1))[np.newaxis, :, :, :]

            raw_out = self._onnx_session.run(None, {input_name: input_arr})[0]

            if raw_out.ndim == 3 and raw_out.shape[1] < raw_out.shape[2]:
                raw_out = np.transpose(raw_out, (0, 2, 1))

            for pred in raw_out[0]:
                xc, yc, bw, bh = pred[:4]
                conf = float(np.max(pred[4:])) if len(pred) > 4 else float(pred[4])
                if conf >= conf_thresh:
                    # Map from 640x640 to patch coordinates
                    px1 = (xc - bw / 2.0) / 640.0 * pw
                    py1 = (yc - bh / 2.0) / 640.0 * ph
                    p_w = bw / 640.0 * pw
                    p_h = bh / 640.0 * ph

                    # Map to full image coordinates
                    gx1 = int(px1 + sx1)
                    gy1 = int(py1 + sy1)
                    gw = int(p_w)
                    gh = int(p_h)

                    all_boxes.append([gx1, gy1, gw, gh])
                    all_confs.append(conf)

        # Global Non-Maximum Suppression across all overlapping slices
        indices = cv2.dnn.NMSBoxes(all_boxes, all_confs, conf_thresh, iou_thresh)
        detections: List[BoundingBox] = []
        annotated = img_np.copy()

        if len(indices) > 0:
            for idx in indices.flatten():
                bx, by, bw, bh = all_boxes[idx]
                c = all_confs[idx]
                detections.append(BoundingBox(
                    id=len(detections) + 1,
                    label="tree",
                    confidence=round(c, 3),
                    x1=max(0, bx),
                    y1=max(0, by),
                    x2=min(w, bx + bw),
                    y2=min(h, by + bh),
                    area_px=bw * bh
                ))
                cv2.rectangle(annotated, (bx, by), (bx + bw, by + bh), (0, 230, 115), 2)

        return self._format_response(
            annotated, detections, w, h,
            inference_mode="Lightweight ONNX Sliced Tiling (Zero-OOM)",
            slice_count=len(slices)
        )

    def _detect_onnx_full(
        self,
        pil_img: Image.Image,
        img_np: np.ndarray,
        w: int,
        h: int,
        conf_thresh: float,
        iou_thresh: float
    ) -> DetectionResponse:
        resized = pil_img.resize((640, 640))
        input_arr = np.array(resized, dtype=np.float32) / 255.0
        input_arr = np.transpose(input_arr, (2, 0, 1))[np.newaxis, :, :, :]

        input_name = self._onnx_session.get_inputs()[0].name
        raw_out = self._onnx_session.run(None, {input_name: input_arr})[0]

        if raw_out.ndim == 3 and raw_out.shape[1] < raw_out.shape[2]:
            raw_out = np.transpose(raw_out, (0, 2, 1))

        boxes, confs = [], []
        for pred in raw_out[0]:
            xc, yc, bw, bh = pred[:4]
            conf = float(np.max(pred[4:])) if len(pred) > 4 else float(pred[4])
            if conf >= conf_thresh:
                x1 = (xc - bw / 2.0) / 640.0 * w
                y1 = (yc - bh / 2.0) / 640.0 * h
                boxes.append([int(x1), int(y1), int(bw / 640.0 * w), int(bh / 640.0 * h)])
                confs.append(conf)

        indices = cv2.dnn.NMSBoxes(boxes, confs, conf_thresh, iou_thresh)
        detections: List[BoundingBox] = []
        annotated = img_np.copy()

        if len(indices) > 0:
            for idx in indices.flatten():
                bx, by, bw, bh = boxes[idx]
                c = confs[idx]
                detections.append(BoundingBox(
                    id=len(detections) + 1,
                    label="tree",
                    confidence=round(c, 3),
                    x1=max(0, bx),
                    y1=max(0, by),
                    x2=min(w, bx + bw),
                    y2=min(h, by + bh),
                    area_px=bw * bh
                ))
                cv2.rectangle(annotated, (bx, by), (bx + bw, by + bh), (0, 230, 115), 2)

        return self._format_response(
            annotated, detections, w, h,
            inference_mode="ONNX Runtime Full Canvas",
            slice_count=1
        )

    def _format_response(
        self,
        annotated: np.ndarray,
        detections: List[BoundingBox],
        w: int,
        h: int,
        inference_mode: str,
        slice_count: int
    ) -> DetectionResponse:
        count = len(detections)
        avg_conf = float(np.mean([d.confidence for d in detections])) if detections else 0.0
        total_px = w * h
        est_tree_px = sum(d.area_px for d in detections)
        est_cov = round(min(100.0, (est_tree_px / total_px) * 100), 2) if total_px > 0 else 0.0

        if count < 15:
            density = "Low Density"
        elif count < 45:
            density = "Medium Density"
        else:
            density = "High Canopy Density"

        # Encode annotated image to Base64
        _, buffer = cv2.imencode(".jpg", cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))
        b64_str = f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"

        return DetectionResponse(
            success=True,
            tree_count=count,
            avg_confidence=round(avg_conf, 3),
            canopy_density=density,
            est_canopy_coverage_pct=est_cov,
            detections=detections,
            image_width=w,
            image_height=h,
            annotated_image=b64_str,
            inference_mode=inference_mode,
            slice_count=slice_count
        )

tree_detector_service = TreeDetectorService()
