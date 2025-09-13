import os
import streamlit as st

# 🔹 MUST be first Streamlit command
st.set_page_config(page_title="Restaurant Back Office", page_icon="📊", layout="wide")

# ----- password gate (optional) -----
APP_PASSWORD = os.getenv("APP_PASSWORD")
if APP_PASSWORD:
    pwd = st.text_input("Enter password", type="password")
    if pwd != APP_PASSWORD:
        st.stop()
# -----------------------------------

st.title("📊 Restaurant Back Office — MVP")
st.write("Private app for tracking Sales, Expenses (COGS/Operating), Payroll, and Monthly P&L.")

with st.sidebar:
    st.header("Navigation")
    st.write("Dashboard (now) • Transactions (soon) • Payroll (soon) • Settings (soon)")

col1, col2, col3 = st.columns(3)
col1.metric("Revenue (net)", "€0")
col2.metric("COGS", "€0")
col3.metric("VAT Payable", "€0")

st.info("Skeleton running. Next steps: add data entry forms and a monthly P&L view.")


