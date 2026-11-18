# FloodGuard — Current Project Status

**Status date:** 18 November 2026  
**Project:** Agentic AI-Based Flood Risk Assessment and Emergency Response Decision Support System  
**Repository state:** Academic prototype / local development  
**Current operational posture:** Demonstrable offline-first dashboard backed by a local FastAPI service; not ready for real emergency operations

**Delivery phase:** Phase 4 — Agent, Alerts, and Incident Workflow (**in progress**); Phase 1 (**complete**); Phase 2 (**complete**); Phase 3 (**complete**)

Phase execution details are maintained in [PHASES.md](PHASES.md), and implementation rationale is maintained in [CHANGELOG.md](CHANGELOG.md).

## 1. Executive status

FloodGuard currently combines three working layers:

1. A Python machine-learning pipeline that generates/engineers hydrological features, trains three classifiers, and exports serialized models and evaluation reports.
2. A FastAPI service exposing station telemetry, model prediction, alerts, preparedness recommendations, and an agent endpoint.
3. A React/Vite command-console frontend with Overview, Stations, Model Lab, and AI Assistant views.

The project is a strong academic proof of concept. It demonstrates the intended architecture and user experience, but the live data, operational integrations, persistence, authentication, deployment, and validation required for a production decision-support system are not complete.

## 2. What is implemented now

### 2.1 Machine-learning layer

Location: `ml/`

- Feature engineering for rainfall windows, river stage, stage-to-threshold ratios, soil saturation, runoff potential, drainage strain, and upstream discharge.
- Three trained candidate models:
  - Logistic Regression baseline
  - Random Forest candidate
  - XGBoost champion
- Serialized artifacts are present in `ml/models/`:
  - `champion_model.joblib`
  - `logistic_regression.joblib`
  - `random_forest.joblib`
  - `xgboost.joblib`
  - `model_summary.json`
  - `evaluation_report.json`
- Current reported held-out-test results:
  - Logistic Regression: 93.04% accuracy
  - Random Forest: 98.97% accuracy
  - XGBoost: 99.20% accuracy / 0.9920 weighted F1
- Evaluation includes weighted and macro metrics, per-class metrics, and a 4 × 4 confusion matrix.

**Important interpretation:** These scores describe performance on the current processed dataset. They are not evidence that the model will achieve the same performance on unseen rivers, new sensor networks, or real operational data.

### 2.2 FastAPI prediction and decision-support service

Location: `backend/app/`

Implemented routes include:

| Route | Purpose | Current source |
|---|---|---|
| `GET /` | Service metadata and available endpoints | FastAPI |
| `GET /api/health` | Health check | FastAPI |
| `GET /api/stations` | All monitoring stations and current telemetry | `backend/app/data/stations.json` |
| `GET /api/stations/{station_id}` | One station and historical events | JSON registry |
| `POST /api/stations/{station_id}/telemetry` | Local scenario/telemetry update | JSON registry |
| `POST /api/prediction/predict` | Champion-model risk prediction | XGBoost artifact |
| `GET /api/prediction/models` | Model evaluation and summary | JSON reports |
| `GET /api/alerts` | Derived High/Critical alerts | Station telemetry |
| `GET /api/alerts/recommendations/{risk_level}` | Preparedness recommendations | MCP tools |
| `POST /api/agent/query` | Agentic flood assessment | ReAct-style orchestrator |
| `GET /api/agent/tools` | Registered MCP tools | MCP registry |

The backend has permissive CORS for local development and is intended to run on port `8000`.

### 2.3 MCP and agent layer

The MCP tool layer currently provides bounded functions for:

- Weather
- Rainfall
- Water levels
- Historical floods
- ML risk prediction
- Risk status
- Affected regions
- Preparedness recommendations

The agent can:

1. Interpret a station-specific or regional question.
2. Select a deterministic investigation plan.
3. Invoke relevant MCP tools.
4. Produce an evidence-grounded response.
5. Apply a human-in-the-loop safety filter.

