# 🌲 TreeSense AI — Production Model Training Guide (Google Colab)

## 🎯 Golden Rule: Transfer Learning vs Training From Scratch

| Parameter | Training from Scratch (❌ Avoid) | Pretrained Transfer Learning (⭐ Recommended) |
| :--- | :--- | :--- |
| **Initial Weights** | Random Gaussian noise ($\mathcal{N}(0, 1)$). | **MS COCO Pretrained Backbone (`yolov8m.pt` / `yolov11m.pt`)**. |
| **Dataset Needed** | $100,000+$ labeled images required. | **$1,500 - 5,000$ high-quality drone crops**. |
| **Compute Cost** | Days/weeks on multi-A100 clusters. | **$45 - 90$ minutes on free Google Colab T4 GPU**. |
| **Final Accuracy** | Severe overfitting ($<60\%$ mAP). | **$93\% - 97\%$ mAP with tight canopy localization**. |

---

## 🚀 4-Step Colab Execution

### Step 1: Open Google Colab & Select GPU
1. Go to [Google Colab](https://colab.research.google.com).
2. Click **Runtime** ➡️ **Change runtime type** ➡️ Select **T4 GPU** (16GB VRAM).

### Step 2: Install Ultralytics & Roboflow
```bash
!pip install ultralytics roboflow sahi onnx onnxruntime
```

### Step 3: Train YOLOv8 / YOLOv11 with Aerial-Specific Augmentations
```python
from ultralytics import YOLO

# 1. Load Pretrained Backbone (Transfer Learning)
model = YOLO("yolov8m.pt")  # or yolov11m.pt

# 2. Train with Aerial Hyperparameters
results = model.train(
    data="path/to/data.yaml",  # Roboflow Aerial Trees dataset
    epochs=80,
    imgsz=1024,              # High-resolution to capture small crowns
    batch=16,
    patience=15,             # Early stopping
    optimizer="AdamW",
    lr0=0.001,
    lrf=0.01,
    # Aerial Augmentations:
    degrees=180.0,           # Rotational invariance for drone nadir view
    flipud=0.5,
    fliplr=0.5,
    mosaic=1.0,
    mixup=0.15,
    device=0
)
```

### Step 4: Validate & Export to ONNX FP16
```python
# Validate mAP@50 and mAP@50-95
metrics = model.val()
print(f"mAP@50: {metrics.box.map50:.4f}")
print(f"mAP@50-95: {metrics.box.map:.4f}")

# Export to optimized ONNX FP16 for deployment
model.export(format="onnx", half=True, dynamic=True)
```

### Step 5: Deploy Model to TreeSense
1. Download `runs/detect/train/weights/best.pt` and `best.onnx`.
2. Replace the files in `TreeSense_Imaging/models/best.pt` and `models/best.onnx`.
3. Restart the FastAPI backend (`.\start_platform.bat`).
