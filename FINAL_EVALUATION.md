# FloodGuard — Major Project Evaluation Readiness

**Evaluation status:** Ready for academic demonstration with synthetic data.

## Demonstration scope

FloodGuard is an end-to-end synthetic-data flood-risk decision-support prototype. It is suitable for a major-project evaluation when clearly presented as a demonstration system rather than an official emergency application.

## What is ready

- React/Vite operations dashboard
- FastAPI prediction and agent service
- XGBoost, Random Forest, and Logistic Regression model artifacts
- Synthetic station and telemetry registry
- Regional risk map with Leaflet/OpenStreetMap/CARTO
- Station search, filtering, detail, and history views
- Model comparison and feature-importance view
- What-if prediction scenario lab
- Open-Meteo live-weather preview without an API key
- Gemini synthesis with deterministic offline fallback
- MCP tool trace and human-safety notice
- SQLite incident lifecycle and audit trail
- Persistent chat sessions
- CSV report export and scenario JSON export
- Docker Compose deployment files as optional infrastructure

## What is intentionally not claimed

- Not connected to official CWC/WRIS river-gauge releases
- Not connected to official barrage discharge feeds
- Not validated on real flood-event data
- Not authorized to issue evacuation or emergency orders
- Not a replacement for CWC, NDMA, IMD, or district authorities
- Docker is optional and is not required for evaluation

## Recommended evaluation sequence

1. Start FastAPI.
2. Start the React frontend.
3. Open Overview and explain synthetic data mode.
4. Demonstrate station search and the real Leaflet map.
5. Open Scenario Lab and run baseline versus simulated prediction.
6. Load Open-Meteo live weather and explain that gauge/discharge values remain synthetic.
7. Ask the AI Assistant a location, regional, rainfall, history, or preparedness question.
8. Open an MCP trace and explain human-in-the-loop safety.
9. Create an incident and move it through acknowledgement/resolution.
10. Explain the remaining real-data roadmap.

## Required local startup

### Activate environment

```powershell
cd C:\Users\ishan\Desktop\flood\FloodGuard
.\.venv\Scripts\Activate.ps1
```

### Start backend

```powershell
cd C:\Users\ishan\Desktop\flood\FloodGuard\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Start frontend

```powershell
cd C:\Users\ishan\Desktop\flood\FloodGuard\frontend
npm run dev
```

## Verification commands

### Backend

```powershell
cd C:\Users\ishan\Desktop\flood\FloodGuard
python -m pytest backend\tests -q
```

### Frontend

```powershell
cd C:\Users\ishan\Desktop\flood\FloodGuard\frontend
npm run build
```

## Docker status

Docker is not a prerequisite for evaluation. If Docker Desktop is open and the Linux engine is started, the optional Compose deployment can be attempted:

```powershell
docker compose up --build
```

If Docker Desktop reports an unavailable engine pipe, continue with the direct backend/frontend commands above.
