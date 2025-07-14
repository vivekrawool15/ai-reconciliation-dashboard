import pandas as pd
import streamlit as st
import plotly.express as px
import io
import plotly.graph_objects as go
import datetime  # ✅ Add this

# 🔧 Page Configuration
st.set_page_config(page_title="AI Reconciliation Dashboard", layout="wide")

# 🧭 Title and Tagline
st.title("💳 AI-Powered Payment Reconciliation Dashboard")
st.markdown("Built by Vivek Rawool – Simulating real-world SWIFT reconciliation")

# 🧾 Load Data
df = pd.read_csv("data/swift_flagged_data.csv")

# ✅ Show UTC timestamp to confirm this version is latest
st.caption(f"📅 Deployed at (UTC): {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")


# 👇 Create simplified grouping labels
def simplify_status(status):
    if status == "Match":
        return "Match"
    elif "Mismatch" in status:
        return status.strip()
    elif "Missing" in status and "," in status:
        return "Multiple Missing Fields"
    elif "Missing" in status:
        return status.strip()
    else:
        return "Other"

# 📊 3. KPI Metrics
total_txns = len(df)
num_matches = len(df[df["Reconciliation_Status"] == "Match"])
num_mismatches = len(df[df["Reconciliation_Status"] != "Match"])
ai_generated = df["Exception_Reason"].apply(lambda x: isinstance(x, str) and len(x.strip()) > 0 and x.strip().lower() != "not applicable").sum()

col1, col2, col3 = st.columns(3)
col1.metric("Total Transactions", total_txns)
col2.metric("✅ Matches", num_matches)
col3.metric("🔴 Mismatches", num_mismatches)


# Show all unique statuses, including Match
status_options = sorted(df["Reconciliation_Status"].dropna().unique())
status_filter = st.selectbox("Select Reconciliation Status", options=["All"] + list(status_options))

# Filter based on dropdown
if status_filter == "All":
    filtered_df = df.copy()
else:
    filtered_df = df[df["Reconciliation_Status"] == status_filter]


# Currency filter
currency_options = sorted(filtered_df["Currency"].dropna().unique())
currency_filter = st.selectbox("Select Currency", options=["All"] + list(currency_options))

# Apply currency filter
if currency_filter != "All":
    filtered_df = filtered_df[filtered_df["Currency"] == currency_filter]

# 🧾 Transaction History Table (Styled Dark Mode Friendly)
st.markdown("### 📋 Transaction History")

# 1. Create display dataframe
display_df = filtered_df.copy()

# 2. Add readable columns
display_df["Reconciliation_Result"] = display_df["Reconciliation_Status"].apply(
    lambda x: "Match" if x == "Match" else "Not Matched"
)


# 👉 Clean up exception reason for display
def simplify_reason(x):
    if x == "Match":
        return "Not Applicable"
    elif "Missing" in x and "," in x:
        return "Multiple Missing Fields"
    elif "Mismatch" in x or "Missing" in x:
        return x.strip()
    else:
        return "Other"

display_df["Exception_Summary"] = display_df["Reconciliation_Status"].apply(simplify_reason)

# 3. Reset index
display_df = display_df.reset_index(drop=True)
display_df.index += 1  # Start row count from 1

# 4. Columns to show
styled_df = display_df[[ 
    "Transaction_Ref", "Amount", "Currency", "Reconciliation_Result", "Exception_Summary"
]]


# 5. Row-wise dark themed styling
def highlight_row(row):
    if row["Reconciliation_Result"] == "Match":
        return ['background-color: #2c3e50; color: #ffffff'] * len(row)
    else:
        return ['background-color: #7f1d1d; color: #ffffff'] * len(row)


# 6. Show styled table
st.dataframe(
    styled_df.style.apply(highlight_row, axis=1),
    use_container_width=True
)


# 📤 Download Transactions
st.markdown("### 📤 Download Transactions")

# Excel
excel_buffer = io.BytesIO()
display_df.to_excel(excel_buffer, index=False, engine='openpyxl')
excel_bytes = excel_buffer.getvalue()
st.markdown("#### 📄 Export as Excel (.xlsx)")
st.download_button(
    label="📥 Click here to download Excel",
    data=excel_bytes,
    file_name="reconciliation_report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# CSV
st.markdown("#### 🧾 Export as CSV (.csv)")
csv = display_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Click here to download CSV",
    data=csv,
    file_name="reconciliation_report.csv",
    mime="text/csv"
)

# ✉️ 7. Sample Email Preview
st.markdown("### 📧 Sample Email Preview")

# Refine preview behavior
valid_preview_df = display_df[
    display_df["Transaction_Ref"].notna() & display_df["Exception_Reason"].notna()
]

if status_filter == "Match":
    st.info("✅ These are matched transactions. No email is required.")
elif status_filter == "All":
    st.info("ℹ️ Select a specific reconciliation issue above to preview a sample email.")
