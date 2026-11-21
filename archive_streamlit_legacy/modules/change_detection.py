"""
Change Detection & Deforestation Alert System
Compares bi-temporal aerial/satellite imagery to compute tree canopy delta and issue alerts.
"""

from pathlib import Path
import numpy as np
from PIL import Image
import streamlit as st

try:
    from ultralytics import YOLO
except (ImportError, ModuleNotFoundError):
    YOLO = None

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "best.pt"


def load_css():
    """Load custom dark-mode modern styles for change detection."""
    st.markdown("""
    <style>
        .header-title {
            font-size: 2.8rem;
            font-weight: 700;
            background: linear-gradient(135deg, #10b981 0%, #34d399 50%, #6ee7b7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 10px;
        }
        
        .header-subtitle {
            text-align: center;
            font-size: 1.05rem;
            color: #cbd5e1;
            margin-bottom: 30px;
            max-width: 700px;
            margin-left: auto;
            margin-right: auto;
        }
        
        .upload-box {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            border: 2px solid #475569;
            border-radius: 14px;
            padding: 24px;
            text-align: center;
            margin-bottom: 15px;
        }
        
        .upload-icon {
            font-size: 2.5rem;
            margin-bottom: 8px;
        }
        
        .upload-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #f1f5f9;
        }
        
        .upload-subtitle {
            font-size: 0.9rem;
            color: #94a3b8;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
            border: 1px solid #475569;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }
        
        .metric-label {
            font-size: 0.85rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }
        
        .metric-value {
            font-size: 2.2rem;
            font-weight: 700;
            color: #10b981;
            margin-bottom: 4px;
        }
        
        .metric-change {
            font-size: 0.95rem;
            color: #cbd5e1;
        }
        
        .alert-danger {
            background: linear-gradient(135deg, rgba(220, 38, 38, 0.15) 0%, rgba(127, 29, 29, 0.2) 100%);
            border: 2px solid #dc2626;
            color: #fca5a5 !important;
            padding: 16px 20px;
            border-radius: 12px;
            font-weight: 600;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .alert-success {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.2) 100%);
            border: 2px solid #10b981;
            color: #86efac !important;
            padding: 16px 20px;
            border-radius: 12px;
            font-weight: 600;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .section-title {
            font-size: 1.6rem;
            font-weight: 700;
            color: #f1f5f9;
            margin: 25px 0 15px 0;
        }
        
        .gallery-label {
            padding: 10px;
            background: #1e293b;
            font-weight: 600;
            color: #cbd5e1;
            text-align: center;
            border-radius: 8px 8px 0 0;
        }
    </style>
    """, unsafe_allow_html=True)


@st.cache_resource
def load_detection_model():
    """Load cached YOLOv8 model safely."""
    if YOLO is None:
        return None
    if not MODEL_PATH.exists():
        return None
    try:
        return YOLO(str(MODEL_PATH))
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None


def show_results(count_before: int, count_after: int):
    """Display metrics cards comparing Time A vs Time B."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Trees in Baseline</div>
                <div class="metric-value">{count_before}</div>
                <div class="metric-change">Time A (Reference)</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Trees in Monitoring</div>
                <div class="metric-value">{count_after}</div>
                <div class="metric-change">Time B (Current)</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        tree_delta = count_after - count_before
        percent_delta = ((count_after - count_before) / count_before) * 100 if count_before > 0 else 0
        delta_color = "#ef4444" if tree_delta < 0 else "#10b981"
        
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Net Canopy Change</div>
                <div class="metric-value" style="color: {delta_color};">{tree_delta:+d}</div>
                <div class="metric-change">{percent_delta:+.1f}% change</div>
            </div>
        """, unsafe_allow_html=True)
    
    return tree_delta, percent_delta


