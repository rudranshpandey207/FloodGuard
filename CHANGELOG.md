# FloodGuard — Project Change Log

This log records material repository changes, why they were needed, and how they are used. It is intentionally written for the project team and future maintainers rather than as a generated package release log.

## 2026-11-18 — Moved project virtual environment

### Moved `C:\Users\ishan\Desktop\flood\.venv` to `C:\Users\ishan\Desktop\flood\FloodGuard\.venv`

- **What changed:** Moved the existing Python virtual environment into the project folder and corrected its recorded creation command.
- **Why it was necessary:** The project should be self-contained so its interpreter, dependencies, and source files live under one project directory.
- **How it is used:** Activate it from the project root with `.\.venv\Scripts\Activate.ps1`. The moved environment was verified with Python 3.13.5, FastAPI, and pytest.
- **Validation:** `C:\Users\ishan\Desktop\flood\FloodGuard\.venv\Scripts\python.exe -m pytest backend\tests -q` is the project-local test command.

## 2026-11-18 — Phase 1 foundation stabilization

### Added `PHASES.md`

- **What changed:** Added the five-phase delivery plan, scope, dependencies, and exit criteria.
- **Why it was necessary:** The project needed a shared execution contract before making incremental changes toward a full synthetic-data demonstration.
- **How it is used:** Check the current phase before starting work and use its exit criteria to decide whether the phase is complete.

### Added `backend/app/config.py`

- **What changed:** Centralized app version, data mode, frontend origin, model version, and optional Gemini key settings.
- **Why it was necessary:** Configuration was previously embedded in route/application code, making local startup and future environment changes error-prone.
- **How it is used:** Set `FLOODGUARD_DATA_MODE`, `FLOODGUARD_MODEL_VERSION`, or `FLOODGUARD_FRONTEND_ORIGIN` as environment variables when needed. The default mode remains synthetic.

### Updated `backend/app/main.py`

- **What changed:** Used centralized settings, restricted development CORS to the configured frontend origins, and exposed data/model metadata in root and health responses.
- **Why it was necessary:** The previous wildcard CORS and missing metadata made the service less explicit and harder to verify from the frontend.
- **How it is used:** `/api/health` now identifies the active data mode and model version.

### Updated `backend/app/api/routes_prediction.py`

- **What changed:** Added strict request validation: unknown JSON fields and unknown feature names are rejected, blank locations are rejected, feature overrides are capped at the known feature set, and non-finite numbers are rejected. Prediction and model responses now include data mode and model version.
- **Why it was necessary:** Invalid scenario input should fail before inference rather than silently defaulting or producing misleading output.
- **How it is used:** Clients can rely on HTTP 422 for malformed input and can display the returned provenance metadata.

### Updated `backend/app/api/routes_stations.py`

- **What changed:** Added strict telemetry validation, including non-negative rainfall/discharge and a soil-moisture range of 0–1.
- **Why it was necessary:** The scenario update endpoint previously accepted physically invalid values.
- **How it is used:** Invalid telemetry receives HTTP 422 and does not update the station registry.

### Added `backend/tests/test_api.py`

- **What changed:** Added seven focused API contract tests.
- **Why it was necessary:** Phase 1 requires a repeatable safety net around health, stations, predictions, and input validation.
- **How it is used:** Run `python -m pytest backend/tests -q` from the repository root, or run `python -m pytest tests -q` from `backend/`.

### Added `frontend/src/api.js`

- **What changed:** Added one request helper for API base URL configuration, JSON parsing, request headers, and useful error messages.
- **Why it was necessary:** The frontend previously used duplicated raw fetch behavior and hid all API failures behind fallback data.
- **How it is used:** Set `VITE_API_BASE_URL` at build/dev time and import `requestJson` for API calls.

### Updated `frontend/src/main.jsx`, `frontend/src/styles.css`, and `frontend/README.md`

- **What changed:** Added dashboard loading state, explicit backend error state, synthetic/offline labels, API connectivity status, and configurable API URL documentation. The footer no longer claims the system is operational when the backend is offline.
- **Why it was necessary:** A demonstration fallback must never be confused with live telemetry, and users need to know why data is unavailable.
- **How it is used:** Start the frontend without the backend to see the clearly labelled offline synthetic mode; start FastAPI to see API-connected synthetic mode.

### Updated `requirements.txt`

- **What changed:** Added `pytest>=8.0.0` as the test dependency.
- **Why it was necessary:** The new API contract tests need an explicit, reproducible test runner.
- **How it is used:** Install the project requirements before running the test suite.

### Phase 1 validation

- `npm run build` — passed.
- `python -m pytest backend/tests -q` from the repository root — passed, 7 tests.
- `python -m pytest tests -q` from `backend/` — passed, 7 tests.
- No API key was required. `GEMINI_API_KEY` remains optional because the offline agent path is available.

## 2026-11-18 — Status-documentation accuracy correction

### Updated `CURRENT_STATUS.md`

