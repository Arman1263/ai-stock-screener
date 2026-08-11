import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

from engine.processor import MarketProcessor
from market_data.angel_auth import AngelAuth
from market_data.angel_provider import AngelOneProvider


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI/ML Stock Screener",
    page_icon="📈",
    layout="wide",
)


# ============================================================
# INITIALIZE SYSTEM
# ============================================================

@st.cache_resource
def initialize_system():

    auth = AngelAuth()

    print("Logging into Angel One...")

    auth.login()

    print("Angel One login successful.")

    provider = AngelOneProvider(auth)

    processor = MarketProcessor()

    provider.connect()

    return provider, processor


provider, processor = initialize_system()

# ============================================================
# MARKET FEED CONTROL
# ============================================================

if "feed_running" not in st.session_state:
    # The WebSocket connects asynchronously in a background thread.
    # provider.connected may still be False immediately after connect()
    # even though the connection is being established.
    st.session_state.feed_running = True

control_col1, control_col2 = st.columns([1, 4])

with control_col1:

    if st.session_state.feed_running:

        if st.button(
            "⏹ Stop Market Feed",
            use_container_width=True,
        ):
            provider.disconnect()
            st.session_state.feed_running = False
            st.rerun()

    else:

        if st.button(
            "▶ Start Market Feed",
            use_container_width=True,
        ):
            provider.connect()
            st.session_state.feed_running = True
            st.rerun()

with control_col2:

    if st.session_state.feed_running:
        st.success("🟢 Market feed running • Data source: Angel One")
    else:
        st.warning("🔴 Market feed stopped")


# ============================================================
# HEADER
# ============================================================

st.title("AI/ML Stock Market Screening & Analysis")

st.caption(
    "Real-time stock screening, SMMA crossover detection "
    "and machine-learning trade analysis"
)


# ============================================================
# LIVE DASHBOARD
# ============================================================

