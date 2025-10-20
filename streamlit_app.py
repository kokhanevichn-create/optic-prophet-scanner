import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd

st.set_page_config(page_title="Optic Prophet: VSRP Scanner", page_icon="🧠")
st.title("🧠 Optic Prophet: VSRP Scanner")
st.subheader("Your AI-Powered Volatility Skew Reaper")
st.markdown("Enter a valid ticker below to scan implied vs realized volatility.")
st.markdown("---")

# Input box
ticker = st.text_input("Enter Ticker (e.g. AAPL, TSLA, NVDA)")

# Interpretation logic
def interpret_ratio(ratio):
    if ratio is None:
        return ("⚠️ Not enough data to determine skew.", "gray")
    elif ratio < 0.7:
        return ("📉 Cheap Premium Detected — Consider Buying Options", "green")
    elif ratio > 1.3:
        return ("🔥 High Skew — Consider Selling Options or Going Short", "red")
    else:
        return ("🟡 Neutral Zone — No strong skew detected", "yellow")

# IV/RV logic
def get_iv_rv_ratio(ticker):
    try:
        data = yf.Ticker(ticker)
        hist = data.history(period="6mo")
        if hist.empty:
            return {"error": "No historical data found for this ticker."}

        hist_returns = hist["Close"].pct_change().dropna()
        rv = np.std(hist_returns) * np.sqrt(252)  # Annualized

        options_dates = data.options
        if not options_dates:
            return {"error": "No options data available."}

        front_month = options_dates[0]
        opt_chain = data.option_chain(front_month)
        calls = opt_chain.calls
        last_price = hist["Close"].iloc[-1]
        atm_call = calls.iloc[(calls['strike'] - last_price).abs().argsort()[:1]]

        if atm_call.empty:
            return {"error": "No ATM call found."}

        iv = atm_call['impliedVolatility'].values[0]
        ratio = iv / rv if rv > 0 else None
        bias_msg, bias_color = interpret_ratio(ratio)

        return {
            "Current Price": round(last_price, 2),
            "IV (ATM)": round(iv, 3),
            "RV (6mo)": round(rv, 3),
            "IV/RV Ratio": round(ratio, 2) if ratio else "N/A",
            "Bias": bias_msg,
            "SignalColor": bias_color
        }

    except Exception as e:
        return {"error": str(e)}

# Display output
if ticker:
    result = get_iv_rv_ratio(ticker.upper())
    if "error" in result:
        st.error(result["error"])
    else:
        st.markdown("### 📊 Volatility Snapshot")
        st.markdown(f"**Current Price:** {result['Current Price']}")
        st.markdown(f"**IV (ATM):** {result['IV (ATM)']}")
        st.markdown(f"**RV (6mo):** {result['RV (6mo)']}")
        st.markdown(f"**IV/RV Ratio:** {result['IV/RV Ratio']}")
        st.markdown("---")
        st.markdown("**Bias Engine Output:**")
        st.markdown(f":{result['SignalColor']}_circle: {result['Bias']}")
