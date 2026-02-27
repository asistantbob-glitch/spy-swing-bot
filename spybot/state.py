from __future__ import annotations

import json
import os
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .risk import RiskState


def default_state_path() -> Path:
    # Keep state local to the repo by default.
    return Path("state") / "risk_state.json"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_risk_state(path: Path) -> RiskState:
    """Load RiskState from JSON. Returns empty RiskState if file does not exist."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return RiskState()

    if not isinstance(data, dict):
        return RiskState()

    return RiskState(
        starting_equity=data.get("starting_equity"),
        day_start_equity=data.get("day_start_equity"),
        day_start_date=data.get("day_start_date"),
    )


def save_risk_state(path: Path, state: RiskState) -> None:
    """Persist RiskState to JSON with restrictive permissions when possible."""
    path.parent.mkdir(parents=True, exist_ok=True)

    payload: dict[str, Any] = {
        "starting_equity": state.starting_equity,
        "day_start_equity": state.day_start_equity,
        "day_start_date": state.day_start_date,
        "last_updated_utc": _utc_now_iso(),
    }

    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    # Best-effort permission tightening.
    try:
        os.chmod(tmp, 0o600)
    except Exception:
        pass

    tmp.replace(path)
