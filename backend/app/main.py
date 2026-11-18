"""
FloodGuard: Main Application Entry Point
========================================
High-performance FastAPI service integrating:
- Machine Learning Prediction Engine (XGBoost champion model)
- Model Context Protocol (MCP) tool server
- Autonomous Flood Intelligence Agent (ReAct reasoning)
- Environmental Telemetry & Emergency Alert Dispatcher
"""

import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from .api.routes_stations import router as stations_router
from .api.routes_prediction import router as prediction_router
from .api.routes_alerts import router as alerts_router
from .api.routes_agent import router as agent_router

app = FastAPI(
    title="FloodGuard: Agentic Flood Risk Assessment & Decision Support System",
    description=(
        "An Agentic AI and Machine Learning platform combining hydrological observations, "
        "supervised risk prediction, Model Context Protocol (MCP) tools, and human-in-the-loop "
        "emergency decision support."
    ),
    version=settings.app_version
)

# Enable CORS for local React/Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API sub-routers
app.include_router(stations_router)
app.include_router(prediction_router)
app.include_router(alerts_router)
app.include_router(agent_router)


@app.get("/")
def root():
    return {
        "system": "FloodGuard Decision Support Platform",
        "version": settings.app_version,
        "status": "OPERATIONAL",
        "data_mode": settings.data_mode,
        "model_version": settings.model_version,
        "models_active": ["LogisticRegression (Baseline)", "RandomForest", "XGBoost (Champion)"],
        "docs_url": "/docs",
        "endpoints": [
            "/api/stations",
            "/api/prediction/predict",
            "/api/prediction/models",
            "/api/alerts",
            "/api/agent/query",
            "/api/agent/tools"
        ]
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "FloodGuard Backend & MCP Engine",
        "data_mode": settings.data_mode,
        "model_version": settings.model_version,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
