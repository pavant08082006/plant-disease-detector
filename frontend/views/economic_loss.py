"""
Economic Loss & Crop Revenue Risk Calculator View.
"""

import streamlit as st
import plotly.graph_objects as go

from backend.ml.loss_predictor import calculate_economic_loss
from backend.services.translation_service import get_text
from backend.utils.constants import PRIMARY_CROPS
from backend.utils.helpers import format_currency


def render_economic_loss(farmer: dict, lang: str):
    """Renders the agricultural economic risk and loss calculation interface."""
    st.title("💰 " + get_text("nav_economic", lang))
    st.write(
        "Estimate the financial exposure of foliar disease outbreaks on your crop harvest. "
        "Calculate yield reduction, potential revenue loss, and net profit margins under varying disease severity."
    )

    # Pre-populate defaults
    def_crop = farmer.get("primary_crop", "Tomato")
    def_land = float(farmer.get("land_area", 2.0))

    # Input Columns
    col_in, col_calc = st.columns([1, 1])

    with col_in:
        st.subheader("🌾 Farm & Crop Inputs")
        
        crop_idx = PRIMARY_CROPS.index(def_crop) if def_crop in PRIMARY_CROPS else 0
        crop = st.selectbox("Select Crop:", PRIMARY_CROPS, index=crop_idx)
        land_area = st.number_input(get_text("land_area", lang), min_value=0.25, max_value=500.0, value=def_land, step=0.5)
        expected_yield = st.number_input(get_text("expected_yield", lang), min_value=1.0, max_value=800.0, value=120.0, step=10.0)
        market_price = st.number_input(get_text("market_price", lang), min_value=500.0, max_value=50000.0, value=2200.0, step=100.0)

        st.subheader("⚠️ Disease Severity Estimation")
        severity = st.select_slider(
            get_text("disease_severity", lang),
            options=["None / Healthy", "Low (Early Stage)", "Moderate (Spreading)", "Severe (Widespread)"],
            value="Moderate (Spreading)"
        )

        with st.expander("Cultivation Expense Settings (Optional)", expanded=False):
            cost_per_acre = st.number_input("Cultivation Cost per Acre (₹):", min_value=5000.0, max_value=200000.0, value=45000.0, step=5000.0)
            other_expenses = st.number_input("Other Expenses / Transport (₹):", min_value=0.0, max_value=100000.0, value=5000.0, step=1000.0)

        econ = calculate_economic_loss(
            crop=crop,
            land_area_acres=land_area,
            expected_yield_per_acre=expected_yield,
            market_price_per_quintal=market_price,
            disease_severity_level=severity,
            cultivation_cost_per_acre=cost_per_acre,
            other_expenses=other_expenses
        )
        st.session_state["last_economic"] = econ

    with col_calc:
        st.subheader("📊 Estimated Financial Exposure")

        # Risk Banner
        st.markdown(
            f"""
            <div style="background-color: #f8fafc; border-left: 6px solid {econ['risk_color']}; border-radius: 8px; padding: 1.2rem; margin-bottom: 1rem;">
                <h4 style="margin: 0; color: {econ['risk_color']};">{econ['risk_level']}</h4>
                <p style="margin: 0.3rem 0 0 0; font-size: 0.9rem; color: #475569;">{econ['action_plan']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Revenue & Loss Comparison
        r1, r2 = st.columns(2)
        r1.metric("Potential Revenue (Healthy)", format_currency(econ["expected_gross_revenue"]))
        r2.metric("Estimated Income Loss ⚠️", format_currency(econ["estimated_income_loss"]), delta=f"-{econ['loss_pct']}% Loss", delta_color="inverse")

        r3, r4 = st.columns(2)
        r3.metric("Realized Gross Revenue", format_currency(econ["realized_gross_revenue"]))
        r4.metric("Realized Net Profit", format_currency(econ["realized_net_profit"]))

        # Visual Comparison Bar Chart
        categories = ["Expected Harvest", "Realized Harvest", "Lost to Disease"]
        yield_values = [econ["total_expected_yield_qtl"], econ["realized_yield_qtl"], econ["lost_yield_qtl"]]

        fig = go.Figure(data=[
            go.Bar(
                x=categories,
                y=yield_values,
                marker_color=["#3B82F6", "#10B981", "#EF4444"],
                text=[f"{v} qtl" for v in yield_values],
                textposition="auto"
            )
        ])

        fig.update_layout(
            title="Yield Impact Breakdown (Quintals)",
            height=280,
            margin=dict(l=20, r=20, t=35, b=20),
            yaxis_title="Quintals"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.info(f"📌 **Disclaimer:** {econ['disclaimer']}")

