# authentication.py
import jwt
import os
import logging
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import datetime

# Environment Variables
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")

# In-memory user store
users = {"admin": generate_password_hash("securepassword")}


def login_user(auth_data):
    """Authenticate the user and return a JWT token if successful."""
    username = auth_data.get("username")
    password = auth_data.get("password")
    if username in users and check_password_hash(users.get(username), password):
        token = jwt.encode(
            {
                "user": username,
                "exp": datetime.datetime.now(datetime.UTC)
                + datetime.timedelta(hours=24),
            },
            SECRET_KEY,
            algorithm="HS256",
        )
        logging.info(f"User {username} logged in successfully.")
        return jsonify({"token": token})
    logging.warning(f"Failed login attempt for user {username}.")
    return jsonify({"message": "Invalid credentials!"}), 401


def token_required(f):
    """Ensure a valid JWT token is provided for protected routes."""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        logging.warning(token)
        if not token:
            logging.warning("Token is missing in request headers.")
            return jsonify({"message": "Token is missing!"}), 401
        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            logging.warning("Token has expired.")
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            logging.warning("Invalid token provided.")
            return jsonify({"message": "Invalid token!"}), 401
        return f(*args, **kwargs)

    return decorated
