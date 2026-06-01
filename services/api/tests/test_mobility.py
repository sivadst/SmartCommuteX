def test_plan_commute_returns_ranked_routes(client) -> None:
    payload = {
        "origin": {"lat": 13.0827, "lng": 80.2707, "label": "Chennai Central"},
        "destination": {"lat": 13.0674, "lng": 80.2376, "label": "T Nagar"},
        "objective": "greenest",
        "allowed_modes": ["bike", "rideshare"],
    }

    response = client.post("/api/v1/mobility/plan", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["best_mode"] == "bike"
    assert data["summary"]["live_refresh_recommended"] is False
    assert len(data["routes"]) == 2
    assert "confidence_score" in data["routes"][0]["analytics"]
    assert data["routes"][0]["route_variant"] == "primary"
    assert data["routes"][0]["mobility_score"] >= data["routes"][1]["mobility_score"]


def test_dashboard_overview_uses_persisted_trip_data(client) -> None:
    payload = {
        "origin": {"lat": 13.0827, "lng": 80.2707, "label": "Chennai Central"},
        "destination": {"lat": 13.0674, "lng": 80.2376, "label": "T Nagar"},
        "objective": "balanced",
        "allowed_modes": ["bike", "rideshare"],
    }
    client.post("/api/v1/mobility/plan", json=payload)

    response = client.get("/api/v1/dashboard/overview")

    assert response.status_code == 200
    data = response.json()
    assert len(data["metrics"]) == 4
    assert len(data["recent_trips"]) == 1
    assert "command_center" in data
    assert len(data["command_center"]["city_pulse"]) >= 1
