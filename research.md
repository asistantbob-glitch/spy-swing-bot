# Research Notebook

Append-only research notes used to make educated trading decisions.

Topics to capture:
- Macro regime notes (rates, inflation, credit spreads)
- SPY/S&P500 historical behavior and seasonality
- Volatility regime (VIX)
- Risk management and position sizing references
- Strategy changes and rationale

---

_No research yet._

## 2026-02-19 — Account tradability probe summary

Findings from controlled paper probes:
- PASS: EURUSD, GBPUSD (IDEALPRO)
- FAIL: USDJPY (currency leverage permission constraint)
- FAIL: BTCUSD/ETHUSD (PAXOS requires cash quantity order semantics)
- FAIL/Pending: CSPX, VUAA (no fill in test window; likely exchange/session/routing constraints)

Actionable implication:
- For rapid bot-learning cycles and execution validation, use FX symbols with confirmed permissions.
- Keep ETF universe as secondary track with explicit session/routing handling.
