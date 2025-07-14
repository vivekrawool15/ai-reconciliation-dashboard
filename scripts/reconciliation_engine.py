import pandas as pd
import os

# 📁 Dynamically resolve the correct data path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # /scripts
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

# 📥 Load incoming and outgoing files
incoming = pd.read_csv(os.path.join(DATA_DIR, "swift_incoming.csv"))
outgoing = pd.read_csv(os.path.join(DATA_DIR, "swift_outgoing.csv"))

# 🔀 Merge on Transaction_Ref
merged = pd.merge(incoming, outgoing, on="Transaction_Ref", how="outer", suffixes=('_in', '_out'))

# 🧾 Fields to compare
columns_to_check = [
    "Sender_BIC", "Receiver_BIC", "Amount", "Currency", "Transaction_Date",
    "Beneficiary_Name", "Beneficiary_Account", "Payment_Purpose"
]

# ✅ Reconciliation logic
def check_reconciliation(row):
    issues = []

    for col in columns_to_check:
        col_in = f"{col}_in"
        col_out = f"{col}_out"

        val_in = row.get(col_in)
        val_out = row.get(col_out)

        if pd.isna(val_in) or pd.isna(val_out):
            issues.append(f"{col} Missing")
        elif str(val_in).strip() != str(val_out).strip():
            issues.append(f"{col} Mismatch")

    return "Match" if not issues else ", ".join(issues)

# 🧠 Apply logic row by row
merged["Reconciliation_Status"] = merged.apply(check_reconciliation, axis=1)

# 💾 Save output
output_path = os.path.join(DATA_DIR, "swift_reconciled.csv")
merged.to_csv(output_path, index=False)

# 📊 Summary print
mismatches = merged[merged["Reconciliation_Status"] != "Match"]
print("✅ Reconciliation completed. Output saved to swift_reconciled.csv")
print(f"⚠️ Total mismatches found: {len(mismatches)}")
