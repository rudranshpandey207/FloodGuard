# FloodGuard: An Agentic AI-Based Flood Risk Assessment & Emergency Response Decision Support System

> **Major Project Part-1 (15B19CI791)**  
> **Program:** B.Tech (CSE / ECS / ECE) — 7th Semester / 4th Year (2026–2027)  
> **Institution:** Jaypee Institute of Information Technology (JIIT), Noida  
> **Submitted to:** Mr. Shariq Murtuza  
> **Project Team:**
> - **Ishan Mittal** (Enrollment No: 9923103062)
> - **Himangi Rawat** (Enrollment No: 9923103064)
> - **Rudransh Pandey** (Enrollment No: 9923103073)

---

## 📌 Executive Summary

**FloodGuard** is an intelligent, multi-layered disaster decision-support system designed to address the challenges of conventional flood monitoring. Floods are complex hydrological hazards governed by non-linear interactions among rainfall intensity, catchment saturation, upstream barrage discharges, and river gauge hydraulics. Conventional platforms present these isolated data streams on separate dashboards, forcing emergency officers to manually synthesize fragmented information under high-stress conditions.

FloodGuard bridges this gap by combining:
1. **Domain-Specific Hydrological Machine Learning**: Supervised risk classification using **Logistic Regression**, **Random Forest**, and **XGBoost** (strictly compliant with university guidelines: **No TensorFlow, No Keras, No MATLAB**).
2. **Model Context Protocol (MCP) Tool Architecture**: An open, auditable interface giving the AI system strictly bounded access to environmental telemetry, historical breach records, and predictive models.
3. **Autonomous Flood Intelligence Agent (ReAct Framework)**: An autonomous reasoning agent that formulates multi-step investigation plans, dynamically invokes MCP tools, and synthesizes evidence-grounded reports.
4. **Human-in-the-Loop Safety & Policy Filter**: Strict adherence to disaster-management ethics; the AI provides non-binding decision support and does not autonomously issue legally binding evacuation orders.
5. **Modern Full-Stack Dashboard (MERN + FastAPI)**: High-performance architecture combining a Python prediction/agent microservice with a Node.js/Express + MongoDB persistence layer and an interactive React + Vite operational dashboard.

---

## 🏛️ System Architecture

```
                                 +--------------------------------------------------+
                                 |            USER / DISASTER RESPONSE TEAM         |
                                 +--------------------------------------------------+
                                                          |
                                                          | (HTTP / WebSocket)
                                                          v
                                 +--------------------------------------------------+
                                 |        APPLICATION FRONTEND (React.js + Vite)    |
                                 |  - Geospatial Flood Risk Map (Leaflet)           |
                                 |  - Real-Time Water Level & Rainfall Gauges       |
                                 |  - "What-If" Flash Flood Scenario Simulator      |
                                 |  - ML Model Comparison & Confusion Matrix UI     |
                                 |  - Agentic AI Assistant Chat & Tool Trace Drawer |
                                 +--------------------------------------------------+
                                                          |
                                                          | (REST API Calls)
                                                          v
                                 +--------------------------------------------------+
                                 |       APPLICATION GATEWAY (Node.js & Express)    |
                                 |  - User Auth & Session Management                |
                                 |  - Emergency Alert Broadcasts                    |
                                 |  - MongoDB Persistence (Chat logs, alert states) |
                                 +--------------------------------------------------+
                                                          |
                                                          | (Internal Microservice RPC)
                                                          v
                                 +--------------------------------------------------+
                                 |       PREDICTION & AGENT ENGINE (FastAPI)        |
                                 |                                                  |
                                 |   +------------------------------------------+   |
                                 |   |    FLOOD INTELLIGENCE AGENT (ReAct)      |   |
                                 |   |    Plan -> Select Tools -> Observe ->    |   |
                                 |   |    Synthesize -> Safety Guardrails       |   |
                                 |   +------------------------------------------+   |
                                 |                        |                         |
                                 |                        v                         |
                                 |   +------------------------------------------+   |
                                 |   |    MODEL CONTEXT PROTOCOL (MCP) LAYER    |   |
                                 |   |  - get_weather         - get_rainfall    |   |
                                 |   |  - get_water_level     - get_history     |   |
                                 |   |  - predict_flood_risk  - get_status      |   |
                                 |   |  - get_affected_areas  - get_recs        |   |
                                 |   +------------------------------------------+   |
                                 |                        |                         |
                                 |                        v                         |
                                 |   +------------------------------------------+   |
                                 |   |      SUPERVISED ML PREDICTION CORE       |   |
                                 |   |  - Champion Model: XGBoost (99.2% F1)    |   |
                                 |   |  - Random Forest & Logistic Regression   |   |
                                 |   |  - Rolling Rainfall (24h/72h/7d)         |   |
                                 |   |  - Soil Saturation & Stage Proximity     |   |
                                 |   +------------------------------------------+   |
                                 +--------------------------------------------------+
```

---

## 🛠️ Technology Stack

