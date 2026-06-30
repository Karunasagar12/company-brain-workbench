from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_demo_flow_priya_creates_rule_and_omar_auto_resolves():
    reset = client.post("/api/demo/reset")
    assert reset.status_code == 200
    assert reset.json()["rules"] == []

    priya = client.post(
        "/api/workflows/intake",
        json={"text": "Priya Sharma joins as a Sales Engineer in Dubai."},
    )
    assert priya.status_code == 200
    priya_body = priya.json()
    assert priya_body["status"] == "needs_human"
    assert priya_body["approval"]["id"]
    assert priya_body["approval"]["options"][0]["label"] == "Sales"

    resolved = client.post(
        f"/api/approvals/{priya_body['approval']['id']}/resolve",
        json={"decision": "Sales", "rationale": "At this company, Sales Engineer belongs to Sales."},
    )
    assert resolved.status_code == 200
    resolved_body = resolved.json()
    assert resolved_body["rule_created"] is True
    assert resolved_body["rule"]["decision"]["department"] == "Sales"

    omar = client.post(
        "/api/workflows/intake",
        json={"text": "Omar Reyes joins as a Sales Engineer in Dubai."},
    )
    assert omar.status_code == 200
    omar_body = omar.json()
    assert omar_body["status"] == "auto_resolved"
    assert omar_body["matched_rule"]["decision"]["department"] == "Sales"


def test_invalid_long_input_is_rejected():
    response = client.post("/api/workflows/intake", json={"text": "x" * 2001})
    assert response.status_code == 422
