import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd

st.set_page_config(page_title="Optic Prophet: VSRP Scanner", page_icon="🧠")
st.title("🧠 Optic Prophet: VSRP Scanner")
st.subheader("Your AI-Powered Volatility Skew Reaper")
st.markdown("---")

ticker = st.text_input("Enter Ticker (e.g. AAPL, TSLA, NVDA)")

def interpret_bias(ratio):
    if ratio is None:
        return ("⚠️ Skew Undetectable", "gray")
    elif ratio < 0.7:
        return ("📉 Cheap Premium — Buy Zone", "green")
    elif ratio > 1.3:
        return ("🔥 High Skew — Sell Zone", "red")
    else:
        return ("🟡 Neutral Skew", "yellow")

def expected_move(price, iv, days):
    return round(price * iv * np.sqrt(days / 365), 2)

def get_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="6mo")
        if hist.empty:
            return {"error": "No historical data found."}

        returns = hist["Close"].pct_change().dropna()
        rv = np.std(returns) * np.sqrt(252)
        last_price = hist["Close"].iloc[-1]

        options_dates = stock.options
        if not options_dates:
            return {"error": "No options available."}

        opt_chain = stock.option_chain(options_dates[0])
        calls = opt_chain.calls
        puts = opt_chain.puts

        atm_call = calls.iloc[(calls['strike'] - last_price).abs().argsort()[:1]]
        if atm_call.empty:
            return {"error": "No ATM option found."}

        iv = atm_call['impliedVolatility'].values[0]
        atm_strike = atm_call['strike'].values[0]
        volume = atm_call['volume'].values[0]
        oi = atm_call['openInterest'].values[0]

        ratio = iv / rv if rv else None
        bias_msg, bias_color = interpret_bias(ratio)

        return {
            "Price": round(last_price, 2),
            "ATM Strike": round(atm_strike, 2),
            "IV": round(iv, 3),
            "RV": round(rv, 3),
            "IV/RV Ratio": round(ratio, 2) if ratio else "N/A",
            "Expected Move (1D)": expected_move(last_price, iv, 1),
            "Expected Move (1W)": expected_move(last_price, iv, 5),
            "Expected Move (1M)": expected_move(last_price, iv, 21),
            "Volume (ATM)": volume,
            "OI (ATM)": oi,
            "Bias": bias_msg,
            "Color": bias_color
        }

    except Exception as e:
        return {"error": str(e)}

if ticker:
    result = get_data(ticker.upper())
    if "error" in result:
        st.error(result["error"])
    else:
        st.markdown("### 📊 Volatility Snapshot")
        st.write(f"**Current Price:** ${result['Price']}")
        st.write(f"**ATM Strike:** {result['ATM Strike']}")
        st.write(f"**IV (ATM):** {result['IV']}")
        st.write(f"**RV (6mo):** {result['RV']}")
        st.write(f"**IV/RV Ratio:** {result['IV/RV Ratio']}")
        st.markdown("---")

        st.markdown("### 🔭 Expected Move Projections")
        st.write(f"1 Day: ±${result['Expected Move (1D)']}")
        st.write(f"1 Week: ±${result['Expected Move (1W)']}")
        st.write(f"1 Month: ±${result['Expected Move (1M)']}")
        st.markdown("---")

        st.markdown("### 🧠 Bias Engine")
        st.markdown(f":{result['Color']}_circle: {result['Bias']}")
        st.markdown("---")

        st.markdown("### 📈 Option Sentiment (ATM Call)")
        st.write(f"Volume: {result['Volume (ATM)']}")
        st.write(f"Open Interest: {result['OI (ATM)']}")
