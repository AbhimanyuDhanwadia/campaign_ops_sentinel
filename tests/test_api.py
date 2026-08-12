from fastapi.testclient import TestClient

from campaign_ops_sentinel.main import app

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


def test_health_and_readiness_report_service_state():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["shadow_mode"] is True
        assert client.get("/ready").json() == {"status": "ready"}


def test_creates_shadow_mode_recommendation():
    with TestClient(app) as client:
        response = client.post(
            "/v1/campaigns/recommendations", json=PAYLOAD, headers={"X-Request-ID": "test-001"}
        )
        assert response.status_code == 200
        body = response.json()
        assert body["proposed_action"] == "shadow_created"
        assert body["approval_required"] is True
        assert body["inventory"][0]["placement_id"] == "inv_001"
        assert response.headers["X-Request-ID"] == "test-001"

        recommendation_id = body["id"]
        assert client.get(f"/v1/campaigns/recommendations/{recommendation_id}").json()["id"] == recommendation_id
        audit = client.get(f"/v1/campaigns/recommendations/{recommendation_id}/audit").json()
        assert audit[0]["event_type"] == "recommendation.created"


def test_rejects_inverted_dates():
    invalid = {**PAYLOAD, "start_date": "2026-09-15", "end_date": "2026-09-14"}
    with TestClient(app) as client:
        assert client.post("/v1/campaigns/recommendations", json=invalid).status_code == 422


def test_blocks_insecure_destination_url():
    insecure = {**PAYLOAD, "destination_url": "http://example.com"}
    with TestClient(app) as client:
        body = client.post("/v1/campaigns/recommendations", json=insecure).json()
        assert body["proposed_action"] == "blocked"


def test_records_human_approval_without_live_mutation():
    with TestClient(app) as client:
        created = client.post("/v1/campaigns/recommendations", json=PAYLOAD).json()
        response = client.post(
            f"/v1/campaigns/recommendations/{created['id']}/approval",
            json={"decision": "approve", "reviewer": "qa-reviewer", "note": "Safe to proceed after integration."},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "recorded_in_shadow_mode"
