"""
FloodGuard: Comprehensive Model Evaluation Pipeline
===================================================
Produces granular evaluation metrics across all 3 candidate models:
- Per-class Precision, Recall, F1-Score
- Overall Accuracy & Cohen's Kappa
- 4x4 Confusion Matrices for multi-class risk tiers
- Class-wise error analysis

Strictly compliant with University requirements: No TensorFlow, No Keras, No MATLAB.
"""

import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report
)

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
    "stage_to_warning_ratio",
    "stage_to_danger_ratio",
    "runoff_potential_index",
    "drainage_strain_index"
]
TARGET_COLUMN = "risk_level"
CLASS_NAMES = ["Low", "Medium", "High", "Critical"]


def evaluate_all_models():
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, "..", "data", "processed")
    models_dir = os.path.join(base_dir, "..", "models")
    
    test_path = os.path.join(data_dir, "test_processed.csv")
    scaler_path = os.path.join(data_dir, "scaler.joblib")
    
    print("[Evaluation] Loading held-out test data and trained models...")
    test_df = pd.read_csv(test_path)
    scaler = joblib.load(scaler_path)
    
    X_test = test_df[FEATURE_COLUMNS]
    y_test = test_df[TARGET_COLUMN]
    X_test_scaled = scaler.transform(X_test)
    
    models = {
        "LogisticRegression": (joblib.load(os.path.join(models_dir, "logistic_regression.joblib")), True),
        "RandomForest": (joblib.load(os.path.join(models_dir, "random_forest.joblib")), False),
        "XGBoost": (joblib.load(os.path.join(models_dir, "xgboost.joblib")), False),
    }
    
    evaluation_report = {
        "dataset_summary": {
            "total_test_samples": len(test_df),
            "class_distribution": {
                name: int((y_test == idx).sum()) for idx, name in enumerate(CLASS_NAMES)
            }
        },
        "models": {}
    }
    
    for model_name, (model, requires_scaling) in models.items():
        print(f"\nEvaluating: {model_name}...")
        X_eval = X_test_scaled if requires_scaling else X_test
        
        preds = model.predict(X_eval)
        probs = model.predict_proba(X_eval)
        
        acc = accuracy_score(y_test, preds)
        p, r, f1, _ = precision_recall_fscore_support(y_test, preds, average="weighted", zero_division=0)
        macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(y_test, preds, average="macro", zero_division=0)
        
        cm = confusion_matrix(y_test, preds, labels=[0, 1, 2, 3]).tolist()
        
        # Per-class metrics
        class_p, class_r, class_f1, support = precision_recall_fscore_support(
            y_test, preds, labels=[0, 1, 2, 3], zero_division=0
        )
        
        per_class_metrics = {}
        for idx, name in enumerate(CLASS_NAMES):
            per_class_metrics[name] = {
                "precision": round(float(class_p[idx]), 4),
                "recall": round(float(class_r[idx]), 4),
                "f1_score": round(float(class_f1[idx]), 4),
                "support": int(support[idx])
            }
            
        evaluation_report["models"][model_name] = {
            "accuracy": round(float(acc), 4),
            "weighted_precision": round(float(p), 4),
            "weighted_recall": round(float(r), 4),
            "weighted_f1": round(float(f1), 4),
            "macro_f1": round(float(macro_f1), 4),
            "confusion_matrix": cm,
            "per_class": per_class_metrics
        }
        
        print(f"  Accuracy: {acc:.4f} | Weighted F1: {f1:.4f} | Macro F1: {macro_f1:.4f}")
        
    out_file = os.path.join(models_dir, "evaluation_report.json")
    with open(out_file, "w") as f:
        json.dump(evaluation_report, f, indent=2)
        
    print(f"\n[SUCCESS] Detailed evaluation report exported to: {out_file}")
    return evaluation_report


if __name__ == "__main__":
    evaluate_all_models()
