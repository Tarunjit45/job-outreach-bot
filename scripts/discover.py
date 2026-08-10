"""
Discovers candidate startup company domains using DuckDuckGo's HTML
search endpoint (no API key / no billing needed).
"""
import re
import time
import random
from urllib.parse import urlparse, unquote

import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"
    )
}

RESULT_LINK_RE = re.compile(r'class="result__a"[^>]*href="([^"]+)"')


def _clean_domain(raw_url: str) -> str | None:
    try:
        if "uddg=" in raw_url:
            raw_url = unquote(raw_url.split("uddg=")[-1].split("&")[0])
        netloc = urlparse(raw_url).netloc.lower()
        return netloc[4:] if netloc.startswith("www.") else netloc
    except Exception:
        return None


def ddg_search_domains(query: str, max_results: int = 15) -> list[str]:
    resp = requests.post(
        "https://html.duckduckgo.com/html/",
        data={"q": query},
        headers=HEADERS,
        timeout=20,
    )
    resp.raise_for_status()
    domains = []
    for link in RESULT_LINK_RE.findall(resp.text):
        domain = _clean_domain(link)
        if domain and domain not in domains:
            domains.append(domain)
    return domains[:max_results]


def discover_new_companies(config: dict, already_known: set[str]) -> list[str]:
    """Runs every configured search query, returns new (unseen) domains."""
    exclude = set(config.get("exclude_domains", []))
    limit = config.get("daily_new_candidates", 10)

    found: list[str] = []
    for query in config.get("search_queries", []):
        try:
            domains = ddg_search_domains(query)
        except Exception as e:
            print(f"  [warn] search failed for '{query}': {e}")
            continue

        for domain in domains:
            if domain in already_known or domain in exclude or domain in found:
                continue
            if any(domain.endswith(bad) for bad in exclude):
                continue
            found.append(domain)
            if len(found) >= limit:
                return found

        time.sleep(random.uniform(1.5, 3.0))  # be polite between queries

    return found
