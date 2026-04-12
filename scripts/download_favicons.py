#!/usr/bin/env python3
"""
Download favicons from Google's favicon service for all services in services.json.

Saves two sizes per domain:
  - {domain}-32.png  (used in service cards, related cards)
  - {domain}-64.png  (used in service page headers)

Output directory: assets/favicons/
"""

import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
SERVICES_JSON = PROJECT_ROOT / "data" / "services.json"
FAVICONS_DIR = PROJECT_ROOT / "assets" / "favicons"
SIZES = [32, 64]
GOOGLE_FAVICON_URL = "https://www.google.com/s2/favicons?domain={domain}&sz={size}"
MAX_WORKERS = 6  # Google rate-limits aggressive concurrency
TIMEOUT = 10  # seconds per request

# Allow only the subset of characters that make up real DNS labels.
_SAFE_DOMAIN = re.compile(r"^[a-z0-9][a-z0-9.\-]*$")


def load_domains():
    """Load unique favicon domains from services.json."""
    with open(SERVICES_JSON, encoding="utf-8") as f:
        data = json.load(f)
    domains = set()
    for service in data["services"]:
        domain = service.get("faviconDomain")
        if domain:
            domains.add(domain)
    return sorted(domains)


def download_favicon(domain, size):
    """Download a single favicon. Returns (domain, size, success, error_msg)."""
    if not _SAFE_DOMAIN.match(domain):
        return (domain, size, False, f"Unsafe domain {domain!r}")

    url = GOOGLE_FAVICON_URL.format(domain=domain, size=size)
    out_path = FAVICONS_DIR / f"{domain}-{size}.png"

    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=TIMEOUT) as resp:
            data = resp.read()
            if len(data) < 10:
                return (domain, size, False, "Empty response")
            out_path.write_bytes(data)
            return (domain, size, True, None)
    except HTTPError as exc:
        return (domain, size, False, f"HTTP {exc.code}")
    except URLError as exc:
        return (domain, size, False, str(exc.reason))
    except (OSError, TimeoutError) as exc:
        return (domain, size, False, str(exc))


def main():
    FAVICONS_DIR.mkdir(parents=True, exist_ok=True)

    domains = load_domains()
    print(f"Found {len(domains)} unique domains in services.json")
    print(f"Downloading favicons at sizes: {SIZES}")
    print(f"Output directory: {FAVICONS_DIR}\n")

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
            if completed % 50 == 0 or completed == total:
                print(f"  Progress: {completed}/{total}")

    print()
    print("=" * 60)
    print("RESULTS")
    print(f"  Total tasks:    {total}")
    print(f"  Successes:      {len(successes)}")
    print(f"  Failures:       {len(failures)}\n")

    if failures:
        print("FAILURES:")
        for domain, size, err in sorted(failures):
            print(f"  {domain} (sz={size}): {err}")
        print()

    successful_domains = {d for d, _ in successes}
    failed_domains = {d for d, _, _ in failures} - successful_domains
    print(f"Domains with at least one favicon: {len(successful_domains)}")
    if failed_domains:
        print(f"Domains with NO favicons at all:  {len(failed_domains)}")
        for d in sorted(failed_domains):
            print(f"  - {d}")

    total_size = sum(f.stat().st_size for f in FAVICONS_DIR.iterdir() if f.is_file())
    file_count = len(list(FAVICONS_DIR.glob("*.png")))
    print()
    print(f"Total favicons directory size: {total_size:,} bytes ({total_size / 1024:.1f} KB)")
    print(f"Total PNG files: {file_count}")

    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
