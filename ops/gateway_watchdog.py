#!/usr/bin/env python3
"""Simple IB Gateway watchdog.

- Checks if API port is listening.
- Restarts `ibgateway.service` (systemd --user) when down.
- Writes state transitions to stdout for journald.

Designed for use with a systemd user timer.
"""

from __future__ import annotations

import argparse
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def port_open(host: str, port: int, timeout: float = 2.0) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            s.connect((host, port))
            return True
        except OSError:
            return False


def read_state(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return "UNKNOWN"


def write_state(path: Path, state: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(state + "\n", encoding="utf-8")


def run_cmd(cmd: list[str]) -> tuple[int, str]:
    p = subprocess.run(cmd, capture_output=True, text=True)
    out = (p.stdout or "") + (p.stderr or "")
    return p.returncode, out.strip()


def restart_ibgateway() -> tuple[bool, str]:
    code, out = run_cmd(["systemctl", "--user", "restart", "ibgateway.service"])
    return code == 0, out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=7497)
    ap.add_argument("--state-file", default="state/watchdog_ibgateway.state")
    args = ap.parse_args()

    state_file = Path(args.state_file)
    prev = read_state(state_file)

    up = port_open(args.host, args.port)
    cur = "UP" if up else "DOWN"

    if cur != prev:
        print(f"[{now_utc()}] WATCHDOG state change: {prev} -> {cur}")

    if not up:
        print(f"[{now_utc()}] WATCHDOG action: restarting ibgateway.service")
        ok, out = restart_ibgateway()
        if not ok:
            print(f"[{now_utc()}] WATCHDOG restart failed: {out}")
            write_state(state_file, "DOWN")
            return 1
        print(f"[{now_utc()}] WATCHDOG restart requested")

    write_state(state_file, cur)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
