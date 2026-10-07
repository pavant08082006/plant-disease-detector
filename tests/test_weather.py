"""
Unit tests for Weather Service.
Validates weather fetching, mock fallback, and agricultural advisories.
"""

import unittest
from backend.services.weather_service import get_weather, generate_farming_advisories


class TestWeatherService(unittest.TestCase):

    def test_weather_fetch_structure(self):
        weather = get_weather("Bengaluru")
        self.assertIn("city", weather)
        self.assertIn("current", weather)
        self.assertIn("forecast", weather)
        self.assertIn("advisories", weather)

        curr = weather["current"]
        self.assertIn("temperature", curr)
        self.assertIn("humidity", curr)
        self.assertIn("wind_speed", curr)
        self.assertIn("rainfall", curr)

    def test_advisories_generation(self):
        # Heavy rain advisory
        adv_rain = generate_farming_advisories(temp=25.0, humidity=85.0, rain_mm=20.0, wind_kmh=10.0)
        types = [a["type"] for a in adv_rain]
        self.assertIn("rain", types)
        self.assertIn("disease", types)

        # High wind advisory
        adv_wind = generate_farming_advisories(temp=30.0, humidity=50.0, rain_mm=0.0, wind_kmh=35.0)
        types_wind = [a["type"] for a in adv_wind]
        self.assertIn("wind", types_wind)


if __name__ == "__main__":
    unittest.main()