| Layer | Technology | Role & Significance |
| :--- | :--- | :--- |
| **Machine Learning** | Python, Scikit-learn, XGBoost, Pandas, NumPy | Hydrological feature engineering and supervised classification. Strictly compliant with university policy (**NO TensorFlow, Keras, or MATLAB**). |
| **Prediction Service** | FastAPI, Uvicorn, Pydantic | High-throughput, asynchronous REST API serving live ML model inference and feature attribution. |
| **Tool Protocol** | Model Context Protocol (MCP) | Industry-standard typed interface decoupling the language model from direct database manipulation. |
| **Agentic AI** | ReAct Pattern (Reason + Act), Google GenAI SDK | Autonomous multi-step planning, dynamic tool invocation, and grounded explanation synthesis. |
| **App Backend & DB** | Node.js, Express.js, MongoDB (MERN) | Manages authentication, incident logs, persistent alert subscriptions, and session history. |
| **Frontend UI** | React.js (v18+), Vite, Vanilla CSS Design System | Ultra-fast local development (ESM), interactive geospatial maps, animated telemetry gauges, and agent trace drawer. |
| **Mapping & Charts** | Leaflet, React-Leaflet, Chart.js / SVG Gauges | Visualizing river basins, floodplains, danger mark thresholds, and sensor curves. |

---

## 🔬 What Has Been Implemented So Far

### 1. Hydrological Data & Feature Engineering Pipeline (`ml/src/`)
Real-world flood prediction cannot rely on rainfall volume alone. The pipeline processes 16 domain-grounded hydrological variables across 6 sentinel monitoring stations (Yamuna, Hindon, and Ganga basins):
* **Temporal Rolling Precipitation Windows**:
  * `rainfall_1h_mm`: Immediate cloudburst/flash flood indicator.
  * `rainfall_24h_mm`: Short-term drainage saturation.
  * `rainfall_72h_mm`: Medium-term river catchment accumulation.
  * `rainfall_7d_mm`: Antecedent rainfall governing regional waterlogging.
* **Hydraulic River Stage Dynamics**:
  * `river_water_level_m`: Current gauge height.
  * `water_level_rate_of_rise_m_hr`: Velocity of rising floodwaters.
  * `stage_to_warning_ratio` & `stage_to_danger_ratio`: Normalized proximity to official Central Water Commission (CWC) benchmarks.
* **Catchment Mechanics**:
  * `soil_moisture_index`: Value between 0.0 (dry) and 1.0 (fully saturated).
  * `runoff_potential_index`: Product of rainfall and soil saturation ($Rainfall \times SoilMoisture$). When soil is saturated, rainfall converts into surface runoff with zero infiltration.
  * `drainage_strain_index`: Cumulative precipitation weighed against urban drainage capacity and elevation.
  * `upstream_discharge_cusecs`: High-volume barrage discharge releases (e.g., Hathnikund Barrage into the Yamuna).

### 2. Supervised Machine Learning Model Benchmarking (`ml/src/train.py` & `evaluate.py`)
Three candidate models were trained and evaluated on a **time-aware 80/20 train/test split** (3,504 training records, 876 held-out future test records) across 4 risk tiers: `Low (0)`, `Medium (1)`, `High (2)`, and `Critical (3)`:

| Candidate Model | Model Family | Accuracy | Weighted F1 | Macro F1 | Training Latency | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression** | Linear / Multinomial Baseline | **93.04%** | **0.9341** | 0.8894 | 2.28s | Baseline Benchmark |
| **Random Forest** | Bagging Ensemble (150 Trees) | **98.97%** | **0.9898** | 0.9866 | 1.05s | Candidate Model |
| **XGBoost Classifier** | Gradient Boosted Trees | **99.20%** | **0.9920** | **0.9851** | 5.88s | 🏆 **Champion Model (Deployed)** |

* All models, scalers, and confusion matrices are serialized in `ml/models/` (`champion_model.joblib`, `model_summary.json`, `evaluation_report.json`).

### 3. Model Context Protocol (MCP) Tool Server (`backend/app/mcp/`)
Implements all **8 standardized tools** specified in Section 7 of the project synopsis:
1. `get_weather(location, time_range)`: Fetches temperature, humidity, weather condition, and soil moisture.
2. `get_rainfall(location, time_range)`: Returns 1h, 24h, 72h, and 7-day cumulative rainfall.
3. `get_water_level(location, time_range)`: Returns current gauge height, rate-of-rise, and status vs. Warning/Danger marks.
4. `get_historical_floods(location)`: Returns historic peak flood records (e.g., historic 2023 Yamuna peak of 208.66m).
5. `predict_flood_risk(location, feature_override)`: Executes the champion XGBoost model, returning risk tier, probabilities, and top risk factors.
6. `get_risk_status(location)`: Rapid health-check summary of a monitoring station.
7. `get_affected_regions()`: Cross-basin survey returning all stations exceeding advisory thresholds.
8. `get_preparedness_recommendations(risk_level)`: Evidence-based disaster preparedness protocols.