- **What changed:** Clarified that the offline frontend fallback contains four stations while the live FastAPI station registry contains six, and changed the backend run command to start from `backend/` with `app.main:app`.
- **Why it was necessary:** The first status draft could make the fallback count appear to be the complete backend registry, and the launch command should match the existing package-relative imports.
- **How it is used:** Use the corrected commands and station-count distinction when demonstrating the system.

## 2026-11-18 — Documentation and project-status baseline

### Added `CURRENT_STATUS.md`

- **What changed:** Added a current-state report covering the ML pipeline, FastAPI routes, MCP/agent layer, frontend, known limitations, synthetic-data assessment, current and target use cases, prioritized future work, pilot-readiness criteria, and run commands.
- **Why it was necessary:** The original project documentation described the intended architecture and roadmap but did not clearly separate implemented features from planned MERN, real-time, mapping, data, and operational features. The team needed one source of truth for current scope and next steps.
- **How it is used:** Read this file before planning new work, presenting the project, claiming model performance, or deciding whether a feature is production-ready.

### Added `CHANGELOG.md`

- **What changed:** Added this maintenance log.
- **Why it was necessary:** The project had no durable record of what changed, why it changed, or how a change should be used. This is especially important for an ML/safety-oriented system where data, labels, model artifacts, UI behavior, and safety assumptions must remain traceable.
- **How it is used:** Add one dated entry for every material code, data, model, infrastructure, documentation, or configuration change. Include the affected path, reason, user-visible/operational effect, and validation performed.

## 2026-11-18 — React/Vite operations frontend

### Added `frontend/package.json`

- **What changed:** Added a Vite/React package manifest with `dev`, `build`, and `preview` scripts.
- **Why it was necessary:** The repository had a FastAPI backend and ML assets but no runnable frontend scaffold.
- **How it is used:** Run `npm install`, then `npm run dev` for local development or `npm run build` for a production bundle.

### Added `frontend/index.html`

- **What changed:** Added the Vite HTML entry point and FloodGuard page metadata.
- **Why it was necessary:** Vite needs an HTML entry document that mounts the React application.
- **How it is used:** Vite serves this file and mounts `frontend/src/main.jsx` into `#root`.

### Added `frontend/src/main.jsx`

- **What changed:** Added the React application with Overview, Stations, Model Lab, and AI Assistant views.
- **Why it was necessary:** The project roadmap called for an operational dashboard over the existing station, alert, prediction, model, and agent APIs.
- **How it is used:** The app calls:
  - `GET /api/stations`
  - `GET /api/alerts`
  - `GET /api/prediction/models`
  - `POST /api/agent/query`
- **Operational note:** It includes checked-in demo telemetry fallback so the interface remains previewable when FastAPI is unavailable. This fallback must not be mistaken for live data.

### Added `frontend/src/styles.css`

- **What changed:** Added the dark command-console visual system, cards, station map-style visualization, gauge, telemetry chart, model cards, alerts, table, and assistant layout.
- **Why it was necessary:** The frontend needed a consistent, usable interface for the project demonstration instead of raw API responses.
- **How it is used:** Imported by `main.jsx`; all current frontend styling is centralized here.

### Added `frontend/README.md`

- **What changed:** Added frontend setup instructions and API/fallback behavior.
- **Why it was necessary:** The root project documentation did not previously contain instructions for running the new frontend.
- **How it is used:** Follow it when starting the dashboard locally.

### Validation

- `npm install` completed successfully.
- `npm run build` completed successfully with Vite.
- Browser validation confirmed the Overview and Model Lab views render.
- The frontend was also checked with the backend unavailable to confirm the demo fallback works.
- `npm install` reported three high-severity dependency audit findings. These are not silently ignored; dependency review and remediation remain required before deployment.

## Existing implementation recorded for traceability

The following components were already present before this log was created and are now documented as the current baseline:

- `backend/app/main.py`: FastAPI application, CORS, route registration, root metadata, and health check.
- `backend/app/api/routes_stations.py`: station listing, station lookup, and local telemetry update.
- `backend/app/api/routes_prediction.py`: champion-model inference and model evaluation retrieval.
- `backend/app/api/routes_alerts.py`: derived alerts and preparedness recommendations.
- `backend/app/api/routes_agent.py`: agent query and MCP-tool listing endpoints.
- `backend/app/mcp/tools.py`: bounded hydrology, prediction, status, region, history, and preparedness tools.
- `backend/app/agent/flood_agent.py` and safety modules: deterministic ReAct-style workflow with safety guardrails.
- `backend/app/data/stations.json`: checked-in station registry and demonstration telemetry.
- `ml/src/`: dataset generation, feature engineering, training, and evaluation scripts.
- `ml/models/`: serialized candidate/champion models and evaluation reports.

## Change-log maintenance rules

For each future entry:

1. Use the date in `YYYY-MM-DD` format.
2. Name every affected path.
3. Explain why the change was necessary, not only what was edited.
4. Describe any behavior, data, model, API, or safety impact.
5. Record validation commands and whether they passed.
6. Record data-source, label-policy, model-version, and schema changes explicitly.
7. Never edit an old entry to hide history; add a correction entry instead.