@st.fragment(run_every=1)
def live_dashboard():

    if not st.session_state.feed_running:
        st.info(
            "Market feed is stopped. "
            "Click 'Start Market Feed' to resume live data."
        )
        return

    ticks = provider.generate_ticks()

    screened_rows = []

    # --------------------------------------------------------
    # PROCESS MARKET DATA
    # --------------------------------------------------------

    for tick in ticks:

        result = processor.process_tick(tick)

        # ----------------------------------------------------
        # SCREENED STOCKS
        # ----------------------------------------------------

        if result["passes_filter"]:

            screened_rows.append(
                {
                    "Stock": result["symbol"],
                    "LTP": result["ltp"],

                    "Bid Price": result["bid_price"],
                    "Bid Qty": result["bid_quantity"],

                    "Ask Price": result["ask_price"],
                    "Ask Qty": result["ask_quantity"],

                    "SMMA 20": (
                        round(result["smma20"], 2)
                        if result["smma20"] is not None
                        else None
                    ),

                    "SMMA 120": (
                        round(result["smma120"], 2)
                        if result["smma120"] is not None
                        else None
                    ),

                    "ETQ 5m": result["etq_5m"],
                    "ETQ 20m": result["etq_20m"],
                    "ETQ 60m": result["etq_60m"],

                    "Avg LTP 20m": (
                        round(result["avg_ltp_20m"], 2)
                        if result["avg_ltp_20m"] is not None
                        else None
                    ),

                    "Avg LTP 60m": (
                        round(result["avg_ltp_60m"], 2)
                        if result["avg_ltp_60m"] is not None
                        else None
                    ),

                    "Signal": result["signal"] or "-",
                }
            )

    # ========================================================
    # SYSTEM STATUS
    # ========================================================

    if provider.connected:

        st.success(
            "Market feed active • "
            "Tracking 500 NSE stocks • "
            "Data source: Angel One"
        )

    else:

        st.error(
            "Angel One market feed disconnected."
        )

    # ========================================================
    # SUMMARY METRICS
    # ========================================================

    signals = processor.get_signal_history()
    trades = processor.get_trade_history()

    total_trades = len(trades)

    profitable_trades = sum(
        1
        for trade in trades
        if trade["profitable"]
    )

    total_pnl = sum(
        trade["pnl"]
        for trade in trades
    )

    win_rate = (
        profitable_trades / total_trades * 100
        if total_trades
        else 0
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Screened Stocks",
        len(screened_rows),
    )

    col2.metric(
        "Crossovers",
        len(signals),
    )

    col3.metric(
        "Completed Trades",
        total_trades,
    )

    col4.metric(
        "Win Rate",
        f"{win_rate:.1f}%",
    )

    col5.metric(
        "Total P/L",
        f"₹{total_pnl:.2f}",
    )

    st.divider()

    # ========================================================
    # LIVE STOCK SCREENING
    # ========================================================

    st.subheader("Live Stock Screening")

    if screened_rows:

        df = pd.DataFrame(screened_rows)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No stocks currently satisfy the "
            "price and liquidity filters."
        )

    st.divider()

    # ========================================================
    # LATEST AI SIGNAL
    # ========================================================

    st.subheader("Latest AI Analysis")

    if signals:

        latest = signals[0]

        ai1, ai2, ai3, ai4 = st.columns(4)

        ai1.metric(
            "Stock",
            latest["symbol"],
        )

        ai2.metric(
            "Signal",
            latest["signal"],
        )

        ai3.metric(
            "Probability",
            (
                f"{latest['probability']:.2f}%"
                if latest["probability"] is not None
                else "N/A"
            ),
        )

        ai4.metric(
            "Decision",
            latest["decision"],
        )

        st.write(
            f"**Crossover Price:** "
            f"₹{latest['price']:.2f}"
        )

        st.write("**Quantitative Observations**")

        if latest["reasons"]:

            for reason in latest["reasons"]:
                st.write(f"• {reason}")

        else:

            st.write(
                "No explanation available."
            )

    else:

        st.info(
            "Waiting for an SMMA crossover..."
        )

    st.divider()

    # ========================================================
    # SIGNAL HISTORY
    # ========================================================

    st.subheader("Signal History")

    if signals:

        signal_rows = []

        for signal in signals:

            signal_rows.append(
                {
                    "Time": signal["timestamp"].strftime(
                        "%H:%M:%S"
                    ),

                    "Stock": signal["symbol"],

                    "Signal": signal["signal"],

                    "Price": round(
                        signal["price"],
                        2,
                    ),

                    "Probability": (
                        round(
                            signal["probability"],
                            2,
                        )
                        if signal["probability"] is not None
                        else None
                    ),

                    "Decision": signal["decision"],
                }
            )

        signal_df = pd.DataFrame(
            signal_rows
        )

        st.dataframe(
            signal_df,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No crossover signals recorded yet."
        )

    st.divider()

    # ========================================================
    # COMPLETED TRADE HISTORY
    # ========================================================

    st.subheader("Completed Trade History")

    if trades:

        trade_rows = []

        for trade in trades:

            trade_rows.append(
                {
                    "Stock": trade["symbol"],

                    "Direction": trade["direction"],

                    "Entry Time": trade[
                        "entry_time"
                    ].strftime("%H:%M:%S"),

                    "Exit Time": trade[
                        "exit_time"
                    ].strftime("%H:%M:%S"),

                    "Entry Price": round(
                        trade["entry_price"],
                        2,
                    ),

                    "Exit Price": round(
                        trade["exit_price"],
                        2,
                    ),

                    "P/L": round(
                        trade["pnl"],
                        2,
                    ),

                    "Result": (
                        "PROFIT"
                        if trade["profitable"]
                        else "LOSS"
                    ),
                }
            )

        trade_df = pd.DataFrame(
            trade_rows
        )

        st.dataframe(
            trade_df,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "Waiting for completed trades..."
        )


# ============================================================
# START DASHBOARD
# ============================================================

live_dashboard()