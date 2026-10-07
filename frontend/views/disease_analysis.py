"""
Real-Time Crop Disease Analysis View.
Integrates trained MobileNetV2 model inference, top-3 predictions,
and authoritative agronomic knowledge base.
"""

import json
from pathlib import Path
from PIL import Image
import streamlit as st

from backend.ml.disease_predictor import predict_disease
from backend.services.translation_service import get_text
from backend.utils.constants import DATA_DIR, UPLOADS_DIR
from backend.database.db import log_disease_scan
from backend.utils.helpers import get_logger

logger = get_logger("DiseaseAnalysisView")


@st.cache_data
def load_diseases_kb():
    """Loads agronomic knowledge base from JSON."""
    kb_path = DATA_DIR / "diseases.json"
    if kb_path.exists():
        with open(kb_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def render_disease_analysis(farmer: dict, lang: str):
    """Renders leaf disease detection workflow."""
    st.title("🌿 " + get_text("nav_disease", lang))
    st.write(
        "Upload a clear photograph of a crop leaf to detect fungal, bacterial, or viral diseases "
        "using your fine-tuned MobileNetV2 deep learning classifier."
    )

    kb = load_diseases_kb()

    col_up, col_preview = st.columns([1, 1])

    with col_up:
        uploaded_file = st.file_uploader(
            get_text("upload_image", lang),
            type=["jpg", "jpeg", "png"],
            help=get_text("upload_hint", lang)
        )

        # Quick Demo Sample Selector
        st.markdown("**— OR try a pre-loaded PlantVillage test sample —**")
        sample_choice = st.selectbox(
            "Select sample leaf:",
            [
                "None (Upload my own)",
                "Apple - Apple Scab",
                "Corn - Common Rust",
                "Potato - Early Blight",
                "Tomato - Early Blight",
                "Tomato - Healthy Leaf"
            ]
        )

    # Determine Image to Process
    img_to_process = None
    file_identifier = ""

    if uploaded_file is not None:
        try:
            img_to_process = Image.open(uploaded_file)
            file_identifier = uploaded_file.name
        except Exception as e:
            st.error(f"Could not open uploaded image: {e}")

    elif sample_choice != "None (Upload my own)":
        sample_map = {
            "Apple - Apple Scab": "dataset/plantvillage dataset/color/Apple___Apple_scab",
            "Corn - Common Rust": "dataset/plantvillage dataset/color/Corn_(maize)___Common_rust_",
            "Potato - Early Blight": "dataset/plantvillage dataset/color/Potato___Early_blight",
            "Tomato - Early Blight": "dataset/plantvillage dataset/color/Tomato___Early_blight",
            "Tomato - Healthy Leaf": "dataset/plantvillage dataset/color/Tomato___healthy"
        }
        dir_path = Path(sample_map[sample_choice])
        if dir_path.exists():
            files = list(dir_path.glob("*.JPG")) + list(dir_path.glob("*.jpg"))
            if files:
                img_to_process = Image.open(files[0])
                file_identifier = files[0].name

    with col_preview:
        if img_to_process is not None:
            st.image(img_to_process, caption=f"Leaf Image: {file_identifier}", use_container_width=True)
        else:
            st.info("👈 Upload an image or pick a demo sample to begin diagnosis.")

    if img_to_process is not None:
        st.markdown("---")
        if st.button("🔍 " + get_text("diagnose_btn", lang), type="primary", use_container_width=True):
            with st.spinner("Analyzing foliar patterns using MobileNetV2..."):
                try:
                    result = predict_disease(img_to_process, top_k=3)
                    st.session_state["last_diagnosis"] = result

                    # Save scan record in SQLite
                    log_disease_scan(result, farmer_id=farmer.get("id", 1))

                    st.success("Analysis Complete!")
                except Exception as e:
                    st.error(f"Inference error: {e}")
                    logger.error(f"Inference failed: {e}")
                    return

    # Render Results if available in session
    if "last_diagnosis" in st.session_state:
        diag = st.session_state["last_diagnosis"]
        st.markdown("### 📋 " + get_text("diagnosis_result", lang))

        # KPI Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(get_text("crop", lang), diag["crop"])
        m2.metric(get_text("disease", lang), diag["disease"])
        m3.metric(get_text("confidence", lang), f"{diag['confidence']}%")
        
        status_label = "✅ " + get_text("healthy", lang) if diag["status"] == "healthy" else "⚠️ " + get_text("diseased", lang)
        m4.metric(get_text("status", lang), status_label)

        # Confidence Grading Badge & Guidance
        conf_level = diag.get("confidence_level", "Moderate")
        badge_class = "badge-high" if conf_level == "High" else ("badge-mod" if conf_level == "Moderate" else "badge-low")
        st.markdown(
            f"""
            <div style="margin: 0.8rem 0;">
                <span class="{badge_class}">Certainty Level: {conf_level} Confidence</span>
                <span style="margin-left: 10px; font-size: 0.9rem; color: #4b5563;">{diag.get('user_guidance', '')}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Top 3 Alternative Predictions
        with st.expander("📊 " + get_text("top_predictions", lang), expanded=True):
            top_preds = diag.get("top_predictions", [])
            for i, p in enumerate(top_preds):
                c_a, c_b = st.columns([3, 1])
                c_a.write(f"**{i+1}. {p['crop']} — {p['disease']}**")
                c_b.progress(p["confidence"] / 100.0, text=f"{p['confidence']}%")

        # Agronomic Knowledge Details
        raw_lbl = diag.get("raw_label", "")
        info = kb.get(raw_lbl)

        if info:
            st.session_state["last_diagnosis"]["guidance"] = info
            st.markdown("---")
            st.subheader(f"📚 Agronomic Profile: {info['disease']} ({info.get('scientific_name', '')})")

            t1, t2, t3 = st.tabs(["🔍 Symptoms & Causes", "🛡️ Prevention & Sanitation", "⚠️ Safe Management"])

            with t1:
                st.markdown("#### " + get_text("symptoms", lang))
                for sym in info.get("symptoms", []):
                    st.markdown(f"- {sym}")
                st.markdown("#### " + get_text("causes", lang))
                for cause in info.get("causes", []):
                    st.markdown(f"- {cause}")

            with t2:
                st.markdown("#### " + get_text("prevention", lang))
                for prev in info.get("prevention", []):
                    st.markdown(f"- {prev}")

            with t3:
                st.markdown("#### " + get_text("management", lang))
                for mgmt in info.get("management", []):
                    st.markdown(f"- {mgmt}")
                st.info(f"**Safety Notice:** {info.get('safety_notice', 'Consult your regional KVK specialist.')}")

        # Agricultural Safety Disclaimer
        st.warning(
            "🛡️ **Agricultural Advisory Notice:** The recommendations provided are for cultural, sanitational, "
            "and integrated pest management (IPM) guidance. Do not purchase or spray hazardous synthetic chemicals "
            "without consulting your local agricultural extension officer."
        )

