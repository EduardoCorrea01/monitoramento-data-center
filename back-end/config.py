"""Configuration for the central monitoring API (Grupo 3)."""
import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()


def _database_uri():
    url = os.getenv("DATABASE_URL", "").strip()
    if url:
        return url

    keys = ("DB_USER", "DB_PASSWORD", "DB_HOST", "DB_NAME")
    present = [key for key in keys if os.getenv(key)]
    if present:
        missing = [key for key in keys if not os.getenv(key)]
        if missing:
            raise ValueError("Incomplete MySQL configuration: " + ", ".join(missing))
        return (
            "mysql+pymysql://"
            + quote_plus(os.environ["DB_USER"])
            + ":" + quote_plus(os.environ["DB_PASSWORD"])
            + "@" + os.environ["DB_HOST"]
            + ":" + os.getenv("DB_PORT", "3306")
            + "/" + os.environ["DB_NAME"]
        )

    # SQLite is for explicitly unconfigured/local development.
    return "sqlite:///monitoring.db"


class Config:
    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
    API_PORT = int(os.getenv("API_PORT", "80"))  # Central HTTP port; SSH is 22.
    OFFLINE_AFTER_SECONDS = int(os.getenv("OFFLINE_AFTER_SECONDS", "120"))
    AVAILABILITY_CHECK_INTERVAL = int(os.getenv("AVAILABILITY_CHECK_INTERVAL", "15"))
    DEBUG = os.getenv("FLASK_DEBUG", "0").lower() in ("1", "true", "yes")
