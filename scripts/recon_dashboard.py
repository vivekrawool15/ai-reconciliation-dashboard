import pandas as pd
import streamlit as st
import datetime
import plotly.graph_objects as go
import plotly.express as px

# Page Config
st.set_page_config(page_title="AI Reconciliation Dashboard", layout="wide")

# Title
st.title("💳 AI-Powered Payment Reconciliation Dashboard")
st.markdown("Built by Vivek Rawool – Simulating real-world SWIFT reconciliation")

st.markdown("### 📥 Download Sample Files")

sample_data = {
    "Transaction_Ref": ["TRX001", "TRX002"],
    "Sender_BIC": ["BANKINBB", "BANKUS33"],
    "Receiver_BIC": ["BANKDEFF", "BANKGB22"],
    "Amount": [1000.50, 750.00],
    "Currency": ["INR", "USD"],
    "Transaction_Date": ["2024-01-01", "2024-01-02"],
    "Beneficiary_Name": ["John Doe", "Jane Smith"],
    "Beneficiary_Account": ["1234567890", "9876543210"],
    "Payment_Purpose": ["Salary", "Invoice Payment"]
}

sample_df = pd.DataFrame(sample_data)
sample_csv = sample_df.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download Sample File", data=sample_csv, file_name="sample_transaction_file.csv", mime="text/csv")

# File Upload
st.markdown("## 📂 Upload Your Files")
inflow_file = st.file_uploader("🗕️ Upload Inflow File", type=["csv"], key="inflow")
outflow_file = st.file_uploader("📄 Upload Outflow File", type=["csv"], key="outflow")

# Reset session state if new files are uploaded
if "prev_inflow" not in st.session_state or inflow_file != st.session_state.get("prev_inflow"):
    st.session_state.prev_inflow = inflow_file

if "prev_outflow" not in st.session_state or outflow_file != st.session_state.get("prev_outflow"):
    st.session_state.prev_outflow = outflow_file

