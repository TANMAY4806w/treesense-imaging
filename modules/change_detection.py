# import streamlit as st
# from PIL import Image
# import numpy as np
# import cv2
# from ultralytics import YOLO

# # A function to load the model and cache it so it doesn't reload on every interaction
# @st.cache_resource
# def load_model():
#     """Loads the YOLOv8 model from the specified path."""
#     # Ensure the model path is correct, relative to your main app.py file
#     return YOLO("models/best.pt")

# def show():
#     """Main function to display the Change Detection page."""
    
#     st.title("📊 Change Detection & Alert System")
    
#     st.markdown("""
#     <div class="nav-description">
#         <div class="description-content">
#             <div class="description-main">
#                 <p>🛰️ Upload two satellite or drone images of the same area from different times. The system will analyze both, compare the tree counts, and trigger an alert if a significant loss in tree cover is detected.</p>
#             </div>
#         </div>
#     </div>
#     """, unsafe_allow_html=True)

#     # Create two columns for the file uploaders
#     col1, col2 = st.columns(2)

#     with col1:
#         before_image = st.file_uploader("Upload Baseline Image (Time A)", type=['png', 'jpg', 'jpeg'])

#     with col2:
#         after_image = st.file_uploader("Upload Monitoring Image (Time B)", type=['png', 'jpg', 'jpeg'])
    
#     # Add a horizontal line
#     st.markdown("---")

#     # Create a button to start the analysis
#     compare_button = st.button("🚀 Analyze & Compare Images", use_container_width=True)

#     # Load the YOLO model
#     model = load_model()

#     # This block runs when the user clicks the button AND has uploaded both files
#     if compare_button and before_image is not None and after_image is not None:
        
#         # Open uploaded files as PIL images
#         before_img_pil = Image.open(before_image)
#         after_img_pil = Image.open(after_image)
        
#         # Convert to RGB if they have an alpha channel (like PNGs)
#         if before_img_pil.mode != 'RGB':
#             before_img_pil = before_img_pil.convert('RGB')
#         if after_img_pil.mode != 'RGB':
#             after_img_pil = after_img_pil.convert('RGB')
            
#         # Convert PIL images to NumPy arrays for model processing
#         before_img_np = np.array(before_img_pil)
#         after_img_np = np.array(after_img_pil)

#         # --- Run the Analysis with a spinner for user feedback ---
#         with st.spinner("Analyzing images... This may take a moment."):
#             results_before = model(before_img_np, verbose=False)
#             count_before = len(results_before[0].boxes)
            
#             results_after = model(after_img_np, verbose=False)
#             count_after = len(results_after[0].boxes)

#         st.success("✅ Analysis complete!")
#         st.markdown("---")

#         # --- Display Results ---
#         st.header("📈 Comparison Results")
        
#         # Display counts using metric cards in columns
#         res_col1, res_col2, res_col3 = st.columns(3)
#         res_col1.metric("Trees in Baseline Image (Time A)", f"{count_before}")
#         res_col2.metric("Trees in Monitoring Image (Time B)", f"{count_after}")
        
#         # --- Trigger Alert Logic ---
#         if count_before > 0:
#             tree_loss = count_before - count_after
#             percent_loss = (tree_loss / count_before) * 100
            
#             res_col3.metric("Change", f"{tree_loss:+}", f"{percent_loss:.2f}%")

#             if percent_loss > 10.0: # Using a 10% threshold
#                 st.error(f"🚨 ALERT: Significant tree loss detected! ({percent_loss:.2f}% decrease)")
#             else:
#                 st.success("✔️ Status: No significant change detected.")
#         else:
#             st.info("Status: No trees were found in the baseline image to compare.")


#         # --- Show Visual Proof ---
#         st.header("🖼️ Visual Proof")
        
#         # Get images with bounding boxes drawn on them
#         img_before_with_boxes = results_before[0].plot()
#         img_after_with_boxes = results_after[0].plot()

#         # Display images side-by-side
#         proof_col1, proof_col2 = st.columns(2)
#         with proof_col1:
#             st.subheader("Baseline Image (Time A)")
#             # Use BGR channel order because YOLO's plot() function returns an OpenCV image
#             st.image(img_before_with_boxes, use_column_width=True, channels="BGR")
#         with proof_col2:
#             st.subheader("Monitoring Image (Time B)")
#             st.image(img_after_with_boxes, use_column_width=True, channels="BGR")

