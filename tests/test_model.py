"""
Unit test for Plant Disease Model Inference.
Tests model loading, image preprocessing, class mapping, and output schemas.
"""

import os
import unittest
from pathlib import Path
from PIL import Image
import numpy as np

from backend.ml.disease_predictor import DiseasePredictor, parse_class_label, predict_disease
from backend.utils.constants import KERAS_MODEL_PATH, CLASSES_PATH


class TestPlantDiseaseModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Verify model files exist and initialize predictor."""
        cls.assertTrue(os.path.exists(KERAS_MODEL_PATH), f"Model missing at {KERAS_MODEL_PATH}")
        cls.assertTrue(os.path.exists(CLASSES_PATH), f"Classes file missing at {CLASSES_PATH}")
        cls.predictor = DiseasePredictor()

    def test_class_names_count(self):
        """Model must have exactly 38 classes."""
        self.assertEqual(len(self.predictor.class_names), 38)
        self.assertIn("Tomato___Early_blight", self.predictor.class_names)
        self.assertIn("Apple___healthy", self.predictor.class_names)

    def test_label_parsing(self):
        """Ensure raw labels are parsed into clean human-readable dictionaries."""
        parsed = parse_class_label("Tomato___Early_blight")
        self.assertEqual(parsed["crop"], "Tomato")
        self.assertEqual(parsed["disease"], "Early Blight")
        self.assertEqual(parsed["status"], "diseased")

        parsed_healthy = parse_class_label("Apple___healthy")
        self.assertEqual(parsed_healthy["crop"], "Apple")
        self.assertEqual(parsed_healthy["disease"], "Healthy")
        self.assertEqual(parsed_healthy["status"], "healthy")

    def test_dummy_image_prediction_shape(self):
        """Ensure inference executes on synthetic RGB image without error."""
        dummy_img = Image.fromarray(np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8))
        result = self.predictor.predict(dummy_img, top_k=3)

        self.assertIn("crop", result)
        self.assertIn("disease", result)
        self.assertIn("confidence", result)
        self.assertIn("status", result)
        self.assertIn("top_predictions", result)
        self.assertEqual(len(result["top_predictions"]), 3)
        self.assertGreaterEqual(result["confidence"], 0.0)
        self.assertLessEqual(result["confidence"], 100.0)

    def test_real_sample_inference(self):
        """Test inference on a real PlantVillage dataset image if available."""
        dataset_sample_dir = Path("dataset/plantvillage dataset/color/Apple___Apple_scab")
        if dataset_sample_dir.exists():
            files = list(dataset_sample_dir.glob("*.JPG")) + list(dataset_sample_dir.glob("*.jpg"))
            if files:
                sample_path = files[0]
                result = predict_disease(sample_path, top_k=3)
                self.assertEqual(result["crop"], "Apple")
                self.assertGreater(result["confidence"], 50.0)
                print(f"\n[TEST PASS] Sample: {sample_path.name} -> Diagnosis: {result['disease']} ({result['confidence']}%)")


if __name__ == "__main__":
    unittest.main()

