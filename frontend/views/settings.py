"""
Farmer Profile Management View.
"""

import streamlit as st
from backend.database.db import save_farmer_profile
from backend.services.translation_service import get_text
from backend.utils.constants import STATES_AND_DISTRICTS, PRIMARY_CROPS, LANGUAGES


def render_settings(farmer: dict, lang: str):
    """Renders profile customization and localization settings."""
    st.title("⚙️ " + get_text("nav_settings", lang))
    st.write(
        "Manage your farm specifications and preferred agricultural region. "
        "These settings calibrate your default weather forecasts, mandi benchmarks, and soil recommendations."
    )

    with st.form("farmer_profile_form"):
        st.subheader("👨‍🌾 Personal & Farm Details")

        f_name = st.text_input("Farmer Full Name:", value=farmer.get("name", "Farmer"))
        f_phone = st.text_input("Contact Number (Optional):", value=farmer.get("phone", ""))

        c_st, c_dt, c_vg = st.columns(3)
        with c_st:
            state_list = list(STATES_AND_DISTRICTS.keys())
            st_idx = state_list.index(farmer.get("state", "Karnataka")) if farmer.get("state") in state_list else 0
            f_state = st.selectbox("State:", state_list, index=st_idx)

        with c_dt:
            dist_list = STATES_AND_DISTRICTS.get(f_state, ["Bengaluru"])
            dt_idx = dist_list.index(farmer.get("district", "Kolar")) if farmer.get("district") in dist_list else 0
            f_district = st.selectbox("District:", dist_list, index=dt_idx)

        with c_vg:
            f_village = st.text_input("Village / Taluk:", value=farmer.get("village", ""))

        c_land, c_crop, c_soil = st.columns(3)
        with c_land:
            f_land = st.number_input("Total Land Holding (Acres):", min_value=0.25, max_value=500.0, value=float(farmer.get("land_area", 2.0)), step=0.5)

        with c_crop:
            cr_idx = PRIMARY_CROPS.index(farmer.get("primary_crop", "Tomato")) if farmer.get("primary_crop") in PRIMARY_CROPS else 0
            f_crop = st.selectbox("Primary Crop:", PRIMARY_CROPS, index=cr_idx)

        with c_soil:
            soil_types = ["Red Loam", "Black Cotton Soil", "Sandy Loam", "Clay Loam", "Alluvial", "Laterite"]
            s_idx = soil_types.index(farmer.get("soil_type", "Red Loam")) if farmer.get("soil_type") in soil_types else 0
            f_soil = st.selectbox("Dominant Soil Type:", soil_types, index=s_idx)

        st.subheader("🌐 " + get_text("language_select", lang))
        lang_keys = list(LANGUAGES.keys())
        curr_lang_idx = lang_keys.index(farmer.get("language", "en")) if farmer.get("language") in lang_keys else 0
        f_lang = st.selectbox(
            "Default Application Language:",
            lang_keys,
            index=curr_lang_idx,
            format_func=lambda x: LANGUAGES[x]
        )

        submit = st.form_submit_button("💾 " + get_text("save_profile", lang), type="primary")

        if submit:
            updated_profile = {
                "name": f_name,
                "phone": f_phone,
                "state": f_state,
                "district": f_district,
                "village": f_village,
                "land_area": f_land,
                "primary_crop": f_crop,
                "soil_type": f_soil,
                "language": f_lang
            }
            if save_farmer_profile(updated_profile):
                st.session_state["farmer"] = updated_profile
                st.session_state["language"] = f_lang
                st.success(get_text("profile_saved", f_lang))
                st.rerun()
            else:
                st.error("Failed to update profile.")

