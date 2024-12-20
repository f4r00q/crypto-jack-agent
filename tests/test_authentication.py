import pytest
import jwt
import datetime
from flask import Flask
from ebpf_monitor.authentication import login_user, token_required
from werkzeug.security import generate_password_hash

SECRET_KEY = "supersecretkey"


# Mock Flask App for Testing
@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    return app


# Mock User Data
users = {"admin": generate_password_hash("securepassword")}


def test_login_success(app):
    auth_data = {"username": "admin", "password": "securepassword"}
    with app.test_request_context():
        response = login_user(auth_data)
        assert response.status_code == 200, "Login failed with valid credentials."
        token = response.get_json("token")
        assert token is not None, "Token was not generated."


def test_login_failure(app):
    auth_data = {"username": "admin", "password": "wrongpassword"}
    with app.test_request_context():
        response, status_code = login_user(auth_data)
        print(response.get_json())
        assert status_code == 401, "Login should fail with invalid credentials."
        assert (
            "token" not in response.get_json()
        ), "Token should not be generated for invalid credentials."


def test_token_required_decorator(app):
    with app.test_request_context(headers={"Authorization": "invalid_token"}):

        @token_required
        def protected():
            return {"message": "Access Denied"}, 401

        response, status_code = protected()
        assert status_code == 401, "Access should be denied with an invalid token."

    valid_token = jwt.encode(
        {
            "user": "admin",
            "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1),
        },
        SECRET_KEY,
        algorithm="HS256",
    )

    with app.test_request_context(headers={"Authorization": valid_token}):

        @token_required
        def protected_valid():
            return {"message": "Access Granted"}, 200

        response, status_code = protected_valid()
        assert status_code == 200, "Access should be granted with a valid token."
        assert (
            response["message"] == "Access Granted"
        ), "Access should be granted with a valid token."
