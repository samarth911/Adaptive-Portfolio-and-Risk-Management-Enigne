"""
FastAPI: portfolio, regime, risk, backtest (with/without risk), stress test, decision log, controls.
"""

import os
import sys
from typing import Dict, List, Optional

# Ensure project root on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.core_engine import CoreEngine
from backend.realtime_simulator import RealtimeSimulator
from backend.stress_test_engine import StressTestEngine
from backend import config as cfg

app = FastAPI(title="Autonomous Portfolio & Risk Management API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state: one backtest result cache, one realtime sim
_backtest_cache: Optional[Dict] = None
_sim: Optional[RealtimeSimulator] = None
_default_tickers = ["SPY", "TLT", "GLD"]
_default_start = "2015-01-01"
_default_end = "2024-01-01"


# ---------- Request models ----------
class BacktestRequest(BaseModel):
    start_date: str = "2015-01-01"
    end_date: str = "2024-01-01"
    tickers: List[str] = ["SPY", "TLT", "GLD"]
    risk_level: str = "MEDIUM"


class StressTestRequest(BaseModel):
    start_date: str = "2015-01-01"
    end_date: str = "2024-01-01"
    tickers: List[str] = ["SPY", "TLT", "GLD"]


class PaymentRequest(BaseModel):
    amount: float
    card_number: str = ""
    expiry: str = ""
    cvv: str = ""


class WithdrawRequest(BaseModel):
    amount: float


class RiskLevelRequest(BaseModel):
    level: str  # LOW | MEDIUM | HIGH


# ---------- Endpoints ----------
@app.get("/")
def root():
    return {"message": "Autonomous Portfolio & Risk Management API", "status": "ok"}


@app.get("/portfolio")
def get_portfolio():
    if _sim:
        state = _sim.get_state()
        return {
            "portfolio_value": state["value"],
            "risk_level": state.get("risk_level", "MEDIUM"),
            "metrics": _backtest_metrics_from_cache(),
        }
    return {
        "portfolio_value": 0,
        "risk_level": "MEDIUM",
        "metrics": _backtest_metrics_from_cache(),
    }


def _backtest_metrics_from_cache():
    if _backtest_cache and "metrics_with_risk" in _backtest_cache:
        m = _backtest_cache["metrics_with_risk"]
        return {k: v for k, v in m.items() if k not in ("suspicious_flags", "suspicious") and isinstance(v, (int, float))}
    return {"CAGR": 0, "Sharpe Ratio": 0, "Max Drawdown": 0}


@app.get("/regime")
def get_regime():
    state = _sim.get_state() if _sim else {}
    return {"current_regime": state.get("regime", "UNKNOWN")}


@app.get("/risk")
def get_risk_status():
    state = _sim.get_state() if _sim else {}
    return {"risk_status": state.get("risk_level", "MEDIUM")}


@app.get("/engine/log")
def get_engine_log(limit: int = 100):
    """AI Decision Log for dashboard panel."""
    if _sim and _sim._engine and _sim._engine.explainability:
        logs = _sim._engine.get_decision_log(limit=limit)
        return {"logs": logs}
    if _backtest_cache and "decision_log" in _backtest_cache:
        return {"logs": _backtest_cache["decision_log"][-limit:]}
    return {"logs": []}


@app.get("/backtest/results")
def get_backtest_results():
    """Return cached backtest results (equity curves + metrics + correlation) for dashboard."""
    if _backtest_cache is None:
        return {
            "metrics_with_risk": None,
            "metrics_without_risk": None,
            "equity_with_risk": [],
            "equity_without_risk": [],
            "correlation_matrix": [],
            "correlation_labels": [],
        }
    return {
        "metrics_with_risk": _backtest_cache.get("metrics_with_risk"),
        "metrics_without_risk": _backtest_cache.get("metrics_without_risk"),
        "equity_with_risk": _backtest_cache.get("equity_with_risk", []),
        "equity_without_risk": _backtest_cache.get("equity_without_risk", []),
        "correlation_matrix": _backtest_cache.get("correlation_matrix", []),
        "correlation_labels": _backtest_cache.get("correlation_labels", []),
    }


@app.post("/run_backtest")
def run_backtest(req: BacktestRequest):
    """Run backtest with and without risk; return both metrics and equity series."""
    global _backtest_cache
    try:
        engine = CoreEngine(
            req.tickers, req.start_date, req.end_date,
            risk_level=req.risk_level,
        )
        result = engine.run_backtest_comparison()
        equity_with = result["equity_with_risk"]
        equity_no = result["equity_without_risk"]
        _backtest_cache = {
            "metrics_with_risk": result["metrics_with_risk"],
            "metrics_without_risk": result["metrics_without_risk"],
            "equity_with_risk": [{"date": str(d)[:10], "value": float(v)} for d, v in equity_with.items()],
            "equity_without_risk": [{"date": str(d)[:10], "value": float(v)} for d, v in equity_no.items()],
            "dates": result["dates"],
            "decision_log": engine.get_decision_log(limit=500),
            "correlation_matrix": result.get("correlation_matrix", []),
            "correlation_labels": result.get("correlation_labels", []),
        }
        return {
            "message": "Backtest executed successfully",
            "metrics_with_risk": result["metrics_with_risk"],
            "metrics_without_risk": result["metrics_without_risk"],
            "suspicious": result["metrics_with_risk"].get("suspicious", False),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stress_test")
def run_stress_test(req: StressTestRequest):
    """Run stress test (-5% shock, vol spike, correlation spike)."""
    try:
        engine = CoreEngine(req.tickers, req.start_date, req.end_date)
        engine.load_and_prepare()
        alloc_fn = engine.build_allocation_function(with_risk=True)
        stress = StressTestEngine(engine.returns)
        metrics_stressed = stress.run_stress_backtest(alloc_fn, cfg.INITIAL_CAPITAL, cfg.REBALANCE_FREQUENCY)
        return {
            "message": "Stress test executed",
            "scenario": "-5% daily shock for 5 days",
            "metrics_after_stress": metrics_stressed,
            "drawdown_after_shock": metrics_stressed.get("Max Drawdown", 0),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/start")
def start_engine():
    """Start real-time simulation (1 sec = 1 day)."""
    global _sim
    if _sim is None:
        _sim = RealtimeSimulator(
            _default_tickers, _default_start, _default_end,
            risk_level="MEDIUM",
        )
    _sim.start()
    return {"status": "started"}


@app.post("/stop")
def stop_engine():
    global _sim
    if _sim:
        _sim.stop()
    return {"status": "stopped"}


@app.get("/state")
def get_state():
    """Full state for dashboard (value, regime, allocations, history, logs)."""
    if _sim is None:
        return {
            "value": 0,
            "regime": "UNKNOWN",
            "allocations": {},
            "history": [],
            "logs": [],
            "risk_level": "MEDIUM",
            "running": False,
        }
    return _sim.get_state()


@app.post("/add-funds")
def add_funds(req: PaymentRequest):
    """Fake payment: add funds (accept any card)."""
    if _sim is None:
        raise HTTPException(status_code=400, detail="Start engine first")
    _sim.add_cash(req.amount)
    return {"status": "success", "message": f"Added ${req.amount:.2f}", "new_balance": _sim.get_state()["value"]}


@app.post("/withdraw")
def withdraw(req: WithdrawRequest):
    if _sim is None:
        raise HTTPException(status_code=400, detail="Start engine first")
    ok = _sim.withdraw_cash(req.amount)
    if not ok:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    return {"status": "success", "new_balance": _sim.get_state()["value"]}


@app.post("/risk-level")
def set_risk_level(req: RiskLevelRequest):
    if req.level not in ("LOW", "MEDIUM", "HIGH"):
        raise HTTPException(status_code=400, detail="Invalid risk level")
    if _sim:
        _sim.set_risk_level(req.level)
    return {"status": "ok", "risk_level": req.level}


@app.post("/rebalance")
def rebalance():
    """Manual rebalance: no-op in sim (sim rebalances on schedule)."""
    return {"status": "ok", "message": "Rebalance runs on schedule"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
