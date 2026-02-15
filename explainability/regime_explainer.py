# explainability/regime_explainer.py

def explain_regime(regime):

    explanations = {
        "BULL": "Strong upward trend detected.",
        "BEAR": "Weak market conditions observed.",
        "HIGH_VOL": "Elevated volatility detected.",
        "CRISIS": "Severe drawdown environment."
    }

    return explanations.get(regime, "Unknown regime.")
