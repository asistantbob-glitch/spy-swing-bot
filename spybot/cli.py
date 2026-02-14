import argparse
from pathlib import Path

from .config import load_config
from .runner import run_bot_once
from .scheduler import run_forever


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="spybot")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="Run the bot")
    r.add_argument("--config", required=True, type=Path)
    r.add_argument("--dry-run", action="store_true", help="No broker connection, no orders")
    r.add_argument("--loop", action="store_true", help="Run forever on an interval")

    args = p.parse_args(argv)

    if args.cmd == "run":
        cfg = load_config(args.config)
        if args.loop:
            run_forever(cfg, dry_run=bool(args.dry_run))
        else:
            run_bot_once(cfg, dry_run=bool(args.dry_run))
        return 0

    return 2
