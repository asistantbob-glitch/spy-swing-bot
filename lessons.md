# Lessons Learned

Append-only notes about what we learn while researching, paper trading, and (later) trading live.

Suggested structure:
- Date:
- Observation:
- Evidence (links, backtests, screenshots):
- Decision / change made:
- Result:

---

_No lessons yet._

- Date: 2026-02-19
- Observation: Account-level tradability constraints vary significantly by instrument and venue.
- Evidence: Paper probes showed EURUSD/GBPUSD roundtrip fills while SPY/QQQ/IWM rejected (KID), CSPX/VUAA stuck pre-submitted in test window, BTC/ETH required cash-quantity order model.
- Decision / change made: Prioritize FX instruments (EURUSD/GBPUSD) for execution-path validation and learning loops.
- Result: Confirmed reliable order submit/fill/close path in paper mode for EURUSD/GBPUSD.
