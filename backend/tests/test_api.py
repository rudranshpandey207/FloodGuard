"""Focused API contract tests for the local foundation."""

import os

os.environ["GEMINI_API_KEY"] = ""

from fastapi.testclient import TestClient

try:
    from backend.app.main import app
    from backend.app.api.routes_integrations import summarize_hourly_weather
except ModuleNotFoundError:
    from app.main import app
    from app.api.routes_integrations import summarize_hourly_weather


client = TestClient(app)


def test_persistent_chat_session_workflow():
    created = client.post("/api/chat/sessions", json={"title": "Test operator chat"})
    assert created.status_code == 201
    session_id = created.json()["id"]

    message = client.post(f"/api/chat/sessions/{session_id}/messages", json={
        "role": "user",
        "content": "Is Delhi at risk?",
        "synthesis_source": "operator-input",
        "tool_count": 0,
    })
    assert message.status_code == 201

    history = client.get(f"/api/chat/sessions/{session_id}/messages")
    assert history.status_code == 200
    assert len(history.json()["messages"]) == 1


def test_create_and_update_incident():
    response = client.post("/api/incidents", json={
        "title": "Test flood incident",
        "station_id": "STN_YAM_01",
        "station_name": "Yamuna Test Station",
        "river": "Yamuna",
        "risk_label": "High",
        "risk_level": 2,
        "water_level_m": 205.15,
        "danger_level_m": 205.33,
        "operator": "Test Operator",
        "summary": "Test acknowledgement workflow",
    })
    assert response.status_code == 201
    incident = response.json()
    assert incident["status"] == "Open"

    updated = client.patch(f"/api/incidents/{incident['id']}", json={
        "status": "Acknowledged",
        "operator": "Test Operator",
        "note": "Human acknowledged the incident",
        "approval_confirmed": True,
    })
    assert updated.status_code == 200
    assert updated.json()["status"] == "Acknowledged"
    assert updated.json()["acknowledged_at"]
    assert updated.json()["approval_confirmed"] is True

    detail = client.get(f"/api/incidents/{incident['id']}")
    assert detail.status_code == 200
    assert len(detail.json()["audit"]) >= 2


def test_acknowledgement_requires_human_approval():
    created = client.post("/api/incidents", json={
        "title": "Approval test incident",
        "risk_label": "High",
        "risk_level": 2,
        "operator": "Test Operator",
        "summary": "Approval gate test",
    })
    assert created.status_code == 201
    updated = client.patch(f"/api/incidents/{created.json()['id']}", json={
        "status": "Acknowledged",
        "operator": "Test Operator",
        "note": "Missing approval confirmation",
    })
    assert updated.status_code == 422


def test_open_meteo_hourly_summary_rolling_windows():
    from datetime import datetime

    payload = {
        "hourly": {
            "time": [f"2026-11-18T{hour:02d}:00" for hour in range(24)],
            "precipitation": [1.0] * 24,
            "temperature_2m": [25.0] * 24,
            "relative_humidity_2m": [80.0] * 24,
            "soil_moisture_0_to_7cm": [0.42] * 24,
        }
    }
    result = summarize_hourly_weather(payload, now=datetime(2026, 11, 18, 23, 30))
    assert result["rainfall_1h_mm"] == 1.0
    assert result["rainfall_24h_mm"] == 24.0
    assert result["temperature_c"] == 25.0
    assert result["soil_moisture_index"] == 0.42


def test_unknown_integration_station_returns_not_found():
    response = client.get("/api/integrations/weather/STN_UNKNOWN")
    assert response.status_code == 404


def test_health_identifies_synthetic_mode():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["data_mode"] == "synthetic"
    assert response.json()["model_version"]


def test_stations_are_available():
    response = client.get("/api/stations")
    assert response.status_code == 200
    stations = response.json()
    assert len(stations) == 6
    assert all("current_telemetry" in station for station in stations)


def test_unknown_station_returns_not_found():
    response = client.get("/api/stations/does-not-exist")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_prediction_requires_a_location_or_features():
    response = client.post("/api/prediction/predict", json={})
    assert response.status_code == 400
    assert "features" in response.json()["detail"].lower()


