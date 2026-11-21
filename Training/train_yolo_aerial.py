"""
TreeSense AI — Aerial Tree Crown Detection Training Pipeline
Optimized for Google Colab (T4 / A100 GPU) with Transfer Learning.
"""

import os
from pathlib import Path
from ultralytics import YOLO

def train_model(
    data_yaml: str,
    base_model: str = "yolov8m.pt",
    epochs: int = 80,
    imgsz: int = 1024,
    batch: int = 16,
    project_name: str = "treesense_training"
):
    print("=" * 60)
    print("🌲 TreeSense AI — Aerial Forestry Transfer Learning")
    print(f"Base Backbone : {base_model}")
    print(f"Image Resolution: {imgsz}x{imgsz} px")
    print(f"Epochs        : {epochs} | Batch: {batch}")
    print("=" * 60)

    # Load pretrained model (Transfer Learning)
    model = YOLO(base_model)

    # Train with aerial computer vision augmentations
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        patience=15,
        optimizer="AdamW",
        lr0=0.001,
        lrf=0.01,
        # Nadir Aerial View Augmentations
        degrees=180.0,
        flipud=0.5,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.15,
        project=project_name,
        name="aerial_tree_run",
        exist_ok=True,
        save=True
    )

    print("\n✅ Training complete! Evaluating on validation set...")
    metrics = model.val()
    print(f"🎯 Validation mAP@50    : {metrics.box.map50:.4f}")
    print(f"🎯 Validation mAP@50-95 : {metrics.box.map:.4f}")

    print("\n📦 Exporting model to ONNX FP16...")
    onnx_path = model.export(format="onnx", half=True, dynamic=True)
    print(f"🚀 Exported ONNX to: {onnx_path}")
    print("\nNext step: Copy 'best.pt' and 'best.onnx' into TreeSense_Imaging/models/")

if __name__ == "__main__":
    # Example usage:
    # Set your dataset data.yaml path here
    DATA_YAML_PATH = "data.yaml"
    if os.path.exists(DATA_YAML_PATH):
        train_model(data_yaml=DATA_YAML_PATH)
    else:
        print("💡 Place this script in Google Colab next to your unzipped dataset data.yaml and run:")
        print("   python train_yolo_aerial.py")
