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

SHARED_CSS = """
        *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', sans-serif;
            background: #000;
            color: #ccc;
            min-height: 100vh;
            line-height: 1.7;
        }
        a { color: inherit; text-decoration: none; }
        .sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); border: 0; }
        :focus-visible { outline: 2px solid #00ff41; outline-offset: 3px; }
        .highlight { color: #00ff41; }
        .highlight-orange { color: #ff9926; }
"""

FOOTER_HTML = """    <footer>
        <nav aria-label="Footer navigation">
            <a href="/services.html">Services</a>
            <a href="/privacy.html">Privacy</a>
            <a href="/support.html">Support</a>
            <a href="mailto:support@vultyr.app">Contact</a>
            <a href="https://klosyt.com" target="_blank" rel="noopener noreferrer">Klosyt</a>
        </nav>
        <p class="copyright">&copy; 2026 Klosyt. All rights reserved.</p>
    </footer>"""


def e(text):
    """HTML-escape text."""
    return html_module.escape(str(text))


def load_data():
    with open(JSON_PATH) as f:
        return json.load(f)


def json_ld(obj):
    """Render a JSON-LD script tag."""
    return f'    <script type="application/ld+json">\n    {json.dumps(obj, indent=2).replace(chr(10), chr(10) + "    ")}\n    </script>'


# ─── SERVICE PAGE ──────────────────────────────────────────────────────────────

SERVICE_CSS = """
        .container { max-width: 720px; margin: 0 auto; padding: 40px 24px 0; }
        .breadcrumb { font-size: 0.8rem; color: #666; margin-bottom: 24px; }
        .breadcrumb a { color: #888; }
        .breadcrumb a:hover { color: #fff; }
        .breadcrumb .sep { margin: 0 6px; }

        .service-header { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; }
        .service-header img { width: 48px; height: 48px; border-radius: 8px; }
        .service-header h1 { font-family: 'Audiowide', sans-serif; font-size: 1.6rem; color: #fff; }

        .status-card {
            background: rgba(255,255,255,0.03);
            border: 1px solid #1a1a1a;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            text-align: center;
        }
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            font-size: 1.1rem;
            color: #fff;
            padding: 10px 24px;
            border-radius: 999px;
            border: 1px solid #222;
            background: rgba(255,255,255,0.02);
        }
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #555;
            flex-shrink: 0;
        }
        .status-dot.pulse { animation: pulse 2s ease-in-out infinite; }
        @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }
        .status-text { font-size: 0.95rem; }
        .status-time { font-size: 0.75rem; color: #555; margin-top: 8px; }

        .links-row { display: flex; gap: 12px; margin-bottom: 32px; flex-wrap: wrap; }
        .links-row a {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 20px;
            border: 1px solid #222;
            border-radius: 999px;
            font-size: 0.875rem;
            color: #ccc;
            background: rgba(255,255,255,0.02);
            transition: border-color 0.2s, color 0.2s;
        }
        .links-row a:hover { border-color: #444; color: #fff; }

        .section-title { font-family: 'Audiowide', sans-serif; font-size: 1rem; color: #ff9926; margin-bottom: 16px; }

        .faq { margin-bottom: 20px; }
        .faq h3 { color: #fff; font-size: 0.95rem; margin-bottom: 4px; }
        .faq p { color: #999; font-size: 0.875rem; }

        .related-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 10px; margin-bottom: 32px; }
        .related-card {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 14px;
            border: 1px solid #1a1a1a;
            border-radius: 10px;
            background: rgba(255,255,255,0.02);
            transition: border-color 0.2s;
            font-size: 0.875rem;
            color: #ccc;
        }
        .related-card:hover { border-color: #333; color: #fff; }
        .related-card img { width: 20px; height: 20px; border-radius: 4px; }

        .cta {
            text-align: center;
            padding: 40px 24px;
            margin-bottom: 16px;
        }
        .cta h2 { font-family: 'Audiowide', sans-serif; font-size: 1.2rem; color: #fff; margin-bottom: 8px; }
        .cta p { color: #888; font-size: 0.9rem; margin-bottom: 20px; }
        .cta a {
            display: inline-block;
            padding: 12px 28px;
            background: #00ff41;
            color: #000;
            font-weight: 600;
            border-radius: 999px;
            font-size: 0.9rem;
            transition: opacity 0.2s;
        }
        .cta a:hover { opacity: 0.85; }

        footer { text-align: center; padding: 24px; border-top: 1px solid #111; }
        footer nav { display: flex; justify-content: center; gap: 24px; flex-wrap: wrap; }
        footer a { color: #666; font-size: 0.8rem; }
        footer a:hover { color: #aaa; }
        .copyright { font-size: 0.7rem; color: #555; margin-top: 12px; }

        @media (max-width: 500px) {
            .service-header h1 { font-size: 1.2rem; }
            .links-row { flex-direction: column; }
            .related-grid { grid-template-columns: 1fr 1fr; }
        }
        @media (prefers-reduced-motion: reduce) {
            .status-dot.pulse { animation: none; }
        }
"""


