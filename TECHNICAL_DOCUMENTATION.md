# FloodGuard — Complete Technical Documentation

**Project:** Agentic AI-Based Flood Risk Assessment and Emergency Response Decision Support System
**Status:** Major-project academic prototype using synthetic hydrological data
**Evaluation readiness:** Complete for local/Docker demonstration
**Safety boundary:** Non-operational; outputs are advisory and require human verification

## 1. Project purpose

FloodGuard combines three concerns in one decision-support interface:

1. Hydrological machine-learning classification.
2. Auditable tool-based agent reasoning.
3. A human-supervised dashboard for observation, scenario, chat, incident, and audit workflows.

The purpose is not to replace CWC, IMD, NDMA, district disaster authorities, or trained hydrologists. It demonstrates how heterogeneous flood information can be collected, predicted, explained, reviewed, and recorded.

## 2. Final implemented architecture

```text
Operator Browser
      |
      | HTTP (React/Vite)
      v
React Operations Console
  - Overview and regional risk map
  - Stations and station detail
  - Model Lab
  - Scenario Lab
  - Incidents
  - AI Assistant
      |
      | REST / JSON
      v
FastAPI Application
  |-- Stations and telemetry routes
  |-- Prediction and model-report routes
  |-- Alert and recommendation routes
  |-- MCP/agent routes
  |-- Open-Meteo integration route
  |-- Incident routes
  `-- Chat-session routes
      |
      +--> SQLite
      |      |-- incidents
      |      |-- incident_audit
      |      |-- chat_sessions
      |      `-- chat_messages
      |
      +--> MCP tools
      |      |-- weather
      |      |-- rainfall
      |      |-- water level
      |      |-- historical floods
      |      |-- risk prediction
      |      |-- risk status
      |      |-- affected regions
      |      `-- preparedness recommendations
      |
      +--> Open-Meteo keyless API
      |
      `--> XGBoost / Random Forest / Logistic Regression artifacts
             `-- synthetic training and test data
