# SPY Swing Bot (IBKR) — skeleton

This is a **paper-trading-first** SPY swing-trading bot skeleton intended to run against **IBKR Gateway / TWS** via the IBKR API.

## Safety goals (current defaults)
- Instrument: **SPY**
- Mode: **paper trading** (no live trading until explicitly enabled)
- Max position: **10% of account equity**
- Max daily loss: **$50**
- Max drawdown: **5%**

## What’s implemented
- Config-driven app (`config.toml`)
- Broker adapter interface + IBKR stub (connects when gateway is available)
- Risk manager (position cap + daily loss + drawdown kill switch)
- Simple swing strategy (daily timeframe): trend filter + pullback entry + ATR-based stop
- Structured logging

## What’s not implemented yet
- Running IBKR Gateway/TWS on this host
- Robust market data (historical + live) handling and retries
- Proper order state reconciliation across restarts
- Backtesting / walk-forward evaluation

## Setup
### 0) System prerequisites (Debian)
You may need venv support:
```bash
sudo apt-get update
sudo apt-get install -y python3.13-venv
```

### 1) Create a virtualenv
```bash
cd projects/spy-swing-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

### 2) Configure
Copy and edit config:
```bash
cp config.example.toml config.toml
nano config.toml
```

Optional env vars:
```bash
cp .env.example .env
nano .env
```

### 3) Dry run (no broker)
```bash
python -m spybot run --config config.toml --dry-run
```

### 4) Run (requires IB Gateway/TWS)
Once IB Gateway/TWS is running (paper):
```bash
python -m spybot run --config config.toml
```

## Notes
- This bot is designed for **swing** trading using **1H bars** and a **4H primary timeframe** (recommended).
- It will refuse to place orders if any risk limit is breached.

## Optional: IB Gateway watchdog (no-VNC routine operations)
This watchdog checks if IBKR API port `7497` is reachable and requests a restart of `ibgateway.service` when down.

Install user units:
```bash
mkdir -p ~/.config/systemd/user
cp ops/systemd/ibgateway-watchdog.service ~/.config/systemd/user/
cp ops/systemd/ibgateway-watchdog.timer ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now ibgateway-watchdog.timer
```

Inspect status/logs:
```bash
systemctl --user status ibgateway-watchdog.timer --no-pager
journalctl --user -u ibgateway-watchdog.service -n 50 --no-pager
```

Caveat: IBKR may still require occasional manual login/2FA/disclaimer interaction in VNC.

