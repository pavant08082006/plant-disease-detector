"""
Disease Prediction Inference Engine.
Integrates the existing trained MobileNetV2 model for Plant Disease Detection.
Supports cached loading, robust image preprocessing, and structured diagnostic outputs.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Union
import numpy as np
from PIL import Image
import tensorflow as tf

from backend.utils.constants import (
    KERAS_MODEL_PATH,
    TFLITE_MODEL_PATH,
    CLASSES_PATH,
    IMAGE_SIZE,
    CONFIDENCE_HIGH_THRESHOLD,
    CONFIDENCE_MODERATE_THRESHOLD,
)
from backend.utils.helpers import get_logger, check_image_quality

logger = get_logger("DiseasePredictor")


def parse_class_label(raw_label: str) -> Dict[str, str]:
    """
    Parses a raw PlantVillage class name into clean crop and disease descriptions.
    Example: 'Tomato___Early_blight' -> {'crop': 'Tomato', 'disease': 'Early Blight', 'status': 'diseased'}
    """
    if "___" in raw_label:
        raw_crop, raw_disease = raw_label.split("___", 1)
    else:
        raw_crop, raw_disease = "Unknown", raw_label

    # Clean crop name
    crop = raw_crop.replace("_", " ").replace(",", "").strip()
    if "(including sour)" in crop.lower():
        crop = "Cherry (Sour)"
    elif "corn (maize)" in crop.lower():
        crop = "Corn (Maize)"
    elif "pepper bell" in crop.lower() or "pepper" in crop.lower():
        crop = "Bell Pepper"

    # Clean disease name
    is_healthy = "healthy" in raw_disease.lower()
    if is_healthy:
        disease = "Healthy"
        status = "healthy"
    else:
        status = "diseased"
        disease = raw_disease.replace("_", " ").strip()
        # Specific beautifications
        if "spider mites" in disease.lower():
            disease = "Spider Mites (Two-Spotted Spider Mite)"
        elif "yellow leaf curl" in disease.lower():
            disease = "Tomato Yellow Leaf Curl Virus"
        elif "mosaic virus" in disease.lower():
            disease = "Tomato Mosaic Virus"
        elif "haunglongbing" in disease.lower() or "citrus greening" in disease.lower():
            disease = "Huanglongbing (Citrus Greening)"
        elif "esca" in disease.lower():
            disease = "Esca (Black Measles)"
        elif "cercospora" in disease.lower():
            disease = "Cercospora / Gray Leaf Spot"
        else:
            disease = " ".join([word.capitalize() for word in disease.split()])

    return {
        "crop": crop,
        "disease": disease,
        "status": status,
        "raw_label": raw_label
    }


class DiseasePredictor:
    """Singleton inference wrapper for plant disease detection."""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DiseasePredictor, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_path: Union[str, Path] = None, classes_path: Union[str, Path] = None):
        if self._initialized:
            return

        self.model_path = Path(model_path) if model_path else KERAS_MODEL_PATH
        self.classes_path = Path(classes_path) if classes_path else CLASSES_PATH
        self.model = None
        self.class_names = []
        self._load_artifacts()
        self._initialized = True

    def _load_artifacts(self):
        """Loads class mapping and TensorFlow Keras model."""
        # 1. Load Classes
        if not self.classes_path.exists():
            raise FileNotFoundError(f"Classes file not found at: {self.classes_path}")

        with open(self.classes_path, "r", encoding="utf-8") as f:
            self.class_names = json.load(f)
        logger.info(f"Loaded {len(self.class_names)} disease classes successfully.")

        # 2. Load Model
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found at: {self.model_path}")

        try:
            logger.info(f"Loading Keras model from {self.model_path}...")
            self.model = tf.keras.models.load_model(str(self.model_path), compile=False)
            logger.info("Plant Disease Detection model loaded successfully into memory.")
        except Exception as e:
            logger.error(f"Failed to load Keras model: {e}")
            raise e

    def preprocess_image(self, image: Union[Image.Image, np.ndarray, str, Path]) -> np.ndarray:
        """
        Prepares input image for model inference.
        - Ensures RGB format
        - Resizes to (224, 224)
        - Converts to float32 NumPy array with batch dimension (1, 224, 224, 3)
        """
        if isinstance(image, (str, Path)):
            image = Image.open(image)
        elif isinstance(image, np.ndarray):
            image = Image.fromarray(image)

        if image.mode != "RGB":
            image = image.convert("RGB")

        # Resize preserving dimensions
        resized_img = image.resize(IMAGE_SIZE, Image.Resampling.BILINEAR)
        img_array = np.array(resized_img, dtype=np.float32)
        
        # Expand dims for batch: (1, 224, 224, 3)
        batch_array = np.expand_dims(img_array, axis=0)
        return batch_array

    def predict(self, image: Union[Image.Image, np.ndarray, str, Path], top_k: int = 3) -> Dict[str, Any]:
        """
        Executes disease diagnosis inference.
        Returns detailed prediction dictionary including confidence grading and top-k predictions.
        """
        if self.model is None or not self.class_names:
            raise RuntimeError("Model or classes not initialized.")

        # Optional quality inspection
        if isinstance(image, Image.Image):
            is_good_quality, quality_msg = check_image_quality(image)
        else:
            is_good_quality, quality_msg = True, "OK"

        input_tensor = self.preprocess_image(image)

        # Inference
        predictions = self.model.predict(input_tensor, verbose=0)[0]
        
        # Softmax safety check
        if np.sum(predictions) > 0:
            probabilities = predictions / np.sum(predictions)
        else:
            probabilities = predictions

        # Top-1 Index & Confidence
        top_idx = int(np.argmax(probabilities))
        top_raw_label = self.class_names[top_idx]
        top_confidence = float(probabilities[top_idx]) * 100.0

        # Confidence categorization
        if top_confidence >= CONFIDENCE_HIGH_THRESHOLD:
            confidence_level = "High"
            user_guidance = "Clear symptom detection. High model certainty."
        elif top_confidence >= CONFIDENCE_MODERATE_THRESHOLD:
            confidence_level = "Moderate"
            user_guidance = "Moderate certainty. Verify visual symptoms against the reference guide."
        else:
            confidence_level = "Low"
            user_guidance = "Low certainty. Please capture a clearer image of the affected leaf under good lighting."

        # Parse primary diagnosis
        primary_info = parse_class_label(top_raw_label)

        # Top-K predictions
        top_k_indices = np.argsort(probabilities)[::-1][:top_k]
        top_predictions: List[Dict[str, Any]] = []
        for idx in top_k_indices:
            raw_lbl = self.class_names[idx]
            info = parse_class_label(raw_lbl)
            top_predictions.append({
                "raw_label": raw_lbl,
                "crop": info["crop"],
                "disease": info["disease"],
                "status": info["status"],
                "confidence": round(float(probabilities[idx]) * 100.0, 2)
            })

        result = {
            "crop": primary_info["crop"],
            "disease": primary_info["disease"],
            "status": primary_info["status"],
            "raw_label": top_raw_label,
            "confidence": round(top_confidence, 2),
            "confidence_level": confidence_level,
            "user_guidance": user_guidance,
            "quality_feedback": quality_msg,
            "top_predictions": top_predictions
        }

        return result


# Global singleton helper
_predictor_instance = None

def get_disease_predictor() -> DiseasePredictor:
    """Returns the singleton DiseasePredictor instance."""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = DiseasePredictor()
    return _predictor_instance


def predict_disease(image: Union[Image.Image, np.ndarray, str, Path], top_k: int = 3) -> Dict[str, Any]:
    """Convenience functional API for disease prediction."""
    predictor = get_disease_predictor()
    return predictor.predict(image, top_k=top_k)

