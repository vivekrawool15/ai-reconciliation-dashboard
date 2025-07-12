from gpt_helper import generate_ai_reason

output = generate_ai_reason(
    ref="TRX45678",
    status="Amount Mismatch",
    amount_in=10000,
    amount_out=8500,
    currency_in="INR",
    currency_out="INR"
)

print(output)
