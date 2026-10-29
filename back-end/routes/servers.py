"""Server list, detail, and summary for the dashboard."""
from flask import Blueprint, jsonify

from models.alert import Alert
from models.server import Server

servers_bp = Blueprint("servers", __name__)


@servers_bp.get("/servers")
@servers_bp.get("/servidores")
def list_servers():
    servers = Server.query.order_by(Server.id).all()
    return jsonify([_serialize_server(server) for server in servers]), 200


@servers_bp.get("/servers/<int:server_id>")
@servers_bp.get("/servidores/<int:server_id>")
def get_server(server_id):
    server = Server.query.filter_by(id=server_id).first()
    if server is None:
        return jsonify({"error": "Server not found"}), 404
    return jsonify(_serialize_server(server)), 200


@servers_bp.get("/summary")
@servers_bp.get("/resumo")
def summary():
    return jsonify({
        "servers_total": Server.query.count(),
        "online": Server.query.filter_by(status="ONLINE").count(),
        "offline": Server.query.filter_by(status="OFFLINE").count(),
        "active_alerts": Alert.query.filter_by(status="ACTIVE").count(),
        "critical_alerts": Alert.query.filter_by(
            status="ACTIVE", level="CRITICAL").count(),
    }), 200


def _serialize_server(server):
    return {
        "id": server.id, "name": server.name, "ip": server.ip,
        "operating_system": server.operating_system,
        "status": server.status, "last_check": server.last_check.isoformat(),
    }
