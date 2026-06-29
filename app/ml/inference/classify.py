# app/ml/inference/classify.py
from typing import List, Dict

class SeverityClassifier:
    @staticmethod
    def calculate_priority_level(detections: List[Dict]) -> str:
        """
        Analyzes the volume and type of structural defects 
        to compute a critical response priority ranking.
        """
        if not detections:
            return "Low"  # Normal roads or negligible flaws
            
        pothole_count = sum(1 for d in detections if "pothole" in d["label"].lower())
        crack_count = sum(1 for d in detections if "crack" in d["label"].lower())
        
        # Urgency Escalation Rules Matrix
        if pothole_count >= 3 or (pothole_count > 0 and crack_count > 4):
            return "High"      # Imminent hazard requiring rapid intervention response
        elif pothole_count > 0 or crack_count >= 2:
            return "Medium"    # Notable deterioration present
            
        return "Low"