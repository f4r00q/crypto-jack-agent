# prometheus.py
import prometheus_client as prom
from flask import Response

# Prometheus Metrics Exporter
ANOMALIES_DETECTED = prom.Counter(
    "anomalies_detected", "Total number of anomalies detected"
)

EVENTS_PROCESSED = prom.Counter("events_processed", "Total number of processed events")

LAST_EVENT_TIMESTAMP = prom.Gauge(
    "last_event_timestamp", "Timestamp of the last processed event"
)


def setup_metrics():
    """Generate and expose Prometheus metrics."""
    return Response(prom.generate_latest(), mimetype="text/plain")


def record_anomaly():
    """Increment anomaly detection counter."""
    ANOMALIES_DETECTED.inc()


def record_event():
    """Increment processed event counter."""
    EVENTS_PROCESSED.inc()


def update_last_event_timestamp(timestamp):
    """Update the last event timestamp gauge."""
    LAST_EVENT_TIMESTAMP.set(timestamp)
