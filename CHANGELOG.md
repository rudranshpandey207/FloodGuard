# FloodGuard — Project Change Log

This log records material repository changes, why they were needed, and how they are used. It is intentionally written for the project team and future maintainers rather than as a generated package release log.

## 2026-11-18 — Complete technical and demonstration documentation

### Added `TECHNICAL_DOCUMENTATION.md`

- **What changed:** Added a complete architecture, technology, ML, API, MCP, persistence, Docker, safety, limitations, and future-scope reference.
- **Why it was necessary:** The project required one thorough document for evaluation, viva preparation, maintenance, and architectural handoff.
- **How it is used:** Use it to explain implementation, data flow, model decisions, and operational boundaries.

### Added `DEMO_GUIDE.md`

- **What changed:** Added a timed presentation sequence, exact UI actions, viva talking points, likely questions, pre-presentation checks, and Docker/direct startup alternatives.
- **Why it was necessary:** The team needed a repeatable way to demonstrate all major features without missing or overclaiming functionality.
- **How it is used:** Follow it from start-demo launch through AI/incident demonstration.

### Documentation corrections

- **What changed:** Corrected the root README and current status to distinguish implemented SQLite/FastAPI/React capabilities from earlier planned Node/MongoDB architecture.
- **Why it was necessary:** Previous architecture text could imply that authentication and MongoDB persistence were already implemented when they were still future work.

## 2026-11-18 — One-command Docker demo launcher

### Added `start-demo.ps1`

- **What changed:** Added a PowerShell launcher that checks Docker, builds/starts Compose services in detached mode, prints URLs, and opens the frontend.
- **Why it was necessary:** Docker startup previously required separate build/start and browser commands.
- **How it is used:** From the project root, run `.\start-demo.ps1`.
- **Validation:** Docker Desktop engine is running; Compose backend and frontend containers started successfully on ports `8000` and `5173`.

## 2026-11-18 — Major-project evaluation finalization

### Added `FINAL_EVALUATION.md`

- **What changed:** Added an evaluation-ready scope, recommended demonstration sequence, startup commands, verification commands, and explicit non-operational limitations.
- **Why it was necessary:** Docker Desktop is optional and may not run on the evaluator machine. The project needed a definitive academic-demonstration baseline that does not depend on Docker.
- **How it is used:** Follow this file before the final presentation or viva.

### Final scope decision

- Docker is retained as an optional Phase 5 deployment asset, not as a required evaluation dependency.
- Direct FastAPI and Vite startup are the supported evaluation path.
- Official CWC/WRIS live gauge/discharge integration remains future work.
- Real-data retraining and operational validation remain future work.

## 2026-11-18 — Phase 5 Docker startup started

### Added Docker deployment baseline

- **What changed:** Added `backend/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml`, and `.dockerignore`.
- **Why it was necessary:** Phase 5 needs a reproducible demo startup separate from manually managed local terminals.
- **How it is used:** Run `docker compose up --build` from the project root. Backend is published on port `8000`; frontend is published on port `5173`.

## 2026-11-18 — Phase 4 incident workflow

### Added `backend/app/api/routes_incidents.py`

- **What changed:** Added SQLite-backed incident creation, listing, detail, status updates, acknowledgement timestamps, and audit entries.
- **Why it was necessary:** Phase 4 requires persistent human-supervised alert handling rather than a visual-only incident control.
- **How it is used:** Create incidents from the UI, change status through Investigating/Acknowledged/Resolved, and retrieve audit details through incident APIs.
- **Safety:** Status changes require an operator name and are not executed by Gemini or MCP synthesis.

### Updated `backend/app/main.py` and `.gitignore`

- **What changed:** Registered incident routes and excluded `.db`, `.sqlite`, and `.sqlite3` files from source control.

### Updated `frontend/src/main.jsx` and `frontend/src/scenario.css`

- **What changed:** Added an Incidents navigation view, operator and station form, incident list, and human status buttons.
- **Validation:** 20 backend tests passed; frontend build passed; browser verification created and acknowledged an incident successfully.

## 2026-11-18 — Scenario history and temperature/humidity controls

### Updated `frontend/src/main.jsx` and `frontend/src/scenario.css`

