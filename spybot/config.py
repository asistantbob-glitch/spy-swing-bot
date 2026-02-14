from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional

try:
    import tomllib  # py3.11+
except Exception:  # pragma: no cover
    import tomli as tomllib


@dataclass(frozen=True)
class BotCfg:
    name: str
    timezone: str = "UTC"


@dataclass(frozen=True)
class BrokerCfg:
    kind: Literal["ibkr"]
    host: str
    port: int
    client_id: int
    account: str = ""


@dataclass(frozen=True)
class MarketCfg:
    symbol: str
    exchange: str = "ARCA"
    currency: str = "USD"
    bar_size: str = "1 hour"
    lookback_days: int = 120


@dataclass(frozen=True)
class TimeframesCfg:
    primary: Literal["1h", "4h"] = "4h"
    use_rth: bool = True


@dataclass(frozen=True)
class StrategyCfg:
    sma_fast: int = 20
    sma_slow: int = 100
    rsi_period: int = 14
    rsi_entry_max: float = 45
    atr_period: int = 14
    stop_atr_mult: float = 2.5


@dataclass(frozen=True)
class RiskCfg:
    max_position_pct: float
    max_daily_loss_usd: float
    max_drawdown_pct: float


@dataclass(frozen=True)
class RunCfg:
    eval_every_minutes: int = 60
    paper_only: bool = True


@dataclass(frozen=True)
class Config:
    bot: BotCfg
    broker: BrokerCfg
    market: MarketCfg
    timeframes: TimeframesCfg
    strategy: StrategyCfg
    risk: RiskCfg
    run: RunCfg


def load_config(path: Path) -> Config:
    raw = tomllib.loads(path.read_text(encoding="utf-8"))

    bot = BotCfg(**raw.get("bot", {}))
    broker = BrokerCfg(**raw["broker"])
    market = MarketCfg(**raw.get("market", {}))
    timeframes = TimeframesCfg(**raw.get("timeframes", {}))
    strategy = StrategyCfg(**raw.get("strategy", {}))
    risk = RiskCfg(**raw["risk"])
    run = RunCfg(**raw.get("run", {}))

    return Config(bot=bot, broker=broker, market=market, timeframes=timeframes, strategy=strategy, risk=risk, run=run)
