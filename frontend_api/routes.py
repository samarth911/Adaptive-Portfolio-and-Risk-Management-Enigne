from fastapi import APIRouter
from engine.live_data_engine import RealTimePortfolioEngine

router = APIRouter()

engine = None
from fastapi import Query

@router.post("/add-fund")
def add_fund(ticker: str = Query(...)):
    global engine

    if engine is None:
        return {"error": "Engine not started"}

    engine.add_fund(ticker.upper())
    return {"status": f"{ticker} added"}




@router.post("/start")
def start_engine():
    global engine

    if engine is None:
        engine = RealTimePortfolioEngine(
            tickers=["AAPL", "MSFT", "GOOGL"],
            capital=100000
        )

    engine.start()
    return {"status": "started"}



@router.post("/stop")
def stop_engine():
    global engine

    if engine:
        engine.stop()

    return {"status": "stopped"}



@router.post("/add-fund")
def add_fund(ticker: str):
    engine.add_fund(ticker.upper())
    return {"status": "added"}


@router.get("/state")
def state():
    return engine.get_state()
