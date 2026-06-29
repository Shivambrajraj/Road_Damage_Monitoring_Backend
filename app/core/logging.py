# app/core/logging.py
import logging
import sys
import os

# Create a dedicated directory logs/ under the project root
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "app.log")

def configure_logging() -> None:
    """Configures global logging format for both stream console and disk file output."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),                     # Outputs directly to terminal
            logging.FileHandler(LOG_FILE, encoding="utf-8")         # Saves permanently to logs/app.log
        ]
    )

# Instantiate a standard logger named for the core application scope
logger = logging.getLogger("road_damage_api")