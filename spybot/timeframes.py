from __future__ import annotations

import pandas as pd


def resample_ohlcv(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    """Resample OHLCV DataFrame with columns: time, open, high, low, close, volume.

    Assumes `time` is datetime-like.
    """
    if df.empty:
        return df
    x = df.copy()
    x = x.sort_values("time")
    x = x.set_index("time")

    o = x["open"].resample(rule).first()
    h = x["high"].resample(rule).max()
    l = x["low"].resample(rule).min()
    c = x["close"].resample(rule).last()
    v = x["volume"].resample(rule).sum()

    out = pd.concat({"open": o, "high": h, "low": l, "close": c, "volume": v}, axis=1).dropna()
    out = out.reset_index()
    return out
