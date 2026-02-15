"""Performance metrics and suspicious-flagging for backtest results."""

import pandas as pd
import numpy as np
from typing import Dict, Any

from .. import config as cfg


def _returns_from_equity(equity: pd.Series) -> pd.Series:
    return equity.pct_change().dropna()


def backtest_metrics(
    equity_curve: pd.Series,
    risk_free_rate: float = 0.02,
) -> Dict[str, float]:
    """CAGR, Ann Vol, Sharpe, Sortino, Max DD, Calmar."""
    if equity_curve is None or len(equity_curve) < 2:
        return {}
    ret = _returns_from_equity(equity_curve)
    if ret.empty:
        return {}
    years = (equity_curve.index[-1] - equity_curve.index[0]).days / 365.25
    if years <= 0:
        years = 1.0
    total_ret = equity_curve.iloc[-1] / equity_curve.iloc[0]
    cagr = total_ret ** (1 / years) - 1
    ann_vol = ret.std() * np.sqrt(252) if ret.std() > 0 else 0
    excess = ret.mean() * 252 - risk_free_rate
    sharpe = excess / ann_vol if ann_vol > 0 else 0
    downside = ret[ret < 0]
    downside_vol = downside.std() * np.sqrt(252) if len(downside) > 0 and downside.std() > 0 else 1e-8
    sortino = excess / downside_vol
    cummax = equity_curve.cummax()
    dd = (equity_curve - cummax) / cummax.replace(0, np.nan)
    max_dd = float(dd.min()) if hasattr(dd, "min") else 0
    calmar = cagr / abs(max_dd) if max_dd != 0 else 0
    return {
        "CAGR": cagr,
        "Annual Volatility": ann_vol,
        "Sharpe Ratio": sharpe,
        "Sortino Ratio": sortino,
        "Max Drawdown": max_dd,
        "Calmar Ratio": calmar,
    }


def flag_suspicious(metrics: Dict[str, float]) -> Dict[str, Any]:
    """Add flags for suspiciously good metrics (e.g. overfitting)."""
    out = dict(metrics)
    suspicious = []
    if metrics.get("Sharpe Ratio", 0) > cfg.SHARPE_SUSPICIOUS:
        suspicious.append(f"Sharpe Ratio > {cfg.SHARPE_SUSPICIOUS}")
    if metrics.get("Calmar Ratio", 0) > cfg.CALMAR_SUSPICIOUS:
        suspicious.append(f"Calmar Ratio > {cfg.CALMAR_SUSPICIOUS}")
    out["suspicious_flags"] = suspicious
    out["suspicious"] = len(suspicious) > 0
    return out
