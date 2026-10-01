from fastapi.testclient import TestClient

from organizer.api import create_app

TOKEN = "test-token"
AUTH = {"Authorization": f"Bearer {TOKEN}"}


def make_client():
    return TestClient(create_app(TOKEN))


def test_status_reports_stopped_before_start():
    response = make_client().get("/status", headers=AUTH)

    assert response.status_code == 200
    assert response.json() == {"state": "stopped", "message": None}


def test_request_without_token_is_rejected():
    response = make_client().get("/status")

    assert response.status_code == 401
    assert response.json() == {
        "error": {"code": "unauthorized", "message": "Missing or invalid token."}
    }
def test_request_with_wrong_token_is_rejected():
    response = make_client().get("/status", headers={"Authorization": "Bearer nope"})

    assert response.status_code == 401
    assert response.json() == {
        "error": {"code": "unauthorized", "message": "Missing or invalid token."}
    }
