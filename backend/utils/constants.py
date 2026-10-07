"""
Constants and application configuration parameters for Smart Agri-Partner.
"""

from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

# Model Artifact Paths
KERAS_MODEL_PATH = MODELS_DIR / "best_plant_model.keras"
TFLITE_MODEL_PATH = MODELS_DIR / "plant_disease_model.tflite"
CLASSES_PATH = MODELS_DIR / "class_names.json"
METADATA_PATH = MODELS_DIR / "model_metadata.json"

# Image Specifications
IMAGE_HEIGHT = 224
IMAGE_WIDTH = 224
IMAGE_SIZE = (IMAGE_HEIGHT, IMAGE_WIDTH)
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
MAX_IMAGE_SIZE_MB = 10

# Confidence Thresholds
CONFIDENCE_HIGH_THRESHOLD = 80.0
CONFIDENCE_MODERATE_THRESHOLD = 60.0

# Supported Languages
LANGUAGES = {
    "en": "English",
    "kn": "ಕನ್ನಡ (Kannada)",
    "hi": "हिन्दी (Hindi)"
}

# Soil Health Reference Ranges (Standard Agronomic Guidelines)
# Values represent typical topsoil requirements in kg/ha or units
SOIL_METRIC_RANGES = {
    "ph": {"low": 5.5, "optimal_min": 6.0, "optimal_max": 7.5, "high": 8.5, "unit": "pH"},
    "nitrogen": {"low": 140, "optimal_min": 280, "optimal_max": 560, "high": 700, "unit": "kg/ha"},
    "phosphorus": {"low": 10, "optimal_min": 23, "optimal_max": 56, "high": 80, "unit": "kg/ha"},
    "potassium": {"low": 110, "optimal_min": 145, "optimal_max": 340, "high": 450, "unit": "kg/ha"},
    "organic_carbon": {"low": 0.5, "optimal_min": 0.5, "optimal_max": 0.75, "high": 1.0, "unit": "%"},
    "moisture": {"low": 20.0, "optimal_min": 40.0, "optimal_max": 70.0, "high": 85.0, "unit": "%"},
    "ec": {"low": 0.5, "optimal_min": 0.8, "optimal_max": 2.0, "high": 3.0, "unit": "dS/m"}
}

# Common Crops Supported
PRIMARY_CROPS = [
    "Apple", "Blueberry", "Cherry", "Corn (Maize)", "Grape", 
    "Orange", "Peach", "Pepper (Bell)", "Potato", "Raspberry", 
    "Soybean", "Squash", "Strawberry", "Tomato", "Wheat", "Rice", "Cotton"
]

# Mandi Standard Commodities
MANDI_COMMODITIES = [
    "Tomato", "Potato", "Onion", "Maize", "Wheat", "Soybean", 
    "Rice", "Cotton", "Apple", "Grape", "Green Chilli"
]

# APMC Districts across States (Focus on Karnataka, Maharashtra, UP, etc.)
STATES_AND_DISTRICTS = {
    "Karnataka": ["Bengaluru", "Kolar", "Belagavi", "Dharwad", "Mysuru", "Shivamogga", "Tumakuru"],
    "Maharashtra": ["Nashik", "Pune", "Nagpur", "Solapur", "Kolhapur", "Ahmednagar"],
    "Uttar Pradesh": ["Agra", "Varanasi", "Lucknow", "Kanpur", "Meerut", "Prayagraj"],
    "Punjab": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda"],
    "Tamil Nadu": ["Coimbatore", "Madurai", "Salem", "Trichy", "Dindigul"]
}

