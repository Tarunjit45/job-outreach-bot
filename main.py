"""
Daily job-outreach bot.
Run order: discover new companies -> find emails -> send -> log.
State lives in data/*.json and is committed back to the repo by
the GitHub Actions workflow, so nothing is ever emailed twice.
"""
import json
import os
import time
import random

import yaml

from scripts.discover import discover_new_companies
from scripts.find_email import find_company_email
from scripts.mailer import send_outreach_email

DATA_DIR = "data"
SENT_LOG = os.path.join(DATA_DIR, "sent_log.json")       # {domain: {email, date, company}}
SKIPPED_LOG = os.path.join(DATA_DIR, "skipped_log.json")  # {domain: reason}


def _load(path: str) -> dict:
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}


def _save(path: str, data: dict) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, sort_keys=True)


def main() -> None:
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    sent_log = _load(SENT_LOG)
    skipped_log = _load(SKIPPED_LOG)
    already_known = set(sent_log.keys()) | set(skipped_log.keys())

    print(f"Already contacted or skipped: {len(already_known)} companies")

    print("Discovering new candidate companies...")
    candidates = discover_new_companies(config, already_known)
    print(f"  found {len(candidates)} new candidates: {candidates}")

    sends_today = 0
    daily_send_limit = config.get("daily_send_limit", 8)

    for domain in candidates:
        if sends_today >= daily_send_limit:
            print("Daily send limit reached — stopping for today.")
            break

        print(f"Looking up email for {domain}...")
        email = None
        try:
            email = find_company_email(domain)
        except Exception as e:
            print(f"  [error] lookup failed for {domain}: {e}")

        if not email:
            print(f"  no public email found for {domain} — skipping")
            skipped_log[domain] = {"reason": "no_email_found"}
            continue

        company_name = domain.split(".")[0].capitalize()
        try:
            send_outreach_email(email, company_name, config)  # company_name kept for logging only
            print(f"  sent to {email} ({domain})")
            sent_log[domain] = {
                "email": email,
                "company": company_name,
                "date": time.strftime("%Y-%m-%d"),
            }
            sends_today += 1
        except Exception as e:
            print(f"  [error] send failed for {domain}: {e}")
            skipped_log[domain] = {"reason": f"send_failed: {e}"}

        time.sleep(random.uniform(2, 5))  # small gap between sends

    _save(SENT_LOG, sent_log)
    _save(SKIPPED_LOG, skipped_log)
    print(f"Done. Sent {sends_today} new emails this run.")


if __name__ == "__main__":
    main()
