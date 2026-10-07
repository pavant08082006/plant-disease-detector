"""
Utility functions for logging, image validation, and data formatting.
"""

import os
import logging
from pathlib import Path
from PIL import Image
import numpy as np
from backend.utils.constants import ALLOWED_EXTENSIONS, MAX_IMAGE_SIZE_MB, LOGS_DIR

# -----------------------------------------------------------------------------
# 1. Logging Configuration
# -----------------------------------------------------------------------------
def get_logger(name: str = "SmartAgriPartner") -> logging.Logger:
    """Configures and returns a centralized application logger."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / "app.log"
    
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # File handler
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
    return logger

logger = get_logger()

# -----------------------------------------------------------------------------
# 2. Image Validation & Preprocessing
# -----------------------------------------------------------------------------
def validate_image_file(file_obj, filename: str) -> tuple[bool, str]:
    """
    Validates uploaded file size and extension.
    Returns (is_valid, error_message).
    """
    if not filename:
        return False, "No file provided."
        
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file type (.{ext}). Allowed formats: JPG, JPEG, PNG."
        
    # Check size if available
    try:
        if hasattr(file_obj, "size"):
            size_mb = file_obj.size / (1024 * 1024)
            if size_mb > MAX_IMAGE_SIZE_MB:
                return False, f"File exceeds maximum allowed size of {MAX_IMAGE_SIZE_MB}MB."
    except Exception as e:
        logger.warning(f"Could not verify file size: {e}")
        
    return True, ""


def check_image_quality(image: Image.Image) -> tuple[bool, str]:
    """
    Performs basic image quality checks (brightness and contrast)
    to give actionable feedback to the farmer.
    """
    try:
        grayscale = image.convert("L")
        stat_array = np.array(grayscale)
        mean_brightness = float(np.mean(stat_array))
        contrast = float(np.std(stat_array))
        
        if mean_brightness < 25:
            return False, "The image appears too dark. Please take a photo in good natural lighting."
        if mean_brightness > 240:
            return False, "The image appears overexposed/washed out. Please avoid direct harsh glare."
        if contrast < 15:
            return False, "The image appears blurry or low contrast. Please ensure the camera is focused on the leaf."
            
        return True, "Good quality"
    except Exception as e:
        logger.warning(f"Quality check warning: {e}")
        return True, "Quality check skipped"


def format_currency(amount: float) -> str:
    """Formats float numbers as Indian Rupee strings, e.g., ₹24,500."""
    try:
        amount_int = int(round(amount))
        # Indian number grouping format
        s = str(amount_int)
        if len(s) <= 3:
            return f"₹{s}"
        last_three = s[-3:]
        remaining = s[:-3]
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        return f"₹{','.join(groups)},{last_three}"
    except Exception:
        return f"₹{amount:,.2f}"

