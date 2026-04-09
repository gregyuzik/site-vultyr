#!/usr/bin/env python3
"""Probe each service's status URL for Statuspage.io API availability.
Updates data/services.json with statuspageApi field where found."""

import json
import os
import urllib.request
import urllib.error
import ssl

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
JSON_PATH = os.path.join(ROOT_DIR, "data", "services.json")

# Don't verify SSL for probing (some status pages have cert issues)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def probe_statuspage_api(status_url):
    """Try to fetch /api/v2/status.json from the status URL domain.
    Returns the API URL if it's a valid Statuspage.io endpoint, else None."""
    if not status_url:
        return None

    # Normalize URL
    base = status_url.rstrip("/")

    # Some status URLs already point to specific pages, get the root
    # e.g., https://developer.apple.com/system-status/ -> not statuspage.io
    api_url = f"{base}/api/v2/status.json"

    try:
        req = urllib.request.Request(api_url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; VultyrProbe/1.0)",
            "Accept": "application/json",
        })
        with urllib.request.urlopen(req, timeout=8, context=ctx) as resp:
            if resp.status != 200:
                return None
            data = json.loads(resp.read().decode())
            # Validate it's a Statuspage.io response
            if "status" in data and "indicator" in data.get("status", {}):
                return api_url
    except Exception:
        pass

    return None


def main():
    with open(JSON_PATH) as f:
        data = json.load(f)

    found = 0
    failed = 0
    total = len(data["services"])

    for i, svc in enumerate(data["services"]):
        name = svc["name"]
        status_url = svc["statusUrl"]
        print(f"[{i+1}/{total}] Probing {name}... ", end="", flush=True)

        api_url = probe_statuspage_api(status_url)
        if api_url:
            svc["statuspageApi"] = api_url
            found += 1
            print(f"OK -> {api_url}")
        else:
            svc["statuspageApi"] = None
            failed += 1
            print("No Statuspage.io API")

    with open(JSON_PATH, "w") as f:
        json.dump(data, f, indent=2)

    print(f"\nDone. {found}/{total} services have Statuspage.io API ({failed} link-only)")


if __name__ == "__main__":
    main()
