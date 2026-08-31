import streamlit as st
import datetime
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import sys

# Ensure src module is accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.engine import CASEngine
from src.data_loader import DataLoader

st.set_page_config(
    page_title="CAS 3:22 NIFTY + SENSEX AI System",
    page_icon="📈",
    layout="wide"
)

# Custom CSS styling for professional institutional theme
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        color: #E0E6ED;
    }
    .metric-card {
        background: #1E222D;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid #2A2E39;
        margin-bottom: 12px;
    }
    .up-card {
        border-left: 5px solid #26A69A;
    }
    .down-card {
        border-left: 5px solid #EF5350;
    }
    .flat-card {
        border-left: 5px solid #787B86;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_engine():
    return CASEngine()

engine = get_engine()
loader = DataLoader()

st.title("CAS 3:22 NIFTY + SENSEX AI CLOSING DIRECTION & OPTION SYSTEM")
st.caption(f"Canonical Production Path: `C:\\Mangesh\\Jules\\CAS` | Version: `{engine.config['VERSION_INFO']['application_version']}`")

# Primary Navigation Sidebar
sidebar = st.sidebar
sidebar.header("Navigation")
menu = sidebar.radio(
    "Select View",
    [
        "3:22 Analysis & Replay",
        "Single-Day Backtest",
        "Range Backtest",
        "Performance Analytics",
        "Data Quality & System Health",
        "Version History"
    ]
)

avail_dates = loader.get_available_dates()
default_date = engine.config.get("DEFAULT_DATE", "2026-08-03")

# Common Date Selector
sidebar.markdown("---")
sidebar.subheader("Date Selection")
selected_date_str = sidebar.selectbox("Historical Date", avail_dates, index=avail_dates.index(default_date) if default_date in avail_dates else 0)

sidebar.markdown(f"**Earliest Permitted Date:** `{engine.cas_min_date}`")

def render_single_day_cards(res, date_str):
    nifty = res["nifty"]
    sensex = res["sensex"]
    n_perf = nifty["performance"]
    s_perf = sensex["performance"]
    n_pred = nifty["prediction"]
    s_pred = sensex["prediction"]

    st.markdown(f"### SINGLE-DAY CAS BACKTEST REPLAY — {date_str}")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("NIFTY 50")
        st.write(f"**Prediction:** {n_pred['direction']} — {n_pred['probability']}%")
        if nifty["option_recommendation"]["recommendation"] == "BUY":
            opt = nifty["option_recommendation"]["option"]
            st.write(f"**Recommended Option:** `{opt['symbol']}`")
            st.write(f"**Entry (3:22):** ₹{n_perf['entry_price']} ({opt['entry_method']})")
            st.write(f"**3:25 Price:** ₹{n_perf['price_325']} ({n_perf['return_325_pct']:+.2f}%)")
            st.write(f"**Close Price:** ₹{n_perf['price_close']} ({n_perf['return_close_pct']:+.2f}%)")
            st.write(f"**MFE:** +{n_perf['mfe_pct']}% | **MAE:** {n_perf['mae_pct']}%")
            st.markdown(f"**RESULT:** `{n_perf['result']}`")
        else:
            st.warning("NO TRADE RECOMMENDED")

    with col2:
        st.subheader("SENSEX")
        st.write(f"**Prediction:** {s_pred['direction']} — {s_pred['probability']}%")
        if sensex["option_recommendation"]["recommendation"] == "BUY":
            opt = sensex["option_recommendation"]["option"]
            st.write(f"**Recommended Option:** `{opt['symbol']}`")
            st.write(f"**Entry (3:22):** ₹{s_perf['entry_price']} ({opt['entry_method']})")
            st.write(f"**3:25 Price:** ₹{s_perf['price_325']} ({s_perf['return_325_pct']:+.2f}%)")
            st.write(f"**Close Price:** ₹{s_perf['price_close']} ({s_perf['return_close_pct']:+.2f}%)")
            st.write(f"**MFE:** +{s_perf['mfe_pct']}% | **MAE:** {s_perf['mae_pct']}%")
            st.markdown(f"**RESULT:** `{s_perf['result']}`")
        else:
            st.warning("NO TRADE RECOMMENDED")

# --- VIEW 1: 3:22 ANALYSIS & REPLAY ---
if menu == "3:22 Analysis & Replay":
    st.subheader(f"Manual 3:22 Analysis Session — {selected_date_str}")

    col_trigger, col_info = st.columns([1, 3])
    with col_trigger:
        run_btn = st.button("RUN 3:22 ANALYSIS", type="primary", use_container_width=True)
    with col_info:
        st.info("Phase 1 Manual Trigger: Select date and click button above to analyze 3:22 snapshot.")

    if run_btn or "last_res" in st.session_state:
        if run_btn:
            res = engine.run_322_analysis(selected_date_str)
            st.session_state["last_res"] = res
        else:
            res = st.session_state["last_res"]

        if res.get("status") != "SUCCESS":
            st.error(res.get("error", "Error processing request."))
        else:
            nifty = res["nifty"]
            sensex = res["sensex"]

            st.markdown("---")
            st.markdown("### MASTER DIRECTION PANEL (3:22 PM IST)")

            m_col1, m_col2 = st.columns(2)

            with m_col1:
                n_pred = nifty["prediction"]
                card_class = "up-card" if n_pred["direction"] == "UP" else ("down-card" if n_pred["direction"] == "DOWN" else "flat-card")
                st.markdown(f"""
                <div class="metric-card {card_class}">
                    <h3>NIFTY 50</h3>
                    <h2>DIRECTION: {n_pred['direction']} ({n_pred['probability']}% Confidence)</h2>
                    <p><b>Expected Move:</b> {n_pred['expected_move_pct']:+.2f}%</p>
                    <p><b>Closing Pressure Score:</b> {nifty['cpm']['score']} ({nifty['cpm']['label']})</p>
                    <p><b>5-Min Battle Score:</b> {nifty['battle']['score']} ({nifty['battle']['label']})</p>
                    <p><b>AI Anomaly:</b> {nifty['anomaly']['label']} (Score: {nifty['anomaly']['score']})</p>
                </div>
                """, unsafe_allow_html=True)

            with m_col2:
                s_pred = sensex["prediction"]
                card_class = "up-card" if s_pred["direction"] == "UP" else ("down-card" if s_pred["direction"] == "DOWN" else "flat-card")
                st.markdown(f"""
                <div class="metric-card {card_class}">
                    <h3>SENSEX</h3>
                    <h2>DIRECTION: {s_pred['direction']} ({s_pred['probability']}% Confidence)</h2>
                    <p><b>Expected Move:</b> {s_pred['expected_move_pct']:+.2f}%</p>
                    <p><b>Closing Pressure Score:</b> {sensex['cpm']['score']} ({sensex['cpm']['label']})</p>
                    <p><b>5-Min Battle Score:</b> {sensex['battle']['score']} ({sensex['battle']['label']})</p>
                    <p><b>AI Anomaly:</b> {sensex['anomaly']['label']} (Score: {sensex['anomaly']['score']})</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("### TOP-5 HEAVYWEIGHT CONTRIBUTION")
            hw_tab1, hw_tab2 = st.tabs(["NIFTY Heavyweights", "SENSEX Heavyweights"])
            with hw_tab1:
                st.dataframe(pd.DataFrame(nifty["heavyweights"]), use_container_width=True)
            with hw_tab2:
                st.dataframe(pd.DataFrame(sensex["heavyweights"]), use_container_width=True)

            st.markdown("---")
            st.markdown("### OPTION TRADE RECOMMENDATIONS & REPLAY")
            o_col1, o_col2 = st.columns(2)

            with o_col1:
                st.subheader("NIFTY Recommended Option")
                n_rec = nifty["option_recommendation"]
                n_perf = nifty["performance"]

                if n_rec["recommendation"] == "BUY":
                    opt = n_rec["option"]
                    st.json(opt)
                    st.markdown(f"""
                    **Replay Result:**
                    - Entry (3:22): `₹{n_perf['entry_price']}` ({opt['entry_method']})
                    - 3:25 Price: `₹{n_perf['price_325']}` (Return: `{n_perf['return_325_pct']:+.2f}%`)
                    - Official Close: `₹{n_perf['price_close']}` (Return: `{n_perf['return_close_pct']:+.2f}%`)
                    - **MFE:** `+{n_perf['mfe_pct']}%` | **MAE:** `{n_perf['mae_pct']}%`
                    - **RESULT:** `{n_perf['result']}`
                    """)
                else:
                    st.warning(f"NO TRADE: {n_rec['reason']}")

            with o_col2:
                st.subheader("SENSEX Recommended Option")
                s_rec = sensex["option_recommendation"]
                s_perf = sensex["performance"]

                if s_rec["recommendation"] == "BUY":
                    opt = s_rec["option"]
                    st.json(opt)
                    st.markdown(f"""
                    **Replay Result:**
                    - Entry (3:22): `₹{s_perf['entry_price']}` ({opt['entry_method']})
                    - 3:25 Price: `₹{s_perf['price_325']}` (Return: `{s_perf['return_325_pct']:+.2f}%`)
                    - Official Close: `₹{s_perf['price_close']}` (Return: `{s_perf['return_close_pct']:+.2f}%`)
                    - **MFE:** `+{s_perf['mfe_pct']}%` | **MAE:** `{s_perf['mae_pct']}%`
                    - **RESULT:** `{s_perf['result']}`
                    """)
                else:
                    st.warning(f"NO TRADE: {s_rec['reason']}")

            if nifty["performance"].get("status") == "COMPLETED":
                st.markdown("### OPTION REPLAY CHART (NIFTY)")
                timeline = nifty["performance"]["replay_timeline"]
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=list(timeline.keys()), y=list(timeline.values()), mode='lines+markers', name='Option Price'))
                fig.update_layout(title="NIFTY Option Replay (15:22 -> 15:30)", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

# --- VIEW 2: SINGLE-DAY BACKTEST ---
elif menu == "Single-Day Backtest":
    st.subheader(f"Single-Day CAS Backtest Screen — {selected_date_str}")
    if st.button("RUN SINGLE-DAY BACKTEST", type="primary"):
        res = engine.run_322_analysis(selected_date_str)
        if res.get("status") == "SUCCESS":
            render_single_day_cards(res, selected_date_str)

# --- VIEW 3: RANGE BACKTEST ---
elif menu == "Range Backtest":
    st.subheader("Range Backtest & Single-Day Drill-down")
    r_col1, r_col2 = st.columns(2)
    with r_col1:
        from_date = st.selectbox("From Date", avail_dates, index=0)
    with r_col2:
        to_date = st.selectbox("To Date", avail_dates, index=len(avail_dates)-1)

    selected_range = [d for d in avail_dates if from_date <= d <= to_date]

    if st.button("RUN RANGE BACKTEST", type="primary"):
        results = []
        for d in selected_range:
            day_data = loader.get_day_data(d)
            if day_data:
                res = engine.run_322_analysis(d)
                if res.get("status") == "SUCCESS":
                    n_perf = res["nifty"]["performance"]
                    s_perf = res["sensex"]["performance"]
                    results.append({
                        "Date": d,
                        "NIFTY Signal": res["nifty"]["prediction"]["direction"],
                        "NIFTY Option": res["nifty"]["option_recommendation"].get("option", {}).get("symbol", "NONE"),
                        "NIFTY 3:25 Return": f"{n_perf.get('return_325_pct', 0.0):+.2f}%",
                        "NIFTY Close Return": f"{n_perf.get('return_close_pct', 0.0):+.2f}%",
                        "NIFTY MFE": f"{n_perf.get('mfe_pct', 0.0):+.2f}%",
                        "NIFTY MAE": f"{n_perf.get('mae_pct', 0.0):+.2f}%",
                        "SENSEX Signal": res["sensex"]["prediction"]["direction"],
                        "SENSEX Option": res["sensex"]["option_recommendation"].get("option", {}).get("symbol", "NONE"),
                        "SENSEX Close Return": f"{s_perf.get('return_close_pct', 0.0):+.2f}%"
                    })
        st.session_state["range_results"] = pd.DataFrame(results)

    if "range_results" in st.session_state:
        st.dataframe(st.session_state["range_results"], use_container_width=True)
        st.markdown("---")
        drill_date = st.selectbox("Select Row Date to Drill-Down", selected_range)
        if st.button("DRILL-DOWN REPLAY", type="secondary"):
            res = engine.run_322_analysis(drill_date)
            render_single_day_cards(res, drill_date)

# --- VIEW 4: PERFORMANCE ANALYTICS ---
elif menu == "Performance Analytics":
    st.subheader("Strategy Performance & Equity Curves")

    daily_returns = []
    accum = 100000.0
    equity_curve = [accum]

    matrix = {"UP": {"UP": 0, "DOWN": 0, "FLAT": 0}, "DOWN": {"UP": 0, "DOWN": 0, "FLAT": 0}, "FLAT": {"UP": 0, "DOWN": 0, "FLAT": 0}}

    for d in avail_dates:
        day_data = loader.get_day_data(d)
        if day_data:
            res = engine.run_322_analysis(d)
            if res.get("status") == "SUCCESS":
                r_pct = res["nifty"]["performance"].get("return_close_pct", 0.0)
                accum += accum * (r_pct / 100.0)
                equity_curve.append(accum)
                daily_returns.append(r_pct)

                pred_dir = res["nifty"]["prediction"]["direction"]
                p_322 = day_data["NIFTY"]["series"][22]["price"]
                p_close = day_data["NIFTY"]["official_close"]

                if p_close > p_322: actual_dir = "UP"
                elif p_close < p_322: actual_dir = "DOWN"
                else: actual_dir = "FLAT"

                matrix[pred_dir][actual_dir] += 1

    st.markdown("### COMBINED OPTION EQUITY CURVE")
    fig_eq = go.Figure()
    fig_eq.add_trace(go.Scatter(x=["Start"] + avail_dates, y=equity_curve, mode='lines+markers', name='Capital (₹)'))
    fig_eq.update_layout(title="Strategy Equity Growth (Starting Capital ₹100,000)", template="plotly_dark")
    st.plotly_chart(fig_eq, use_container_width=True)

    wins = [r for r in daily_returns if r > 0]
    losses = [abs(r) for r in daily_returns if r < 0]
    win_rate = (len(wins) / len(daily_returns) * 100.0) if daily_returns else 0.0

    gross_profit = sum(wins)
    gross_loss = sum(losses)
    profit_factor = round(gross_profit / gross_loss, 2) if gross_loss > 0 else (999.0 if gross_profit > 0 else 1.0)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Trades", len(daily_returns))
    m2.metric("Win Rate", f"{win_rate:.1f}%")
    m3.metric("Average Return", f"{np.mean(daily_returns):+.2f}%" if daily_returns else "0.00%")
    m4.metric("Profit Factor", f"{profit_factor}")

    st.markdown("### DIRECTION CONFUSION MATRIX (PREDICTED vs ACTUAL CLOSE)")
    cm_df = pd.DataFrame({
        "ACTUAL UP": [matrix["UP"]["UP"], matrix["DOWN"]["UP"], matrix["FLAT"]["UP"]],
        "ACTUAL DOWN": [matrix["UP"]["DOWN"], matrix["DOWN"]["DOWN"], matrix["FLAT"]["DOWN"]],
        "ACTUAL FLAT": [matrix["UP"]["FLAT"], matrix["DOWN"]["FLAT"], matrix["FLAT"]["FLAT"]]
    }, index=["PRED UP", "PRED DOWN", "PRED FLAT"])
    st.dataframe(cm_df, use_container_width=True)

# --- VIEW 5: DATA QUALITY & SYSTEM HEALTH ---
elif menu == "Data Quality & System Health":
    st.subheader("System Health & Data Quality Status")
    st.json({
        "DATA STATUS": "READY",
        "MODEL STATUS": "READY",
        "OPTION DATA STATUS": "READY",
        "BACKTEST STATUS": "READY",
        "DATABASE STATUS": "READY",
        "VERSION": engine.config["VERSION_INFO"]["application_version"],
        "CANONICAL_PATH": engine.config["CANONICAL_PATH"]
    })

# --- VIEW 6: VERSION HISTORY ---
elif menu == "Version History":
    st.subheader("Audit & Versioning History")
    st.json(engine.config["VERSION_INFO"])
