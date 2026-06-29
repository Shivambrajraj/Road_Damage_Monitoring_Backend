# app/ml/inference/detect.py
"""
PLACEHOLDER DETECTION MODULE — Phase 1 (website-first build)
==============================================================
This intentionally does NOT load a real YOLO model yet. The real
`road_damage.pt` weights aren't trained/exported yet, so this module
generates a plausible, structured detection result instead, in the
exact shape the real model will eventually return:

    [{"label": "Pothole", "confidence": 0.87}, ...]

This lets the rest of the system (DB storage, severity classification,
dashboard, map, analytics) be built and tested end-to-end right now.

PHASE 2 TODO (swap this out once you have a trained model):
  1. `pip install ultralytics` and add it back to requirements.txt
  2. Replace the body of `run_damage_detection` below with:

        from ultralytics import YOLO
        MODEL_PATH = "app/ml/models/road_damage.pt"
        model = YOLO(MODEL_PATH)
        results = model(image_path)
        detected_damages = []
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                label = model.names[class_id]
                confidence = float(box.conf[0])
                detected_damages.append({"label": label, "confidence": round(confidence, 2)})
        return detected_damages

  3. Delete the `random`-based logic below.
"""
import random

# Keep these labels in sync with ANOMALY_TYPES in the frontend's constants.js
DAMAGE_LABELS = ["Pothole", "Longitudinal Crack", "Rutting"]


def run_damage_detection(image_path: str):
    """
    MOCK implementation. Returns a small random set of plausible
    detections so the rest of the pipeline (severity scoring, DB
    storage, dashboard/analytics) has realistic data to work with.

    Real signature/behavior to preserve when swapping in YOLOv8:
    takes an image path, returns List[{"label": str, "confidence": float}]
    """
    num_detections = random.choices([0, 1, 2, 3], weights=[15, 35, 35, 15])[0]

    detections = []
    for _ in range(num_detections):
        label = random.choice(DAMAGE_LABELS)
        confidence = round(random.uniform(0.55, 0.97), 2)
        detections.append({"label": label, "confidence": confidence})

    return detections
