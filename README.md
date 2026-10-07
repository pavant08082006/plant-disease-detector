# 🌾 SMART AGRI-PARTNER: AI APP FOR FARMERS
### *Farmer Friend – AI-Powered Smart Agriculture Assistant*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.21-orange.svg)](https://tensorflow.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.42%2B-red.svg)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/Database-SQLite%203-lightgrey.svg)](https://sqlite.org/)
[![License](https://img.shields.io/badge/Academic%20Project-AIML%20Major-brightgreen.svg)]()

---

## 📖 Executive Summary & Problem Statement

Smallholder farmers in India and developing agricultural economies confront compounding challenges:
1. **Delayed Crop Disease Diagnosis:** Foliar pathogens (fungi, bacteria, viruses) cause between 20% to 40% of pre-harvest yield losses annually. Farmers often lack direct, timely access to plant pathologists, leading to misdiagnoses and indiscriminate pesticide applications.
2. **Sub-optimal Nutrient Management:** Soil imbalance and incorrect N-P-K (Nitrogen, Phosphorus, Potassium) application degrade soil microbiomes, elevate cultivation costs, and restrict crop productivity.
3. **Information Asymmetry:** Farmers often make harvesting and marketing choices without localized weather alerts (rain wash-off risk) or wholesale APMC mandi price trend visibility.
4. **Economic Risk Exposure:** Without clear yield loss modeling, farmers cannot calculate whether protective agricultural interventions will safeguard net profits.

**SMART AGRI-PARTNER** bridges this gap by integrating a pre-trained **MobileNetV2 Deep Learning Plant Disease Classifier** into an integrated agronomic platform featuring soil health scoring, crop suitability recommendations, meteorological forecasting, APMC mandi rates, economic loss estimation, and multilingual advisory support (English and Kannada).

---

## 🎯 Project Objectives

- **Deep Learning Diagnosis:** Classify 38 disease and healthy states across 14 crops using fine-tuned transfer learning on MobileNetV2 with real-time confidence ratings and top-3 alternatives.
- **Explainable Agronomic Guidance:** Provide authoritative, non-chemical, cultural management practices (sanitation, leaf pruning, airflow, IPM) without prescribing hazardous synthetic chemicals.
- **Soil Fertility Index:** Compute an interactive Soil Health Index (0–100) using multi-parameter classification (pH, N, P, K, Organic Carbon, Moisture) paired with dynamic Plotly radar visualizations.
- **Multi-Criteria Crop Recommendation:** Recommend crops aligned with soil fertility, moisture availability, and seasonal rainfall.
- **Localized Weather & Risk Advisories:** Issue automated meteorological warnings (irrigation windows, fungal spore humidity risk, heat stress, wind drift hazard).
- **Mandi Market Visibility:** Monitor daily APMC wholesale modal, minimum, and maximum prices alongside 7-day trend analysis.
- **Economic Loss Estimation:** Model potential financial loss and yield reduction to support informed risk mitigation.
- **Multilingual Inclusivity:** Support English and Kannada (ಕನ್ನಡ), with modular architecture ready for Hindi and other regional languages.
- **Offline Demonstration Mode (`DEMO_MODE=true`):** Ensure seamless demonstration in academic settings without internet or live API dependencies.

---

## 🏛️ System Architecture

```text
                                 +-----------------------+
                                 |        FARMER         |
                                 +-----------+-----------+
                                             |
                                             v
                           +-----------------------------------+
                           |    SMART AGRI-PARTNER UI          |
                           |   (Streamlit / Responsive CSS)    |
                           +-----------------+-----------------+
                                             |
       +--------------------+----------------+-------------------+--------------------+
       |                    |                |                   |                    |
       v                    v                v                   v                    v
+--------------+    +--------------+  +--------------+   +---------------+   +------------------+
|   Disease    |    |     Soil     |  |   Weather    |   |  Mandi Price  |   |  Economic Loss   |
|  Detection   |    |    Health    |  |   Service    |   |    Service    |   |    Calculator    |
+------+-------+    +-------+------+  +-------+------+   +-------+-------+   +--------+---------+
       |                    |                 |                  |                    |
       v                    v                 v                  v                    v
+--------------+    +--------------+  +--------------+   +---------------+   +------------------+
| MobileNetV2  |    |  NPK Engine  |  |  Open-Meteo  |   | APMC Provider |   | Yield Loss Model |
| Keras/TFLite |    | Radar Chart  |  | / Demo Cache |   | (Live / CSV)  |   | Revenue Risk Est |
+------+-------+    +-------+------+  +-------+------+   +-------+-------+   +--------+---------+
       |                    |                 |                  |                    |
       +--------------------+-----------------+------------------+--------------------+
                                             |
                                             v
                           +-----------------------------------+
                           |    Agronomic Knowledge Base       |
                           |       (data/diseases.json)        |
                           +-----------------+-----------------+
                                             |
                                             v
                           +-----------------------------------+
                           |   SQLite Storage & Report Engine  |
                           |     (SQLAlchemy ORM / ReportLab)  |
                           +-----------------------------------+
```

---

## 🧠 Machine Learning Model & Training Pipeline

### Model Specifications
- **Architecture:** MobileNetV2 (ImageNet Pre-trained feature extractor, frozen backbone)
- **Input Dimensions:** `224 × 224 × 3` RGB
- **Built-in Graph Preprocessing:** `tf.keras.applications.mobilenet_v2.preprocess_input` (scales $[0, 255] \to [-1, 1]$ directly in the computation graph)
- **Classification Head:** `GlobalAveragePooling2D` $\to$ `Dropout(0.3)` $\to$ `Dense(38, activation='softmax')`
- **Total Parameters:** 2,404,020 (Trainable: 48,678; Non-trainable: 2,257,984)
- **Dataset:** PlantVillage Color Benchmark (54,305 curated images across 38 classes)
- **Exports:** Native Keras v3 format (`models/best_plant_model.keras`) and optimized TensorFlow Lite (`models/plant_disease_model.tflite`).

### Supported PlantVillage Classes (38)
```text
Apple (Scab, Black Rot, Cedar Apple Rust, Healthy)
Blueberry (Healthy)
Cherry (Powdery Mildew, Healthy)
Corn/Maize (Cercospora/Gray Leaf Spot, Common Rust, Northern Leaf Blight, Healthy)
Grape (Black Rot, Esca/Black Measles, Leaf Blight, Healthy)
Orange (Citrus Greening/Huanglongbing)
Peach (Bacterial Spot, Healthy)
Bell Pepper (Bacterial Spot, Healthy)
Potato (Early Blight, Late Blight, Healthy)
Raspberry (Healthy)
Soybean (Healthy)
Squash (Powdery Mildew)
Strawberry (Leaf Scorch, Healthy)
Tomato (Bacterial Spot, Early Blight, Late Blight, Leaf Mold, Septoria Leaf Spot, 
        Spider Mites, Target Spot, Tomato Yellow Leaf Curl Virus, Mosaic Virus, Healthy)
```

---

## 📁 Project Directory Structure

```text
smart-agri-partner/
│
├── app.py                         # Streamlit application entry point & view router
├── requirements.txt               # Locked production dependencies
├── README.md                      # Comprehensive academic project documentation
├── .env.example                   # Environment configuration template
├── .env                           # Local runtime environment (DEMO_MODE=true)
├── .gitignore                     # Git ignore rules
│
├── models/                        # Trained models & metadata
│   ├── best_plant_model.keras     # Trained MobileNetV2 Keras model (10.2 MB)
│   ├── plant_disease_model.tflite # Quantized edge model (2.58 MB)
│   ├── class_names.json           # Canonical 38 class labels
│   └── model_metadata.json        # Hyperparameters, architecture, and training details
│
├── backend/
│   ├── ml/
│   │   ├── disease_predictor.py   # Cached inference engine & confidence grader
│   │   ├── soil_analyzer.py       # NPK soil scoring and radar normalizer
│   │   ├── crop_recommender.py    # Multi-criteria crop suitability engine
│   │   └── loss_predictor.py      # Yield loss and revenue risk calculator
│   │
│   ├── services/
│   │   ├── weather_service.py     # Open-Meteo connector & agricultural advisories
│   │   ├── mandi_service.py       # APMC mandi provider & historical trend engine
│   │   ├── translation_service.py # Localization engine (English, Kannada, Hindi)
│   │   ├── report_generator.py    # PDF & CSV generation via ReportLab & Pandas
│   │   └── ai_assistant.py        # Agronomic FAQ and query assistant
│   │
│   ├── database/
│   │   ├── db.py                  # SQLite engine, sessions, and persistence helpers
│   │   └── models.py              # SQLAlchemy ORM models (Farmer, Scans, Soil, Mandi)
│   │
│   └── utils/
│       ├── constants.py           # Agronomic thresholds, constants, and paths
│       ├── helpers.py             # Image validation, logging, and currency formatting
│       └── create_disease_kb.py   # Knowledge base builder
│
├── data/
│   ├── diseases.json              # Authoritative agronomic KB for all 38 classes
│   ├── crops_database.json        # Crop environmental and nutrient requirements
│   └── mandi_demo.csv             # Realistic APMC benchmark market records
│
├── frontend/
│   ├── styles/
│   │   └── custom.css             # Agricultural theme styling (green/emerald/teal)
│   └── views/
│       ├── dashboard.py           # Farmer overview & quick action tiles
│       ├── disease_analysis.py    # Image upload, diagnosis & symptoms
│       ├── soil_health.py         # NPK sliders, radar chart & advisories
│       ├── crop_recommendation.py # Crop suitability ranking & explanations
│       ├── weather_alerts.py      # Live weather, 5-day forecast & alerts
│       ├── mandi_prices.py        # APMC modal rates & Plotly trend chart
│       ├── economic_loss.py       # Yield reduction & revenue impact calculator
│       ├── reports.py             # One-click PDF & CSV report export
│       ├── about_model.py         # Model specifications & academic limitations
│       └── settings.py            # Farmer profile and localization settings
│
├── reports/                       # Generated farmer PDF/CSV reports
├── logs/                          # System execution logs
├── tests/
│   ├── test_model.py              # Disease model unit tests
│   ├── test_weather.py            # Weather service unit tests
│   ├── test_soil.py               # Soil & crop recommendation unit tests
│   └── test_prices.py             # Mandi service unit tests
│
├── dataset/                       # Preserved PlantVillage dataset
└── train.py                       # Preserved training script
```

---

## ⚙️ Installation & Setup Guide

### 1. Prerequisites
- Python 3.10, 3.11, or 3.12 (Windows / Linux / macOS)
- Standard system terminal or PowerShell

### 2. Activate Virtual Environment
From the project root:

**On Windows:**
```powershell
.\venv\Scripts\activate
```

**On Linux/macOS:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Default `.env` configuration:
```ini
DEMO_MODE=true
WEATHER_API_KEY=
MANDI_API_KEY=
DEFAULT_LANGUAGE=en
DATABASE_URL=sqlite:///smart_agri_partner.db
```

---

## 🚀 Running the Application

Launch the Streamlit web dashboard:
```powershell
streamlit run app.py
```
The application will open automatically in your browser at:
`http://localhost:8501`

---

## 🧪 Running Automated Unit Tests

Run the full automated test suite covering all modules:
```powershell
python -m unittest discover -s tests
```
*Expected Result:*
```text
Ran 11 tests in 2.1s
OK
```

---

## 🛡️ Agricultural Safety Standards

Smart Agri-Partner strictly conforms to the following agronomic safety rules:
1. **No Chemical Hallucination:** The system **never invents synthetic pesticide chemical names, chemical dosages, or dilution instructions**.
2. **Integrated Pest Management (IPM):** Guidance prioritizes sanitation, pruning lower suckers, crop rotation, soil aeration, drip irrigation, and biological controls.
3. **Regulatory Advisory:** All diagnostic recommendations clearly urge farmers to consult their local **Krishi Vigyan Kendra (KVK)** or state agricultural university extension before purchasing any chemical treatments.

---

## 🔬 Limitations & Future Scope

### Limitations
- **Background Bias (Domain Shift):** The underlying PlantVillage dataset was collected under laboratory conditions with uniform backgrounds. Performance on field images with complex foliage clutter, shadows, or multiple diseases per leaf may show variance.
- **Single-Leaf Focus:** The current classifier evaluates individual leaf photos rather than whole plant canopy shots.

### Future Scope
- **Object Detection (YOLOv8 / RT-DETR):** Multi-disease localization and bounding box detection directly on standing crops.
- **Edge Deployment (Mobile & IoT):** Deploying the exported `plant_disease_model.tflite` model directly onto offline Android / Flutter apps and IoT camera traps.
- **Multilingual Voice Assistant:** Speech-to-text input in Kannada, Telugu, and Hindi for low-literacy rural accessibility.
- **Satellite Vegetation Indices:** Integrating Sentinel-2 NDVI imagery for field-scale crop stress monitoring.

---

## 🎓 Academic Project Information

- **Project Title:** SMART AGRI-PARTNER: AI APP FOR FARMERS
- **Domain:** Artificial Intelligence & Machine Learning (AIML) / AgTech
- **Core Technology:** Deep Learning (CNN / MobileNetV2), Streamlit, SQLite, Plotly, ReportLab
- **Dataset:** PlantVillage Dataset (David P. Hughes & Marcel Salathé, Penn State University)

#   p l a n t - d i s e a s e - d e t e c t o r  
 