"""
Quick standalone test for the Gmail App Password setup.
Run this BEFORE testing through the website — it isolates the
email step so you know immediately whether the problem is your
credentials or something else.

Usage:
    export KABNEX_SMTP_USER="kabnextechnologies@gmail.com"
    export KABNEX_SMTP_PASS="your-16-character-app-password"
    python test_email.py
"""

import os
import smtplib
from email.message import EmailMessage

SMTP_USER = os.environ.get("KABNEX_SMTP_USER")
SMTP_PASS = os.environ.get("KABNEX_SMTP_PASS")
COMPANY_EMAIL = "kabnextechnologies@gmail.com"

print("Checking environment variables...")
if not SMTP_USER:
    print("  ✗ KABNEX_SMTP_USER is NOT set.")
else:
    print(f"  ✓ KABNEX_SMTP_USER = {SMTP_USER}")

if not SMTP_PASS:
    print("  ✗ KABNEX_SMTP_PASS is NOT set.")
else:
    masked = SMTP_PASS[:2] + "*" * (len(SMTP_PASS) - 2)
    print(f"  ✓ KABNEX_SMTP_PASS = {masked} ({len(SMTP_PASS)} characters)")
    if len(SMTP_PASS.replace(' ', '')) != 16:
        print("  ⚠ Gmail App Passwords are normally 16 characters (spaces don't count).")
        print("    Double-check you copied the whole thing.")

if not (SMTP_USER and SMTP_PASS):
    print("\nSet both variables first, then re-run this script.")
    raise SystemExit(1)

print("\nConnecting to smtp.gmail.com and attempting to send a test email...")
try:
    msg = EmailMessage()
    msg["Subject"] = "Kabnex — SMTP test email"
    msg["From"] = SMTP_USER
    msg["To"] = COMPANY_EMAIL
    msg.set_content("This is a test email from test_email.py — if you got this, your SMTP setup works.")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

    print(f"✓ SUCCESS — test email sent to {COMPANY_EMAIL}. Check the inbox (and spam folder).")
except smtplib.SMTPAuthenticationError as exc:
    print(f"✗ AUTH FAILED — Gmail rejected the username/password: {exc}")
    print("  Most common causes:")
    print("  - This is your normal Gmail password, not an App Password (won't work)")
    print("  - 2-Step Verification isn't enabled on this Google account")
    print("  - The App Password was copied incorrectly (extra space, missing character)")
except Exception as exc:
    print(f"✗ FAILED — {type(exc).__name__}: {exc}")
