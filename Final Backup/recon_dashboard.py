import pandas as pd
import streamlit as st
import plotly.express as px
import os
import io
import base64

st.title("🔍 AI-Powered Reconciliation Dashboard")
df = pd.read_csv("../data/swift_flagged_data.csv")


# Calculate summary metrics
total_txns = len(df)
mismatches = df[df["Reconciliation_Status"] != "OK"]
num_mismatches = len(mismatches)
ai_generated = mismatches["Exception_Reason"].apply(lambda x: isinstance(x, str) and len(x.strip()) > 0).sum()

# Show KPIs in 3 columns
col1, col2, col3 = st.columns(3)
col1.metric("Total Transactions", total_txns)
col2.metric("Mismatches", num_mismatches)
col3.metric("AI Exception Reasons", ai_generated)
# 🎯 Add Filter Controls
status_options = [status for status in df["Reconciliation_Status"].unique() if status != "OK"]

# Step 1: Reconciliation Status Filter - exclude "OK" in dropdown
status_options = [status for status in df["Reconciliation_Status"].unique() if status != "OK"]
status_filter = st.selectbox("Select Reconciliation Status", options=["All"] + status_options)

# Step 2: Filter df based on selected status
if status_filter == "All":
    filtered_df = df[df["Reconciliation_Status"] != "OK"]  # All mismatches
else:
    filtered_df = df[df["Reconciliation_Status"] == status_filter]

# Step 3: Currency filter options only from filtered mismatches
# Step 3: Currency filter options - adjust for "All" vs specific status
if status_filter == "All":
    currency_source_df = df[df["Reconciliation_Status"] != "OK"]
else:
    currency_source_df = df[df["Reconciliation_Status"] == status_filter]

currency_options = sorted(currency_source_df["Currency"].dropna().unique())
currency_filter = st.selectbox("Select Currency", options=["All"] + list(currency_options))

# Step 4: Final filter based on selected currency
if currency_filter != "All":
    filtered_df = filtered_df[filtered_df["Currency"] == currency_filter]


st.markdown("### 🔍 Mismatched Transactions")

# Only keep mismatches
mismatch_df = filtered_df[filtered_df["Reconciliation_Status"] != "OK"]

# Show table
st.dataframe(mismatch_df[[
    "Transaction_Ref",
    "Amount",
    "Currency",
    "Reconciliation_Status",
    "Exception_Reason"
]])
# Export mismatches to Excel
st.markdown("### 📤 Download Mismatched Transactions")

# Create Excel download
excel_buffer = io.BytesIO()
mismatch_df.to_excel(excel_buffer, index=False, engine='openpyxl')
excel_bytes = excel_buffer.getvalue()
b64 = base64.b64encode(excel_bytes).decode()

href = f'<a href="data:application/octet-stream;base64,{b64}" download="mismatch_report.xlsx">📥 Click here to download Excel</a>'
st.markdown(href, unsafe_allow_html=True)

# 📥 Download Button for Mismatches
csv = mismatch_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download Mismatched Transactions",
    data=csv,
    file_name="mismatched_transactions.csv",
    mime="text/csv"
)



st.subheader("Summary: Matched vs Mismatched Transactions")

summary = df["Reconciliation_Status"].value_counts()
st.write(summary)

st.markdown("### 📧 Sample Email Preview")

if not mismatch_df.empty:
    first_row = mismatch_df.iloc[0]
    st.markdown(f"""
    **To:** client@example.com  
    **Subject:** Issue with Transaction ID: `{first_row['Transaction_Ref']}`

    {first_row['Exception_Reason']}
    """)
else:
    st.info("No mismatched transactions to preview.")


# Load the reconciled data
# df = pd.read_csv("../data/swift_reconciled.csv")

st.set_page_config(page_title="Payment Reconciliation Dashboard", layout="wide")


# Show a pie chart of reconciliation status
st.markdown("### 📊 Reconciliation Status Summary")

summary = df['Reconciliation_Status'].value_counts().reset_index()
summary.columns = ['Status', 'Count']

fig = px.pie(summary, names='Status', values='Count', title='Reconciliation Results')
st.plotly_chart(fig)


# Show status counts in a table
st.markdown("### 📋 Summary Table")

st.dataframe(summary)


# Function to color rows
def highlight_exceptions(row):
    if row["Reconciliation_Status"] == "Match":
        return ['background-color: #d4edda'] * len(row)  # Light green
    else:
        return ['background-color: #f8d7da'] * len(row)  # Light red


# 📈 AI Insight Summary Panel
st.markdown("## 📊 AI Learning & Insights")

try:
    # Step 1: Total transactions
    total_txns = len(df)

    # Step 2: Filter out 'OK' and 'Match' to get only mismatches
    issue_df = df[~df["Reconciliation_Status"].isin(["OK", "Match"])]
    mismatch_txns = len(issue_df)

    # Step 3: Determine the most common issue (if any)
    if issue_df.empty:
        most_common_issue = "None"
    elif issue_df["Reconciliation_Status"].value_counts().nunique() == 1:
        most_common_issue = "No dominant issue – all occurred equally"
    else:
        most_common_issue = issue_df["Reconciliation_Status"].value_counts().idxmax()

    # Step 4: Final summary string
    ai_summary = f"""
- Out of **{total_txns}** transactions, **{mismatch_txns}** had issues.
- The most common issue is: **{most_common_issue}**.
- This indicates a potential area for improvement in transaction accuracy or client instructions.
    """

    st.markdown(ai_summary)
    # Step 5: Add a simple bar chart of mismatch reasons
    issue_counts = issue_df["Reconciliation_Status"].value_counts().reset_index()
    issue_counts.columns = ["Issue Type", "Count"]

    st.markdown("### 📈 Issue Frequency")
    st.bar_chart(issue_counts.set_index("Issue Type"))

except Exception as e:
    st.warning(f"Could not generate AI summary due to error: {e}")

# Footer separator
st.markdown("---")
st.caption("🔐 Confidential simulation – not real payment data. | Made by Vivek Rawool")
