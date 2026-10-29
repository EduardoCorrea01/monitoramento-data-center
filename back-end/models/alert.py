from datetime import datetime

from database.db import db


class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(
        db.Integer,
        db.ForeignKey("servers.id"),
        nullable=False,
    )
    alert_type = db.Column(db.String(20), nullable=False)
    level = db.Column(db.String(20), nullable=False)
    message = db.Column(db.String(255))
    status = db.Column(db.String(20), nullable=False, default="ACTIVE")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