- **What changed:** Added temperature and humidity sliders, local browser persistence for the latest 10 scenarios, export-to-JSON, and clear-history controls.
- **Why it was necessary:** Scenarios should be reproducible and reviewable after a prediction run; official gauge integration is deferred, so local evidence must remain useful for the synthetic/what-if workflow.
- **How it is used:** Run a scenario to save it locally; export the recent list as JSON or clear it from the browser.
- **Validation:** `npm run build` passed, 19 backend tests passed, browser verification showed temperature/humidity controls and the recent-scenarios panel.
- **Boundary:** Stored scenarios remain in this browser only and are not server-persisted incidents or official records.

## 2026-11-18 — Open-Meteo live weather preview

### Added `backend/app/api/routes_integrations.py`

- **What changed:** Added keyless Open-Meteo integration at `GET /api/integrations/weather/{station_id}`.
- **What it provides:** Rolling 1h, 24h, 72h, and 7d precipitation, temperature, humidity, soil moisture, timestamp, source URL, and missing-field list.
- **How it is used:** Scenario Lab can load live weather while preserving station-based synthetic river level and discharge until a gauge/discharge source is connected.
- **Fallback behavior:** HTTP, network, and unusable-response failures return explicit 502/503 API errors rather than silently fabricating values.

### Updated `frontend/src/main.jsx` and `frontend/src/scenario.css`

- **What changed:** Added a Live Weather Preview panel to Scenario Lab with an Open-Meteo load action and missing-field status.
- **Why it was necessary:** Phase 3 needs external weather inputs before moving to a full live-assessment pipeline.

### Validation

- Pylance syntax check — no syntax errors in `routes_integrations.py`.
- Backend tests — 18 passed, including rolling precipitation parsing and unknown-station integration handling.
- Live endpoint verification — `STN_YAM_01` returned Open-Meteo data with timestamp, rolling rainfall, temperature, humidity, soil moisture, and no missing fields.
- Timezone fix — normalized naive Open-Meteo hour strings and local-aware `datetime.now()` values before comparison.
- Browser verification — Scenario Lab loaded live weather and applied rainfall, soil moisture, and 7-day rainfall controls.
- Frontend build — passed.

## 2026-11-18 — Phase 3 what-if prediction lab

### Updated `frontend/src/main.jsx` and added `frontend/src/scenario.css`

- **What changed:** Added Scenario Lab navigation and a station-based what-if interface with rainfall, river level, rate of rise, soil moisture, and upstream discharge controls.
- **Why it was necessary:** Phase 3 requires a visible, reproducible way to compare baseline and simulated flood risk without mutating station telemetry.
- **How it is used:** Select a station, change controls, and run the XGBoost prediction to see baseline risk, simulated risk, tier change, class probabilities, and model risk drivers.

### Updated `backend/app/mcp/tools.py`

- **What changed:** Recomputed stage-to-warning, stage-to-danger, runoff-potential, and drainage-strain derived features after applying scenario overrides.
- **Why it was necessary:** Raw river/rainfall/soil overrides could otherwise leave derived model inputs stale.
- **How it is used:** Every location-based prediction override now produces a consistent feature set before model inference.

### Updated `backend/app/api/routes_prediction.py`

- **What changed:** Added `scenario_mode` and `feature_overrides` response metadata. Expanded scenario override validation for negative rainfall/discharge and soil moisture outside 0–1.

### Updated `backend/tests/test_api.py`

- **What changed:** Added scenario success, negative rainfall, and invalid soil moisture tests.

### Phase 3 validation

- `python -m pytest backend\tests -q` — passed, 16 tests.
- `npm run build` — passed.
- Browser verification — Scenario Lab rendered and ran baseline/simulation predictions.
- Verified simulation — Old Railway Bridge changed from High / 76.9% baseline to Critical / 99.4% at 400 mm 24h rainfall, 600 mm 72h rainfall, and 206.2 m river level (+1 tier).
- Pylance syntax check — `backend/app/mcp/tools.py` returned no syntax errors.

## 2026-11-18 — Friendly offline conversational routing

### Updated `backend/app/agent/flood_agent.py`

- **What changed:** Added conversational intent handling for greetings, help/capabilities, thanks, and unsupported general queries before location extraction.
- **Why it was necessary:** Any unrecognized query previously reached `_extract_location_mention()`, which returned `Delhi` and produced a station assessment even for `hey` or `how are you`.
- **How it is used:** `hey`, `hi`, and `hello` explain the bot’s capabilities; help requests list supported flood-risk queries; unsupported general questions are redirected without pretending to have Delhi evidence.
- **Fallback behavior:** Conversational responses do not call Gemini or MCP tools and are returned directly as deterministic offline assistance. Gemini synthesis calls for other questions now use a 12-second HTTP timeout.

