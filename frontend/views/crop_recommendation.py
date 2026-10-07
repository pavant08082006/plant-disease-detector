"""
Crop Recommendation System View.
Suggests optimal crops tailored to soil fertility, moisture, and local climate.
"""

import streamlit as st
from backend.ml.crop_recommender import recommend_crops
from backend.services.translation_service import get_text


def render_crop_recommendation(farmer: dict, lang: str):
    """Renders crop recommendation interface."""
    st.title("🌾 " + get_text("nav_crop_rec", lang))
    st.write(
        "Determine the best-suited, highest-yielding crops based on your soil's chemical parameters, "
        "local rainfall, ambient temperature, and current cropping season."
    )

    # Pre-populate from soil tab if available
    default_n = 280.0
    default_p = 35.0
    default_k = 210.0
    default_ph = 6.8
    if "last_soil" in st.session_state:
        raws = st.session_state["last_soil"].get("raw_inputs", {})
        default_n = raws.get("nitrogen", default_n)
        default_p = raws.get("phosphorus", default_p)
        default_k = raws.get("potassium", default_k)
        default_ph = raws.get("ph", default_ph)

    col_soil, col_climate = st.columns(2)

    with col_soil:
        st.subheader("🌱 Soil Profile")
        n = st.number_input("Soil Nitrogen (kg/ha):", value=float(default_n), step=10.0, key="cr_n")
        p = st.number_input("Soil Phosphorus (kg/ha):", value=float(default_p), step=5.0, key="cr_p")
        k = st.number_input("Soil Potassium (kg/ha):", value=float(default_k), step=10.0, key="cr_k")
        ph = st.slider("Soil pH:", min_value=4.5, max_value=8.5, value=float(default_ph), step=0.1, key="cr_ph")

    with col_climate:
        st.subheader("🌤️ Climate & Location")
        season = st.selectbox("Current Sowing Season:", ["Kharif", "Rabi", "Zaid", "All"], index=0, key="cr_season")
        temp = st.slider("Average Temperature (°C):", min_value=10.0, max_value=45.0, value=26.0, step=1.0, key="cr_temp")
        rainfall = st.slider("Annual / Seasonal Rainfall (mm):", min_value=200.0, max_value=2500.0, value=750.0, step=50.0, key="cr_rain")
        humidity = st.slider("Relative Humidity (%):", min_value=20.0, max_value=95.0, value=65.0, step=5.0, key="cr_hum")

    st.markdown("---")
    if st.button("🚀 " + get_text("recommend_crops_btn", lang), type="primary", use_container_width=True):
        recs = recommend_crops(
            nitrogen=n, phosphorus=p, potassium=k, ph=ph,
            temperature=temp, humidity=humidity, rainfall=rainfall,
            season=season, top_n=4
        )
        st.session_state["crop_recommendations"] = recs

    if "crop_recommendations" in st.session_state:
        recs = st.session_state["crop_recommendations"]
        st.subheader("🏆 " + get_text("recommended_crops", lang))

        for item in recs:
            with st.container(border=True):
                c_title, c_score = st.columns([3, 1])
                with c_title:
                    st.markdown(f"### {item.get('rank_badge', '•')} {item['crop']}")
                    st.caption(item["description"])
                with c_score:
                    st.metric("Suitability", f"{item['suitability']}%")

                st.markdown(f"**Why this crop is suitable:** {item['explanation']}")
                
                # Agronomic reference tags
                r1, r2, r3 = st.columns(3)
                r1.markdown(f"🧪 **Target pH:** {item['ideal_ph']}")
                r2.markdown(f"🌡️ **Target Temp:** {item['ideal_temp']}")
                r3.markdown(f"🌧️ **Target Rain:** {item['ideal_rainfall']}")

