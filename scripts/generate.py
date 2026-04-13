#!/usr/bin/env python3
"""Generate services.html, category pages, service pages, 404.html, and sitemap.xml from services.json."""

import base64
import hashlib
import html as html_module
import json
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
JSON_PATH = ROOT_DIR / "data" / "services.json"
STATUS_DIR = ROOT_DIR / "status"
CATEGORIES_DIR = ROOT_DIR / "categories"
FAVICONS_DIR = ROOT_DIR / "assets" / "favicons"
TODAY = date.today().isoformat()

GA_ID = "G-YYDJLZG0X1"
FAVICON_HREF = "/favicon.png?v=20260413"
PLATFORM_DEVICE_LIST = "iPhone, iPad, Mac, Apple Watch, Apple TV, and Vision Pro"

ALLOWED_URL_SCHEMES = {"https", "mailto"}

GA_SNIPPET = f"""    <!-- Google tag (gtag.js) — cookieless, anonymized -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
    <script defer src="/assets/js/analytics.js"></script>"""

FOOTER_HTML = """    <footer>
        <nav aria-label="Footer navigation">
            <a href="/">Home</a>
            <a href="/services.html">Services</a>
            <a href="/privacy.html">Privacy</a>
            <a href="/support.html">Support</a>
            <a href="mailto:support@vultyr.app">Contact</a>
        </nav>
        <p class="copyright">&copy; 2026 Vultyr. All rights reserved.</p>
    </footer>"""


def e(text):
    """HTML-escape text, including attribute quotes."""
    return html_module.escape(str(text), quote=True)


def safe_url(url):
    """Return the URL escaped for HTML attribute use iff its scheme is allowed.
    Raises ValueError on disallowed schemes (javascript:, file:, data:, etc.)."""
    if not url:
        return ""
    parsed = urlparse(str(url))
    if parsed.scheme not in ALLOWED_URL_SCHEMES:
        raise ValueError(f"disallowed URL scheme {parsed.scheme!r} in {url!r}")
    return e(url)


def csp_hash(content):
    """Return a CSP sha256 hash token for inline script content."""
    digest = hashlib.sha256(content.encode("utf-8")).digest()
    return f"'sha256-{base64.b64encode(digest).decode('ascii')}'"


def build_csp(script_hashes=()):
    """Build a CSP that avoids unsafe-inline while allowing hashed JSON-LD."""
    script_src = ["'self'", "https://www.googletagmanager.com", *script_hashes]
    directives = [
        "default-src 'self'",
        f"script-src {' '.join(script_src)}",
        "style-src 'self'",
        "font-src 'self'",
        "img-src 'self' data:",
        "connect-src 'self' https://www.google-analytics.com https://*.analytics.google.com https://www.googletagmanager.com",
        "frame-ancestors 'none'",
        "object-src 'none'",
        "base-uri 'self'",
        "form-action 'none'",
    ]
    return "; ".join(directives)


def head_common(script_hashes=()):
    """Shared head tags plus a per-page CSP."""
    return "\n".join([
        '    <meta charset="UTF-8">',
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f'    <meta http-equiv="Content-Security-Policy" content="{build_csp(script_hashes=script_hashes)}">',
    ])


def json_ld_block(obj):
    """Return a JSON-LD block and matching CSP hash."""
    body = json.dumps(obj, indent=2, ensure_ascii=False).replace("</", "<\\/")
    content = f"\n{body}\n"
    return f'    <script type="application/ld+json">{content}</script>', csp_hash(content)