elif not valid_preview_df.empty:
    preview_row = valid_preview_df.iloc[0]
    st.markdown(f"""
**To:** client@example.com  
**Subject:** Issue with Transaction ID: `{preview_row['Transaction_Ref']}`

{preview_row['Exception_Reason']}
    """)
else:
    st.info("⚠️ No valid transaction found with exception reason for email preview.")


# 📊 AI Learning & Insights
st.markdown("## 📊 AI Learning & Insights")

try:
    # Filter mismatches (exclude OK and Match)
    issue_df = df[df["Reconciliation_Status"].isin(["OK", "Match"]) == False]
    mismatch_txns = len(issue_df)

    if issue_df.empty:
        most_common_issue = "None"
    else:
        issue_df["Status_Label"] = issue_df["Reconciliation_Status"].apply(simplify_status)
        issue_counts = issue_df["Status_Label"].value_counts()
        top_count = issue_counts.iloc[0]
        most_common_issues = issue_counts[issue_counts == top_count].index.tolist()

        if len(most_common_issues) == 1:
            most_common_issue = most_common_issues[0]
        else:
            most_common_issue = ", ".join(most_common_issues)

    ai_summary = f"""
- Out of **{total_txns}** transactions, **{mismatch_txns}** had issues.
- The most common issue is: **{most_common_issue}**.
- This indicates a potential area for improvement in transaction accuracy or client instructions.
    """
    st.markdown(ai_summary)

except Exception as e:
    st.warning(f"Could not generate AI summary due to error: {e}")



# 👇 Create simplified grouping labels
def simplify_status(status):
    if status == "Match":
        return "Match"
    elif "Mismatch" in status:
        return status.strip()
    elif "Missing" in status and "," in status:
        return "Multiple Missing Fields"
    elif "Missing" in status:
        return status.strip()
    else:
        return "Other"

# 👇 Add new column
# 👇 Create simplified grouping labels
def simplify_status(status):
    if status == "Match":
        return "Match"
    elif "Mismatch" in status:
        return status.strip()
    elif "Missing" in status and "," in status:
        return "Multiple Missing Fields"
    elif "Missing" in status:
        return status.strip()
    else:
        return "Other"

# Apply to main df and filtered_df both
df["Status_Label"] = df["Reconciliation_Status"].apply(simplify_status)
filtered_df["Status_Label"] = filtered_df["Reconciliation_Status"].apply(simplify_status)

# Update Exception Summary in Transaction History Table
filtered_df["Exception_Reason"] = filtered_df["Status_Label"].apply(
    lambda x: "Not Applicable" if x == "Match" else x
)




   # ✅ Bar Chart with Clean Labels + Matching Colors
import plotly.graph_objects as go

st.markdown("### 🔢 Frequency")

# Count by simplified label
clean_counts = df["Status_Label"].value_counts().reset_index()
clean_counts.columns = ["Status", "Count"]

# Define consistent color mapping
bar_colors = {
    "Match": "#63b3ed",
    "Amount Mismatch": "#f56565",
    "Currency Mismatch": "#ed8936",
    "Receiver_BIC Mismatch": "#d69e2e",
    "Sender_BIC Mismatch": "#48bb78",
    "Beneficiary_Name Mismatch": "#38b2ac",
    "Beneficiary_Account Mismatch": "#805ad5",
    "Transaction_Date Mismatch": "#718096",
    "Payment_Purpose Mismatch": "#fbbf24",
    "Multiple Missing Fields": "#e53e3e",
    "Other": "#a0aec0"
}

# Assign matching colors
colors = [bar_colors.get(status, "#a0aec0") for status in clean_counts["Status"]]

# Build the bar chart
fig = go.Figure(data=[
    go.Bar(
        x=clean_counts["Status"],
        y=clean_counts["Count"],
        marker_color=colors
    )
])

fig.update_layout(
    xaxis_title="Reconciliation Status",
    yaxis_title="Count",
    plot_bgcolor="#1a202c",
    paper_bgcolor="#1a202c",
    font_color="#e2e8f0"
)

st.plotly_chart(fig)



# 🥧 Pie Chart of Reconciliation Status
st.markdown("### 📊 Reconciliation Status Summary")
summary = df['Status_Label'].value_counts().reset_index()
summary.columns = ['Status', 'Count']

fig = px.pie(summary, names='Status', values='Count', title='Reconciliation Results')
st.plotly_chart(fig)

# 📋 Summary Table
st.markdown("### 📋 Summary Table")
summary = summary.reset_index(drop=True)
summary.index += 1  # Make index start from 1
st.dataframe(summary)


# ⬇️ Download All Transactions
st.markdown("### 📥 Download Filtered Results")
st.download_button(
    label="Download as CSV",
    data=df.to_csv(index=False),
    file_name='filtered_reconciliation_results.csv',
    mime='text/csv'
)

# 🔐 Footer
st.markdown("---")
st.caption("🔐 Confidential simulation – not real payment data.")
