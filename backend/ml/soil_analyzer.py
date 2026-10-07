"""
Soil Health Analyzer Engine.
Calculates Soil Health Score (0-100), classifies N-P-K-pH-OC metrics,
generates safe agronomic recommendations, and prepares radar chart data.
"""

from typing import Dict, Any, List
from backend.utils.constants import SOIL_METRIC_RANGES


def classify_metric(value: float, metric_key: str) -> Dict[str, Any]:
    """Classifies a given soil metric against benchmark agricultural ranges."""
    ranges = SOIL_METRIC_RANGES.get(metric_key)
    if not ranges:
        return {"status": "Unknown", "score": 70, "recommendation": "Maintain standard soil care."}

    low_bound = ranges["low"]
    opt_min = ranges["optimal_min"]
    opt_max = ranges["optimal_max"]
    high_bound = ranges["high"]
    unit = ranges["unit"]

    if value < low_bound:
        status = "Deficient"
        score = 40
        advisory = f"Level is significantly deficient (< {low_bound} {unit})."
    elif low_bound <= value < opt_min:
        status = "Low"
        score = 65
        advisory = f"Level is low. Sub-optimal for high-yield demand ({opt_min}-{opt_max} {unit} target)."
    elif opt_min <= value <= opt_max:
        status = "Optimal"
        score = 100
        advisory = f"Within ideal agronomic range ({opt_min}-{opt_max} {unit})."
    elif opt_max < value <= high_bound:
        status = "High"
        score = 75
        advisory = f"Level is above optimal target ({opt_min}-{opt_max} {unit})."
    else:
        status = "Excessive"
        score = 50
        advisory = f"Excessive level detected (> {high_bound} {unit}). May cause nutrient lockup."

    # Normalized score between 0 and 100 for radar plotting
    # Map opt_min -> 100, low_bound -> 50, etc.
    if value <= 0:
        radar_norm = 10
    elif value < opt_min:
        radar_norm = max(20, min(80, int((value / opt_min) * 80)))
    elif value <= opt_max:
        radar_norm = 100
    else:
        ratio = value / opt_max
        radar_norm = max(30, int(100 - (ratio - 1.0) * 40))

    return {
        "status": status,
        "score": score,
        "radar_norm": radar_norm,
        "advisory": advisory,
        "unit": unit
    }


def analyze_soil_health(
    ph: float = 6.8,
    nitrogen: float = 280.0,
    phosphorus: float = 35.0,
    potassium: float = 210.0,
    organic_carbon: float = 0.65,
    moisture: float = 55.0,
    temperature: float = 26.0,
    ec: float = 1.1
) -> Dict[str, Any]:
    """
    Evaluates complete soil health profile.
    Returns composite health score (0-100), metric breakdowns, and safe advisories.
    """
    metrics = {
        "ph": classify_metric(ph, "ph"),
        "nitrogen": classify_metric(nitrogen, "nitrogen"),
        "phosphorus": classify_metric(phosphorus, "phosphorus"),
        "potassium": classify_metric(potassium, "potassium"),
        "organic_carbon": classify_metric(organic_carbon, "organic_carbon"),
        "moisture": classify_metric(moisture, "moisture"),
        "ec": classify_metric(ec, "ec")
    }

    # Weighting factors for overall Soil Health Index
    weights = {
        "ph": 0.20,
        "nitrogen": 0.20,
        "phosphorus": 0.15,
        "potassium": 0.15,
        "organic_carbon": 0.15,
        "moisture": 0.10,
        "ec": 0.05
    }

    composite_score = sum(metrics[k]["score"] * weights[k] for k in weights)
    composite_score = round(composite_score, 1)

    if composite_score >= 80:
        grade = "Excellent (Fertile)"
        color = "#10B981"  # Emerald green
    elif composite_score >= 65:
        grade = "Moderate (Good)"
        color = "#3B82F6"  # Blue
    elif composite_score >= 50:
        grade = "Fair (Needs Care)"
        color = "#F59E0B"  # Amber
    else:
        grade = "Poor (Degraded)"
        color = "#EF4444"  # Red

    # Agronomic recommendations
    recommendations: List[str] = []

    # pH guidance
    if metrics["ph"]["status"] in ["Deficient", "Low"]:
        recommendations.append("Soil is acidic. Consider applying agricultural lime (calcium carbonate) or dolomite per local soil lab test.")
    elif metrics["ph"]["status"] in ["High", "Excessive"]:
        recommendations.append("Soil is alkaline. Incorporate organic matter (compost/FYM) or gypsum to improve nutrient availability.")
    else:
        recommendations.append("Soil pH is optimal for most horticulture and field crops.")

    # Nitrogen
    if metrics["nitrogen"]["status"] in ["Deficient", "Low"]:
        recommendations.append("Available Nitrogen is low. Incorporate well-decomposed Farm Yard Manure (FYM), compost, or green manuring with leguminous crops.")
    elif metrics["nitrogen"]["status"] == "Excessive":
        recommendations.append("High nitrogen detected. Avoid further nitrogenous inputs to prevent vegetative lodging and disease vulnerability.")

    # Phosphorus
    if metrics["phosphorus"]["status"] in ["Deficient", "Low"]:
        recommendations.append("Available Phosphorus is low. Apply organic compost or biofertilizers (PSB - Phosphorus Solubilizing Bacteria) to mobilize fixed soil phosphorus.")

    # Potassium
    if metrics["potassium"]["status"] in ["Deficient", "Low"]:
        recommendations.append("Potassium is below optimal. Ensure potash nutrition to enhance disease resistance and water stress tolerance.")

    # Organic Carbon
    if metrics["organic_carbon"]["status"] in ["Deficient", "Low"]:
        recommendations.append("Organic Carbon is low. Prioritize mulching, crop residue recycling, and vermicompost to revitalize soil microbial activity.")
    else:
        recommendations.append("Soil Organic Carbon content is healthy, promoting moisture retention and biological activity.")

    # Radar Chart Data
    radar_labels = ["Nitrogen (N)", "Phosphorus (P)", "Potassium (K)", "Soil pH", "Organic Carbon", "Moisture"]
    radar_values = [
        metrics["nitrogen"]["radar_norm"],
        metrics["phosphorus"]["radar_norm"],
        metrics["potassium"]["radar_norm"],
        metrics["ph"]["radar_norm"],
        metrics["organic_carbon"]["radar_norm"],
        metrics["moisture"]["radar_norm"],
    ]

    return {
        "score": composite_score,
        "grade": grade,
        "color": color,
        "raw_inputs": {
            "ph": ph, "nitrogen": nitrogen, "phosphorus": phosphorus,
            "potassium": potassium, "organic_carbon": organic_carbon,
            "moisture": moisture, "temperature": temperature, "ec": ec
        },
        "metrics": metrics,
        "recommendations": recommendations,
        "radar_data": {
            "categories": radar_labels,
            "values": radar_values
        }
    }

