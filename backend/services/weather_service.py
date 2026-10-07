"""
Weather Service Module.
Provides live local weather observations, multi-day forecasts, and agricultural advisories.
Features automatic fallback to realistic demonstration datasets when in DEMO_MODE or offline.
"""

import os
import random
from typing import Dict, Any, List
import requests
from dotenv import load_dotenv

from backend.utils.helpers import get_logger

load_dotenv()
logger = get_logger("WeatherService")

# District coordinates mapping for popular agricultural hubs in India
DISTRICT_COORDINATES = {
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946, "state": "Karnataka"},
    "Kolar": {"lat": 13.1367, "lon": 78.1291, "state": "Karnataka"},
    "Belagavi": {"lat": 15.8497, "lon": 74.4977, "state": "Karnataka"},
    "Dharwad": {"lat": 15.4589, "lon": 75.0078, "state": "Karnataka"},
    "Mysuru": {"lat": 12.2958, "lon": 76.6394, "state": "Karnataka"},
    "Shivamogga": {"lat": 13.9299, "lon": 75.5681, "state": "Karnataka"},
    "Tumakuru": {"lat": 13.3409, "lon": 77.1010, "state": "Karnataka"},
    "Nashik": {"lat": 19.9975, "lon": 73.7898, "state": "Maharashtra"},
    "Pune": {"lat": 18.5204, "lon": 73.8567, "state": "Maharashtra"},
    "Nagpur": {"lat": 21.1458, "lon": 79.0882, "state": "Maharashtra"},
    "Agra": {"lat": 27.1767, "lon": 78.0081, "state": "Uttar Pradesh"},
    "Varanasi": {"lat": 25.3176, "lon": 82.9739, "state": "Uttar Pradesh"},
    "Ludhiana": {"lat": 30.9010, "lon": 75.8573, "state": "Punjab"},
    "Coimbatore": {"lat": 11.0168, "lon": 76.9558, "state": "Tamil Nadu"}
}


def generate_farming_advisories(temp: float, humidity: float, rain_mm: float, wind_kmh: float) -> List[Dict[str, str]]:
    """Generates conservative, actionable farming advisories based on meteorological metrics."""
    advisories = []

    if rain_mm > 15.0:
        advisories.append({
            "type": "rain",
            "icon": "🌧️",
            "title": "Heavy Rain Alert",
            "message": f"Rainfall expected ({rain_mm:.1f} mm). Postpone irrigation and fertilizer top-dressing to prevent nutrient leaching.",
            "severity": "warning"
        })
    elif rain_mm > 2.0:
        advisories.append({
            "type": "rain",
            "icon": "🌦️",
            "title": "Light Rain Expected",
            "message": "Moderate showers predicted. Hold off on foliar sprays to prevent wash-off.",
            "severity": "info"
        })
    else:
        advisories.append({
            "type": "irrigation",
            "icon": "💧",
            "title": "Irrigation Opportunity",
            "message": "Dry weather window. Safe for scheduled irrigation or planned field weeding.",
            "severity": "success"
        })

    if humidity >= 80.0 and temp >= 20.0:
        advisories.append({
            "type": "disease",
            "icon": "🍄",
            "title": "Fungal Risk Advisory",
            "message": f"High humidity ({humidity:.0f}%) and warm weather elevate fungal spore germination risk. Monitor lower canopy closely.",
            "severity": "warning"
        })

    if temp >= 36.0:
        advisories.append({
            "type": "heat",
            "icon": "🔥",
            "title": "Heat Stress Warning",
            "message": f"Elevated temperature ({temp:.1f}°C). Irrigate early morning or late evening to reduce flower drop and transpiration shock.",
            "severity": "warning"
        })
    elif temp < 12.0:
        advisories.append({
            "type": "cold",
            "icon": "❄️",
            "title": "Cool Weather Advisory",
            "message": f"Low ambient temperature ({temp:.1f}°C). Slow vegetative growth expected; avoid nitrogen surges.",
            "severity": "info"
        })

    if wind_kmh >= 30.0:
        advisories.append({
            "type": "wind",
            "icon": "💨",
            "title": "High Wind Speed",
            "message": f"Strong gusts ({wind_kmh:.1f} km/h). Avoid pesticide spraying (high drift hazard) and inspect crop trellising.",
            "severity": "warning"
        })

    return advisories