def load_data():
    """Load services data with error handling."""
    try:
        with open(JSON_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Error loading {JSON_PATH}: {exc}")
        raise SystemExit(1)


def write_file(path, content):
    """Write content to a file as UTF-8."""
    try:
        Path(path).write_text(content, encoding="utf-8")
    except OSError as exc:
        print(f"Error writing {path}: {exc}")
        raise SystemExit(1)


def prune_generated_dir(directory, expected_names):
    """Remove generated HTML files that no longer exist in the source data."""
    removed = []
    for path in sorted(directory.glob("*.html")):
        if path.name not in expected_names:
            path.unlink()
            removed.append(path.name)
    return removed


_PLACEHOLDER = (
    "data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20"
    "viewBox%3D%220%200%2032%2032%22%3E%3Crect%20width%3D%2232%22%20height%3D%2232%22%20"
    "rx%3D%226%22%20fill%3D%22%231a1a1a%22%2F%3E%3C%2Fsvg%3E"
)


def build_favicon_lookup():
    """Scan FAVICONS_DIR once. Return a callable(domain, size) -> path, falling
    back to an inline SVG data URL placeholder if no local PNG exists. No
    runtime requests to external favicon services."""
    have = set()
    if FAVICONS_DIR.is_dir():
        for f in FAVICONS_DIR.glob("*.png"):
            have.add(f.name)

    missing = set()

    def resolve(domain, size):
        if domain and f"{domain}-{size}.png" in have:
            return f"/assets/favicons/{domain}-{size}.png"
        if domain:
            missing.add(f"{domain}-{size}")
        return _PLACEHOLDER

    resolve.missing = missing
    return resolve


# ─── SERVICES.HTML ─────────────────────────────────────────────────────────────

def generate_services_page(data, favicon):
    services_by_slug = {s["slug"]: s for s in data["services"]}
    categories = data["categories"]
    total = len(data["services"])

    title = f"Vultyr — {total}+ Monitored Services"
    description = (
        f"All {total}+ services monitored by Vultyr, organized by category. "
        "Cloud, dev tools, communication, AI, and more."
    )

    # Category pills at top
    cat_pills = "\n".join(
        f'        <a class="cat-pill" href="/categories/{e(cat["slug"])}.html">'
        f'{e(cat["name"])} <span>{len(cat["serviceSlugs"])}</span></a>'
        for cat in categories
    )

    # Per-category sections
    sections = []
    for cat in categories:
        rows = []
        for ss in cat["serviceSlugs"]:
            svc = services_by_slug.get(ss)
            if not svc:
                continue
            fav = favicon(svc["faviconDomain"], 32)
            status_href = safe_url(svc["statusUrl"])
            home_href = safe_url(svc["homepageUrl"])
            rows.append(
                f'            <div class="service">\n'
                f'                <img class="service-favicon" src="{fav}" alt="" width="24" height="24" loading="lazy" decoding="async" aria-hidden="true">\n'
                f'                <div class="service-name"><a href="/status/{e(svc["slug"])}.html">{e(svc["name"])}</a></div>\n'
                f'                <div class="service-links">\n'
                f'                    <a href="{status_href}" target="_blank" rel="noopener noreferrer">Status Page</a>\n'
                f'                    <a href="{home_href}" target="_blank" rel="noopener noreferrer">Homepage</a>\n'
                f'                </div>\n'
                f'            </div>'
            )
        rows_html = "\n".join(rows)
        sections.append(
            f'        <div class="category">\n'
            f'            <h2><a href="/categories/{e(cat["slug"])}.html">{e(cat["name"])}</a> '
            f'<span>{len(cat["serviceSlugs"])} services</span></h2>\n'
            f'{rows_html}\n'
            f'        </div>'
        )
    sections_html = "\n\n".join(sections)

    # ItemList JSON-LD (numbered list of every service)
    item_list_ld = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Services Monitored by Vultyr",
        "numberOfItems": total,
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": svc["name"],
                "url": f"https://vultyr.app/status/{svc['slug']}.html",
            }
            for i, svc in enumerate(data["services"])
        ],
    }

    item_list_ld_html, item_list_ld_hash = json_ld_block(item_list_ld)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{head_common(script_hashes=(item_list_ld_hash,))}
    <title>{e(title)}</title>
    <meta name="description" content="{e(description)}">
    <meta name="theme-color" content="#000000">
    <meta property="og:title" content="{e(title)}">
    <meta property="og:description" content="{e(description)}">
    <meta property="og:image" content="https://vultyr.app/icon.png">
    <meta property="og:url" content="https://vultyr.app/services.html">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{e(title)}">
    <meta name="twitter:description" content="{e(description)}">
    <meta name="twitter:image" content="https://vultyr.app/icon.png">
    <link rel="canonical" href="https://vultyr.app/services.html">
    <link rel="apple-touch-icon" href="/icon.png">
    <link rel="icon" type="image/png" sizes="64x64" href="{FAVICON_HREF}">
    <link rel="stylesheet" href="/assets/css/shared.css">
    <link rel="stylesheet" href="/assets/css/services-list.css">
{item_list_ld_html}
{GA_SNIPPET}
</head>
<body>
    <a href="#main" class="sr-only">Skip to main content</a>
    <main id="main">
    <div class="header">
        <a href="/">&larr; Back to vultyr</a>
        <h1>Monitored <span class="highlight-orange">Services</span></h1>
        <p class="subtitle">All {total} services vultyr actively monitors via status APIs.</p>
    </div>

    <nav class="content categories-nav" aria-label="Browse by category">
{cat_pills}
    </nav>

    <div class="content">
{sections_html}
    </div>
    </main>

