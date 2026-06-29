# app/utils/validators.py
from app.exceptions.reports import InvalidImageException
from app.core.constants import ALLOWED_IMAGE_EXTENSIONS  # Use centralized constants

class SystemValidator:
    @staticmethod
    def validate_image_extension(filename: str) -> None:
        """Ensures the uploaded file extension matches standard computer vision formats."""
        if not "." in filename:
            raise InvalidImageException(detail="File missing standard extension metadata.")
            
        ext = filename.rsplit(".", 1)[1].lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            raise InvalidImageException(
                detail=f"Unsupported file format .{ext}. Allowed formats: {ALLOWED_IMAGE_EXTENSIONS}"
            )

    @staticmethod
    def validate_coordinates(latitude: float | None, longitude: float | None) -> None:
        """Validates that incoming telemetry points fall inside actual global boundaries."""
        if latitude is not None and not (-90.0 <= latitude <= 90.0):
            raise ValueError("Latitude coordinates must be scaled strictly between -90 and 90 degrees.")
            
        if longitude is not None and not (-180.0 <= longitude <= 180.0):
            raise ValueError("Longitude coordinates must be scaled strictly between -180 and 180 degrees.")