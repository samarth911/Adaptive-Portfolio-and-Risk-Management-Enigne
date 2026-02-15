"""
Portfolio State: single source of truth for value, cash, positions, regime, history.
Used by backtest (simulated state) and real-time sim (live state).
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class PortfolioState:
    """
    Tracks portfolio value, cash, positions, current regime, and history.
    """
    initial_capital: float = 100_000.0
    current_value: float = 100_000.0
    cash: float = 100_000.0
    positions: Dict[str, float] = field(default_factory=dict)  # ticker -> quantity
    current_regime: str = "UNKNOWN"
    risk_level: str = "MEDIUM"
    equity_history: List[float] = field(default_factory=list)
    date_history: List[str] = field(default_factory=list)

    def update_from_weights(self, weights: Dict[str, float], prices: Dict[str, float]) -> None:
        """Set positions from target weights and current prices."""
        self.positions = {}
        for asset, weight in weights.items():
            if weight <= 0 or asset not in prices or prices[asset] <= 0:
                continue
            allocation = self.current_value * weight
            self.positions[asset] = allocation / prices[asset]

    def update_value(self, prices: Dict[str, float]) -> float:
        """Mark-to-market; return new current_value."""
        total = 0.0
        for asset, qty in self.positions.items():
            total += qty * prices.get(asset, 0)
        self.current_value = total
        return total

    def append_history(self, value: float, date: str = "") -> None:
        self.equity_history.append(value)
        self.date_history.append(date)

    def get_snapshot(self) -> Dict[str, Any]:
        return {
            "value": self.current_value,
            "cash": self.cash,
            "regime": self.current_regime,
            "risk_level": self.risk_level,
            "positions": dict(self.positions),
            "equity_history": list(self.equity_history),
            "date_history": list(self.date_history),
        }

    def add_cash(self, amount: float) -> None:
        self.cash += amount
        self.current_value += amount

    def withdraw_cash(self, amount: float) -> bool:
        if amount > self.cash:
            return False
        self.cash -= amount
        self.current_value -= amount
        return True
