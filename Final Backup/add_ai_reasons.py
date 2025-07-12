from gpt_helper import generate_ai_reason
import pandas as pd
import time

# Load flagged transactions
df = pd.read_csv("../data/swift_flagged_data.csv")


# Clean up old AI errors from previously skipped rows
df.loc[df["Reconciliation_Status"].isin(["OK", "Match"]), "Exception_Reason"] = ""

# Generate AI Reason only for mismatched rows
for i, row in df.iterrows():
    if row["Reconciliation_Status"] not in ["OK", "Match"]:
        print(f"Generating for {row['Transaction_Ref']}...")

        try:
            # You can pass more columns if needed
            reason = generate_ai_reason(
                ref=row["Transaction_Ref"],
                status=row["Reconciliation_Status"],
                amount=row["Amount"],
                currency=row["Currency"],
                purpose=row["Payment_Purpose"]
            )

            df.at[i, "Exception_Reason"] = reason
            time.sleep(2)  # Pause to avoid OpenAI rate limit

        except Exception as e:
            print(f"Error with {row['Transaction_Ref']}: {e}")
            df.at[i, "Exception_Reason"] = "AI Error: " + str(e)

# Save updated file
df.to_csv("../data/swift_flagged_data.csv", index=False)
print("✅ All AI reasons added to swift_flagged_data.csv")