{FOOTER_HTML}
</body>
</html>
"""


# ─── SERVICE PAGE ──────────────────────────────────────────────────────────────

def generate_service_page(svc, categories_lookup, all_services_by_slug, total_services, favicon):
    name = svc["name"]
    slug = svc["slug"]
    favicon_domain = svc["faviconDomain"]
    status_url = svc["statusUrl"]
    homepage_url = svc["homepageUrl"]
    cat_slugs = svc["categories"] or []

    if not cat_slugs:
        print(f"Error: service {slug!r} has no categories")
        raise SystemExit(1)

    primary_cat = categories_lookup.get(cat_slugs[0], {"name": cat_slugs[0], "slug": cat_slugs[0]})

    related = []
    primary_cat_data = categories_lookup.get(cat_slugs[0], {})
    for rs in primary_cat_data.get("serviceSlugs", []):
        if rs != slug and rs in all_services_by_slug:
            related.append(all_services_by_slug[rs])
            if len(related) >= 6:
                break

    breadcrumb_ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Vultyr", "item": "https://vultyr.app"},
            {"@type": "ListItem", "position": 2, "name": "Services", "item": "https://vultyr.app/services.html"},
            {"@type": "ListItem", "position": 3, "name": primary_cat["name"],
             "item": f"https://vultyr.app/categories/{primary_cat['slug']}.html"},
            {"@type": "ListItem", "position": 4, "name": name},
        ],
    }

    faq_ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": f"Is {name} down right now?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": f"Check the official {name} status page at {status_url} for current status. Download the free Vultyr app for instant outage alerts on all your Apple devices.",
                },
            },
            {
                "@type": "Question",
                "name": f"How can I monitor {name} status?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": f"Download Vultyr (free) to monitor {name} and {total_services}+ other services with real-time alerts on {PLATFORM_DEVICE_LIST}. Vultyr checks service status automatically and notifies you the moment an outage is detected.",
                },
            },
        ],
    }

    breadcrumb_html = f'''        <nav class="breadcrumb" aria-label="Breadcrumb">
            <a href="/">Vultyr</a><span class="sep" aria-hidden="true">&rsaquo;</span>
            <a href="/services.html">Services</a><span class="sep" aria-hidden="true">&rsaquo;</span>
            <a href="/categories/{e(primary_cat["slug"])}.html">{e(primary_cat["name"])}</a><span class="sep" aria-hidden="true">&rsaquo;</span>
            <span class="breadcrumb-current" aria-current="page">{e(name)}</span>
        </nav>'''

    related_html = ""
    if related:
        cards = ""
        for rs in related:
            cards += (
                f'                <a class="related-card" href="/status/{e(rs["slug"])}.html">\n'
                f'                    <img src="{favicon(rs["faviconDomain"], 32)}" alt="" width="20" height="20" loading="lazy" decoding="async" aria-hidden="true">\n'
                f'                    {e(rs["name"])}\n'
                f'                </a>\n'
            )
        related_html = (
            f'        <h2 class="section-title">Related Services</h2>\n'
            f'        <nav class="related-grid" aria-label="Related services">\n'
            f'{cards}        </nav>'
        )

    cat_links_html = ""
    if len(cat_slugs) > 1:
        links = ", ".join(
            f'<a href="/categories/{e(cs)}.html" class="highlight-orange">'
            f'{e(categories_lookup.get(cs, {}).get("name", cs))}</a>'
            for cs in cat_slugs
        )
        cat_links_html = f'        <p class="category-note">Categories: {links}</p>'

    title = f"Is {name} Down? {name} Status Monitor | Vultyr"
    description = (
        f"Check if {name} is down right now. Live {name} status updates and outage monitoring with Vultyr. "
        f"Free on {PLATFORM_DEVICE_LIST}."
    )

    status_href = safe_url(status_url)
    home_href = safe_url(homepage_url)
    breadcrumb_ld_html, breadcrumb_ld_hash = json_ld_block(breadcrumb_ld)
    faq_ld_html, faq_ld_hash = json_ld_block(faq_ld)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{head_common(script_hashes=(breadcrumb_ld_hash, faq_ld_hash))}
    <title>{e(title)}</title>
    <meta name="description" content="{e(description)}">
    <meta name="theme-color" content="#000000">
    <meta property="og:title" content="{e(title)}">
    <meta property="og:description" content="{e(description)}">
    <meta property="og:image" content="https://vultyr.app/icon.png">
    <meta property="og:url" content="https://vultyr.app/status/{e(slug)}.html">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{e(title)}">
    <meta name="twitter:description" content="{e(description)}">
    <meta name="twitter:image" content="https://vultyr.app/icon.png">
    <link rel="canonical" href="https://vultyr.app/status/{e(slug)}.html">
    <link rel="apple-touch-icon" href="/icon.png">
    <link rel="icon" type="image/png" sizes="64x64" href="{FAVICON_HREF}">
    <link rel="stylesheet" href="/assets/css/shared.css">
    <link rel="stylesheet" href="/assets/css/service.css">
{breadcrumb_ld_html}
{faq_ld_html}
{GA_SNIPPET}
</head>
<body>
    <a href="#main" class="sr-only">Skip to main content</a>
    <main id="main">
    <div class="container">
{breadcrumb_html}
        <div class="service-header">
            <img src="{favicon(favicon_domain, 64)}" alt="" width="48" height="48" decoding="async" aria-hidden="true">
            <h1>{e(name)}</h1>
        </div>

        <div class="status-card">
            <a href="{status_href}" target="_blank" rel="noopener noreferrer" class="status-badge">
                <span class="status-text">View Current Status &rarr;</span>
            </a>
            <p class="status-time">For live alerts, <a href="https://apps.apple.com/us/app/vultyr/id6761264004">download Vultyr</a></p>
        </div>
{cat_links_html}
        <div class="links-row">
            <a href="{status_href}" target="_blank" rel="noopener noreferrer">
                <svg width="16" height="16" viewBox="0 0 256 256" fill="currentColor" aria-hidden="true" focusable="false"><path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24Zm-26.37,144H96a8,8,0,0,1-8-8V96a8,8,0,0,1,8-8h5.63a8,8,0,0,1,5.66,2.34l56,56a8,8,0,0,1-11.32,11.32L101.63,107.31V160A8,8,0,0,1,101.63,168Z"/></svg>
                Official Status Page
            </a>
            <a href="{home_href}" target="_blank" rel="noopener noreferrer">
                <svg width="16" height="16" viewBox="0 0 256 256" fill="currentColor" aria-hidden="true" focusable="false"><path d="M128,16a112,112,0,1,0,112,112A112.13,112.13,0,0,0,128,16ZM40,128a87.5,87.5,0,0,1,8.43-37.65l46.46,127.38A88.14,88.14,0,0,1,40,128Zm88,88a87.53,87.53,0,0,1-28.34-4.67l30.09-87.39,30.83,84.49A88.18,88.18,0,0,1,128,216Z"/></svg>
                {e(name)} Homepage
            </a>
        </div>

        <h2 class="section-title">FAQ</h2>
        <div class="faq">
            <h3>Is {e(name)} down right now?</h3>
            <p>Check the official {e(name)} status page linked above for current status. For continuous monitoring with instant outage alerts on all your Apple devices, download the free Vultyr app.</p>
        </div>
        <div class="faq">
            <h3>How can I monitor {e(name)} status?</h3>
            <p>Vultyr monitors {e(name)} and {total_services}+ other cloud services, dev tools, and platforms. Get instant outage alerts on {PLATFORM_DEVICE_LIST} — completely free.</p>
        </div>

{related_html}
        <div class="cta">
            <h2>Monitor {e(name)} on all your devices</h2>
            <p>Get instant alerts when {e(name)} goes down. Free on all Apple platforms.</p>
            <a href="https://apps.apple.com/us/app/vultyr/id6761264004" aria-label="Download Vultyr on the App Store">Download Vultyr</a>
        </div>
    </div>
    </main>
{FOOTER_HTML}
</body>
</html>
"""


