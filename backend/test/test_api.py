from fastapi.testclient import TestClient

def test_status_reports_stopped_before_start():
    client = TestClient(create_app())

    response = client.get("/status")

    assert response.status_code == 200
    assert response.json() == {"state": "stopped", "message": None}
    
from organizer.api import create_app
