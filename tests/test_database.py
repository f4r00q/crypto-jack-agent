import pytest
import sqlite3
import os
from ebpf_monitor.database import init_db, save_event, get_events_from_db

# Define a test database file path
db_file = "test_monitor_logs.db"


@pytest.fixture(scope="module")
def setup_database():
    # Setup: Initialize test database
    if os.path.exists(db_file):
        os.remove(db_file)
    conn = sqlite3.connect(db_file)
    init_db(db_file)  # Pass db_file as an argument
    yield conn
    # Teardown: Remove the test database
    conn.close()
    if os.path.exists(db_file):
        os.remove(db_file)


def test_database_initialization(setup_database):
    conn = setup_database
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='events'"
    )
    assert cursor.fetchone() is not None, "Table 'events' was not created."


def test_save_event(setup_database):
    timestamp = "2024-12-18T12:00:00"
    event_type = "ANOMALY"
    message = "Test event detected."
    metadata = {"key": "value"}

    save_event(timestamp, event_type, message, metadata, db_file)  # Use db_file

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events WHERE message = ?", (message,))
    event = cursor.fetchone()
    assert event is not None, "Event was not saved."
    assert event[1] == timestamp
    assert event[2] == event_type
    assert event[3] == message


def test_get_events_from_db(setup_database):
    events = get_events_from_db(db_file)  # Use db_file
    assert len(events) > 0, "No events found in the database."
    assert events[0]["event_type"] == "ANOMALY", "Incorrect event type retrieved."