# ─── CATEGORY PAGE ─────────────────────────────────────────────────────────────

def generate_category_page(cat, all_services_by_slug, all_categories, favicon):
    name = cat["name"]
    slug = cat["slug"]
    icon = cat.get("icon", "")
    service_slugs = cat["serviceSlugs"]
    count = len(service_slugs)

    cards = ""
    for ss in service_slugs:
        svc = all_services_by_slug.get(ss)
        if not svc:
            continue
        cards += (
            f'            <a class="service-card" href="/status/{e(svc["slug"])}.html">\n'
            f'                <img src="{favicon(svc["faviconDomain"], 32)}" alt="" width="24" height="24" loading="lazy" decoding="async" aria-hidden="true">\n'
            f'                <span>{e(svc["name"])}</span>\n'
            f'            </a>\n'
        )

    other_cats = ""
    for oc in all_categories:
        if oc["slug"] != slug:
            other_cats += (
                f'                <a class="cat-link" href="/categories/{e(oc["slug"])}.html">'
                f'{e(oc["name"])}</a>\n'
            )

    icon_html = ""
    if icon:
        icon_path = ROOT_DIR / "assets" / "icons" / icon
        if icon_path.exists():
            try:
                svg = icon_path.read_text(encoding="utf-8")
                svg = svg.replace("<svg", '<svg class="cat-icon" aria-hidden="true" focusable="false"', 1)
                icon_html = svg
            except OSError as exc:
                print(f"Warning: could not read icon {icon_path}: {exc}")

    breadcrumb_ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Vultyr", "item": "https://vultyr.app"},
            {"@type": "ListItem", "position": 2, "name": "Services", "item": "https://vultyr.app/services.html"},
            {"@type": "ListItem", "position": 3, "name": name},
        ],
    }

    item_list_ld = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": f"{name} Status Monitors",
        "numberOfItems": count,
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": all_services_by_slug[ss]["name"],
                "url": f"https://vultyr.app/status/{all_services_by_slug[ss]['slug']}.html",
            }
            for i, ss in enumerate(service_slugs)
            if ss in all_services_by_slug
        ],
    }

    title = f"{name} Status Monitor — {count} Services | Vultyr"
    sample_names = ", ".join(
        all_services_by_slug[s]["name"]
        for s in service_slugs[:4]
        if s in all_services_by_slug
    )
    description = f"Monitor the status of {count} {name.lower()} services. Real-time outage alerts for {sample_names}, and more."

    breadcrumb_ld_html, breadcrumb_ld_hash = json_ld_block(breadcrumb_ld)
    item_list_ld_html, item_list_ld_hash = json_ld_block(item_list_ld)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{head_common(script_hashes=(breadcrumb_ld_hash, item_list_ld_hash))}
    <title>{e(title)}</title>
    <meta name="description" content="{e(description)}">
    <meta name="theme-color" content="#000000">
    <meta property="og:title" content="{e(title)}">
    <meta property="og:description" content="{e(description)}">
    <meta property="og:image" content="https://vultyr.app/icon.png">
    <meta property="og:url" content="https://vultyr.app/categories/{e(slug)}.html">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{e(title)}">
    <meta name="twitter:description" content="{e(description)}">
    <meta name="twitter:image" content="https://vultyr.app/icon.png">
    <link rel="canonical" href="https://vultyr.app/categories/{e(slug)}.html">
    <link rel="apple-touch-icon" href="/icon.png">
    <link rel="icon" type="image/png" sizes="64x64" href="{FAVICON_HREF}">
    <link rel="stylesheet" href="/assets/css/shared.css">
    <link rel="stylesheet" href="/assets/css/category.css">
{breadcrumb_ld_html}
{item_list_ld_html}
{GA_SNIPPET}
</head>
<body>
    <a href="#main" class="sr-only">Skip to main content</a>
    <main id="main">
    <div class="container">
        <nav class="breadcrumb" aria-label="Breadcrumb">
            <a href="/">Vultyr</a><span class="sep" aria-hidden="true">&rsaquo;</span>
            <a href="/services.html">Services</a><span class="sep" aria-hidden="true">&rsaquo;</span>
            <span class="breadcrumb-current" aria-current="page">{e(name)}</span>
        </nav>

        <div class="cat-header">
            {icon_html}
            <h1>{e(name)}</h1>
        </div>
        <p class="cat-subtitle">{count} services monitored by Vultyr</p>

        <nav class="services-grid" aria-label="{e(name)} services">
{cards}        </nav>

        <nav class="other-categories" aria-labelledby="other-cats-heading">
            <h2 id="other-cats-heading">Other Categories</h2>
            <div class="cat-links">
{other_cats}            </div>
        </nav>

        <div class="cta">
            <h2>Monitor all {count} services instantly</h2>
            <p>Get real-time outage alerts on all your Apple devices. Free.</p>
            <a href="https://apps.apple.com/us/app/vultyr/id6761264004" aria-label="Download Vultyr on the App Store">Download Vultyr</a>
        </div>
    </div>
    </main>
{FOOTER_HTML}
</body>
</html>
"""


# ─── 404 PAGE ──────────────────────────────────────────────────────────────────

def generate_404(data, favicon):
    # Popular services and all categories for recovery navigation.
    popular = ["aws", "github", "cloudflare", "slack", "stripe", "discord", "openai", "anthropic"]
    services_by_slug = {s["slug"]: s for s in data["services"]}
    popular_links = []
    for slug in popular:
        svc = services_by_slug.get(slug)
        if svc:
            popular_links.append(
                f'            <a href="/status/{e(slug)}.html">'
                f'<img src="{favicon(svc["faviconDomain"], 32)}" alt="" width="20" height="20" loading="lazy" decoding="async" aria-hidden="true"> '
                f'{e(svc["name"])}</a>'
            )
    popular_html = "\n".join(popular_links)

    cat_links = "\n".join(
        f'            <a class="cat-link" href="/categories/{e(c["slug"])}.html">{e(c["name"])}</a>'
        for c in data["categories"]
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{head_common()}
    <title>Page Not Found — Vultyr</title>
    <meta name="description" content="The page you're looking for doesn't exist.">
    <meta name="theme-color" content="#000000">
    <meta name="robots" content="noindex">
    <link rel="apple-touch-icon" href="/icon.png">
    <link rel="icon" type="image/png" sizes="64x64" href="{FAVICON_HREF}">
    <link rel="stylesheet" href="/assets/css/shared.css">
    <link rel="stylesheet" href="/assets/css/404.css">
{GA_SNIPPET}
</head>
<body>
    <a href="#main" class="sr-only">Skip to main content</a>
    <main id="main" class="error-main">
        <p class="error-code" aria-hidden="true">404</p>
        <h1 class="error-title">Page not found</h1>
        <p class="error-message">The page you're looking for doesn't exist or has been moved.</p>

        <div class="error-section">
            <h2>Popular services</h2>
            <div class="popular">
{popular_html}
            </div>
        </div>

        <div class="error-section">
            <h2>Browse categories</h2>
            <div class="cat-links">
{cat_links}
            </div>
        </div>
    </main>
{FOOTER_HTML}
</body>
</html>
"""


