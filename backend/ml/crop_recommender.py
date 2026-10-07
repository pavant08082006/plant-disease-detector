"""
Crop Recommendation Engine.
Calculates agronomic suitability score based on soil chemistry (N, P, K, pH),
weather factors (temperature, humidity, rainfall), season, and soil texture.
Modular architecture designed for plug-and-play ML model integration.
"""

import json
from pathlib import Path
from typing import Dict, Any, List

from backend.utils.constants import DATA_DIR
from backend.utils.helpers import get_logger

logger = get_logger("CropRecommender")


class CropRecommender:
    """Agronomic recommendation engine."""

    def __init__(self, data_file: Path = None):
        self.data_file = data_file or (DATA_DIR / "crops_database.json")
        self.crops_data: Dict[str, Any] = {}
        self._load_database()

    def _load_database(self):
        """Loads crop agronomic profile standards."""
        if not self.data_file.exists():
            logger.warning(f"Crops database not found at {self.data_file}. Initializing defaults.")
            self.crops_data = {}
            return

        with open(self.data_file, "r", encoding="utf-8") as f:
            self.crops_data = json.load(f)

    @staticmethod
    def _score_parameter(val: float, val_range: List[float], weight: float) -> tuple[float, bool]:
        """Calculates suitability sub-score for a single environmental metric."""
        min_val, max_val = val_range
        tolerance = (max_val - min_val) * 0.35  # 35% margin for acceptable growth

        if min_val <= val <= max_val:
            return weight, True
        elif (min_val - tolerance) <= val < min_val:
            diff = min_val - val
            penalty = (diff / tolerance) * 0.4
            return weight * (1.0 - penalty), False
        elif max_val < val <= (max_val + tolerance):
            diff = val - max_val
            penalty = (diff / tolerance) * 0.4
            return weight * (1.0 - penalty), False
        else:
            return weight * 0.2, False

    def recommend(
        self,
        nitrogen: float,
        phosphorus: float,
        potassium: float,
        ph: float,
        temperature: float = 25.0,
        humidity: float = 65.0,
        rainfall: float = 750.0,
        season: str = "All",
        soil_type: str = "Loam",
        top_n: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Calculates multi-criteria suitability percentage and generates human-readable explanations.
        """
        recommendations = []

        # Feature Weights (total = 100)
        weights = {
            "n": 15.0,
            "p": 15.0,
            "k": 15.0,
            "ph": 15.0,
            "temp": 15.0,
            "humidity": 10.0,
            "rainfall": 15.0
        }

        for crop_name, spec in self.crops_data.items():
            score = 0.0
            reasons = []
            cautions = []

            # 1. Nitrogen
            n_score, n_in = self._score_parameter(nitrogen, spec["n_range"], weights["n"])
            score += n_score
            if n_in:
                reasons.append("optimal soil Nitrogen")
            elif nitrogen < spec["n_range"][0]:
                cautions.append("lower soil Nitrogen than preferred")

            # 2. Phosphorus
            p_score, p_in = self._score_parameter(phosphorus, spec["p_range"], weights["p"])
            score += p_score
            if p_in:
                reasons.append("balanced Phosphorus")

            # 3. Potassium
            k_score, k_in = self._score_parameter(potassium, spec["k_range"], weights["k"])
            score += k_score
            if k_in:
                reasons.append("adequate Potassium")

            # 4. pH
            ph_score, ph_in = self._score_parameter(ph, spec["ph_range"], weights["ph"])
            score += ph_score
            if ph_in:
                reasons.append(f"favorable soil pH ({ph:.1f})")
            else:
                cautions.append(f"pH ({ph:.1f}) differs from ideal {spec['ph_range'][0]}-{spec['ph_range'][1]}")

            # 5. Temperature
            t_score, t_in = self._score_parameter(temperature, spec["temp_range"], weights["temp"])
            score += t_score
            if t_in:
                reasons.append(f"suitable ambient temperature ({temperature:.0f}°C)")

            # 6. Humidity
            h_score, h_in = self._score_parameter(humidity, spec["humidity_range"], weights["humidity"])
            score += h_score

            # 7. Rainfall
            r_score, r_in = self._score_parameter(rainfall, spec["rainfall_range"], weights["rainfall"])
            score += r_score
            if r_in:
                reasons.append(f"compatible moisture/rainfall regime ({rainfall:.0f} mm)")

            # Bonus for Season Match
            if season in spec.get("suitable_seasons", []) or "All" in spec.get("suitable_seasons", []):
                score = min(100.0, score + 4.0)
                reasons.append(f"conducive season ({season})")
            else:
                score = max(20.0, score - 6.0)
                cautions.append(f"season '{season}' is outside normal sowing window")

            # Normalize final score between 25% and 98%
            suitability_pct = round(min(98.0, max(25.0, score)), 1)

            # Build readable explanation
            explanation = f"{crop_name} is recommended due to " + ", ".join(reasons[:3]) + "."
            if cautions:
                explanation += " Note: " + ", ".join(cautions[:2]) + "."

            recommendations.append({
                "crop": crop_name,
                "suitability": suitability_pct,
                "explanation": explanation,
                "description": spec.get("description", ""),
                "ideal_ph": f"{spec['ph_range'][0]} - {spec['ph_range'][1]}",
                "ideal_temp": f"{spec['temp_range'][0]} - {spec['temp_range'][1]}°C",
                "ideal_rainfall": f"{spec['rainfall_range'][0]} - {spec['rainfall_range'][1]} mm"
            })

        # Sort descending by suitability
        recommendations.sort(key=lambda x: x["suitability"], reverse=True)

        # Assign medals / rank
        ranks = ["🥇", "🥈", "🥉", "🏅"]
        for i, item in enumerate(recommendations[:top_n]):
            item["rank_badge"] = ranks[i] if i < len(ranks) else "•"

        return recommendations[:top_n]


_crop_recommender_instance = None

def get_crop_recommender() -> CropRecommender:
    """Returns singleton CropRecommender instance."""
    global _crop_recommender_instance
    if _crop_recommender_instance is None:
        _crop_recommender_instance = CropRecommender()
    return _crop_recommender_instance


def recommend_crops(**kwargs) -> List[Dict[str, Any]]:
    """Functional convenience helper."""
    recommender = get_crop_recommender()
    return recommender.recommend(**kwargs)