import streamlit as st
from PIL import Image
import numpy as np
import cv2
from ultralytics import YOLO

# Custom CSS for modern UI
def load_css():
    st.markdown("""
    <style>
        /* Main container */
        .main {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f2f4f 100%);
            color: #e2e8f0;
        }
        
        /* Header styling */
        .header-title {
            font-size: 3.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #10b981 0%, #34d399 50%, #6ee7b7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 10px;
        }
        
        .header-subtitle {
            text-align: center;
            font-size: 1.1rem;
            color: #cbd5e1;
            margin-bottom: 40px;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }
        
        /* Upload boxes */
        .upload-box {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            border: 2px solid #475569;
            border-radius: 16px;
            padding: 40px;
            text-align: center;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .upload-icon {
            font-size: 3.5rem;
            margin-bottom: 15px;
        }
        
        .upload-title {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 8px;
            color: #f1f5f9;
        }
        
        .upload-subtitle {
            font-size: 0.95rem;
            color: #94a3b8;
            margin-top: 8px;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
            color: white !important;
            border: none !important;
            padding: 18px 50px !important;
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            border-radius: 12px !important;
            cursor: pointer !important;
            width: 100% !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 10px 30px rgba(16, 185, 129, 0.3) !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 15px 40px rgba(16, 185, 129, 0.4) !important;
        }
        
        /* Metric cards */
        .metric-card {
            background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
            border: 1px solid #475569;
            border-radius: 12px;
            padding: 25px;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            border-color: #10b981;
            background: linear-gradient(135deg, #2d5555 0%, #1a3333 100%);
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(16, 185, 129, 0.1);
        }
        
        .metric-label {
            font-size: 0.9rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 10px;
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: #10b981;
            margin-bottom: 5px;
        }
        
        .metric-change {
            font-size: 1rem;
            color: #cbd5e1;
        }
        
        /* Alert boxes */
        .alert-danger {
            background: linear-gradient(135deg, rgba(220, 38, 38, 0.1) 0%, rgba(127, 29, 29, 0.1) 100%);
            border: 2px solid #dc2626;
            color: #fca5a5 !important;
            padding: 20px;
            border-radius: 12px;
            font-weight: 600;
            margin-bottom: 30px;
        }
        
        .alert-success {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
            border: 2px solid #10b981;
            color: #86efac !important;
            padding: 20px;
            border-radius: 12px;
            font-weight: 600;
            margin-bottom: 30px;
        }
        
        /* Section titles */
        .section-title {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 30px;
            color: #f1f5f9;
            margin-top: 40px;
        }
        
        /* Gallery items */
        .gallery-label {
            padding: 15px;
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            font-weight: 600;
            color: #cbd5e1;
            border-bottom: 1px solid #475569;
        }
    </style>
    """, unsafe_allow_html=True)

# Load and cache the model
@st.cache_resource
def load_model():
    """Loads the YOLOv8 model from the specified path."""
    return YOLO("models/best.pt")

def show_results(count_before, count_after):
    """Display results in beautiful cards"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Trees in Baseline</div>
                <div class="metric-value">{count_before}</div>
                <div class="metric-change">Time A</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Trees in Monitoring</div>
                <div class="metric-value">{count_after}</div>
                <div class="metric-change">Time B</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        tree_loss = count_before - count_after
        percent_loss = (tree_loss / count_before) * 100 if count_before > 0 else 0
        
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Change Detected</div>
                <div class="metric-value">{tree_loss:+}</div>
                <div class="metric-change">{percent_loss:.2f}%</div>
            </div>
        """, unsafe_allow_html=True)
    
    return tree_loss, percent_loss

