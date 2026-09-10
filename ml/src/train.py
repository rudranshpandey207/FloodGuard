"""
FloodGuard: Model Training Pipeline
===================================
Trains and compares candidate supervised machine learning models:
1. Logistic Regression (Linear Baseline)
2. Random Forest Classifier (Bagging Ensemble)
3. XGBoost Classifier (Gradient Boosting)

Strictly compliant with University Guidelines:
- No TensorFlow, No Keras, No MATLAB.
- Uses Scikit-learn and XGBoost.
"""

import os
import sys
import json
import time
import joblib
import pandas as pd
import numpy as np

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report

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


def train_models():
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, "..", "data", "processed")
    models_dir = os.path.join(base_dir, "..", "models")
    os.makedirs(models_dir, exist_ok=True)
    
    train_path = os.path.join(data_dir, "train_processed.csv")
    test_path = os.path.join(data_dir, "test_processed.csv")
    scaler_path = os.path.join(data_dir, "scaler.joblib")
    
    print("[Training] Loading processed datasets...")
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    scaler = joblib.load(scaler_path)
    
    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df[TARGET_COLUMN]
    X_test = test_df[FEATURE_COLUMNS]
    y_test = test_df[TARGET_COLUMN]
    
    # Scaled inputs for Logistic Regression
    X_train_scaled = scaler.transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    results = {}
    
    # ==========================================
    # 1. Baseline Model: Logistic Regression
    # ==========================================
    print("\n--- Training Model 1: Logistic Regression (Baseline) ---")
    start_time = time.time()
    lr_model = LogisticRegression(
        max_iter=1000, 
        solver="lbfgs",
        class_weight="balanced", 
        random_state=42
    )
    lr_model.fit(X_train_scaled, y_train)
    lr_train_time = time.time() - start_time
    
    lr_preds = lr_model.predict(X_test_scaled)
    lr_acc = accuracy_score(y_test, lr_preds)
    p, r, f1, _ = precision_recall_fscore_support(y_test, lr_preds, average="weighted", zero_division=0)
    
    print(f"Logistic Regression - Accuracy: {lr_acc:.4f}, F1 (weighted): {f1:.4f} (took {lr_train_time:.2f}s)")
    results["LogisticRegression"] = {
        "accuracy": round(float(lr_acc), 4),
        "precision": round(float(p), 4),
        "recall": round(float(r), 4),
        "f1_score": round(float(f1), 4),
        "training_time_sec": round(float(lr_train_time), 3),
        "model_type": "Linear / Multinomial",
        "description": "Baseline linear classifier with L2 regularization and balanced class weights"
    }
    joblib.dump(lr_model, os.path.join(models_dir, "logistic_regression.joblib"))

    # ==========================================
    # 2. Candidate Model: Random Forest
    # ==========================================
    print("\n--- Training Model 2: Random Forest Classifier (Bagging) ---")
    start_time = time.time()
    rf_model = RandomForestClassifier(
        n_estimators=150, 
        max_depth=12, 
        min_samples_split=4,
        class_weight="balanced", 
        random_state=42, 
        n_jobs=-1
    )
    rf_model.fit(X_train, y_train)
    rf_train_time = time.time() - start_time
    
    rf_preds = rf_model.predict(X_test)
    rf_acc = accuracy_score(y_test, rf_preds)
    p, r, f1, _ = precision_recall_fscore_support(y_test, rf_preds, average="weighted", zero_division=0)
    
    print(f"Random Forest - Accuracy: {rf_acc:.4f}, F1 (weighted): {f1:.4f} (took {rf_train_time:.2f}s)")
    results["RandomForest"] = {
        "accuracy": round(float(rf_acc), 4),
        "precision": round(float(p), 4),
        "recall": round(float(r), 4),
        "f1_score": round(float(f1), 4),
        "training_time_sec": round(float(rf_train_time), 3),
        "model_type": "Ensemble (Bagging)",
        "description": "150 Decision Trees with out-of-bag feature randomization and balanced subsampling"
    }
    joblib.dump(rf_model, os.path.join(models_dir, "random_forest.joblib"))

    # ==========================================
    # 3. Candidate Model: XGBoost Classifier
    # ==========================================
    print("\n--- Training Model 3: XGBoost Classifier (Boosting) ---")
    start_time = time.time()
    xgb_model = XGBClassifier(
        n_estimators=180,
        learning_rate=0.08,
        max_depth=6,
        subsample=0.85,
        colsample_bytree=0.85,
        objective="multi:softprob",
        num_class=4,
        random_state=42,
        n_jobs=-1
    )
    xgb_model.fit(X_train, y_train)
    xgb_train_time = time.time() - start_time
    
    xgb_preds = xgb_model.predict(X_test)
    xgb_acc = accuracy_score(y_test, xgb_preds)
    p, r, f1, _ = precision_recall_fscore_support(y_test, xgb_preds, average="weighted", zero_division=0)
    
    print(f"XGBoost - Accuracy: {xgb_acc:.4f}, F1 (weighted): {f1:.4f} (took {xgb_train_time:.2f}s)")
    results["XGBoost"] = {
        "accuracy": round(float(xgb_acc), 4),
        "precision": round(float(p), 4),
        "recall": round(float(r), 4),
        "f1_score": round(float(f1), 4),
        "training_time_sec": round(float(xgb_train_time), 3),
        "model_type": "Ensemble (Gradient Boosted Trees)",
        "description": "Sequential gradient boosted decision trees optimizing multi-class log-loss"
    }
    joblib.dump(xgb_model, os.path.join(models_dir, "xgboost.joblib"))

    # Determine Champion Model
    best_model_name = max(results.keys(), key=lambda k: results[k]["f1_score"])
    print(f"\n[CHAMPION] Model selected for production deployment: {best_model_name} (F1: {results[best_model_name]['f1_score']})")
    
    if best_model_name == "XGBoost":
        joblib.dump(xgb_model, os.path.join(models_dir, "champion_model.joblib"))
        champion_importances = xgb_model.feature_importances_
    elif best_model_name == "RandomForest":
        joblib.dump(rf_model, os.path.join(models_dir, "champion_model.joblib"))
        champion_importances = rf_model.feature_importances_
    else:
        joblib.dump(lr_model, os.path.join(models_dir, "champion_model.joblib"))
        champion_importances = np.mean(np.abs(lr_model.coef_), axis=0)

    # Calculate Feature Importances for Explainability
    feature_importance_dict = {
        feat: round(float(imp), 4)
        for feat, imp in sorted(zip(FEATURE_COLUMNS, champion_importances), key=lambda x: x[1], reverse=True)
    }

    # Save summary metadata
    summary = {
        "models": results,
        "champion_model": best_model_name,
        "feature_importances": feature_importance_dict,
        "feature_columns": FEATURE_COLUMNS,
        "target_mapping": {
            0: {"label": "Low", "color": "#10B981", "action": "Routine hydrologic monitoring"},
            1: {"label": "Medium", "color": "#F59E0B", "action": "Increased sensor polling, inspect low-lying catchments"},
            2: {"label": "High", "color": "#F97316", "action": "Flood defense activation, prepare temporary diversion bunds"},
            3: {"label": "Critical", "color": "#EF4444", "action": "Immediate emergency response mobilization, priority evacuation alerts"}
        }
    }
    
    summary_path = os.path.join(models_dir, "model_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
        
    print(f"\n[SUCCESS] All models trained and saved to {models_dir}")
    print(f"[METADATA] Summary exported to {summary_path}")


if __name__ == "__main__":
    train_models()