The Gemini integration is optional. The built-in offline orchestrator allows local demonstrations without an API key.

### 2.4 Frontend

Location: `frontend/`

Implemented with React 18 and Vite:

- Overview dashboard
  - Station count
  - Alert count
  - High/Critical risk distribution
  - System confidence
  - Regional station map-style visualization
  - Selected-station gauge and thresholds
  - Network telemetry chart
  - Active alert list
- Stations table
  - Station, river, region, water level, rainfall, rate of rise, and risk
- Model Lab
  - Candidate model comparison
  - Champion indicator
  - Feature-importance presentation
- AI Assistant
  - Chat interface
  - Agent API integration
  - Offline fallback response
  - Human-oversight notice

The frontend has demo-data fallback so it can be previewed even when FastAPI is stopped. It builds successfully with `npm run build`.

**Current frontend limitations:**

- The map is a styled operational visualization, not yet a real Leaflet/Mapbox geospatial map.
- The telemetry chart is currently illustrative SVG data rather than a historical time-series API.
- Export, station-details, filter, refresh, map zoom, and “View all alerts” controls are primarily presentation controls.
- The “What-if” simulator described in the original roadmap is not yet implemented.

### Gemini and Phase 2 alert/report increment

- Gemini synthesis is integrated through a project-root ignored `.env` file and remains optional.
- The configured model is `gemini-3.8-flash`; fallback is the deterministic MCP/model response.
- Agent responses identify `GEMINI ENHANCED` or `OFFLINE FALLBACK` synthesis.
- The supplied Gemini key appeared in chat and must be revoked/replaced for security.
- Overview alert severity filtering and CSV report export are implemented.

### Phase 2 dashboard increment started

- The schematic CSS map has been replaced by a real Leaflet/Carto Dark map.
- Synthetic station coordinates are displayed as risk-colored circle markers.
- Selecting a marker updates the selected-station detail panel.
- The Overview map includes a Low/Medium/High/Critical risk filter and station count.
- A Delhi/NCR risk question now returns regional affected-station evidence instead of always defaulting to one Old Railway Bridge result.
- Phase 3 includes a Scenario Lab with baseline-versus-simulated XGBoost prediction, class probabilities, model risk drivers, temperature/humidity controls, local recent-run history, and JSON export.
- Open-Meteo live-weather preview is available without an API key for temperature, humidity, soil moisture, and rolling precipitation; it does not replace CWC gauge level or official barrage discharge.
- Scenario overrides recompute derived stage, runoff, and drainage-strain features before model inference.
- A floating refresh control reloads stations, alerts, and model metadata.
- The Stations view has live search and risk filtering, a selectable station detail panel, coordinates and thresholds, and a synthetic 24-hour history sparkline.
- The synthetic history endpoint is explicitly marked as generated demonstration data and not observed telemetry.
- Phase 4 incidents are persisted in a local SQLite database and can be investigated, acknowledged, or resolved by a human operator.
- Incident transitions are recorded in an audit table; Gemini/AI output cannot create or resolve incidents without the operator UI/API action.
- The Overview network telemetry chart now loads a 25-point backend-provided synthetic 24-hour series instead of hardcoded SVG values.

### 2.5 Phase 1 stabilization completed

- Added centralized backend settings for app version, synthetic data mode, frontend origin, and model version.
- Added strict prediction and telemetry input validation.
- Added explicit synthetic-data and model-version metadata to health, root, prediction, and model responses.
- Added focused FastAPI contract tests covering health, station retrieval, 404 handling, prediction validation, prediction metadata, and telemetry bounds.
- Added a centralized frontend API request helper with consistent JSON/error handling.
- Added frontend loading, backend-error, offline-fallback, and synthetic-data labels.
- Added `pytest` as a project test dependency.
- Verified the frontend production build and all seven Phase 1 backend tests.

## 3. What is not implemented yet

