from flask import Flask, jsonify, request
from ebpf_monitor.database import get_events_from_db
from ebpf_monitor.authentication import token_required, login_user
from ebpf_monitor.alert import update_alert_config
from ebpf_monitor.prom import setup_metrics

# Flask Application Factory


def create_app():
    app = Flask(__name__)

    # Authentication Route
    @app.route("/login", methods=["POST"])
    def login():
        return login_user(request.json)

    # Protected Route: Retrieve Events
    @app.route("/events", methods=["GET"])
    @token_required
    def events():
        events = get_events_from_db()
        return jsonify(events)

    # Protected Route: Update Alert Config
    @app.route("/update_config", methods=["POST"])
    @token_required
    def update_config():
        config_data = request.json
        update_alert_config(config_data)  # Use the updated function
        return jsonify({"message": "Alert configuration updated successfully"})

    # Metrics Endpoint
    @app.route("/metrics")
    def metrics():
        return setup_metrics()

    return app
