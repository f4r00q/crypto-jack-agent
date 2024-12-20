import sqlite3
import json
import logging

# Default database file
DATABASE_FILE = "monitor_logs.db"


def init_db(database_file=DATABASE_FILE):
    """Initialize the database and create necessary tables."""
    conn = sqlite3.connect(database_file)
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                message TEXT NOT NULL,
                metadata TEXT
            )
            """
        )
    conn.close()
    logging.info(f"Database initialized: {database_file}")


def save_event(timestamp, event_type, message, metadata, database_file=DATABASE_FILE):
    """Save an event to the specified database."""
    conn = sqlite3.connect(database_file)
    with conn:
        conn.execute(
            "INSERT INTO events (timestamp, event_type, message, metadata)\
                  VALUES (?, ?, ?, ?)",
            (timestamp, event_type, message, json.dumps(metadata)),
        )
    conn.close()
    logging.info(f"Saved event: {event_type} at {timestamp} in {database_file}")


def get_events_from_db(database_file=DATABASE_FILE):
    """Retrieve all events from the specified database."""
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "timestamp": row[1],
            "event_type": row[2],
            "message": row[3],
            "metadata": json.loads(row[4]) if row[4] else None,
        }
        for row in rows
    ]
