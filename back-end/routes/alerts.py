"""List alerts and allow manual resolution of resource alerts."""
from flask import Blueprint, jsonify, request

from database.db import db
from models.alert import Alert
from models.server import Server

alerts_bp = Blueprint("alerts", __name__)


@alerts_bp.get("/alerts")
@alerts_bp.get("/alertas")
def list_alerts():
    status = request.args.get("status", "ACTIVE").upper()
    if status not in ("ACTIVE", "RESOLVED", "ALL"):
        return jsonify({"error": "status must be ACTIVE, RESOLVED, or ALL"}), 400
    query = Alert.query
    if status != "ALL":
        query = query.filter_by(status=status)
    alerts = query.order_by(Alert.created_at.desc(), Alert.id.desc()).all()
    return jsonify([_serialize_alert(alert) for alert in alerts]), 200


@alerts_bp.put("/alerts/<int:alert_id>/resolve")
@alerts_bp.put("/alertas/<int:alert_id>/resolver")
def resolve_alert(alert_id):
    alert = db.session.get(Alert, alert_id)
    if alert is None:
        return jsonify({"error": "Alert not found"}), 404
    if alert.alert_type == "AVAILABILITY":
        server = db.session.get(Server, alert.server_id)
        if server and server.status == "OFFLINE":
            return jsonify({"error": "Cannot resolve availability while server is OFFLINE"}), 409
    alert.status = "RESOLVED"
    db.session.commit()
    return jsonify(_serialize_alert(alert)), 200


def _serialize_alert(alert):
    return {
        "id": alert.id, "server_id": alert.server_id,
        "alert_type": alert.alert_type, "level": alert.level,
        "message": alert.message, "status": alert.status,
        "created_at": alert.created_at.isoformat(),
    }
