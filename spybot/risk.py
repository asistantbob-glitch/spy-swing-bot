from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone

from .models import AccountState

log = logging.getLogger(__name__)


@dataclass
class RiskState:
    starting_equity: float | None = None
    day_start_equity: float | None = None
    day_start_date: str | None = None  # YYYY-MM-DD


class RiskManager:
    def __init__(self, *, max_position_pct: float, max_daily_loss_usd: float, max_drawdown_pct: float):
        self.max_position_pct = max_position_pct / 100.0
        self.max_daily_loss_usd = float(max_daily_loss_usd)
        self.max_drawdown_pct = max_drawdown_pct / 100.0
        self.state = RiskState()

    def update_equity(self, acct: AccountState) -> None:
        now = datetime.now(timezone.utc)
        day = now.date().isoformat()

        if self.state.starting_equity is None:
            self.state.starting_equity = float(acct.equity)
            log.info(f"Risk: starting equity set to {self.state.starting_equity:.2f}")

        if self.state.day_start_date != day:
            self.state.day_start_date = day
            self.state.day_start_equity = float(acct.equity)
            log.info(f"Risk: day start equity set to {self.state.day_start_equity:.2f} for {day}")

    def check_drawdown(self, acct: AccountState) -> tuple[bool, str]:
        if self.state.starting_equity is None:
            return True, "starting equity not set"
        dd = (self.state.starting_equity - acct.equity) / self.state.starting_equity
        if dd > self.max_drawdown_pct:
            return False, f"max drawdown exceeded: {dd*100:.2f}% > {self.max_drawdown_pct*100:.2f}%"
        return True, f"drawdown ok: {dd*100:.2f}%"

    def check_daily_loss(self, acct: AccountState) -> tuple[bool, str]:
        if self.state.day_start_equity is None:
            return True, "day start equity not set"
        loss = self.state.day_start_equity - acct.equity
        if loss > self.max_daily_loss_usd:
            return False, f"max daily loss exceeded: ${loss:.2f} > ${self.max_daily_loss_usd:.2f}"
        return True, f"daily loss ok: ${loss:.2f}"

    def max_position_value(self, acct: AccountState) -> float:
        return float(acct.net_liquidation) * self.max_position_pct
