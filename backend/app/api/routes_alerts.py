"""
FloodGuard: Alerts & Preparedness Routes
"""

import os
import json
from typing import Dict, Any, List
from fastapi import APIRouter
from ..mcp.tools import get_preparedness_recommendations

router = APIRouter(prefix="/api/alerts", tags=["Emergency Alerts & Preparedness"])

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "stations.json")


@router.get("")
def get_active_alerts():
    """Generates active warning & danger alerts based on live sensor readings."""
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        stations = json.load(f)["stations"]
        
    alerts = []
    for stn in stations:
        tel = stn["current_telemetry"]
        risk_lvl = tel["risk_level"]
        if risk_lvl >= 2:
            severity = "CRITICAL DANGER" if risk_lvl == 3 else "HIGH FLOOD WARNING"
            alerts.append({
                "id": f"ALT_{stn['station_id']}",
                "station_name": stn["station_name"],
                "river": stn["river"],
                "severity": severity,
                "risk_level": risk_lvl,
                "risk_label": tel["risk_label"],
                "water_level_m": tel["river_water_level_m"],
                "danger_level_m": stn["danger_level_m"],
                "message": f"{stn['river']} stage at {stn['station_name']} is currently {tel['river_water_level_m']}m. Central Water Commission Danger Mark is {stn['danger_level_m']}m.",
                "action_advisory": "District emergency operations center alerted. Floodplain patrols activated."
            })
            
    return {
        "active_alert_count": len(alerts),
        "alerts": alerts
    }


@router.get("/recommendations/{risk_level}")
def get_recommendations(risk_level: str):
    """Retrieves non-binding emergency recommendations for a specific risk tier."""
    return get_preparedness_recommendations(risk_level)
