"""
Dashboard Landing View for Smart Agri-Partner.
"""

import streamlit as st
from backend.services.translation_service import get_text
from backend.services.weather_service import get_weather
from backend.services.mandi_service import get_mandi_prices
from backend.database.db import get_recent_scans
from backend.services.ai_assistant import ask_assistant


def render_dashboard(farmer: dict, lang: str):
    """Renders the comprehensive farmer overview dashboard."""
    # Hero Section
    st.markdown(
        f"""
        <div class="hero-banner">
            <h1>🌾 {get_text('app_title', lang)}</h1>
            <p style="font-size: 1.15rem; font-weight: 500; margin-bottom: 0.5rem;">
                {get_text('hero_title', lang)}
            </p>
            <p style="font-size: 0.95rem; opacity: 0.9;">
                👨‍🌾 <b>{get_text('welcome', lang)}, {farmer.get('name', 'Farmer')}</b> | 📍 {farmer.get('district', 'Bengaluru')}, {farmer.get('state', 'Karnataka')} | 🚜 {farmer.get('land_area', 2.0)} Acres ({farmer.get('primary_crop', 'Tomato')})
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Overview Cards
    col1, col2, col3, col4 = st.columns(4)

    # 1. Weather Snapshot
    weather = get_weather(farmer.get("district", "Bengaluru"))
    w_curr = weather.get("current", {})
    with col1:
        st.metric(
            label=f"🌦️ Weather ({farmer.get('district', 'Local')})",
            value=f"{w_curr.get('temperature', 28)}°C",
            delta=w_curr.get("condition", "Fair")
        )

    # 2. Mandi Price Snapshot
    mandi_list = get_mandi_prices(
        state=farmer.get("state"),
        district=farmer.get("district"),
        commodity=farmer.get("primary_crop", "Tomato")
    )
    modal_val = mandi_list[0]["modal_price"] if mandi_list else 2450.0
    with col2:
        st.metric(
            label=f"📈 Mandi: {farmer.get('primary_crop', 'Tomato')}",
            value=f"₹{modal_val:,.0f} / qtl",
            delta="APMC Benchmark"
        )

    # 3. Soil Health Snapshot
    with col3:
        st.metric(
            label="🧪 Soil Health Score",
            value="78 / 100",
            delta="Optimal Index"
        )

    # 4. Economic Risk Snapshot
    with col4:
        st.metric(
            label="💰 Estimated Risk",
            value="Low (Safe)",
            delta="No active crisis"
        )

    st.markdown("---")

    # Module Quick Action Grid
    st.subheader("⚡ Quick Services & Agricultural Tools")
    q1, q2, q3 = st.columns(3)

    with q1:
        with st.container(border=True):
            st.markdown("### 🌿 Leaf Disease Detection")
            st.write("Scan plant leaves instantly using your trained MobileNetV2 deep learning model.")
            if st.button("Open Disease Scanner ➜", key="btn_dash_disease", use_container_width=True):
                st.session_state["nav_choice"] = "🌿 Disease Detection"
                st.rerun()

    with q2:
        with st.container(border=True):
            st.markdown("### 🧪 Soil Health & NPK")
            st.write("Evaluate nitrogen, phosphorus, potassium, and pH with interactive radar charts.")
            if st.button("Check Soil Health ➜", key="btn_dash_soil", use_container_width=True):
                st.session_state["nav_choice"] = "🧪 Soil Health"
                st.rerun()

    with q3:
        with st.container(border=True):
            st.markdown("### 🌾 Crop Recommendation")
            st.write("Discover the most profitable and climate-suited crops for your farmland.")
            if st.button("Recommend Crops ➜", key="btn_dash_crop", use_container_width=True):
                st.session_state["nav_choice"] = "🌾 Crop Recommendation"
                st.rerun()

    q4, q5, q6 = st.columns(3)
    with q4:
        with st.container(border=True):
            st.markdown("### 🌦️ Weather Advisories")
            st.write("Check localized weather forecasts, rain alerts, and disease risk notifications.")
            if st.button("View Weather ➜", key="btn_dash_weather", use_container_width=True):
                st.session_state["nav_choice"] = "🌦️ Weather Alerts"
                st.rerun()

    with q5:
        with st.container(border=True):
            st.markdown("### 📈 Mandi Market Prices")
            st.write("Compare APMC prices across markets and view 7-day historical trends.")
            if st.button("Explore Mandi Rates ➜", key="btn_dash_mandi", use_container_width=True):
                st.session_state["nav_choice"] = "📈 Mandi Prices"
                st.rerun()

    with q6:
        with st.container(border=True):
            st.markdown("### 💰 Economic Loss Calculator")
            st.write("Estimate revenue risk, potential yield reduction, and net financial outcomes.")
            if st.button("Calculate Loss ➜", key="btn_dash_econ", use_container_width=True):
                st.session_state["nav_choice"] = "💰 Economic Calculator"
                st.rerun()

    st.markdown("---")

    # Bottom Split: Recent Scans + Farmer AI Assistant
    b_col1, b_col2 = st.columns([1, 1])

    with b_col1:
        st.subheader("📋 Recent Crop Scans")
        recent_scans = get_recent_scans(limit=4)
        if recent_scans:
            for s in recent_scans:
                with st.expander(f"{s['crop']} - {s['disease']} ({s['confidence']}%)", expanded=False):
                    st.write(f"**Date:** {s['created_at']}")
                    st.write(f"**Health Status:** `{s['status']}`")
            if st.button("View All Test Reports 📋", key="btn_dash_view_reports", use_container_width=True):
                st.session_state["nav_choice"] = get_text("nav_reports", lang)
                st.rerun()
        else:
            st.info("No leaf scans recorded yet. Upload a leaf photo in the **Disease Detection** tab.")

    with b_col2:
        st.subheader("🤖 Farmer AI Assistant")
        st.caption("Ask quick questions about crop diseases, fertilizers, weather, or market rates.")
        user_q = st.text_input(
            "Your Question:",
            placeholder="e.g., What does low soil nitrogen mean?",
            key="dash_ai_query"
        )
        if st.button("Ask Assistant 💬", key="dash_ask_btn"):
            if user_q.strip():
                ans = ask_assistant(user_q)
                st.markdown(ans)
            else:
                st.warning("Please enter a question.")

