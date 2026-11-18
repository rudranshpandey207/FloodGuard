"""Runtime configuration for the FloodGuard local demonstration service."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_version: str = os.getenv("FLOODGUARD_APP_VERSION", "1.1.0")
    data_mode: str = os.getenv("FLOODGUARD_DATA_MODE", "synthetic")
    frontend_origin: str = os.getenv("FLOODGUARD_FRONTEND_ORIGIN", "http://localhost:5173")
    model_version: str = os.getenv("FLOODGUARD_MODEL_VERSION", "xgboost-champion-local")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")


settings = Settings()
