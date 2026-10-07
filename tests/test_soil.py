"""
Unit tests for Soil Health and Crop Recommendation.
"""

import unittest
from backend.ml.soil_analyzer import analyze_soil_health, classify_metric
from backend.ml.crop_recommender import recommend_crops


class TestSoilAndCrop(unittest.TestCase):

    def test_classify_metric(self):
        res = classify_metric(6.8, "ph")
        self.assertEqual(res["status"], "Optimal")
        self.assertEqual(res["score"], 100)

        res_low = classify_metric(100.0, "nitrogen")
        self.assertEqual(res_low["status"], "Deficient")

    def test_soil_health_composite_score(self):
        result = analyze_soil_health(ph=6.8, nitrogen=280.0, phosphorus=35.0, potassium=210.0)
        self.assertIn("score", result)
        self.assertIn("grade", result)
        self.assertGreaterEqual(result["score"], 70.0)
        self.assertIn("radar_data", result)
        self.assertEqual(len(result["radar_data"]["categories"]), 6)

    def test_crop_recommendations(self):
        recs = recommend_crops(nitrogen=280.0, phosphorus=35.0, potassium=210.0, ph=6.8, top_n=3)
        self.assertEqual(len(recs), 3)
        for r in recs:
            self.assertIn("crop", r)
            self.assertIn("suitability", r)
            self.assertIn("explanation", r)
            self.assertGreater(r["suitability"], 0.0)


if __name__ == "__main__":
    unittest.main()

