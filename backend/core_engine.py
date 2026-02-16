"""
Unified Portfolio Engine: orchestrates data -> regime -> allocation -> risk -> backtest.
Used for both one-shot backtest and for real-time simulation (1 sec = 1 day).
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any

from . import config as cfg
from .data_engine import DataEngine
from .regime_engine import RegimeEngine
from .allocation_engine import AllocationEngine
from .risk_engine import RiskEngine
from .explainability_engine import ExplainabilityEngine
from .backtest_engine import BacktestEngine, backtest_metrics, flag_suspicious
from .portfolio_state import PortfolioState


class CoreEngine:
    """
    Single engine: load data, compute features, regime, allocation (with/without risk), log decisions.
    """

    def __init__(
        self,
        tickers: List[str],
        start_date: str,
        end_date: str,
        risk_level: str = "MEDIUM",
        vol_window: int = 21,
    ):
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.risk_level = risk_level
        self.vol_window = vol_window
        risk_params = cfg.RISK_LEVELS.get(risk_level, cfg.RISK_LEVELS["MEDIUM"])
        self.vol_target = risk_params["vol_target"]
        self.max_drawdown_limit = risk_params["max_drawdown_limit"]
        self.exposure_floor = risk_params["exposure_floor"]

        self.data_engine: Optional[DataEngine] = None
        self.regime_engine: Optional[RegimeEngine] = None
        self.allocation_engine: Optional[AllocationEngine] = None
        self.risk_engine: Optional[RiskEngine] = None
        self.explainability: Optional[ExplainabilityEngine] = None
        self.regime_series: Optional[pd.Series] = None
        self.features: Optional[Dict] = None
        self.returns: Optional[pd.DataFrame] = None
        self.prices: Optional[pd.DataFrame] = None

    def load_and_prepare(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load data and compute features. Returns (prices, returns)."""
        self.data_engine = DataEngine(
            self.tickers, self.start_date, self.end_date, vol_window=self.vol_window
        )
        self.prices, self.returns = self.data_engine.load()
        self.features = self.data_engine.get_features()
        self.regime_engine = RegimeEngine(
            vol_threshold=cfg.VOL_THRESHOLD,
            drawdown_threshold=cfg.DRAWDOWN_THRESHOLD,
        )
        self.regime_series = self.regime_engine.generate_regime_series(
            self.features["volatility"],
            self.features["drawdown"],
            self.features["trend_signal"],
        )
        self.allocation_engine = AllocationEngine(self.tickers)
        self.risk_engine = RiskEngine(
            self.returns,
            vol_target=self.vol_target,
            max_drawdown_limit=self.max_drawdown_limit,
            exposure_floor=self.exposure_floor,
            enabled=True,
            vol_window=self.vol_window,
        )
        self.explainability = ExplainabilityEngine()
        return self.prices, self.returns

    def build_allocation_function(self, with_risk: bool = True):
        """Returns allocation_function(i, equity_curve_so_far) -> weights dict, and logs decisions."""
        returns = self.returns
        regime_series = self.regime_series
        allocator = self.allocation_engine
        risk_engine = self.risk_engine
        explain = self.explainability

        def allocation_function(i: int, equity_curve_so_far: Optional[pd.Series] = None) -> Dict[str, float]:
            regime = regime_series.iloc[i]
            base_weights = allocator.get_weights(regime)
            if with_risk:
                adj_weights = risk_engine.apply(
                    base_weights, i, equity_curve=equity_curve_so_far,
                    last_returns=returns.iloc[i - 1] if i > 0 else None,
                )
            else:
                adj_weights = base_weights
            port_vol = risk_engine._portfolio_vol(adj_weights, i) if with_risk else 0
            dd = None
            if equity_curve_so_far is not None and len(equity_curve_so_far) > 0:
                ec = equity_curve_so_far.dropna()
                if len(ec) > 0 and ec.iloc[-1] > 0:
                    cummax = ec.cummax()
                    dd = float((ec.iloc[-1] - cummax.iloc[-1]) / cummax.iloc[-1])
            reason = f"Regime: {regime}"
            action = "Allocation updated"
            if with_risk and port_vol > self.vol_target:
                reason += "; Vol scaled to target"
                action = "Reduced exposure (vol targeting)"
            if explain:
                explain.log(
                    date=str(returns.index[i])[:10],
                    regime=regime,
                    portfolio_volatility=port_vol if with_risk else None,
                    action_taken=action,
                    reason=reason,
                    new_allocation=adj_weights,
                    base_allocation=base_weights,
                    drawdown=dd,
                    risk_reduced=with_risk and adj_weights != base_weights,
                )
            return adj_weights

        return allocation_function

    def run_backtest(
        self,
        with_risk: bool = True,
        initial_capital: float = None,
    ) -> Tuple[pd.Series, Dict[str, Any]]:
        """
        Run single backtest. Returns (equity_curve, metrics_with_flags).
        """
        if self.returns is None:
            self.load_and_prepare()
        cap = initial_capital or cfg.INITIAL_CAPITAL
        alloc_fn = self.build_allocation_function(with_risk=with_risk)
        bt = BacktestEngine(
            self.returns,
            alloc_fn,
            cfg.REBALANCE_FREQUENCY,
            cfg.TRANSACTION_COST,
            cap,
        )
        equity = bt.run()
        metrics = flag_suspicious(backtest_metrics(equity))
        return equity, metrics

    def run_backtest_comparison(
        self,
    ) -> Dict[str, Any]:
        """
        Run backtest WITH and WITHOUT risk engine. Returns both equity curves and metrics.
        """
        if self.returns is None:
            self.load_and_prepare()
        alloc_with = self.build_allocation_function(with_risk=True)
        alloc_no = self.build_allocation_function(with_risk=False)
        bt_with = BacktestEngine(
            self.returns, alloc_with,
            cfg.REBALANCE_FREQUENCY, cfg.TRANSACTION_COST, cfg.INITIAL_CAPITAL,
        )
        bt_no = BacktestEngine(
            self.returns, alloc_no,
            cfg.REBALANCE_FREQUENCY, cfg.TRANSACTION_COST, cfg.INITIAL_CAPITAL,
        )
        equity_with = bt_with.run()
        equity_no = bt_no.run()
        metrics_with = flag_suspicious(backtest_metrics(equity_with))
        metrics_no = flag_suspicious(backtest_metrics(equity_no))
        # Correlation matrix from full backtest returns (for heatmap)
        corr = self.returns.corr()
        labels = list(corr.columns)
        correlation_matrix = [
            {labels[j]: float(corr.iloc[i].iloc[j]) for j in range(len(labels))}
            for i in range(len(labels))
        ]
        return {
            "equity_with_risk": equity_with,
            "equity_without_risk": equity_no,
            "metrics_with_risk": metrics_with,
            "metrics_without_risk": metrics_no,
            "dates": list(equity_with.index.astype(str)),
            "correlation_matrix": correlation_matrix,
            "correlation_labels": labels,
        }

    def get_decision_log(self, limit: Optional[int] = None) -> List[Dict]:
        if self.explainability is None:
            return []
        return self.explainability.get_logs(limit=limit)
