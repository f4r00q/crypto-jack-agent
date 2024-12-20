from unittest.mock import patch, MagicMock
import pytest
from requests.exceptions import RequestException

from ebpf_monitor.alert import (
    send_slack_alert,
    send_alert,
    update_alert_config,
    ALERT_METHODS,
)


@pytest.fixture
def reset_alert_methods():
    # Store the original state
    original_methods = {
        "slack": ALERT_METHODS["slack"].copy(),
        "log": ALERT_METHODS["log"].copy(),
    }
    yield
    # Reset to original state after each test
    ALERT_METHODS["slack"] = original_methods["slack"]
    ALERT_METHODS["log"] = original_methods["log"]


@patch("ebpf_monitor.alert.requests.post")
@patch("ebpf_monitor.alert.logging")
def test_send_slack_alert_success(mock_logging, mock_post, reset_alert_methods):
    # Given
    ALERT_METHODS["slack"]["enabled"] = True
    ALERT_METHODS["slack"]["webhook_url"] = "https://hooks.slack.com/"

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    # When
    send_slack_alert("Test message")

    # Then
    mock_post.assert_called_once_with(
        "https://hooks.slack.com/services/", json={"text": "Test message"}
    )
    mock_logging.info.assert_any_call("Sent Slack alert: Test message")


@patch("ebpf_monitor.alert.requests.post")
@patch("ebpf_monitor.alert.logging")
def test_send_slack_alert_disabled(mock_logging, mock_post, reset_alert_methods):
    # Given
    ALERT_METHODS["slack"]["enabled"] = False
    ALERT_METHODS["slack"]["webhook_url"] = "https://hooks.slack.com/"

    # When
    send_slack_alert("Test message")

    # Then
    mock_post.assert_not_called()
    mock_logging.warning.assert_called_once_with("Slack alerts are disabled.")


@patch("ebpf_monitor.alert.requests.post")
@patch("ebpf_monitor.alert.logging")
def test_send_slack_alert_no_webhook(mock_logging, mock_post, reset_alert_methods):
    # Given
    ALERT_METHODS["slack"]["enabled"] = True
    ALERT_METHODS["slack"]["webhook_url"] = None

    # When
    send_slack_alert("Test message")

    # Then
    mock_post.assert_not_called()
    mock_logging.warning.assert_called_once_with(
        "Slack webhook URL is not configured, skipping Slack alert."
    )


@patch("ebpf_monitor.alert.requests.post")
@patch("ebpf_monitor.alert.logging")
def test_send_slack_alert_request_error(mock_logging, mock_post, reset_alert_methods):
    # Given
    ALERT_METHODS["slack"]["enabled"] = True
    ALERT_METHODS["slack"]["webhook_url"] = "https://hooks.slack.com/"

    mock_post.side_effect = RequestException("Network error")

    # When
    send_slack_alert("Test message")

    # Then
    mock_post.assert_called_once()
    mock_logging.error.assert_called_once()
    assert (
        "Failed to send Slack alert: Network error"
        in mock_logging.error.call_args[0][0]
    )


@patch("ebpf_monitor.alert.send_slack_alert")
@patch("ebpf_monitor.alert.logging")
def test_send_alert_with_slack_enabled(
    mock_logging, mock_send_slack_alert, reset_alert_methods
):
    # Given
    ALERT_METHODS["slack"]["enabled"] = True
    ALERT_METHODS["slack"]["webhook_url"] = "https://hooks.slack.com/"

    # When
    send_alert("Alert message")

    # Then
    mock_send_slack_alert.assert_called_once_with("Alert message")
    mock_logging.info.assert_any_call("Alert message")


@patch("ebpf_monitor.alert.send_slack_alert")
@patch("ebpf_monitor.alert.logging")
def test_send_alert_with_slack_disabled(
    mock_logging, mock_send_slack_alert, reset_alert_methods
):
    # Given
    ALERT_METHODS["slack"]["enabled"] = False

    # When
    send_alert("Alert message")

    # Then
    mock_send_slack_alert.assert_not_called()
    mock_logging.info.assert_any_call("Alert message")


@patch("ebpf_monitor.alert.logging")
def test_update_alert_config_known_method(mock_logging, reset_alert_methods):
    # Given
    config_data = {"slack": {"enabled": False}, "log": {"level": "ERROR"}}

    # When
    update_alert_config(config_data)

    # Then
    assert ALERT_METHODS["slack"]["enabled"] is False
    assert ALERT_METHODS["log"]["level"] == "ERROR"
    mock_logging.info.assert_any_call("Updated alert method configuration for 'slack'.")
    mock_logging.info.assert_any_call("Updated alert method configuration for 'log'.")


@patch("ebpf_monitor.alert.logging")
def test_update_alert_config_unknown_method(mock_logging, reset_alert_methods):
    # Given
    config_data = {"unknown_method": {"enabled": True}}

    # When
    update_alert_config(config_data)

    # Then
    # Unchanged because unknown method shouldn't be applied
    assert "unknown_method" not in ALERT_METHODS
    mock_logging.warning.assert_called_once_with(
        "Ignoring unknown alert method 'unknown_method'."
    )
