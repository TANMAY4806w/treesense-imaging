import streamlit as st
import numpy as np
from PIL import Image, ImageDraw
import cv2
import requests
import io
from typing import Tuple
import base64

def show_tree_count_page():
    """Tree detection, counting, and tree cover estimation page"""
    st.title("🌳 Tree Count & Cover Estimator")
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    
    if not uploaded_file:
        st.info("Please upload an image to detect trees.")
        return

    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    @st.cache_resource
    def load_model():
        if YOLO is not None:
            return YOLO("models/best.pt")  # Path to your trained YOLO model
        else:
            st.error("YOLO model not available. Please check your installation.")
            return None

    model = load_model()
    if model is not None:
        with st.spinner("Detecting trees..."):
            results = model(np.array(image))

        # Extract boxes and confidence
        boxes = results[0].boxes.xyxy.cpu().numpy() if results[0].boxes is not None else []
        confidences = results[0].boxes.conf.cpu().numpy() if results[0].boxes is not None else []

        img_np = np.array(image)
        total_area = img_np.shape[0] * img_np.shape[1]  # total pixels
        total_tree_area = 0

        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = box.astype(int)
            # Draw rectangle and label
            cv2.rectangle(img_np, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img_np, f"Tree {confidences[i]:.2f}", (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            # Add to total area
            total_tree_area += (x2 - x1) * (y2 - y1)

        # ✅ Calculate Tree Cover Percentage
        tree_cover_percent = (total_tree_area / total_area) * 100 if total_area > 0 else 0

        # Display results
        st.image(img_np, caption="Detected Trees", use_container_width=True)
        st.success(f"🌲 Number of trees detected: **{len(boxes)}**")
        st.metric("🟩 Tree Cover Percentage", f"{tree_cover_percent:.2f}%")

        # Density classification
        if len(boxes) < 10:
            st.info("Category: 🌱 Low Density Area")
        elif len(boxes) < 30:
            st.info("Category: 🌿 Medium Density Area")
        else:
            st.info("Category: 🌳 High Density Area")

        # Optional expandable detailed metrics
        with st.expander("📊 Detailed Metrics"):
            st.write({
                "Total Image Area (px²)": int(total_area),
                "Total Tree Area (px²)": int(total_tree_area),
                "Tree Cover (%)": round(tree_cover_percent, 2),
                "Detected Trees": len(boxes),
                "Model Used": "YOLO (ultralytics)"
            })
    else:
        st.error("Tree detection is not available due to missing dependencies.")


def show_upload_method():
    """Upload image method for green cover analysis"""
    
    st.markdown("### Upload Image Analysis")
    st.info("Upload a satellite or aerial image to analyze green cover percentage.")
    
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['png', 'jpg', 'jpeg'],
        help="Upload satellite imagery or aerial photos"
    )
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Analysis Settings")
        
        # Green threshold slider
        green_threshold = st.slider(
            "Green Sensitivity",
            min_value=0.5,
            max_value=2.5,
            value=1.5,
            step=0.1,
            help="Adjust sensitivity for green detection"
        )
        
        # Processing method
        method = st.selectbox(
            "Processing Method",
            ["Green Channel Analysis", "HSV Color Space", "NDVI Simulation"]
        )
        
        # Show analysis stats
        show_stats = st.checkbox("Show Detailed Statistics", value=True)
    
    with col2:
        if uploaded_file is not None:
            # Display original image
            image = Image.open(uploaded_file)
            st.markdown("### Original Image")
            st.image(image, caption="Original Image", use_container_width=True)
            
            if st.button("🔍 Analyze Green Cover", type="primary"):
                with st.spinner("Analyzing vegetation coverage..."):
                    # Analyze green cover
                    processed_image, green_percentage, idle_percentage, stats = analyze_green_cover(
                        image, green_threshold, method
                    )
                    
                    # Display results
                    st.success(f"✅ Analysis Complete!")
                    
                    # Show processed image
                    st.markdown("### Analysis Results")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.image(processed_image, caption="Green Cover Analysis", use_container_width=True)
                    
                    with col2:
                        # Metrics
                        st.metric("Green Cover", f"{green_percentage:.2f}%", 
                                 delta=f"{green_percentage - 50:.1f}% vs average")
                        st.metric("Idle/Non-Green Land", f"{idle_percentage:.2f}%")
                        st.metric("Total Pixels Analyzed", f"{stats['total_pixels']:,}")
                        
                        # Progress bars
                        st.markdown("#### Coverage Breakdown")
                        st.progress(green_percentage / 100, text=f"Green: {green_percentage:.1f}%")
                        st.progress(idle_percentage / 100, text=f"Non-Green: {idle_percentage:.1f}%")
                        
                        if show_stats:
                            st.markdown("#### Detailed Statistics")
                            st.json(stats)

def show_map_method():
    """Interactive map method (placeholder for Google Maps integration)"""
    
    st.markdown("### Interactive Map Analysis")
    st.warning("🚧 Interactive mapping feature coming soon!")
    
    st.markdown("""
    This feature will include:
    - Interactive Google Maps interface
    - Draw boundary selection tools
    - Real-time satellite imagery analysis
    - Location-based vegetation reports
    
    **For now, please use the Upload Image method above.**
    """)
    
    # Placeholder for coordinates input
    col1, col2 = st.columns(2)
    with col1:
        latitude = st.number_input("Latitude", value=23.2599, format="%.6f")
    with col2:
        longitude = st.number_input("Longitude", value=77.4126, format="%.6f")
    
    zoom_level = st.slider("Zoom Level", min_value=10, max_value=20, value=15)
    
    if st.button("📍 Analyze Location"):
        st.info("This feature requires Google Maps API integration. Please use the Upload Image method for now.")

def show_coordinates_method():
    """Custom coordinates method"""
    
    st.markdown("### Custom Coordinates Analysis")
    st.info("Enter specific coordinates to download and analyze satellite imagery.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Location Settings")
        latitude = st.number_input("Latitude", value=23.2599, format="%.6f", 
                                 help="Latitude in decimal degrees")
        longitude = st.number_input("Longitude", value=77.4126, format="%.6f",
                                  help="Longitude in decimal degrees")
        
    with col2:
        st.markdown("#### Image Settings")
        zoom_level = st.slider("Zoom Level", min_value=10, max_value=20, value=15,
                              help="Higher zoom = more detailed view")
        image_size = st.selectbox("Image Size", ["640x640", "800x800", "1024x1024"])
    
    if st.button("🛰️ Download & Analyze", type="primary"):
        st.warning("This feature requires satellite imagery API access. Please use the Upload Image method for full functionality.")

def analyze_green_cover(image: Image.Image, threshold_factor: float, method: str) -> Tuple[Image.Image, float, float, dict]:
    """
    Analyze green cover in the uploaded image
    """
    
    # Convert PIL image to numpy array
    img_array = np.array(image)
    original_shape = img_array.shape
    
    if method == "Green Channel Analysis":
        processed_img, green_pct, idle_pct, stats = green_channel_analysis(img_array, threshold_factor)
    elif method == "HSV Color Space":
        processed_img, green_pct, idle_pct, stats = hsv_analysis(img_array, threshold_factor)
    else:  # NDVI Simulation
        processed_img, green_pct, idle_pct, stats = ndvi_simulation(img_array, threshold_factor)
    
    # Convert back to PIL Image
    processed_image = Image.fromarray(processed_img)
    
    return processed_image, green_pct, idle_pct, stats

def green_channel_analysis(img_array: np.ndarray, threshold_factor: float) -> Tuple[np.ndarray, float, float, dict]:
    """
    Analyze green cover using green channel analysis
    """
    height, width = img_array.shape[:2]
    total_pixels = height * width
    
    # Extract green channel
    if len(img_array.shape) == 3:
        green_channel = img_array[:, :, 1].astype(np.float32)
    else:
        green_channel = img_array.astype(np.float32)
    
    # Calculate mean green value
    mean_green = np.mean(green_channel)
    
    # Create threshold
    threshold = mean_green / threshold_factor
    
    # Create binary mask
    green_mask = green_channel >= threshold
    
    # Count green pixels
    green_pixels = np.sum(green_mask)
    idle_pixels = total_pixels - green_pixels
    
    # Calculate percentages
    green_percentage = (green_pixels / total_pixels) * 100
    idle_percentage = (idle_pixels / total_pixels) * 100
    
    # Create visualization
    processed_img = np.zeros_like(img_array)
    if len(img_array.shape) == 3:
        processed_img[green_mask] = [0, 255, 0]  # Green for vegetation
        processed_img[~green_mask] = [128, 128, 128]  # Gray for non-vegetation
    else:
        processed_img[green_mask] = 255
        processed_img[~green_mask] = 128
    
    # Statistics
    stats = {
        "total_pixels": int(total_pixels),
        "green_pixels": int(green_pixels),
        "idle_pixels": int(idle_pixels),
        "mean_green_value": float(mean_green),
        "threshold_used": float(threshold),
        "method": "Green Channel Analysis"
    }
    
    return processed_img, green_percentage, idle_percentage, stats

def hsv_analysis(img_array: np.ndarray, threshold_factor: float) -> Tuple[np.ndarray, float, float, dict]:
    """
    Analyze green cover using HSV color space
    """
    height, width = img_array.shape[:2]
    total_pixels = height * width
    
    # Convert to HSV
    if len(img_array.shape) == 3:
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
    else:
        # If grayscale, convert to RGB first
        rgb_img = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
        hsv = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2HSV)
    
    # Define green range in HSV
    lower_green = np.array([35, 40, 40])  # Adjusted for vegetation
    upper_green = np.array([85, 255, 255])
    
    # Adjust range based on threshold factor
    saturation_min = max(20, 40 - (threshold_factor - 1) * 20)
    value_min = max(20, 40 - (threshold_factor - 1) * 20)
    
    lower_green[1] = int(saturation_min)
    lower_green[2] = int(value_min)
    
    # Create mask
    green_mask = cv2.inRange(hsv, lower_green, upper_green)
    green_mask = green_mask > 0
    
    # Count pixels
    green_pixels = np.sum(green_mask)
    idle_pixels = total_pixels - green_pixels
    
    # Calculate percentages
    green_percentage = (green_pixels / total_pixels) * 100
    idle_percentage = (idle_pixels / total_pixels) * 100
    
    # Create visualization
    processed_img = np.zeros_like(img_array)
    if len(processed_img.shape) == 3:
        processed_img[green_mask] = [0, 255, 0]  # Green
        processed_img[~green_mask] = [128, 128, 128]  # Gray
    else:
        processed_img[green_mask] = 255
        processed_img[~green_mask] = 128
    
    stats = {
        "total_pixels": int(total_pixels),
        "green_pixels": int(green_pixels),
        "idle_pixels": int(idle_pixels),
        "hsv_range_lower": lower_green.tolist(),
        "hsv_range_upper": upper_green.tolist(),
        "method": "HSV Color Space Analysis"
    }
    
    return processed_img, green_percentage, idle_percentage, stats

