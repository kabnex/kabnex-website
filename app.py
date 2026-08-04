"""
Kabnex Technologies — website backend
--------------------------------------
Serves the Home, About, Services, and Contact pages, and handles
contact form submissions at POST /api/contact.

Run:
    pip install -r requirements.txt
    python app.py

Then open http://127.0.0.1:5000
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CONTACTS_FILE = DATA_DIR / "contacts.json"


@app.context_processor
def inject_asset_version():
    """Adds ?v=<file-modified-time> to static asset URLs in templates.

    This guarantees that whenever style.css or script.js changes on disk,
    the URL the browser requests changes too — so browsers (and any CDN)
    can never keep serving a stale cached copy after an update.
    """

    def asset_version(rel_path: str) -> int:
        try:
            return int((BASE_DIR / "static" / rel_path).stat().st_mtime)
        except OSError:
            return 0

    return dict(asset_version=asset_version)


COMPANY_EMAIL = "kabishanattudurai@gmail.com"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Optional: set this environment variable to also email each submission to
# COMPANY_EMAIL via the Brevo HTTP API (sends over port 443, so it works even
# on hosts that block outbound SMTP ports). If not set, submissions are still
# saved to data/contacts.json, which is enough to run the site.
BREVO_API_KEY = os.environ.get("BREVO_API_KEY")
BREVO_SENDER_EMAIL = os.environ.get("BREVO_SENDER_EMAIL", COMPANY_EMAIL)


def ensure_data_file():
    DATA_DIR.mkdir(exist_ok=True)
    if not CONTACTS_FILE.exists():
        CONTACTS_FILE.write_text("[]", encoding="utf-8")


def save_submission(entry: dict):
    ensure_data_file()
    with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
        try:
            records = json.load(f)
        except json.JSONDecodeError:
            records = []
    records.append(entry)
    with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)


def try_send_email(entry: dict) -> bool:
    """Best-effort email notification via the Brevo API. Never raises — returns False on failure."""
    if not BREVO_API_KEY:
        print("[email] skipped — BREVO_API_KEY not set.")
        return False
    try:
        text_body = (
            f"Name: {entry['name']}\n"
            f"Email: {entry['email']}\n"
            f"Service: {entry['service']}\n"
            f"Submitted: {entry['submitted_at']}\n\n"
            f"Message:\n{entry['message']}\n"
        )
        resp = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "api-key": BREVO_API_KEY,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json={
                "sender": {"email": BREVO_SENDER_EMAIL, "name": "Kabnex Website"},
                "to": [{"email": COMPANY_EMAIL}],
                "replyTo": {"email": entry["email"], "name": entry["name"]},
                "subject": f"New Kabnex enquiry — {entry['service']}",
                "textContent": text_body,
            },
            timeout=10,
        )
        if resp.status_code >= 300:
            print(f"[email] FAILED to send: {resp.status_code} {resp.text}")
            return False
        print(f"[email] sent to {COMPANY_EMAIL} ok.")
        return True
    except Exception as exc:
        print(f"[email] FAILED to send: {type(exc).__name__}: {exc}")
        return False


@app.route("/")
def home():
    return render_template("home.html", active_page="home")


@app.route("/about")
def about():
    return render_template("about.html", active_page="about")


@app.route("/services")
def services():
    return render_template("services.html", active_page="services")


@app.route("/contact")
def contact():
    return render_template("contact.html", active_page="contact")


@app.route("/api/contact", methods=["POST"])
def api_contact():
    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    service = (data.get("service") or "Not sure yet").strip()
    message = (data.get("message") or "").strip()

    if not name or not email or not message:
        return jsonify(status="error", message="name, email, and message are required."), 400

    if not EMAIL_RE.match(email):
        return jsonify(status="error", message="please enter a valid email address."), 400

    entry = {
        "name": name,
        "email": email,
        "service": service,
        "message": message,
        "submitted_at": datetime.utcnow().isoformat() + "Z",
    }

    save_submission(entry)
    try_send_email(entry)

    return jsonify(status="ok", message="message received."), 200


if __name__ == "__main__":
    ensure_data_file()
    app.run(debug=True)
