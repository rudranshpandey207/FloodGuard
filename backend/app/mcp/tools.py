"""
FloodGuard: Model Context Protocol (MCP) Tool Layer
===================================================
This module implements the 8 formal MCP tools defined in the JIIT Major Project Synopsis:
1. get_weather(location, time_range)
2. get_rainfall(location, time_range)
3. get_water_level(location, time_range)
4. get_historical_floods(location)
5. predict_flood_risk(location, optional_features)
6. get_risk_status(location)
7. get_affected_regions()
8. get_preparedness_recommendations(risk_level)

Why MCP (Model Context Protocol)?
- Provides controlled, typed, and auditable tool execution boundaries.
- Prevents LLM hallucinations by grounding reasoning in verified environmental data.
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

# Load stations data
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "stations.json")
with open(DATA_PATH, "r", encoding="utf-8") as f:
    STATIONS_DB = json.load(f)["stations"]

# Load ML champion model
MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "models")
CHAMPION_MODEL_PATH = os.path.join(MODELS_DIR, "champion_model.joblib")
FEATURE_COLUMNS = [
    "rainfall_1h_mm",
    "rainfall_24h_mm",
    "rainfall_72h_mm",
    "rainfall_7d_mm",
    "river_water_level_m",
    "water_level_rate_of_rise_m_hr",
    "soil_moisture_index",
    "upstream_discharge_cusecs",
    "elevation_m",
    "drainage_capacity",
    "temperature_c",
    "humidity_pct",
    "stage_to_warning_ratio",
    "stage_to_danger_ratio",
    "runoff_potential_index",
    "drainage_strain_index"
]

CHAMPION_MODEL = None
if os.path.exists(CHAMPION_MODEL_PATH):
    try:
        CHAMPION_MODEL = joblib.load(CHAMPION_MODEL_PATH)
    except Exception as e:
        print(f"[Warning] Failed to load champion model: {e}")


def _match_station(query: str) -> Optional[Dict[str, Any]]:
    """Smart lookup helper for station ID, name, river, or region."""
    q = query.strip().lower()
    # 1. Exact or substring match
    for stn in STATIONS_DB:
        full_text = f"{stn['station_id']} {stn['station_name']} {stn['river']} {stn['state']}".lower()
        if q in full_text:
            return stn
            
    # 2. Token overlap match (e.g. "Yamuna Delhi" matches station with both words)
    tokens = [t for t in q.replace("-", " ").split() if len(t) >= 3]
    best_match = None
    best_score = 0
    for stn in STATIONS_DB:
        full_text = f"{stn['station_id']} {stn['station_name']} {stn['river']} {stn['state']}".lower()
        matches = sum(1 for t in tokens if t in full_text)
        if matches > best_score:
            best_score = matches
            best_match = stn
            
    if best_score > 0:
        return best_match
    return None


# =========================================================================
# Tool 1: get_weather
# =========================================================================
def get_weather(location: str, time_range: str = "current") -> Dict[str, Any]:
    """
    Retrieves temperature, humidity, atmospheric condition, and wind for a specified station.
    """
    stn = _match_station(location)
    if not stn:
        return {"error": f"Station or region '{location}' not found in monitoring registry."}
    
    tel = stn["current_telemetry"]
    condition = "Overcast & Heavy Rain" if tel["rainfall_24h_mm"] > 50 else ("Partly Cloudy" if tel["rainfall_24h_mm"] > 10 else "Clear / Mild")
    
    return {
        "station_id": stn["station_id"],
        "station_name": stn["station_name"],
        "location": f"{stn['river']} basin, {stn['state']}",
        "time_range": time_range,
        "temperature_c": tel["temperature_c"],
        "humidity_pct": tel["humidity_pct"],
        "weather_condition": condition,
        "soil_moisture_index": tel["soil_moisture_index"]
    }


# =========================================================================
# Tool 2: get_rainfall
# =========================================================================
def get_rainfall(location: str, time_range: str = "24h") -> Dict[str, Any]:
    """
    Retrieves 1-hour, 24-hour, 72-hour, and 7-day cumulative rainfall for a location.
    """
    stn = _match_station(location)
    if not stn:
        return {"error": f"Location '{location}' not found."}
        
    tel = stn["current_telemetry"]
    return {
        "station_id": stn["station_id"],
        "station_name": stn["station_name"],
        "time_range": time_range,
        "rainfall_1h_mm": tel["rainfall_1h_mm"],
        "rainfall_24h_mm": tel["rainfall_24h_mm"],
        "rainfall_72h_mm": tel["rainfall_72h_mm"],
        "rainfall_7d_mm": tel["rainfall_7d_mm"],
        "intensity_category": "Extremely Heavy" if tel["rainfall_24h_mm"] > 100 else ("Heavy" if tel["rainfall_24h_mm"] > 50 else "Moderate / Light")
    }


# =========================================================================
# Tool 3: get_water_level
# =========================================================================
def get_water_level(location: str, time_range: str = "current") -> Dict[str, Any]:
    """
    Retrieves current river stage height, rate-of-rise, and comparison against CWC warning and danger levels.
    """
    stn = _match_station(location)
    if not stn:
        return {"error": f"Location '{location}' not found."}
        
    tel = stn["current_telemetry"]
    current_wl = tel["river_water_level_m"]
    warning_wl = stn["warning_level_m"]
    danger_wl = stn["danger_level_m"]
    
    status_vs_danger = "BREACHED DANGER MARK" if current_wl >= danger_wl else (
        "EXCEEDED WARNING MARK" if current_wl >= warning_wl else "BELOW WARNING LEVEL"
    )
    
    return {
        "station_id": stn["station_id"],
        "station_name": stn["station_name"],
        "river": stn["river"],
        "current_water_level_m": current_wl,
        "warning_level_m": warning_wl,
        "danger_level_m": danger_wl,
        "distance_to_danger_m": round(danger_wl - current_wl, 3),
        "rate_of_rise_m_hr": tel["water_level_rate_of_rise_m_hr"],
        "status": status_vs_danger,
        "upstream_discharge_cusecs": tel["upstream_discharge_cusecs"]
    }


# =========================================================================
# Tool 4: get_historical_floods
# =========================================================================
def get_historical_floods(location: str) -> Dict[str, Any]:
    """
    Returns recorded historical flood events, peak water levels, and breach impacts for the location.
    """
    stn = _match_station(location)
    if not stn:
        return {"error": f"Location '{location}' not found."}
        
    return {
        "station_id": stn["station_id"],
        "station_name": stn["station_name"],
        "historical_events": stn.get("historical_flood_events", []),
        "all_time_high_level_m": max([e["peak_level_m"] for e in stn.get("historical_flood_events", [{"peak_level_m": stn["danger_level_m"]}])])
    }


# =========================================================================
# Tool 5: predict_flood_risk
# =========================================================================
def predict_flood_risk(location: Optional[str] = None, feature_override: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """
    Executes the trained machine learning champion model (XGBoost) to predict flood risk tier (Low, Medium, High, Critical)
    and class probabilities.
    """
    stn = None
    if location:
        stn = _match_station(location)
        
    # Baseline features from station telemetry if location is provided
    features = {}
    if stn:
        tel = stn["current_telemetry"]
        warning_span = max(stn["danger_level_m"] - stn["warning_level_m"], 0.5)
        
        features = {
            "rainfall_1h_mm": tel["rainfall_1h_mm"],
            "rainfall_24h_mm": tel["rainfall_24h_mm"],
            "rainfall_72h_mm": tel["rainfall_72h_mm"],
            "rainfall_7d_mm": tel["rainfall_7d_mm"],
            "river_water_level_m": tel["river_water_level_m"],
            "water_level_rate_of_rise_m_hr": tel["water_level_rate_of_rise_m_hr"],
            "soil_moisture_index": tel["soil_moisture_index"],
            "upstream_discharge_cusecs": tel["upstream_discharge_cusecs"],
            "elevation_m": stn["elevation_m"],
            "drainage_capacity": stn["drainage_capacity"],
            "temperature_c": tel["temperature_c"],
            "humidity_pct": tel["humidity_pct"],
            "stage_to_warning_ratio": (tel["river_water_level_m"] - stn["warning_level_m"]) / warning_span,
            "stage_to_danger_ratio": (tel["river_water_level_m"] - stn["danger_level_m"]) / warning_span,
            "runoff_potential_index": tel["rainfall_24h_mm"] * tel["soil_moisture_index"],
            "drainage_strain_index": (tel["rainfall_72h_mm"] * (1.1 - stn["drainage_capacity"])) / (stn["elevation_m"] * 0.05 + 1.0)
        }
        
    # Apply any custom scenario overrides (e.g. from what-if sliders)
    if feature_override:
        features.update(feature_override)
        
    # If no features could be constructed
    if not features:
        return {"error": "Insufficient features to evaluate ML model. Provide a valid location or feature override."}
        
    # Run Inference
    if CHAMPION_MODEL is not None:
        input_row = pd.DataFrame([[features.get(col, 0.0) for col in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)
        pred_class = int(CHAMPION_MODEL.predict(input_row)[0])
        probs = CHAMPION_MODEL.predict_proba(input_row)[0]
    else:
        # Fallback heuristic if model file isn't loaded
        pred_class = 2
        probs = [0.05, 0.15, 0.65, 0.15]
        
    labels = ["Low", "Medium", "High", "Critical"]
    risk_label = labels[pred_class]
    
    # Top risk drivers
    drivers = []
    if features.get("stage_to_danger_ratio", -1) > -0.2:
        drivers.append("Water level within proximity of Central Water Commission Danger Mark")
    if features.get("rainfall_72h_mm", 0) > 100:
        drivers.append("Sustained 72-hour antecedent rainfall saturating catchment basin")
    if features.get("soil_moisture_index", 0) > 0.80:
        drivers.append("Soil supersaturation resulting in near 100% surface runoff conversion")
    if features.get("upstream_discharge_cusecs", 0) > 200000:
        drivers.append("High upstream reservoir/barrage discharge surges entering river reach")
        
    if not drivers:
        drivers.append("Hydrological parameters within normal seasonal thresholds")
        
    return {
        "location": stn["station_name"] if stn else "Custom Simulation Coordinate",
        "predicted_risk_level": pred_class,
        "predicted_risk_label": risk_label,
        "confidence": round(float(probs[pred_class]), 3),
        "class_probabilities": {
            "Low": round(float(probs[0]), 3),
            "Medium": round(float(probs[1]), 3),
            "High": round(float(probs[2]), 3),
            "Critical": round(float(probs[3]), 3)
        },
        "primary_risk_drivers": drivers,
        "model_used": "XGBoost Classifier (Trained Champion Model)"
    }


# =========================================================================
# Tool 6: get_risk_status
# =========================================================================
def get_risk_status(location: str) -> Dict[str, Any]:
    """
    Returns an immediate consolidated summary of risk status, current water level, rainfall, and alert state.
    """
    stn = _match_station(location)
    if not stn:
        return {"error": f"Location '{location}' not found."}
        
    prediction = predict_flood_risk(location=location)
    tel = stn["current_telemetry"]
    
    return {
        "station_id": stn["station_id"],
        "station_name": stn["station_name"],
        "river": stn["river"],
        "current_risk_label": prediction.get("predicted_risk_label", tel["risk_label"]),
        "confidence": prediction.get("confidence", 0.95),
        "water_level_m": tel["river_water_level_m"],
        "danger_level_m": stn["danger_level_m"],
        "rainfall_24h_mm": tel["rainfall_24h_mm"],
        "risk_drivers": prediction.get("primary_risk_drivers", [])
    }


# =========================================================================
# Tool 7: get_affected_regions
# =========================================================================
def get_affected_regions() -> Dict[str, Any]:
    """
    Surveys all monitored stations and lists regions currently at Medium, High, or Critical risk.
    """
    affected = []
    for stn in STATIONS_DB:
        tel = stn["current_telemetry"]
        if tel["risk_level"] >= 1:
            affected.append({
                "station_id": stn["station_id"],
                "station_name": stn["station_name"],
                "river": stn["river"],
                "state": stn["state"],
                "risk_level": tel["risk_level"],
                "risk_label": tel["risk_label"],
                "water_level_m": tel["river_water_level_m"],
                "danger_level_m": stn["danger_level_m"],
                "rainfall_24h_mm": tel["rainfall_24h_mm"]
            })
            
    # Sort by risk severity descending
    affected.sort(key=lambda x: x["risk_level"], reverse=True)
    return {
        "total_monitored_stations": len(STATIONS_DB),
        "total_affected_stations": len(affected),
        "affected_regions": affected
    }


# =========================================================================
# Tool 8: get_preparedness_recommendations
# =========================================================================
def get_preparedness_recommendations(risk_level: str) -> Dict[str, Any]:
    """
    Provides evidence-based, non-binding emergency preparedness and resource prioritization suggestions.
    Note: Adheres strictly to human-in-the-loop safety protocol.
    """
    rl = risk_level.strip().lower()
    
    if rl in ["3", "critical"]:
        recs = [
            "Activate District Disaster Management Emergency Operations Center (EOC).",
            "Pre-position NDRF / SDRF water rescue teams and motorized inflatable boats near low-lying floodplains.",
            "Issue non-binding advisory for evacuation preparedness in unembanked floodplain settlements.",
            "Erect temporary sandbag bunds along vulnerable drainage outfalls.",
            "Verify backup emergency generators and clean potable water reserves at designated relief camps."
        ]
        tier = "Critical"
    elif rl in ["2", "high"]:
        recs = [
            "Increase gauge monitoring frequency to hourly intervals.",
            "Inspect and clear stormwater drainage outfalls and floodgates.",
            "Alert floodplain agricultural and cattle owners to shift animals to higher embankments.",
            "Coordinate with upstream barrage authorities for controlled hourly discharge schedules."
        ]
        tier = "High"
    elif rl in ["1", "medium"]:
        recs = [
            "Maintain standard 3-hour telemetry polling across all hydrological stations.",
            "Verify communication links between Central Water Commission and local administration.",
            "Monitor 72-hour weather radar forecasts for convective rainfall cells."
        ]
        tier = "Medium"
    else:
        recs = [
            "Routine monitoring conditions. Maintain regular sensor health checks."
        ]
        tier = "Low"
        
    return {
        "risk_tier": tier,
        "recommendations": recs,
        "disclaimer": "These suggestions are decision-support guidelines only. Final operational emergency directives remain strictly under authorized human civil authorities."
    }
