import os
import time
import json
import cv2
import numpy as np
import torch
from ultralytics import YOLO

try:
    from sahi import AutoDetectionModel
    from sahi.predict import get_sliced_prediction
    SAHI_AVAILABLE = True
except ImportError:
    SAHI_AVAILABLE = False

BASE_DIR = r"c:\Users\TANMAY\OneDrive\Desktop\Resume\03_Projects\TreeSense_Imaging"
MODEL_PATH = os.path.join(BASE_DIR, "models", "best.pt")
SAMPLES_DIR = os.path.join(BASE_DIR, "evaluation", "test_samples")
OUTPUT_DIR = os.path.join(BASE_DIR, "evaluation", "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 65)
print("🌲 TreeSense AI - Comprehensive YOLOv11m Model Evaluation Engine")
print("=" * 65)

device = "cuda:0" if torch.cuda.is_available() else "cpu"
print(f"Device: {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")
print(f"Loading Model: {MODEL_PATH}")

model = YOLO(MODEL_PATH)

# Test images
test_images = [
    "tree1.jpg",
    "drone_mixed_canopy.jpg",
    "aerial_drone_forest_2.jpg"
]

evaluation_summary = {
    "model_info": {
        "architecture": "YOLOv11m",
        "task": "detect",
        "classes": model.names,
        "total_parameters": sum(p.numel() for p in model.model.parameters()),
        "trained_epochs": 50,
        "dataset_images": 1384
    },
    "benchmark_results": []
}

if SAHI_AVAILABLE:
    print("Initializing SAHI AutoDetectionModel...")
    sahi_model = AutoDetectionModel.from_pretrained(
        model_type='ultralytics',
        model_path=MODEL_PATH,
        confidence_threshold=0.25,
        device=device
    )

for img_name in test_images:
    img_path = os.path.join(SAMPLES_DIR, img_name)
    if not os.path.exists(img_path):
        print(f"Skipping {img_name} (not found)")
        continue

    print(f"\n🖼️  Processing Aerial Image: {img_name}")
    raw_img = cv2.imread(img_path)
    h, w, c = raw_img.shape
    file_size_kb = os.path.getsize(img_path) / 1024
    print(f"   Resolution: {w}x{h} px | Size: {file_size_kb:.1f} KB")

    # 1. Standard YOLOv11 inference
    t0 = time.time()
    results = model.predict(source=img_path, conf=0.25, device=device, verbose=False)
    yolo_latency_ms = (time.time() - t0) * 1000

    boxes = results[0].boxes
    det_count = len(boxes)
    confs = boxes.conf.cpu().numpy() if det_count > 0 else []
    avg_conf = float(np.mean(confs)) if len(confs) > 0 else 0.0

    print(f"   [Standard YOLOv11]")
    print(f"     Tree Crowns Detected: {det_count}")
    print(f"     Mean Confidence:     {avg_conf * 100:.1f}%")
    print(f"     Inference Latency:   {yolo_latency_ms:.1f} ms ({1000/yolo_latency_ms:.1f} FPS)")

    # Save standard prediction annotated visual
    annotated_std = results[0].plot()
    # Add status banner
    banner_text = f"TreeSense YOLOv11m | Detected: {det_count} Tree Crowns | Conf: {avg_conf*100:.1f}% | {yolo_latency_ms:.1f}ms"
    cv2.rectangle(annotated_std, (0, 0), (annotated_std.shape[1], 40), (20, 20, 20), -1)
    cv2.putText(annotated_std, banner_text, (20, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 127), 2)
    std_out_path = os.path.join(OUTPUT_DIR, f"std_{img_name}")
    cv2.imwrite(std_out_path, annotated_std)
    print(f"     Saved annotated view: {std_out_path}")

    # 2. SAHI Sliced Inference (for high-res imagery)
    sahi_result_data = None
    if SAHI_AVAILABLE:
        t0_sahi = time.time()
        sahi_pred = get_sliced_prediction(
            img_path,
            sahi_model,
            slice_height=512,
            slice_width=512,
            overlap_height_ratio=0.2,
            overlap_width_ratio=0.2,
            verbose=0
        )
        sahi_latency_ms = (time.time() - t0_sahi) * 1000
        sahi_count = len(sahi_pred.object_prediction_list)
        sahi_confs = [p.score.value for p in sahi_pred.object_prediction_list]
        sahi_avg_conf = float(np.mean(sahi_confs)) if sahi_confs else 0.0

        print(f"   [SAHI Sliced Inference (512x512 tiles, 20% overlap)]")
        print(f"     Tree Crowns Detected: {sahi_count}  (🚀 +{sahi_count - det_count} small crowns found)")
        print(f"     Mean Confidence:     {sahi_avg_conf * 100:.1f}%")
        print(f"     Total Sliced Latency:{sahi_latency_ms:.1f} ms")

        # Annotate SAHI
        annotated_sahi = raw_img.copy()
        for pred in sahi_pred.object_prediction_list:
            bbox = pred.bbox
            x1, y1, x2, y2 = int(bbox.minx), int(bbox.miny), int(bbox.maxx), int(bbox.maxy)
            cv2.rectangle(annotated_sahi, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        sahi_banner = f"TreeSense SAHI + YOLOv11m | High-Recall Crowns: {sahi_count} | Slice: 512x512"
        cv2.rectangle(annotated_sahi, (0, 0), (annotated_sahi.shape[1], 40), (20, 20, 20), -1)
        cv2.putText(annotated_sahi, sahi_banner, (20, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        sahi_out_path = os.path.join(OUTPUT_DIR, f"sahi_{img_name}")
        cv2.imwrite(sahi_out_path, annotated_sahi)
        print(f"     Saved SAHI view:      {sahi_out_path}")

        sahi_result_data = {
            "sahi_detections": sahi_count,
            "sahi_mean_conf": round(sahi_avg_conf, 4),
            "sahi_latency_ms": round(sahi_latency_ms, 1),
            "small_crown_gain": sahi_count - det_count
        }

    evaluation_summary["benchmark_results"].append({
        "image": img_name,
        "resolution": f"{w}x{h}",
        "file_size_kb": round(file_size_kb, 1),
        "standard_yolo11": {
            "detections": det_count,
            "mean_confidence": round(avg_conf, 4),
            "latency_ms": round(yolo_latency_ms, 1),
            "fps": round(1000 / max(yolo_latency_ms, 0.001), 1)
        },
        "sahi_inference": sahi_result_data
    })

# Save JSON report
report_path = os.path.join(BASE_DIR, "evaluation", "evaluation_report.json")
with open(report_path, "w") as f:
    json.dump(evaluation_summary, f, indent=2)

print("\n" + "=" * 65)
print(f"✅ EVALUATION COMPLETED SUCCESSFULLY!")
print(f"📄 Full JSON Metric Report: {report_path}")
print(f"🖼️  Visual Annotated Images Saved in: {OUTPUT_DIR}")
print("=" * 65)
