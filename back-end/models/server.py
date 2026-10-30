from datetime import datetime

from database.db import db


class Server(db.Model):
    __tablename__ = "servers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ip = db.Column(db.String(45), nullable=False, unique=True)
    operating_system = db.Column(
        db.String(100),
        nullable=False,
        default="Unknown",
    )
    status = db.Column(db.String(20), nullable=False, default="ONLINE")
    last_check = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
