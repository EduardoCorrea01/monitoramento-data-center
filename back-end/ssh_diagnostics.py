"""Optional SSH diagnostics WITHOUT writing measurements or heartbeats.

Safe to run alongside the HTTP agents. To simulate the HTTP-free
alternative, use collector.py instead, but never both for the same VMs.
"""
import os
import sys
from ipaddress import ip_address

from dotenv import load_dotenv

from services.ssh_service import collect_vm


def main():
    load_dotenv()
    key_path = os.getenv("SSH_KEY_PATH", "").strip()
    default_user = os.getenv("SSH_USER", "").strip()
    if not key_path or not default_user:
        print("Set SSH_USER and SSH_KEY_PATH in .env first.", file=sys.stderr)
        return 2

    failed = False
    for index in (1, 2, 3):
        ip = os.getenv(f"VM{index}_IP", "").strip()
        user = os.getenv(f"VM{index}_USER", default_user).strip()
        if not ip:
            print(f"VM{index}_IP is not configured", file=sys.stderr)
            failed = True
            continue
        try:
            ip_address(ip)
            vm = {
                "ip": ip, "port": int(os.getenv(f"VM{index}_PORT", "22")),
                "name": os.getenv(f"VM{index}_NAME", f"VM{index}"),
                "user": user,
            }
            result = collect_vm(vm, user, key_path, os.getenv("SSH_KNOWN_HOSTS"))
            print(f"{ip} SSH OK | CPU={result['cpu']:.1f}% "
                  f"RAM={result['memory']:.1f}% DISK={result['disk']:.1f}%")
        except Exception as exc:
            print(f"{ip} SSH FAILURE: {exc}", file=sys.stderr)
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
