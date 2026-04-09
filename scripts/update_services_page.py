#!/usr/bin/env python3
"""Update services.html with internal links to individual service/category pages
and add ItemList JSON-LD schema."""

import json
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
JSON_PATH = os.path.join(ROOT_DIR, "data", "services.json")
SERVICES_HTML = os.path.join(ROOT_DIR, "services.html")


def main():
    with open(JSON_PATH) as f:
        data = json.load(f)

    with open(SERVICES_HTML) as f:
        html = f.read()

    # Build lookup: service name -> slug
    name_to_slug = {}
    for svc in data["services"]:
        name_to_slug[svc["name"]] = svc["slug"]

    # Build lookup: category name -> slug
    cat_name_to_slug = {}
    for cat in data["categories"]:
        cat_name_to_slug[cat["name"]] = cat["slug"]

    # 1. Wrap service names in links to /status/{slug}.html
    # Pattern: <div class="service-name">Service Name</div>
    def replace_service_name(match):
        name = match.group(1)
        slug = name_to_slug.get(name)
        if slug:
            return f'<div class="service-name"><a href="/status/{slug}.html">{name}</a></div>'
        return match.group(0)

    html = re.sub(
        r'<div class="service-name">([^<]+)</div>',
        replace_service_name,
        html
    )

    # 2. Wrap category h2 headers in links to /categories/{slug}.html
    # Pattern: <h2>Category Name <span>N services</span></h2>
    def replace_category_h2(match):
        cat_name = match.group(1)
        span = match.group(2)
        slug = cat_name_to_slug.get(cat_name)
        if slug:
            return f'<h2><a href="/categories/{slug}.html">{cat_name}</a> {span}</h2>'
        return match.group(0)

    html = re.sub(
        r'<h2>([^<]+?)\s*(<span>[^<]+</span>)</h2>',
        replace_category_h2,
        html
    )

    # 3. Add ItemList JSON-LD before </head>
    item_list = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Services Monitored by Vultyr",
        "numberOfItems": len(data["services"]),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": svc["name"],
                "url": f"https://vultyr.app/status/{svc['slug']}.html"
            }
            for i, svc in enumerate(data["services"])
        ]
    }

    json_ld_tag = f'    <script type="application/ld+json">\n    {json.dumps(item_list, indent=2).replace(chr(10), chr(10) + "    ")}\n    </script>\n'

    # Insert before <style> tag
    html = html.replace("    <style>", json_ld_tag + "    <style>", 1)

    # 4. Add CSS for linked service names and category headers
    link_css = """
        .service-name a { color: inherit; text-decoration: none; }
        .service-name a:hover { color: #00ff41; }
        h2 a { color: inherit; text-decoration: none; }
        h2 a:hover { color: #ff9926; }
"""
    # Insert after the existing .sr-only rule
    html = html.replace(
        "        .sr-only {",
        link_css + "        .sr-only {",
        1
    )

    with open(SERVICES_HTML, "w") as f:
        f.write(html)

    print(f"Updated services.html:")
    print(f"  - Linked {len(name_to_slug)} service names to /status/ pages")
    print(f"  - Linked {len(cat_name_to_slug)} category headers to /categories/ pages")
    print(f"  - Added ItemList JSON-LD with {len(data['services'])} items")


if __name__ == "__main__":
    main()
