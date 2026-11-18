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


@router.get("/network/history")
def get_network_history():
    """Returns a deterministic synthetic 24-hour network-average series."""
    stations = _get_stations()
    if not stations:
        return {"data_mode": "synthetic", "data_source": "deterministic-demo-generator", "series": []}

    series = []
    for hour in range(24, -1, -1):
        progress = (24 - hour) / 24
        normalized_levels = []
        rainfall_values = []
        for index, station in enumerate(stations):
            telemetry = station["current_telemetry"]
            current_level = float(telemetry["river_water_level_m"])
            station_drift = 0.18 + (index % 4) * 0.08
            normalized_levels.append(current_level - station_drift * (1 - progress) - 0.04 * (progress ** 2))
            rainfall_values.append(float(telemetry["rainfall_24h_mm"]) * progress)

        series.append({
            "minutes_from_now": -hour * 60,
            "time_label": f"-{hour}h" if hour else "NOW",
            "average_water_level_m": round(sum(normalized_levels) / len(normalized_levels), 3),
            "average_rainfall_cumulative_mm": round(sum(rainfall_values) / len(rainfall_values), 2),
            "quality": "synthetic",
        })

    return {
        "data_mode": "synthetic",
        "data_source": "deterministic-demo-generator",
        "station_count": len(stations),
        "series": series,
    }


@router.get("/{station_id}/history")
def get_station_history(station_id: str):
    """Returns deterministic synthetic 24-hour chart samples for demonstration UI use."""
    stations = _get_stations()
    target = next((station for station in stations if station["station_id"].lower() == station_id.lower()), None)
    if not target:
        raise HTTPException(status_code=404, detail="Station not found")

    telemetry = target["current_telemetry"]
    current_level = float(telemetry["river_water_level_m"])
    rainfall = float(telemetry["rainfall_24h_mm"])
    samples = []
    for hour in range(24, -1, -1):
        progress = (24 - hour) / 24
        simulated_level = current_level - ((0.42 * (1 - progress)) + (0.08 * (progress ** 2)))
        simulated_rain = max(0.0, rainfall * (1 - progress) * (0.65 + 0.35 * ((hour % 5) / 5)))
        samples.append({
            "hour_offset": -hour,
            "river_water_level_m": round(simulated_level, 3),
            "rainfall_cumulative_mm": round(simulated_rain, 2),
            "quality": "synthetic",
        })

    return {
        "station_id": target["station_id"],
        "station_name": target["station_name"],
        "data_mode": "synthetic",
        "data_source": "deterministic-demo-generator",
        "series": samples,
    }


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
