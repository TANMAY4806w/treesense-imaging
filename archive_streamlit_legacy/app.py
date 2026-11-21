import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import cv2

# Handle YOLO import properly
try:
    from ultralytics import YOLO
except (ImportError, ModuleNotFoundError):
    YOLO = None
    st.warning("YOLO not available. Tree detection will be disabled.")

# from modules.green_cover import show_green_cover_page

from modules.optimal_pathing import show_optimal_pathing_page
from modules.historical_data import show_historical_data_page
from modules.change_detection import show as show_change_detection_page
from modules.green_cover import show_upload_method

# Configure page
st.set_page_config(
    page_title="TreeSense Imaging",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .main > div { padding-top: 0 !important; }
    #MainMenu, footer, header { visibility: hidden; }
    
    .hero-section {
        background: linear-gradient(135deg, #1a472a 0%, #2E8B57 50%, #3cb371 100%);
        padding: 3rem 2rem;
        border-radius: 24px;
        margin-bottom: 3rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(46, 139, 87, 0.3);
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        border-radius: 50%;
    }
    
    .hero-content { position: relative; z-index: 2; max-width: 1400px; margin: 0 auto; }
    
    .hero-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 2rem;
        margin-bottom: 2.5rem;
    }
    
    .hero-brand { display: flex; align-items: center; gap: 1.5rem; }
    
    .hero-icon {
        font-size: 4rem;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2));
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .hero-title {
        color: white;
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 0 4px 12px rgba(0,0,0,0.3);
        letter-spacing: -1px;
    }
    
    .hero-subtitle {
        color: rgba(255,255,255,0.95);
        font-size: 1.1rem;
        font-weight: 400;
        margin: 0.5rem 0 0 0;
        letter-spacing: 1px;
    }
    
    .hero-status {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        background: rgba(255,255,255,0.2);
        padding: 1rem 1.5rem;
        border-radius: 50px;
        backdrop-filter: blur(20px);
        border: 2px solid rgba(255,255,255,0.3);
    }
    
    .status-dot {
        width: 12px;
        height: 12px;
        background: #90EE90;
        border-radius: 50%;
        box-shadow: 0 0 15px #90EE90;
        animation: pulse-dot 2s ease-in-out infinite;
    }
    
    @keyframes pulse-dot {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    .status-text {
        color: white;
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    .hero-description {
        background: rgba(255,255,255,0.15);
        backdrop-filter: blur(20px);
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.25);
        margin-bottom: 2rem;
    }
    
    .hero-description p {
        color: white;
        font-size: 1.1rem;
        line-height: 1.8;
        margin: 0;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1.5rem;
    }
    
    .stat-card {
        background: rgba(255,255,255,0.15);
        backdrop-filter: blur(20px);
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.25);
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        background: rgba(255,255,255,0.22);
        transform: translateY(-5px);
    }
    
    .stat-number {
        color: white;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
    }
    
    .stat-label {
        color: rgba(255,255,255,0.9);
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .section-title {
        text-align: center;
        color: #1a472a;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 3rem 0 3rem 0;
        position: relative;
    }
    
    .section-title::after {
        content: '';
        display: block;
        width: 80px;
        height: 4px;
        background: linear-gradient(90deg, #2E8B57, #3cb371);
        margin: 1rem auto 0;
        border-radius: 2px;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin-bottom: 3rem;
    }
    
    .feature-card {
        background: white;
        padding: 2.5rem 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
        text-align: center;
        border: 1px solid rgba(46, 139, 87, 0.1);
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #2E8B57, #3cb371);
        transform: scaleX(0);
        transition: transform 0.4s ease;
    }
    
    .feature-card:hover::before { transform: scaleX(1); }
    
    .feature-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 60px rgba(46, 139, 87, 0.15);
    }
    
    .feature-icon {
        font-size: 3.5rem;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover .feature-icon { transform: scale(1.1); }
    
    .feature-title {
        color: #1a472a;
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .feature-description {
        color: #666;
        line-height: 1.7;
        font-size: 1rem;
    }
    
    .getting-started {
        background: linear-gradient(135deg, #f0f9f4 0%, #e8f5e9 100%);
        padding: 3rem;
        border-radius: 24px;
        margin: 3rem 0;
        border: 2px solid rgba(46, 139, 87, 0.15);
    }
    
    .getting-started h3 {
        color: #1a472a;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .tools-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
    }
    
    .tool-item {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        border-left: 4px solid #2E8B57;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
    }
    
    .tool-item:hover {
        transform: translateX(5px);
        box-shadow: 0 8px 30px rgba(46, 139, 87, 0.15);
    }
    
    .tool-item strong {
        color: #1a472a;
        font-size: 1.1rem;
        display: block;
        margin-bottom: 0.5rem;
    }
    
    .tool-item span {
        color: #555;
        font-size: 0.95rem;
        line-height: 1.6;
        display: block;
    }
    
    .modern-footer {
        margin-top: 5rem;
        padding: 3rem 0 2rem;
        border-top: 2px solid #e8f5e9;
        text-align: center;
    }
    
    .footer-divider {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 2rem;
    }
    
    .divider-line {
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, #2E8B57, #3cb371);
    }
    
    .footer-icon { font-size: 2rem; margin: 0 2rem; }
    
    .footer-title {
        color: #1a472a;
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .footer-subtitle { color: #666; margin-bottom: 2rem; }
    
    .footer-tags {
        display: flex;
        justify-content: center;
        gap: 1rem;
        flex-wrap: wrap;
        margin-bottom: 2rem;
    }
    
    .footer-tag {
        background: white;
        color: #2E8B57;
        padding: 0.6rem 1.5rem;
        border-radius: 25px;
        font-size: 0.9rem;
        border: 2px solid #e8f5e9;
        transition: all 0.3s ease;
    }
    
    .footer-tag:hover {
        background: #e8f5e9;
        transform: translateY(-2px);
    }
    
    .footer-copyright { color: #999; font-size: 0.9rem; }
    
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a1a 0%, #2d2d2d 100%);
        border-right: 2px solid #3d3d3d;
    }
    
    section[data-testid="stSidebar"] > div {
        padding-top: 2rem;
    }
    
    section[data-testid="stSidebar"] h3 {
        color: #90EE90 !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
        font-size: 1.3rem !important;
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: #e0e0e0 !important;
    }
    
    section[data-testid="stSidebar"] label {
        color: #e0e0e0 !important;
        font-weight: 600 !important;
    }
    
    section[data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: #2d2d2d !important;
        border: 1px solid #3d3d3d !important;
        color: #e0e0e0 !important;
    }
    
    section[data-testid="stSidebar"] option {
        background-color: #2d2d2d !important;
        color: #e0e0e0 !important;
    }
    
    @media (max-width: 768px) {
        .hero-title { font-size: 2rem; }
        .hero-header { flex-direction: column; text-align: center; }
        .stats-grid { grid-template-columns: repeat(2, 1fr); }
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.sidebar.markdown("### 🌳 TreeSense")
    
    page = st.sidebar.selectbox(
        "Navigation",
        ["🏠 Home", "🌳 Tree Count", "🌿 Green Cover Estimator", 
         "📊 Change Detection", "🛤️ Optimal Pathing", "📊 Historical Data"],  # Added Change Detection
        label_visibility="visible"
    )

    if page == "🏠 Home":
        show_home_page()
    elif page == "🌳 Tree Count":
        show_tree_count_page()
    elif page == "🌿 Green Cover Estimator":
        show_upload_method()

    # Added change detection page
    elif page == "📊 Change Detection":
        st.title("📊 Change Detection & Alert System")
        show_change_detection_page()
    # Removed species identifier page
    elif page == "🛤️ Optimal Pathing":
        st.title("🛤️ Optimal Pathing")
        show_optimal_pathing_page()
    elif page == "📊 Historical Data":
        st.title("📊 Historical Data")
        show_historical_data_page()


def show_home_page():
    """Enhanced Landing Page"""
    
    st.markdown("""
        <div class="hero-section">
            <div class="hero-content">
                <div class="hero-header">
                    <div class="hero-brand">
                        <div class="hero-icon">🌳</div>
                        <div>
                            <div class="hero-title">TreeSense Imaging</div>
                            <div class="hero-subtitle">Advanced Forest Analytics Platform</div>
                        </div>
                    </div>
                    <div class="hero-status">
                        <div class="status-dot"></div>
                        <span class="status-text">System Online</span>
                    </div>
                </div>
                <div class="hero-description">
                    <p>🌲 Comprehensive forest management platform leveraging cutting-edge AI and advanced analytics for accurate tree enumeration, vegetation analysis, and environmental insights supporting sustainable forest management decisions.</p>
                </div>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">94.5%</div>
                        <div class="stat-label">Accuracy</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">50K+</div>
                        <div class="stat-label">Trees Analyzed</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">&lt; 5s</div>
                        <div class="stat-label">Processing</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">24/7</div>
                        <div class="stat-label">Monitoring</div>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<h2 class="section-title">🚀 Platform Capabilities</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <h3 class="feature-title">AI-Powered Detection</h3>
                <p class="feature-description">State-of-the-art YOLO neural networks provide accurate tree detection and counting with real-time processing capabilities</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🌍</div>
                <h3 class="feature-title">Smart Vegetation Analysis</h3>
                <p class="feature-description">Advanced satellite imagery processing with multiple analysis methods including NDVI, HSV, and green channel analysis</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📈</div>
                <h3 class="feature-title">Intelligent Insights</h3>
                <p class="feature-description">Comprehensive analytics dashboard with historical trends, environmental correlations, and predictive insights</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="getting-started">
            <h3>🎯 Choose Your Analysis Tool</h3>
            <div class="tools-grid">
                <div class="tool-item">
                    <strong>🌳 Tree Detection</strong>
                    <span>AI-powered tree counting with confidence scoring and density classification</span>
                </div>
                <div class="tool-item">
                    <strong>🌿 Green Cover Analysis</strong>
                    <span>Multi-method vegetation coverage assessment with NDVI and HSV analysis</span>
                </div>
                <!-- Removed Interactive Mapping -->
                <div class="tool-item">
                    <strong>🛤️ Path Optimization</strong>
                    <span>Advanced pathfinding algorithms for efficient terrain navigation</span>
                </div>
                <div class="tool-item">
                    <strong>📊 Historical Analytics</strong>
                    <span>Environmental trends and correlation analysis with predictive modeling</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="modern-footer">
            <div class="footer-divider">
                <div class="divider-line"></div>
                <div class="footer-icon">🌳</div>
                <div class="divider-line"></div>
            </div>
            <h3 class="footer-title">TreeSense Imaging</h3>
            <p class="footer-subtitle">Advanced Forest Analytics Platform</p>
            <div class="footer-tags">
                <span class="footer-tag">AI-Powered</span>
                <span class="footer-tag">Real-time Analysis</span>
                <span class="footer-tag">Environmental Intelligence</span>
                <span class="footer-tag">Sustainable Solutions</span>
            </div>
            <p class="footer-copyright">© 2024 TreeSense Imaging | Powered by Streamlit & AI</p>
        </div>
    """, unsafe_allow_html=True)

def show_tree_count_page():
    """Tree detection and counting page"""
    st.title("🌳 Tree Count")
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    
    if not uploaded_file:
        st.info("Please upload an image to detect trees.")
        return

    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    @st.cache_resource
    def load_model():
        if YOLO is not None:
            return YOLO("models/best.pt")
        else:
            st.error("YOLO model not available. Please check your installation.")
            return None

    model = load_model()
    if model is not None:
        results = model(np.array(image))
        
        boxes = results[0].boxes.xyxy.cpu().numpy() if results[0].boxes is not None else []
        confidences = results[0].boxes.conf.cpu().numpy() if results[0].boxes is not None else []

        img_np = np.array(image)
        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = box.astype(int)
            cv2.rectangle(img_np, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img_np, f"Tree {confidences[i]:.2f}", (x1, y1-5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        st.image(img_np, caption="Detected Trees", use_container_width=True)
        st.success(f"🌲 Number of trees detected: **{len(boxes)}**")

        if len(boxes) < 10:
            st.info("Category: 🌱 Low density")
        elif len(boxes) < 30:
            st.info("Category: 🌿 Medium density")
        else:
            st.info("Category: 🌳 High density")
    else:
        st.error("Tree detection is not available due to missing dependencies.")

if __name__ == "__main__":
    main()