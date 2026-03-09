from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

import pandas as pd
from ib_insync import IB, Stock, Forex, util

from .broker import Broker, OrderResult
from .models import AccountState, Position

log = logging.getLogger(__name__)


class IbkrBroker(Broker):
    def __init__(
        self,
        *,
        host: str,
        port: int,
        client_id: int,
        account: str = "",
        exchange: str = "ARCA",
        currency: str = "USD",
    ):
        self.host = host
        self.port = port
        self.client_id = client_id
        self.account = account
        self.exchange = exchange
        self.currency = currency
        self.ib = IB()

    def _make_contract(self, symbol: str):
        # Forex shorthand: EURUSD with IDEALPRO becomes Forex('EURUSD').
        if self.exchange.upper() == "IDEALPRO" and len(symbol) == 6 and symbol.isalpha():
            return Forex(symbol.upper())
        return Stock(symbol, self.exchange, self.currency)

    def connect(self) -> None:
        log.info(f"Connecting to IBKR {self.host}:{self.port} clientId={self.client_id}...")
        self.ib.connect(self.host, self.port, clientId=self.client_id)
        log.info("Connected.")

    def disconnect(self) -> None:
        if self.ib.isConnected():
            self.ib.disconnect()

    def get_account_state(self) -> AccountState:
        # net liquidation
        values = self.ib.accountSummary(account=self.account or "")
        def get(tag: str) -> float:
            for v in values:
                if v.tag == tag:
                    try:
                        return float(v.value)
                    except Exception:
                        return 0.0
            return 0.0
        nlv = get("NetLiquidation")
        eq = get("EquityWithLoanValue") or nlv
        return AccountState(net_liquidation=nlv, equity=eq)

    def get_position(self, symbol: str) -> Optional[Position]:
        for p in self.ib.positions():
            if p.contract.symbol == symbol:
                # market price from ticker
                c = p.contract
                ticker = self.ib.reqMktData(c, "", False, False)
                self.ib.sleep(1)
                mkt = float(ticker.marketPrice() or 0.0)
                return Position(symbol=symbol, qty=float(p.position), avg_price=float(p.avgCost), market_price=mkt)
        return None

    def get_bars(self, symbol: str, *, bar_size: str, lookback_days: int, use_rth: bool = True) -> pd.DataFrame:
        contract = self._make_contract(symbol)
        self.ib.qualifyContracts(contract)

        # Forex historical bars are typically requested with MIDPOINT.
        what_to_show = "MIDPOINT" if isinstance(contract, Forex) else "TRADES"

        bars = self.ib.reqHistoricalData(
            contract,
            endDateTime="",
            durationStr=f"{lookback_days} D",
            barSizeSetting=bar_size,
            whatToShow=what_to_show,
            useRTH=bool(use_rth),
            formatDate=1,
        )

        df = util.df(bars)
        if df is None or getattr(df, "empty", True):
            return pd.DataFrame(columns=["time", "open", "high", "low", "close", "volume"])

        df = df.rename(columns={"date": "time"})
        if "time" not in df.columns:
            return pd.DataFrame(columns=["time", "open", "high", "low", "close", "volume"])

        # Ensure datetime
        if not pd.api.types.is_datetime64_any_dtype(df["time"]):
            df["time"] = pd.to_datetime(df["time"])

        cols = ["time", "open", "high", "low", "close", "volume"]
        for c in cols:
            if c not in df.columns:
                df[c] = 0.0
        return df[cols].copy()

    def place_target_value_order(self, symbol: str, target_value: float, *, paper_only: bool) -> OrderResult:
        if paper_only:
            return OrderResult(order_id="DRY", status="SKIPPED_PAPER_ONLY")

        contract = self._make_contract(symbol)
        self.ib.qualifyContracts(contract)

        # Get price
        ticker = self.ib.reqMktData(contract, "", False, False)
        self.ib.sleep(1)
        price = float(ticker.marketPrice() or 0.0)
        if price <= 0:
            raise RuntimeError("No market price")

        current_pos = self.get_position(symbol)
        current_qty = current_pos.qty if current_pos else 0.0
        target_qty = int(target_value / price)
        delta = target_qty - int(current_qty)

        if delta == 0:
            return OrderResult(order_id="0", status="NOOP")

        action = "BUY" if delta > 0 else "SELL"
        qty = abs(delta)
        order = util.marketOrder(action, qty)
        trade = self.ib.placeOrder(contract, order)
        self.ib.sleep(1)
        return OrderResult(order_id=str(trade.order.orderId), status=str(trade.orderStatus.status))
