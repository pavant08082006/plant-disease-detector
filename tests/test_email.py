"""
Unit test for Email Service and Test Report Generation.
"""

import unittest
from backend.services.email_service import get_smtp_config
from backend.services.report_generator import generate_pdf_report


class TestEmailAndReports(unittest.TestCase):

    def test_smtp_config_loaded(self):
        host, port, user, password = get_smtp_config()
        self.assertEqual(host, "smtp.gmail.com")
        self.assertEqual(port, 587)
        self.assertEqual(user, "Lokeshmmankith@gmail.com")
        self.assertGreater(len(password), 0)

    def test_pdf_report_generation(self):
        sample_payload = {
            "farmer": {
                "name": "Shri Basavaraj Gowda",
                "district": "Kolar",
                "state": "Karnataka",
                "land_area": 3.5,
                "primary_crop": "Tomato"
            },
            "disease": {
                "crop": "Tomato",
                "disease": "Early Blight",
                "confidence": 94.7,
                "confidence_level": "High",
                "status": "diseased",
                "guidance": {
                    "symptoms": ["Dark brown spots with concentric rings"],
                    "management": ["Prune bottom leaves and improve airflow"],
                    "safety_notice": "Consult local KVK."
                }
            },
            "soil": {"score": 78.0, "grade": "Good", "ph": 6.8, "nitrogen": 280, "phosphorus": 35, "potassium": 210},
            "weather": {"city": "Kolar", "current": {"temperature": 27.5, "condition": "Partly Cloudy", "humidity": 65, "rainfall": 0}},
            "mandi": {"commodity": "Tomato", "market": "Kolar APMC", "modal_price": 2450.0},
            "economic": {"total_expected_yield_qtl": 240, "lost_yield_qtl": 36, "loss_pct": 15, "estimated_income_loss": 79200}
        }
        pdf_bytes = generate_pdf_report(sample_payload)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 1000)
        # PDF files start with %PDF
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()

