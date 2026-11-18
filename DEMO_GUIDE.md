# FloodGuard — Major Project Demonstration Guide

## 1. Before the demonstration

### Requirements

- Docker Desktop running
- Internet available for map tiles and Open-Meteo weather
- Gemini key optional
- Browser open at `http://localhost:5173`

### Start

From Windows PowerShell:

```powershell
cd C:\Users\ishan\Desktop\flood\FloodGuard
.\start-demo.ps1
```

Wait until the script prints:

```text
FloodGuard frontend: http://localhost:5173
FloodGuard API docs: http://localhost:8000/docs
```

### If Docker is unavailable

```powershell
cd C:\Users\ishan\Desktop\flood\FloodGuard\backend
..\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

In another terminal:

```powershell
cd C:\Users\ishan\Desktop\flood\FloodGuard\frontend
npm run dev
```

## 2. Recommended 10-minute demonstration

### Minute 0–1: Problem and scope

Say:

> FloodGuard combines hydrological data, machine learning, MCP tools, an AI agent, and human oversight. All station observations in this prototype are synthetic. The system demonstrates the intended workflow and must not be presented as an official real-time warning system.

### Minute 1–2: Overview

Open **Overview**.

Point out:

- Six stations
- Two High-risk alerts in the synthetic data
- Leaflet geographic map
- Risk marker colors
- 99.2% XGBoost model confidence metric
- Current station gauge and thresholds

### Minute 2–3: Real map and filtering

On the map:

1. Select `High` in the risk filter.
2. Explain that only the two High-risk stations remain visible.
3. Change to `All`.
4. Click an Old Railway Bridge marker.
5. Explain that the selected station detail updates.

### Minute 3–4: Stations and data

Open **Stations**.

Demonstrate:

- Search for `Yamuna`
- Filter by `High`
- Select the Old Railway Bridge row
- Read water level, warning mark, danger mark, rainfall, rate of rise, soil saturation, and discharge
- Explain that the history sparkline is synthetic

### Minute 4–5: Model Lab

Open **Model Lab**.

Explain:

- Logistic Regression is the baseline
- Random Forest is the ensemble candidate
- XGBoost is deployed as champion
- The current accuracies and feature rankings are based on the synthetic holdout dataset

### Minute 5–7: Scenario Lab

Open **Scenario Lab**.

Demonstrate baseline prediction:

1. Select Yamuna Old Railway Bridge.
2. Click **Run prediction**.
3. Show High risk and probabilities.

Demonstrate escalation:

1. Set 24-hour rainfall to `400` mm.
2. Set 72-hour rainfall to `600` mm.
3. Set river level to `206.2` m.
4. Run prediction.
5. Show the result can change to Critical with a +1 tier change.

Explain:

- The controls are what-if overrides.
- Derived stage/runoff/drainage features are recalculated.
- Baseline station data are not mutated.
- These predictions use synthetic training data.

### Minute 7–8: Open-Meteo

Click **Load live weather**.

Explain:

- Open-Meteo requires no key in this implementation.
- It provides weather and rolling precipitation preview values.
- It does not provide official CWC gauge level or barrage discharge.
- The result is a mixed-source demonstration, not an official warning.

### Minute 8–9: AI Assistant

Open **AI Assistant**.

Start with:

```text
hey
```

Explain that the greeting is handled as a friendly offline capability response, not as a Delhi-location query.

Then ask:

```text
is delhi at risk?
```

Explain the response now surveys affected Delhi-region stations rather than returning only one station.

Open **View tool trace** and explain:

- Investigation plan
- MCP tool calls
- Tool arguments and summaries
- Evidence grounding
- Human safety notice

Optional Gemini status:

- Say that Gemini enhances wording only.
- If unavailable or quota-limited, the deterministic offline agent remains active.
- Gemini has no direct database or model mutation tools.

### Minute 9–10: Incidents

Open **Incidents**.

1. Enter a short operator name.
2. Select Yamuna Old Railway Bridge.
3. Enter `Synthetic flood-risk review for demonstration`.
4. Create incident.
5. Select the incident to inspect its audit timeline.
6. Click **Investigate**.
7. Acknowledge and confirm the human approval dialog.
8. Optionally resolve and confirm approval again.

Explain:

- Incidents are stored in SQLite.
- Audit entries record creation and status changes.
- AI output does not create or resolve an incident by itself.

## 3. Viva explanation topics

### Why FastAPI?

FastAPI provides typed Pydantic validation, asynchronous capability, automatic API documentation, and a convenient Python interface for scikit-learn/XGBoost models.

### Why MCP?

MCP-style tools define bounded evidence operations. The agent can read data and run prediction without direct uncontrolled database or infrastructure access.

### Why no TensorFlow or MATLAB?

The system uses scikit-learn and XGBoost, satisfying the project’s supervised-machine-learning/compliance requirement.

### Why XGBoost?

It achieved the highest held-out accuracy and weighted F1 in the current synthetic benchmark and is stored as the deployed champion model.

### Why synthetic data?

It allows development and end-to-end academic evaluation while real official gauge/discharge acquisition and licensing are completed later. The UI and evidence clearly identify synthetic data.

### Why Leaflet?

Leaflet is a free, extensible JavaScript map library with OpenStreetMap/CARTO basemap support and no mandatory paid map API key.

### Why SQLite?

SQLite is sufficient for a local academic prototype and supports incident/audit/chat persistence without requiring an external database server. MongoDB or PostgreSQL can replace it for a later multi-user deployment.

### Why Docker?

Docker provides reproducible frontend/backend startup and isolates runtime dependencies. Direct Vite/Uvicorn startup remains supported without Docker.

## 4. Questions that may appear

**“Is this live?”**

Answer: Synthetic station telemetry and river/discharge values are demonstrative. Open-Meteo weather is the live weather preview. CWC/WRIS official gauge/discharge integration is future work.

**“Can it issue evacuation orders?”**

No. It is human-in-the-loop decision support. The safety layer rejects/directs imperative wording toward advisory language.

**“Is 99.2% accuracy enough?”**

It is a result on the current synthetic held-out dataset only. Real-world deployment requires real flood events, temporal/geographic holdouts, calibration, false-negative review, and hydrologist validation.

**“Why not real data now?”**

Official gauge acquisition requires mapping exact WRIS/CWC station IDs, units, datums, timestamps, and data-usage permissions. That integration was intentionally deferred until verified source data is available.

**“What happens if Gemini fails?”**

The agent uses deterministic MCP tool collection and an offline formatted assessment. It remains evidence-grounded.

**“What is the most important remaining production work?”**

Official gauge/discharge integration, real label/data validation, authentication/roles, immutable logs, secure public deployment, alert authorization, and independent hydrological review.

## 5. Pre-presentation verification

```powershell
cd C:\Users\ishan\Desktop\flood\FloodGuard
.\.venv\Scripts\Activate.ps1
python -m pytest backend\tests -q
cd frontend
npm run build
cd ..
.\start-demo.ps1
```

Expected:

- Backend tests pass
- Frontend build passes
- Docker containers start
- Browser opens at `http://localhost:5173`
