"""
FloodGuard: Feature Engineering & Preprocessing Pipeline
========================================================
This module processes raw hydrological observations and constructs 
physically meaningful predictive features for flood risk assessment.

Hydrological Concept:
1. 'Rainfall alone does not equal flood': Runoff depends on soil infiltration capacity.
   If soil moisture is already high (saturated), almost 100% of new rainfall 
   turns directly into surface runoff.
2. 'Stage Proximity': Difference between current river level and the designated 
   warning/danger marks set by Central Water Commission (CWC).
3. 'Drainage Strain': In urban floodplains, low elevation and low drainage 
   capacity create bottle-necking.
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

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
    # Engineered interaction features:
    "stage_to_warning_ratio",
    "stage_to_danger_ratio",
    "runoff_potential_index",
    "drainage_strain_index"
]

TARGET_COLUMN = "risk_level"


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes domain-specific hydrological features from raw observations.
    """
    df_out = df.copy()
    
    # 1. Stage proximity to official CWC thresholds
    warning_span = df_out["danger_level_m"] - df_out["warning_level_m"]
    # Protect against divide-by-zero
    warning_span = np.where(warning_span == 0, 1.0, warning_span)
    
    df_out["stage_to_warning_ratio"] = (
        (df_out["river_water_level_m"] - df_out["warning_level_m"]) / warning_span
    )
    df_out["stage_to_danger_ratio"] = (
        (df_out["river_water_level_m"] - df_out["danger_level_m"]) / warning_span
    )
    
    # 2. Runoff potential index: rainfall multiplied by antecedent soil saturation
    df_out["runoff_potential_index"] = (
        df_out["rainfall_24h_mm"] * df_out["soil_moisture_index"]
    )
    
    # 3. Drainage strain index: cumulative precipitation weighed against urban drainage capacity
    df_out["drainage_strain_index"] = (
        (df_out["rainfall_72h_mm"] * (1.1 - df_out["drainage_capacity"])) 
        / (df_out["elevation_m"] * 0.05 + 1.0)
    )
    
    return df_out


def prepare_datasets(raw_csv_path: str, output_dir: str):
    """
    Loads raw observations, constructs engineered features, performs a time-aware 
    train-test split, fits a standard scaler, and saves clean artifacts.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    print("[Preprocessing] Loading raw hydrological dataset...")
    df_raw = pd.read_csv(raw_csv_path)
    
    df_engineered = engineer_features(df_raw)
    
    # Sort chronologically by timestamp to maintain temporal sequence integrity
    df_engineered["timestamp"] = pd.to_datetime(df_engineered["timestamp"])
    df_engineered = df_engineered.sort_values(by=["timestamp", "station_id"]).reset_index(drop=True)
    
    X = df_engineered[FEATURE_COLUMNS]
    y = df_engineered[TARGET_COLUMN]
    
    # Time-aware split: Train on first 80% of timeline, test on held-out 20% future observations
    split_idx = int(len(df_engineered) * 0.80)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    # Fit StandardScaler on train set only (to avoid data leakage)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Save processed CSVs
    processed_train_path = os.path.join(output_dir, "train_processed.csv")
    processed_test_path = os.path.join(output_dir, "test_processed.csv")
    scaler_path = os.path.join(output_dir, "scaler.joblib")
    
    train_df = pd.DataFrame(X_train, columns=FEATURE_COLUMNS)
    train_df[TARGET_COLUMN] = y_train.values
    train_df.to_csv(processed_train_path, index=False)
    
    test_df = pd.DataFrame(X_test, columns=FEATURE_COLUMNS)
    test_df[TARGET_COLUMN] = y_test.values
    test_df.to_csv(processed_test_path, index=False)
    
    joblib.dump(scaler, scaler_path)
    
    print(f"[SUCCESS] Feature engineering complete.")
    print(f" - Train samples: {len(X_train)}")
    print(f" - Held-out Test samples: {len(X_test)}")
    print(f" - Total features: {len(FEATURE_COLUMNS)}")
    print(f" - Scaler saved to: {scaler_path}")


if __name__ == "__main__":
    raw_path = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "hydrological_observations.csv")
    proc_dir = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
    prepare_datasets(raw_path, proc_dir)