*Verified with an automated integration test script (`test_mcp.py`) achieving 100% pass rate.*

### 4. Autonomous Flood Intelligence Agent & Safety Filter (`backend/app/agent/`)
* **ReAct Loop**: Formulates an explicit investigation plan, executes required MCP tools dynamically, grounds its response strictly in tool outputs, and displays the full tool-call trace.
* **Human-in-the-Loop Safety Filter (`safety.py`)**: Validates agent output to prevent unauthorized emergency declarations, replacing imperative commands with advisory language and appending mandatory CWC/NDMA verification notices.

### 5. High-Performance Prediction API (`backend/app/main.py`)
FastAPI application running on port `8000` with 10 interactive REST endpoints, CORS enabled, and auto-generated OpenAPI documentation available at `/docs`.

---

## 🔮 What is Planned Next (Future Roadmap)

### Phase 5: MERN Application Gateway & Persistence Layer
* **Node.js & Express API Gateway**: Runs on port `5000` to handle user authentication, notification subscriptions, and forward AI/ML queries to the FastAPI microservice.
* **MongoDB Collections**:
  * `users`: Authorized disaster management personnel.
  * `incidents`: Historical records of flood warnings and logged alerts.
  * `chat_sessions`: Persistent agent inquiry logs with recorded tool calls.

### Phase 6: Interactive Web Dashboard (React + Vite)
* **Geospatial Map View**: Interactive map using Leaflet with color-coded risk markers (Green: Low, Amber: Medium, Orange: High, Red: Critical) and river basin boundary overlays.
* **Real-Time Telemetry Gauges**: Animated SVG gauges displaying river level relative to official CWC danger marks.
* **"What-If" Flash Flood Scenario Simulator**: Interactive sliders allowing users to artificially simulate +150mm of cloudburst rainfall or 300,000 cusecs of barrage release and observe real-time model predictions.
* **Model Comparison & Explainability Tab**: Interactive confusion matrices, precision/recall curves, and feature importance rankings.
* **Agentic Chat Interface**: Conversational assistant with an expandable "Thought Process" drawer displaying the agent's multi-step plan, tool invocations, and confidence levels.

### Phase 7: Real-World Public API Grounding
* Live integration with the free, public **Open-Meteo API** for live weather and precipitation forecasts across the NCR and northern river catchments.

---

## 🎯 Academic Alignment: Complex Engineering Problem (WP / EA)

This project is aligned with the **Complex Engineering Problem (WP1–WP7)** and **Complex Engineering Activities (EA1–EA5)** criteria mandated by the Department:

* **WP1 (In-depth Knowledge)**: Integrates hydrological domain feature engineering, supervised gradient boosted trees, asynchronous Python web services, and the Model Context Protocol.
* **WP2 (Conflicting Issues)**: Balances early flood warning sensitivity (minimizing false negatives to protect human life) against false alarm rates (which induce public panic and unnecessary economic shutdown).
* **WP3 (Non-Obvious Approach)**: Solves the challenge of combining heterogeneous physical sensor readings (river stage, rainfall, soil saturation) with generative AI reasoning without allowing hallucination.
* **WP5 / EA4 (Safety, Ethics & Human Oversight)**: Enforces Section 15 safety guardrails. The AI is designed strictly for decision support, maintaining final operational authority with human emergency officers.
* **WP7 (Systems Approach)**: Connects data ingestion, ML training, API microservices, database persistence, MCP tools, and a reactive frontend into a unified deployable platform.

---

## 🚀 Quickstart: Running the Project Locally

### Prerequisites
* **Python 3.10+** (Tested on Python 3.12)
* **Node.js v18+** & **npm**

### Step 1: Virtual Environment & Dependencies
```powershell
# Navigate to project root
cd F:\Projects\floodguard

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Verify installed packages
pip list
```

### Step 2: Run the Machine Learning Pipeline
```powershell
# 1. Generate hydrological dataset
python ml/src/generate_dataset.py

# 2. Run feature engineering
python ml/src/feature_engineering.py

# 3. Train all models & export champion XGBoost
python ml/src/train.py

# 4. Generate evaluation reports & confusion matrices
python ml/src/evaluate.py
```

### Step 3: Test MCP Tools
```powershell
python backend/app/mcp/test_mcp.py
```

### Step 4: Start the FastAPI Prediction & Agent Engine
```powershell
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
* Interactive Swagger API Documentation: **`http://127.0.0.1:8000/docs`**

---

## 👥 Project Team & Contributions

* **Ishan Mittal (9923103062)**: Machine learning model benchmarking, XGBoost optimization, and hydrological feature engineering.
* **Himangi Rawat (9923103064)**: Model Context Protocol (MCP) server architecture, tool schema definitions, and human-in-the-loop safety filters.
* **Rudransh Pandey (9923103073)**: Full-stack architecture, FastAPI microservice design, agentic ReAct workflow orchestration, and MERN integration.
* **Supervisor: Mr. Shariq Murtuza**: Project guidance, problem formulation, and academic review.
