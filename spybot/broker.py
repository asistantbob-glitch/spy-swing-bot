from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Iterable, Optional

import pandas as pd

from .models import AccountState, Position


@dataclass(frozen=True)
class OrderResult:
    order_id: str
    status: str


class Broker(abc.ABC):
    @abc.abstractmethod
    def connect(self) -> None: ...

    @abc.abstractmethod
    def disconnect(self) -> None: ...

    @abc.abstractmethod
    def get_account_state(self) -> AccountState: ...

    @abc.abstractmethod
    def get_position(self, symbol: str) -> Optional[Position]: ...

    @abc.abstractmethod
    def get_bars(self, symbol: str, *, bar_size: str, lookback_days: int, use_rth: bool = True) -> pd.DataFrame:
        """Return DataFrame with columns: time, open, high, low, close, volume"""

    @abc.abstractmethod
    def place_target_value_order(self, symbol: str, target_value: float, *, paper_only: bool) -> OrderResult:
        """Place an order to reach target notional value. Implementation may use MKT order."""
