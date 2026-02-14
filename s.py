import streamlit as st
import pandas as pd
import numpy as np
import time

# ----------------- CONFIG -----------------
st.set_page_config(page_title="Mini Stock Exchange", layout="wide")

# ----------------- SESSION STATE -----------------
if "cash" not in st.session_state:
    st.session_state.cash = 100000
    st.session_state.portfolio = {}
    st.session_state.prices = {
        "RELIANCE": 2500,
        "TCS": 3800,
        "INFY": 1500,
        "HDFCBANK": 1600,
        "SBIN": 600
    }

# ----------------- PRICE SIMULATION -----------------
def update_prices():
    for stock in st.session_state.prices:
        change = np.random.uniform(-1.5, 1.5)
        st.session_state.prices[stock] *= (1 + change / 100)

# ----------------- UI -----------------
st.title("📈 Mini Stock Exchange Simulator")

update_prices()

# ----------------- MARKET TABLE -----------------
market_df = pd.DataFrame({
    "Stock": st.session_state.prices.keys(),
    "Price (₹)": [round(v, 2) for v in st.session_state.prices.values()]
})

st.subheader("📊 Market Prices")
st.dataframe(market_df, use_container_width=True)

# ----------------- TRADE PANEL -----------------
st.subheader("💹 Trade")

col1, col2, col3 = st.columns(3)

with col1:
    stock = st.selectbox("Select Stock", list(st.session_state.prices.keys()))

with col2:
    qty = st.number_input("Quantity", min_value=1, step=1)

with col3:
    trade_type = st.radio("Action", ["Buy", "Sell"])

price = st.session_state.prices[stock]
total = price * qty

if st.button("Execute Trade"):
    if trade_type == "Buy":
        if st.session_state.cash >= total:
            st.session_state.cash -= total
            st.session_state.portfolio[stock] = st.session_state.portfolio.get(stock, 0) + qty
            st.success("✅ Buy Order Executed")
        else:
            st.error("❌ Insufficient Balance")

    else:
        if st.session_state.portfolio.get(stock, 0) >= qty:
            st.session_state.cash += total
            st.session_state.portfolio[stock] -= qty
            st.success("✅ Sell Order Executed")
        else:
            st.error("❌ Not enough shares")

# ----------------- PORTFOLIO -----------------
st.subheader("📂 Portfolio")

portfolio_df = pd.DataFrame([
    {"Stock": s, "Quantity": q, "Value (₹)": round(q * st.session_state.prices[s], 2)}
    for s, q in st.session_state.portfolio.items()
])

st.dataframe(portfolio_df, use_container_width=True)

# ----------------- CASH -----------------
st.metric("💰 Available Cash", f"₹{st.session_state.cash:,.2f}")

st.caption("🔄 Prices update every refresh (simulated exchange)")
