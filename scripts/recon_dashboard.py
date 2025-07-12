import pandas as pd
import streamlit as st
import plotly.express as px
import os
import io
import base64

# Page config
st.set_page_config(page_title="AI Reconciliation Dashboard", layout="wide")

# 🧭 1. Title + Tagline
st.title("💳 AI-Powered Payment Reconciliation Dashboard")
st.markdown("Built by Vivek Rawool – Simulating real-world SWIFT reconciliation")

# 🧾 2. Load data
df = pd.read_csv("data/swift_flagged_data.csv")


# 📊 3. KPI Metrics
total_txns = len(df)
mismatches = df[df["Reconciliation_Status"] != "OK"]
num_mismatches = len(mismatches)
ai_generated = mismatches["Exception_Reason"].apply(lambda x: isinstance(x, str) and len(x.strip()) > 0).sum()

col1, col2, col3 = st.columns(3)
col1.metric("Total Transactions", total_txns)
col2.metric("Mismatches", num_mismatches)
col3.metric("AI Exception Reasons", ai_generated)

# 🔍 4. Filters
status_options = [status for status in df["Reconciliation_Status"].unique() if status != "OK"]
status_filter = st.selectbox("Select Reconciliation Status", options=["All"] + status_options)

# Filter by status
if status_filter == "All":
    filtered_df = df[df["Reconciliation_Status"] != "OK"]
else:
    filtered_df = df[df["Reconciliation_Status"] == status_filter]

# Currency dropdown based on filtered data
currency_source_df = filtered_df
currency_options = sorted(currency_source_df["Currency"].dropna().unique())
currency_filter = st.selectbox("Select Currency", options=["All"] + list(currency_options))

# Final currency filter
if currency_filter != "All":
    filtered_df = filtered_df[filtered_df["Currency"] == currency_filter]

# 🧾 5. Mismatched Table
st.markdown("### 🔍 Mismatched Transactions")
mismatch_df = filtered_df[filtered_df["Reconciliation_Status"] != "OK"]
st.dataframe(mismatch_df[[
    "Transaction_Ref", "Amount", "Currency", "Reconciliation_Status", "Exception_Reason"
]])

# 📤 Download Mismatched Transactions
st.markdown("### 📤 Download Mismatched Transactions")

# 🔹 Excel Download Button
st.markdown("#### 📄 Export as Excel (.xlsx)")
excel_buffer = io.BytesIO()
mismatch_df.to_excel(excel_buffer, index=False, engine='openpyxl')
excel_bytes = excel_buffer.getvalue()

st.download_button(
    label="📥 Click here to download Excel",
    data=excel_bytes,
    file_name="mismatch_report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# 🔹 CSV Download Button
st.markdown("#### 🧾 Export as CSV (.csv)")
csv = mismatch_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Click here to download CSV",
    data=csv,
    file_name="mismatched_transactions.csv",
    mime="text/csv"
)



# ✉️ 7. Sample Email Preview
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

# 🧠 8. AI Learning & Insights
st.markdown("## 📊 AI Learning & Insights")
try:
    issue_df = df[~df["Reconciliation_Status"].isin(["OK", "Match"])]
    mismatch_txns = len(issue_df)

    if issue_df.empty:
        most_common_issue = "None"
    elif issue_df["Reconciliation_Status"].value_counts().nunique() == 1:
        most_common_issue = "No dominant issue – all occurred equally"
    else:
        most_common_issue = issue_df["Reconciliation_Status"].value_counts().idxmax()

    ai_summary = f"""
- Out of **{total_txns}** transactions, **{mismatch_txns}** had issues.
- The most common issue is: **{most_common_issue}**.
- This indicates a potential area for improvement in transaction accuracy or client instructions.
    """
    st.markdown(ai_summary)

    # Issue frequency bar chart
    issue_counts = issue_df["Reconciliation_Status"].value_counts().reset_index()
    issue_counts.columns = ["Issue Type", "Count"]
    st.markdown("### 📈 Issue Frequency")
    st.bar_chart(issue_counts.set_index("Issue Type"))

except Exception as e:
    st.warning(f"Could not generate AI summary due to error: {e}")

# 🧮 9. Reconciliation Status Pie Chart
st.markdown("### 📊 Reconciliation Status Summary")
summary = df['Reconciliation_Status'].value_counts().reset_index()
summary.columns = ['Status', 'Count']
fig = px.pie(summary, names='Status', values='Count', title='Reconciliation Results')
st.plotly_chart(fig)

# 📋 10. Full Summary Table
st.markdown("### 📋 Summary Table")
st.dataframe(summary)

# 📥 11. Download All Filtered Results
st.markdown("### 📥 Download Filtered Results")
st.download_button(
    label="Download as CSV",
    data=df.to_csv(index=False),
    file_name='filtered_reconciliation_results.csv',
    mime='text/csv'
)

# 🔐 12. Footer
st.markdown("---")
st.caption("🔐 Confidential simulation – not real payment data.")
