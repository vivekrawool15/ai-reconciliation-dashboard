import pandas as pd
import os

# 📁 Dynamically resolve data paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # /scripts
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

# 📥 Load reconciled data
df = pd.read_csv(os.path.join(DATA_DIR, "swift_reconciled.csv"))

# ⛑️ Fallback logic for incoming/outgoing
def choose_value(row, col):
    return row.get(f"{col}_in") if pd.notna(row.get(f"{col}_in")) else row.get(f"{col}_out")

# 📄 Columns to extract
columns = [
    "Transaction_Ref", "Sender_BIC", "Receiver_BIC", "Amount", "Currency",
    "Transaction_Date", "Beneficiary_Name", "Beneficiary_Account", "Payment_Purpose"
]

# 🧱 Build final flagged dataset
final_data = pd.DataFrame()

for col in columns:
    if col == "Transaction_Ref":
        final_data[col] = df.apply(
            lambda row: row.get("Transaction_Ref") if pd.notna(row.get("Transaction_Ref")) else "Unknown", axis=1
        )
    else:
        final_data[col] = df.apply(lambda row: choose_value(row, col), axis=1)

# 🧾 Add status + empty AI reason
final_data["Reconciliation_Status"] = df["Reconciliation_Status"]
final_data["Exception_Reason"] = ""

# 💾 Save output
output_path = os.path.join(DATA_DIR, "swift_flagged_data.csv")
final_data.to_csv(output_path, index=False)

print("✅ swift_flagged_data.csv regenerated with ALL transactions.")
