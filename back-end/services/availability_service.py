"""Detect missing HTTP heartbeats and update server availability.

Server.last_check is the UTC time when the API accepted the last valid reading.
The agent-supplied timestamp is stored in Metric but NEVER used as a heartbeat.
"""
from datetime import datetime, timedelta

from database.db import db
from models.event import Event
from models.server import Server
from services.alert_service import sync_availability_alert


def mark_stale_servers(now=None, timeout_seconds=120):
    """Mark ONLINE servers OFFLINE once when they stop sending data.

    Must run inside a Flask app context (normally from availability_worker.py).
    Returns number of newly offline servers. Does not manufacture readings.
    """
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    now = now or datetime.utcnow()
    cutoff = now - timedelta(seconds=timeout_seconds)
    try:
        stale = Server.query.filter(
            Server.status == "ONLINE",
            Server.last_check < cutoff,
        ).all()
        for server in stale:
            server.status = "OFFLINE"
            db.session.add(Event(
                server_id=server.id,
                history=f"No monitoring data received for over {timeout_seconds} seconds",
                unavailable=True,
            ))
            sync_availability_alert(server.id, offline=True)
        db.session.commit()
        return len(stale)
    except Exception:
        db.session.rollback()
        raise
