from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    assert client.get("/api/health").json()["status"] == "ok"

def test_summary_shape():
    response = client.get("/api/summary")
    assert response.status_code == 200
    body = response.json()
    assert "report_count" in body
    assert "critical_count" in body

def test_replay():
    response = client.post("/api/scenario/replay", json={
        "text": "Flood rising fast, 12 people trapped near Rampur",
        "source": "test", "location_name": "Rampur"
    })
    assert response.status_code == 200
    assert response.json()["report_count"] >= 1
