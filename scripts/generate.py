#!/usr/bin/env python3
"""Generate service pages, category pages, 404.html, and sitemap.xml from services.json."""

import json
import os
import html as html_module
from datetime import date

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
JSON_PATH = os.path.join(ROOT_DIR, "data", "services.json")
STATUS_DIR = os.path.join(ROOT_DIR, "status")
CATEGORIES_DIR = os.path.join(ROOT_DIR, "categories")
TODAY = date.today().isoformat()
ELLIPSIS = "\u2026"

GA_SNIPPET = """    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-YYDJLZG0X1"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag("js", new Date());
      gtag("config", "G-YYDJLZG0X1");
    </script>"""

CSP_META = """    <meta http-equiv="Content-Security-Policy" content="default-src 'self' https:; script-src 'self' 'unsafe-inline' https://www.googletagmanager.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' https: data:;">"""

FOOTER_HTML = """    <footer>
        <nav aria-label="Footer navigation">
            <a href="/services.html">Services</a>
            <a href="/privacy.html">Privacy</a>
            <a href="/support.html">Support</a>
            <a href="mailto:support@vultyr.app">Contact</a>
        </nav>
        <p class="copyright">&copy; 2026 Vultyr. All rights reserved.</p>
    </footer>"""


def e(text):
    """HTML-escape text."""
    return html_module.escape(str(text))


def load_data():
    """Load services data with error handling."""
    try:
        with open(JSON_PATH) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Error loading {JSON_PATH}: {exc}")
        raise SystemExit(1)


def write_file(path, content):
    """Write content to a file with error handling."""
    try:
        with open(path, "w") as f:
            f.write(content)
    except OSError as exc:
        print(f"Error writing {path}: {exc}")
        raise SystemExit(1)


def json_ld(obj):
    """Render a JSON-LD script tag."""
    return f'    <script type="application/ld+json">\n    {json.dumps(obj, indent=2).replace(chr(10), chr(10) + "    ")}\n    </script>'


# ─── SERVICE PAGE ──────────────────────────────────────────────────────────────

def generate_service_page(svc, categories_lookup, all_services_by_slug, total_services):
    """Generate HTML for an individual service page."""
    name = svc["name"]
    slug = svc["slug"]
    favicon_domain = svc["faviconDomain"]
    status_url = svc["statusUrl"]
    homepage_url = svc["homepageUrl"]
    cat_slugs = svc["categories"]

    # Get primary category info
    primary_cat = categories_lookup.get(cat_slugs[0], {"name": cat_slugs[0], "slug": cat_slugs[0]})

    # Build related services (from primary category, excluding self)
    related = []
    primary_cat_data = categories_lookup.get(cat_slugs[0], {})
    for rs in primary_cat_data.get("serviceSlugs", []):
        if rs != slug and rs in all_services_by_slug:
            related.append(all_services_by_slug[rs])
            if len(related) >= 6:
                break

    # Breadcrumb JSON-LD
    breadcrumb_ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Vultyr", "item": "https://vultyr.app"},
            {"@type": "ListItem", "position": 2, "name": "Services", "item": "https://vultyr.app/services.html"},
            {"@type": "ListItem", "position": 3, "name": primary_cat["name"], "item": f"https://vultyr.app/categories/{primary_cat['slug']}.html"},
            {"@type": "ListItem", "position": 4, "name": name},
        ]
    }

    # FAQ JSON-LD
    faq_ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": f"Is {name} down right now?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": f"Check the official {name} status page at {status_url} for current status. Download the free Vultyr app for instant outage alerts on all your Apple devices."
                }
            },
            {
                "@type": "Question",
                "name": f"How can I monitor {name} status?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": f"Download Vultyr (free) to monitor {name} and {total_services}+ other services with real-time alerts on iPhone, Mac, Apple Watch, Apple TV, and Vision Pro. Vultyr checks service status automatically and notifies you the moment an outage is detected."
                }
            },
        ]
    }

    # Category links for breadcrumb
    breadcrumb_html = f'''        <div class="breadcrumb">
            <a href="/">Vultyr</a><span class="sep">&rsaquo;</span>
            <a href="/services.html">Services</a><span class="sep">&rsaquo;</span>
            <a href="/categories/{e(primary_cat["slug"])}.html">{e(primary_cat["name"])}</a><span class="sep">&rsaquo;</span>
            <span class="breadcrumb-current">{e(name)}</span>
        </div>'''

    # Related services HTML
    related_html = ""
    if related:
        cards = ""
        for rs in related:
            cards += f'''            <a class="related-card" href="/status/{e(rs["slug"])}.html">
                <img role="presentation" src="https://www.google.com/s2/favicons?domain={e(rs["faviconDomain"])}&sz=32" alt="" loading="lazy" width="20" height="20">
                {e(rs["name"])}
            </a>\n'''
        related_html = f'''        <h2 class="section-title">Related Services</h2>
        <div class="related-grid">
{cards}        </div>'''

    # Multi-category note
    cat_links_html = ""
    if len(cat_slugs) > 1:
        links = ", ".join(
            f'<a href="/categories/{e(cs)}.html" class="highlight-orange">{e(categories_lookup.get(cs, {}).get("name", cs))}</a>'
            for cs in cat_slugs
        )
        cat_links_html = f'        <p class="category-note">Categories: {links}</p>'

    title = f"Is {name} Down? {name} Status Monitor | Vultyr"
    description = f"Check if {name} is down right now. Live {name} status updates and outage monitoring with Vultyr. Free on iPhone, Mac, Apple Watch, Apple TV, and Vision Pro."

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{GA_SNIPPET}
{CSP_META}
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
    <link rel="icon" type="image/png" href="/favicon.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Audiowide&display=swap" rel="stylesheet">
{json_ld(breadcrumb_ld)}
{json_ld(faq_ld)}
    <link rel="stylesheet" href="/assets/css/shared.css">
    <link rel="stylesheet" href="/assets/css/service.css">
