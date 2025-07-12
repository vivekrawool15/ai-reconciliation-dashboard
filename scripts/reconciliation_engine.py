import pandas as pd

# Load incoming and outgoing files
incoming = pd.read_csv("../data/swift_incoming.csv")
outgoing = pd.read_csv("../data/swift_outgoing.csv")

# Merge based on Transaction Ref
merged = pd.merge(incoming, outgoing, on="Transaction_Ref", how="outer", suffixes=('_in', '_out'))

# Define a function to check match
def check_reconciliation(row):
    if pd.isna(row['Amount_in']) or pd.isna(row['Amount_out']):
        return "Missing Entry"
    elif row['Amount_in'] != row['Amount_out']:
        return "Amount Mismatch"
    elif row['Currency_in'] != row['Currency_out']:
        return "Currency Mismatch"
    else:
        return "Match"

# Apply function
merged['Reconciliation_Status'] = merged.apply(check_reconciliation, axis=1)

# Save output
merged.to_csv("../data/swift_reconciled.csv", index=False)

print("✅ Reconciliation completed. Output saved to swift_reconciled.csv")
