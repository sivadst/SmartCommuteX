from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_recommendations_rank_options() -> None:
    payload = {
        "origin": {"lat": 13.0827, "lng": 80.2707},
        "destination": {"lat": 13.0674, "lng": 80.2376},
        "priority": "carbon",
        "allowed_modes": ["transit", "bike", "ev"],
    }

    response = client.post("/api/v1/mobility/recommendations", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["recommended_mode"] == "bike"
    assert len(data["options"]) == 3
    assert data["options"][0]["mobility_score"] >= data["options"][1]["mobility_score"]