</head>
<body>
    <a href="#main" class="sr-only">Skip to main content</a>
    <main id="main">
    <div class="container">
{breadcrumb_html}
        <div class="service-header">
            <img src="https://www.google.com/s2/favicons?domain={e(favicon_domain)}&sz=64" alt="{e(name)} icon" width="48" height="48">
            <h1>{e(name)}</h1>
        </div>

        <div class="status-card">
            <a href="{e(status_url)}" target="_blank" rel="noopener noreferrer" class="status-badge">
                <span class="status-text">View Current Status &rarr;</span>
            </a>
            <p class="status-time">For live alerts, <a href="https://apps.apple.com/us/app/vultyr/id6761264004">download Vultyr</a></p>
        </div>
{cat_links_html}
        <div class="links-row">
            <a href="{e(status_url)}" target="_blank" rel="noopener noreferrer">
                <svg width="16" height="16" viewBox="0 0 256 256" fill="currentColor"><path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24Zm-26.37,144H96a8,8,0,0,1-8-8V96a8,8,0,0,1,8-8h5.63a8,8,0,0,1,5.66,2.34l56,56a8,8,0,0,1-11.32,11.32L101.63,107.31V160A8,8,0,0,1,101.63,168Z"/></svg>
                Official Status Page
            </a>
            <a href="{e(homepage_url)}" target="_blank" rel="noopener noreferrer">
                <svg width="16" height="16" viewBox="0 0 256 256" fill="currentColor"><path d="M128,16a112,112,0,1,0,112,112A112.13,112.13,0,0,0,128,16ZM40,128a87.5,87.5,0,0,1,8.43-37.65l46.46,127.38A88.14,88.14,0,0,1,40,128Zm88,88a87.53,87.53,0,0,1-28.34-4.67l30.09-87.39,30.83,84.49A88.18,88.18,0,0,1,128,216Z"/></svg>
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
            <p>Vultyr monitors {e(name)} and {total_services}+ other cloud services, dev tools, and platforms. Get instant outage alerts on iPhone, Mac, Apple Watch, Apple TV, and Vision Pro — completely free.</p>
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