def get_mock_weather(city: str) -> Dict[str, Any]:
    """Provides realistic offline demonstration weather data."""
    # Deterministic seed based on city name for stable demo experience
    seed_val = sum(ord(c) for c in city)
    random.seed(seed_val)

    temp = round(random.uniform(24.0, 31.0), 1)
    humidity = round(random.uniform(55.0, 78.0), 1)
    wind_kmh = round(random.uniform(8.0, 18.0), 1)
    rain_mm = round(random.uniform(0.0, 8.0), 1)
    feels_like = round(temp + (1.2 if humidity > 60 else -0.5), 1)

    forecast = [
        {"day": "Today", "temp_max": temp + 2.0, "temp_min": temp - 5.0, "condition": "Partly Cloudy", "icon": "🌤️", "rain_chance": 20},
        {"day": "Tomorrow", "temp_max": temp + 1.5, "temp_min": temp - 4.5, "condition": "Passing Showers", "icon": "🌦️", "rain_chance": 45},
        {"day": "Day 3", "temp_max": temp + 3.0, "temp_min": temp - 4.0, "condition": "Sunny", "icon": "☀️", "rain_chance": 10},
        {"day": "Day 4", "temp_max": temp + 0.5, "temp_min": temp - 6.0, "condition": "Overcast", "icon": "☁️", "rain_chance": 35},
        {"day": "Day 5", "temp_max": temp + 2.0, "temp_min": temp - 5.5, "condition": "Light Rain", "icon": "🌧️", "rain_chance": 60}
    ]

    advisories = generate_farming_advisories(temp, humidity, rain_mm, wind_kmh)

    return {
        "city": city,
        "is_demo": True,
        "source": "Demo Simulation Engine (Offline Safe)",
        "current": {
            "temperature": temp,
            "feels_like": feels_like,
            "humidity": humidity,
            "wind_speed": wind_kmh,
            "rainfall": rain_mm,
            "condition": "Partly Cloudy" if rain_mm < 3.0 else "Light Showers",
            "icon": "🌤️" if rain_mm < 3.0 else "🌧️"
        },
        "forecast": forecast,
        "advisories": advisories
    }


def get_weather(city: str = "Bengaluru") -> Dict[str, Any]:
    """
    Fetches real-time weather via Open-Meteo free API (no API key required),
    falling back seamlessly to offline demo mode when necessary.
    """
    demo_mode_env = os.getenv("DEMO_MODE", "false").lower() == "true"
    coords = DISTRICT_COORDINATES.get(city, DISTRICT_COORDINATES["Bengaluru"])

    if demo_mode_env:
        return get_mock_weather(city)

    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={coords['lat']}&longitude={coords['lon']}&"
            f"current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m&"
            f"daily=temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max&"
            f"timezone=Asia%2FKolkata&forecast_days=5"
        )
        response = requests.get(url, timeout=4)
        if response.status_code == 200:
            data = response.json()
            curr = data.get("current", {})
            daily = data.get("daily", {})

            temp = round(curr.get("temperature_2m", 27.0), 1)
            humidity = round(curr.get("relative_humidity_2m", 60.0), 1)
            feels_like = round(curr.get("apparent_temperature", temp), 1)
            rain_mm = round(curr.get("precipitation", 0.0), 1)
            wind_kmh = round(curr.get("wind_speed_10m", 12.0), 1)

            # Map weather code to icon
            wcode = curr.get("weather_code", 0)
            if wcode in [0, 1]:
                cond, icon = "Clear / Sunny", "☀️"
            elif wcode in [2, 3]:
                cond, icon = "Partly Cloudy", "🌤️"
            elif wcode in [45, 48]:
                cond, icon = "Foggy", "🌫️"
            elif wcode in [51, 53, 55, 61, 63, 65]:
                cond, icon = "Rainy", "🌧️"
            elif wcode >= 80:
                cond, icon = "Showers / Thunderstorms", "⛈️"
            else:
                cond, icon = "Mild", "⛅"

            # Build 5-day forecast
            forecast = []
            days_labels = ["Today", "Tomorrow", "Day 3", "Day 4", "Day 5"]
            for i in range(min(5, len(daily.get("time", [])))):
                max_t = daily["temperature_2m_max"][i]
                min_t = daily["temperature_2m_min"][i]
                precip = daily["precipitation_sum"][i]
                prob = daily["precipitation_probability_max"][i]
                f_icon = "🌧️" if precip > 2.0 else "🌤️"
                forecast.append({
                    "day": days_labels[i],
                    "temp_max": round(max_t, 1),
                    "temp_min": round(min_t, 1),
                    "condition": f"Rain ({precip}mm)" if precip > 2.0 else "Partly Cloudy",
                    "icon": f_icon,
                    "rain_chance": int(prob or 0)
                })

            advisories = generate_farming_advisories(temp, humidity, rain_mm, wind_kmh)

            return {
                "city": city,
                "is_demo": False,
                "source": "Open-Meteo Live API",
                "current": {
                    "temperature": temp,
                    "feels_like": feels_like,
                    "humidity": humidity,
                    "wind_speed": wind_kmh,
                    "rainfall": rain_mm,
                    "condition": cond,
                    "icon": icon
                },
                "forecast": forecast,
                "advisories": advisories
            }
        else:
            logger.warning(f"Weather API status code {response.status_code}. Using fallback.")
            return get_mock_weather(city)

    except Exception as e:
        logger.warning(f"Live Weather fetch failed ({e}). Falling back to demo mode.")
        return get_mock_weather(city)

