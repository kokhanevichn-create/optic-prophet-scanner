import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd

st.set_page_config(page_title="Optic Prophet: VSRP Scanner", page_icon="🧠")
st.title("🧠 Optic Prophet: VSRP Scanner")
st.subheader("Your AI-Powered Volatility Skew Reaper")
st.markdown("Enter a valid ticker below to scan implied vs realized volatility.")
st.markdown("---")

ticker = st.text_input("Enter Ticker (e.g. AAPL, TSLA, NVDA)")

def get_iv_rv_ratio(ticker):
    try:
        data = yf.Ticker(ticker)
        hist = data.history(period="6mo")
        if hist.empty:
            return {"error": "No historical data found for this ticker."}

        hist_returns = hist["Close"].pct_change().dropna()
        rv = np.std(hist_returns) * np.sqrt(252)

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

        return {
            "Current Price": round(last_price, 2),
            "IV (ATM)": round(iv, 3),
            "RV (6mo)": round(rv, 3),
            "IV/RV Ratio": round(ratio, 2) if ratio else "N/A"
        }

    except Exception as e:
        return {"error": str(e)}

if ticker:
    result = get_iv_rv_ratio(ticker.upper())
    if "error" in result:
        st.error(result["error"])
    else:
        st.markdown("### 📊 Volatility Snapshot")
        for key, value in result.items():
            st.write(f"**{key}:** {value}")
