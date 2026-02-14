from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass(frozen=True)
class AccountState:
    net_liquidation: float
    equity: float


@dataclass(frozen=True)
class Position:
    symbol: str
    qty: float
    avg_price: float
    market_price: float

    @property
    def market_value(self) -> float:
        return float(self.qty) * float(self.market_price)


@dataclass(frozen=True)
class Signal:
    action: str  # "BUY" | "SELL" | "HOLD"
    reason: str
    target_position_value: float = 0.0


@dataclass(frozen=True)
class Bar:
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
