"""
Local Weather & Agricultural Advisories View.
"""

import streamlit as st
from backend.services.weather_service import get_weather, DISTRICT_COORDINATES
from backend.services.translation_service import get_text
from backend.utils.constants import STATES_AND_DISTRICTS


def render_weather_alerts(farmer: dict, lang: str):
    """Renders local weather conditions and agronomic alerts."""
    st.title("🌦️ " + get_text("nav_weather", lang))
    st.write(
        "Monitor micro-climate conditions, impending rainfall events, and automated agronomic warnings "
        "designed to prevent foliar disease outbreaks and fertilizer wash-off."
    )

    # Location Selector
    col_state, col_dist = st.columns(2)
    with col_state:
        state_list = list(STATES_AND_DISTRICTS.keys())
        default_state_idx = state_list.index(farmer.get("state", "Karnataka")) if farmer.get("state") in state_list else 0
        selected_state = st.selectbox("State:", state_list, index=default_state_idx)

    with col_dist:
        dist_list = STATES_AND_DISTRICTS.get(selected_state, ["Bengaluru"])
        default_dist_idx = dist_list.index(farmer.get("district", "Kolar")) if farmer.get("district") in dist_list else 0
        selected_dist = st.selectbox("District / Station:", dist_list, index=default_dist_idx)

    # Fetch Weather
    weather = get_weather(selected_dist)
    curr = weather.get("current", {})

    # Data Source & Demo Indicator
    source_label = weather.get("source", "Live Meteorological Service")
    badge_cls = "badge-demo" if weather.get("is_demo") else "badge-high"
    st.markdown(
        f"""
        <div style="margin: 0.5rem 0 1rem 0;">
            <span class="{badge_cls}">Data Source: {source_label}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Current Weather Metrics Row
    w1, w2, w3, w4, w5 = st.columns(5)
    w1.metric(f"Current Temp {curr.get('icon', '🌤️')}", f"{curr.get('temperature', 28)}°C", f"Feels {curr.get('feels_like', 29)}°C")
    w2.metric("Humidity 💧", f"{curr.get('humidity', 60)}%")
    w3.metric("Rainfall 🌧️", f"{curr.get('rainfall', 0)} mm")
    w4.metric("Wind Speed 💨", f"{curr.get('wind_speed', 12)} km/h")
    w5.metric("Condition", curr.get("condition", "Partly Cloudy"))

    st.markdown("---")

    # Farmer-Specific Actionable Alerts
    st.subheader("🔔 " + get_text("farming_alerts", lang))
    advisories = weather.get("advisories", [])

    if advisories:
        for adv in advisories:
            sev = adv.get("severity", "info")
            icon = adv.get("icon", "⚠️")
            title = adv.get("title", "Advisory")
            msg = adv.get("message", "")

            if sev == "warning":
                st.warning(f"**{icon} {title}:** {msg}")
            elif sev == "success":
                st.success(f"**{icon} {title}:** {msg}")
            else:
                st.info(f"**{icon} {title}:** {msg}")
    else:
        st.success("✅ No adverse meteorological alerts for your region today.")

    st.markdown("---")

    # 5-Day Agricultural Forecast Cards
    st.subheader("📅 5-Day Field Forecast")
    forecast = weather.get("forecast", [])
    if forecast:
        cols = st.columns(len(forecast))
        for i, f_day in enumerate(forecast):
            with cols[i]:
                with st.container(border=True):
                    st.markdown(f"**{f_day['day']}**")
                    st.markdown(f"### {f_day.get('icon', '🌤️')}")
                    st.write(f"🌡️ {f_day['temp_max']}° / {f_day['temp_min']}°")
                    st.caption(f"{f_day['condition']}")
                    st.caption(f"Rain: {f_day['rain_chance']}%")

