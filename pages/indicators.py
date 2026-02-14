import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Indicators", layout="wide")
st.title("📊 EMA • RSI • Volatility")

# Fetch stocks
stocks = requests.get(f"{API_URL}/stocks").json()["stocks"]
symbol = st.selectbox("Select Stock", stocks)

if st.button("Load Indicators"):
    res = requests.get(f"{API_URL}/stock_indicators/{symbol}")

    if res.status_code == 200:
        df = pd.DataFrame(res.json())
        df["Date"] = pd.to_datetime(df["Date"])

        st.subheader("📈 Price & EMA")
        st.line_chart(df.set_index("Date")[["Close", "EMA_20"]])

        st.subheader("📉 RSI")
        st.line_chart(df.set_index("Date")["RSI"])

        st.subheader("🌪 Volatility")
        st.line_chart(df.set_index("Date")["Volatility"])

        st.dataframe(df.tail(10))

    else:
        st.error("Failed to load indicator data")
