import base64
import io
from pathlib import Path
from typing import Tuple, List, Optional
import cv2
import numpy as np
from PIL import Image

try:
    from ultralytics import YOLO
except (ImportError, ModuleNotFoundError):
    YOLO = None

try:
    import onnxruntime as ort
except (ImportError, ModuleNotFoundError):
    ort = None

try:
    from sahi import AutoDetectionModel
    from sahi.predict import get_sliced_prediction
    SAHI_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    SAHI_AVAILABLE = False

from backend.app.core.config import settings
from backend.app.schemas.detection import BoundingBox, DetectionResponse

class TreeDetectorService:
    def __init__(self):
        self._yolo_model = None
        self._onnx_session = None
        self._sahi_model = None
        self._init_models()

    def _init_models(self):
        if YOLO is not None and settings.DEFAULT_MODEL_PT.exists():
            try:
                self._yolo_model = YOLO(str(settings.DEFAULT_MODEL_PT))
            except Exception as e:
                print(f"[Detector] Failed to load PyTorch YOLO: {e}")

        if ort is not None and settings.DEFAULT_MODEL_ONNX.exists():
            try:
                self._onnx_session = ort.InferenceSession(
                    str(settings.DEFAULT_MODEL_ONNX),
                    providers=["CPUExecutionProvider"]
                )
            except Exception as e:
                print(f"[Detector] Failed to load ONNX: {e}")

        if SAHI_AVAILABLE and settings.DEFAULT_MODEL_PT.exists():
            try:
                import torch
                dev = "cuda:0" if torch.cuda.is_available() else "cpu"
                self._sahi_model = AutoDetectionModel.from_pretrained(
                    model_type="yolov8",
                    model_path=str(settings.DEFAULT_MODEL_PT),
                    confidence_threshold=0.25,
                    device=dev
                )
            except Exception as e:
                print(f"[Detector] Failed to pre-init SAHI: {e}")

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

        # Decide whether to use SAHI Sliced Inference:
        # If user explicitly requested SAHI, or if image dimensions exceed standard 640px
        is_large_image = max(w, h) >= 640
        should_slice = use_sahi and SAHI_AVAILABLE and is_large_image and settings.DEFAULT_MODEL_PT.exists()

        if should_slice:
            return self._detect_sahi(
                pil_img, img_np, w, h, conf_thresh, slice_size, overlap_ratio
            )
        elif (engine in ["auto", "yolo"]) and self._yolo_model is not None:
            return self._detect_yolo(pil_img, img_np, w, h, conf_thresh, iou_thresh)
        elif self._onnx_session is not None:
            return self._detect_onnx(pil_img, img_np, w, h, conf_thresh, iou_thresh)
        else:
            raise RuntimeError("No inference engine (SAHI, YOLO, or ONNX) available on the server.")

    def _detect_sahi(
        self,
        pil_img: Image.Image,
        img_np: np.ndarray,
        w: int,
        h: int,
        conf_thresh: float,
        slice_size: int,
        overlap_ratio: float
    ) -> DetectionResponse:
        import torch
        dev = "cuda:0" if torch.cuda.is_available() else "cpu"
        if self._sahi_model is None:
            self._sahi_model = AutoDetectionModel.from_pretrained(
                model_type="yolov8",
                model_path=str(settings.DEFAULT_MODEL_PT),
                confidence_threshold=conf_thresh,
                device=dev
            )
        else:
            self._sahi_model.confidence_threshold = conf_thresh
        sahi_model = self._sahi_model

        slice_dim = min(slice_size, max(w, h))

        # Run SAHI sliced inference with overlapping patches
        sahi_result = get_sliced_prediction(
            image=pil_img,
            detection_model=sahi_model,
            slice_height=slice_dim,
            slice_width=slice_dim,
            overlap_height_ratio=overlap_ratio,
            overlap_width_ratio=overlap_ratio,
            verbose=0
        )

        detections: List[BoundingBox] = []
        annotated = img_np.copy()

        for i, obj in enumerate(sahi_result.object_prediction_list):
            bbox = obj.bbox
            x1, y1, x2, y2 = int(bbox.minx), int(bbox.miny), int(bbox.maxx), int(bbox.maxy)
            conf = float(obj.score.value)
            label = obj.category.name if obj.category else "tree"
            area = int((x2 - x1) * (y2 - y1))

            detections.append(BoundingBox(
                id=i + 1,
                label=label,
                confidence=round(conf, 3),
                x1=x1, y1=y1, x2=x2, y2=y2,
                area_px=area
            ))

            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 230, 115), 2)
            label_txt = f"{label} {conf:.2f}"
            cv2.putText(annotated, label_txt, (x1, max(y1 - 6, 12)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 230, 115), 1, cv2.LINE_AA)

        slice_cnt = len(sahi_result.durations_in_seconds) if hasattr(sahi_result, "durations_in_seconds") else 1

        return self._format_response(
            annotated, detections, w, h,
            inference_mode="SAHI Sliced Tiling (High-Res Drone Ortho)",
            slice_count=slice_cnt
        )

    def _detect_yolo(
        self, pil_img: Image.Image, img_np: np.ndarray, w: int, h: int,
        conf_thresh: float, iou_thresh: float
    ) -> DetectionResponse:
        results = self._yolo_model.predict(img_np, conf=conf_thresh, iou=iou_thresh, verbose=False)
        boxes = results[0].boxes

        detections: List[BoundingBox] = []
        annotated = img_np.copy()

        if boxes is not None and len(boxes) > 0:
            xyxy = boxes.xyxy.cpu().numpy()
            confs = boxes.conf.cpu().numpy()
            cls_ids = boxes.cls.cpu().numpy().astype(int)

            for i, box in enumerate(xyxy):
                x1, y1, x2, y2 = box.astype(int)
                conf = float(confs[i])
                label = self._yolo_model.names.get(cls_ids[i], "tree") if hasattr(self._yolo_model, "names") else "tree"
                area = int((x2 - x1) * (y2 - y1))

                detections.append(BoundingBox(
                    id=i + 1,
                    label=label,
                    confidence=round(conf, 3),
                    x1=x1, y1=y1, x2=x2, y2=y2,
                    area_px=area
                ))

                cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 230, 115), 2)
                label_txt = f"{label} {conf:.2f}"
                cv2.putText(annotated, label_txt, (x1, max(y1 - 6, 12)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 230, 115), 1, cv2.LINE_AA)

        return self._format_response(
            annotated, detections, w, h,
            inference_mode="Standard Full-Canvas YOLO",
            slice_count=1
        )

    def _detect_onnx(
        self, pil_img: Image.Image, img_np: np.ndarray, w: int, h: int,
        conf_thresh: float, iou_thresh: float
    ) -> DetectionResponse:
        resized = pil_img.resize((640, 640))
        input_arr = np.array(resized).astype(np.float32) / 255.0
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
                x1 = (xc - bw / 2) / 640.0 * w
                y1 = (yc - bh / 2) / 640.0 * h
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
                    x1=bx, y1=by, x2=bx + bw, y2=by + bh,
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
