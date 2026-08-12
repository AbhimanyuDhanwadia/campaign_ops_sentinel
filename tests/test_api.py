from fastapi.testclient import TestClient

from campaign_ops_sentinel.main import app

client = TestClient(app)

PAYLOAD = {
    "brand": "Pulse Energy",
    "budget_inr": 500000,
    "markets": ["IN"],
    "audience": "Mobile gamers aged 18 to 30",
    "objective": "attention",
    "start_date": "2026-09-01",
    "end_date": "2026-09-14",
    "formats": ["video", "playable"],
    "destination_url": "https://example.com/campaign",
}


def test_health_reports_shadow_mode():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["shadow_mode"] is True


def test_creates_shadow_mode_recommendation():
    response = client.post("/v1/campaigns/recommendations", json=PAYLOAD)
    assert response.status_code == 200
    body = response.json()
    assert body["proposed_action"] == "shadow_created"
    assert body["approval_required"] is True
    assert body["inventory"][0]["placement_id"] == "inv_001"


def test_rejects_inverted_dates():
    invalid = {**PAYLOAD, "start_date": "2026-09-15", "end_date": "2026-09-14"}
    assert client.post("/v1/campaigns/recommendations", json=invalid).status_code == 422


def test_blocks_insecure_destination_url():
    insecure = {**PAYLOAD, "destination_url": "http://example.com"}
    body = client.post("/v1/campaigns/recommendations", json=insecure).json()
    assert body["proposed_action"] == "blocked"
