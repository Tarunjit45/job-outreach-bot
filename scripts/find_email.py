"""
For a given company domain, tries to find a public HR / careers /
contact email by scraping the homepage plus a few common subpages.
"""
import re
import time
import random

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"
    )
}

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

# Junk / template-generated addresses to ignore
BAD_SNIPPETS = [
    "example.com", "sentry.io", "wixpress.com", "godaddy.com",
    "yourdomain", "domain.com", ".png", ".jpg", ".jpeg", ".svg",
    "schema.org", "w3.org",
]

# Prefer emails that look like they go to a real hiring inbox
PREFERRED_PREFIXES = ["hr", "career", "careers", "job", "jobs", "talent", "people", "recruit"]

CANDIDATE_PATHS = ["", "/careers", "/jobs", "/contact", "/contact-us", "/about", "/about-us"]


def _fetch(url: str) -> str | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=12)
        if resp.status_code == 200:
            return resp.text
    except Exception:
        pass
    return None


def _extract_emails(html: str) -> list[str]:
    emails = set(EMAIL_RE.findall(html))
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.select('a[href^="mailto:"]'):
        addr = a["href"].split("mailto:")[-1].split("?")[0].strip()
        if addr:
            emails.add(addr)
    return [e for e in emails if not any(bad in e.lower() for bad in BAD_SNIPPETS)]


def find_company_email(domain: str) -> str | None:
    found: list[str] = []
    for path in CANDIDATE_PATHS:
        for scheme in ("https://", "http://"):
            html = _fetch(f"{scheme}{domain}{path}")
            if html:
                found.extend(_extract_emails(html))
                break  # https worked or we already tried http fallback
        if found:
            break  # stop as soon as one page yields emails
        time.sleep(random.uniform(0.5, 1.2))

    if not found:
        return None

    # Prefer an address that matches the company's own domain
    same_domain = [e for e in found if domain in e.lower()]
    pool = same_domain or found

    for prefix in PREFERRED_PREFIXES:
        for email in pool:
            if email.lower().startswith(prefix):
                return email

    return pool[0]
