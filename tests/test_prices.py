"""
Unit tests for APMC Mandi Price Service.
"""

import unittest
from backend.services.mandi_service import get_mandi_prices, get_mandi_price_trend


class TestMandiService(unittest.TestCase):

    def test_fetch_prices(self):
        prices = get_mandi_prices(state="Karnataka", commodity="Tomato")
        self.assertIsInstance(prices, list)
        self.assertGreater(len(prices), 0)
        first = prices[0]
        self.assertIn("modal_price", first)
        self.assertIn("market", first)
        self.assertIn("commodity", first)
        self.assertGreater(first["modal_price"], 0)

    def test_price_trend(self):
        trend = get_mandi_price_trend(market="Kolar APMC", commodity="Tomato", days=7)
        self.assertEqual(len(trend), 7)
        for t in trend:
            self.assertIn("date", t)
            self.assertIn("modal_price", t)


if __name__ == "__main__":
    unittest.main()

