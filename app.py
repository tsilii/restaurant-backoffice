import os
import streamlit as st
import pandas as pd
from datetime import date

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Restaurant Back Office", page_icon="📊", layout="wide")
DATA_FILE = "transactions.csv"

# ---------------- PASSWORD (optional) ----------------
APP_PASSWORD = os.getenv("APP_PASSWORD")
if APP_PASSWORD:
    pwd = st.text_input("Enter password", type="password")
    if pwd != APP_PASSWORD:
        st.stop()

# ---------------- LOAD / SAVE DATA ----------------
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=[
            "date","type","channel","category","description",
            "gross","vat_rate","net","vat_amount"
        ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

# ---------------- SIDEBAR NAV ----------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Transactions"])  # later add Payroll, P&L

# ---------------- DASHBOARD PAGE ----------------
if page == "Dashboard":
    st.title("📊 Restaurant Back Office — Dashboard")

    if not df.empty:
        revenue = df.query("type == 'sale'")["net"].sum()
        cost_products = df.query("category == 'Cost of Products'")["net"].sum()
        operating_costs = df.query("category == 'Operating Costs'")["net"].sum()
        vat_payable = df.query("type == 'sale'")["vat_amount"].sum() - df.query("type == 'expense'")["vat_amount"].sum()
    else:
        revenue = cost_products = operating_costs = vat_payable = 0.0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Revenue (net)", f"€{revenue:,.2f}")
    col2.metric("Cost of Products", f"€{cost_products:,.2f}")
    col3.metric("Operating Costs", f"€{operating_costs:,.2f}")
    col4.metric("VAT Payable", f"€{vat_payable:,.2f}")

    st.info("Use the sidebar to add Transactions.")

# ---------------- TRANSACTIONS PAGE ----------------
elif page == "Transactions":
    st.title("🧾 Transactions")

    # ----- choice lists -----
    SALE_CHANNELS = ["Dine-in", "Takeaway", "Delivery"]

    EXPENSE_CATEGORIES = ["Cost of Products", "Operating Costs"]
    EXPENSE_SOURCES_COST = [
        "Supermarket", "Meat supplier", "Vegetable supplier", "Beverage supplier",
        "Bakery", "Seafood supplier", "Other"
    ]
    EXPENSE_SOURCES_OPER = [
        "Rent", "Electricity", "Water", "WiFi / Internet",
        "Delivery platform fees", "Marketing",
        "Repairs & Maintenance", "POS/Software", "Cleaning", "Other"
    ]

    with st.form("tx_form"):
        col1, col2 = st.columns(2)
        t_date = col1.date_input("Date", value=date.today())
        t_type = col2.selectbox("Type", ["sale", "expense"], index=0)

        # Dynamic fields based on type
        if t_type == "sale":
            category = "Sales"
            channel = st.selectbox("Sales channel", SALE_CHANNELS)
            desc = st.text_input("Description (optional)", placeholder="e.g., Daily Z-total")
        else:
            category = st.selectbox("Expense category", EXPENSE_CATEGORIES)
            if category == "Cost of Products":
                channel = st.selectbox("Supplier / Source", EXPENSE_SOURCES_COST)
            else:
                channel = st.selectbox("Expense type / Source", EXPENSE_SOURCES_OPER)
            desc = st.text_input("Description", placeholder="e.g., Flour 25kg, August rent")

        col5, col6 = st.columns(2)
        gross = col5.number_input("Gross Amount (€)", min_value=0.0, step=1.0, format="%.2f")
        vat_default = 13.0 if (t_type == "sale" and channel in ["Dine-in","Takeaway"]) else 24.0
        vat_rate = col6.number_input("VAT %", min_value=0.0, max_value=24.0, value=vat_default, step=1.0)

        submitted = st.form_submit_button("Add Transaction")

        if submitted:
            if gross <= 0:
                st.error("Enter a gross amount greater than 0.")
            else:
                net = round(gross / (1 + vat_rate/100), 2)
                vat_amount = round(gross - net, 2)
                new_row = pd.DataFrame([{
                    "date": t_date,
                    "type": t_type,
                    "channel": channel,        # Sales channel or expense source
                    "category": category,      # 'Sales' | 'Cost of Products' | 'Operating Costs'
                    "description": desc,
                    "gross": gross,
                    "vat_rate": vat_rate,
                    "net": net,
                    "vat_amount": vat_amount
                }])
                df = pd.concat([df, new_row], ignore_index=True)
                save_data(df)
                st.success("✅ Transaction added!")

    st.subheader("All Transactions")
    if not df.empty:
        show_df = df.copy()
        show_df.loc[show_df["type"]=="sale","channel"] = "Sales: " + show_df.loc[show_df["type"]=="sale","channel"]
        show_df.loc[show_df["type"]=="expense","channel"] = "Source: " + show_df.loc[show_df["type"]=="expense","channel"]
        st.dataframe(show_df)
    else:
        st.warning("No transactions yet.")
