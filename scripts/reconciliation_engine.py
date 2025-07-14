import pandas as pd

# Load files
incoming = pd.read_csv("../data/swift_incoming.csv")
outgoing = pd.read_csv("../data/swift_outgoing.csv")

# Merge on Transaction_Ref
merged = pd.merge(incoming, outgoing, on="Transaction_Ref", how="outer", suffixes=('_in', '_out'))

# All columns to check
columns_to_check = [
    "Sender_BIC", "Receiver_BIC", "Amount", "Currency", "Transaction_Date",
    "Beneficiary_Name", "Beneficiary_Account", "Payment_Purpose"
]

# Define detailed reconciliation check
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

    if not issues:
        return "Match"
    else:
        return ", ".join(issues)

# Apply function to each row
merged["Reconciliation_Status"] = merged.apply(check_reconciliation, axis=1)

# Save result
merged.to_csv("../data/swift_reconciled.csv", index=False)

# Show total mismatches
mismatches = merged[merged["Reconciliation_Status"] != "Match"]
print("✅ Reconciliation completed. Output saved to swift_reconciled.csv")
print(f"⚠️ Total mismatches found: {len(mismatches)}")
