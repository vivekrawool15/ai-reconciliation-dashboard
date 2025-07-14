import subprocess
import datetime
import os

print("🔄 Starting auto-update process...")

try:
    print("⚙️ Running reconciliation_engine.py...")
    subprocess.run(["python", "scripts/reconciliation_engine.py"], check=True)

    print("⚙️ Running generate_flagged_data.py...")
    subprocess.run(["python", "scripts/generate_flagged_data.py"], check=True)

    print("⚙️ Running add_ai_reasons.py...")
    subprocess.run(["python", "scripts/add_ai_reasons.py"], check=True)

    print("✅ Reconciliation and flagged data updated successfully!")

    print("🚀 Pushing updates to GitHub...")
    subprocess.run(["git", "add", "data/swift_flagged_data.csv"], check=True)

    commit_msg = f"✅ Auto update: Flagged data @ {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    subprocess.run(["git", "commit", "-m", commit_msg], check=True)
    subprocess.run(["git", "push"], check=True)

    print("✅ Git push successful!")

except subprocess.CalledProcessError as e:
    print("❌ Error:", e)
