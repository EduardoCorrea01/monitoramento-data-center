"""Independent check for missing agent readings (not an SSH monitor).

Run exactly one copy: python availability_worker.py
"""
import logging
import time

from app import app
from services.availability_service import mark_stale_servers

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("availability")


def main():
    interval = app.config["AVAILABILITY_CHECK_INTERVAL"]
    timeout = app.config["OFFLINE_AFTER_SECONDS"]
    if interval <= 0 or timeout <= 0:
        raise ValueError("AVAILABILITY_CHECK_INTERVAL and OFFLINE_AFTER_SECONDS must be > 0")
    logger.info("Checking agent activity every %ds; OFFLINE after %ds", interval, timeout)
    while True:
        started = time.monotonic()
        try:
            with app.app_context():
                count = mark_stale_servers(timeout_seconds=timeout)
            if count:
                logger.warning("Marked %d servers OFFLINE", count)
        except Exception:
            logger.exception("Availability check failed; will retry")
        time.sleep(max(0, interval - (time.monotonic() - started)))


if __name__ == "__main__":
    main()
