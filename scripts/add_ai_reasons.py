import pandas as pd
import os
from gpt_helper import generate_ai_reason

# 📁 Resolve path to data directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
flagged_path = os.path.join(DATA_DIR, "swift_flagged_data.csv")

# 📥 Load data
df = pd.read_csv(flagged_path)

# 🧹 Remove old AI reasons
df["Exception_Reason"] = ""

# 🔍 Loop through mismatches
for idx, row in df.iterrows():
    if row["Reconciliation_Status"] not in ["Match", "OK"]:
        ref = row["Transaction_Ref"] if pd.notna(row["Transaction_Ref"]) else "Unknown"
        status = row["Reconciliation_Status"]
        amount = row["Amount"] if pd.notna(row["Amount"]) else "Unknown"
        currency = row["Currency"] if pd.notna(row["Currency"]) else "Unknown"
        purpose = row["Payment_Purpose"] if pd.notna(row["Payment_Purpose"]) else "No purpose provided"

        reason = generate_ai_reason(ref, status, amount, currency, purpose)
        df.at[idx, "Exception_Reason"] = str(reason)
        print(f"✅ Generated for {ref}")

# 💾 Save updated data
df.to_csv(flagged_path, index=False)
print("✅ All AI reasons added to swift_flagged_data.csv")
