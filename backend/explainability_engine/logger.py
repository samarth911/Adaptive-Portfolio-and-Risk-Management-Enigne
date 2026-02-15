"""
Explainability Engine: structured decision log for every rebalance/risk action.
Each entry includes plain-language explanations so a 12th grader can understand.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import copy


def _format_pct(w: float) -> str:
    return f"{w * 100:.0f}%" if w is not None else "—"


def _plain_language(
    regime: str,
    base_allocation: Optional[Dict[str, float]],
    new_allocation: Optional[Dict[str, float]],
    action_taken: str,
    reason: str,
    drawdown: Optional[float],
    portfolio_volatility: Optional[float],
    risk_reduced: bool,
) -> Dict[str, str]:
    """Generate 12th-grade-friendly explanations."""
    regime_explain = {
        "TRENDING_UP": "the market is in an **upward trend** (prices are generally going up over time).",
        "TRENDING_DOWN": "the market is in a **downward trend** (prices are generally going down).",
        "HIGH_VOL": "the market is **very jumpy** right now (big swings up and down).",
        "CRASH": "the market is in a **sharp drop** (we’re seeing a big loss from recent highs).",
    }.get(regime, "the market regime is unclear.")

    what_we_did = "We updated how your money is split across assets (stocks, bonds, gold, etc.)."
    if new_allocation:
        parts = [f"{asset}: {_format_pct(w)}" for asset, w in sorted(new_allocation.items()) if w and w > 0]
        if parts:
            what_we_did = "We set your portfolio to: " + ", ".join(parts) + "."

    why_it_matters = ""
    if regime == "TRENDING_UP":
        why_it_matters = "When the market is going up, we tilt a bit more toward growth assets (like stocks) to try to grow your money, while still keeping some in safer assets in case things change."
    elif regime == "TRENDING_DOWN":
        why_it_matters = "When the market is going down, we shift more into safer assets (like bonds) so your portfolio doesn’t fall as hard."
    elif regime == "HIGH_VOL":
        why_it_matters = "When the market is very jumpy, we spread your money more evenly and may reduce how much we put at risk so you’re less exposed to big swings."
    elif regime == "CRASH":
        why_it_matters = "When the market is in a sharp drop, we move heavily into safer assets to protect your capital and limit further losses."

    if risk_reduced:
        why_it_matters += " We also reduced risk (for example by lowering volatility or cutting exposure) to keep the portfolio within your risk target."

    if portfolio_volatility is not None and portfolio_volatility > 0:
        vol_pct = f"{portfolio_volatility * 100:.1f}%"
        why_it_matters += f" Your portfolio’s current volatility (how much it bounces around) is about {vol_pct} per year."
    if drawdown is not None and drawdown < 0:
        dd_pct = f"{drawdown * 100:.1f}%"
        why_it_matters += f" You’re currently down {dd_pct} from the highest value your portfolio has reached."

    summary = f"On this date we detected that {regime_explain} {what_we_did} {why_it_matters}"

    return {
        "plain_summary": summary,
        "what_we_did": what_we_did,
        "why_it_matters": why_it_matters.strip(),
        "regime_in_plain_english": regime_explain,
    }


class ExplainabilityEngine:
    """
    Logs every decision with: date, regime, portfolio_volatility, action_taken, reason, new_allocation,
    plus plain-language fields (plain_summary, what_we_did, why_it_matters) for easy reading.
    """

    def __init__(self):
        self._logs: List[Dict[str, Any]] = []

    def log(
        self,
        date: str,
        regime: str,
        portfolio_volatility: Optional[float] = None,
        action_taken: str = "",
        reason: str = "",
        new_allocation: Optional[Dict[str, float]] = None,
        base_allocation: Optional[Dict[str, float]] = None,
        drawdown: Optional[float] = None,
        risk_reduced: bool = False,
    ) -> None:
        plain = _plain_language(
            regime=regime,
            base_allocation=base_allocation,
            new_allocation=new_allocation,
            action_taken=action_taken,
            reason=reason,
            drawdown=drawdown,
            portfolio_volatility=portfolio_volatility,
            risk_reduced=risk_reduced,
        )
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "date": date,
            "regime": regime,
            "portfolio_volatility": portfolio_volatility,
            "action_taken": action_taken,
            "reason": reason,
            "new_allocation": copy.deepcopy(new_allocation) if new_allocation else None,
            "base_allocation": copy.deepcopy(base_allocation) if base_allocation else None,
            "drawdown": drawdown,
            "risk_reduced": risk_reduced,
            "plain_summary": plain["plain_summary"],
            "what_we_did": plain["what_we_did"],
            "why_it_matters": plain["why_it_matters"],
            "regime_in_plain_english": plain["regime_in_plain_english"],
        }
        self._logs.append(entry)

    def get_logs(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return logs (newest last). Optionally limit count (take last N)."""
        if limit is not None:
            return self._logs[-limit:]
        return list(self._logs)

    def clear(self) -> None:
        self._logs.clear()
