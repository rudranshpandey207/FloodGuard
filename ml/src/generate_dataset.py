"""
FloodGuard: Hydrological & Meteorological Dataset Generator
===========================================================
This module generates a high-fidelity synthetic time-series dataset of 
environmental, hydrological, and meteorological observations across major 
river monitoring stations (e.g., Yamuna Basin, Hindon, and Ganga).

Why this matters:
- Real flood forecasting models require multi-station time-series data reflecting 
  seasonal monsoon cycles, sudden storm downpours, soil saturation dynamics, 
  and upstream barrage discharges (e.g., Hathnikund Barrage releases).
- This dataset serves as the benchmark training and evaluation set for candidate 
  supervised ML models (Logistic Regression, Random Forest, XGBoost).
"""

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Fix Windows console encoding for UTF-8 characters
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Target river basin stations with realistic baseline elevations and danger marks
STATIONS = [
    {
        "station_id": "STN_YAM_01",
        "station_name": "Yamuna - Old Railway Bridge (Delhi)",
        "river": "Yamuna",
        "latitude": 28.6635,
        "longitude": 77.2478,
        "elevation_m": 204.0,
        "warning_level_m": 204.50,
        "danger_level_m": 205.33,
        "drainage_capacity": 0.45  # Dense urban constraints
    },
    {
        "station_id": "STN_YAM_02",
        "station_name": "Yamuna - Okhla Barrage (Noida/Delhi)",
        "river": "Yamuna",
        "latitude": 28.5448,
        "longitude": 77.3069,
        "elevation_m": 198.5,
        "warning_level_m": 199.50,
        "danger_level_m": 200.60,
        "drainage_capacity": 0.50
    },
    {
        "station_id": "STN_HIN_01",
        "station_name": "Hindon - Ghaziabad Barrage",
        "river": "Hindon",
        "latitude": 28.6508,
        "longitude": 77.4124,
        "elevation_m": 208.0,
        "warning_level_m": 209.00,
        "danger_level_m": 210.20,
        "drainage_capacity": 0.40
    },
    {
        "station_id": "STN_HIN_02",
        "station_name": "Hindon - Noida Sector 135 Floodplain",
        "river": "Hindon",
        "latitude": 28.4985,
        "longitude": 77.4012,
        "elevation_m": 195.0,
        "warning_level_m": 196.20,
        "danger_level_m": 197.50,
        "drainage_capacity": 0.55
    },
    {
        "station_id": "STN_GAN_01",
        "station_name": "Ganga - Haridwar Bhimgoda",
        "river": "Ganga",
        "latitude": 29.9576,
        "longitude": 78.1728,
        "elevation_m": 294.0,
        "warning_level_m": 293.00,
        "danger_level_m": 294.00,
        "drainage_capacity": 0.70
    },
    {
        "station_id": "STN_GAN_02",
        "station_name": "Ganga - Prayagraj Sangam",
        "river": "Ganga",
        "latitude": 25.4358,
        "longitude": 81.8463,
        "elevation_m": 84.0,
        "warning_level_m": 83.73,
        "danger_level_m": 84.73,
        "drainage_capacity": 0.65
    }
]


