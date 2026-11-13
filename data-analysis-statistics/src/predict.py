"""
Inference entry point for Model 1 v6: Next-Month Environmental Condition Prediction.
Provides fast prediction access for API endpoints and web UI without re-executing training.
"""
from __future__ import annotations

import json
from pathlib import Path


def predict_next_month(region: str | None = None, variable: str | None = None) -> dict:
    """Predict next-month environmental condition risk for African regions.
    
    Uses the frozen v6 model forecast manifest and bundle to predict the upcoming
    month date (e.g. 2025-01) from the latest available observation (2024-12).
    
    Args:
        region: Optional region identifier (e.g. 'North_Africa', 'north-africa', 'central-africa')
        variable: Optional variable identifier ('temperature_anomaly' or 'precipitation_mm')
        
    Returns:
        Structured prediction dictionary with target_horizon, latest_obs, records, and metadata.
    """
    base_dir = Path(__file__).resolve().parent
    candidates = [
        base_dir / "summary_v6.json",
        base_dir.parent / "data" / "summary_v6.json",
        Path(__file__).resolve().parents[2] / "model-1-environmental-prediction" / "summary_v6.json",
    ]
    summary_path = None
    for p in candidates:
        if p.exists():
            summary_path = p
            break
            
    if summary_path is None:
        return {
            "success": False,
            "error": "Model summary file (summary_v6.json) not found.",
            "records": []
        }
        
    with open(summary_path, "r", encoding="utf-8") as f:
        summary_data = json.load(f)
        
    forecast = summary_data.get("live_forecast", {})
    latest_obs = forecast.get("latest_obs", "2024-12")
    target_horizon = forecast.get("target_horizon", "2025-01")
    raw_records = forecast.get("records", [])
    
    region_map = {
        "sahel_region": ("West_Africa", "west-africa", "West Africa"),
        "west_africa": ("West_Africa", "west-africa", "West Africa"),
        "west-africa": ("West_Africa", "west-africa", "West Africa"),
        "south_africa": ("Southern_Africa", "southern-africa", "Southern Africa"),
        "southern_africa": ("Southern_Africa", "southern-africa", "Southern Africa"),
        "southern-africa": ("Southern_Africa", "southern-africa", "Southern Africa"),
        "north_africa": ("North_Africa", "north-africa", "North Africa"),
        "north-africa": ("North_Africa", "north-africa", "North Africa"),
        "central_africa": ("Central_Africa", "central-africa", "Central Africa"),
        "central-africa": ("Central_Africa", "central-africa", "Central Africa"),
        "east_africa": ("East_Africa", "east-africa", "East Africa"),
        "east-africa": ("East_Africa", "east-africa", "East Africa"),
    }
    
    target_var_map = {
        "Temperature (High)": "temperature_anomaly",
        "Precipitation Rate": "precipitation_mm",
    }
    
    formatted_records = []
    for r in raw_records:
        reg_raw = str(r.get("region", "")).lower()
        canonical, slug, display_name = region_map.get(
            reg_raw, 
            (r.get("region", ""), str(r.get("region", "")).lower().replace("_", "-"), r.get("region", "").replace("_", " "))
        )
        
        target = r.get("target", "")
        var_id = target_var_map.get(target, "unknown")
        tier = r.get("tier", "Unknown")
        pred_z = r.get("pred_z")
        risk_pct = r.get("risk_pct")
        lift = r.get("lift")
        
        is_temp = "Temperature" in target
        tier_validated = is_temp
        
        if tier == "N/A - dry season (degenerate)":
            interp = f"In {display_name}, {target_horizon} falls during the climatological dry season (>30% zero rainfall historically). Active precipitation anomaly forecasting is masked out to prevent degenerate false alarms."
        elif is_temp:
            interp = f"For {target_horizon}, {display_name} is projected in the {tier} risk tier for extreme warmth ({risk_pct}% probability, {lift}x baseline lift). The temperature model has statistically confirmed skill on out-of-fold test sets (ROC-AUC = 0.753)."
        else:
            interp = f"For {target_horizon}, {display_name} has a modeled precipitation anomaly risk score of {risk_pct}% ({lift}x lift). Notice: Precipitation risk tiers are marked NOT VALIDATED due to high regional variance."
            
        formatted_records.append({
            "region": canonical,
            "region_id": slug,
            "region_name": display_name,
            "target": target,
            "variable_id": var_id,
            "pred_z": pred_z,
            "risk_pct": risk_pct,
            "lift": lift,
            "tier": tier,
            "tier_validated": tier_validated,
            "interpretation": interp,
        })
        
    filtered = formatted_records
    if region and region.lower() != "all":
        reg_query = region.lower().replace(" ", "_").replace("-", "_")
        filtered = [rec for rec in filtered if reg_query in (rec["region"].lower(), rec["region_id"].replace("-", "_"), rec["region_name"].lower().replace(" ", "_"))]
        
    if variable:
        var_query = variable.lower()
        if "temp" in var_query:
            filtered = [rec for rec in filtered if rec["variable_id"] == "temperature_anomaly"]
        elif "precip" in var_query or "rain" in var_query:
            filtered = [rec for rec in filtered if rec["variable_id"] == "precipitation_mm"]
            
    return {
        "success": True,
        "latest_observation": latest_obs,
        "target_horizon": target_horizon,
        "region_filter": region,
        "variable_filter": variable,
        "records": filtered,
        "model_metadata": {
            "model_version": "Model 1 v6 Final Freeze Engine",
            "temperature_skill": "CONFIRMED (Test ROC-AUC: 0.753 vs Baseline 0.675, Diff: +0.079, 4/4 Conditions Passed)",
            "precipitation_skill": "NO RELIABLE SKILL (Test ROC-AUC: 0.562 vs Baseline 0.520, Diff: +0.043, Failed Cond B)",
            "validation_protocol": "3-Fold Walk-Forward Cross Validation + Held-Out Test Set (2022–2024)",
        }
    }


if __name__ == "__main__":
    import pprint
    res = predict_next_month()
    print("Prediction Result (All Regions):")
    pprint.pprint(res)
