#!/usr/bin/env python3
"""Extract service data from services.html into data/services.json."""

import json
import re
import os
from html.parser import HTMLParser

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
SERVICES_HTML = os.path.join(ROOT_DIR, "services.html")
OUTPUT_JSON = os.path.join(ROOT_DIR, "data", "services.json")

CATEGORY_SLUGS = {
    "Cloud & Infrastructure": "cloud-infrastructure",
    "Developer Tools": "developer-tools",
    "Communication": "communication",
    "Productivity & SaaS": "productivity-saas",
    "Payments & Commerce": "payments-commerce",
    "Apple": "apple",
    "Google": "google",
    "Microsoft": "microsoft",
    "Amazon": "amazon",
    "AI & Machine Learning": "ai-machine-learning",
    "Social Media": "social-media",
    "Streaming & Media": "streaming-media",
    "Gaming": "gaming",
    "Telecom & ISP": "telecom-isp",
    "Security": "security",
    "Email & Marketing": "email-marketing",
}

CATEGORY_ICONS = {
    "cloud-infrastructure": "cloud-check-regular.svg",
    "developer-tools": "code-regular.svg",
    "communication": "chat-circle-regular.svg",
    "productivity-saas": "gear-regular.svg",
    "payments-commerce": "credit-card-regular.svg",
    "apple": "apple-logo-regular.svg",
    "google": "globe-regular.svg",
    "microsoft": "monitor-regular.svg",
    "amazon": "database-regular.svg",
    "ai-machine-learning": "robot-regular.svg",
    "social-media": "users-regular.svg",
    "streaming-media": "play-circle-regular.svg",
    "gaming": "game-controller-regular.svg",
    "telecom-isp": "wifi-high-regular.svg",
    "security": "shield-check-regular.svg",
    "email-marketing": "envelope-simple-regular.svg",
}


def make_slug(name):
    """Convert a service name to a URL-safe slug."""
    s = name.lower()
    s = s.replace(" & ", " and ")
    s = s.replace("&", "and")
    # Remove parenthetical content but keep it for disambiguation
    paren = re.search(r"\(([^)]+)\)", s)
    s = re.sub(r"\s*\([^)]*\)", "", s)
    s = s.replace(" / ", "-")
    s = s.replace("/", "-")
    s = s.replace("+", "plus")
    s = s.replace(".", "")
    s = s.replace("'", "")
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = s.strip()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-+", "-", s)
    s = s.strip("-")
    return s


def extract_domain(url):
    """Extract domain from a URL for favicon purposes."""
    m = re.search(r"https?://(?:www\.)?([^/]+)", url)
    return m.group(1) if m else ""


class ServicesParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.categories = []  # list of {"name", "slug", "icon", "services": [...]}
        self.current_category = None
        self.current_service = None

        # State tracking
        self.in_h2 = False
        self.in_service_name = False
        self.in_service_links = False
        self.link_index = 0
        self.h2_text = ""
        self.service_name_text = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get("class", "")

        if tag == "h2":
            self.in_h2 = True
            self.h2_text = ""

        elif tag == "div" and "service" == cls:
            self.current_service = {
                "faviconDomain": "",
                "name": "",
                "statusUrl": "",
                "homepageUrl": "",
            }

        elif tag == "img" and "service-favicon" in cls and self.current_service:
            src = attrs_dict.get("src", "")
            # Extract domain from Google Favicons URL
            m = re.search(r"domain=([^&]+)", src)
            if m:
                self.current_service["faviconDomain"] = m.group(1)

        elif tag == "div" and "service-name" in cls:
            self.in_service_name = True
            self.service_name_text = ""

        elif tag == "div" and "service-links" in cls:
            self.in_service_links = True
            self.link_index = 0

        elif tag == "a" and self.in_service_links and self.current_service:
            href = attrs_dict.get("href", "")
            if self.link_index == 0:
                self.current_service["statusUrl"] = href
            elif self.link_index == 1:
                self.current_service["homepageUrl"] = href
            self.link_index += 1

    def handle_data(self, data):
        if self.in_h2:
            self.h2_text += data
        if self.in_service_name:
            self.service_name_text += data

    def handle_endtag(self, tag):
        if tag == "h2" and self.in_h2:
            self.in_h2 = False
            # Parse category name from h2 text (strip the count span)
            cat_name = self.h2_text.strip()
            # Remove trailing count like "30 services"
            cat_name = re.sub(r"\s*\d+\s+services?\s*$", "", cat_name).strip()
            if cat_name in CATEGORY_SLUGS:
                slug = CATEGORY_SLUGS[cat_name]
                self.current_category = {
                    "name": cat_name,
                    "slug": slug,
                    "icon": CATEGORY_ICONS.get(slug, ""),
                    "services": [],
                }
                self.categories.append(self.current_category)

        elif tag == "div" and self.in_service_name:
            self.in_service_name = False
            if self.current_service:
                self.current_service["name"] = self.service_name_text.strip()

        elif tag == "div" and self.in_service_links:
            self.in_service_links = False
            # Service is complete, add to current category
            if self.current_service and self.current_category:
                svc = self.current_service
                svc["slug"] = make_slug(svc["name"])
                self.current_category["services"].append(svc)
            self.current_service = None


def deduplicate_services(categories):
    """Build a flat service list, handling duplicates (e.g. YouTube in 2 categories)."""
    services_by_slug = {}
    category_list = []

    for cat in categories:
        cat_info = {
            "name": cat["name"],
            "slug": cat["slug"],
            "icon": cat["icon"],
            "serviceSlugs": [],
        }
        for svc in cat["services"]:
            slug = svc["slug"]
            if slug in services_by_slug:
                # Duplicate — add this category to existing service
                if cat["slug"] not in services_by_slug[slug]["categories"]:
                    services_by_slug[slug]["categories"].append(cat["slug"])
            else:
                services_by_slug[slug] = {
                    "name": svc["name"],
                    "slug": slug,
                    "faviconDomain": svc["faviconDomain"],
                    "statusUrl": svc["statusUrl"],
                    "homepageUrl": svc["homepageUrl"],
                    "statuspageApi": None,
                    "categories": [cat["slug"]],
                }
            cat_info["serviceSlugs"].append(slug)
        category_list.append(cat_info)

    return list(services_by_slug.values()), category_list


def main():
    with open(SERVICES_HTML, "r") as f:
        html = f.read()

    parser = ServicesParser()
    parser.feed(html)

    services, categories = deduplicate_services(parser.categories)

    # Check for slug collisions
    slugs = [s["slug"] for s in services]
    dupes = [s for s in slugs if slugs.count(s) > 1]
    if dupes:
        print(f"WARNING: Duplicate slugs found: {set(dupes)}")
        # Disambiguate by appending category
        seen = {}
        for svc in services:
            if svc["slug"] in seen:
                # Rename both
                other = seen[svc["slug"]]
                if other["slug"] == svc["slug"]:
                    other["slug"] = f"{other['slug']}-{other['categories'][0]}"
                svc["slug"] = f"{svc['slug']}-{svc['categories'][0]}"
            else:
                seen[svc["slug"]] = svc

    data = {
        "services": services,
        "categories": categories,
    }

    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Extracted {len(services)} unique services across {len(categories)} categories")
    print(f"Written to {OUTPUT_JSON}")

    # Print category summary
    for cat in categories:
        print(f"  {cat['name']}: {len(cat['serviceSlugs'])} services")


if __name__ == "__main__":
    main()
