import logging
from typing import Dict, Any, List
from app.ml.inference.detect import run_damage_detection

logger = logging.getLogger(__name__)


class MLService:
    @staticmethod
    def analyze_road_image(image_path: str) -> Dict[str, Any]:
        """
        Processes an image through the YOLO segmentation pipeline and produces
        structured results suitable for DB persistence and API responses, including
        itemized damage counts.
        """
        try:
            # Execute YOLO model inference
            result: Dict[str, Any] = run_damage_detection(image_path)

            detections: List[Dict[str, Any]] = result.get("detections", [])
            counts_by_type: Dict[str, int] = result.get("counts_by_type", {})
            processed_image_path: str | None = result.get("processed_image_path")

            if not detections:
                return {
                    "summary": "Normal (No Damage Detected)",
                    "damage_count": 0,
                    "counts_by_type": {},
                    "categories": [],
                    "detections": [],
                    "processed_image_path": processed_image_path
                }

            # Construct human-readable summary string (e.g. "3 Pothole(s), 2 Crack(s)")
            summary_parts = [f"{count} {label}(s)" for label, count in counts_by_type.items()]
            summary_str = ", ".join(summary_parts)

            return {
                "summary": summary_str,
                "damage_count": len(detections),      # Total count across all detected objects
                "counts_by_type": counts_by_type,     # Breakdown, e.g. {"Pothole": 3, "Crack": 2}
                "categories": list(counts_by_type.keys()),
                "detections": detections,             # List of {"label": str, "confidence": float, "bounding_box": [...]}
                "processed_image_path": processed_image_path
            }

        except Exception as e:
            logger.error(f"ML Processing Exception for image '{image_path}': {str(e)}", exc_info=True)
            return {
                "summary": "Unknown (Processing Error)",
                "damage_count": 0,
                "counts_by_type": {},
                "categories": [],
                "detections": [],
                "processed_image_path": None,
                "error": str(e)
            }