### Updated `frontend/src/main.jsx`

- **What changed:** Replaced the initial generic morning message with a friendly capability summary and added `What can you do?` to the suggested prompts.
- **Why it was necessary:** New users should immediately understand supported actions instead of seeing a response that implies a live station is being summarized.

### Updated `backend/tests/test_api.py`

- **What changed:** Added greeting, help, and unknown-query API tests.
- **Validation:** 13 backend tests cover greeting, help, unknown-query, station, prediction, and regional routing behavior.

## 2026-11-18 — Backend network telemetry chart

### Updated `backend/app/api/routes_stations.py`

- **What changed:** Added `GET /api/stations/network/history`, returning 25 deterministic synthetic network-average samples for the last 24 hours.
- **Why it was necessary:** The Overview chart still used hardcoded SVG paths and fixed labels. It needed a backend-owned series with explicit synthetic provenance.
- **How it is used:** The frontend requests this endpoint and renders average water level, relative timestamps, and synthetic quality metadata.

### Updated `frontend/src/main.jsx`

- **What changed:** Replaced the illustrative Overview water-level path with dynamic points from the network-history endpoint, including calculated chart bounds and -24h-to-NOW labels.
- **Fallback behavior:** If the endpoint fails, the chart displays “Network history unavailable” instead of showing fabricated telemetry.
- **How it is used:** The header identifies the series as 24-hour synthetic data and the chart updates from backend values.

## 2026-11-18 — Gemini integration and Phase 2 alert/report work

### Added project-root ignored `.env`

- **What changed:** Stored `GEMINI_API_KEY` and `GEMINI_MODEL=gemini-3.8-flash` in the project-root `.env`, which is excluded by `.gitignore`.
- **Security:** The supplied key appeared in chat and should be considered exposed. It should be revoked and replaced in Google AI Studio even though it is not present in source files.
- **Why it was necessary:** Gemini synthesis is optional but should use a local environment secret, never a frontend constant or committed credential.

### Updated `backend/app/agent/flood_agent.py`

- **What changed:** Added an optional Gemini synthesis step after MCP/model evidence is collected. Added `synthesis_source` and `gemini_enabled` to agent responses.
- **Fallback behavior:** Missing credentials, API errors, quota limits, model outages, or 503 capacity errors return the deterministic offline response. Safety guardrails are applied after both Gemini and fallback synthesis.
- **Validation:** Direct SDK testing reached `gemini-3.8-flash` but Google returned 503 high-demand; the agent correctly returned `offline-deterministic-fallback` and retained all MCP evidence.

### Updated `frontend/src/main.jsx`

- **What changed:** Added Gemini/offline synthesis badges to assistant messages, alert severity filtering, and CSV station report export.
- **How it is used:** Assistant messages show whether Gemini or the offline fallback produced the wording. The Overview alert panel can filter High/Critical alerts, and Export Report downloads station state as CSV.

## 2026-11-18 — Phase 2 station detail and refresh work

### Updated `frontend/src/main.jsx`

- **What changed:** Added dashboard refresh, selectable station detail panel, station search, risk filtering, and a synthetic 24-hour station history sparkline.
- **Why it was necessary:** Phase 2 requires complete operator navigation rather than only a map and overview cards. Search and detail panels expose station-specific evidence, while refresh reloads API state without restarting the app.
- **How it is used:** Use the Overview floating refresh button, open Stations for search/filter/detail, and select rows to update the detail panel.
- **Data limitation:** The history endpoint is deterministic synthetic data and is clearly labelled, because no real historical telemetry source is connected yet.

### Updated `backend/app/api/routes_stations.py`

- **What changed:** Added `GET /api/stations/{station_id}/history` with 25 deterministic synthetic samples and explicit data provenance.
- **Why it was necessary:** The station-detail view needs a repeatable backend-provided series instead of a separate hardcoded frontend chart.
- **How it is used:** The station page requests a series for the selected station. It must not be presented as observed history.

### Map API decision

- **What changed:** No paid API or key was added.
- **Why:** Leaflet, OpenStreetMap, and CARTO provide the basemap and coordinate visualization without a paid map token. A paid provider would be needed mainly for premium basemap styling, commercial SLA, satellite imagery, or flood-specific map layers.
- **Accuracy note:** Marker accuracy depends on coordinates in `backend/app/data/stations.json`; basemap accuracy and scale can be adjusted later through real station-coordinate and datum validation.

