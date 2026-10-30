import pytest
from fastapi.testclient import TestClient

from organizer.api import create_app
from organizer.lock import OrganizerLock
from organizer.service import OrganizerService

TOKEN = "test-token"
AUTH = {"Authorization": f"Bearer {TOKEN}"}


@pytest.fixture
def service(tmp_path):
    service = OrganizerService(tmp_path / "settings.yaml", tmp_path / "organizer.lock")
    yield service
    service.stop()


@pytest.fixture
def folders(tmp_path):
    watch = tmp_path / "downloads"
    watch.mkdir()
    return {"watch_folder": str(watch), "destination_root": str(tmp_path / "organized")}


def make_client(service, on_shutdown=None):
    return TestClient(create_app(TOKEN, service, on_shutdown=on_shutdown))


def test_status_reports_stopped_before_start(service):
    response = make_client(service).get("/status", headers=AUTH)

    assert response.status_code == 200
    assert response.json() == {"state": "stopped", "message": None}


def test_request_without_token_is_rejected(service):
    response = make_client(service).get("/status")

    assert response.status_code == 401
    assert response.json() == {
        "error": {"code": "unauthorized", "message": "Missing or invalid token."}
    }


def test_request_with_wrong_token_is_rejected(service):
    response = make_client(service).get("/status", headers={"Authorization": "Bearer nope"})

    assert response.status_code == 401
    assert response.json() == {
        "error": {"code": "unauthorized", "message": "Missing or invalid token."}
    }


def test_every_endpoint_requires_the_token(service):
    client = make_client(service)

    for method, path in [
        ("post", "/start"),
        ("post", "/stop"),
        ("get", "/settings"),
        ("put", "/settings"),
        ("get", "/activity"),
        ("post", "/shutdown"),
    ]:
        response = getattr(client, method)(path)
        assert response.status_code == 401, path


def test_cors_preflight_from_app_window_is_allowed(service):
    response = make_client(service).options(
        "/status",
        headers={
            "Origin": "http://localhost:1420",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:1420"


def test_cors_preflight_from_other_website_is_refused(service):
    response = make_client(service).options(
        "/status",
        headers={
            "Origin": "https://evil.example",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


def test_start_without_settings_returns_invalid_settings(service):
    response = make_client(service).post("/start", headers=AUTH)

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "invalid_settings",
            "message": "watch_folder must be a folder path",
        }
    }


def test_put_and_get_settings(service, folders):
    client = make_client(service)

    response = client.put("/settings", headers=AUTH, json=folders)
    assert response.status_code == 200
    saved = response.json()
    assert saved["watch_folder"] == folders["watch_folder"]
    assert saved["destination_root"] == folders["destination_root"]
    assert "Images" in saved["categories"]

    assert client.get("/settings", headers=AUTH).json() == saved


def test_put_invalid_settings_returns_400(service, tmp_path):
    response = make_client(service).put(
        "/settings",
        headers=AUTH,
        json={
            "watch_folder": str(tmp_path / "missing"),
            "destination_root": str(tmp_path / "out"),
        },
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_settings"
    assert "not an existing folder" in response.json()["error"]["message"]


def test_put_settings_with_missing_field_returns_400(service):
    response = make_client(service).put(
        "/settings", headers=AUTH, json={"watch_folder": "/tmp"}
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_request"


def test_start_and_stop_report_real_state(service, folders):
    client = make_client(service)
    client.put("/settings", headers=AUTH, json=folders)

    response = client.post("/start", headers=AUTH)
    assert response.status_code == 200
    assert response.json() == {"state": "running", "message": None}
    assert client.get("/status", headers=AUTH).json()["state"] == "running"

    # Starting again succeeds and changes nothing.
    assert client.post("/start", headers=AUTH).json()["state"] == "running"

    response = client.post("/stop", headers=AUTH)
    assert response.status_code == 200
    assert response.json() == {"state": "stopped", "message": None}
    assert client.post("/stop", headers=AUTH).json()["state"] == "stopped"


def test_put_settings_while_running_returns_409(service, folders):
    client = make_client(service)
    client.put("/settings", headers=AUTH, json=folders)
    client.post("/start", headers=AUTH)

    response = client.put("/settings", headers=AUTH, json=folders)

    assert response.status_code == 409
    assert response.json() == {
        "error": {
            "code": "organizer_running",
            "message": "Stop the organizer before changing settings.",
        }
    }


def test_start_while_another_organizer_runs_returns_409(service, folders, tmp_path):
    client = make_client(service)
    client.put("/settings", headers=AUTH, json=folders)

    other = OrganizerLock(tmp_path / "organizer.lock")
    other.acquire()
    try:
        response = client.post("/start", headers=AUTH)
    finally:
        other.release()

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "already_running"
    assert "Another file organizer is already running" in response.json()["error"]["message"]
    assert client.get("/status", headers=AUTH).json()["state"] == "stopped"


def test_activity_lists_recorded_events(service):
    service.activity.record_move("/in/a.jpg", "/out/Images/A.jpg")
    service.activity.record_error("/in/b.pdf", "Could not move file: denied")

    response = make_client(service).get("/activity", headers=AUTH)

    assert response.status_code == 200
    events = response.json()
    assert [event["type"] for event in events] == ["error", "moved"]
    assert events[1]["destination"] == "/out/Images/A.jpg"


def test_shutdown_stops_watcher_then_calls_shutdown_hook(service, folders):
    calls = []
    client = make_client(service, on_shutdown=lambda: calls.append("shutdown"))
    client.put("/settings", headers=AUTH, json=folders)
    client.post("/start", headers=AUTH)

    response = client.post("/shutdown", headers=AUTH)

    assert response.status_code == 200
    assert response.json() == {"state": "stopped", "message": None}
    assert service.status()["state"] == "stopped"
    assert calls == ["shutdown"]
