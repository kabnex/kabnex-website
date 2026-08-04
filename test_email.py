"""
Quick standalone check that Brevo email sending is configured correctly.

Run:
    export BREVO_API_KEY="your-brevo-api-key"
    export BREVO_SENDER_EMAIL="kabnextechnologies@gmail.com"   # optional, must be a verified sender
    python test_email.py

Or, if you have a .env file with these set, just:
    python test_email.py
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("BREVO_API_KEY")
SENDER_EMAIL = os.environ.get("BREVO_SENDER_EMAIL", "kabnextechnologies@gmail.com")
COMPANY_EMAIL = "kabnextechnologies@gmail.com"

print("Checking Brevo configuration...")

if not API_KEY:
    print("  ✗ BREVO_API_KEY is NOT set.")
    raise SystemExit(1)
print(f"  ✓ BREVO_API_KEY = {API_KEY[:6]}...{API_KEY[-4:]} ({len(API_KEY)} characters)")
print(f"  ✓ BREVO_SENDER_EMAIL = {SENDER_EMAIL}")

print("\nSending a test email via the Brevo API...")

resp = requests.post(
    "https://api.brevo.com/v3/smtp/email",
    headers={
        "api-key": API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
    },
    json={
        "sender": {"email": SENDER_EMAIL, "name": "Kabnex Website"},
        "to": [{"email": COMPANY_EMAIL}],
        "subject": "Kabnex — Brevo test email",
        "textContent": "This is a test email from test_email.py — if you got this, Brevo is set up correctly.",
    },
    timeout=10,
)

if resp.status_code < 300:
    print(f"  ✓ Sent successfully (status {resp.status_code}). Check {COMPANY_EMAIL} inbox (and spam folder).")
else:
    print(f"  ✗ FAILED — status {resp.status_code}")
    print(f"    Response: {resp.text}")
    print("\n  Common causes:")
    print("   - BREVO_API_KEY is wrong or was regenerated")
    print("   - BREVO_SENDER_EMAIL is not a verified sender in your Brevo account")
