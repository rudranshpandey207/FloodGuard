"""
FloodGuard: ML Prediction & Model Evaluation Routes
"""

import os
import json
import math
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator
from ..config import settings
from ..mcp.tools import predict_flood_risk

router = APIRouter(prefix="/api/prediction", tags=["ML Prediction & Evaluation"])

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "models")


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    location: Optional[str] = None
    feature_override: Optional[Dict[str, float]] = Field(default=None, max_length=17)

    @field_validator("location")
    @classmethod
    def validate_location(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not value.strip():
            raise ValueError("location must not be blank")
        return value

    @field_validator("feature_override")
    @classmethod
    def validate_features(cls, value: Optional[Dict[str, float]]) -> Optional[Dict[str, float]]:
        if value is None:
            return value
        unknown = set(value) - set(FEATURE_COLUMNS)
        if unknown:
            raise ValueError(f"unknown feature override(s): {', '.join(sorted(unknown))}")
        if any(not math.isfinite(number) for number in value.values()):
            raise ValueError("feature overrides must contain finite numbers")
        return value


FEATURE_COLUMNS = [
    "rainfall_1h_mm", "rainfall_24h_mm", "rainfall_72h_mm", "rainfall_7d_mm",
    "river_water_level_m", "water_level_rate_of_rise_m_hr", "soil_moisture_index",
    "upstream_discharge_cusecs", "elevation_m", "drainage_capacity",
    "temperature_c", "humidity_pct", "stage_to_warning_ratio",
    "stage_to_danger_ratio", "runoff_potential_index", "drainage_strain_index",
]


@router.post("/predict")
def run_model_prediction(payload: PredictionRequest):
    """
    Executes the trained XGBoost champion model to evaluate flood risk.
    """
    res = predict_flood_risk(location=payload.location, feature_override=payload.feature_override)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    res["data_mode"] = settings.data_mode
    res["model_version"] = settings.model_version
    return res


@router.get("/models")
def get_model_evaluations():
    """
    Retrieves comparative metrics (Accuracy, Precision, Recall, F1, Confusion Matrix)
    across Logistic Regression, Random Forest, and XGBoost.
    """
    eval_file = os.path.join(MODELS_DIR, "evaluation_report.json")
    summary_file = os.path.join(MODELS_DIR, "model_summary.json")
    
    if not os.path.exists(eval_file) or not os.path.exists(summary_file):
        raise HTTPException(status_code=404, detail="Model evaluation records not found. Please train models first.")
        
    with open(eval_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)
        
    with open(summary_file, "r", encoding="utf-8") as f:
        summary_data = json.load(f)
        
    return {
        "evaluation_report": eval_data,
        "summary": summary_data,
        "data_mode": settings.data_mode,
        "model_version": settings.model_version,
    }
