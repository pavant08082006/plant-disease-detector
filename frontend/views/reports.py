"""
Crop Diagnostic Test Reports View.
Displays verified disease test reports, detailed diagnosis dossiers, PDF/CSV downloads,
and direct email delivery via SMTP (host: Lokeshmmankith@gmail.com).
Untested modules are kept empty in the report as requested.
"""

import json
from pathlib import Path
import streamlit as st
import pandas as pd

from backend.database.db import get_all_test_reports, log_disease_scan
from backend.services.report_generator import generate_pdf_report, generate_csv_summary
from backend.services.email_service import send_report_email, get_smtp_config
from backend.services.translation_service import get_text
from backend.utils.constants import DATA_DIR


@st.cache_data
def load_kb_data():
    """Loads agronomic knowledge base."""
    kb_file = DATA_DIR / "diseases.json"
    if kb_file.exists():
        with open(kb_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def render_reports(farmer: dict, lang: str):
    """Renders test reports view with email dispatcher."""
    st.title("📊 Crop Diagnostic Test Reports")
    st.write(
        "View and export your verified plant disease laboratory test reports. "
        "Review diagnostic confidence, agronomic advisories, and email PDF dossiers directly."
    )

    kb = load_kb_data()
    test_reports = get_all_test_reports(farmer_id=farmer.get("id"))

    # Quick seed action if no test scans exist yet
    if not test_reports:
        st.info("ℹ️ No crop leaf test scans recorded yet for your account.")
        col_seed, _ = st.columns([1, 1])
        with col_seed:
            if st.button("⚡ Generate Benchmark Test Report (Tomato Early Blight)", type="primary"):
                sample_scan = {
                    "crop": "Tomato",
                    "disease": "Early Blight",
                    "confidence": 94.7,
                    "confidence_level": "High",
                    "status": "diseased",
                    "image_path": "dataset/plantvillage dataset/color/Tomato___Early_blight/sample.JPG"
                }
                log_disease_scan(sample_scan, farmer_id=farmer.get("id", 1))
                st.success("Benchmark test report created!")
                st.rerun()
        st.caption("Or navigate to **🌿 Disease Detection** to upload and diagnose a leaf image.")
        return

    # 1. Test Summary Statistics
    total_tests = len(test_reports)
    diseased_tests = sum(1 for r in test_reports if r.get("status") == "diseased")
    healthy_tests = total_tests - diseased_tests

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Tests Recorded", total_tests)
    m2.metric("Diseased Detections ⚠️", diseased_tests)
    m3.metric("Healthy Observations ✅", healthy_tests)

    st.markdown("---")

    # 2. Test Reports Selection Dropdown
    st.subheader("📋 Select Test Report to Inspect")
    report_options = [
        f"Test #{r['id']} | {r['crop']} — {r['disease']} ({r['confidence']}% Conf.) — {r['created_at']}"
        for r in test_reports
    ]

    selected_idx = st.selectbox(
        "Choose Test Record:",
        range(len(report_options)),
        format_func=lambda i: report_options[i]
    )
    current_test = test_reports[selected_idx]

    # Match KB info
    raw_key = f"{current_test['crop']}___{current_test['disease'].replace(' ', '_')}"
    disease_info = kb.get(raw_key, {})
    if not disease_info:
        for k, v in kb.items():
            if v.get("disease", "").lower() == current_test["disease"].lower():
                disease_info = v
                break

    # 3. Test Report Details Card (Disease Diagnosis Only)
    with st.container(border=True):
        st.markdown(f"### 🧪 Test Report #{current_test['id']}: **{current_test['crop']} — {current_test['disease']}**")
        st.caption(f"Tested on: **{current_test['created_at']}** | Status: **{current_test['status'].upper()}**")

        d_col1, d_col2, d_col3 = st.columns(3)
        d_col1.metric("Tested Crop", current_test["crop"])
        d_col2.metric("Diagnosed Condition", current_test["disease"])
        d_col3.metric("Model Confidence", f"{current_test['confidence']}%", delta=current_test.get("confidence_level", "High"))

        if disease_info:
            st.markdown("#### 🔍 Observed Foliar Symptoms")
            symptoms_list = disease_info.get("symptoms", ["Foliar spots observed on leaf tissue."])
            for s in symptoms_list[:3]:
                st.markdown(f"- {s}")

            st.markdown("#### 🛡️ Safe Non-Chemical Agronomic Management")
            mgmt_list = disease_info.get("management", ["Maintain orchard hygiene and avoid overhead splash."])
            for m in mgmt_list[:3]:
                st.markdown(f"- 🌿 {m}")

            st.info(f"📌 **Advisory Note:** {disease_info.get('safety_notice', 'Consult your local KVK agricultural extension officer.')}")

        # Note about other modules being empty
        with st.expander("ℹ️ Other Modules Status for this Test Report", expanded=False):
            st.write("• **Soil Health (NPK):** `[EMPTY / NOT TESTED]`")
            st.write("• **Local Weather:** `[EMPTY / NOT TESTED]`")
            st.write("• **APMC Mandi Benchmark:** `[EMPTY / NOT TESTED]`")
            st.write("• **Economic Loss Calculator:** `[EMPTY / NOT TESTED]`")
            st.caption("This test report is dedicated specifically to the crop leaf disease diagnosis.")

    # 4. Build Report Payload for Export & Email (Focused strictly on disease test)
    report_payload = {
        "farmer": farmer,
        "disease": {
            "id": current_test["id"],
            "crop": current_test["crop"],
            "disease": current_test["disease"],
            "confidence": current_test["confidence"],
            "confidence_level": current_test.get("confidence_level", "High"),
            "status": current_test["status"],
            "guidance": disease_info
        },
        # Other modules explicitly flagged as not included/empty
        "include_soil": False,
        "include_weather": False,
        "include_mandi": False,
        "include_economic": False
    }

    # Generate PDF bytes
    pdf_bytes = generate_pdf_report(report_payload)
    pdf_filename = f"Smart_Agri_Report_Test_{current_test['id']}_{current_test['crop']}.pdf"

    st.markdown("---")

    # 5. Export & Email Actions
    c_download, c_email = st.columns([1, 1.3])

    with c_download:
        st.subheader("📥 Download Test Report")
        
        # Download PDF Button
        st.download_button(
            label="📄 Download PDF Disease Report",
            data=pdf_bytes,
            file_name=pdf_filename,
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )

        # Download CSV Button
        csv_str = generate_csv_summary(report_payload)
        st.download_button(
            label="📊 Download CSV Summary",
            data=csv_str,
            file_name=f"Smart_Agri_Test_{current_test['id']}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with c_email:
        st.subheader("📧 Send Report to Email")
        _, _, host_user, _ = get_smtp_config()
        st.caption(f"Host Dispatcher: **{host_user}** (Gmail SMTP)")

        # Recipient Selection options
        recipient_mode = st.radio(
            "Select Recipient Email:",
            [
                f"Send to Host Email ({host_user})",
                "Enter Custom Email Address"
            ],
            key="rep_mode_choice"
        )

        if "Host Email" in recipient_mode:
            target_email = host_user
        else:
            custom_email = st.text_input(
                "Enter Email Address:",
                value="",
                placeholder="e.g., student@college.edu or farmer@gmail.com",
                key="custom_recipient_email"
            )
            target_email = custom_email.strip()

        email_subject = st.text_input(
            "Email Subject:",
            value=f"Smart Agri-Partner Test Report #{current_test['id']}: {current_test['crop']} - {current_test['disease']}",
            key="report_email_subject"
        )

        email_notes = st.text_area(
            "Message Body:",
            value=f"Attached is your verified crop leaf disease diagnostic test report for {current_test['crop']} ({current_test['disease']}, {current_test['confidence']}% certainty).",
            height=70,
            key="report_email_notes"
        )

        if st.button("✉️ Send Test Report via Email", type="primary", use_container_width=True, key="btn_send_report_email"):
            if not target_email or "@" not in target_email:
                st.warning("Please provide a valid recipient email address.")
            else:
                with st.spinner(f"Sending diagnostic PDF report to {target_email}..."):
                    success, msg = send_report_email(
                        recipient_email=target_email,
                        subject=email_subject,
                        body_text=email_notes,
                        pdf_bytes=pdf_bytes,
                        filename=pdf_filename,
                        farmer_name=farmer.get("name", "Farmer")
                    )
                    if success:
                        st.success(f"✅ {msg}")
                        st.info("💡 **Tip:** If checking for the email, please check both your **Inbox** and **Spam / Junk** folder (Gmail may occasionally place automated attachments from new senders in Spam).")
                    else:
                        st.error(f"❌ {msg}")
