"""Focused API contract tests for the Phase 1 local foundation."""

from fastapi.testclient import TestClient

try:
    from backend.app.main import app
except ModuleNotFoundError:
    from app.main import app


client = TestClient(app)


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


def test_prediction_rejects_unknown_feature_override():
    response = client.post(
        "/api/prediction/predict",
        json={"feature_override": {"not_a_feature": 1}},
    )
    assert response.status_code == 422


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


def test_telemetry_rejects_invalid_soil_moisture():
    response = client.post(
        "/api/stations/STN_YAM_01/telemetry",
        json={"soil_moisture_index": 1.5},
    )
    assert response.status_code == 422
