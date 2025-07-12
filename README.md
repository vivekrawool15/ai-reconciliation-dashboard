# 💳 AI-Powered Payment Reconciliation Dashboard

This project simulates an intelligent SWIFT payment reconciliation tool using AI.

## 🔍 Features
- Reconciles real-looking international payment data
- Uses OpenAI GPT-4 to generate exception reasons for mismatches
- Beautiful interactive dashboard built with Streamlit
- Filters by reconciliation status, currency, and transaction reference
- One-click Excel and CSV downloads
- Smart AI summary insights and issue frequency chart
- Sample email previews for flagged transactions

## 🛠️ How to Run
1. Clone this repo or download the ZIP
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
3. Run the dashboard:
   ```bash
   streamlit run scripts/recon_dashboard.py

## 📁 Project Structure

AI Reconciliation Project/
├── data/
│   └── swift_flagged_data.csv
├── scripts/
│   ├── recon_dashboard.py
│   └── add_ai_reasons.py
├── gpt_helper.py
├── requirements.txt
└── README.md
### 📸 Dashboard Preview



![Dashboard Screenshot](screenshots/dashboard_preview.png)
### 🚀 Deployment Suggestions (Optional)

You can deploy this project using:
- **Streamlit Cloud** (Recommended for simplicity)
- **Render**, **Railway**, or **Azure** for more backend flexibility

Let me know if you want help deploying — it's just a few clicks!
### 📄 License

This project is for educational purposes only. No real client data is used.
