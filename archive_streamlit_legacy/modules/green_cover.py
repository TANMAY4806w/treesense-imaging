"""
Green Cover & Vegetation Index Analytics Module
Calculates canopy cover using scientific RGB spectral indices (VARI, GLI, Excess Green) and HSV segmentation.
"""

from typing import Tuple, Dict, Any
import numpy as np
import cv2
from PIL import Image
import streamlit as st


def compute_spectral_index(
    img_array: np.ndarray, method: str, threshold: float
) -> Tuple[np.ndarray, np.ndarray, float, float, Dict[str, Any]]:
    """
    Computes vegetation coverage using RGB spectral indices or color-space masks.
    Returns: overlay_rgb, mask, green_pct, non_green_pct, stats_dict
    """
    h, w = img_array.shape[:2]
    total_pixels = h * w

    # Convert to float normalized [0, 1]
    r = img_array[:, :, 0].astype(np.float32) / 255.0
    g = img_array[:, :, 1].astype(np.float32) / 255.0
    b = img_array[:, :, 2].astype(np.float32) / 255.0

    eps = 1e-6

    if method == "VARI (Visible Atmospherically Resistant)":
        # VARI = (Green - Red) / (Green + Red - Blue + eps)
        denom = g + r - b
        denom = np.where(np.abs(denom) < eps, eps, denom)
        idx_map = (g - r) / denom
        idx_map = np.clip(idx_map, -1.0, 1.0)
        mask = idx_map > threshold

    elif method == "GLI (Green Leaf Index)":
        # GLI = (2*G - R - B) / (2*G + R + B + eps)
        denom = 2 * g + r + b
        denom = np.where(denom < eps, eps, denom)
        idx_map = (2 * g - r - b) / denom
        idx_map = np.clip(idx_map, -1.0, 1.0)
        mask = idx_map > threshold

    elif method == "ExG (Excess Green)":
        # ExG = 2*g - r - b normalized by sum
        sum_rgb = r + g + b + eps
        rn, gn, bn = r / sum_rgb, g / sum_rgb, b / sum_rgb
        idx_map = 2 * gn - rn - bn
        mask = idx_map > threshold

    elif method == "HSV Color Space Segmentation":
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        # Standard vegetation range in OpenCV HSV: H: 30-90, S: 35-255, V: 35-255
        lower_green = np.array([30, int(threshold * 50), int(threshold * 40)])
        upper_green = np.array([90, 255, 255])
        mask = cv2.inRange(hsv, lower_green, upper_green) > 0
        idx_map = (hsv[:, :, 0].astype(np.float32) / 180.0)

    else:
        # Default Green Channel dominance
        mask = (g > (r * threshold)) & (g > (b * threshold))
        idx_map = g - np.maximum(r, b)

    green_pixels = int(np.sum(mask))
    green_pct = (green_pixels / total_pixels) * 100.0
    non_green_pct = 100.0 - green_pct

    # Create visual heatmap overlay
    norm_idx = cv2.normalize(idx_map, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    heatmap = cv2.applyColorMap(norm_idx, cv2.COLORMAP_SUMMER)
    heatmap_rgb = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)

    # Blend original image with vegetation highlight
    overlay = img_array.copy()
    overlay[mask] = (overlay[mask] * 0.4 + np.array([0, 230, 80]) * 0.6).astype(np.uint8)

    stats = {
        "Total Pixels Analyzed": total_pixels,
        "Vegetation Pixels": green_pixels,
        "Canopy Cover": f"{green_pct:.2f}%",
        "Barren / Non-Green": f"{non_green_pct:.2f}%",
        "Index Method": method,
        "Sensitivity Threshold": threshold,
    }

    return overlay, heatmap_rgb, green_pct, non_green_pct, stats


def show_upload_method():
    """Main Streamlit page for Green Cover & Spectral Vegetation Estimation."""
    st.title("🌿 Green Cover & Remote Sensing Vegetation Indices")
    st.markdown(
        "Analyze vegetation density, canopy fraction, and vegetative health using standard remote-sensing RGB indices."
    )

    with st.sidebar:
        st.markdown("---")
        st.markdown("### ⚙️ Spectral Analysis Settings")
        method = st.selectbox(
            "Vegetation Index Method",
            [
                "VARI (Visible Atmospherically Resistant)",
                "GLI (Green Leaf Index)",
                "ExG (Excess Green)",
                "HSV Color Space Segmentation",
            ],
            help="VARI and GLI are scientifically validated indices for standard RGB aerial photography."
        )

        default_thresh = 0.05 if "VARI" in method else (0.1 if "GLI" in method else (0.05 if "ExG" in method else 0.8))
        threshold = st.slider("Index Sensitivity Threshold", -0.5, 1.0, float(default_thresh), 0.02)

    uploaded_file = st.file_uploader(
        "Upload Aerial or Satellite Imagery",
        type=['png', 'jpg', 'jpeg'],
        help="Upload drone orthomosaics or satellite captures (RGB)"
    )

    if not uploaded_file:
        st.info("👆 Please upload an aerial image to analyze green cover.")
        return

    image = Image.open(uploaded_file).convert("RGB")
    img_np = np.array(image)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Original Image")
        st.image(image, use_container_width=True, caption=f"Input Image ({image.width}x{image.height} px)")

    if st.button("🔬 Compute Vegetation Coverage", type="primary", use_container_width=True):
        with st.spinner("Executing spectral calculations and spatial segmentation..."):
            overlay, heatmap, green_pct, non_green_pct, stats = compute_spectral_index(
                img_np, method, threshold
            )

        with col2:
            st.markdown("#### Canopy Segmentation Overlay")
            st.image(overlay, use_container_width=True, caption=f"Vegetation Mask ({green_pct:.1f}% Covered)")

        # Summary KPIs
        st.markdown("---")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Vegetation Canopy", f"{green_pct:.2f}%")
        m2.metric("Barren / Non-Green", f"{non_green_pct:.2f}%")
        
        status = "🌲 Dense Forest" if green_pct > 60 else ("🌿 Moderate Cover" if green_pct > 30 else "🌾 Sparse Cover")
        m3.metric("Ecological Classification", status)
        m4.metric("Active Index", method.split()[0])

        st.progress(green_pct / 100.0, text=f"Canopy Ratio: {green_pct:.1f}%")

        # Spectral Heatmap View
        st.markdown("---")
        st.markdown("#### 🗺️ Relative Vegetation Density Heatmap")
        st.image(heatmap, use_container_width=True, caption="Spectral Index Intensity Map (Higher = Denser Biomass)")

        with st.expander("📊 Detailed Pixel Telemetry"):
            st.json(stats)
