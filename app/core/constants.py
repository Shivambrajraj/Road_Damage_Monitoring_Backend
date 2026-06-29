# app/core/constants.py

# System Security Constants
MIN_PASSWORD_LENGTH = 8
ACCESS_TOKEN_TYPE = "bearer"

# Machine Learning & Media Validation Constants
YOLO_CANVAS_SIZE = 640
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
DEFAULT_STORAGE_PATH = "app/storage/uploads/original"

# Severity Prioritization Categories
SEVERITY_HIGH = "High"
SEVERITY_MEDIUM = "Medium"
SEVERITY_LOW = "Low"

# System Actions for Security Audit Logging
ACTION_LOGIN = "USER_LOGIN"
ACTION_REGISTRATION = "USER_REGISTRATION"
ACTION_SUBMIT_REPORT = "REPORT_SUBMISSION"
ACTION_UPDATE_NOTIFICATION = "NOTIFICATION_ACKNOWLEDGE"