# ─── SITEMAP ───────────────────────────────────────────────────────────────────

def generate_sitemap(services, categories):
    urls = ["https://vultyr.app/",
            "https://vultyr.app/services.html",
            "https://vultyr.app/support.html",
            "https://vultyr.app/privacy.html"]
    for cat in categories:
        urls.append(f"https://vultyr.app/categories/{cat['slug']}.html")
    for svc in services:
        urls.append(f"https://vultyr.app/status/{svc['slug']}.html")

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        lines.append(f"    <lastmod>{TODAY}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


# ─── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    data = load_data()
    services = data["services"]
    categories = data["categories"]

    services_by_slug = {s["slug"]: s for s in services}
    categories_by_slug = {c["slug"]: c for c in categories}
    favicon = build_favicon_lookup()

    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    CATEGORIES_DIR.mkdir(parents=True, exist_ok=True)

    total_services = len(services)

    print(f"Generating services.html...")
    write_file(ROOT_DIR / "services.html", generate_services_page(data, favicon))

    print(f"Generating {total_services} service pages...")
    for svc in services:
        html = generate_service_page(svc, categories_by_slug, services_by_slug, total_services, favicon)
        write_file(STATUS_DIR / f"{svc['slug']}.html", html)
    removed_status = prune_generated_dir(STATUS_DIR, {f"{svc['slug']}.html" for svc in services})

    print(f"Generating {len(categories)} category pages...")
    for cat in categories:
        html = generate_category_page(cat, services_by_slug, categories, favicon)
        write_file(CATEGORIES_DIR / f"{cat['slug']}.html", html)
    removed_categories = prune_generated_dir(CATEGORIES_DIR, {f"{cat['slug']}.html" for cat in categories})

    print("Generating 404.html...")
    write_file(ROOT_DIR / "404.html", generate_404(data, favicon))

    print("Generating sitemap.xml...")
    write_file(ROOT_DIR / "sitemap.xml", generate_sitemap(services, categories))

    total = total_services + len(categories) + 3  # +3 for services, 404, sitemap
    print(f"\nDone! Generated {total} files:")
    print(f"  services.html")
    print(f"  {total_services} service pages in /status/")
    print(f"  {len(categories)} category pages in /categories/")
    print(f"  404.html")
    print(f"  sitemap.xml ({total_services + len(categories) + 4} URLs)")
    if removed_status or removed_categories:
        print(f"  Removed {len(removed_status) + len(removed_categories)} stale generated page(s)")

    if favicon.missing:
        print(f"\nWarning: {len(favicon.missing)} missing favicon(s), using placeholder:")
        for m in sorted(favicon.missing):
            print(f"  {m}")
        print("Run scripts/download_favicons.py to fetch them.")


if __name__ == "__main__":
    main()
