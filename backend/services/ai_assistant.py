"""
Farmer AI Assistant Engine.
Provides rule-based agronomic Q&A grounded in application data,
with safe fallback and plug-and-play LLM API integration readiness.
"""

import os
from typing import Dict, Any, List
from dotenv import load_dotenv

from backend.utils.helpers import get_logger

load_dotenv()
logger = get_logger("AIAssistant")

KNOWLEDGE_FAQ: List[Dict[str, Any]] = [
    {
        "keywords": ["nitrogen", "low nitrogen", "yellowing leaves", "urea"],
        "answer": (
            "🌱 **Low Soil Nitrogen:** Nitrogen is vital for chlorophyll synthesis and leaf development. "
            "Deficiency shows up as generalized yellowing of older lower leaves and stunted growth. "
            "**Safe Action:** Incorporate well-decomposed farmyard manure (FYM), vermicompost, or cultivate "
            "leguminous green manures (like sunn hemp or sesbania). Avoid excessive chemical nitrogen surges."
        )
    },
    {
        "keywords": ["phosphorus", "low phosphorus", "purple leaves"],
        "answer": (
            "🧪 **Phosphorus Deficiency:** Phosphorus drives root establishment, flowering, and seed formation. "
            "Deficiency often causes purplish tint on stems and underside of older leaves with poor root growth. "
            "**Safe Action:** Add well-rotted organic compost or inoculate with Phosphorus Solubilizing Bacteria (PSB) "
            "which mobilizes bound phosphorus in native soils."
        )
    },
    {
        "keywords": ["potassium", "potash", "leaf scorching"],
        "answer": (
            "🌾 **Potassium Status:** Potassium regulates plant water balance, stomatal conductance, and disease defense. "
            "Low levels cause brown scorching along leaf margins and weak stems prone to lodging. "
            "**Safe Action:** Apply organic mulch, wood ash in regulated small quantities, or balanced potash fertilizer."
        )
    },
    {
        "keywords": ["early blight", "tomato blight", "concentric rings"],
        "answer": (
            "🌿 **Tomato Early Blight (*Alternaria solani*):** Characterized by dark brown spots with concentric target-board rings, "
            "usually starting on the lowest leaves. "
            "**Non-Chemical Management:** 1. Prune bottom leaves 30 cm from the ground. 2. Mulch beds with straw to block soil splash. "
            "3. Water with drip irrigation early in the morning so foliage stays dry. 4. Never work in wet crops."
        )
    },
    {
        "keywords": ["late blight", "potato late blight", "water soaked"],
        "answer": (
            "⚠️ **Late Blight (*Phytophthora infestans*):** A fast-spreading destructive disease favored by cool, foggy/wet weather. "
            "Shows large dark greasy water-soaked spots with white fuzz on leaf undersides. "
            "**Urgent Advice:** Immediately remove and safely bag severely infected plants to protect healthy blocks. "
            "Contact your local Krishi Vigyan Kendra (KVK) promptly for regional emergency advisories."
        )
    },
    {
        "keywords": ["rain", "rain tomorrow", "weather forecast", "irrigation"],
        "answer": (
            "🌦️ **Weather & Irrigation Advisory:** Check our live Weather tab before watering! "
            "If rainfall (>5 mm) is expected in the next 24 hours, postpone field irrigation and top-dressing "
            "fertilizers to prevent expensive nutrient wash-off."
        )
    },
    {
        "keywords": ["maize", "planting maize", "corn"],
        "answer": (
            "🌽 **Maize Cultivation Tips:** Maize performs best in well-drained loamy soils with a pH of 6.0 to 7.5. "
            "Ensure adequate basal phosphorus and potassium during sowing. Avoid waterlogging during seedling emergence."
        )
    },
    {
        "keywords": ["price", "tomato price", "mandi", "rate"],
        "answer": (
            "📈 **Mandi Prices:** Please navigate to the **Mandi Prices** dashboard to view the latest APMC modal "
            "rates across Kolar, Bengaluru, Nashik, and other regional hubs with 7-day trend analysis."
        )
    },
    {
        "keywords": ["pesticide", "chemical", "dose", "spray"],
        "answer": (
            "🛡️ **Agricultural Safety Notice:** Smart Agri-Partner promotes Integrated Pest Management (IPM). "
            "We do not prescribe synthetic pesticide chemical dosages. Always consult your local certified agricultural "
            "officer or follow the CIBRC product label to ensure food safety and prevent pollinator harm."
        )
    }
]


def ask_assistant(user_query: str, context: Dict[str, Any] = None) -> str:
    """Processes farmer question and returns safe, helpful answer."""
    query_lower = user_query.strip().lower()
    if not query_lower:
        return "Please ask an agricultural question about crop diseases, soil health, weather, or market prices."

    # Keyword matching against agronomic knowledge bank
    best_match = None
    max_hits = 0

    for item in KNOWLEDGE_FAQ:
        hits = sum(1 for kw in item["keywords"] if kw in query_lower)
        if hits > max_hits:
            max_hits = hits
            best_match = item["answer"]

    if best_match and max_hits > 0:
        return best_match

    # General supportive answer
    return (
        f"🌾 **Agricultural Advisory:** Regarding your query on *'{user_query}'*:\n\n"
        "1. For leaf spots or discoloration, upload a photo in the **🌿 Disease Detection** tab for automated AI diagnosis.\n"
        "2. For fertilizer and nutrient recommendations, input your soil test values in the **🧪 Soil Health** tab.\n"
        "3. For market rates and selling decisions, view the **📈 Mandi Prices** tab.\n\n"
        "*Tip: Consult your local Krishi Vigyan Kendra (KVK) agricultural extension officer for regional agronomic recommendations.*"
    )