def test_scenario_prediction_returns_metadata_and_probabilities():
    response = client.post(
        "/api/prediction/predict",
        json={
            "location": "Delhi",
            "feature_override": {
                "river_water_level_m": 206.0,
                "rainfall_72h_mm": 250.0,
                "soil_moisture_index": 0.95,
                "upstream_discharge_cusecs": 300000,
            },
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["scenario_mode"] is True
    assert body["data_mode"] == "synthetic"
    assert set(body["class_probabilities"]) == {"Low", "Medium", "High", "Critical"}


def test_scenario_rejects_negative_feature_override():
    response = client.post(
        "/api/prediction/predict",
        json={"location": "Delhi", "feature_override": {"rainfall_24h_mm": -1}},
    )
    assert response.status_code == 422


def test_scenario_rejects_invalid_soil_moisture_override():
    response = client.post(
        "/api/prediction/predict",
        json={"location": "Delhi", "feature_override": {"soil_moisture_index": 1.5}},
    )
    assert response.status_code == 422


def test_prediction_rejects_unknown_feature_override():
    response = client.post(
        "/api/prediction/predict",
        json={"feature_override": {"not_a_feature": 1}},
    )
    assert response.status_code == 422


def test_scenario_temperature_and_humidity_are_validated():
    response = client.post(
        "/api/prediction/predict",
        json={"location": "Delhi", "feature_override": {"temperature_c": 30.0, "humidity_pct": 85.0}},
    )
    assert response.status_code == 200
    assert response.json()["scenario_mode"] is True


def test_prediction_returns_synthetic_model_metadata():
    response = client.post(
        "/api/prediction/predict",
        json={"location": "Delhi"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["data_mode"] == "synthetic"
    assert body["model_version"]
    assert body["predicted_risk_label"] in {"Low", "Medium", "High", "Critical"}


def test_network_history_is_marked_synthetic():
    response = client.get("/api/stations/network/history")
    assert response.status_code == 200
    body = response.json()
    assert body["data_mode"] == "synthetic"
    assert body["station_count"] == 6
    assert len(body["series"]) == 25


def test_station_history_is_marked_synthetic():
    response = client.get("/api/stations/STN_YAM_01/history")
    assert response.status_code == 200
    body = response.json()
    assert body["data_mode"] == "synthetic"
    assert len(body["series"]) == 25


def test_agent_greeting_returns_helpful_capabilities():
    response = client.post("/api/agent/query", json={"query": "hey"})
    assert response.status_code == 200
    body = response.json()
    assert body["target_location"] is None
    assert body["tool_calls"] == []
    assert "What can you do" not in body["response"] or "FloodGuard AI Assistant" in body["response"]
    assert "synthetic flood-risk data" in body["response"]


def test_agent_help_lists_supported_tasks():
    response = client.post("/api/agent/query", json={"query": "what can you do?"})
    assert response.status_code == 200
    body = response.json()
    assert body["target_location"] is None
    assert "Which stations need immediate attention?" in body["response"]
    assert "historical" in body["response"].lower()


def test_agent_unknown_query_does_not_default_to_delhi():
    response = client.post("/api/agent/query", json={"query": "how are you today?"})
    assert response.status_code == 200
    body = response.json()
    assert body["target_location"] is None
    assert body["tool_calls"] == []
    assert "I’m a flood-risk assistant" in body["response"]


def test_agent_treats_delhi_risk_question_as_regional():
    response = client.post("/api/agent/query", json={"query": "is delhi at risk?"})
    assert response.status_code == 200
    body = response.json()
    assert body["target_location"] == "delhi"
    assert body["tool_calls"][0]["tool"] == "get_affected_regions"
    assert body["synthesis_source"] in {"gemini", "offline-deterministic", "offline-deterministic-fallback"}
    assert "Regional Flood Risk Intelligence Overview" in body["response"]


def test_telemetry_rejects_invalid_soil_moisture():
    response = client.post(
        "/api/stations/STN_YAM_01/telemetry",
        json={"soil_moisture_index": 1.5},
    )
    assert response.status_code == 422
