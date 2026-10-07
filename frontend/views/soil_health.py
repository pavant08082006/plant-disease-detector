"""
Soil Health Monitoring & NPK Radar Analysis View.
"""

import streamlit as st
import plotly.graph_objects as go

from backend.ml.soil_analyzer import analyze_soil_health
from backend.services.translation_service import get_text


def render_soil_health(farmer: dict, lang: str):
    """Renders interactive soil analysis dashboard."""
    st.title("🧪 " + get_text("nav_soil", lang))
    st.write(
        "Evaluate topsoil chemical properties (NPK, pH, Organic Carbon) to calculate an overall "
        "Soil Health Index and view customized soil enhancement advisories."
    )

    # Input Columns
    col_in, col_viz = st.columns([1, 1])

    with col_in:
        st.subheader("📝 Enter Soil Test Lab Values")
        
        ph = st.slider(get_text("soil_ph", lang), min_value=4.0, max_value=9.5, value=6.8, step=0.1, help="Ideal range: 6.0 - 7.5")
        nitrogen = st.number_input(get_text("nitrogen", lang), min_value=50.0, max_value=900.0, value=280.0, step=10.0, help="Available Nitrogen (kg/ha)")
        phosphorus = st.number_input(get_text("phosphorus", lang), min_value=5.0, max_value=120.0, value=35.0, step=5.0, help="Available Phosphorus (kg/ha)")
        potassium = st.number_input(get_text("potassium", lang), min_value=50.0, max_value=600.0, value=210.0, step=10.0, help="Available Potassium (kg/ha)")
        
        with st.expander("Additional Physical & Chemical Parameters", expanded=False):
            oc = st.slider(get_text("organic_carbon", lang), min_value=0.1, max_value=2.0, value=0.65, step=0.05)
            moisture = st.slider(get_text("moisture", lang), min_value=10.0, max_value=90.0, value=55.0, step=5.0)
            ec = st.number_input("Electrical Conductivity (EC - dS/m)", min_value=0.1, max_value=5.0, value=1.1, step=0.1)

        soil_result = analyze_soil_health(
            ph=ph, nitrogen=nitrogen, phosphorus=phosphorus,
            potassium=potassium, organic_carbon=oc, moisture=moisture, ec=ec
        )
        st.session_state["last_soil"] = soil_result

    with col_viz:
        st.subheader("🎯 " + get_text("soil_health_score", lang))
        score = soil_result["score"]
        grade = soil_result["grade"]
        color = soil_result["color"]

        # Gauge / Metric Display
        st.markdown(
            f"""
            <div style="background-color: #f8fafc; border-radius: 16px; padding: 1.5rem; text-align: center; border: 2px solid {color}; margin-bottom: 1rem;">
                <h1 style="color: {color}; font-size: 3.5rem; margin: 0; font-weight: 700;">{score} <span style="font-size: 1.5rem; color: #64748b;">/ 100</span></h1>
                <h3 style="color: #1e293b; margin: 0.5rem 0 0 0;">{grade}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Plotly Radar Chart
        radar_data = soil_result["radar_data"]
        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=radar_data["values"] + [radar_data["values"][0]],
            theta=radar_data["categories"] + [radar_data["categories"][0]],
            fill='toself',
            fillcolor='rgba(16, 185, 129, 0.25)',
            line=dict(color='#10B981', width=2),
            name='Current Status'
        ))

        # Benchmark Ideal Ring
        fig.add_trace(go.Scatterpolar(
            r=[100, 100, 100, 100, 100, 100, 100],
            theta=radar_data["categories"] + [radar_data["categories"][0]],
            line=dict(color='#94a3b8', width=1, dash='dash'),
            name='Optimal Benchmark (100)'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 110])
            ),
            showlegend=True,
            margin=dict(l=30, r=30, t=20, b=20),
            height=320
        )

        st.plotly_chart(fig, use_container_width=True)

    # Nutrient Status Cards
    st.markdown("---")
    st.subheader("📊 Individual Nutrient Classifications")

    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m = soil_result["metrics"]

    with m_col1:
        st.metric("Soil pH", f"{ph:.1f}", delta=m["ph"]["status"])
    with m_col2:
        st.metric("Nitrogen (N)", f"{nitrogen:.0f} kg/ha", delta=m["nitrogen"]["status"])
    with m_col3:
        st.metric("Phosphorus (P)", f"{phosphorus:.0f} kg/ha", delta=m["phosphorus"]["status"])
    with m_col4:
        st.metric("Potassium (K)", f"{potassium:.0f} kg/ha", delta=m["potassium"]["status"])

    # Actionable Advisories
    st.markdown("---")
    st.subheader("💡 Agronomic Improvement Recommendations")
    for rec in soil_result["recommendations"]:
        st.markdown(f"- 🌿 {rec}")

    st.info(
        "📌 **Soil Stewardship Note:** Always calibrate fertilizer inputs against laboratory soil test reports. "
        "Prioritize organic manures, vermicompost, and crop rotation to preserve soil microbiomes."
    )

