"""
REAL DETECTION & SEGMENTATION MODULE — Phase 2 (YOLO Integration)
==================================================================
This module loads the trained YOLO segmentation model (`road_damage.pt`),
runs inference on incoming image paths, renders bounding boxes and masks,
saves the annotated output image, and returns detection details alongside 
itemized category counts.
"""

import os
import base64
import cv2
from typing import List, Dict, Any
from ultralytics import YOLO

# Resolve path to weights file inside app/models/
MODEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../models/road_damage.pt")
)
# Git-safe plain-text copy of the same weights (base64).
MODEL_PATH_B64 = MODEL_PATH + ".b64"


def _ensure_model_file():
    """Always rebuild road_damage.pt from its base64 text copy, if present."""
    if os.path.exists(MODEL_PATH_B64):
        with open(MODEL_PATH_B64, "r") as f:
            encoded = f.read()
        decoded = base64.b64decode(encoded.encode())
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        with open(MODEL_PATH, "wb") as f:
            f.write(decoded)
        print(f"[detect.py] Rebuilt {MODEL_PATH} from base64 copy ({len(decoded)} bytes).")
    elif not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Neither {MODEL_PATH} nor {MODEL_PATH_B64} was found — "
            "the model weights are missing from this deployment."
        )


_ensure_model_file()

# Load the model once when the application starts
model = YOLO(MODEL_PATH)


def run_damage_detection(image_path: str) -> Dict[str, Any]:
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at path: {image_path}")

    # 1. Run YOLO Segmentation Inference
    # conf=0.15 ensures lower-confidence predictions (like large/faint potholes) are captured
    # imgsz=640 matches the standard YOLO training canvas size
    results = model(image_path, conf=0.15, iou=0.45, imgsz=640)

    detected_damages = []
    counts_by_type = {}
    annotated_image_path = None

    for result in results:
        # 2. Extract bounding boxes, class labels, and confidence
        if result.boxes is not None:
            for box in result.boxes:
                class_id = int(box.cls[0])
                label = model.names[class_id]  # e.g., "Pothole", "Crack"
                confidence = float(box.conf[0])
                
                # Get bounding box coordinates [x1, y1, x2, y2]
                xyxy = box.xyxy[0].tolist()

                # Increment count per damage category
                counts_by_type[label] = counts_by_type.get(label, 0) + 1

                detected_damages.append({
                    "label": label,
                    "confidence": round(confidence, 2),
                    "bounding_box": [round(coord, 2) for coord in xyxy]
                })

        # 3. Render bounding boxes, labels, and segmentation masks
        annotated_array = result.plot(
            line_width=3,
            masks=True,
            boxes=True,
            labels=True,
            conf=True
        )

        # 4. Save the annotated image into the 'processed' directory
        directory, filename = os.path.split(image_path)
        processed_dir = os.path.join(directory, "..", "processed")
        os.makedirs(processed_dir, exist_ok=True)

        annotated_filename = f"annotated_{filename}"
        annotated_image_path = os.path.abspath(os.path.join(processed_dir, annotated_filename))

        # Write the annotated OpenCV image array to disk
        cv2.imwrite(annotated_image_path, annotated_array)

    return {
        "detections": detected_damages,
        "counts_by_type": counts_by_type,
        "processed_image_path": annotated_image_path
    }