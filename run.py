import argparse
import logging
import prometheus_client as prom
from ebpf_monitor.app import create_app
from ebpf_monitor.database import init_db
from ebpf_monitor.ebpf_monitor import EBPFMonitor
from ebpf_monitor.simulation import run_adversary_actions
import threading

def setup_logging():
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[logging.StreamHandler()])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="eBPF Monitoring Application")
    parser.add_argument('--init-db', action='store_true', help="Initialize the database")
    parser.add_argument('--start', action='store_true', help="Start the application")
    parser.add_argument('--simulate', action='store_true', help="Run adversary action simulation")
    args = parser.parse_args()

    setup_logging()

    if args.init_db:
        init_db()
        logging.info("Database initialized.")

    if args.simulate:
        run_adversary_actions()
        exit(0)

    if args.start:
        prom.start_http_server(8000)
        monitor = EBPFMonitor()
        monitor_thread = threading.Thread(target=monitor.monitor, daemon=True)
        monitor_thread.start()
        logging.info("eBPF Monitoring started.")

        app = create_app()
        app.run(host="0.0.0.0", port=5000)
