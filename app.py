"""
SMART AGRI-PARTNER: AI APP FOR FARMERS
Main Streamlit Application Entrypoint & Modular View Router.
"""

import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

# Load environment configuration
load_dotenv()

# Initialize Page Settings
st.set_page_config(
    page_title="Smart Agri-Partner",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Core Imports
from backend.database.db import init_db, get_current_farmer
from backend.services.translation_service import get_text
from backend.utils.constants import LANGUAGES

# Modular Views
from frontend.views.dashboard import render_dashboard
from frontend.views.disease_analysis import render_disease_analysis
from frontend.views.soil_health import render_soil_health
from frontend.views.crop_recommendation import render_crop_recommendation
from frontend.views.weather_alerts import render_weather_alerts
from frontend.views.mandi_prices import render_mandi_prices
from frontend.views.economic_loss import render_economic_loss
from frontend.views.reports import render_reports
from frontend.views.about_model import render_about_model
from frontend.views.settings import render_settings


def load_custom_css():
    """Injects agricultural UI stylesheets."""
    css_path = Path(__file__).resolve().parent / "frontend" / "styles" / "custom.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def main():
    # 1. Initialize Database & Styles
    init_db()
    load_custom_css()

    # 2. Session State Setup
    if "farmer" not in st.session_state:
        st.session_state["farmer"] = get_current_farmer()

    farmer = st.session_state["farmer"]

    if "language" not in st.session_state:
        st.session_state["language"] = farmer.get("language", "en")

    current_lang = st.session_state["language"]

    # 3. Sidebar Navigation & Global Controls
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 1.2rem;">
                <h2 style="color: #1b5e20; margin-bottom: 0.2rem;">🌾 Smart Agri-Partner</h2>
                <span style="font-size: 0.85rem; color: #4b5563;">AI Companion for Farmers</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Demo Mode Badge
        is_demo = os.getenv("DEMO_MODE", "true").lower() == "true"
        if is_demo:
            st.markdown(
                """
                <div style="text-align: center; margin-bottom: 1rem;">
                    <span class="badge-demo">🟢 DEMO MODE (OFFLINE READY)</span>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Language Selector
        st.markdown(f"**🌐 {get_text('language_select', current_lang)}**")
        lang_keys = list(LANGUAGES.keys())
        selected_lang = st.selectbox(
            "Language",
            options=lang_keys,
            index=lang_keys.index(current_lang) if current_lang in lang_keys else 0,
            format_func=lambda x: LANGUAGES[x],
            label_visibility="collapsed"
        )
        if selected_lang != current_lang:
            st.session_state["language"] = selected_lang
            current_lang = selected_lang
            st.rerun()

        st.markdown("---")

        # Navigation Options
        nav_options = [
            get_text("nav_dashboard", current_lang),
            get_text("nav_disease", current_lang),
            get_text("nav_soil", current_lang),
            get_text("nav_crop_rec", current_lang),
            get_text("nav_weather", current_lang),
            get_text("nav_mandi", current_lang),
            get_text("nav_economic", current_lang),
            get_text("nav_reports", current_lang),
            get_text("nav_about_model", current_lang),
            get_text("nav_settings", current_lang)
        ]

        if "nav_choice" not in st.session_state or st.session_state["nav_choice"] not in nav_options:
            st.session_state["nav_choice"] = nav_options[0]

        choice = st.radio(
            "Navigation",
            options=nav_options,
            index=nav_options.index(st.session_state["nav_choice"]),
            label_visibility="collapsed"
        )
        st.session_state["nav_choice"] = choice

        st.markdown("---")
        st.caption(f"👨‍🌾 Active: **{farmer.get('name', 'Farmer')}**")
        st.caption(f"📍 {farmer.get('district', 'Kolar')}, {farmer.get('state', 'Karnataka')}")
        st.caption("v1.0.0 (AIML Major Project)")

    # 4. View Routing
    if choice == nav_options[0]:
        render_dashboard(farmer, current_lang)
    elif choice == nav_options[1]:
        render_disease_analysis(farmer, current_lang)
    elif choice == nav_options[2]:
        render_soil_health(farmer, current_lang)
    elif choice == nav_options[3]:
        render_crop_recommendation(farmer, current_lang)
    elif choice == nav_options[4]:
        render_weather_alerts(farmer, current_lang)
    elif choice == nav_options[5]:
        render_mandi_prices(farmer, current_lang)
    elif choice == nav_options[6]:
        render_economic_loss(farmer, current_lang)
    elif choice == nav_options[7]:
        render_reports(farmer, current_lang)
    elif choice == nav_options[8]:
        render_about_model()
    elif choice == nav_options[9]:
        render_settings(farmer, current_lang)


if __name__ == "__main__":
    main()

