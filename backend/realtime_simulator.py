"""
Real-time simulation: 1 second = 1 trading day.
Replays historical returns, runs regime + allocation + risk each "day", updates state and decision log.
"""

import time
import threading
from typing import Dict, List, Optional, Callable
from datetime import datetime

import pandas as pd

from .core_engine import CoreEngine
from .portfolio_state import PortfolioState
from . import config as cfg


class RealtimeSimulator:
    """
    Simulates market in accelerated time. 1 sec = 1 day.
    Portfolio updates in real-time; regime and risk engine run each day; log panel can poll.
    """

    def __init__(
        self,
        tickers: List[str],
        start_date: str,
        end_date: str,
        risk_level: str = "MEDIUM",
        initial_capital: float = None,
        on_tick: Optional[Callable[[Dict], None]] = None,
    ):
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.risk_level = risk_level
        self.initial_capital = initial_capital or cfg.INITIAL_CAPITAL
        self.on_tick = on_tick  # callback for UI updates

        self._engine: Optional[CoreEngine] = None
        self._state: Optional[PortfolioState] = None
        self._returns: Optional[pd.DataFrame] = None
        self._prices: Optional[pd.DataFrame] = None
        self._regime_series: Optional[pd.Series] = None
        self._alloc_fn = None
        self._current_day_index = 0
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def start(self) -> None:
        """Load data and prepare; start simulation thread."""
        with self._lock:
            if self._running:
                return
            self._engine = CoreEngine(
                self.tickers, self.start_date, self.end_date,
                risk_level=self.risk_level,
            )
            self._engine.load_and_prepare()
            self._returns = self._engine.returns
            self._prices = self._engine.prices
            self._regime_series = self._engine.regime_series
            self._alloc_fn = self._engine.build_allocation_function(with_risk=True)
            self._state = PortfolioState(
                initial_capital=self.initial_capital,
                current_value=self.initial_capital,
                cash=self.initial_capital,
                risk_level=self.risk_level,
            )
            self._current_day_index = 0
            self._running = True
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()

    def stop(self) -> None:
        with self._lock:
            self._running = False

    def _run_loop(self) -> None:
        """Advance one day per second."""
        returns = self._returns
        n = len(returns)
        dates = returns.index
        # Day 0: set initial value
        self._state.append_history(self._state.current_value, str(dates[0])[:10])
        self._current_day_index = 1
        while self._running and self._current_day_index < n:
            i = self._current_day_index
            date_str = str(dates[i])[:10]
            equity_so_far = pd.Series(self._state.equity_history) if self._state.equity_history else None
            if i % cfg.REBALANCE_FREQUENCY == 0:
                weights = self._alloc_fn(i, equity_so_far)
                prices_i = self._prices.loc[dates[i]].to_dict()
                self._state.update_from_weights(weights, prices_i)
            self._state.current_regime = self._regime_series.iloc[i]
            row = returns.iloc[i]
            port_ret = sum(
                self._state.positions.get(t, 0) * self._prices.loc[dates[i], t] / self._state.current_value * row.get(t, 0)
                for t in self.tickers if t in row.index and self._state.current_value > 0
            ) if self._state.current_value > 0 else 0
            self._state.current_value = self._state.current_value * (1 + port_ret)
            self._state.append_history(self._state.current_value, date_str)
            self._current_day_index += 1
            if self.on_tick:
                self.on_tick(self.get_state())
            time.sleep(1)

    def get_state(self) -> Dict:
        """Current state for API/dashboard."""
        with self._lock:
            if self._state is None:
                return {
                    "value": 0,
                    "regime": "UNKNOWN",
                    "allocations": {},
                    "history": [],
                    "logs": [],
                    "risk_level": self.risk_level,
                    "running": False,
                }
            snap = self._state.get_snapshot()
            allocations = {}
            if self._state.current_value > 0 and self._state.positions and self._prices is not None:
                for t, qty in self._state.positions.items():
                    if t in self._prices.columns and len(self._prices) > 0:
                        last_price = self._prices.iloc[min(self._current_day_index, len(self._prices) - 1)][t]
                        allocations[t] = (qty * last_price) / self._state.current_value
            else:
                allocations = {t: 1.0 / len(self.tickers) for t in self.tickers}
            logs = []
            if self._engine and self._engine.explainability:
                logs = [
                    {
                        "time": e.get("timestamp", "")[-8:],
                        "message": f"{e.get('regime', '')} | {e.get('action_taken', '')}",
                    }
                    for e in self._engine.get_decision_log(limit=50)
                ]
            return {
                "value": self._state.current_value,
                "regime": self._state.current_regime,
                "allocations": allocations,
                "history": self._state.equity_history,
                "logs": logs,
                "risk_level": self._state.risk_level,
                "running": self._running,
            }

    def add_cash(self, amount: float) -> None:
        with self._lock:
            if self._state:
                self._state.add_cash(amount)

    def withdraw_cash(self, amount: float) -> bool:
        with self._lock:
            if self._state:
                return self._state.withdraw_cash(amount)
        return False

    def set_risk_level(self, level: str) -> None:
        with self._lock:
            if self._state:
                self._state.risk_level = level
            self.risk_level = level
