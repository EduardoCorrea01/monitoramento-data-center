"""HTTP intake from Group 2 agents and metric history for Group 4."""
from flask import Blueprint, jsonify, request

from models.metric import Metric
from services.monitoring_service import process_monitoring

monitoring_bp = Blueprint("monitoring", __name__)


@monitoring_bp.post("/monitoring")
@monitoring_bp.post("/monitoramento")
def receive_monitoring_data():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid or missing JSON object"}), 400
    try:
        return jsonify(process_monitoring(data)), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@monitoring_bp.get("/metrics")
@monitoring_bp.get("/metricas")
def list_metrics():
    server_id = request.args.get("server_id", type=int)
    if server_id is None:
        server_id = request.args.get("servidor_id", type=int)
    try:
        limit = int(request.args.get("limit", "100"))
    except (ValueError, TypeError):
        return jsonify({"error": "limit must be between 1 and 1000"}), 400
    if not 1 <= limit <= 1000:
        return jsonify({"error": "limit must be between 1 and 1000"}), 400
    query = Metric.query
    if server_id is not None:
        query = query.filter_by(server_id=server_id)
    metrics = query.order_by(Metric.timestamp.desc(), Metric.id.desc()).limit(limit).all()
    return jsonify([{
        "id": metric.id, "server_id": metric.server_id,
        "cpu_percent": float(metric.cpu_percent),
        "memory_percent": float(metric.memory_percent),
        "disk_percent": float(metric.disk_percent),
        "disk_total_gb": (float(metric.disk_total_gb)
                           if metric.disk_total_gb is not None else None),
        "disk_used_gb": (float(metric.disk_used_gb)
                          if metric.disk_used_gb is not None else None),
        "network_percent": float(metric.network_percent),
        "timestamp": metric.timestamp.isoformat(),
    } for metric in metrics]), 200