```

## 3. Technology stack

| Layer | Implementation | Purpose |
|---|---|---|
| Frontend | React 18, Vite | Interactive operations interface |
| Map | Leaflet, React-Leaflet, CARTO, OpenStreetMap | Geographic station visualization |
| Backend | Python 3.13, FastAPI, Pydantic, Uvicorn | REST APIs and validation |
| ML | pandas, NumPy, scikit-learn, XGBoost, joblib | Features and model inference |
| Agent tools | Model Context Protocol-style Python registry | Bounded evidence retrieval |
| Language enhancement | Google GenAI SDK | Optional response synthesis |
| Weather preview | Open-Meteo | No-key live weather and soil-moisture preview |
| Persistence | SQLite | Incidents, audit, chat sessions/messages |
| Deployment | Docker, Docker Compose, Nginx | Reproducible containerized demo |

## 4. Machine-learning pipeline

### 4.1 Data

The ML pipeline currently uses an artificially generated hydrological time-series dataset in `ml/data/processed/`. It contains 16 feature columns and a four-class risk target:

| Risk class | Label |
|---|---|
| 0 | Low |
| 1 | Medium |
| 2 | High |
| 3 | Critical |

Synthetic data is appropriate for academic pipeline development and UI demonstration, not real operational flood decisions.

### 4.2 Feature engineering

The model uses:

- 1-hour rainfall
- 24-hour rainfall
- 72-hour rainfall
- 7-day rainfall
- River water level
- Rate of water-level rise
- Soil moisture index
- Upstream discharge
- Elevation
- Drainage capacity
- Temperature
- Humidity
- Stage-to-warning ratio
- Stage-to-danger ratio
- Runoff potential index
- Drainage strain index

### 4.3 Candidate models

| Model | Held-out accuracy | Weighted F1 |
|---|---:|---:|
| Logistic Regression | 93.04% | 0.9341 |
| Random Forest | 98.97% | 0.9898 |
| XGBoost champion | 99.20% | 0.9920 |

These numbers describe the current synthetic holdout dataset. They do not establish real-world accuracy.

### 4.4 Artifacts

- `ml/models/champion_model.joblib`
- `ml/models/xgboost.joblib`
- `ml/models/random_forest.joblib`
- `ml/models/logistic_regression.joblib`
- `ml/data/processed/scaler.joblib`
- `ml/models/model_summary.json`
- `ml/models/evaluation_report.json`

## 5. Backend services

### 5.1 Station routes

| Method | Route | Function |
|---|---|---|
| GET | `/api/stations` | List all stations |
| GET | `/api/stations/{station_id}` | Retrieve one station |
| GET | `/api/stations/{station_id}/history` | Synthetic 24-hour station history |
| GET | `/api/stations/network/history` | Synthetic 24-hour network average |
| POST | `/api/stations/{station_id}/telemetry` | Validated local telemetry update |

### 5.2 Prediction routes

| Method | Route | Function |
|---|---|---|
| POST | `/api/prediction/predict` | Baseline or what-if model prediction |
| GET | `/api/prediction/models` | Candidate-model metrics and summary |

Scenario overrides can change rainfall, river level, rise rate, soil moisture, discharge, temperature, and humidity. Derived stage ratios, runoff potential, and drainage strain are recalculated before inference.

### 5.3 Alerts and agent routes

| Method | Route | Function |
|---|---|---|
| GET | `/api/alerts` | Active synthetic High/Critical alerts |
| GET | `/api/alerts/recommendations/{risk_level}` | Risk-tier preparedness recommendations |
| POST | `/api/agent/query` | Agentic ReAct-style assessment |
| GET | `/api/agent/tools` | Registered MCP tool catalog |

### 5.4 Weather integration

`GET /api/integrations/weather/{station_id}` calls Open-Meteo for:

- 1-hour, 24-hour, 72-hour, and 7-day precipitation
- Temperature
- Relative humidity
- Soil moisture

This is a weather preview. It does not provide official river gauge level or barrage discharge.

### 5.5 Incident routes

| Method | Route | Function |
|---|---|---|
| POST | `/api/incidents` | Create an incident |
| GET | `/api/incidents` | List incidents |
| GET | `/api/incidents/{incident_id}` | Incident detail plus audit |
| PATCH | `/api/incidents/{incident_id}` | Human lifecycle update |

Acknowledgement and resolution require `approval_confirmed: true`. Resolution requires an Investigating or Acknowledged state first.

### 5.6 Chat routes

| Method | Route | Function |
|---|---|---|
| POST | `/api/chat/sessions` | Create chat session |
| GET | `/api/chat/sessions` | List chat sessions |
| GET | `/api/chat/sessions/{session_id}/messages` | Load one chat history |
| POST | `/api/chat/sessions/{session_id}/messages` | Persist user or assistant message |

## 6. MCP and agent behavior

The MCP layer exposes eight tool concepts:

1. `get_weather`
2. `get_rainfall`
3. `get_water_level`
4. `get_historical_floods`
5. `predict_flood_risk`
6. `get_risk_status`
7. `get_affected_regions`
8. `get_preparedness_recommendations`

The offline agent performs deterministic intent detection and tool invocation. It recognizes:

- Greetings and capability questions
- Regional/affected-station questions
- Station-specific risk questions
- Rainfall and river-level requests
- Historical flood requests
- Preparedness requests
- Unknown/general questions

Gemini is an optional response-synthesis enhancement. MCP/model evidence is collected first. Gemini receives an evidence-grounded prompt and is not granted direct database or model mutation tools. The safety filter is applied after synthesis. Missing credentials or API errors fall back to the deterministic response.

## 7. Frontend features

### 7.1 Overview

- Six synthetic stations
- Risk distribution cards
- Leaflet risk-map
- Station risk filter
- Selected-station gauge
- Backend synthetic network history
- Active alert list
- Alert severity filter
- CSV export
- Dashboard refresh

### 7.2 Stations

- Search by name, station ID, river, or region
- Low/Medium/High/Critical filtering
- Selectable station table
- Station detail fields
- Coordinates and elevation
- Warning/danger marks
- Rainfall, rise, soil, and discharge values
- Synthetic station history sparkline

### 7.3 Model Lab

- Logistic Regression benchmark
- Random Forest benchmark
- XGBoost champion
- Accuracy, weighted F1, and model metadata
- Predictive feature ranking

### 7.4 Scenario Lab

- Station selection
- Rainfall, stage, rise, soil, discharge, temperature, and humidity controls
- Baseline/simulated class comparison
- Risk-tier change
- Class probabilities
- Primary model drivers
- Open-Meteo live-weather preview
- Mixed-provenance warning
- Latest 10 browser-saved runs
- JSON export and clear history

### 7.5 Incidents

- Operator name
- Station selection
- Situation summary
- Incident lifecycle controls
- Browser confirmation for acknowledgement/resolution
- Incident detail and audit timeline
- SQLite persistence

### 7.6 AI Assistant

- Friendly greeting and help behavior
- Structured Markdown response rendering
- Gemini/offline synthesis label
- MCP tool trace drawer
- Investigation plan display
- Safety notice
- Persistent chat sessions and messages

## 8. Persistence

SQLite stores:

- Incident records
- Incident audit transitions
- Chat sessions
- Chat messages

The database is under `backend/data/incidents.db` and is excluded from Git.

## 9. Docker deployment

The Docker Compose deployment contains:

- `backend` container on port `8000`
- `frontend` container on port `5173`
- Python 3.13 backend image
- Node 20 build stage and Nginx frontend stage

One-command demo:

```powershell
cd C:\Users\ishan\Desktop\flood\FloodGuard
.\start-demo.ps1
```

Stop:

```powershell
docker compose down
```

## 10. Demonstration script

1. Run `start-demo.ps1`.
2. Open `http://localhost:5173`.
3. Explain that the station registry and model data are synthetic.
4. Open Overview and describe the six stations and active alerts.
5. Select a station on the Leaflet map.
6. Open Stations and demonstrate search/filter/detail.
7. Open Model Lab and compare the three models.
8. Open Scenario Lab and raise rainfall and river level until the risk changes.
9. Load Open-Meteo live weather and explain the mixed provenance.
10. Open AI Assistant, greet it, ask for affected stations, and open the tool trace.
11. Open Incidents, create an incident, acknowledge it, and inspect the audit.
12. Explain that official CWC/WRIS gauge/discharge feeds remain future work.

## 11. Data-governance and safety limitations

- Synthetic scores must not be described as operational accuracy.
- Open-Meteo weather is forecast/observation weather, not an official flood warning.
- River level and discharge in the current registry are demonstration values.
- Gemini can improve wording but cannot establish facts outside MCP/evidence content.
- Incident actions require human confirmation.
- No evacuation order or official notification is issued by the system.

## 12. Future production scope

- Official CWC/WRIS gauge and discharge adapters
- Real district rainfall and sensor ingestion
- Real chronological and station-held-out model retraining
- Authentication and role-based authorization
- Immutable audit/event log
- Alert notification integrations
- Real official-source verification
- Production monitoring, backups, logs, and rollback
- Calibration and false-negative analysis
- Human-approved pilot deployment

## 13. Final evaluation statement

FloodGuard is complete as an academic synthetic-data flood-risk decision-support demonstration. It provides an integrated ML, MCP/agent, dashboard, scenario, weather, incident, and audit workflow. It is not suitable for real emergency decisions until official data, real validation, and operational governance are implemented.
