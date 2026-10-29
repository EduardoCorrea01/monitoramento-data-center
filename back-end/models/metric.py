from datetime import datetime

from database.db import db


class Metric(db.Model):
    __tablename__ = "metrics"

    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(
        db.Integer,
        db.ForeignKey("servers.id"),
        nullable=False,
    )
    cpu_percent = db.Column(db.Numeric(5, 2), nullable=False)
    memory_percent = db.Column(db.Numeric(5, 2), nullable=False)
    disk_percent = db.Column(db.Numeric(5, 2), nullable=False)
    disk_total_gb = db.Column(db.Numeric(10, 2), nullable=True)
    disk_used_gb = db.Column(db.Numeric(10, 2), nullable=True)
    network_percent = db.Column(db.Numeric(5, 2), nullable=False, default=0)
    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
