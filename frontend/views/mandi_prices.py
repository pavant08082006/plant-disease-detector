"""
APMC Mandi Commodity Prices View.
"""

import streamlit as st
import plotly.express as px
import pandas as pd

from backend.services.mandi_service import get_mandi_prices, get_mandi_price_trend
from backend.services.translation_service import get_text
from backend.utils.constants import STATES_AND_DISTRICTS, MANDI_COMMODITIES


def render_mandi_prices(farmer: dict, lang: str):
    """Renders APMC mandi rates, commodity trends, and market comparisons."""
    st.title("📈 " + get_text("nav_mandi", lang))
    st.write(
        "Track wholesale APMC agricultural commodity prices, analyze 7-day price fluctuations, "
        "and optimize selling timings for maximum crop realization."
    )

    # Filter Bar
    c_state, c_dist, c_comm = st.columns(3)

    with c_state:
        state_list = ["All"] + list(STATES_AND_DISTRICTS.keys())
        default_s_idx = state_list.index(farmer.get("state", "Karnataka")) if farmer.get("state") in state_list else 0
        state = st.selectbox("Filter State:", state_list, index=default_s_idx)

    with c_dist:
        if state != "All":
            dist_options = ["All"] + STATES_AND_DISTRICTS.get(state, [])
        else:
            dist_options = ["All"]
        dist = st.selectbox("Filter District:", dist_options, index=0)

    with c_comm:
        comm_list = ["All"] + MANDI_COMMODITIES
        default_c_idx = comm_list.index(farmer.get("primary_crop", "Tomato")) if farmer.get("primary_crop") in comm_list else 1
        commodity = st.selectbox("Commodity:", comm_list, index=default_c_idx)

    # Fetch Data
    prices = get_mandi_prices(
        state=state if state != "All" else None,
        district=dist if dist != "All" else None,
        commodity=commodity if commodity != "All" else None
    )

    # Demo Mode Transparency Indicator
    if prices and prices[0].get("is_demo"):
        st.markdown(
            """
            <div style="margin: 0.5rem 0 1.2rem 0;">
                <span class="badge-demo">📌 Data Notice: Showing APMC Benchmark Records (Offline Demo Mode)</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    if not prices:
        st.warning("No APMC market records found for the selected combination. Try selecting 'All'.")
        return

    # Primary Benchmark Card
    top_entry = prices[0]
    st.markdown(f"### 📍 Benchmark Market: **{top_entry['market']}** ({top_entry['commodity']} - {top_entry['variety']})")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric(get_text("modal_price", lang), f"₹{top_entry['modal_price']:,.0f} / qtl")
    k2.metric(get_text("min_price", lang), f"₹{top_entry['min_price']:,.0f} / qtl")
    k3.metric(get_text("max_price", lang), f"₹{top_entry['max_price']:,.0f} / qtl")
    k4.metric("Recorded Date", top_entry["date"])

    st.markdown("---")

    # 7-Day Historical Trend Plotly Chart
    st.subheader(f"📊 7-Day Price Trend ({top_entry['commodity']})")
    trend_data = get_mandi_price_trend(top_entry["market"], top_entry["commodity"], days=7)
    df_trend = pd.DataFrame(trend_data)

    if not df_trend.empty:
        fig = px.line(
            df_trend,
            x="date",
            y="modal_price",
            markers=True,
            title=f"Daily Modal Rate: {top_entry['commodity']} (₹ / Quintal)",
            labels={"modal_price": "Price (₹/qtl)", "date": "Date"}
        )
        fig.update_traces(line_color="#10B981", line_width=3, marker_size=8)
        fig.update_layout(
            margin=dict(l=20, r=20, t=40, b=20),
            height=320,
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)

    # APMC Market Comparison Table
    st.markdown("---")
    st.subheader("📋 Regional APMC Market Rates Comparison")
    df_table = pd.DataFrame(prices)[["state", "district", "market", "commodity", "variety", "min_price", "modal_price", "max_price"]]
    df_table.columns = ["State", "District", "APMC Market", "Crop", "Variety", "Min (₹)", "Modal (₹)", "Max (₹)"]
    st.dataframe(df_table, use_container_width=True, hide_index=True)

