

# import streamlit as st
# import numpy as np
# import cv2
# from PIL import Image, ImageDraw, ImageFont
# import onnxruntime as ort
# import io
# from typing import List, Tuple
# import time

# def show_historical_data_page():
#     """Tree detection and counting page"""
    
#     st.title("🌳 AI Tree Detection & Counting")
#     st.markdown("🤖 **Advanced Neural Network Analysis** - Upload satellite or aerial images to automatically detect and count trees with high precision using our YOLO ONNX model.")
    
#     # ✅ Local model configuration
#     MODEL_PATH = r"C:\Users\TANMAY\OneDrive\Desktop\streamlit-app_editted\models\best.onnx"   # <--- your local ONNX model
#     CONFIDENCE_THRESHOLD = 0.2
#     IOU_THRESHOLD = 0.7
    
#     # File uploader
#     uploaded_file = st.file_uploader(
#         "Choose an image file", 
#         type=['png', 'jpg', 'jpeg'],
#         help="Upload an aerial or satellite image of a forested area"
#     )
    
#     col1, col2 = st.columns([1, 2])
    
#     with col1:
#         st.markdown("### Settings")
#         confidence_threshold = st.slider(
#             "Confidence Threshold", 
#             min_value=0.1, 
#             max_value=0.9, 
#             value=CONFIDENCE_THRESHOLD,
#             step=0.05,
#             help="Minimum confidence score for tree detection"
#         )
        
#         iou_threshold = st.slider(
#             "IoU Threshold", 
#             min_value=0.3, 
#             max_value=0.9, 
#             value=IOU_THRESHOLD,
#             step=0.05,
#             help="Intersection over Union threshold for non-max suppression"
#         )
    
#     with col2:
#         if uploaded_file is not None:
#             # Display original image
#             image = Image.open(uploaded_file)
#             st.markdown("### Original Image")
#             st.image(image, caption="Uploaded Image", use_container_width=True)
            
#             # Process button
#             if st.button("🔍 Detect Trees", type="primary"):
#                 with st.spinner("Detecting trees... This may take a few moments."):
#                     try:
#                         detected_image, tree_count, detections = detect_trees(
#                             image, confidence_threshold, iou_threshold
#                         )
                        
#                         st.success(f"✅ Detection Complete! Found {tree_count} trees")
                        
#                         col1, col2 = st.columns(2)
                        
#                         with col1:
#                             st.markdown("### Detection Results")
#                             st.image(detected_image, caption=f"Detected {tree_count} Trees", use_container_width=True)
                        
#                         with col2:
#                             st.markdown("### Detection Statistics")
#                             st.metric("Total Trees Detected", tree_count)
#                             if detections:
#                                 st.metric("Average Confidence", f"{np.mean([d[5] for d in detections]):.2%}")
                            
#                             if st.checkbox("Show Detection Details"):
#                                 st.markdown("#### Individual Detections")
#                                 for i, (x1, y1, x2, y2, label, conf) in enumerate(detections):
#                                     st.write(f"Tree {i+1}: Confidence {conf:.2%}, Position ({int(x1)}, {int(y1)}, {int(x2)}, {int(y2)})")
                    
#                     except Exception as e:
#                         st.error(f"Error during detection: {str(e)}")

# def detect_trees(image: Image.Image, confidence_threshold: float, iou_threshold: float) -> Tuple[Image.Image, int, List]:
#     """
#     Detect trees in the uploaded image using ONNX model
#     """
#     input_tensor, img_width, img_height = prepare_input(image)
#     output = run_model(input_tensor)
#     detections = process_output(output, img_width, img_height, confidence_threshold, iou_threshold)
#     detected_image = draw_detections(image, detections)
#     return detected_image, len(detections), detections

# def prepare_input(image: Image.Image) -> Tuple[np.ndarray, int, int]:
#     img_width, img_height = image.size
#     resized_img = image.resize((640, 640))
#     img_array = np.array(resized_img)
    
#     if len(img_array.shape) == 3 and img_array.shape[2] == 3:
#         img_array = img_array.astype(np.float32) / 255.0
#         img_array = np.transpose(img_array, (2, 0, 1))  # HWC to CHW
#         img_array = np.expand_dims(img_array, axis=0)
    
#     return img_array, img_width, img_height

# @st.cache_resource
# def load_onnx_model():
#     """
#     ✅ Load local ONNX model with caching
#     """
#     try:
#         session = ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])
#         return session
#     except Exception as e:
#         st.error(f"Failed to load ONNX model: {str(e)}")
#         return None

# def run_model(input_tensor: np.ndarray) -> np.ndarray:
#     session = load_onnx_model()
#     if session is None:
#         raise Exception("Model could not be loaded")
#     input_name = session.get_inputs()[0].name
#     outputs = session.run(None, {input_name: input_tensor})
#     return outputs[0]

# def process_output(output: np.ndarray, img_width: int, img_height: int, confidence_threshold: float, iou_threshold: float) -> List:
#     boxes = []
#     # Assuming YOLOv5 single-class output
#     num_predictions = output.shape[2] if output.ndim == 3 else output.shape[1]
#     for i in range(num_predictions):
#         xc = output[0][0][i]
#         yc = output[0][1][i]
#         w = output[0][2][i]
#         h = output[0][3][i]
#         conf = output[0][4][i]
#         if conf >= confidence_threshold:
#             x1 = (xc - w/2) / 640 * img_width
#             y1 = (yc - h/2) / 640 * img_height
#             x2 = (xc + w/2) / 640 * img_width
#             y2 = (yc + h/2) / 640 * img_height
#             boxes.append([x1, y1, x2, y2, "tree", conf])
#     if len(boxes) > 0:
#         boxes = apply_nms(boxes, iou_threshold)
#     return boxes

