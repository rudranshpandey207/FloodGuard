# FloodGuard — Delivery Phases

This file is the execution plan for completing the synthetic-data demonstration application. **Phase 1 is complete**, **Phase 2 is complete**, **Phase 3 is complete**, and the current work is **Phase 4**.

## Phase 1 — Stabilize the Existing Foundation

**Goal:** Make the current ML, FastAPI, and React application predictable to run, validate, and demonstrate.

**Scope:**

- Centralize backend configuration and local data-mode metadata.
- Validate API inputs and return consistent errors.
- Add focused backend API tests.
- Centralize frontend API calls and expose loading/error/offline state.
- Make synthetic/demo data status explicit.
- Verify frontend build and backend test commands.
- Record every material change in `CHANGELOG.md`.

**Exit criteria:**

- Backend starts with one documented command.
- Health, stations, prediction, alerts, and agent API behavior is covered by tests.
- Invalid prediction and telemetry input is rejected before model/file work.
- Frontend has explicit loading and error states and does not mislabel fallback data as live.
- Frontend production build passes.

## Phase 2 — Complete the Core Operations Dashboard

**Goal:** Turn the current dashboard into a fully functional monitoring interface.

**Scope:**

- Real interactive map with station markers and risk filtering.
- Functional station detail view and alert filters.
- Historical telemetry API and real charts.
- Refresh, export, and station navigation actions.
- Responsive and accessible operator interface.

**Phase 2 started:** The overview map is being converted from a schematic visualization to a real interactive Leaflet map with filterable station markers.

**Exit criteria:**

- An operator can select, filter, inspect, and refresh every station.
- All charts are backed by API data rather than illustrative values.
- Main dashboard workflows have browser tests.

## Phase 3 — Prediction and What-If Simulation

**Goal:** Provide transparent, reproducible prediction and scenario analysis.

**Scope:**

- Feature-input and station-based prediction flows.
- What-if overrides for rainfall, discharge, stage, soil saturation, and rate of rise.
- Current-versus-simulated comparison.
- Probability, driver, model-version, and validation display.
- Prediction boundary and regression tests.

**Exit criteria:**

- A user can run a valid prediction from the UI.
- A user can run a marked simulation without mutating baseline telemetry.
- Invalid and extreme inputs receive clear feedback.

## Phase 4 — Agent, Alerts, and Incident Workflow

**Goal:** Make AI assistance auditable and human-supervised.

**Scope:**

- Structured agent responses and MCP/tool trace drawer.
- Alert acknowledgement and escalation.
- Local incident lifecycle and audit timeline.
- Preparedness panels and human approval gates.
- Explicit separation of AI advice, official warnings, and approved actions.

**Phase 4 started:** Incidents now persist in SQLite and support human Open → Investigating → Acknowledged → Resolved transitions with audit entries.

**Exit criteria:**

- Every agent recommendation shows its evidence and safety notice.
- Incidents and alert actions are traceable.
- No AI response can be treated as an autonomous evacuation order.

## Phase 5 — Reliability, Security, and Demonstration Readiness

**Goal:** Produce a complete, repeatable, testable project demonstration.

**Scope:**

- Authentication, roles, and persistent storage.
- Request IDs, structured logs, backups, and environment configuration.
- Full API, integration, and end-to-end test suites.
- Dependency/security review and reproducible startup.
- Demonstration scenario from telemetry change through incident resolution.

**Exit criteria:**

- A clean machine can start the system from documented commands.
- Critical workflows are tested and auditable.
- Synthetic data and model versions are visibly labelled everywhere.
- The project is ready for academic evaluation and later real-data replacement.

## Dependency order

`Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5`

Real-data integration remains a later track. Until then, all screens, logs, predictions, and demonstrations must visibly identify the system as synthetic-data based.