def show():
    """Main function to render Change Detection & Alert System page."""
    load_css()
    
    st.markdown('<div class="header-title">📊 Change Detection & Deforestation Alert</div>', unsafe_allow_html=True)
    st.markdown("""
        <div class="header-subtitle">
            Upload baseline (Time A) and monitoring (Time B) aerial imagery of the same area to evaluate canopy depletion and trigger ecological alerts.
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
            <div class="upload-box">
                <div class="upload-icon">📅</div>
                <div class="upload-title">Baseline Imagery</div>
                <div class="upload-subtitle">Time A (Historical / Pre-Event)</div>
            </div>
        """, unsafe_allow_html=True)
        before_image = st.file_uploader("Upload Baseline Image (Time A)", type=['png', 'jpg', 'jpeg'], key="cd_before")
    
    with col2:
        st.markdown("""
            <div class="upload-box">
                <div class="upload-icon">🛰️</div>
                <div class="upload-title">Monitoring Imagery</div>
                <div class="upload-subtitle">Time B (Recent / Post-Event)</div>
            </div>
        """, unsafe_allow_html=True)
        after_image = st.file_uploader("Upload Monitoring Image (Time B)", type=['png', 'jpg', 'jpeg'], key="cd_after")
    
    st.markdown("---")
    
    col_btn = st.columns([1, 2, 1])
    with col_btn[1]:
        analyze_button = st.button("🚀 Analyze & Compare Imagery", type="primary", use_container_width=True)
    
    if analyze_button:
        if before_image is None or after_image is None:
            st.error("❌ Please upload both Time A and Time B images to perform change detection.")
            return

        model = load_detection_model()
        if model is None:
            st.error("❌ Tree detection model weights not found in `models/best.pt`.")
            return

        before_img_pil = Image.open(before_image).convert('RGB')
        after_img_pil = Image.open(after_image).convert('RGB')

        before_np = np.array(before_img_pil)
        after_np = np.array(after_img_pil)

        with st.spinner("Analyzing multi-temporal canopy changes..."):
            results_before = model(before_np, verbose=False)
            count_before = len(results_before[0].boxes) if results_before[0].boxes is not None else 0

            results_after = model(after_np, verbose=False)
            count_after = len(results_after[0].boxes) if results_after[0].boxes is not None else 0

        st.success("✅ Multi-temporal analysis complete!")
        
        # Results metrics
        st.markdown('<div class="section-title">📈 Comparison Metrics</div>', unsafe_allow_html=True)
        tree_delta, percent_delta = show_results(count_before, count_after)
        
        # Alert thresholding
        st.markdown("---")
        if count_before > 0:
            if percent_delta <= -10.0:
                st.markdown(f"""
                    <div class="alert-danger">
                        🚨 CRITICAL ALERT: Significant tree canopy depletion detected! ({abs(percent_delta):.1f}% loss)
                    </div>
                """, unsafe_allow_html=True)
            elif percent_delta < 0.0:
                st.markdown(f"""
                    <div class="alert-danger" style="border-color: #f59e0b; color: #fde68a;">
                        ⚠️ WARNING: Minor canopy reduction detected ({abs(percent_delta):.1f}% loss).
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div class="alert-success">
                        ✔️ STABLE: No net canopy loss detected between observation intervals.
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("ℹ️ Baseline image had zero detected trees. Unable to compute depletion ratio.")

        # Visual Comparison
        st.markdown('<div class="section-title">🖼️ Visual Detections</div>', unsafe_allow_html=True)
        
        vis_before = results_before[0].plot()
        vis_after = results_after[0].plot()
        
        proof_col1, proof_col2 = st.columns(2)
        with proof_col1:
            st.markdown('<div class="gallery-label">Baseline (Time A) Annotations</div>', unsafe_allow_html=True)
            st.image(vis_before, use_container_width=True, channels="BGR")
        
        with proof_col2:
            st.markdown('<div class="gallery-label">Monitoring (Time B) Annotations</div>', unsafe_allow_html=True)
            st.image(vis_after, use_container_width=True, channels="BGR")
