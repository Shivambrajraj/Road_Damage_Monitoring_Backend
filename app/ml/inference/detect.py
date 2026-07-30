"""
REAL DETECTION MODULE — Phase 2 (YOLO Integration)
==================================================
This module loads the trained YOLO model (`best.pt` or `road_damage.pt`)
and runs actual object detection on incoming image paths.

It maintains the existing return signature:
    [{"label": "Pothole", "confidence": 0.87}, ...]
so all downstream services (DB storage, severity scoring, maps)
continue working seamlessly.
"""

import os
import base64
from typing import List, Dict, Any
from ultralytics import YOLO

# Resolve path to weights file inside app/models/ (a sibling of app/ml/,
# NOT app/ml/models/ — that folder only ever held an empty 0-byte
# placeholder file, which is what was actually being loaded and crashing).
MODEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../models/road_damage.pt")
)
# Git-safe plain-text copy of the same weights (base64). Binary .pt files
# can get silently corrupted by git's CRLF/LF line-ending conversion on
# push/clone; a base64 text file is immune to that, so we always rebuild
# the real .pt from it here rather than trusting whatever binary made it
# through git.
MODEL_PATH_B64 = MODEL_PATH + ".b64"


def _ensure_model_file():
    """Always rebuild road_damage.pt from its base64 text copy, if that
    copy is present. We don't try to guess whether the committed binary
    is "corrupted enough" (e.g. by size) — corruption can leave the file
    at a normal size but with scrambled bytes, which a size check would
    miss entirely. The .b64 file is plain text and survives git/GitHub
    untouched, so it's always the trustworthy source when present."""
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


def run_damage_detection(image_path: str) -> List[Dict[str, Any]]:
    """
    Runs YOLO object detection on the provided image path.

    Parameters:
        image_path (str): Full filesystem path to the input image.

    Returns:
        List[Dict[str, Any]]: List of detected objects with 'label' and 'confidence'.
                              Example: [{"label": "Pothole", "confidence": 0.87}]
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at path: {image_path}")

    # Run YOLO inference
    results = model(image_path)

    detected_damages = []

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            label = model.names[class_id]
            confidence = float(box.conf[0])

            detected_damages.append({
                "label": label,
                "confidence": round(confidence, 2)
            })

    return detected_damages