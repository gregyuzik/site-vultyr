#!/usr/bin/env python3
"""Probe each service's status URL for Statuspage.io API availability.
Updates data/services.json with statuspageApi field where found."""

import json
import logging
import os
import ssl
import urllib.error
import urllib.request

logger = logging.getLogger(__name__)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
JSON_PATH = os.path.join(ROOT_DIR, "data", "services.json")

# Secure SSL context (default)
_secure_ctx = ssl.create_default_context()

# Insecure fallback for status pages with certificate issues
_insecure_ctx = ssl.create_default_context()
_insecure_ctx.check_hostname = False
_insecure_ctx.verify_mode = ssl.CERT_NONE


def _try_fetch(api_url, ctx):
    """Attempt to fetch and validate a Statuspage.io API endpoint."""
    req = urllib.request.Request(api_url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; VultyrProbe/1.0)",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=8, context=ctx) as resp:
        if resp.status != 200:
            return None
        data = json.loads(resp.read().decode())
        if "status" in data and "indicator" in data.get("status", {}):
            return api_url
    return None


def probe_statuspage_api(status_url):
    """Try to fetch /api/v2/status.json from the status URL domain.
    Returns the API URL if it's a valid Statuspage.io endpoint, else None."""
    if not status_url:
        return None

    base = status_url.rstrip("/")
    api_url = f"{base}/api/v2/status.json"

    # Try with secure SSL first
    try:
        return _try_fetch(api_url, _secure_ctx)
    except ssl.SSLError:
        # Retry with verification disabled for status pages with cert issues
        try:
            return _try_fetch(api_url, _insecure_ctx)
        except (urllib.error.URLError, urllib.error.HTTPError, ssl.SSLError,
                json.JSONDecodeError, TimeoutError, OSError) as exc:
            logger.debug("Probe failed (insecure fallback) for %s: %s", api_url, exc)
    except (urllib.error.URLError, urllib.error.HTTPError,
            json.JSONDecodeError, TimeoutError, OSError) as exc:
        logger.debug("Probe failed for %s: %s", api_url, exc)

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
