"""External data-source integrations for FloodGuard.

Open-Meteo provides keyless weather observations/forecasts. Its values are optional
adapters for scenario preparation; gauge level and discharge remain station data.
"""

import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Dict, Any, Optional

import httpx
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/integrations", tags=["External Integrations"])

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "stations.json")
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def _load_stations():
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        return json.load(file)["stations"]


def _find_station(station_id: str) -> Optional[Dict[str, Any]]:
    station_id_lower = station_id.lower()
    return next((station for station in _load_stations() if station["station_id"].lower() == station_id_lower), None)


def summarize_hourly_weather(payload: Dict[str, Any], now: Optional[datetime] = None) -> Dict[str, Any]:
    """Summarize Open-Meteo hourly arrays into FloodGuard rolling inputs."""
    hourly = payload.get("hourly") or {}
    times = hourly.get("time") or []
    if not times:
        raise ValueError("Open-Meteo response did not contain hourly time data")

    if now is None:
        now = datetime.now(ZoneInfo("Asia/Kolkata"))
    now = now.replace(minute=0, second=0, microsecond=0)

    index = -1
    for candidate_index, time_text in enumerate(times):
        try:
            candidate = datetime.fromisoformat(time_text)
        except (TypeError, ValueError):
            continue
        candidate_comparable = candidate.replace(tzinfo=None) if candidate.tzinfo else candidate
        now_comparable = now.replace(tzinfo=None)
        if candidate_comparable <= now_comparable:
            index = candidate_index
        else:
            break

    if index < 0:
        index = 0

    def values(name: str):
        return hourly.get(name) or []

    precipitation = values("precipitation")
    temperatures = values("temperature_2m")
    humidity = values("relative_humidity_2m")
    soil = values("soil_moisture_0_to_7cm")

    def sum_last(hours: int) -> float:
        start = max(0, index - hours + 1)
        return round(sum(float(item or 0) for item in precipitation[start:index + 1]), 2)

    def last_value(items):
        if not items:
            return None
        try:
            return float(items[index])
        except (IndexError, TypeError, ValueError):
            return None

    if precipitation:
        rainfall_1h = round(sum_last(1), 2)
        rainfall_24h = sum_last(24)
        rainfall_72h = sum_last(72)
        rainfall_7d = sum_last(168)
    else:
        rainfall_1h = rainfall_24h = rainfall_72h = rainfall_7d = None

    return {
        "timestamp": times[index],
        "rainfall_1h_mm": rainfall_1h,
        "rainfall_24h_mm": rainfall_24h,
        "rainfall_72h_mm": rainfall_72h,
        "rainfall_7d_mm": rainfall_7d,
        "temperature_c": last_value(temperatures),
        "humidity_pct": last_value(humidity),
        "soil_moisture_index": last_value(soil),
    }


@router.get("/weather/{station_id}")
def get_open_meteo_weather(station_id: str):
    """Fetch optional live weather features for a registered station from Open-Meteo."""
    station = _find_station(station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    params = {
        "latitude": station["latitude"],
        "longitude": station["longitude"],
        "hourly": "temperature_2m,relative_humidity_2m,precipitation,soil_moisture_0_to_7cm",
        "past_days": 7,
        "forecast_days": 1,
        "timezone": "Asia/Kolkata",
    }

    try:
        with httpx.Client(timeout=12.0) as client:
            response = client.get(OPEN_METEO_URL, params=params)
            response.raise_for_status()
            payload = response.json()
        weather = summarize_hourly_weather(payload)
    except httpx.HTTPStatusError as error:
        raise HTTPException(status_code=502, detail=f"Open-Meteo returned HTTP {error.response.status_code}")
    except httpx.RequestError as error:
        raise HTTPException(status_code=503, detail=f"Open-Meteo is unavailable: {type(error).__name__}")
    except (KeyError, ValueError, TypeError) as error:
        raise HTTPException(status_code=502, detail=f"Open-Meteo returned unusable weather data: {error}")

    missing = [name for name, value in weather.items() if name not in {"timestamp"} and value is None]
    return {
        "station_id": station["station_id"],
        "station_name": station["station_name"],
        "latitude": station["latitude"],
        "longitude": station["longitude"],
        "source": "Open-Meteo",
        "source_url": OPEN_METEO_URL,
        "data_mode": "live-weather-preview",
        "missing_fields": missing,
        "weather": weather,
        "safety_notice": "Weather is external forecast/observation data, not a CWC gauge release or official flood warning.",
    }