def generate_hydrological_records(num_days: int = 730, seed: int = 42) -> pd.DataFrame:
    """
    Generates realistic daily/hourly records spanning 2 full annual cycles (730 days)
    to cover dry seasons (Nov-May), monsoon build-up (June), peak monsoon floods (July-Sept),
    and post-monsoon recession (Oct).
    """
    np.random.seed(seed)
    start_date = datetime(2024, 1, 1)
    
    records = []
    
    for stn in STATIONS:
        # State tracking for continuous autoregressive hydrology
        soil_moisture = 0.25
        water_level = stn["warning_level_m"] - 2.5
        past_rainfall = [0.0] * 7  # Last 7 days rainfall history
        
        for day_idx in range(num_days):
            current_date = start_date + timedelta(days=day_idx)
            month = current_date.month
            day_of_year = current_date.timetuple().tm_yday
            
            # Monsoon seasonality factor (Peaks in July-August, days 180 - 245)
            is_monsoon = month in [6, 7, 8, 9]
            if is_monsoon:
                monsoon_intensity = np.sin((day_of_year - 150) / 120 * np.pi) ** 2
            else:
                monsoon_intensity = 0.05 * np.random.uniform(0, 1)
                
            # Simulate random storm events (clusters of heavy rain)
            is_storm = np.random.rand() < (0.28 if is_monsoon else 0.04)
            if is_storm:
                daily_rain = np.random.gamma(shape=3.0, scale=25.0 * (1.0 + monsoon_intensity))
            else:
                daily_rain = np.random.exponential(scale=2.0 if is_monsoon else 0.2)
                
            daily_rain = float(np.clip(daily_rain, 0, 240.0))
            
            # Update 7-day rainfall memory
            past_rainfall.pop(0)
            past_rainfall.append(daily_rain)
            
            rain_1h = float(np.clip(daily_rain * np.random.uniform(0.15, 0.45), 0, 85.0))
            rain_24h = daily_rain
            rain_72h = float(sum(past_rainfall[-3:]))
            rain_7d = float(sum(past_rainfall))
            
            # Soil moisture dynamics:
            # - Infiltrates with rain
            # - Evaporates/drains gradually during dry periods
            soil_moisture = soil_moisture * 0.92 + (rain_24h / 150.0) * 0.40
            soil_moisture = float(np.clip(soil_moisture, 0.10, 0.98))
            
            # Upstream discharge (e.g. Barrage gate openings during high rainfall)
            base_discharge = 15000  # normal baseline cusecs
            if rain_72h > 80 or soil_moisture > 0.75:
                upstream_discharge = base_discharge + (rain_72h * 1800) + np.random.uniform(20000, 150000)
            else:
                upstream_discharge = base_discharge + np.random.uniform(1000, 12000)
            upstream_discharge = float(np.clip(upstream_discharge, 5000, 380000))
            
            # Water level physics:
            # Affected by upstream discharge, local runoff (rain * soil saturation), minus river discharge flow
            target_water_level = (
                stn["warning_level_m"] - 2.5
                + (upstream_discharge / 380000.0) * 3.8
                + (rain_24h * soil_moisture / 100.0) * 1.5
            )
            # Add lag / smoothing
            water_level_prev = water_level
            water_level = water_level * 0.75 + target_water_level * 0.25 + np.random.normal(0, 0.05)
            
            # Rate of rise (meters per 3 hours converted to m/hr)
            rate_of_rise = float(np.clip((water_level - water_level_prev) / 3.0, -0.8, 1.2))
            
            # Temperature and atmospheric pressure
            temp_c = float(28.0 + 10.0 * np.sin((day_of_year - 100) / 365 * 2 * np.pi) + np.random.normal(0, 2))
            humidity_pct = float(np.clip(45.0 + soil_moisture * 50.0 + np.random.normal(0, 5), 20.0, 99.0))
            
            # Determine Ground Truth Flood Risk Level based on Hydrological Rules:
            # 0 = Low (Water well below warning mark)
            # 1 = Medium (Water approaching warning level or sustained high rainfall)
            # 2 = High (Water exceeding warning level, high rate of rise, or soil supersaturated)
            # 3 = Critical (Water breaching danger mark or major barrage surge)
            
            wl_ratio = (water_level - stn["warning_level_m"]) / (stn["danger_level_m"] - stn["warning_level_m"])
            
            if water_level >= stn["danger_level_m"] or (wl_ratio > 0.85 and rate_of_rise > 0.15) or upstream_discharge > 280000:
                risk_level = 3  # Critical
            elif water_level >= stn["warning_level_m"] or (wl_ratio > 0.40 and rain_72h > 100) or (rain_24h > 120 and soil_moisture > 0.80):
                risk_level = 2  # High
            elif (water_level >= stn["warning_level_m"] - 0.75) or rain_72h > 60 or soil_moisture > 0.65:
                risk_level = 1  # Medium
            else:
                risk_level = 0  # Low
                
            records.append({
                "timestamp": current_date.strftime("%Y-%m-%d"),
                "station_id": stn["station_id"],
                "station_name": stn["station_name"],
                "river": stn["river"],
                "latitude": stn["latitude"],
                "longitude": stn["longitude"],
                "elevation_m": stn["elevation_m"],
                "warning_level_m": stn["warning_level_m"],
                "danger_level_m": stn["danger_level_m"],
                "drainage_capacity": stn["drainage_capacity"],
                "rainfall_1h_mm": round(rain_1h, 2),
                "rainfall_24h_mm": round(rain_24h, 2),
                "rainfall_72h_mm": round(rain_72h, 2),
                "rainfall_7d_mm": round(rain_7d, 2),
                "river_water_level_m": round(water_level, 3),
                "water_level_rate_of_rise_m_hr": round(rate_of_rise, 3),
                "soil_moisture_index": round(soil_moisture, 3),
                "upstream_discharge_cusecs": round(upstream_discharge, 1),
                "temperature_c": round(temp_c, 1),
                "humidity_pct": round(humidity_pct, 1),
                "risk_level": risk_level
            })
            
    df = pd.DataFrame(records)
    return df


if __name__ == "__main__":
    output_dir = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
    os.makedirs(output_dir, exist_ok=True)
    
    print("[FloodGuard Data Generator] Generating hydrological time-series observations...")
    df = generate_hydrological_records(num_days=730)
    
    output_path = os.path.join(output_dir, "hydrological_observations.csv")
    df.to_csv(output_path, index=False)
    
    print(f"[SUCCESS] Generated {len(df)} records across {len(STATIONS)} river stations.")
    print(f"[PATH] Saved to: {os.path.abspath(output_path)}")
    print("\nRisk Level Distribution:")
    print(df["risk_level"].value_counts().sort_index().rename(
        index={0: "0 - Low", 1: "1 - Medium", 2: "2 - High", 3: "3 - Critical"}
    ))
