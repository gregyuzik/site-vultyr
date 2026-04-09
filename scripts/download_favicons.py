#!/usr/bin/env python3
"""
Download favicons from Google's favicon service for all services in services.json.

Saves two sizes per domain:
  - {domain}-32.png  (used in service cards, related cards)
  - {domain}-64.png  (used in service page headers)

Output directory: assets/favicons/
"""

import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
SERVICES_JSON = PROJECT_ROOT / "data" / "services.json"
FAVICONS_DIR = PROJECT_ROOT / "assets" / "favicons"
SIZES = [32, 64]
GOOGLE_FAVICON_URL = "https://www.google.com/s2/favicons?domain={domain}&sz={size}"
MAX_WORKERS = 20
TIMEOUT = 10  # seconds per request


def load_domains():
    """Load unique favicon domains from services.json."""
    with open(SERVICES_JSON) as f:
        data = json.load(f)
    domains = set()
    for service in data["services"]:
        domain = service.get("faviconDomain")
        if domain:
            domains.add(domain)
    return sorted(domains)


def download_favicon(domain, size):
    """Download a single favicon. Returns (domain, size, success, error_msg)."""
    url = GOOGLE_FAVICON_URL.format(domain=domain, size=size)
    out_path = FAVICONS_DIR / f"{domain}-{size}.png"

    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=TIMEOUT) as resp:
            data = resp.read()
            if len(data) < 10:
                return (domain, size, False, "Empty response")
            with open(out_path, "wb") as f:
                f.write(data)
            return (domain, size, True, None)
    except HTTPError as e:
        return (domain, size, False, f"HTTP {e.code}")
    except URLError as e:
        return (domain, size, False, str(e.reason))
    except Exception as e:
        return (domain, size, False, str(e))


def main():
    FAVICONS_DIR.mkdir(parents=True, exist_ok=True)

    domains = load_domains()
    print(f"Found {len(domains)} unique domains in services.json")
    print(f"Downloading favicons at sizes: {SIZES}")
    print(f"Output directory: {FAVICONS_DIR}")
    print()

    # Build task list: (domain, size) pairs
    tasks = [(d, s) for d in domains for s in SIZES]
    total = len(tasks)

    successes = []
    failures = []
    completed = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(download_favicon, d, s): (d, s) for d, s in tasks}
        for future in as_completed(futures):
            domain, size, ok, err = future.result()
            completed += 1
            if ok:
                successes.append((domain, size))
            else:
                failures.append((domain, size, err))
            # Progress every 50
            if completed % 50 == 0 or completed == total:
                print(f"  Progress: {completed}/{total}")

    print()
    print("=" * 60)
    print(f"RESULTS")
    print(f"  Total tasks:    {total}")
    print(f"  Successes:      {len(successes)}")
    print(f"  Failures:       {len(failures)}")
    print()

    if failures:
        print("FAILURES:")
        for domain, size, err in sorted(failures):
            print(f"  {domain} (sz={size}): {err}")
        print()

    # Report unique domains with at least one success
    successful_domains = set(d for d, s in successes)
    failed_domains = set(d for d, s, e in failures) - successful_domains
    print(f"Domains with at least one favicon: {len(successful_domains)}")
    if failed_domains:
        print(f"Domains with NO favicons at all:  {len(failed_domains)}")
        for d in sorted(failed_domains):
            print(f"  - {d}")

    # Directory size
    total_size = sum(f.stat().st_size for f in FAVICONS_DIR.iterdir() if f.is_file())
    print()
    print(f"Total favicons directory size: {total_size:,} bytes ({total_size / 1024:.1f} KB)")
    file_count = len(list(FAVICONS_DIR.glob("*.png")))
    print(f"Total PNG files: {file_count}")

    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
