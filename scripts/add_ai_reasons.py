import pandas as pd
from gpt_helper import generate_ai_reason

df = pd.read_csv("../data/swift_flagged_data.csv")

# Remove any existing reasons
df["Exception_Reason"] = ""

# Loop only through mismatches (not Match or OK)
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

df.to_csv("../data/swift_flagged_data.csv", index=False)
print("✅ All AI reasons added to swift_flagged_data.csv")
