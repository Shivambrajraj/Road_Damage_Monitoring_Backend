# app/services/ml_service.py
from app.ml.inference.detect import run_damage_detection

class MLService:
    @staticmethod
    def analyze_road_image(image_path: str):
        try:
            # Execute our YOLO model inference
            detections = run_damage_detection(image_path)
            
            if not detections:
                return "Normal" # No damage caught
            
            # Extract the unique names of detected issues
            categories = list(set([d["label"] for d in detections]))
            return ", ".join(categories)
            
        except Exception as e:
            print(f"ML Processing Exception: {str(e)}")
            return "Unknown (Processing Error)"