import pandas as pd

# Load the dummy SWIFT data
df = pd.read_csv("../data/swift_dummy_data.csv")

# Define a function to check for exceptions
def apply_rules(row):
    reasons = []

    # Rule 1: Missing Beneficiary Account
    if pd.isna(row['Beneficiary_Account']) or row['Beneficiary_Account'] == "":
        reasons.append("Missing Beneficiary Account")

    # Rule 2: High Amount
    if row['Amount'] > 100000:
        reasons.append("High Value Transaction")

    # Rule 3: Invalid Currency
    valid_currencies = ['USD', 'EUR', 'GBP', 'INR', 'JPY']
    if row['Currency'] not in valid_currencies:
        reasons.append("Unknown Currency")

    # Rule 4: Sender and Receiver BIC same
    if row['Sender_BIC'] == row['Receiver_BIC']:
        reasons.append("Sender and Receiver BIC Match")

    # Return reasons if any, else mark as OK
    if reasons:
        return ("Exception", "; ".join(reasons))
    else:
        return ("OK", "")

# Apply the rules to each row
df[['Status', 'Exception_Reason']] = df.apply(lambda row: pd.Series(apply_rules(row)), axis=1)

# Save the result to a new CSV
df.to_csv("../data/swift_flagged_data.csv", index=False)

print("✅ Rule-based exception check completed. Output saved as swift_flagged_data.csv.")
