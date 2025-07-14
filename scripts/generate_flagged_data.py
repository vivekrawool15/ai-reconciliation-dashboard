import pandas as pd

# Load reconciled file
df = pd.read_csv("../data/swift_reconciled.csv")

# Fallback logic: prefer _in if exists, else _out
def choose_value(row, col):
    return row.get(f"{col}_in") if pd.notna(row.get(f"{col}_in")) else row.get(f"{col}_out")

final_data = pd.DataFrame()
columns = [
    "Transaction_Ref", "Sender_BIC", "Receiver_BIC", "Amount", "Currency",
    "Transaction_Date", "Beneficiary_Name", "Beneficiary_Account", "Payment_Purpose"
]

for col in columns:
    if col == "Transaction_Ref":
        final_data[col] = df.apply(lambda row: row.get("Transaction_Ref") if pd.notna(row.get("Transaction_Ref")) else "Unknown", axis=1)
    else:
        final_data[col] = df.apply(lambda row: choose_value(row, col), axis=1)

# Add reconciliation result and blank exception reason
final_data["Reconciliation_Status"] = df["Reconciliation_Status"]
final_data["Exception_Reason"] = ""

# Save output
final_data.to_csv("../data/swift_flagged_data.csv", index=False)
print("✅ swift_flagged_data.csv regenerated with ALL transactions.")
