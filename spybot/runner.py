from __future__ import annotations

import logging

from .broker import Broker
from .config import Config
from .ibkr_broker import IbkrBroker
from .logging_setup import setup_logging
from .risk import RiskManager
from .strategy import SpySwingStrategy, StrategyParams

log = logging.getLogger(__name__)


def make_broker(cfg: Config) -> Broker:
    if cfg.broker.kind == "ibkr":
        return IbkrBroker(
            host=cfg.broker.host,
            port=cfg.broker.port,
            client_id=cfg.broker.client_id,
            account=cfg.broker.account,
        )
    raise ValueError(f"Unsupported broker kind: {cfg.broker.kind}")


def run_bot_once(cfg: Config, *, dry_run: bool = False) -> None:
    setup_logging()

    log.info(f"Bot: {cfg.bot.name}")
    log.info(f"Symbol: {cfg.market.symbol}")
    log.info(f"Dry run: {dry_run}")

    risk = RiskManager(
        max_position_pct=cfg.risk.max_position_pct,
        max_daily_loss_usd=cfg.risk.max_daily_loss_usd,
        max_drawdown_pct=cfg.risk.max_drawdown_pct,
    )

    strat = SpySwingStrategy(
        StrategyParams(
            sma_fast=cfg.strategy.sma_fast,
            sma_slow=cfg.strategy.sma_slow,
            rsi_period=cfg.strategy.rsi_period,
            rsi_entry_max=cfg.strategy.rsi_entry_max,
            atr_period=cfg.strategy.atr_period,
            stop_atr_mult=cfg.strategy.stop_atr_mult,
        )
    )

    if dry_run:
        log.warning("Dry run selected: skipping broker connect + orders")
        return

    broker = make_broker(cfg)
    broker.connect()
    try:
        acct = broker.get_account_state()
        risk.update_equity(acct)

        ok_dd, msg_dd = risk.check_drawdown(acct)
        ok_dl, msg_dl = risk.check_daily_loss(acct)
        log.info(f"Risk: {msg_dd}")
        log.info(f"Risk: {msg_dl}")
        if not ok_dd or not ok_dl:
            log.error("Risk limits breached: refusing to trade")
            return

        pos = broker.get_position(cfg.market.symbol)
        current_value = pos.market_value if pos else 0.0
        max_value = risk.max_position_value(acct)

        bars_1h = broker.get_bars(
            cfg.market.symbol,
            bar_size=cfg.market.bar_size,
            lookback_days=cfg.market.lookback_days,
            use_rth=cfg.timeframes.use_rth,
        )

        if cfg.timeframes.primary == "4h":
            from .timeframes import resample_ohlcv
            bars = resample_ohlcv(bars_1h, "4h")
        else:
            bars = bars_1h

        sig = strat.generate(bars, current_position_value=current_value, target_position_value=max_value)

        log.info(f"Signal: {sig.action} ({sig.reason})")

        if sig.action == "BUY":
            res = broker.place_target_value_order(cfg.market.symbol, sig.target_position_value, paper_only=cfg.run.paper_only)
            log.info(f"Order: {res.status} id={res.order_id}")
        elif sig.action == "SELL":
            res = broker.place_target_value_order(cfg.market.symbol, 0.0, paper_only=cfg.run.paper_only)
            log.info(f"Order: {res.status} id={res.order_id}")
        else:
            log.info("No action.")

    finally:
        broker.disconnect()