def generate_service_page(svc, categories_lookup, all_services_by_slug):
    """Generate HTML for an individual service page."""
    name = svc["name"]
    slug = svc["slug"]
    favicon_domain = svc["faviconDomain"]
    status_url = svc["statusUrl"]
    homepage_url = svc["homepageUrl"]
    api_url = svc.get("statuspageApi")
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
                    "text": f"Check the current {name} service status on this page.{' Vultyr checks ' + name + ' status in real-time via the Statuspage.io API.' if api_url else ''} You can also visit the official {name} status page at {status_url} or download the free Vultyr app for instant outage alerts on all your Apple devices."
                }
            },
            {
                "@type": "Question",
                "name": f"How can I monitor {name} status?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": f"Download Vultyr (free) to monitor {name} and 200+ other services with real-time alerts on iPhone, Mac, Apple Watch, Apple TV, and Vision Pro. Vultyr checks service status automatically and notifies you the moment an outage is detected."
                }
            },
        ]
    }

    # Status check script
    if api_url:
        status_script = f"""
    <script src="/assets/js/status-checker.js"></script>
    <script>
    document.addEventListener("DOMContentLoaded", function() {{
        var dot = document.getElementById("status-dot");
        var text = document.getElementById("status-text");
        var time = document.getElementById("status-time");
        VultyrStatus.checkStatus("{api_url}", "{slug}").then(function(r) {{
            dot.style.background = VultyrStatus.COLORS[r.indicator] || VultyrStatus.COLORS.unknown;
            dot.classList.add("pulse");
            text.textContent = r.description || VultyrStatus.LABELS[r.indicator] || "Unknown";
            time.textContent = "Checked just now";
        }});
    }});
    </script>"""
    else:
        status_script = ""

    # Category links for breadcrumb
    breadcrumb_html = f'''        <div class="breadcrumb">
            <a href="/">Vultyr</a><span class="sep">&rsaquo;</span>
            <a href="/services.html">Services</a><span class="sep">&rsaquo;</span>
            <a href="/categories/{e(primary_cat["slug"])}.html">{e(primary_cat["name"])}</a><span class="sep">&rsaquo;</span>
            <span style="color:#ccc">{e(name)}</span>
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
            f'<a href="/categories/{e(cs)}.html" style="color:#ff9926">{e(categories_lookup.get(cs, {}).get("name", cs))}</a>'
            for cs in cat_slugs
        )
        cat_links_html = f'        <p style="font-size:0.8rem;color:#666;margin-bottom:24px">Categories: {links}</p>'

    title = f"Is {name} Down? {name} Status Monitor | Vultyr"
    description = f"Check if {name} is down right now. Live {name} status updates and outage monitoring with Vultyr. Free on iPhone, Mac, Apple Watch, Apple TV, and Vision Pro."

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{GA_SNIPPET}
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
    <style>{SHARED_CSS}{SERVICE_CSS}
    </style>
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
            <div class="status-badge">
                <span class="status-dot" id="status-dot"></span>
                <span class="status-text" id="status-text">{"Checking status" + ELLIPSIS if api_url else "Visit status page for current status"}</span>
            </div>
            <p class="status-time" id="status-time">{"" if api_url else ""}</p>
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
            <p>{"This page checks " + e(name) + " status in real-time via the Statuspage.io API. The status shown above updates automatically when you visit." if api_url else "Visit the official " + e(name) + " status page linked above for current status information."} For continuous monitoring with instant alerts, download the free Vultyr app.</p>
        </div>
        <div class="faq">
            <h3>How can I monitor {e(name)} status?</h3>
            <p>Vultyr monitors {e(name)} and 200+ other cloud services, dev tools, and platforms. Get instant outage alerts on iPhone, Mac, Apple Watch, Apple TV, and Vision Pro — completely free.</p>
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
{status_script}
</body>
</html>
"""


# ─── CATEGORY PAGE ─────────────────────────────────────────────────────────────

CATEGORY_CSS = """
        .container { max-width: 800px; margin: 0 auto; padding: 40px 24px 0; }
        .breadcrumb { font-size: 0.8rem; color: #666; margin-bottom: 24px; }
        .breadcrumb a { color: #888; }
        .breadcrumb a:hover { color: #fff; }
        .breadcrumb .sep { margin: 0 6px; }

        .cat-header { display: flex; align-items: center; gap: 16px; margin-bottom: 8px; }
        .cat-icon { width: 36px; height: 36px; color: #ff9926; }
        .cat-header h1 { font-family: 'Audiowide', sans-serif; font-size: 1.5rem; color: #fff; }
        .cat-subtitle { color: #888; font-size: 0.9rem; margin-bottom: 32px; }

        .services-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 10px; margin-bottom: 40px; }
        .service-card {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            border: 1px solid #1a1a1a;
            border-radius: 10px;
            background: rgba(255,255,255,0.02);
            transition: border-color 0.2s;
            color: #ccc;
            font-size: 0.9rem;
        }
        .service-card:hover { border-color: #333; color: #fff; }
        .service-card img { width: 24px; height: 24px; border-radius: 4px; flex-shrink: 0; }
        .service-card .card-status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #333;
            margin-left: auto;
            flex-shrink: 0;
        }

        .other-categories { margin-bottom: 32px; }
        .other-categories h2 { font-family: 'Audiowide', sans-serif; font-size: 1rem; color: #ff9926; margin-bottom: 16px; }
        .cat-links { display: flex; flex-wrap: wrap; gap: 8px; }
        .cat-link {
            padding: 6px 14px;
            border: 1px solid #1a1a1a;
            border-radius: 999px;
            font-size: 0.8rem;
            color: #888;
            transition: border-color 0.2s, color 0.2s;
        }
        .cat-link:hover { border-color: #444; color: #fff; }

        .cta {
            text-align: center;
            padding: 40px 24px;
            margin-bottom: 16px;
        }
        .cta h2 { font-family: 'Audiowide', sans-serif; font-size: 1.2rem; color: #fff; margin-bottom: 8px; }
        .cta p { color: #888; font-size: 0.9rem; margin-bottom: 20px; }
        .cta a {
            display: inline-block;
            padding: 12px 28px;
            background: #00ff41;
            color: #000;
            font-weight: 600;
            border-radius: 999px;
            font-size: 0.9rem;
            transition: opacity 0.2s;
        }
        .cta a:hover { opacity: 0.85; }

        footer { text-align: center; padding: 24px; border-top: 1px solid #111; }
        footer nav { display: flex; justify-content: center; gap: 24px; flex-wrap: wrap; }
        footer a { color: #666; font-size: 0.8rem; }
        footer a:hover { color: #aaa; }
        .copyright { font-size: 0.7rem; color: #555; margin-top: 12px; }

        @media (max-width: 500px) {
            .services-grid { grid-template-columns: 1fr; }
            .cat-header h1 { font-size: 1.2rem; }
        }
"""


def generate_category_page(cat, all_services_by_slug, all_categories):
    """Generate HTML for a category page."""
    name = cat["name"]
    slug = cat["slug"]
    icon = cat.get("icon", "")
    service_slugs = cat["serviceSlugs"]
    count = len(service_slugs)

    # Collect services with API URLs for status checking
    api_services = []

    # Build service cards
    cards = ""
    for ss in service_slugs:
        svc = all_services_by_slug.get(ss)
        if not svc:
            continue
        cards += f'''            <a class="service-card" href="/status/{e(svc["slug"])}.html">
                <img role="presentation" src="https://www.google.com/s2/favicons?domain={e(svc["faviconDomain"])}&sz=32" alt="" loading="lazy" width="24" height="24">
                <span>{e(svc["name"])}</span>
                <span class="card-status-dot" data-slug="{e(svc["slug"])}"></span>
            </a>\n'''
        if svc.get("statuspageApi"):
            api_services.append({"slug": svc["slug"], "apiUrl": svc["statuspageApi"]})

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
            with open(icon_path) as f:
                svg = f.read()
            # Add class to SVG
            svg = svg.replace("<svg", '<svg class="cat-icon"', 1)
            icon_html = svg

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

    # Status checking script for category page
    if api_services:
        svc_json = json.dumps(api_services)
        status_script = f"""
    <script src="/assets/js/status-checker.js"></script>
    <script>
    document.addEventListener("DOMContentLoaded", function() {{
        var services = {svc_json};
        VultyrStatus.checkMultiple(services, function(slug, result) {{
            var dot = document.querySelector('[data-slug="' + slug + '"]');
            if (dot) dot.style.background = VultyrStatus.COLORS[result.indicator] || VultyrStatus.COLORS.unknown;
        }});
    }});
    </script>"""
    else:
        status_script = ""

    title = f"{name} Status Monitor — {count} Services | Vultyr"
    description = f"Monitor the status of {count} {name.lower()} services. Real-time outage alerts for {', '.join(all_services_by_slug[s]['name'] for s in service_slugs[:4] if s in all_services_by_slug)}, and more."

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{GA_SNIPPET}
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
    <style>{SHARED_CSS}{CATEGORY_CSS}
    </style>
</head>
<body>
    <a href="#main" class="sr-only">Skip to main content</a>
    <main id="main">
    <div class="container">
        <div class="breadcrumb">
            <a href="/">Vultyr</a><span class="sep">&rsaquo;</span>
            <a href="/services.html">Services</a><span class="sep">&rsaquo;</span>
            <span style="color:#ccc">{e(name)}</span>
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
{status_script}
</body>
</html>
"""


# ─── 404 PAGE ──────────────────────────────────────────────────────────────────

def generate_404():
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{GA_SNIPPET}
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
    <style>{SHARED_CSS}
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
        footer {{ margin-top: auto; text-align: center; padding: 24px; border-top: 1px solid #111; width: 100%; }}
        footer nav {{ display: flex; justify-content: center; gap: 24px; flex-wrap: wrap; }}
        footer a {{ color: #666; font-size: 0.8rem; }}
        footer a:hover {{ color: #aaa; }}
        .copyright {{ font-size: 0.7rem; color: #555; margin-top: 12px; }}
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

    # Generate service pages
    print(f"Generating {len(services)} service pages...")
    for svc in services:
        html = generate_service_page(svc, categories_by_slug, services_by_slug)
        path = os.path.join(STATUS_DIR, f"{svc['slug']}.html")
        with open(path, "w") as f:
            f.write(html)

    # Generate category pages
    print(f"Generating {len(categories)} category pages...")
    for cat in categories:
        html = generate_category_page(cat, services_by_slug, categories)
        path = os.path.join(CATEGORIES_DIR, f"{cat['slug']}.html")
        with open(path, "w") as f:
            f.write(html)

    # Generate 404
    print("Generating 404.html...")
    with open(os.path.join(ROOT_DIR, "404.html"), "w") as f:
        f.write(generate_404())

    # Generate sitemap
    print("Generating sitemap.xml...")
    with open(os.path.join(ROOT_DIR, "sitemap.xml"), "w") as f:
        f.write(generate_sitemap(services, categories))

    total = len(services) + len(categories) + 2  # +2 for 404 and sitemap
    print(f"\nDone! Generated {total} files:")
    print(f"  {len(services)} service pages in /status/")
    print(f"  {len(categories)} category pages in /categories/")
    print(f"  1 × 404.html")
    print(f"  1 × sitemap.xml ({len(services) + len(categories) + 4} URLs)")


if __name__ == "__main__":
    main()
