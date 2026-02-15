# explainability/decision_logger.py

from typing import Dict, List
import pandas as pd


class DecisionLogger:
    """
    Logs system decisions for transparency and frontend display.
    """

    def __init__(self):
        self.logs: List[Dict] = []

    # -------------------------------------------------------
    # 1️⃣ Log Decision
    # -------------------------------------------------------
    def log_decision(
        self,
        date,
        regime: str,
        base_weights: Dict[str, float],
        adjusted_weights: Dict[str, float],
        volatility: float = None,
        drawdown: float = None
    ):

        explanation = self._generate_explanation(
            regime, volatility, drawdown
        )

        log_entry = {
            "date": date,
            "regime": regime,
            "base_weights": base_weights,
            "adjusted_weights": adjusted_weights,
            "volatility": volatility,
            "drawdown": drawdown,
            "explanation": explanation
        }

        self.logs.append(log_entry)

    # -------------------------------------------------------
    # 2️⃣ Explanation Generator
    # -------------------------------------------------------
    def _generate_explanation(
        self,
        regime: str,
        volatility: float,
        drawdown: float
    ) -> str:

        message = f"Market regime detected: {regime}. "

        if regime == "CRISIS":
            message += "Significant drawdown observed. Defensive allocation activated. "

        elif regime == "HIGH_VOL":
            message += "Volatility elevated. Exposure reduced to manage risk. "

        elif regime == "BULL":
            message += "Positive trend detected. Increasing growth asset exposure. "

        elif regime == "BEAR":
            message += "Weak trend observed. Maintaining defensive balance. "

        if volatility is not None:
            message += f"Current portfolio volatility: {round(volatility, 3)}. "

        if drawdown is not None:
            message += f"Current drawdown: {round(drawdown, 3)}."

        return message

    # -------------------------------------------------------
    # 3️⃣ Export Logs
    # -------------------------------------------------------
    def get_logs(self) -> pd.DataFrame:
        return pd.DataFrame(self.logs)
