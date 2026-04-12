#!/usr/bin/env python3
"""Probe each service's status URL for Statuspage.io API availability.
Updates data/services.json with statuspageApi field where found."""

import ipaddress
import json
import logging
import os
import socket
import ssl
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
JSON_PATH = ROOT_DIR / "data" / "services.json"

_SSL_CTX = ssl.create_default_context()
_REQUEST_TIMEOUT = 8


def _is_public_address(hostname):
    """True iff `hostname` resolves only to globally-routable IPv4/IPv6 addresses.
    Blocks SSRF via link-local, loopback, private, or multicast targets."""
    try:
        infos = socket.getaddrinfo(hostname, None)
    except OSError:
        return False
    for family, _, _, _, sockaddr in infos:
        ip_str = sockaddr[0]
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            return False
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved:
            return False
    return True


def _try_fetch(api_url):
    """Attempt to fetch and validate a Statuspage.io API endpoint."""
    req = urllib.request.Request(api_url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; VultyrProbe/1.0)",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=_REQUEST_TIMEOUT, context=_SSL_CTX) as resp:
        if resp.status != 200:
            return None
        data = json.loads(resp.read().decode("utf-8"))
        if "status" in data and "indicator" in data.get("status", {}):
            return api_url
    return None


def probe_statuspage_api(status_url):
    """Try to fetch /api/v2/status.json from the status URL domain.
    Returns the API URL if it's a valid Statuspage.io endpoint, else None."""
    if not status_url:
        return None

    parsed = urlparse(status_url)
    if parsed.scheme != "https" or not parsed.hostname:
        return None
    if not _is_public_address(parsed.hostname):
        logger.debug("Refusing to probe non-public host %s", parsed.hostname)
        return None

    api_url = f"{status_url.rstrip('/')}/api/v2/status.json"

    try:
        return _try_fetch(api_url)
    except (urllib.error.URLError, urllib.error.HTTPError, ssl.SSLError,
            json.JSONDecodeError, TimeoutError, OSError) as exc:
        logger.debug("Probe failed for %s: %s", api_url, exc)
    return None


def main():
    with open(JSON_PATH, encoding="utf-8") as f:
        data = json.load(f)

    found = 0
    failed = 0
    total = len(data["services"])

    for i, svc in enumerate(data["services"]):
        name = svc["name"]
        status_url = svc["statusUrl"]
        print(f"[{i + 1}/{total}] Probing {name}... ", end="", flush=True)

        api_url = probe_statuspage_api(status_url)
        if api_url:
            svc["statuspageApi"] = api_url
            found += 1
            print(f"OK -> {api_url}")
        else:
            svc["statuspageApi"] = None
            failed += 1
            print("No Statuspage.io API")

    # Atomic write: write temp file, then rename.
    tmp_path = JSON_PATH.with_suffix(JSON_PATH.suffix + ".tmp")
    tmp_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp_path, JSON_PATH)

    print(f"\nDone. {found}/{total} services have Statuspage.io API ({failed} link-only)")


if __name__ == "__main__":
    main()
