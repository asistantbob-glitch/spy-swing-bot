from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from .config import Config
from .runner import run_bot_once

log = logging.getLogger(__name__)


def run_forever(cfg: Config, *, dry_run: bool = False) -> None:
    """Simple interval scheduler.

    Runs `run_bot_once` every `cfg.run.eval_every_minutes` minutes.
    """
    interval_s = max(1, int(cfg.run.eval_every_minutes) * 60)
    log.info(f"Scheduler: running every {interval_s}s")

    while True:
        start = datetime.now(timezone.utc)
        try:
            run_bot_once(cfg, dry_run=dry_run)
        except Exception:
            log.exception("Run failed")
        elapsed = (datetime.now(timezone.utc) - start).total_seconds()
        sleep_s = max(1, interval_s - int(elapsed))
        log.info(f"Scheduler: sleeping {sleep_s}s")
        time.sleep(sleep_s)
