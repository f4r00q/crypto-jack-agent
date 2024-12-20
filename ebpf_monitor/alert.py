import logging
import os
from urllib.parse import urljoin

import requests

# Environment Variables
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# Alert Configuration
ALERT_METHODS = {
    "slack": {"enabled": True, "webhook_url": SLACK_WEBHOOK_URL},
    "log": {"enabled": True, "level": "INFO"},  # Always log alerts
}


def send_slack_alert(message):
    """
    Send an alert message to a Slack channel using a webhook.
    """
    if not ALERT_METHODS["slack"]["enabled"]:
        logging.warning("Slack alerts are disabled.")
        return

    if not ALERT_METHODS["slack"]["webhook_url"]:
        logging.warning("Slack webhook URL is not configured, skipping Slack alert.")
        return

    payload = {"text": message}
    url = urljoin(ALERT_METHODS["slack"]["webhook_url"], "/services/")
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        logging.info(f"Sent Slack alert: {message}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send Slack alert: {e}")


def send_alert(message):
    """
    Send an alert message to configured destinations (Slack and logs).
    """
    logging.info(f"Alert message: {message}")

    if ALERT_METHODS["slack"]["enabled"]:
        send_slack_alert(message)

    logging.info(message)  # Log the message


def update_alert_config(config_data):
    """
    Update alert configuration based on incoming config data.
    """
    global ALERT_METHODS

    for method, settings in config_data.items():
        if method in ALERT_METHODS:
            ALERT_METHODS[method].update(settings)
            logging.info(f"Updated alert method configuration for '{method}'.")
        else:
            logging.warning(f"Ignoring unknown alert method '{method}'.")

    if "log_level" in config_data:
        logging.getLogger().setLevel(config_data["log_level"])
        logging.info(f"Log level updated to '{config_data['log_level']}'.")
