# ebpf_monitor.py
import bcc
import logging
import sqlite3
import numpy as np
from datetime import datetime
from sklearn.ensemble import IsolationForest
from ebpf_monitor.database import save_event
from ebpf_monitor.alert import send_email_alert
from ebpf_monitor.prom import ANOMALIES_DETECTED
from ebpf_monitor.config import ALERT_CONFIG
from ebpf_monitor.enricher import EventEnricher
from kubernetes import client, config


class EBPFMonitor:
    def __init__(self):
        self.bpf_program = """
        # eBPF C program
        # Traces system calls and processes related to attack indicators
        #include <uapi/linux/ptrace.h>
        #include <linux/sched.h>
        BPF_HASH(exec_count, u32);

        int on_exec(struct pt_regs *ctx) {
            u32 pid = bpf_get_current_pid_tgid();
            char comm[TASK_COMM_LEN];
            bpf_get_current_comm(&comm, sizeof(comm));
            if (comm[0] == 'c' && comm[1] == 'u' && comm[2] == 'r' && comm[3] == 'l') {
                bpf_trace_printk("Detected curl execution by PID %d\n", pid);
                exec_count.increment(pid);
            }
            if (comm[0] == 'w' && comm[1] == 'g' && comm[2] == 'e' && comm[3] == 't') {
                bpf_trace_printk("Detected wget execution by PID %d\n", pid);
                exec_count.increment(pid);
            }
            if (comm[0] == 's' && comm[1] == 's' && comm[2] == 'h') {
                bpf_trace_printk("Detected SSH usage by PID %d\n", pid);
                exec_count.increment(pid);
            }
            if (comm[0] == 'd' && comm[1] == 'o' && comm[2] == 'c' && comm[3] == 'k') {
                bpf_trace_printk("Detected Docker command execution by PID %d\n", pid);
                exec_count.increment(pid);
            }
            return 0;
        }
        """
        self.b = bcc.BPF(text=self.bpf_program)
        self.db_conn = sqlite3.connect("monitor_logs.db")
        self.create_database()
        config.load_kube_config()
        self.k8s_client = client.CoreV1Api()
        self.enricher = EventEnricher(self.k8s_client)
        self.ml_model = IsolationForest(contamination=0.05)
        self.ml_model.fit(np.random.rand(1000, 3))

    def create_database(self):
        with self.db_conn:
            self.db_conn.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    event_type TEXT,
                    message TEXT,
                    metadata TEXT
                )
            """
            )

    def monitor(self):
        try:
            logging.info("Starting eBPF monitoring...")
            while True:
                (task, pid, cpu, flags, ts, msg) = self.b.trace_fields()
                metadata = self.enricher.enrich_event(pid)
                timestamp = datetime.now().isoformat()
                logging.info(f"{timestamp}: {msg} Metadata: {metadata}")
                features = np.array([[pid, cpu, flags]])
                anomaly_score = self.ml_model.predict(features)[0]
                if anomaly_score == -1:
                    logging.warning("Anomaly detected!")
                    save_event(timestamp, "ANOMALY", msg, metadata)
                    ANOMALIES_DETECTED.inc()
                    if ALERT_CONFIG["email_alerts"]:
                        send_email_alert(msg)
        except KeyboardInterrupt:
            logging.info("Terminating monitoring...")