def show():
    """Main function to display the Change Detection page."""
    
    # Load custom CSS
    load_css()
    
    # Header section
    st.markdown('<div class="header-title">🌳 TreeSense</div>', unsafe_allow_html=True)
    st.markdown("""
        <div class="header-subtitle">
            🛰️ Upload two satellite or drone images of the same area from different times. The system will analyze both, compare the tree counts, and trigger an alert if a significant loss in tree cover is detected.
        </div>
    """, unsafe_allow_html=True)
    
    # Upload section with two columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="upload-box">
                <div class="upload-icon">📷</div>
                <div class="upload-title">Baseline Image</div>
                <div class="upload-subtitle">Time A - Reference</div>
            </div>
        """, unsafe_allow_html=True)
        before_image = st.file_uploader("Upload Baseline Image (Time A)", type=['png', 'jpg', 'jpeg'], key="before")
    
    with col2:
        st.markdown("""
            <div class="upload-box">
                <div class="upload-icon">📷</div>
                <div class="upload-title">Monitoring Image</div>
                <div class="upload-subtitle">Time B - Current</div>
            </div>
        """, unsafe_allow_html=True)
        after_image = st.file_uploader("Upload Monitoring Image (Time B)", type=['png', 'jpg', 'jpeg'], key="after")
    
    st.markdown("---")
    
    # Analyze button centered
    col_btn = st.columns(3)
    with col_btn[1]:
        analyze_button = st.button("🚀 Analyze & Compare Images", use_container_width=True)
    
    # Load model
    model = load_model()
    
    # Analysis logic
    if analyze_button and before_image is not None and after_image is not None:
        
        # Open images and convert
        before_img_pil = Image.open(before_image)
        after_img_pil = Image.open(after_image)
        
        if before_img_pil.mode != 'RGB':
            before_img_pil = before_img_pil.convert('RGB')
        if after_img_pil.mode != 'RGB':
            after_img_pil = after_img_pil.convert('RGB')
        
        before_img_np = np.array(before_img_pil)
        after_img_np = np.array(after_img_pil)
        
        # Analysis with progress
        with st.spinner("🔍 Analyzing images... This may take a moment."):
            results_before = model(before_img_np, verbose=False)
            count_before = len(results_before[0].boxes)
            
            results_after = model(after_img_np, verbose=False)
            count_after = len(results_after[0].boxes)
        
        st.success("✅ Analysis complete!")
        st.markdown("---")
        
        # Results section
        st.markdown('<div class="section-title">📊 Comparison Results</div>', unsafe_allow_html=True)
        
        # Show metrics
        tree_loss, percent_loss = show_results(count_before, count_after)
        
        # Alert logic
        st.markdown("---")
        if count_before > 0:
            if percent_loss > 10.0:
                st.markdown(f"""
                    <div class="alert-danger">
                        🚨 ALERT: Significant tree loss detected! ({percent_loss:.2f}% decrease)
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div class="alert-success">
                        ✔️ Status: No significant change detected.
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("⚠️ Status: No trees were found in the baseline image to compare.")
        
        st.markdown("---")
        
        # Visual proof section
        st.markdown('<div class="section-title">🖼️ Visual Proof</div>', unsafe_allow_html=True)
        
        img_before_with_boxes = results_before[0].plot()
        img_after_with_boxes = results_after[0].plot()
        
        proof_col1, proof_col2 = st.columns(2)
        
        with proof_col1:
            st.markdown('<div class="gallery-label">Baseline Image (Time A)</div>', unsafe_allow_html=True)
            st.image(img_before_with_boxes, use_column_width=True, channels="BGR")
        
        with proof_col2:
            st.markdown('<div class="gallery-label">Monitoring Image (Time B)</div>', unsafe_allow_html=True)
            st.image(img_after_with_boxes, use_column_width=True, channels="BGR")
        
        # Summary section
        st.markdown("---")
        st.markdown('<div class="section-title">📋 Summary</div>', unsafe_allow_html=True)
        
        summary_col1, summary_col2, summary_col3 = st.columns(3)
        with summary_col1:
            st.metric("Total Loss", f"{tree_loss} trees")
        with summary_col2:
            st.metric("Loss Rate", f"{percent_loss:.2f}%")
        with summary_col3:
            status = "⚠️ ALERT" if percent_loss > 10.0 else "✔️ NORMAL"
            st.metric("Status", status)
    
    elif analyze_button:
        st.error("❌ Please upload both images before analyzing.")