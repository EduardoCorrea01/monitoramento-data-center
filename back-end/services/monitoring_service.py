"""Validation and persistence shared by the API and optional SSH collector."""
from datetime import datetime, timezone
from ipaddress import ip_address
from math import isfinite

from database.db import db
from models.event import Event
from models.metric import Metric
from models.server import Server
from services.alert_service import sync_availability_alert, sync_metric_alerts


def _value(data, *keys, default=None):
    for key in keys:
        if key in data and data[key] is not None:
            return data[key]
    return default


def _percent(value, name):
    if isinstance(value, bool):
        raise ValueError(f"Invalid {name} value")
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"Invalid or missing {name}") from exc
    if not isfinite(number) or not 0 <= number <= 100:
        raise ValueError(f"{name} must be a finite number between 0 and 100")
    return round(number, 2)


def _gigabytes(value, name):
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError(f"Invalid {name} value")
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"Invalid {name} value") from exc
    if not isfinite(number) or number < 0:
        raise ValueError(f"{name} must be a finite number greater than or equal to 0")
    return round(number, 2)


def _metric_timestamp(data):
    supplied = _value(data, "timestamp", "data_hora")
    if supplied is None or supplied == "":
        return datetime.utcnow()
    try:
        parsed = datetime.fromisoformat(str(supplied).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("timestamp/data_hora must use ISO 8601") from exc
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed


def process_monitoring(data):
    """Process one valid agent reading as an atomic database transaction.

    Call inside Flask application context. Receiving data implies the agent is
    reachable; only the availability worker may declare absence as OFFLINE.
    """
    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object")
    name = _value(data, "server", "servidor")
    ip = data.get("ip")
    if not isinstance(name, str) or not name.strip() or not isinstance(ip, str):
        raise ValueError("Required fields: server/servidor and ip")
    try:
        ip_address(ip)
    except ValueError as exc:
        raise ValueError("Invalid IP address") from exc

    cpu = _percent(data.get("cpu"), "cpu")
    memory = _percent(_value(data, "memory", "memoria"), "memory")
    disk = _percent(_value(data, "disk", "disco"), "disk")
    disk_total_gb = _gigabytes(data.get("disk_total_gb"), "disk_total_gb")
    disk_used_gb = _gigabytes(data.get("disk_used_gb"), "disk_used_gb")
    # Network percentage is optional because the supplied agent doesn't send it.
    network = _percent(_value(data, "network", "rede", default=0), "network")
    measured_at = _metric_timestamp(data)
    if str(data.get("status", "ONLINE")).upper() != "ONLINE":
        raise ValueError("Readings must be ONLINE; the API detects OFFLINE automatically")
    os_name = str(_value(data, "operating_system", "sistema_operacional", default="Unknown"))
    received_at = datetime.utcnow()
    try:
        server = Server.query.filter_by(ip=ip).first()
        if server is None:
            server = Server(name=name.strip(), ip=ip,
                            operating_system=os_name, status="ONLINE",
                            last_check=received_at)
            db.session.add(server)
            db.session.flush()
        else:
            was_offline = server.status == "OFFLINE"
            server.name = name.strip()
            if os_name != "Unknown":
                server.operating_system = os_name
            server.status = "ONLINE"
            server.last_check = received_at
            if was_offline:
                db.session.add(Event(
                    server_id=server.id, history="Monitoring data resumed; server ONLINE",
                    unavailable=False,
                ))
        db.session.add(Metric(
            server_id=server.id, cpu_percent=cpu,
            memory_percent=memory, disk_percent=disk,
            disk_total_gb=disk_total_gb, disk_used_gb=disk_used_gb,
            network_percent=network, timestamp=measured_at,
        ))
        created, resolved = sync_metric_alerts(server.id, {
            "cpu": cpu, "memory": memory, "disk": disk,
        })
        _, availability_resolved = sync_availability_alert(server.id, offline=False)
        db.session.commit()
        return {
            "message": "Data received successfully", "status": "ok",
            "server_id": server.id, "alerts_created": created,
            "alerts_resolved": resolved + availability_resolved,
        }
    except Exception:
        db.session.rollback()
        raise
