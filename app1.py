import streamlit as st
import requests
import pandas as pd

API_BASE_URL="http://127.0.0.1:8000"

try:
    stocks_response = requests.get(f"{API_BASE_URL}/stocks", timeout=5)
    stocks_response.raise_for_status()
    stocks = stocks_response.json()["stocks"]
except Exception as e:
    st.error(f"❌ Cannot connect to API server. Make sure it's running with: uvicorn api_server:app --reload\nError: {str(e)}")
    st.stop()

def make_api_request(method, endpoint, data=None,timeout=5):
    try:
        url=f"{API_BASE_URL}{endpoint}"
        if method == "GET":
                response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
        elif method == "POST":
            response = requests.post(f"{API_BASE_URL}{endpoint}", json=data, timeout=5)
        else:
            st.error("Unsupported HTTP method")
            return None
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {str(e)}")
            return None
def get_stocks():
    #get list of all stocks from API
    result=make_api_request("GET", "/stocks")
    if result:
        return result.get("stocks", [])
    return []

def analyze_stock(stock: str):
     """Analyze a specific stock and get trading decisions."""
     return make_api_request("POST", f"/analyze_stock/{stock}")
    


st.subheader("trading mode")
mode = st.radio(
    "Trading Mode",
    ["Manual Trading", "Autonomous Trading", "Model Trading"],
    horizontal=True   # puts them on the same line
)

st.title("Stock Selector")
dropdown = st.selectbox("Select Stock", stocks)

st.write("Selected mode:", mode)

#fetch reliance data 






if mode == "Manual Trading":
    all_stocks=get_stocks()  # Assume this function fetches all available stocks
    stock=st.selectbox("Select Stock for Manual Trading", all_stocks)
    if st.button("Run AI Trading Brain"):
        st.info("Analyzing stock and running AI Brain...")
        # Here you would add the logic to analyze the stock and run the AI trading brain
        result=analyze_stock(stock)