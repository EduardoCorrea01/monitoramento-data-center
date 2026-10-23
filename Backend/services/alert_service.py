"""Resource threshold alerts and server availability alerts."""
from database.db import db
from models.alert import Alert

ALERT_THRESHOLD = 85
METRIC_ALERTS = {
    "cpu": ("CPU", "CPU"),
    "memory": ("MEMORY", "Memory"),
    "disk": ("DISK", "Disk"),
}


def sync_metric_alerts(server_id, data):
    """Create each active threshold alert only once and resolve on recovery."""
    created = resolved = 0
    for key, (alert_type, label) in METRIC_ALERTS.items():
        value = data.get(key)
        if value is None:
            continue
        active_alerts = Alert.query.filter_by(
            server_id=server_id, alert_type=alert_type, status="ACTIVE",
        ).all()
        if value >= ALERT_THRESHOLD:
            if not active_alerts:
                db.session.add(Alert(
                    server_id=server_id, alert_type=alert_type,
                    level="ALERT",
                    message=f"{label} reached the {ALERT_THRESHOLD}% threshold",
                    status="ACTIVE",
                ))
                created += 1
        else:
            for alert in active_alerts:
                alert.status = "RESOLVED"
                resolved += 1
    return created, resolved


def sync_availability_alert(server_id, offline):
    """Create one critical availability alert or resolve active ones."""
    active = Alert.query.filter_by(
        server_id=server_id, alert_type="AVAILABILITY", status="ACTIVE",
    ).all()
    if offline:
        if not active:
            db.session.add(Alert(
                server_id=server_id, alert_type="AVAILABILITY",
                level="CRITICAL", status="ACTIVE",
                message="Monitoring agent stopped sending data",
            ))
            return 1, 0
        return 0, 0

    for alert in active:
        alert.status = "RESOLVED"
    return 0, len(active)
