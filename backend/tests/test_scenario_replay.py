from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_replay_returns_injected_emergency():
    response = client.post(
        "/api/scenario/replay",
        json={
            "text": "Critical flood rising fast, 120 people trapped near Rampur",
            "source": "scenario_test",
            "location_name": "Rampur",
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert "injected_report" in body
    assert "incidents" in body
    assert body["report_count"] >= 1

    injected_id = body["injected_report"]["report_id"]
    incident_ids = {item["report_id"] for item in body["incidents"]}

    assert injected_id in incident_ids

def test_replay_produces_risk_and_priority():
    response = client.post(
        "/api/scenario/replay",
        json={
            "text": "Critical flood rising fast, 120 people trapped near Rampur",
            "source": "scenario_test",
            "location_name": "Rampur",
        },
    )

    assert response.status_code == 200
    body = response.json()
    injected_id = body["injected_report"]["report_id"]

    incident = next(
        item for item in body["incidents"]
        if item["report_id"] == injected_id
    )

    assert 0 <= incident["risk_score"] <= 100
    assert incident["priority"] in {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
    assert isinstance(incident["assigned_resources"], list)
    assert isinstance(incident["explanation"], list)