def ndvi_simulation(img_array: np.ndarray, threshold_factor: float) -> Tuple[np.ndarray, float, float, dict]:
    """
    Simulate NDVI analysis using RGB channels
    """
    height, width = img_array.shape[:2]
    total_pixels = height * width
    
    if len(img_array.shape) == 3:
        # Simulate NDVI using Red and Green channels
        red = img_array[:, :, 0].astype(np.float32)
        green = img_array[:, :, 1].astype(np.float32)
        
        # Avoid division by zero
        denominator = red + green
        denominator[denominator == 0] = 1
        
        # Calculate pseudo-NDVI
        ndvi = (green - red) / denominator
        
        # Adjust threshold based on factor
        threshold = 0.1 / threshold_factor
        
        # Create mask
        green_mask = ndvi > threshold
        
    else:
        # For grayscale, use simple thresholding
        gray = img_array.astype(np.float32)
        threshold = np.mean(gray) / threshold_factor
        green_mask = gray > threshold
        ndvi = gray  # For stats
    
    # Count pixels
    green_pixels = np.sum(green_mask)
    idle_pixels = total_pixels - green_pixels
    
    # Calculate percentages
    green_percentage = (green_pixels / total_pixels) * 100
    idle_percentage = (idle_pixels / total_pixels) * 100
    
    # Create visualization
    processed_img = np.zeros_like(img_array)
    if len(processed_img.shape) == 3:
        processed_img[green_mask] = [0, 255, 0]  # Green
        processed_img[~green_mask] = [128, 128, 128]  # Gray
    else:
        processed_img[green_mask] = 255
        processed_img[~green_mask] = 128
    
    stats = {
        "total_pixels": int(total_pixels),
        "green_pixels": int(green_pixels),
        "idle_pixels": int(idle_pixels),
        "mean_ndvi": float(np.mean(ndvi)) if len(img_array.shape) == 3 else None,
        "ndvi_threshold": float(threshold) if len(img_array.shape) == 3 else None,
        "method": "NDVI Simulation"
    }
    
    return processed_img, green_percentage, idle_percentage, stats

# Show tips at the bottom
if st.checkbox("💡 Analysis Tips"):
    st.markdown("""
    ### Green Cover Analysis Methods:
    
    **🌿 Green Channel Analysis**
    - Uses the green color channel intensity
    - Good for general vegetation detection
    - Fast processing
    
    **🎨 HSV Color Space**
    - Analyzes Hue, Saturation, and Value
    - More accurate for different lighting conditions
    - Better separation of green vegetation
    
    **📊 NDVI Simulation**
    - Simulates Normalized Difference Vegetation Index
    - Uses Red and Green channels
    - Most accurate for vegetation health assessment
    
    ### Tips for Better Results:
    - Use high-resolution satellite imagery
    - Ensure good lighting conditions
    - Adjust sensitivity based on vegetation density
    - Try different methods for comparison
    """)

