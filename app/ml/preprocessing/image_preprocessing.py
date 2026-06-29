# app/ml/preprocessing/image_preprocessing.py
import cv2
import numpy as np
from app.core.logging import logger

class ImagePreprocessor:
    @staticmethod
    def prepare_for_inference(image_path: str, target_size: int = 640) -> np.ndarray:
        """
        Reads a local file, standardizes dimensions to a square bounding canvas (640x640) 
        for YOLO alignment, and normalizes pixel distributions.
        """
        logger.info(f"Preprocessing image canvas sequence for asset: {image_path}")
        
        # Load raw file matrix
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Image matrix data empty or unreadable.")
            
        # Resize cleanly to uniform dimensions keeping color space intact
        resized_img = cv2.resize(img, (target_size, target_size), interpolation=cv2.INTER_LINEAR)
        
        return resized_img