
from venv import logger
from fastapi import FastAPI, HTTPException
from data.universe import NIFTY50
from pydantic import BaseModel
from typing import List
import pandas as pd

app=FastAPI()

class StockListResponse(BaseModel):
    stocks: List[str]
    count: int

class AnalysisResponse(BaseModel):
    stock: str
    signal: str
    rei: float
    volatility: float
    current_price: float
    ai_decision: str
    trade_action: float




@app.get("/stocks", response_model=StockListResponse,tags=["Stocks"])
def get_stocks():
    try:
        return{
            "stocks": NIFTY50,
            "count": len(NIFTY50)
        }
    except Exception as e:
        logger.error(f"Error fetching stocks: {(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze", response_model=AnalysisResponse, tags=["Manual Trading"])
async def analyze_stock(request: TradeRequest):
    try:
        stock = request.stock
        logger.info(f"Analyzing stock: {stock}")

        df = fetch(stock)
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for stock: {stock}")
        
    except Exception as e:
        logger.error(f"Error analyzing stock {stock}: {(e)}")
        raise HTTPException(status_code=500, detail=str(e))