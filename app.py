import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

from auth import login_screen

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="EquiAlgo – Client Report",
    layout="wide"
)

# -------------------------------------------------
# AUTH GATE
# -------------------------------------------------
if "is_authenticated" not in st.session_state:
    st.session_state["is_authenticated"] = False

if not st.session_state["is_authenticated"]:
    login_screen()
    st.stop()

# HARD DEBUG (remove later)
st.error(f"DEBUG → user_role = {st.session_state.get('user_role')}")

user_email = st.session_state.get("user_email")
login_time = st.session_state.get("login_time")

# =================================================
# ADMIN INTELLIGENCE PANEL
# =================================================
if st.session_state.get("user_role") == "admin":

    st.success("🧠 ADMIN INTELLIGENCE PANEL – ACTIVE")

    st.markdown("""
    ### 📊 System Intelligence Status
    - Login tracking: ✅ Enabled  
    - Session tracking: ✅ Enabled  
    - Role-based access: ✅ Enabled  
    - CSV audit trail: ✅ Enabled  
    - SEBI disclosure enforcement: ✅ Enabled  
    """)

    st.info("If you can see this box, admin rendering is 100% working.")

    try:
        users = pd.read_csv("data/users.csv")
    except Exception as e:
        st.error(f"Unable to load users.csv → {e}")
        users = None

    if users is not None and not users.empty:

        c1, c2, c3 = st.columns(3)
        c1.metric("👤 Unique Users", users["email"].nunique())
        c2.metric("📊 Total Logins", int(users["login_count"].sum()))
        c3.metric("🔥 Active Users", users[users["login_count"] > 0].shape[0])

        def intent(row):
            if row["login_count"] >= 10:
                return "🔥 HOT"
            elif row["login_count"] >= 3:
                return "🟡 WARM"
            else:
                return "❄️ COLD"

        users["Intent"] = users.apply(intent, axis=1)

        st.markdown("### 🔥 Client Intent Tracker")
        st.dataframe(
            users[
                [
                    "email",
                    "role",
                    "login_count",
                    "last_login",
                    "Intent",
                    "active_session_id",
                ]
            ],
            use_container_width=True
        )

    st.divider()

# -------------------------------------------------
# 🔐 TOP CONFIDENTIAL BANNER (WATERMARK #1)
# -------------------------------------------------
st.markdown(
    f"""
<div style="
    padding:12px;
    background:#fff4e5;
    border-radius:8px;
    border:1px solid #ffd8a8;
    font-weight:600;
">
🔒 <b>Confidential</b> | For: {user_email} |
Accessed: {login_time}
</div>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
if st.session_state["user_role"] == "admin":
    st.sidebar.success("🔐 Admin Mode")
else:
    st.sidebar.info("👤 Client Access")

# -------------------------------------------------
# LIVE REPORT
# -------------------------------------------------
st.markdown(
    """
<div style="padding:16px; border-radius:12px; background:#f5f9ff; border:1px solid #dbe7ff;">
<h3>🚀 Live Trades – Updated Automatically</h3>
<p>This report updates every evening after market close.</p>
</div>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------
# HTML REPORT WITH OVERLAY WATERMARK (WATERMARK #2)
# -------------------------------------------------
with st.expander("📌 View Live Trades & Strategy Report", expanded=True):
    try:
        with open("reports/EquiAlgo_Client_Report.html", "r", encoding="utf-8") as f:
            html = f.read()

        watermark_css = f"""
        <style>
        .equi-watermark {{
            position: fixed;
            top: 40%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-30deg);
            font-size: 28px;
            color: rgba(150,150,150,0.18);
            z-index: 9999;
            pointer-events: none;
            text-align: center;
            white-space: pre-line;
        }}
        </style>

        <div class="equi-watermark">
        CONFIDENTIAL\n{user_email}\n{login_time}
        </div>
        """

        st.components.v1.html(
            watermark_css + html,
            height=750,
            scrolling=True
        )

    except:
        st.info("Live report not available")

st.divider()

# -------------------------------------------------
# STRATEGY VS INDEX
# -------------------------------------------------
st.markdown("## 📊 Strategy vs Index Calculator")

investment = st.number_input(
    "Investment Amount (₹)",
    min_value=1000,
    step=1000,
    value=100000
)

benchmark_choice = st.selectbox(
    "Select Benchmark",
    ["NIFTY 50 PRICE", "NIFTY 200 PRICE"]
)

start_date = pd.to_datetime(st.date_input("Start Date", datetime(2021, 5, 5)))
end_date = pd.to_datetime(st.date_input("End Date", datetime(2025, 12, 31)))

strategy = pd.read_csv("data/strategy_equity.csv", parse_dates=["date"])

if benchmark_choice == "NIFTY 50 PRICE":
    benchmark = pd.read_csv("data/nifty50_price_fixed.csv", parse_dates=["date"])
    bench_name = "NIFTY 50"
else:
    benchmark = pd.read_csv("data/nifty200_price_fixed.csv", parse_dates=["date"])
    bench_name = "NIFTY 200"

strategy = strategy[(strategy["date"] >= start_date) & (strategy["date"] <= end_date)]
benchmark = benchmark[(benchmark["date"] >= start_date) & (benchmark["date"] <= end_date)]

df = pd.merge(strategy, benchmark, on="date", how="inner")

df["strategy_value"] = investment * df["equity"] / df["equity"].iloc[0]
df["benchmark_value"] = investment * df["close"] / df["close"].iloc[0]

fig = go.Figure()
fig.add_trace(go.Scatter(x=df["date"], y=df["strategy_value"], name="EquiAlgo"))
fig.add_trace(go.Scatter(x=df["date"], y=df["benchmark_value"], name=bench_name))

fig.update_layout(
    hovermode="x unified",
    height=500,
    xaxis_title="Date",
    yaxis_title="Portfolio Value (₹)"
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------
# 🔒 STICKY FOOTER WATERMARK (WATERMARK #3)
# -------------------------------------------------
st.markdown(
    f"""
<style>
.equi-footer {{
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background: rgba(255,244,229,0.95);
    border-top: 1px solid #ffd8a8;
    padding: 6px 12px;
    font-size: 12px;
    text-align: center;
    z-index: 10000;
}}
</style>

<div class="equi-footer">
🔒 Confidential • {user_email} • {login_time} • Redistribution prohibited
</div>
""",
    unsafe_allow_html=True,
)
