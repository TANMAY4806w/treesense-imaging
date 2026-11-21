"""
Tree Detection & Enumeration Module
Provides AI-powered tree detection using YOLO and ONNX Runtime with interactive thresholding.
"""

from pathlib import Path
from typing import List, Tuple, Optional
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import streamlit as st

try:
    from ultralytics import YOLO
except (ImportError, ModuleNotFoundError):
    YOLO = None

try:
    import onnxruntime as ort
except (ImportError, ModuleNotFoundError):
    ort = None

# Base path relative to project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL_PT = PROJECT_ROOT / "models" / "best.pt"
DEFAULT_MODEL_ONNX = PROJECT_ROOT / "models" / "best.onnx"


@st.cache_resource
def load_yolo_model(model_path: Path):
    """Load Ultralytics YOLO model with Streamlit caching."""
    if YOLO is None:
        return None
    if not model_path.exists():
        return None
    try:
        return YOLO(str(model_path))
    except Exception as e:
        st.error(f"Failed to load PyTorch YOLO model: {e}")
        return None


@st.cache_resource
def load_onnx_session(model_path: Path):
    """Load ONNX Runtime inference session with caching."""
    if ort is None:
        return None
    if not model_path.exists():
        return None
    try:
        session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
        return session
    except Exception as e:
        st.error(f"Failed to load ONNX model: {e}")
        return None


def run_yolo_inference(
    model, image: Image.Image, conf_threshold: float, iou_threshold: float
) -> Tuple[np.ndarray, List[dict], int]:
    """
    Run detection using YOLO PyTorch model.
    Returns: annotated RGB image array, list of detections, count.
    """
    # Ensure RGB
    img_rgb = image.convert("RGB")
    img_np = np.array(img_rgb)
    h, w = img_np.shape[:2]

    results = model.predict(img_np, conf=conf_threshold, iou=iou_threshold, verbose=False)
    boxes = results[0].boxes

    detections = []
    annotated = img_np.copy()

    if boxes is not None and len(boxes) > 0:
        xyxy = boxes.xyxy.cpu().numpy()
        confs = boxes.conf.cpu().numpy()
        cls_ids = boxes.cls.cpu().numpy().astype(int)

        for i, box in enumerate(xyxy):
            x1, y1, x2, y2 = box.astype(int)
            conf = float(confs[i])
            cls_name = model.names.get(cls_ids[i], "tree") if hasattr(model, "names") else "tree"

            detections.append({
                "id": i + 1,
                "label": cls_name,
                "confidence": conf,
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "area_px": (x2 - x1) * (y2 - y1),
            })

            # Draw bounding box and label
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 230, 115), 2)
            label_text = f"{cls_name} {conf:.2f}"
            t_size = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)[0]
            cv2.rectangle(annotated, (x1, y1 - t_size[1] - 4), (x1 + t_size[0] + 4, y1), (0, 230, 115), -1)
            cv2.putText(
                annotated,
                label_text,
                (x1 + 2, y1 - 3),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )

    return annotated, detections, len(detections)


