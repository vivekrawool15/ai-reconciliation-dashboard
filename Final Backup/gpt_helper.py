import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_ai_reason(ref, status, amount, currency, purpose):
    prompt = f"""
Transaction ID: {ref}
Status: {status}
Amount: {amount} {currency}
Purpose: {purpose}

Please generate a professional, human-like explanation to the client for this reconciliation issue. 
Ensure the explanation ends with a polite closing and a call to action for the client.

"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=1000
    )

    return response.choices[0].message["content"].strip()
