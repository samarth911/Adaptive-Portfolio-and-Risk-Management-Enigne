# main.py

from main_engine import AutonomousPortfolioEngine

if __name__ == "__main__":

    engine = AutonomousPortfolioEngine(
        tickers=["SPY", "TLT", "GLD"],
        start_date="2010-01-01",
        end_date="2024-01-01"
    )

    results = engine.run()

    print("Metrics:")
    for k, v in results["metrics"].items():
        print(k, ":", round(v, 4))
