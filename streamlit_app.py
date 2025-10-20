import streamlit as st
import yfinance as yf
import numpy as np

st.set_page_config(page_title="Optic Prophet: VSRP Scanner", page_icon="🧠")
st.title("🧠 Optic Prophet: VSRP Scanner")
st.subheader("Your AI-Powered Volatility Skew Reaper")
st.markdown("---")

ticker = st.text_input("Enter Ticker (e.g. AAPL, TSLA, NVDA)")

def interpret_ratio(ratio):
    if ratio is None:
        return ("⚠️ Not enough data to determine skew.", "gray")
    elif ratio < 0.7:
        return ("📉 Cheap Premium Detected — Consider Buying Options", "green")
    elif ratio > 1.3:
        return ("🔥 High Skew — Consider Selling Options or Going Short", "red")
    else:
        return ("🟡 Neutral Zone — No strong skew detected", "yellow")

def calculate_expected_move(price, iv, days):
    return round(price * iv * np.sqrt(days / 365), 2)

def get_iv_rv_data(ticker):
    try:
        data = yf.Ticker(ticker)
        hist = data.history(period="6mo")
        if hist.empty:
            return {"error": "No historical price data found."}

        hist_returns = hist["Close"].pct_change().dropna()
        rv = np.std(hist_returns) * np.sqrt(252)
        options_dates = data.options
        if not options_dates:
            return {"error": "No options data found."}

        front_month = options_dates[0]
        opt_chain = data.option_chain(front_month)
        calls = opt_chain.calls
        last_price = hist["Close"].iloc[-1]
        atm_call = calls.iloc[(calls['strike'] - last_price).abs().argsort()[:1]]
        if atm_call.empty:
            return {"error": "No ATM call found."}

        iv = atm
