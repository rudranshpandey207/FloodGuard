"""
FloodGuard: Stations & Telemetry Routes
"""

import os
import json
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

router = APIRouter(prefix="/api/stations", tags=["Stations & Telemetry"])

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "stations.json")


def _get_stations():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)["stations"]


def _save_stations(stations):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump({"stations": stations}, f, indent=2)


class TelemetryUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rainfall_1h_mm: Optional[float] = Field(default=None, ge=0)
    rainfall_24h_mm: Optional[float] = Field(default=None, ge=0)
    rainfall_72h_mm: Optional[float] = Field(default=None, ge=0)
    river_water_level_m: Optional[float] = None
    water_level_rate_of_rise_m_hr: Optional[float] = None
    soil_moisture_index: Optional[float] = Field(default=None, ge=0, le=1)
    upstream_discharge_cusecs: Optional[float] = Field(default=None, ge=0)


@router.get("", response_model=List[Dict[str, Any]])
def get_all_stations():
    """Retrieve all monitored river stations with live telemetry."""
    return _get_stations()


@router.get("/{station_id}")
def get_station_by_id(station_id: str):
    """Retrieve detailed telemetry and historical floods for a specific station."""
    stations = _get_stations()
    for stn in stations:
        if stn["station_id"].lower() == station_id.lower():
            return stn
    raise HTTPException(status_code=404, detail=f"Station '{station_id}' not found.")


@router.post("/{station_id}/telemetry")
def update_station_telemetry(station_id: str, update: TelemetryUpdate):
    """Update live telemetry for a station (used by the Scenario Simulator)."""
    stations = _get_stations()
    target = None
    for stn in stations:
        if stn["station_id"].lower() == station_id.lower():
            target = stn
            break
            
    if not target:
        raise HTTPException(status_code=404, detail="Station not found")
        
    tel = target["current_telemetry"]
    data = update.model_dump(exclude_unset=True)
    tel.update(data)
    
    # Recalculate risk level based on updated stage
    wl = tel["river_water_level_m"]
    warn = target["warning_level_m"]
    dang = target["danger_level_m"]
    
    if wl >= dang:
        tel["risk_level"] = 3
        tel["risk_label"] = "Critical"
    elif wl >= warn:
        tel["risk_level"] = 2
        tel["risk_label"] = "High"
    elif wl >= (warn - 0.75) or tel["rainfall_72h_mm"] > 60:
        tel["risk_level"] = 1
        tel["risk_label"] = "Medium"
    else:
        tel["risk_level"] = 0
        tel["risk_label"] = "Low"
        
    _save_stations(stations)
    return {"message": "Telemetry updated successfully", "station": target}
