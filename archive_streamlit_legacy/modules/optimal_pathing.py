

import streamlit as st
import os
import sys
from PIL import Image

# -----------------------------
# Add ForestPathPlanner to Python path
# -----------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FOREST_PATH_PLANNER_DIR = os.path.join(CURRENT_DIR, "..", "ForestPathPlanner")

if FOREST_PATH_PLANNER_DIR not in sys.path:
    sys.path.insert(0, FOREST_PATH_PLANNER_DIR)

# Import appOptim from ForestPathPlanner
try:
    import appOptim
except ImportError as e:
    st.error(f"❌ Could not import ForestPathPlanner.appOptim: {e}")
    raise e

# -----------------------------
# Streamlit Page Function
# -----------------------------
def show_optimal_pathing_page():
    st.title("🛪️ Smart Path Optimization")
    st.markdown(
        "🧮 **Advanced Route Planning** - Compute optimal paths through forested terrain "
        "using the ForestPathPlanner C++ backend."
    )

    method = st.selectbox(
        "Choose Pathfinding Method",
        ["📁 Upload Forest Image", "🎯 Coordinate-based Planning", "🗺️ Interactive Route Planning"]
    )

    if method == "📁 Upload Forest Image":
        show_image_based_pathing()
    else:
        st.warning("🚧 This feature is under development!")

# -----------------------------
# Image-Based Pathing Section
# -----------------------------
def show_image_based_pathing():
    st.markdown("### Forest Image Analysis & Path Planning")
    uploaded_file = st.file_uploader("Upload a forest image", type=['png', 'jpg', 'jpeg'])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Forest Area", use_container_width=True)

        st.markdown("### Set Start and End Points")
        col1, col2 = st.columns(2)
        with col1:
            start_x = st.number_input("Start X", min_value=0, max_value=image.width-1, value=50)
            start_y = st.number_input("Start Y", min_value=0, max_value=image.height-1, value=50)
        with col2:
            end_x = st.number_input("End X", min_value=0, max_value=image.width-1, value=image.width-50)
            end_y = st.number_input("End Y", min_value=0, max_value=image.height-1, value=image.height-50)

        if st.button("🗺️ Find Optimal Path"):
            with st.spinner("Calculating optimal path..."):
                try:
                    # Call the ForestPathPlanner C++ backend
                    result = appOptim.main_with_return(
                        image=image,
                        start=(start_x, start_y),
                        end=(end_x, end_y)
                    )
                    display_path_results(result)

                except Exception as e:
                    st.error(f"Error computing path: {str(e)}")

# -----------------------------
# Display Results Function
# -----------------------------
def display_path_results(result: dict):
    st.success("✅ Optimal path calculated!")

    col1, col2 = st.columns(2)
    with col1:
        st.image(result['path_image'], caption="Optimal Path", use_container_width=True)

    with col2:
        st.metric("Path Length", f"{result['path_length']:.1f} pixels")
        st.metric("Total Cost", f"{result['total_cost']:.1f}")
        st.metric("Green Coverage", f"{result['green_coverage']:.1f}%")
        st.metric("Open Areas", f"{result['idle_coverage']:.1f}%")
    
    if 'terrain_image' in result:
        st.image(result['terrain_image'], caption="Terrain Map", use_container_width=True)
    if 'cost_image' in result:
        st.image(result['cost_image'], caption="Cost Map", use_container_width=True)