def generate_category_page(cat, all_services_by_slug, all_categories):
    """Generate HTML for a category page."""
    name = cat["name"]
    slug = cat["slug"]
    icon = cat.get("icon", "")
    service_slugs = cat["serviceSlugs"]
    count = len(service_slugs)

    # Build service cards
    cards = ""
    for ss in service_slugs:
        svc = all_services_by_slug.get(ss)
        if not svc:
            continue
        cards += f'''            <a class="service-card" href="/status/{e(svc["slug"])}.html">
                <img role="presentation" src="https://www.google.com/s2/favicons?domain={e(svc["faviconDomain"])}&sz=32" alt="" loading="lazy" width="24" height="24">
                <span>{e(svc["name"])}</span>
            </a>\n'''

    # Other category links
    other_cats = ""
    for oc in all_categories:
        if oc["slug"] != slug:
            other_cats += f'            <a class="cat-link" href="/categories/{e(oc["slug"])}.html">{e(oc["name"])}</a>\n'

    # SVG icon (read from assets/icons if available)
    icon_html = ""
    if icon:
        icon_path = os.path.join(ROOT_DIR, "assets", "icons", icon)
        if os.path.exists(icon_path):
            try:
                with open(icon_path) as f:
                    svg = f.read()
                svg = svg.replace("<svg", '<svg class="cat-icon"', 1)
                icon_html = svg
            except OSError as exc:
                print(f"Warning: could not read icon {icon_path}: {exc}")

    # Breadcrumb JSON-LD
    breadcrumb_ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Vultyr", "item": "https://vultyr.app"},
            {"@type": "ListItem", "position": 2, "name": "Services", "item": "https://vultyr.app/services.html"},
            {"@type": "ListItem", "position": 3, "name": name},
        ]
    }

    # ItemList JSON-LD
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
                "url": f"https://vultyr.app/status/{all_services_by_slug[ss]['slug']}.html"
            }
            for i, ss in enumerate(service_slugs) if ss in all_services_by_slug
        ]
    }

    title = f"{name} Status Monitor — {count} Services | Vultyr"
    description = f"Monitor the status of {count} {name.lower()} services. Real-time outage alerts for {', '.join(all_services_by_slug[s]['name'] for s in service_slugs[:4] if s in all_services_by_slug)}, and more."

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{GA_SNIPPET}
{CSP_META}
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
    <link rel="icon" type="image/png" href="/favicon.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Audiowide&display=swap" rel="stylesheet">
{json_ld(breadcrumb_ld)}
{json_ld(item_list_ld)}
    <link rel="stylesheet" href="/assets/css/shared.css">
    <link rel="stylesheet" href="/assets/css/category.css">
</head>
<body>
    <a href="#main" class="sr-only">Skip to main content</a>
    <main id="main">
    <div class="container">
        <div class="breadcrumb">
            <a href="/">Vultyr</a><span class="sep">&rsaquo;</span>
            <a href="/services.html">Services</a><span class="sep">&rsaquo;</span>
            <span class="breadcrumb-current">{e(name)}</span>
        </div>

        <div class="cat-header">
            {icon_html}
            <h1>{e(name)}</h1>
        </div>
        <p class="cat-subtitle">{count} services monitored by Vultyr</p>

        <div class="services-grid">
{cards}        </div>

        <div class="other-categories">
            <h2>Other Categories</h2>
            <div class="cat-links">
{other_cats}            </div>
        </div>

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

