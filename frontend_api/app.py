# frontend_api/app.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
from frontend_api.routes import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# -------------------------------------------------------
# 📦 Mock Storage (Replace with real engine output)
# -------------------------------------------------------

system_state = {
    "portfolio_value": 1_000_000,
    "regime": "BULL",
    "risk_status": "LOW",
    "metrics": {
        "CAGR": 0.12,
        "Sharpe": 1.4,
        "Max Drawdown": -0.18
    }
}

# -------------------------------------------------------
# 🧠 API Endpoints
# -------------------------------------------------------

@app.get("/")
def root():
    return {"message": "Portfolio Engine API Running"}

# -------------------------------------------------------
# 1️⃣ Portfolio Summary
# -------------------------------------------------------

@app.get("/portfolio")
def get_portfolio():
    return {
        "portfolio_value": system_state["portfolio_value"],
        "metrics": system_state["metrics"]
    }

# -------------------------------------------------------
# 2️⃣ Current Regime
# -------------------------------------------------------

@app.get("/regime")
def get_regime():
    return {
        "current_regime": system_state["regime"]
    }

# -------------------------------------------------------
# 3️⃣ Risk Status
# -------------------------------------------------------

@app.get("/risk")
def get_risk_status():
    return {
        "risk_status": system_state["risk_status"]
    }

# -------------------------------------------------------
# 4️⃣ Run Backtest
# -------------------------------------------------------

class BacktestRequest(BaseModel):
    start_date: str
    end_date: str


@app.post("/run_backtest")
def run_backtest(request: BacktestRequest):
    """
    This should trigger:
    - Data load
    - Feature generation
    - Regime detection
    - Allocation
    - Risk engine
    - Backtest
    - Metrics computation
    """

    # Replace this with real system call
    # results = run_full_system(request.start_date, request.end_date)

    return {
        "message": "Backtest executed successfully",
        "start_date": request.start_date,
        "end_date": request.end_date
    }

# -------------------------------------------------------
# 5️⃣ Stress Test Endpoint
# -------------------------------------------------------

@app.post("/stress_test")
def run_stress_test():
    return {
        "message": "Stress test executed",
        "drawdown_after_shock": -0.22
    }