The root `README.md` describes a larger target architecture. The following items are still future work rather than current capabilities:

- Node.js/Express application gateway
- MongoDB persistence
- User authentication, authorization, roles, and session management
- Persistent incident, alert, and chat records
- WebSocket/SSE real-time updates
- Real Leaflet/React-Leaflet map layers and river-basin geometry
- Real historical telemetry and live weather ingestion
- Public alert delivery through SMS, email, push, or official channels
- Production monitoring, audit logging, deployment, backups, and disaster recovery
- Formal model registry, versioning, rollback, and drift monitoring
- Independent external validation of predictions

## 4. Synthetic dataset assessment

### Is replacing the artificial dataset with a real dataset a good decision?

**Yes, if the goal is credible flood-risk prediction or any operational claim.** A real observational dataset is necessary because synthetic records usually encode the assumptions and thresholds used to generate them. A model can therefore learn the generator’s rules and achieve excellent test scores without learning the full complexity of actual floods.

Synthetic data is still useful for:

- Early pipeline and API development
- Testing rare combinations and failure paths
- Demonstrating the system before data-sharing approvals
- Balancing or augmenting under-represented classes, if clearly labelled as synthetic
- Regression tests with deterministic fixtures

It should not be the only evidence used to claim field accuracy.

### Recommended data strategy

Use a **hybrid progression**, not a sudden deletion of the current data:

1. Keep the synthetic dataset as a development fixture and baseline.
2. Acquire licensed, quality-controlled observations from official or reputable sources.
3. Build a documented schema mapping source fields to the 17 model features.
4. Preserve source, timestamp, station ID, units, quality flags, and missing-value reasons.
5. Create labels from a documented rule or authoritative event record. Do not silently use a feature-derived label that leaks the answer.
6. Retrain and compare synthetic-only, real-only, and hybrid models.
7. Use chronological, station-held-out, and preferably basin-held-out validation.
8. Report calibration, false negatives, per-class recall, lead time, and uncertainty—not just accuracy.
9. Run a shadow deployment against live data before allowing the system to influence decisions.

### Real-data risks to solve

- **Label quality:** “Flood risk” must be tied to a clear event definition, warning/danger mark, inundation observation, or official incident record.
- **Temporal leakage:** Future rainfall aggregates, post-event measurements, or revisions must not enter an earlier prediction window.
- **Station shift:** A model trained on one basin may not generalize to another.
- **Missingness and sensor faults:** Missing readings are operational signals, not automatically zero.
- **Class imbalance:** Critical events are rare; optimize for dangerous false negatives and report PR curves.
- **Units and datum differences:** Gauge levels and discharge values must be normalized and documented.
- **Licensing and governance:** Confirm permission to use, retain, redistribute, and operationalize each source.

## 5. Use-case comparison

### 5.1 Current project use case: local command-console demonstration

**Scenario:** An operator asks, “Which monitored locations need attention?” while the local FastAPI service is running.

1. The frontend loads the station registry from `/api/stations`.
2. The Overview page shows the four checked-in fallback stations when the API is offline; with the FastAPI service running, it loads the six stations in `backend/app/data/stations.json`.
3. Two Yamuna stations are shown as High risk from their checked-in telemetry.
4. The operator selects Old Railway Bridge.
5. The UI presents water level, warning mark, danger mark, rate of rise, rainfall, soil saturation, and upstream discharge.
6. The operator can ask the AI Assistant for a station assessment.
7. The agent calls bounded MCP tools, runs the champion model, and returns an advisory response.
8. The operator must manually verify the recommendation against official CWC/NDMA information.

**Value now:** An auditable academic demonstration of the data-to-assessment workflow.

**What it cannot safely do now:** Confirm real conditions, issue an official evacuation order, guarantee model accuracy, or deliver a reliable public warning.

### 5.2 Target future use case: operational early-warning workflow

**Scenario:** Heavy rainfall and upstream discharge rise across the Yamuna catchment overnight.

