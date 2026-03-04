import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import os
from utils.export_pdf import export_pdf

st.set_page_config(page_title="UPI Bank Dashboard", layout="wide")
st.title("UPI Bank Statement Insights Dashboard")

file_path = "data/bank_statement.csv"

if os.path.exists(file_path):
    if st.button("Delete Existing CSV File"):
        os.remove(file_path)
        st.success("CSV file deleted. Upload a new one below.")

uploaded = st.file_uploader("Upload your bank statement CSV", type=["csv"])
if uploaded:
    with open(file_path, "wb") as f:
        f.write(uploaded.getbuffer())
    st.success("File uploaded.")

if os.path.exists(file_path):
    raw_df = pd.read_csv(file_path, skiprows=17)
    raw_df.columns = ["Date", "Details", "Ref No", "Debit", "Credit", "Balance"]
    raw_df = raw_df.dropna(subset=["Date", "Details", "Balance"])
    raw_df["Date"] = pd.to_datetime(raw_df["Date"], errors="coerce")
    raw_df = raw_df.dropna(subset=["Date"])
    for col in ["Debit", "Credit", "Balance"]:
        raw_df[col] = pd.to_numeric(raw_df[col], errors="coerce")

    df = raw_df.copy()
else:
    st.warning("Please upload your bank statement.")
    st.stop()

st.sidebar.header("📆 Date Filter")
date_range = st.sidebar.date_input("Date Range", [df["Date"].min(), df["Date"].max()])
df = df[(df["Date"].dt.date >= date_range[0]) & (df["Date"].dt.date <= date_range[1])]

with st.sidebar.expander("More Filters"):
    search = st.text_input("Filter by Merchant/Details")
    if search:
        df = df[df["Details"].str.contains(search, case=False)]

total_spend = df["Debit"].sum()
total_income = df["Credit"].sum()
transactions = df.shape[0]

col1, col2, col3 = st.columns(3)
col1.metric("💸 Total Spend", f"₹{total_spend:.2f}")
col2.metric("💰 Total Income", f"₹{total_income:.2f}")
col3.metric("🔁 Total Transactions", transactions)

st.subheader("📆 Monthly Spending Trend")
monthly = df.groupby(df["Date"].dt.to_period("M"))["Debit"].sum().reset_index()
monthly["Date"] = monthly["Date"].astype(str)
fig1 = px.line(monthly, x="Date", y="Debit", title="Monthly Spending")
st.plotly_chart(fig1, use_container_width=True)

st.subheader("📦 Spending by Merchant/Details")
detail_pie = df.groupby("Details")["Debit"].sum().sort_values(ascending=False).head(10).reset_index()
fig2 = px.pie(detail_pie, names="Details", values="Debit", title="Top 10 Merchants by Spend")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("🔥 Spend Heatmap")
df["Day"] = df["Date"].dt.day_name()
df["Hour"] = df["Date"].dt.hour
heatmap_data = df.pivot_table(index="Day", columns="Hour", values="Debit", aggfunc="sum").fillna(0)
fig3, ax = plt.subplots(figsize=(10, 5))
sns.heatmap(heatmap_data, cmap="YlGnBu", ax=ax)
st.pyplot(fig3)

if st.button("📄 Export PDF Summary"):
    summary = {
        "Total Spend": total_spend,
        "Total Income": total_income,
        "Transactions": transactions
    }
    export_pdf(summary)
    with open("upi_report.pdf", "rb") as f:
        st.download_button("Download PDF", f, file_name="upi_report.pdf")

with st.expander("🔍 View Raw Transactions"):
    st.dataframe(df)