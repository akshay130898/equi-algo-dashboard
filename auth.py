import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path

USERS_FILE = Path("data/users.csv")

# -------------------------------------------------
# LOAD USERS
# -------------------------------------------------
def load_users():
    if not USERS_FILE.exists():
        st.error("users.csv not found")
        st.stop()

    users = pd.read_csv(USERS_FILE)

    required_cols = [
        "email",
        "password",
        "role",
        "is_active",
        "login_count",
        "last_login",
        "active_session_id",
        "session_last_seen",
    ]

    for col in required_cols:
        if col not in users.columns:
            st.error(f"Missing column in users.csv: {col}")
            st.stop()

    # Normalize data (CRITICAL)
    users["email"] = users["email"].astype(str).str.strip().str.lower()
    users["password"] = users["password"].astype(str).str.strip()
    users["role"] = users["role"].astype(str).str.strip().str.lower()
    users["is_active"] = users["is_active"].astype(str).str.strip().str.upper()
    users["login_count"] = users["login_count"].fillna(0).astype(int)

    return users


# -------------------------------------------------
# SAVE USERS
# -------------------------------------------------
def save_users(users):
    users.to_csv(USERS_FILE, index=False)


# -------------------------------------------------
# LOGIN SCREEN
# -------------------------------------------------
def login_screen():
    st.markdown("## 🔐 EquiAlgo Secure Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    st.markdown("### Mandatory Risk & Regulatory Disclosure")
    st.markdown(
        """
- Educational & informational only  
- No investment advice  
- Past performance is not indicative of future returns  
- Reports must not be forwarded or redistributed  
- User bears full market risk  
"""
    )

    agree = st.checkbox("I Understand & Agree to the disclosure")

    if not agree:
        st.warning("Please accept the disclosure to continue")
        return

    if st.button("Login", use_container_width=True):
        users = load_users()

        email_clean = email.strip().lower()
        password_clean = password.strip()

        match = users[
            (users["email"] == email_clean)
            & (users["password"] == password_clean)
            & (users["is_active"] == "TRUE")
        ]

        if match.empty:
            st.error("Invalid credentials")
            return

        # ---- SUCCESSFUL LOGIN ----
        user = match.iloc[0]

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        users.loc[users["email"] == email_clean, "login_count"] += 1
        users.loc[users["email"] == email_clean, "last_login"] = now
        users.loc[users["email"] == email_clean, "active_session_id"] = st.session_state.get("_session_id", "active")
        users.loc[users["email"] == email_clean, "session_last_seen"] = now

        save_users(users)

        st.session_state["is_authenticated"] = True
        st.session_state["user_email"] = email_clean
        st.session_state["user_role"] = user["role"]
        st.session_state["login_time"] = now

        st.rerun()