1. Licensed sensor and weather connectors ingest timestamped observations.
2. Quality checks identify stale, impossible, or missing values.
3. The feature service produces only values available at the prediction time.
4. The versioned model predicts risk and calibrated probabilities for each station.
5. A rules/policy service checks official warning and danger marks.
6. The system opens an incident and records the model version, data snapshot, evidence, and decision trail.
7. Role-based officers receive a dashboard alert and approved notification.
8. The agent summarizes evidence and proposes non-binding preparedness steps.
9. A human officer approves, edits, or rejects any public communication.
10. Every action is persisted for audit, later evaluation, and model improvement.
11. After the event, observed inundation and official records are joined back for lead-time and false-negative analysis.

**Value after completion:** Faster evidence synthesis, traceable decisions, measurable warning performance, and safer human-supervised operations.

## 6. Work remaining from now

### Phase 1 — Data credibility (highest priority)

1. Select one initial geography, preferably the Yamuna/NCR basin.
2. Identify authoritative water-level, rainfall, discharge, weather, and flood-event sources.
3. Confirm licensing/access and create a source register.
4. Implement ingestion, normalization, quality flags, timestamps, and raw-data retention.
5. Define and review the target-label policy with a hydrology/domain expert.
6. Retrain using chronological and station/basin holdouts.
7. Add calibration, false-negative analysis, lead-time evaluation, and model cards.

### Phase 2 — Backend reliability

1. Replace JSON-file mutation with a database or append-only event store.
2. Add request validation, structured errors, authentication, authorization, and rate limits.
3. Separate ingestion, feature computation, inference, alerts, and agent orchestration into testable services.
4. Add API contract tests and integration tests.
5. Add model versioning, artifact checksums, rollback, and health checks for dependencies.

### Phase 3 — Frontend operational behavior

1. Integrate a real map provider and geographic station/basin layers.
2. Add real time-series endpoints and render actual telemetry history.
3. Implement the What-if simulator using explicit, reproducible feature overrides.
4. Make filters, refresh, station detail, alerts, and report export functional.
5. Display data freshness, source, quality flags, model version, confidence/calibration, and uncertainty.
6. Add accessibility, responsive layouts, and end-to-end browser tests.

### Phase 4 — Safety and operations

1. Define alert escalation policies with authorized stakeholders.
2. Add human approval gates for every external/public communication.
3. Integrate official verification links and an incident/audit timeline.
4. Conduct threat modeling, dependency scanning, secrets management, and penetration testing.
5. Deploy in a staging environment with logs, metrics, tracing, backups, and recovery drills.
6. Run a shadow/pilot period before operational use.

## 7. Definition of “ready for pilot”

FloodGuard should not be described as pilot-ready until it has:

- A documented real-data source and label policy
- Independent temporal and geographic validation
- Demonstrated sensor-quality handling
- Measured false-negative and warning-lead-time performance
- Authenticated users and audited actions
- Persistent incident and model-version records
- Human approval for outbound alerts
- Staging tests, monitoring, rollback, and recovery procedures
- Domain-expert review and a shadow deployment

## 8. Local run commands

### Backend

```powershell
cd C:\Users\ishan\Desktop\flood\FloodGuard\backend
..\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend

```powershell
cd C:\Users\ishan\Desktop\flood\FloodGuard\frontend
npm install
npm run dev
```

### ML and MCP checks

```powershell
cd C:\Users\ishan\Desktop\flood\FloodGuard
.\.venv\Scripts\Activate.ps1
python ml\src\evaluate.py
python backend\app\mcp\test_mcp.py
```

## 9. Bottom line

The project has moved beyond a model-only prototype: the local service, MCP/agent workflow, and frontend command console are present. The next major milestone should **not** be adding more UI polish first. It should be establishing trustworthy real observational data, defensible labels, leakage-resistant evaluation, and operational auditability. Once those foundations are in place, the existing frontend can expose credible live decision support rather than only a convincing demonstration.
