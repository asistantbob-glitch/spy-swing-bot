from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def append_signal(*, path: str = "trades.md", symbol: str, action: str, reason: str) -> None:
    p = Path(path)
    line = f"- Signal (UTC { _now_utc() }): {symbol} | {action} | {reason}\n"
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(line)
