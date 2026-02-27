from pathlib import Path

from spybot.risk import RiskState
from spybot.state import load_risk_state, save_risk_state


def test_load_missing(tmp_path: Path):
    p = tmp_path / "risk_state.json"
    st = load_risk_state(p)
    assert st == RiskState()


def test_roundtrip(tmp_path: Path):
    p = tmp_path / "risk_state.json"
    st = RiskState(starting_equity=100.0, day_start_equity=95.0, day_start_date="2026-02-14")
    save_risk_state(p, st)
    st2 = load_risk_state(p)
    assert st2.starting_equity == 100.0
    assert st2.day_start_equity == 95.0
    assert st2.day_start_date == "2026-02-14"
