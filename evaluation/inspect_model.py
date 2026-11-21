import os
import torch
from ultralytics import YOLO

model_path = r"c:\Users\TANMAY\OneDrive\Desktop\Resume\03_Projects\TreeSense_Imaging\models\best.pt"
print(f"Loading model from: {model_path}")

model = YOLO(model_path)
print("Task:", model.task)
print("Classes:", model.names)
total_params = sum(p.numel() for p in model.model.parameters())
print(f"Total Parameters: {total_params:,}")

# Check onnx model too
onnx_path = r"c:\Users\TANMAY\OneDrive\Desktop\Resume\03_Projects\TreeSense_Imaging\models\best.onnx"
print(f"ONNX Model exists: {os.path.exists(onnx_path)} ({os.path.getsize(onnx_path):,} bytes)")
