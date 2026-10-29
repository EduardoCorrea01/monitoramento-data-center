"""Group 3 end-to-end test suite on in-memory SQLite; no network needed."""
import unittest
from datetime import datetime, timedelta

from app import create_app
from database.db import db
from models.alert import Alert
from models.event import Event
from models.metric import Metric
from models.server import Server
from services.availability_service import mark_stale_servers


class TestingConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = "*"
    API_PORT = 80
    OFFLINE_AFTER_SECONDS = 120
    AVAILABILITY_CHECK_INTERVAL = 15
    DEBUG = False


class MonitoringApiTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.client = self.app.test_client()
        db.session.remove()
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def post_reading(self, ip="192.168.56.11", cpu=30, **overrides):
        body = {
            "servidor": "srv-monitor-01", "ip": ip,
            "cpu": cpu, "memoria": 50, "disco": 55,
        }
        body.update(overrides)
        return self.client.post("/monitoramento", json=body)

    def test_health_and_empty_summary(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.get("/resumo").json, {
            "servers_total": 0, "online": 0, "offline": 0,
            "active_alerts": 0, "critical_alerts": 0,
        })

    def test_post_creates_server_and_metric_in_both_languages(self):
        response = self.post_reading()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["alerts_created"], 0)
        self.assertEqual(Server.query.count(), 1)
        self.assertEqual(Metric.query.count(), 1)
        self.assertEqual(self.client.get("/servidores").json[0]["status"], "ONLINE")
        self.assertEqual(self.client.get("/servers/1").status_code, 200)
        self.assertEqual(self.client.get("/metricas?servidor_id=1").status_code, 200)
        self.assertEqual(self.client.get("/servers/999").status_code, 404)
        eng = self.client.post("/monitoring", json={
            "server": "srv-monitor-02", "ip": "192.168.56.12",
            "cpu": 20, "memory": 30, "disk": 40,
        })
        self.assertEqual(eng.status_code, 201)
        self.assertEqual(Server.query.count(), 2)
        self.assertEqual(Metric.query.count(), 2)
        self.assertEqual(self.client.get("/summary").json["online"], 2)

    def test_invalid_payload_does_not_write_to_database(self):
        bad = [
            None, [], "hello", {"cpu": 30},
            {"server": "vm", "ip": "bad", "cpu": 20, "memory": 30, "disk": 40},
            {"server": "vm", "ip": "192.168.56.11", "cpu": 150, "memory": 30, "disk": 40},
            {"server": "vm", "ip": "192.168.56.11", "cpu": True, "memory": 30, "disk": 40},
            {"server": "vm", "ip": "192.168.56.11", "cpu": 20, "memory": float("nan"), "disk": 40},
            {"server": "vm", "ip": "192.168.56.11", "cpu": 20, "memory": 30, "disk": 40, "status": "OFFLINE"},
            {"server": "vm", "ip": "192.168.56.11", "cpu": 20, "memory": 30, "disk": 40, "timestamp": "wrong"},
        ]
        for data in bad:
            with self.subTest(data=data):
                res = self.client.post("/monitoramento", json=data)
                self.assertEqual(res.status_code, 400)
        self.assertEqual(Metric.query.count(), 0)
        self.assertEqual(Server.query.count(), 0)

    def test_cpu_alert_deduplication_and_resolution(self):
        self.assertEqual(self.post_reading(cpu=90).json["alerts_created"], 1)
        self.assertEqual(self.post_reading(cpu=95).json["alerts_created"], 0)
        self.assertEqual(Alert.query.filter_by(alert_type="CPU").count(), 1)
        self.assertEqual(self.client.get("/alertas").json[0]["level"], "ALERT")
        self.assertEqual(self.post_reading(cpu=30).json["alerts_resolved"], 1)
        self.assertEqual(len(self.client.get("/alertas").json), 0)
        self.assertEqual(len(self.client.get("/alerts?status=ALL").json), 1)
        self.assertEqual(self.client.get("/alerts?status=INVALID").status_code, 400)

    def test_exact_85_percent_creates_three_metric_alerts(self):
        response = self.post_reading(cpu=85, memoria=85, disco=85)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["alerts_created"], 3)
        self.assertEqual({a.alert_type for a in Alert.query.all()},
                         {"CPU", "MEMORY", "DISK"})
        response = self.post_reading(cpu=84, memoria=84, disco=84)
        self.assertEqual(response.json["alerts_resolved"], 3)

    def test_offline_after_120_seconds_then_recovery(self):
        self.assertEqual(self.post_reading(cpu=90).status_code, 201)
        server = Server.query.filter_by(ip="192.168.56.11").one()
        server.last_check = datetime.utcnow() - timedelta(seconds=121)
        db.session.commit()
        self.assertEqual(mark_stale_servers(timeout_seconds=120), 1)
        self.assertEqual(server.status, "OFFLINE")
        self.assertEqual(Event.query.filter_by(unavailable=True).count(), 1)
        critical = Alert.query.filter_by(alert_type="AVAILABILITY").one()
        self.assertEqual(critical.level, "CRITICAL")
        self.assertEqual(critical.status, "ACTIVE")
        self.assertEqual(self.client.get("/resumo").json["critical_alerts"], 1)
        # Another worker cycle does not duplicate events or alerts.
        self.assertEqual(mark_stale_servers(timeout_seconds=120), 0)
        self.assertEqual(Alert.query.filter_by(alert_type="AVAILABILITY").count(), 1)
        self.assertEqual(Event.query.count(), 1)
        # A critical availability alert cannot be resolved manually while OFFLINE.
        conflict = self.client.put(f"/alertas/{critical.id}/resolver")
        self.assertEqual(conflict.status_code, 409)
        # An invalid request cannot mark it ONLINE again.
        self.assertEqual(self.post_reading(cpu=101).status_code, 400)
        self.assertEqual(Server.query.first().status, "OFFLINE")
        # New valid reading restores ONLINE, resolves availability; CPU still high.
        recovered = self.post_reading(cpu=90)
        self.assertEqual(recovered.status_code, 201)
        self.assertGreaterEqual(recovered.json["alerts_resolved"], 1)
        self.assertEqual(Server.query.first().status, "ONLINE")
        self.assertEqual(Alert.query.filter_by(alert_type="AVAILABILITY").one().status, "RESOLVED")
        self.assertEqual(Alert.query.filter_by(alert_type="CPU").one().status, "ACTIVE")
        self.assertEqual(Event.query.filter_by(unavailable=False).count(), 1)
        self.assertEqual(len(self.client.get("/eventos").json), 2)
        self.assertEqual(self.client.get("/resumo").json["critical_alerts"], 0)

    def test_no_offline_at_exact_threshold(self):
        self.post_reading()
        server = Server.query.first()
        point = datetime(2026, 10, 19, 19, 0, 0)
        server.last_check = point - timedelta(seconds=120)
        db.session.commit()
        self.assertEqual(mark_stale_servers(now=point, timeout_seconds=120), 0)
        self.assertEqual(server.status, "ONLINE")
        self.assertEqual(mark_stale_servers(
            now=point + timedelta(seconds=1), timeout_seconds=120), 1)

    def test_timestamp_from_agent_does_not_change_heartbeat(self):
        res = self.post_reading(data_hora="2010-01-01T00:00:00Z")
        self.assertEqual(res.status_code, 201)
        self.assertEqual(Metric.query.first().timestamp.year, 2010)
        self.assertGreater(Server.query.first().last_check.year, 2020)
        self.assertEqual(mark_stale_servers(timeout_seconds=120), 0)

    def test_filters_limits_and_manual_resolve(self):
        self.post_reading(cpu=90)
        alert = Alert.query.filter_by(alert_type="CPU").one()
        response = self.client.put(f"/alerts/{alert.id}/resolve")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "RESOLVED")
        self.assertEqual(self.client.put("/alerts/9999/resolve").status_code, 404)
        self.assertEqual(self.client.get("/metricas?limit=0").status_code, 400)
        self.assertEqual(self.client.get("/metricas?limit=xyz").status_code, 400)
        self.assertEqual(self.client.get("/eventos?limit=0").status_code, 400)
        self.assertEqual(self.client.get("/eventos?limit=xyz").status_code, 400)
        self.assertEqual(len(self.client.get("/metrics?limit=1").json), 1)
        self.assertEqual(self.client.get("/events?limit=1").status_code, 200)


if __name__ == "__main__":
    unittest.main()
