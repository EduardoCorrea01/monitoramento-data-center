from datetime import datetime

from database.db import db


class Service(db.Model):
    __tablename__ = "services"

    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(
        db.Integer,
        db.ForeignKey("servers.id"),
        nullable=False,
    )
    service_name = db.Column(db.String(100), nullable=False)
    service_type = db.Column(db.String(50), nullable=False)
    endpoint_port = db.Column(db.String(50))
    status = db.Column(db.String(20), nullable=False, default="ACTIVE")
    response_time = db.Column(db.Integer)
    last_check = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