# def apply_nms(boxes: List, iou_threshold: float) -> List:
#     if len(boxes) == 0:
#         return []
#     boxes = sorted(boxes, key=lambda x: x[5], reverse=True)
#     result = []
#     while boxes:
#         result.append(boxes[0])
#         boxes = [box for box in boxes[1:] if calculate_iou(boxes[0], box) < iou_threshold]
#     return result

# def calculate_iou(box1: List, box2: List) -> float:
#     x1_max = max(box1[0], box2[0])
#     y1_max = max(box1[1], box2[1])
#     x2_min = min(box1[2], box2[2])
#     y2_min = min(box1[3], box2[3])
#     if x2_min <= x1_max or y2_min <= y1_max:
#         return 0.0
#     inter = (x2_min - x1_max) * (y2_min - y1_max)
#     area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
#     area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
#     union = area1 + area2 - inter
#     return inter / union if union > 0 else 0.0

# def draw_detections(image: Image.Image, detections: List) -> Image.Image:
#     img_with_boxes = image.copy()
#     draw = ImageDraw.Draw(img_with_boxes)
#     try:
#         font = ImageFont.truetype("arial.ttf", 20)
#     except:
#         font = ImageFont.load_default()
#     for x1, y1, x2, y2, label, confidence in detections:
#         draw.rectangle([x1, y1, x2, y2], outline="lime", width=3)
#         text = f"{label} ({confidence:.2%})"
#         bbox = draw.textbbox((x1, y1), text, font=font)
#         text_width = bbox[2] - bbox[0]
#         text_height = bbox[3] - bbox[1]
#         draw.rectangle([x1, y1, x1 + text_width + 10, y1 + text_height + 5], fill="lime")
#         draw.text((x1 + 5, y1), text, fill="black", font=font)
#     return img_with_boxes

# # Tips section remains same
# if st.checkbox("💡 Show Tips & Examples"):
#     st.markdown("""
#     ### Tips for Better Results:
#     - Use **high-resolution** aerial/satellite images.
#     - JPG/PNG formats supported. Automatically resized to 640×640.
#     - Confidence ↓ = more detections (may include false), ↑ = more strict.
#     - IoU controls how overlapping boxes are filtered.
#     """)

import streamlit as st
import numpy as np
from PIL import Image
import cv2
import onnxruntime as ort

# ✅ Configuration
MODEL_PATH = r"C:\Users\TANMAY\OneDrive\Desktop\streamlit-app_editted\models\best.onnx"
CONFIDENCE_THRESHOLD = 0.2
IOU_THRESHOLD = 0.7  # optional if your model uses NMS

# --- Streamlit App ---
st.title("🌳 Tree-Based Green Cover Estimation")
st.markdown("Upload an aerial or satellite image, and the model will detect trees to estimate green cover percentage.")

# File uploader
uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_container_width=True)

    if st.button("Calculate Green Cover"):
        with st.spinner("Detecting trees and calculating green cover..."):
            
            def calculate_green_cover_yolo(image: Image.Image, model_path, conf_thresh=0.2):
                img = np.array(image)
                h, w = img.shape[:2]

                # Preprocess for model
                img_resized = cv2.resize(img, (640, 640))
                input_img = img_resized.astype(np.float32)/255.0
                input_img = np.transpose(input_img, (2,0,1))[np.newaxis,:,:,:]

                # Load ONNX model
                session = ort.InferenceSession(model_path)
                outputs = session.run(None, {session.get_inputs()[0].name: input_img})

                # Post-process (adjust if your ONNX outputs differently)
                # Assume outputs[0] = boxes, outputs[1] = scores, outputs[2] = class_ids
                boxes = np.array(outputs[0])
                scores = np.array(outputs[1])
                # class_ids = np.array(outputs[2])  # optional if multiple classes

                # Filter by confidence
                valid = scores > conf_thresh
                boxes = boxes[valid]

                # Rescale boxes to original image size
                scale_x = w / 640
                scale_y = h / 640
                boxes[:, [0,2]] = boxes[:, [0,2]] * scale_x
                boxes[:, [1,3]] = boxes[:, [1,3]] * scale_y

                # Compute total area of boxes
                tree_area = np.sum((boxes[:,2]-boxes[:,0]) * (boxes[:,3]-boxes[:,1]))
                total_area = h * w
                green_cover_pct = (tree_area / total_area) * 100

                # Annotate image
                annotated_img = np.array(image).copy()
                for box in boxes:
                    x1, y1, x2, y2 = map(int, box)
                    cv2.rectangle(annotated_img, (x1, y1), (x2, y2), (0,255,0), 2)

                annotated_img = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB)
                annotated_img = Image.fromarray(annotated_img)

                return green_cover_pct, annotated_img

            # Run calculation
            green_cover_pct, annotated_image = calculate_green_cover_yolo(image, MODEL_PATH, CONFIDENCE_THRESHOLD)

            st.success(f"🌿 Estimated Green Cover: {green_cover_pct:.2f}%")
            st.image(annotated_image, caption="Annotated Tree Detection", use_container_width=True)

st.markdown("---")
st.markdown("""
💡 **Note:** This method estimates green cover based on **tree area detected** by your model.  
- Overlapping trees may slightly overestimate coverage.  
- Works best with clear aerial or satellite images where trees are visible.  
""")

