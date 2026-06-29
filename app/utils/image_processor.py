# app/utils/image_processor.py
import cv2
from app.exceptions.reports import InvalidImageException

class ImageProcessor:
    @staticmethod
    def validate_and_read_image(file_path: str):
        """
        Uses OpenCV to read the saved file. Verifies the image is uncorrupted
        and can be parsed as a valid matrix of pixels.
        """
        image_matrix = cv2.imread(file_path)
        if image_matrix is None:
            raise InvalidImageException(detail="Failed to decode image file structure. File may be corrupted.")
        return image_matrix