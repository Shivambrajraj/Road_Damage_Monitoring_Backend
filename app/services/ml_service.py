import logging
from typing import Dict, Any, List
from app.ml.inference.detect import run_damage_detection

logger = logging.getLogger(__name__)


class MLService:
    @staticmethod
    def analyze_road_image(image_path: str) -> Dict[str, Any]:
        """
        Processes an image through the YOLO detection pipeline and produces
        structured results suitable for DB persistence and API responses.
        """
        try:
            # Execute YOLO model inference
            detections: List[Dict[str, Any]] = run_damage_detection(image_path)

            if not detections:
                return {
                    "summary": "Normal",
                    "damage_count": 0,
                    "categories": [],
                    "detections": []
                }

            # Extract unique damage categories
            categories = list(set([d["label"] for d in detections]))
            summary_str = ", ".join(categories)

            return {
                "summary": summary_str,
                "damage_count": len(detections),
                "categories": categories,
                "detections": detections  # List of {"label": str, "confidence": float}
            }

        except Exception as e:
            logger.error(f"ML Processing Exception for image '{image_path}': {str(e)}", exc_info=True)
            return {
                "summary": "Unknown (Processing Error)",
                "damage_count": 0,
                "categories": [],
                "detections": [],
                "error": str(e)
            }