if inflow_file is not None and outflow_file is not None:
    try:
        df_incoming = pd.read_csv(inflow_file)
    except pd.errors.EmptyDataError:
        st.error("❌ Inflow file is empty or has no valid columns.")
        st.stop()
    try:
        df_outgoing = pd.read_csv(outflow_file)
    except pd.errors.EmptyDataError:
        st.error("❌ Outflow file is empty or has no valid columns.")
        st.stop()

    required_columns = [
        "Transaction_Ref", "Sender_BIC", "Receiver_BIC", "Amount", "Currency",
        "Transaction_Date", "Beneficiary_Name", "Beneficiary_Account", "Payment_Purpose"
    ]

    missing_in = [col for col in required_columns if col not in df_incoming.columns]
    missing_out = [col for col in required_columns if col not in df_outgoing.columns]

    if missing_in or missing_out:
        st.error(f"""
❌ Required columns are missing or misnamed:

🔍 Missing in Inflow File: {', '.join(missing_in) if missing_in else '✅ All OK'}
🔍 Missing in Outflow File: {', '.join(missing_out) if missing_out else '✅ All OK'}

✅ Please ensure **both** files have exact column names like:
- Transaction_Ref
- Sender_BIC
- Receiver_BIC
- Amount
- Currency
- Transaction_Date
- Beneficiary_Name
- Beneficiary_Account
- Payment_Purpose
        """)
        st.stop()

    df_incoming = df_incoming.loc[:, ~df_incoming.columns.duplicated()]
    df_outgoing = df_outgoing.loc[:, ~df_outgoing.columns.duplicated()]

    # ✅ FIELD CHECKBOXES
    st.markdown("### ⚙️ Select Fields for Reconciliation")
    field_options = [
        "Amount", "Currency", "Sender_BIC", "Receiver_BIC",
        "Transaction_Date", "Beneficiary_Name", "Beneficiary_Account", "Payment_Purpose"
    ]
    default_selected = ["Amount", "Currency", "Sender_BIC", "Receiver_BIC"]

    cols = st.columns(4)
    recon_fields = []
    for i, field in enumerate(field_options):
        with cols[i % 4]:
            if st.checkbox(field, value=field in default_selected, key=f"chk_{field}"):
                recon_fields.append(field)

    # Merge
    df = pd.merge(df_incoming, df_outgoing, on="Transaction_Ref", suffixes=("_in", "_out"), how="inner")
    inflow_only = df_incoming[~df_incoming["Transaction_Ref"].isin(df_outgoing["Transaction_Ref"])]
    outflow_only = df_outgoing[~df_outgoing["Transaction_Ref"].isin(df_incoming["Transaction_Ref"])]

    df = pd.merge(df_incoming, df_outgoing, on="Transaction_Ref", suffixes=("_in", "_out"), how="inner")
   
    # Reconciliation Logic
    def reconcile_row(row):
        mismatches = []
        if pd.isna(row["Transaction_Ref"]):
            return "Transaction Ref Missing"
        if "Amount" in recon_fields and row["Amount_in"] != row["Amount_out"]:
            mismatches.append("Amount Mismatch")
        if "Currency" in recon_fields and row["Currency_in"] != row["Currency_out"]:
            mismatches.append("Currency Mismatch")
        if "Sender_BIC" in recon_fields and row["Sender_BIC_in"] != row["Sender_BIC_out"]:
            mismatches.append("Sender_BIC Mismatch")
        if "Receiver_BIC" in recon_fields and row["Receiver_BIC_in"] != row["Receiver_BIC_out"]:
            mismatches.append("Receiver_BIC Mismatch")
        if "Transaction_Date" in recon_fields and row["Transaction_Date_in"] != row["Transaction_Date_out"]:
            mismatches.append("Transaction Date Mismatch")
        if "Beneficiary_Name" in recon_fields and row["Beneficiary_Name_in"] != row["Beneficiary_Name_out"]:
            mismatches.append("Beneficiary Name Mismatch")
        if "Beneficiary_Account" in recon_fields and row["Beneficiary_Account_in"] != row["Beneficiary_Account_out"]:
            mismatches.append("Beneficiary Account Mismatch")
        if "Payment_Purpose" in recon_fields and row["Payment_Purpose_in"] != row["Payment_Purpose_out"]:
            mismatches.append("Payment Purpose Mismatch")
        return "Match" if not mismatches else "Mismatch"

    def generate_reason(row):
        if row["Reconciliation_Status"] == "Match":
            return "Not Applicable"
        reasons = []
        if "Amount" in recon_fields and row["Amount_in"] != row["Amount_out"]:
            reasons.append("Amount mismatch.")
        if "Currency" in recon_fields and row["Currency_in"] != row["Currency_out"]:
            reasons.append("Currency mismatch.")
        if "Sender_BIC" in recon_fields and row["Sender_BIC_in"] != row["Sender_BIC_out"]:
            reasons.append("Sender BIC mismatch.")
        if "Receiver_BIC" in recon_fields and row["Receiver_BIC_in"] != row["Receiver_BIC_out"]:
            reasons.append("Receiver BIC mismatch.")
        if "Transaction_Date" in recon_fields and row["Transaction_Date_in"] != row["Transaction_Date_out"]:
            reasons.append("Transaction date mismatch.")
        if "Beneficiary_Name" in recon_fields and row["Beneficiary_Name_in"] != row["Beneficiary_Name_out"]:
            reasons.append("Beneficiary name mismatch.")
        if "Beneficiary_Account" in recon_fields and row["Beneficiary_Account_in"] != row["Beneficiary_Account_out"]:
            reasons.append("Beneficiary account mismatch.")
        if "Payment_Purpose" in recon_fields and row["Payment_Purpose_in"] != row["Payment_Purpose_out"]:
            reasons.append("Payment purpose mismatch.")
        return " ".join(reasons)

    df["Reconciliation_Status"] = df.apply(reconcile_row, axis=1)
    df["Reconciliation_Summary"] = df.apply(generate_reason, axis=1)

    # ✅ STATUS CHECKBOXES
    st.markdown("### 📜 Select Transactions")
    status_options = sorted(df["Reconciliation_Status"].unique())
    status_cols = st.columns(len(status_options))
    status_filter = []
    for i, status in enumerate(status_options):
        with status_cols[i]:
            if st.checkbox(status, key=f"status_{status}"):
                status_filter.append(status)

    # ✅ SUMMARY CHECKBOXES
    summary_filter = []
    if status_filter == ["Match"]:
        summary_filter = ["Not Applicable"]
        st.markdown("🔍 Only 'Not Applicable' summaries apply for Matches.")
    elif "Mismatch" in status_filter:
        st.markdown("### 📝 Select Reconciliation Summary")
        summary_options = sorted(df[df["Reconciliation_Summary"] != "Not Applicable"]["Reconciliation_Summary"].unique())
        summary_cols = st.columns(3)
        for i, summary in enumerate(summary_options):
            with summary_cols[i % 3]:
                if st.checkbox(summary, key=f"summary_{summary}"):
                    summary_filter.append(summary)

    # Apply Filters
    filtered_df = df.copy()
    if status_filter:
        filtered_df = filtered_df[filtered_df["Reconciliation_Status"].isin(status_filter)]
    if summary_filter:
        filtered_df = filtered_df[filtered_df["Reconciliation_Summary"].isin(summary_filter)]

    # KPIs
    st.metric("Total Transactions", len(df))
    st.metric("✅ Matches", len(df[df["Reconciliation_Status"] == "Match"]))
    st.metric("🔴 Mismatches", len(df[df["Reconciliation_Status"] == "Mismatch"]))

    # Display Filtered Table
    st.markdown("### 📊 Transaction Results")
    st.dataframe(filtered_df[[
        "Transaction_Ref", "Amount_in", "Currency_in", "Amount_out", "Currency_out",
        "Reconciliation_Status", "Reconciliation_Summary"
    ]], use_container_width=True)

    # Downloads
    st.markdown("### 📅 Download Reconciliation Results")
    col1, col2, col3, col4 = st.columns(4)

    csv_all = df.to_csv(index=False).encode("utf-8")
    csv_matches = df[df["Reconciliation_Status"] == "Match"].to_csv(index=False).encode("utf-8")
    csv_mismatches = df[df["Reconciliation_Status"] == "Mismatch"].to_csv(index=False).encode("utf-8")
    csv_filtered = filtered_df.to_csv(index=False).encode("utf-8")

    with col1:
        st.download_button("⬇️ Download All", data=csv_all, file_name="reconciliation_all.csv", mime="text/csv")
    with col2:
        st.download_button("✅ Download Matches", data=csv_matches, file_name="reconciliation_matches.csv", mime="text/csv")
    with col3:
        st.download_button("🔴 Download Mismatches", data=csv_mismatches, file_name="reconciliation_mismatches.csv", mime="text/csv")
    with col4:
        st.download_button("🔽️ Download Table View", data=csv_filtered, file_name="reconciliation_table_view.csv", mime="text/csv")

    # Email Preview
    st.markdown("### 📧 Sample Email Preview")
    summary_values = sorted(df[df["Reconciliation_Summary"] != "Not Applicable"]["Reconciliation_Summary"].unique())
    selected_summary = st.selectbox("Select Reconciliation Summary for Preview", summary_values)

    email_preview_df = df[df["Reconciliation_Summary"] == selected_summary]
    if not email_preview_df.empty:
        txn_id = email_preview_df["Transaction_Ref"].iloc[0]
        reason = email_preview_df["Reconciliation_Summary"].iloc[0]

        email_body = f"""
        Dear Client,

        We hope this message finds you well.

        Upon reconciling your recent transactions, we identified a discrepancy in Transaction Ref: **{txn_id}**.
        The issue appears to be: **{reason}**.

        Please verify and advise on further action.

        Best Regards,  
        Reconciliation Team
        """
        st.text_area("📨 Email Preview", value=email_body.strip(), height=200, max_chars=1000)
    else:
        st.info("✅ No mismatch found for selected summary.")

    # Insights
    st.markdown("## 🤖 AI Learning & Insights")
    issue_df = df[df["Reconciliation_Summary"] != "Not Applicable"]
    mismatch_txns = len(issue_df)
    top_summary = issue_df["Reconciliation_Summary"].value_counts()
    if not top_summary.empty:
        top_count = top_summary.iloc[0]
        top_issues = top_summary[top_summary == top_count].index.tolist()
        if len(top_issues) == 1:
            common_issue = top_issues[0]
        else:
            common_issue = "Multiple Issues"
    else:
        common_issue = "None"

    st.markdown(f"""
    - Out of **{len(df)}** transactions, **{mismatch_txns}** had reconciliation issues.
    - Most frequent issue detected: **{common_issue}**.
    - Suggests potential process review or client clarification.
    """)

    # Bar Chart
    st.markdown("### 📊 Reconciliation Status Frequency")
    freq_df = df["Reconciliation_Status"].value_counts().reset_index()
    freq_df.columns = ["Status", "Count"]
    color_map = {"Match": "#63b3ed", "Mismatch": "#f56565"}
    colors = [color_map.get(status, "#a0aec0") for status in freq_df["Status"]]
    fig_bar = go.Figure(data=[go.Bar(x=freq_df["Status"], y=freq_df["Count"], marker_color=colors)])
    fig_bar.update_layout(
        xaxis_title="Reconciliation Status",
        yaxis_title="Count",
        plot_bgcolor="#1a202c",
        paper_bgcolor="#1a202c",
        font_color="#e2e8f0"
    )
    st.plotly_chart(fig_bar)

    # Pie Chart
    st.markdown("### 🥧 Reconciliation Summary Frequency")
    pie_df = df[df["Reconciliation_Summary"] != "Not Applicable"]["Reconciliation_Summary"].value_counts().reset_index()
    pie_df.columns = ["Summary", "Count"]
    fig_pie = px.pie(pie_df, names="Summary", values="Count", title="Reconciliation Summary Frequency")
    st.plotly_chart(fig_pie)

    # Footer
    st.markdown("---")
    st.markdown("**Built by Vivek Rawool | AI-Powered Reconciliation Dashboard | For Study & Demo Use Only**")

else:
    st.warning("⚠️ Please upload both inflow and outflow CSV files to begin reconciliation.")
