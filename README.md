# 🌳 TreeSense Imaging - Advanced Forest Analytics Platform

A modern, interactive Streamlit application for comprehensive forest management and analysis. Features AI-powered tree detection, vegetation analysis, interactive mapping, and environmental insights with an enhanced, professional UI.

## 🚀 First-Time Setup

### Prerequisites
- Python 3.11 or higher
- pip package manager

### Step 1: Create Virtual Environment
```bash
py -3.11 -m venv venv
```

### Step 2: Activate Virtual Environment
```bash
.\venv\Scripts\Activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
streamlit run app.py
```

Your default browser should automatically open to: `http://localhost:8501`

## ▶️ Running Subsequent Times

After the initial setup, you only need to activate the virtual environment and run the application:

### Step 1: Activate Virtual Environment
```bash
.\venv\Scripts\Activate
```

### Step 2: Run the Application
```bash
streamlit run app.py
```

Your default browser should automatically open to: `http://localhost:8501`

## 🌟 Features

### 🌳 Tree Detection & Counting
- **AI-Powered Detection**: Uses YOLOv8 neural network with ONNX runtime
- **Real-time Processing**: Upload images and get instant tree counting results
- **Interactive Settings**: Adjustable confidence thresholds and IoU parameters
- **Detailed Analysis**: Confidence scores, bounding boxes, and detection statistics

### 🌿 Green Cover Estimator
- **Multiple Analysis Methods**: Green Channel Analysis, HSV Color Space, NDVI Simulation
- **Image Processing**: Advanced algorithms for vegetation coverage estimation
- **Comprehensive Statistics**: Detailed pixel analysis and coverage percentages
- **Visual Results**: Side-by-side comparison of original and processed images

### 🗺️ Species Identifier & Mapping
- **Interactive Maps**: Folium-based mapping with multiple tile layers
- **Location Analysis**: Click-to-analyze functionality for forest areas
- **Species Distribution**: Estimated species breakdown and biodiversity metrics
- **Regional Comparison**: Multi-zone forest health monitoring

### 🛤️ Optimal Pathing
- **Advanced Algorithms**: A*, Dijkstra, Greedy Best-First, and Simple Line pathfinding
- **Terrain Analysis**: Automated forest density and obstacle detection
- **Cost Mapping**: Customizable terrain traversal costs
- **Path Visualization**: Interactive path overlay on original images

### 📊 Historical Data Analysis
- **Weather Integration**: Historical weather data visualization
- **Forest Trends**: Long-term forest cover and biodiversity tracking
- **Environmental Correlations**: Multi-factor analysis and correlation matrices
- **Interactive Dashboards**: Plotly-powered charts and visualizations


## 🎯 Usage Guide

### Navigation
- Use the **sidebar** to switch between different analysis tools
- Each tool has dedicated settings and controls
- **Tips sections** provide detailed usage instructions

### Tree Detection
1. Select "🌳 Tree Count" from the sidebar
2. Upload an aerial or satellite image
3. Adjust confidence and IoU thresholds
4. Click "🔍 Detect Trees" to process
5. View results with bounding boxes and statistics

### Green Cover Analysis
1. Select "🌿 Green Cover Estimator"
2. Choose analysis method (Green Channel, HSV, or NDVI)
3. Upload satellite imagery
4. Adjust sensitivity settings
5. Analyze vegetation coverage percentages

### Interactive Mapping
1. Select "🗺️ Species Identifier & Mapping"
2. Configure map settings (location, zoom, style)
3. Click on map locations to analyze
4. View species distribution and forest health metrics

### Path Planning
1. Select "🛤️ Optimal Pathing"
2. Upload forest imagery
3. Set start and end coordinates
4. Choose pathfinding algorithm
5. Adjust terrain costs and preferences
6. Generate optimal routes

### Historical Analysis
1. Select "📊 Historical Data"
2. Choose data type (Weather/Forest/Environmental)
3. Configure location and date ranges
4. View trends and correlations




