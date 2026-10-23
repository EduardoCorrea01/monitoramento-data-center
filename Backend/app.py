"""Central monitoring REST API - Group 3."""
from flask import Flask
from flask_cors import CORS

from config import Config
from database.db import db
from routes.alerts import alerts_bp
from routes.events import events_bp
from routes.monitoring import monitoring_bp
from routes.servers import servers_bp


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)
    db.init_app(app)
    CORS(app, origins=app.config["CORS_ORIGINS"])

    for blueprint in (monitoring_bp, alerts_bp, servers_bp, events_bp):
        app.register_blueprint(blueprint)

    @app.get("/")
    def home():
        return {"status": "online", "system": "MONITORING", "version": "2.0"}

    import models  # noqa: F401 - register all ORM models for create_all

    with app.app_context():
        db.create_all()  # Creates missing tables; DOES NOT migrate existing tables.
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=app.config["API_PORT"], debug=app.config["DEBUG"])