def show_tree_count_page():
    """Main Streamlit page for Tree Detection & Enumeration."""
    st.title("🌳 AI Tree Detection & Canopy Enumeration")
    st.markdown(
        "Upload aerial or satellite imagery to automatically detect, count, and evaluate tree canopies."
    )

    # Sidebar controls
    with st.sidebar:
        st.markdown("---")
        st.markdown("### ⚙️ Detection Settings")
        conf_thresh = st.slider("Confidence Threshold", 0.05, 0.95, 0.25, 0.05)
        iou_thresh = st.slider("IoU NMS Threshold", 0.1, 0.9, 0.45, 0.05)
        engine = st.radio("Inference Engine", ["YOLO (PyTorch)", "ONNX Runtime"], index=0)

    uploaded_file = st.file_uploader(
        "Upload Forest Aerial / Drone / Satellite Image",
        type=["jpg", "jpeg", "png"],
        help="Recommended: Orthomosaics or aerial crops with visible tree canopies"
    )

    if not uploaded_file:
        st.info("👆 Please upload an aerial or drone image to begin detection.")
        return

    image = Image.open(uploaded_file)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("#### Input Image")
        st.image(image, use_container_width=True, caption=f"Original ({image.width}x{image.height} px)")

    if st.button("🔍 Run Tree Detection", type="primary", use_container_width=True):
        with st.spinner("Analyzing canopy features with neural network..."):
            model = None
            if engine == "YOLO (PyTorch)":
                model = load_yolo_model(DEFAULT_MODEL_PT)
            
            if model is None and engine == "YOLO (PyTorch)":
                st.warning("⚠️ PyTorch model not found or Ultralytics unavailable. Checking ONNX fallback...")
                engine = "ONNX Runtime"

            if engine == "YOLO (PyTorch)" and model is not None:
                annotated, detections, count = run_yolo_inference(model, image, conf_thresh, iou_thresh)
            else:
                # ONNX or Fallback
                onnx_session = load_onnx_session(DEFAULT_MODEL_ONNX)
                if onnx_session is not None:
                    # Preprocess for ONNX (640x640)
                    img_rgb = image.convert("RGB")
                    orig_w, orig_h = img_rgb.size
                    resized = img_rgb.resize((640, 640))
                    input_arr = np.array(resized).astype(np.float32) / 255.0
                    input_arr = np.transpose(input_arr, (2, 0, 1))[np.newaxis, :, :, :]

                    input_name = onnx_session.get_inputs()[0].name
                    raw_out = onnx_session.run(None, {input_name: input_arr})[0]

                    # Standard YOLOv8 ONNX postprocessing [1, 5, 8400]
                    annotated = np.array(img_rgb).copy()
                    detections = []
                    if raw_out.ndim == 3 and raw_out.shape[1] < raw_out.shape[2]:
                        raw_out = np.transpose(raw_out, (0, 2, 1))

                    boxes = []
                    confs = []
                    for pred in raw_out[0]:
                        xc, yc, w, h = pred[:4]
                        conf = float(np.max(pred[4:])) if len(pred) > 4 else float(pred[4])
                        if conf >= conf_thresh:
                            x1 = (xc - w / 2) / 640.0 * orig_w
                            y1 = (yc - h / 2) / 640.0 * orig_h
                            x2 = (xc + w / 2) / 640.0 * orig_w
                            y2 = (yc + h / 2) / 640.0 * orig_h
                            boxes.append([int(x1), int(y1), int(x2 - x1), int(y2 - y1)])
                            confs.append(conf)

                    indices = cv2.dnn.NMSBoxes(boxes, confs, conf_thresh, iou_thresh)
                    if len(indices) > 0:
                        indices = indices.flatten()
                        for idx in indices:
                            bx, by, bw, bh = boxes[idx]
                            c = confs[idx]
                            detections.append({
                                "id": len(detections) + 1,
                                "label": "tree",
                                "confidence": c,
                                "x1": bx,
                                "y1": by,
                                "x2": bx + bw,
                                "y2": by + bh,
                                "area_px": bw * bh,
                            })
                            cv2.rectangle(annotated, (bx, by), (bx + bw, by + bh), (0, 230, 115), 2)
                    count = len(detections)
                else:
                    st.error("No compatible model weights found in `models/` directory.")
                    return

            with col2:
                st.markdown("#### Detection Output")
                st.image(annotated, use_container_width=True, caption=f"Detected {count} Trees")

            # Metrics
            st.markdown("---")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Trees Detected", count)
            avg_conf = np.mean([d["confidence"] for d in detections]) if detections else 0.0
            m2.metric("Avg Confidence", f"{avg_conf:.1%}")

            # Density classification
            if count < 15:
                density = "🌱 Low Density"
            elif count < 45:
                density = "🌿 Medium Density"
            else:
                density = "🌳 High Canopy Density"
            m3.metric("Canopy Density", density)

            total_px = image.width * image.height
            est_tree_px = sum(d["area_px"] for d in detections)
            est_cover = min(100.0, (est_tree_px / total_px) * 100) if total_px > 0 else 0
            m4.metric("Est. Bounding Area", f"{est_cover:.1f}%")

            # Expandable table & CSV export
            if detections:
                with st.expander("📊 View Detection Coordinates & Export"):
                    df_det = pd.DataFrame(detections)
                    st.dataframe(df_det, use_container_width=True)
                    csv_data = df_det.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "📥 Download Detections (CSV)",
                        data=csv_data,
                        file_name="treesense_detections.csv",
                        mime="text/csv",
                    )
