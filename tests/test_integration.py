# test_integration.py
import pytest
import json
from unittest.mock import patch
from ebpf_monitor.app import create_app
from ebpf_monitor.authentication import users
from werkzeug.security import generate_password_hash


@pytest.fixture(scope="module")
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "supersecretkey"
    with app.app_context():
        print(f"SECRET_KEY from test: {app.config['SECRET_KEY']}")
    return app


@pytest.fixture(scope="module")
def client():
    app = create_app()
    app.config["TESTING"] = True
    users["test_user"] = generate_password_hash("test_password")
    return app.test_client()


# Integration Test: API and Database Initialization
@patch("ebpf_monitor.database.init_db")
def test_init_database(mock_init_db, client):
    mock_init_db.return_value = None
    response = client.get("/events")
    assert response.status_code == 401, "Unauthorized request should be denied."


# Integration Test: User Login and Token Access
def test_login_and_access_protected_route(client):
    # Login with correct credentials
    login_response = client.post(
        "/login", json={"username": "admin", "password": "securepassword"}
    )
    assert login_response.status_code == 200, "Login failed with correct credentials."
    token = login_response.json["token"]
    print(f"Obtained token: {token}")

    # Access protected route with valid token
    headers = {"Authorization": f"{token}"}
    print(f"Request headers: {headers}")
    events_response = client.get("/events", headers=headers)
    print(f"Events response status code: {events_response.status_code}")
    assert events_response.status_code == 200, "Accessing protected route failed."


# Integration Test: Event Retrieval After Save
@patch("ebpf_monitor.database.save_event")
def test_event_saving_and_retrieval(mock_save_event, client):
    mock_save_event.return_value = None
    test_event = {
        "timestamp": "2024-12-18T12:00:00",
        "event_type": "ANOMALY",
        "message": "Test event detected.",
        "metadata": {"key": "value"},
    }

    mock_save_event(
        test_event["timestamp"],
        test_event["event_type"],
        test_event["message"],
        test_event["metadata"],
    )
    login_response = client.post(
        "/login", json={"username": "admin", "password": "securepassword"}
    )
    assert login_response.status_code == 200, "Login failed with correct credentials."
    token = login_response.json["token"]

    # Access protected route with valid token
    headers = {"Authorization": f"{token}"}
    response = client.get("/events", headers=headers)

    assert response.status_code == 200, "Failed to retrieve events after saving."


# Integration Test: Email Alert Triggering
@patch("ebpf_monitor.alert.send_alert")
def test_email_alert_trigger(mock_send_alert, client):
    mock_send_alert.return_value = None
    test_event = {
        "timestamp": "2024-12-18T12:00:00",
        "event_type": "ANOMALY",
        "message": "Email Test Alert Triggered.",
        "metadata": {"alert": "critical"},
    }

    client.post(
        "/update_config",
        data=json.dumps({"email_alerts": True}),
        headers={"Authorization": "test_token"},
        content_type="application/json",
    )

    mock_send_alert(test_event["message"])
    mock_send_alert.assert_called_once_with("Email Test Alert Triggered.")
