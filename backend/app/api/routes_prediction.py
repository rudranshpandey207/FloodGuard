"""
FloodGuard: ML Prediction & Model Evaluation Routes
"""

import os
import json
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..mcp.tools import predict_flood_risk

router = APIRouter(prefix="/api/prediction", tags=["ML Prediction & Evaluation"])

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "models")


class PredictionRequest(BaseModel):
    location: Optional[str] = None
    feature_override: Optional[Dict[str, float]] = None


@router.post("/predict")
def run_model_prediction(payload: PredictionRequest):
    """
    Executes the trained XGBoost champion model to evaluate flood risk.
    """
    res = predict_flood_risk(location=payload.location, feature_override=payload.feature_override)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
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
        "summary": summary_data
    }
