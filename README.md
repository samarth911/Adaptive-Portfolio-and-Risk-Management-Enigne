# Autonomous Adaptive Portfolio & Risk Management Engine

A full financial decision system: regime detection, dynamic allocation, risk management, backtesting (with/without risk), stress testing, and explainability — with a real-time simulation dashboard.

## What this is

- **Not** a stock predictor or single ML model or buy/sell signal generator.
- **Is** a robo-advisor + risk-desk style engine that:
  - Detects market regimes (TRENDING_UP, TRENDING_DOWN, HIGH_VOL, CRASH)
  - Allocates capital dynamically (regime + risk parity / momentum)
  - Applies volatility targeting and drawdown protection
  - Backtests with and without risk for comparison
  - Stress-tests portfolios (-5% shock, vol/correlation spike)
  - Logs every decision for an "AI Decision Log" panel

## Quick start

### Backend (Python)

```bash
# From project root
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
PYTHONPATH=. python run_backend.py
# API: http://127.0.0.1:8000
```

### Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
# Dashboard: http://localhost:5173
```

### Usage

1. Open the dashboard.
2. Click **Run backtest** to run historical backtest (with vs without risk); equity curve and metrics appear.
3. Click **Stress test** to run the -5% shock scenario.
4. Click **Start simulation** to run 1 sec = 1 day real-time sim; portfolio and AI Decision Log update live.
5. Use **Add funds** / **Withdraw** (fake payment modal) and **Risk level** (Low / Medium / High) as needed.

## Project layout

```
backend/
  data_engine/       # Prices, returns, rolling vol/MA/correlations (no leakage)
  regime_engine/     # Rule-based + optional clustering → TRENDING_UP/DOWN, HIGH_VOL, CRASH
  allocation_engine/ # Regime-adaptive weights (risk parity, momentum, templates)
  risk_engine/      # Vol targeting, drawdown protection, optional stop-loss
  backtest_engine/  # Walk-forward backtest, with/without risk, metrics + suspicious flags
  stress_test_engine/ # -5% shock, vol spike, correlation spike
  explainability_engine/ # Structured decision log per rebalance
  portfolio_state/   # Value, positions, regime, history
  api/               # FastAPI: portfolio, regime, backtest, stress, /engine/log, controls
  core_engine.py     # Orchestrator
  realtime_simulator.py  # 1 sec = 1 day sim
frontend/
  dashboard/        # Main dashboard
  charts/           # Equity, drawdown, allocation, correlation
  engine_log_panel/ # AI Decision Log (terminal-style)
  payment_modal/    # Fake add/withdraw
  portfolio_controls/ # Start/stop, backtest, stress, risk level
```

## API (summary)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/portfolio` | Current value, risk level, metrics |
| GET | `/regime` | Current regime |
| GET | `/state` | Full state (value, allocations, history, logs) |
| GET | `/engine/log` | AI Decision Log entries |
| GET | `/backtest/results` | Cached backtest equity + metrics |
| POST | `/run_backtest` | Run backtest (with/without risk) |
| POST | `/stress_test` | Run stress test |
| POST | `/start` | Start real-time sim |
| POST | `/stop` | Stop sim |
| POST | `/add-funds` | Fake add funds (body: amount, card_number, expiry, cvv) |
| POST | `/withdraw` | Withdraw (body: amount) |
| POST | `/risk-level` | Set LOW / MEDIUM / HIGH (body: level) |

## Config

Edit `backend/config.py` for vol target, max drawdown, rebalance frequency, train/test windows, and risk-level presets.
