"""Optional SSH collector, not part of the guide's primary HTTP-agent flow.

Do NOT run this together with Group 2 HTTP agents for the same VMs: duplicate
samples and conflicting heartbeat sources would undermine availability checks.
"""
import logging
import os
import time
from ipaddress import ip_address

from dotenv import load_dotenv

from app import app
from database.db import db
from models.event import Event
from models.server import Server
from services.monitoring_service import process_monitoring
from services.ssh_service import collect_vm

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("ssh-collector")


def load_vms():
    vms = []
    for number in range(1, 4):  # 3 monitored VMs; .20 is central, not a target.
        ip = os.getenv(f"VM{number}_IP", "").strip()
        if not ip:
            raise ValueError(f"VM{number}_IP not configured")
        ip_address(ip)
        vms.append({
            "ip": ip, "name": os.getenv(f"VM{number}_NAME", f"VM{number}"),
            "port": int(os.getenv(f"VM{number}_PORT", "22")),
            "user": os.getenv(f"VM{number}_USER", os.getenv("SSH_USER")),
        })
    if len({vm["ip"] for vm in vms}) != 3:
        raise ValueError("Each monitored VM needs a distinct IP")
    if not os.getenv("SSH_KEY_PATH") or not all(vm["user"] for vm in vms):
        raise ValueError("SSH_USER and SSH_KEY_PATH are required in SSH mode")
    return vms


def _write_connection_event(vm, history, unavailable):
    """SSH failures are NOT proof that a VM is powered off."""
    try:
        with app.app_context():
            server = Server.query.filter_by(ip=vm["ip"]).first()
            if server is not None:
                db.session.add(Event(
                    server_id=server.id, history=history[:255],
                    unavailable=unavailable,
                ))
                db.session.commit()
    except Exception:
        db.session.rollback()
        log.exception("Could not write SSH diagnostic event for %s", vm["ip"])


def collect_once(vms, failed_ips):
    for vm in vms:
        try:
            data = collect_vm(vm, vm["user"],
                              os.environ["SSH_KEY_PATH"],
                              os.getenv("SSH_KNOWN_HOSTS"))
        except Exception as exc:
            log.error("SSH collection failed for %s: %s", vm["ip"], exc)
            if vm["ip"] not in failed_ips:
                _write_connection_event(
                    vm, f"SSH collection failed: {str(exc)[:180]}", False,
                )
                failed_ips.add(vm["ip"])
            continue
        try:
            with app.app_context():
                result = process_monitoring(data)
            if vm["ip"] in failed_ips:
                _write_connection_event(vm, "SSH collection recovered", False)
                failed_ips.remove(vm["ip"])
            log.info("%s CPU %.1f MEM %.1f DISK %.1f new alerts %s",
                     vm["ip"], data["cpu"], data["memory"], data["disk"],
                     result["alerts_created"])
        except Exception:
            log.exception("Could not store SSH reading from %s", vm["ip"])


def main():
    vms = load_vms()
    interval = int(os.getenv("COLLECTION_INTERVAL", "60"))
    if interval < 5:
        raise ValueError("COLLECTION_INTERVAL must be at least 5 seconds")
    failed_ips = set()
    while True:
        started = time.monotonic()
        collect_once(vms, failed_ips)
        time.sleep(max(0, interval - (time.monotonic() - started)))


if __name__ == "__main__":
    main()