## 2026-11-18 — Phase 2 dashboard map started

### Updated `frontend/package.json`

- **What changed:** Added `leaflet` and `react-leaflet` dependencies for real interactive geospatial station mapping.
- **Why it was necessary:** The previous regional map was a schematic CSS/SVG visualization rather than a navigable geographic map.
- **How it is used:** The Overview map will render real station coordinates with Leaflet tiles, clickable markers, popups, zooming, and risk filtering.

### Updated `frontend/src/main.jsx` and `frontend/src/styles.css`

- **What changed:** Started replacing the schematic map with `MapContainer`, `TileLayer`, and risk-colored `CircleMarker` components. Added a risk filter and map focus when a station is selected.
- **Why it was necessary:** Phase 2 requires an operator to select and filter stations geographically instead of relying on a decorative map.
- **How it is used:** Select an Overview marker or change the map risk filter to inspect matching synthetic stations.
- **Validation:** Leaflet 1.9.4 and React-Leaflet 4.2.1 pass a production build. Browser verification confirmed the real map, zoom controls, station markers, and High-risk filter (`2 of 6 stations`).

### Updated `backend/app/agent/flood_agent.py`

- **What changed:** Added regional detection for questions such as “is Delhi at risk?” so they can trigger the affected-regions survey rather than a single-station assessment.
- **Why it was necessary:** A geographic question is not necessarily a request for one station. Routing it to a station-only response can be misleading.
- **How it is used:** Delhi/NCR risk queries now request the affected-region tool and return multiple monitored station results.

### Gemini API key status

- **What changed:** No Gemini integration was added for this step.
- **Why:** Phase 2 and the current offline agent do not require a Gemini API key. The key remains optional for later conversational/language-generation enhancements in Phase 4 or 5.

## 2026-11-18 — Agent response formatting and tool-trace fix

### Updated `frontend/src/main.jsx`

- **What changed:** Added React formatting for headings, bold text, inline code values, bullets, and separators returned by the agent. Added a visible expandable MCP tool trace using the backend’s `tool_calls` response field and investigation plan.
- **Why it was necessary:** The agent response was previously placed inside a plain `<p>`, so Markdown markers such as `###`, `**`, and backticks appeared literally as in the user screenshot.
- **How it is used:** Agent responses now render as structured assessment sections, while the trace button reveals plan steps and MCP tool summaries.
- **Validation:** Frontend build passed. Browser verification confirmed the agent response renders structured headings, bold values, evidence bullets, and the 5-call MCP trace drawer.

### Phase 2 validation update

- `npm run build` — passed with the real Leaflet map dependencies.
- `python -m pytest backend\tests -q` — passed, 10 tests.
- Network history endpoint — returned 25 synthetic points from `-24h` to `NOW` across 6 stations.
- Browser verification — the real map renders, zoom works, and the High risk filter shows 2 of 6 stations.
- Delhi/NCR regional routing — `is delhi at risk?` now returns the affected-regions response with Old Railway Bridge, Okhla Barrage, and Hindon Ghaziabad, rather than a single-station response.

### Updated `backend/app/agent/flood_agent.py`

- **What changed:** Removed an extra bullet character from model-contributed risk-driver entries.
- **Why it was necessary:** The frontend formatter already adds a bullet, so the backend text had created double-prefixed risk-driver lines.
- **How it is used:** Contributing risk drivers now render once per line as a clean UI bullet.

## 2026-11-18 — Duplicate-server troubleshooting during UI validation

### Resolved frontend “offline synthetic fallback” screenshots

- **What changed:** Identified that the screenshots were caused by stale or duplicate local frontend/backend server processes, not by missing React rendering or a frontend compilation defect.
- **Why it was necessary:** The browser first showed an offline fallback banner while the existing backend was also healthy, and stale Vite instances had moved the frontend between ports or stopped accepting connections.
- **How it is used:** Start only one backend on port `8000` and one frontend on port `5173`. When port conflicts occur, stop the specific process listening on that port and restart the application. The frontend now distinguishes API-connected synthetic mode from offline synthetic fallback mode.
- **Validation:** `/api/health` returned `data_mode: synthetic` and `model_version: xgboost-champion-local`; a clean Vite restart showed six live synthetic stations and `API CONNECTED · SYNTHETIC`.

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
