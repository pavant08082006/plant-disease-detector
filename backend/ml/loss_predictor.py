"""
Economic Loss & Yield Impact Predictor.
Calculates crop yield loss, financial revenue impact, and economic exposure
due to diagnosed foliar disease severity.
"""

from typing import Dict, Any


def calculate_economic_loss(
    crop: str = "Tomato",
    land_area_acres: float = 2.0,
    expected_yield_per_acre: float = 120.0,  # quintals/acre
    market_price_per_quintal: float = 2200.0,  # ₹/quintal
    disease_severity_level: str = "Moderate",  # Low, Moderate, Severe
    custom_yield_loss_pct: float = None,
    cultivation_cost_per_acre: float = 45000.0,
    other_expenses: float = 5000.0
) -> Dict[str, Any]:
    """
    Computes expected agricultural economics and estimated disease loss.
    All figures are estimated advisories and not guaranteed outcomes.
    """
    # 1. Total baseline production
    total_expected_yield_qtl = round(land_area_acres * expected_yield_per_acre, 2)
    expected_gross_revenue = round(total_expected_yield_qtl * market_price_per_quintal, 2)
    total_production_cost = round((land_area_acres * cultivation_cost_per_acre) + other_expenses, 2)
    expected_net_profit = round(expected_gross_revenue - total_production_cost, 2)

    # 2. Disease Loss Estimation Percentage
    if custom_yield_loss_pct is not None:
        loss_pct = max(0.0, min(100.0, float(custom_yield_loss_pct)))
    else:
        severity_map = {
            "None / Healthy": 0.0,
            "Low (Early Stage)": 10.0,
            "Moderate (Spreading)": 25.0,
            "Severe (Widespread)": 50.0
        }
        loss_pct = severity_map.get(disease_severity_level, 20.0)

    # 3. Loss Calculations
    lost_yield_qtl = round(total_expected_yield_qtl * (loss_pct / 100.0), 2)
    realized_yield_qtl = round(total_expected_yield_qtl - lost_yield_qtl, 2)
    
    estimated_income_loss = round(lost_yield_qtl * market_price_per_quintal, 2)
    realized_gross_revenue = round(realized_yield_qtl * market_price_per_quintal, 2)
    realized_net_profit = round(realized_gross_revenue - total_production_cost, 2)

    # 4. Risk Categorization
    if loss_pct <= 5.0:
        risk_level = "Minimal Risk"
        risk_color = "#10B981"
        action_plan = "Crop health is sound. Maintain preventative scouting and routine fertigation."
    elif loss_pct <= 20.0:
        risk_level = "Moderate Economic Risk"
        risk_color = "#F59E0B"
        action_plan = "Early foliar sanitation, infected leaf pruning, and airflow improvement can safeguard ~75% of profits."
    else:
        risk_level = "High Financial Hazard"
        risk_color = "#EF4444"
        action_plan = "Urgent agronomic intervention required. Consult local KVK officer to prevent total crop loss."

    return {
        "crop": crop,
        "land_area_acres": land_area_acres,
        "loss_pct": loss_pct,
        "disease_severity_level": disease_severity_level,
        "total_expected_yield_qtl": total_expected_yield_qtl,
        "realized_yield_qtl": realized_yield_qtl,
        "lost_yield_qtl": lost_yield_qtl,
        "market_price_per_quintal": market_price_per_quintal,
        "total_production_cost": total_production_cost,
        "expected_gross_revenue": expected_gross_revenue,
        "realized_gross_revenue": realized_gross_revenue,
        "estimated_income_loss": estimated_income_loss,
        "expected_net_profit": expected_net_profit,
        "realized_net_profit": realized_net_profit,
        "risk_level": risk_level,
        "risk_color": risk_color,
        "action_plan": action_plan,
        "disclaimer": "All financial outcomes are estimated advisories based on farmer-provided metrics and do not constitute guaranteed returns."
    }