def generate_404():
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{GA_SNIPPET}
{CSP_META}
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Not Found — Vultyr</title>
    <meta name="description" content="The page you're looking for doesn't exist.">
    <meta name="theme-color" content="#000000">
    <meta name="robots" content="noindex">
    <link rel="apple-touch-icon" href="/icon.png">
    <link rel="icon" type="image/png" href="/favicon.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Audiowide&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/assets/css/shared.css">
    <style>
        body {{ display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 40px 24px; }}
        h1 {{ font-family: 'Audiowide', sans-serif; font-size: 4rem; color: #ff9926; margin-bottom: 8px; }}
        .subtitle {{ font-size: 1.2rem; color: #fff; margin-bottom: 24px; }}
        .message {{ color: #888; max-width: 400px; margin-bottom: 32px; font-size: 0.95rem; }}
        .links {{ display: flex; gap: 16px; flex-wrap: wrap; justify-content: center; margin-bottom: 48px; }}
        .links a {{
            padding: 10px 24px;
            border: 1px solid #222;
            border-radius: 999px;
            color: #ccc;
            font-size: 0.9rem;
            transition: border-color 0.2s, color 0.2s;
        }}
        .links a:hover {{ border-color: #00ff41; color: #fff; }}
        footer {{ margin-top: auto; width: 100%; }}
    </style>
</head>
<body>
    <a href="#main" class="sr-only">Skip to main content</a>
    <main id="main">
        <h1>404</h1>
        <p class="subtitle">Page not found</p>
        <p class="message">The page you're looking for doesn't exist or has been moved.</p>
        <div class="links">
            <a href="/">Home</a>
            <a href="/services.html">Services</a>
            <a href="/support.html">Support</a>
        </div>
    </main>
{FOOTER_HTML}
</body>
</html>
"""


# ─── SITEMAP ───────────────────────────────────────────────────────────────────

def generate_sitemap(services, categories):
    urls = []

    # Existing pages
    urls.append(("https://vultyr.app/", "1.0", "weekly"))
    urls.append(("https://vultyr.app/services.html", "0.8", "weekly"))
    urls.append(("https://vultyr.app/support.html", "0.6", "monthly"))
    urls.append(("https://vultyr.app/privacy.html", "0.5", "monthly"))

    # Category pages
    for cat in categories:
        urls.append((f"https://vultyr.app/categories/{cat['slug']}.html", "0.7", "weekly"))

    # Service pages
    for svc in services:
        urls.append((f"https://vultyr.app/status/{svc['slug']}.html", "0.6", "weekly"))

    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for loc, priority, freq in urls:
        lines.append(f"  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        lines.append(f"    <lastmod>{TODAY}</lastmod>")
        lines.append(f"    <priority>{priority}</priority>")
        lines.append(f"    <changefreq>{freq}</changefreq>")
        lines.append(f"  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


# ─── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    data = load_data()
    services = data["services"]
    categories = data["categories"]

    # Build lookup maps
    services_by_slug = {s["slug"]: s for s in services}
    categories_by_slug = {}
    for cat in categories:
        categories_by_slug[cat["slug"]] = cat

    # Create directories
    os.makedirs(STATUS_DIR, exist_ok=True)
    os.makedirs(CATEGORIES_DIR, exist_ok=True)

    total_services = len(services)

    # Generate service pages
    print(f"Generating {total_services} service pages...")
    for svc in services:
        html = generate_service_page(svc, categories_by_slug, services_by_slug, total_services)
        path = os.path.join(STATUS_DIR, f"{svc['slug']}.html")
        write_file(path, html)

    # Generate category pages
    print(f"Generating {len(categories)} category pages...")
    for cat in categories:
        html = generate_category_page(cat, services_by_slug, categories)
        path = os.path.join(CATEGORIES_DIR, f"{cat['slug']}.html")
        write_file(path, html)

    # Generate 404
    print("Generating 404.html...")
    write_file(os.path.join(ROOT_DIR, "404.html"), generate_404())

    # Generate sitemap
    print("Generating sitemap.xml...")
    write_file(os.path.join(ROOT_DIR, "sitemap.xml"), generate_sitemap(services, categories))

    total = total_services + len(categories) + 2  # +2 for 404 and sitemap
    print(f"\nDone! Generated {total} files:")
    print(f"  {total_services} service pages in /status/")
    print(f"  {len(categories)} category pages in /categories/")
    print(f"  1 x 404.html")
    print(f"  1 x sitemap.xml ({total_services + len(categories) + 4} URLs)")


if __name__ == "__main__":
    main()
