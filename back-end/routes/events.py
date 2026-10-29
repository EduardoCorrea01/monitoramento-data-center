"""Event history for the dashboard (downtime and recovery)."""
from flask import Blueprint, jsonify, request

from models.event import Event


events_bp = Blueprint("events", __name__)


@events_bp.get("/events")
@events_bp.get("/eventos")
def list_events():
    server_id = request.args.get("server_id", type=int)
    if server_id is None:
        server_id = request.args.get("servidor_id", type=int)
    try:
        limit = int(request.args.get("limit", "100"))
    except (ValueError, TypeError):
        return jsonify({"error": "limit must be between 1 and 1000"}), 400
    if not 1 <= limit <= 1000:
        return jsonify({"error": "limit must be between 1 and 1000"}), 400
    query = Event.query
    if server_id is not None:
        query = query.filter_by(server_id=server_id)
    events = query.order_by(Event.timestamp.desc(), Event.id.desc()).limit(limit).all()
    return jsonify([{
        "id": event.id, "server_id": event.server_id,
        "history": event.history, "unavailable": event.unavailable,
        "timestamp": event.timestamp.isoformat(),
    } for event in events]), 200
