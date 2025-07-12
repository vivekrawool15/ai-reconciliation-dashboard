import pandas as pd
from faker import Faker
import random

fake = Faker()

# Define a list of dummy currencies
currencies = ['USD', 'EUR', 'GBP', 'INR', 'JPY']

# Create a list to store payment records
data = []

for _ in range(20):  # generate 20 dummy transactions
    transaction = {
        "Transaction_Ref": fake.bothify(text="TRX#####"),
        "Sender_BIC": fake.bothify(text="ABCDUS33XXX"),
        "Receiver_BIC": fake.bothify(text="EFGHIN22XXX"),
        "Amount": round(random.uniform(100, 100000), 2),
        "Currency": random.choice(currencies),
        "Transaction_Date": fake.date_this_year(),
        "Beneficiary_Name": fake.name(),
        "Beneficiary_Account": fake.bban(),
        "Payment_Purpose": fake.sentence(nb_words=4)
    }
    data.append(transaction)

# Convert list to DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv("../data/swift_dummy_data.csv", index=False)

print("✅ Dummy SWIFT data created and saved to /data folder.")
