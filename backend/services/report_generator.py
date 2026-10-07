"""
Farmer Diagnostic and Advisory Report Generator.
Generates focused Crop Disease Diagnostic Test Reports in PDF (via ReportLab) and CSV formats.
When disease is tested, the report features the disease diagnosis prominently,
leaving untested modules explicitly marked as empty.
"""

import io
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

from backend.utils.constants import REPORTS_DIR
from backend.utils.helpers import get_logger

logger = get_logger("ReportGenerator")


def generate_pdf_report(report_data: Dict[str, Any]) -> bytes:
    """
    Generates a dedicated Crop Disease Diagnostic Test Report PDF.
    Prominently displays the disease test diagnosis and leaves untested modules empty.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    primary_color = colors.HexColor("#1b5e20")  # Dark forest green
    accent_color = colors.HexColor("#2e7d32")
    alert_color = colors.HexColor("#c62828")   # Red for disease alert
    neutral_bg = colors.HexColor("#f8fafc")

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontSize=18,
        leading=22,
        textColor=primary_color,
        alignment=1,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#555555"),
        alignment=1,
        spaceAfter=12
    )

    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=12,
        leading=16,
        textColor=accent_color,
        spaceBefore=8,
        spaceAfter=5
    )

    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#222222")
    )

    bullet_style = ParagraphStyle(
        "BulletText",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#333333"),
        leftIndent=10,
        spaceAfter=3
    )

    elements = []

    # 1. Header & Title
    elements.append(Paragraph("🌾 SMART AGRI-PARTNER", title_style))
    elements.append(Paragraph("<b>PLANT DISEASE DIAGNOSTIC TEST REPORT</b><br/>AI-Assisted Crop Leaf Pathology Laboratory Record", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceAfter=10))

    # 2. Farmer & Test Identification Table
    farmer = report_data.get("farmer", {})
    disease = report_data.get("disease", {})
    now_str = datetime.now().strftime("%d %B %Y, %I:%M %p")
    test_id = disease.get("id", "TEST-" + datetime.now().strftime("%Y%m%d"))

    farmer_table_data = [
        [
            Paragraph("<b>Farmer Name:</b> " + str(farmer.get("name", "Farmer")), body_style),
            Paragraph("<b>Test Report ID:</b> #" + str(test_id), body_style)
        ],
        [
            Paragraph(f"<b>Location:</b> {farmer.get('village', '') or 'Rural'}, {farmer.get('district', 'Kolar')}, {farmer.get('state', 'Karnataka')}", body_style),
            Paragraph("<b>Date & Time:</b> " + now_str, body_style)
        ],
        [
            Paragraph(f"<b>Primary Crop:</b> {farmer.get('primary_crop', 'Tomato')}", body_style),
            Paragraph(f"<b>Land Holding:</b> {farmer.get('land_area', 2.0)} Acres", body_style)
        ]
    ]

    t_farmer = Table(farmer_table_data, colWidths=[270, 270])
    t_farmer.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f8e9")),
        ("PADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#c5e1a5")),
    ]))
    elements.append(t_farmer)
    elements.append(Spacer(1, 10))

    # 3. Primary Disease Diagnostic Findings
    elements.append(Paragraph("🌿 CROP DISEASE DIAGNOSTIC FINDINGS (PRIMARY TEST)", section_heading))

    crop_name = disease.get("crop", "Tomato")
    disease_name = disease.get("disease", "Unknown Condition")
    conf_val = disease.get("confidence", 0.0)
    conf_level = disease.get("confidence_level", "High")
    status_val = disease.get("status", "diseased").upper()

    status_bg = colors.HexColor("#ffebee") if status_val == "DISEASED" else colors.HexColor("#e8f5e9")
    status_border = alert_color if status_val == "DISEASED" else accent_color

    diag_data = [
        [
            Paragraph(f"<b>Tested Crop:</b><br/><font size=11 color='#1b5e20'><b>{crop_name}</b></font>", body_style),
            Paragraph(f"<b>Detected Disease:</b><br/><font size=11 color='#b71c1c'><b>{disease_name}</b></font>", body_style),
            Paragraph(f"<b>Model Confidence:</b><br/><b>{conf_val}%</b> ({conf_level})", body_style),
            Paragraph(f"<b>Health Status:</b><br/><b>{status_val}</b>", body_style)
        ]
    ]
    t_diag = Table(diag_data, colWidths=[130, 170, 130, 110])
    t_diag.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), status_bg),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("BOX", (0, 0), (-1, -1), 1, status_border),
    ]))
    elements.append(t_diag)
    elements.append(Spacer(1, 8))

    # 4. Detailed Pathology: Symptoms, Causes, Management
    guidance = disease.get("guidance", {})
    if guidance:
        # Symptoms
        symptoms = guidance.get("symptoms", [])
        if symptoms:
            elements.append(Paragraph("<b>Observed Foliar Symptoms:</b>", body_style))
            for s in symptoms[:3]:
                elements.append(Paragraph(f"• {s}", bullet_style))
            elements.append(Spacer(1, 4))

        # Causes
        causes = guidance.get("causes", [])
        if causes:
            elements.append(Paragraph("<b>Biological & Environmental Causes:</b>", body_style))
            for c in causes[:2]:
                elements.append(Paragraph(f"• {c}", bullet_style))
            elements.append(Spacer(1, 4))

        # Management
        mgmt = guidance.get("management", [])
        if mgmt:
            elements.append(Paragraph("<b>Safe Non-Chemical Agronomic Management (IPM):</b>", body_style))
            for m in mgmt[:3]:
                elements.append(Paragraph(f"• {m}", bullet_style))
            elements.append(Spacer(1, 4))

        # Prevention
        prev = guidance.get("prevention", [])
        if prev:
            elements.append(Paragraph("<b>Preventative Field Sanitation:</b>", body_style))
            for p in prev[:2]:
                elements.append(Paragraph(f"• {p}", bullet_style))
            elements.append(Spacer(1, 6))

    # Top Alternative Predictions if available
    top_preds = disease.get("top_predictions", [])
    if top_preds and len(top_preds) > 1:
        alt_text = " | ".join([f"{p.get('disease', '')}: {p.get('confidence', 0)}%" for p in top_preds[1:3]])
        elements.append(Paragraph(f"<b>Alternative Candidate Diagnoses:</b> <font color='#666666'>{alt_text}</font>", body_style))
        elements.append(Spacer(1, 8))

    # 5. Untested Modules Section (Explicitly marked empty as requested)
    elements.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#e0e0e0"), spaceAfter=6))
    elements.append(Paragraph("📋 OTHER FARM MODULES STATUS FOR THIS SCAN", section_heading))

    # Check if other modules were tested or should show empty
    has_custom_soil = report_data.get("include_soil", False)
    has_custom_weather = report_data.get("include_weather", False)
    has_custom_mandi = report_data.get("include_mandi", False)
    has_custom_econ = report_data.get("include_economic", False)

    other_modules_data = [
        [
            Paragraph("<b>Module</b>", body_style),
            Paragraph("<b>Test Status</b>", body_style),
            Paragraph("<b>Details / Notes</b>", body_style)
        ],
        [
            Paragraph("🧪 Soil Health & NPK", body_style),
            Paragraph("<font color='#9e9e9e'><i>[EMPTY / NOT TESTED]</i></font>", body_style),
            Paragraph("No laboratory soil sample submitted with this leaf scan.", bullet_style)
        ],
        [
            Paragraph("🌦️ Local Weather Advisory", body_style),
            Paragraph("<font color='#9e9e9e'><i>[EMPTY / NOT EVALUATED]</i></font>", body_style),
            Paragraph("Foliar diagnosis executed independently of station micro-climate.", bullet_style)
        ],
        [
            Paragraph("📈 APMC Mandi Benchmark", body_style),
            Paragraph("<font color='#9e9e9e'><i>[EMPTY / NOT EVALUATED]</i></font>", body_style),
            Paragraph("Wholesale price trends not linked to pathology testing.", bullet_style)
        ],
        [
            Paragraph("💰 Economic Loss Calculator", body_style),
            Paragraph("<font color='#9e9e9e'><i>[EMPTY / NOT EVALUATED]</i></font>", body_style),
            Paragraph("Financial revenue risk calculation not requested for this record.", bullet_style)
        ]
    ]

    t_other = Table(other_modules_data, colWidths=[150, 150, 240])
    t_other.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f5f5f5")),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#fafafa")),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(t_other)
    elements.append(Spacer(1, 10))

    # 6. Agricultural Safety Advisory Footer
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc"), spaceAfter=6))
    footer_text = (
        "<b>Important Agricultural Safety Notice:</b> This test report is generated by Smart Agri-Partner "
        "as an educational and diagnostic aid based on MobileNetV2 computer vision analysis. "
        "Recommendations focus strictly on cultural practices, aeration, and Integrated Pest Management (IPM). "
        "Do not apply synthetic chemical pesticides without consulting your local Krishi Vigyan Kendra (KVK) officer."
    )
    elements.append(Paragraph(footer_text, ParagraphStyle("Footer", parent=styles["Normal"], fontSize=7.5, textColor=colors.HexColor("#555555"), leading=9.5)))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def generate_csv_summary(report_data: Dict[str, Any]) -> str:
    """Generates a structured flat CSV record representing the disease test record."""
    farmer = report_data.get("farmer", {})
    disease = report_data.get("disease", {})

    record = {
        "test_timestamp": datetime.now().isoformat(),
        "farmer_name": farmer.get("name", "Farmer"),
        "district": farmer.get("district", ""),
        "state": farmer.get("state", ""),
        "crop_tested": disease.get("crop", ""),
        "diagnosed_disease": disease.get("disease", "Unknown"),
        "confidence_percentage": disease.get("confidence", 0.0),
        "confidence_level": disease.get("confidence_level", "High"),
        "health_status": disease.get("status", "diseased"),
        "soil_tested": "EMPTY / NOT TESTED",
        "weather_evaluated": "EMPTY / NOT TESTED",
        "mandi_evaluated": "EMPTY / NOT TESTED",
        "economic_loss_evaluated": "EMPTY / NOT TESTED"
    }

    df = pd.DataFrame([record])
    return df.to_csv(index=False)
