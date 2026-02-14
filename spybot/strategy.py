from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .models import Signal

log = logging.getLogger(__name__)


def _rsi(series: pd.Series, period: int) -> pd.Series:
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / (loss.replace(0, np.nan))
    return 100 - (100 / (1 + rs))


def _atr(df: pd.DataFrame, period: int) -> pd.Series:
    high = df["high"]
    low = df["low"]
    close = df["close"]
    prev_close = close.shift(1)
    tr = pd.concat([
        (high - low),
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.rolling(period).mean()


@dataclass(frozen=True)
class StrategyParams:
    sma_fast: int
    sma_slow: int
    rsi_period: int
    rsi_entry_max: float
    atr_period: int
    stop_atr_mult: float


class SpySwingStrategy:
    """Very simple swing strategy on daily bars.

    - Trend filter: close > SMA(slow)
    - Entry: pullback condition (RSI <= rsi_entry_max) while above SMA(slow)
    - Exit: close < SMA(slow) (trend broken)

    This is intentionally simple; we’ll refine later.
    """

    def __init__(self, params: StrategyParams):
        self.p = params

    def generate(self, bars: pd.DataFrame, *, current_position_value: float, target_position_value: float) -> Signal:
        if len(bars) < max(self.p.sma_slow, self.p.rsi_period, self.p.atr_period) + 5:
            return Signal(action="HOLD", reason="not enough bars")

        df = bars.copy()
        df["sma_fast"] = df["close"].rolling(self.p.sma_fast).mean()
        df["sma_slow"] = df["close"].rolling(self.p.sma_slow).mean()
        df["rsi"] = _rsi(df["close"], self.p.rsi_period)
        df["atr"] = _atr(df, self.p.atr_period)

        last = df.iloc[-1]

        if np.isnan(last["sma_slow"]) or np.isnan(last["rsi"]):
            return Signal(action="HOLD", reason="indicators not ready")

        in_uptrend = last["close"] > last["sma_slow"]
        if not in_uptrend:
            if current_position_value > 0:
                return Signal(action="SELL", reason="trend break: close < sma_slow")
            return Signal(action="HOLD", reason="no uptrend")

        # Uptrend: consider entry
        if current_position_value <= 0 and last["rsi"] <= self.p.rsi_entry_max:
            return Signal(action="BUY", reason=f"pullback entry rsi={last['rsi']:.1f}", target_position_value=target_position_value)

        return Signal(action="HOLD", reason="no signal")
