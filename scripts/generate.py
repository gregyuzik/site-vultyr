#!/usr/bin/env python3
"""Generate the Vultyr site in two locales: English (root) and Russian (/ru/).

English pages land at the existing URLs (/, /services.html, /status/<slug>.html,
/categories/<slug>.html). Russian pages mirror that structure under /ru/.
Brand/service names stay in their original form; UI chrome and prose are
translated via the STRINGS dict at the top of this file.
"""

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
RU_DIR = ROOT_DIR / "ru"
RU_STATUS_DIR = RU_DIR / "status"
RU_CATEGORIES_DIR = RU_DIR / "categories"
FAVICONS_DIR = ROOT_DIR / "assets" / "favicons"
ICONS_DIR = ROOT_DIR / "assets" / "icons"
TODAY = date.today().isoformat()

SITE_ORIGIN = "https://vultyr.app"
APP_STORE_URL = "https://apps.apple.com/us/app/vultyr/id6761264004"
GA_ID = "G-YYDJLZG0X1"
FAVICON_HREF = "/favicon.png?v=20260417e"
# Bump when any CSS file changes so caches (Safari, CDN edges) reload.
ASSET_VERSION = "20260423c"
# Bump when icon-256.png changes so CDN edges pick up the new asset.
ICON_VERSION = "20260417e"
OG_IMAGE = f"{SITE_ORIGIN}/icon.png"

THEMES_COUNT = 12
APP_LANGUAGE_COUNT = 17

# Old slug -> new slug. When a service is renamed, we emit a redirect stub at
# /status/<old>.html (and under each locale) so external links and search
# results don't 404. GitHub Pages has no server-side redirects, so the stub
# uses meta-refresh + canonical + noindex.
SLUG_ALIASES = {
    "app-center": "appcenter",
    "apple-services": "apple-system",
    "bunny-cdn": "bunnycdn",
    "cash-app": "cashapp",
    "cloudflare-zero-trust": "cloudflare-security",
    "coinbase-exchange": "coinbase-ex",
    "dbt-cloud": "dbt",
    "dropbox-sign": "dropboxsign",
    "duo-security": "duo",
    "elastic-cloud": "elastic",
    "epic-games": "epicgames",
    "falai": "fal",
    "flyio": "fly",
    "gemini-exchange": "gemini-ex",
    "influxdb-cloud": "influxdb",
    "maven-central": "mavencentral",
    "mondaycom": "monday",
    "mongodb-cloud": "mongodb",
    "new-relic": "newrelic",
    "otterai": "otter",
    "palo-alto-networks": "paloalto",
    "sauce-labs": "saucelabs",
    "splunk-cloud": "splunk",
    "splunk-on-call": "splunk-oncall",
    "stability-ai": "stability",
    "travis-ci": "travisci",
}

# Ordered alphabetically by LOCALE_NATIVE_NAMES value (what users see in the
# language picker): Latin-script names A-Z, then Cyrillic, then CJK by codepoint.
LOCALES = (
    "da", "de", "en", "es", "fr", "it", "nl", "nb", "pt-BR", "sv",
    "vi", "tr", "ru", "ja", "zh-Hans", "zh-Hant", "ko",
)
DEFAULT_LOCALE = "en"

OG_LOCALES = {
    "en": "en_US", "da": "da_DK", "de": "de_DE", "es": "es_ES",
    "fr": "fr_FR", "it": "it_IT", "ja": "ja_JP", "ko": "ko_KR",
    "nb": "nb_NO", "nl": "nl_NL", "pt-BR": "pt_BR", "ru": "ru_RU",
    "sv": "sv_SE", "tr": "tr_TR", "vi": "vi_VN",
    "zh-Hans": "zh_CN", "zh-Hant": "zh_TW",
}


def html_lang(locale):
    return locale


def og_locale(locale):
    return OG_LOCALES.get(locale, "en_US")


LOCALE_NATIVE_NAMES = {
    "en": "English",
    "da": "Dansk",
    "de": "Deutsch",
    "es": "Espa\u00f1ol",
    "fr": "Fran\u00e7ais",
    "it": "Italiano",
    "ja": "\u65e5\u672c\u8a9e",
    "ko": "\ud55c\uad6d\uc5b4",
    "nb": "Norsk",
    "nl": "Nederlands",
    "pt-BR": "Portugu\u00eas",
    "ru": "\u0420\u0443\u0441\u0441\u043a\u0438\u0439",
    "sv": "Svenska",
    "tr": "T\u00fcrk\u00e7e",
    "vi": "Ti\u1ebfng Vi\u1ec7t",
    "zh-Hans": "\u7b80\u4f53\u4e2d\u6587",
    "zh-Hant": "\u7e41\u9ad4\u4e2d\u6587",
}

ALLOWED_URL_SCHEMES = {"https", "mailto"}

GA_SNIPPET = f"""    <!-- Google tag (gtag.js) — cookieless, anonymized -->
    <script defer src="/assets/js/analytics.js"></script>
    <script defer src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>"""


# ─── STRINGS ───────────────────────────────────────────────────────────────────

STRINGS = {
    "en": {
        "html_lang": "en",
        "og_locale": "en_US",
        "og_image_alt": "Vultyr app icon \u2014 Service Status Monitor",
        "devices": "iPhone, iPad, Mac, Apple Watch, Apple TV, and Vision Pro",
        "skip_to_main": "Skip to main content",
        "topbar_brand_aria": "Vultyr home",
        "nav_primary_aria": "Primary",
        "nav_services": "services",
        "nav_support": "support",
        "nav_download": "Download",
        "footer_nav_aria": "Footer navigation",
        "footer_home": "Home",
        "footer_services": "Services",
        "footer_privacy": "Privacy",
        "footer_support": "Support",
        "footer_contact": "Contact",
        "copyright": "\u00a9 2026 Vultyr. All rights reserved.",
        "breadcrumb_aria": "Breadcrumb",
        "breadcrumb_vultyr": "Vultyr",
        "breadcrumb_services": "Services",
        # services page
        "svcs_title": "Vultyr \u2014 200+ Status Checks",
        "svcs_description": "200+ status checks across cloud services, dev tools, communication, AI, and more \u2014 all monitored by Vultyr.",
        "svcs_h1_lead": "Status",
        "svcs_h1_highlight": "Checks",
        "svcs_subtitle": "200+ status checks vultyr runs across cloud services, dev tools, and platforms.",
        "svcs_categories_aria": "Browse by category",
        "svc_row_status": "Status Page",
        "svc_row_homepage": "Homepage",
        "svcs_item_list_name": "Services Monitored by Vultyr",
        # service page
        "svcp_title_fmt": "Is {name} Down? {name} Status Monitor | Vultyr",
        "svcp_description_fmt": "Check if {name} is down right now. Live {name} status updates and outage monitoring with Vultyr. Free on {devices}.",
        "svcp_live_check": "Live check",
        "svcp_view_current_status": "View Current Status \u2192",
        "svcp_alert_hint_prefix": "For instant alerts, ",
        "svcp_alert_hint_link": "download Vultyr",
        "svcp_categories_label": "Categories:",
        "svcp_official_status": "Official Status Page",
        "svcp_homepage_fmt": "{name} Homepage",
        "svcp_faq_heading": "FAQ",
        "svcp_faq_q1_fmt": "Is {name} down right now?",
        "svcp_faq_a1_fmt": "Check the official {name} status page linked above for current status. For continuous monitoring with instant outage alerts on all your Apple devices, download the free Vultyr app.",
        "svcp_faq_a1_ld_fmt": "Check the official {name} status page at {url} for current status. Download the free Vultyr app for instant outage alerts on all your Apple devices.",
        "svcp_faq_q2_fmt": "How can I monitor {name} status?",
        "svcp_faq_a2_fmt": "Vultyr monitors {name} as part of 200+ status checks across cloud services, dev tools, and platforms. Get instant outage alerts on {devices} \u2014 completely free.",
        "svcp_faq_a2_ld_fmt": "Download Vultyr (free) to monitor {name} as part of 200+ status checks with real-time alerts on {devices}. Vultyr runs each check automatically and notifies you the moment an outage is detected.",
        "svcp_related_heading": "Related Services",
        "svcp_related_aria": "Related services",
        "svcp_cta_heading_fmt": "Monitor {name} on all your devices",
        "svcp_cta_body_fmt": "Get instant alerts when {name} goes down. Free on all Apple platforms.",
        "cta_download_vultyr": "Download Vultyr",
        "cta_download_vultyr_aria": "Download Vultyr on the App Store",
        # category page
        "catp_title_fmt": "{name} Status Monitor \u2014 {count_services} | Vultyr",
        "catp_description_fmt": "Monitor the status of {count_services} in {name_lower}. Real-time outage alerts for {sample}, and more.",
        "catp_item_list_name_fmt": "{name} Status Monitors",
        "catp_subtitle_fmt": "{count_services} monitored by Vultyr",
        "catp_services_aria_fmt": "{name} services",
        "catp_other_heading": "Other Categories",
        "catp_cta_heading_fmt": "Monitor all {count_services} instantly",
        "catp_cta_body": "Get real-time outage alerts on all your Apple devices. Free.",
        # home page
        "home_title": "Vultyr \u2014 Service Status Monitor for AWS, Slack, GitHub & More",
        "home_description": "Is it down? 200+ status checks across cloud services, dev tools, and platforms with instant outage alerts. Free on iPhone, iPad, Mac, Apple Watch, Apple TV, and Apple Vision Pro.",
        "home_og_title": "Vultyr \u2014 Service Status Monitor",
        "home_app_ld_description": "Monitor 200+ status checks across cloud services, dev tools, and platforms with instant outage alerts.",
        "home_hero_tag": "200+ checks",
        "home_hero_question": "Is it down?",
        "home_hero_answer": "Know before your users do.",
        "home_hero_services": "200+ status checks \u2014 AWS, GitHub, Slack, Stripe &amp; more \u2014 with instant outage alerts across every Apple device.",
        "home_appstore_alt": "Download on the App Store",
        "home_appstore_aria": "Download Vultyr on the App Store",
        "home_free_on_prefix": "Free on",
        "home_screenshots_aria": "App screenshots",
        "home_screenshot_dash_alt": "Vultyr dashboard showing All Clear status with services like AWS, GitHub, and Slack monitored",
        "home_screenshot_settings_alt_fmt": "Vultyr appearance settings with {themes} themes including Terminal, Amber, Dracula, and Nord",
        "home_screenshot_services_alt_fmt": "Vultyr service browser showing {categories} categories including Cloud, Dev Tools, and AI",
        "home_stats_aria": "Key numbers",
        "home_stats_checks": "Checks",
        "home_stats_categories": "Categories",
        "home_stats_platforms": "Platforms",
        "home_stats_languages": "Languages",
        "home_features_heading": "Everything you need to stay ahead of outages",
        "home_features_sub": "No app accounts, no in-app tracking. Just status.",
        "home_bottom_heading": "Ready to monitor your stack?",
        "home_bottom_sub": "Free. No app account required. Available everywhere.",
        "home_bottom_button": "Download Free",
        "home_bottom_aria": "Download Vultyr free on the App Store",
        "home_languages_heading": "Available in 17 languages",
        "home_features": [
            ("chart-bar-regular.svg", "Live Status Dashboard",
             "AWS, GitHub, Cloudflare, Slack, Stripe, Discord, OpenAI, Anthropic and 200+ more — all in one place. Status orbs sync to 120Hz ProMotion on iPhone Pro and iPad Pro."),
            ("bell-ringing-regular.svg", "Smart Alerts",
             "Down and recovery notifications with each service's favicon attached on iOS. Major outages pulse noticeably larger than minor incidents, so severity reads at a glance. Mute known issues, star critical services."),
            ("microphone-regular.svg", "Siri & Shortcuts",
             "Ask Siri \u201cmute GitHub for 2 hours\u201d or \u201cshow current issues.\u201d App Intents for every action, plus a Focus Filter that quiets non-critical services."),
            ("squares-four-regular.svg", "Widgets & Live Activities",
             "Home Screen and Lock Screen widgets on iOS, plus a Control Center widget. Active outages pin to the Dynamic Island."),
            ("watch-regular.svg", "Watch Complications",
             "Pin a critical service to a watch face, or let Smart Stack surface active issues automatically."),
            ("cloud-check-regular.svg", "Mac Hub — iPhone Fallback",
             "Mac is the most reliable hub: it polls as often as every 60 seconds (configurable up to 15 min) and broadcasts status changes to iPhone, iPad, Watch, and Vision Pro via iCloud. If no Mac is online, your iPhone steps in as the fallback publisher so the other devices still get alerts."),
            ("monitor-regular.svg", "Alert Reliability View",
             "See at a glance whether alerts will actually reach you — Mac heartbeat freshness, background-refresh status, CloudKit push, and when each device last checked."),
            ("devices-regular.svg", "Every Apple Platform",
             "iPhone, iPad, Mac menu bar, Apple TV, Apple Watch, and Vision Pro. Services sync across all devices."),
            ("lightning-regular.svg", "Incident Details",
             "Affected components, active incidents, scheduled maintenance, and timeline updates \u2014 localized into your language."),
            ("battery-charging-regular.svg", "Battery-Aware Polling",
             "Smart auto-refresh adapts to battery, power state, and thermals. Every minute on Mac, 5–15 on iPhone, with background refresh honoured on iPad, Apple Watch, Vision Pro, and Apple TV."),
            ("palette-regular.svg", f"{THEMES_COUNT} Themes",
             "Standard and three retro themes are included. Fossil, Monolith, HAL and the rest unlock through optional tip-jar IAPs."),
            ("shield-check-regular.svg", "App Data Stays Local",
             "The app has no sign-up and no in-app analytics. Your watched services stay on your device."),
            ("translate-regular.svg", f"{APP_LANGUAGE_COUNT} App Languages",
             "English, German, French, Spanish, Japanese, Korean, Chinese, Portuguese, Russian, and more."),
        ],
        # 404
        "err_title": "Page Not Found \u2014 Vultyr",
        "err_description": "The page you're looking for doesn't exist.",
        "err_heading": "Page not found",
        "err_message": "The page you're looking for doesn't exist or has been moved.",
        "redirect_moved_fmt": "This page has moved. Redirecting to {name}…",
        "err_popular_heading": "Popular services",
        "err_browse_heading": "Browse categories",
        # privacy
        "privacy_title": "Privacy Policy",
        "privacy_description": "Vultyr privacy policy. The app collects no personal data. This website uses cookieless Google Analytics for aggregate visitor traffic.",
        "privacy_last_updated": "Last updated: April 11, 2026",
        "privacy_sections": [
            ("Summary",
             "<p>The Vultyr <strong>app</strong> collects, stores, and transmits no personal data. The Vultyr <strong>website</strong> (vultyr.app) uses cookieless Google Analytics to understand aggregate visitor traffic. This page explains both in detail.</p>"),
            ("App \u2014 Data Collection",
             "<p>The vultyr app does not collect any personal information. It does not require an account, does not include any third-party analytics or tracking SDKs, and does not phone home to any server we operate.</p>"),
            ("App \u2014 Network Requests",
             "<p>The app makes direct HTTPS requests to public status page APIs (such as Statuspage.io, Apple, Google Cloud, and others) to check service status. These requests go directly from your device to the service's public API \u2014 they do not pass through any server we operate.</p>"),
            ("App \u2014 Data Storage",
             "<p>All data is stored locally on your device using Apple's SwiftData framework. If you enable iCloud Sync, your list of watched services is synced via Apple's iCloud Key-Value Store, which is governed by Apple's privacy policy. We never see this data.</p>"),
            ("App \u2014 Cross-Device Alerts",
             "<p>If you enable Cross-Device Alerts, status changes are shared between your devices via Apple's iCloud Key-Value Store. When your Mac detects a status change, it writes a lightweight signal to your iCloud account. Your other devices observe the change and run their own local check. No third-party server is involved \u2014 all communication goes through Apple's iCloud infrastructure. You can toggle this from any device.</p>"),
            ("App \u2014 Favicons",
             "<p>Service favicons are fetched from Google's public favicon service and cached locally on your device.</p>"),
            ("Website \u2014 Analytics",
             "<p>This website (vultyr.app) uses Google Analytics 4 in cookieless, IP-anonymized mode to count aggregate page views. Specifically, we configure gtag.js with <code>anonymize_ip: true</code>, <code>client_storage: 'none'</code>, <code>allow_google_signals: false</code>, and <code>allow_ad_personalization_signals: false</code>. This means no <code>_ga</code> cookie is set, your IP is truncated before storage, and no advertising identifiers are collected. The vultyr app itself does not include any analytics.</p>"),
            ("Website \u2014 Third-Party Domains",
             "<p>Loading vultyr.app will contact the following third-party domains:</p>\n    <ul>\n        <li><strong>www.googletagmanager.com</strong> \u2014 loads the gtag.js script</li>\n        <li><strong>www.google-analytics.com</strong> / <strong>*.analytics.google.com</strong> \u2014 receives anonymized page-view beacons</li>\n        <li><strong>www.google.com/g/collect</strong> \u2014 receives the same anonymized page-view beacons (Google Analytics 4 fallback collection endpoint)</li>\n    </ul>\n    <p>We do not load Google Fonts (the Audiowide font is self-hosted on vultyr.app) and do not use a third-party favicon service for the website's own imagery.</p>"),
            ("App \u2014 Third-Party Services",
             "<p>The vultyr app does not integrate with any third-party analytics, advertising, or tracking services. The only external requests are to public status APIs and Google's favicon service.</p>"),
            ("Children's Privacy",
             "<p>The vultyr app does not collect data from anyone, including children under 13. The website logs only anonymized, aggregate visitor counts.</p>"),
            ("Changes",
             "<p>If this policy changes, we will update the date above.</p>"),
            ("Contact",
             "<p>Questions? Email <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a></p>"),
        ],
        # support
        "support_title": "Support",
        "support_description": "Get help with Vultyr, the service status monitor for iPhone, iPad, Mac, Apple Watch, Apple TV, and Apple Vision Pro. FAQs, contact, and troubleshooting.",
        "support_contact_heading": "Contact",
        "support_contact_html": "<p>For bug reports, feature requests, or questions:<br>\n    <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a></p>",
        "support_faq_heading": "FAQ",
        "support_faqs": [
            ("How often does vultyr check service status?",
             "On Mac: as often as every 60 seconds when plugged in. On iPhone: every 5, 10, or 15 minutes (configurable), with periodic background checks when conditions allow. On Apple Watch: every 15 minutes. On Apple TV: every 5 minutes. Polling adapts automatically to battery level, power state, and thermal conditions.",
             "<p>On Mac: as often as every 60 seconds when plugged in. On iPhone: every 5, 10, or 15 minutes (configurable), with periodic background checks when conditions allow. On Apple Watch: every 15 minutes. On Apple TV: every 5 minutes. Polling adapts automatically to battery level, power state, and thermal conditions.</p>"),
            ("How do Cross-Device Alerts work?",
             "The Mac app is the hub. Keep it running (menu bar or full window) and it polls as often as every 60 seconds (configurable up to 15 min). When a status change is detected, it writes a lightweight signal to iCloud Key-Value Store; your iPhone, iPad, Watch, Apple TV, and Vision Pro pick up the change and run their own local check. No keys, no tokens, no setup \u2014 just enable \"Cross-Device Alerts\" in settings on any device. Without a Mac acting as the hub, alerts rely on iOS background execution and will be delayed or missed.",
             "<p>The Mac app is the hub. Keep it running (menu bar or full window) and it polls as often as every 60 seconds (configurable up to 15 min). When a status change is detected, it writes a lightweight signal to iCloud Key-Value Store; your iPhone, iPad, Watch, Apple TV, and Vision Pro pick up the change and run their own local check. No keys, no tokens, no setup \u2014 just enable \"Cross-Device Alerts\" in settings on any device. Without a Mac acting as the hub, alerts rely on iOS background execution and will be delayed or missed.</p>"),
            ("Do I need the Mac app for reliable alerts?",
             "Yes \u2014 we strongly recommend it. iOS limits background execution, so iPhone and iPad can only check every 5-15 minutes (configurable) and may defer further on low battery, Low Power Mode, or poor connectivity. The Mac app polls as often as every 60 seconds when plugged in (configurable up to 15 min) and broadcasts status changes to your other devices via iCloud. Without a Mac running Vultyr, iOS, watchOS, and tvOS alerts still work but can be significantly delayed or missed. For real-time monitoring, keep the Mac app running \u2014 it's tiny in the menu bar and is how Vultyr is meant to be used.",
             "<p>Yes \u2014 we strongly recommend it. iOS limits background execution, so iPhone and iPad can only check every 5-15 minutes (configurable) and may defer further on low battery, Low Power Mode, or poor connectivity. The Mac app polls as often as every 60 seconds when plugged in (configurable up to 15 min) and broadcasts status changes to your other devices via iCloud. Without a Mac running Vultyr, iOS, watchOS, and tvOS alerts still work but can be significantly delayed or missed. For real-time monitoring, keep the Mac app running \u2014 it's tiny in the menu bar and is how Vultyr is meant to be used.</p>"),
            ("Does vultyr work with Siri and Shortcuts?",
             "Yes. Built-in App Intents let you say \u201cHey Siri, mute GitHub for 2 hours,\u201d \u201ccheck Stripe status,\u201d or \u201cshow current issues,\u201d and you can wire those same actions into the Shortcuts app. There's also a Focus Filter so a \u201cvultyr Focus\u201d mode can quiet non-critical services automatically.",
             "<p>Yes. Built-in App Intents let you say \u201cHey Siri, mute GitHub for 2 hours,\u201d \u201ccheck Stripe status,\u201d or \u201cshow current issues,\u201d and you can wire those same actions into the Shortcuts app. There's also a Focus Filter so a \u201cvultyr Focus\u201d mode can quiet non-critical services automatically.</p>"),
            ("Are there widgets and Live Activities?",
             "On iOS, there are Home Screen and Lock Screen widgets (single-service and status summary) plus a Control Center widget. Active outages pin to the Dynamic Island as Live Activities. On watchOS, complications are available for all watch faces, with Smart Stack relevance so the right service surfaces when something is down.",
             "<p>On iOS, there are Home Screen and Lock Screen widgets (single-service and status summary) plus a Control Center widget. Active outages pin to the Dynamic Island as Live Activities. On watchOS, complications are available for all watch faces, with Smart Stack relevance so the right service surfaces when something is down.</p>"),
            ("Does the vultyr app collect my data?",
             "No. The app has no accounts, no in-app tracking, no in-app analytics. All your watched services stay on your device. Note: this website (vultyr.app) uses cookieless Google Analytics for aggregate visitor counts \u2014 see the Privacy Policy for details.",
             "<p>No. The app has no accounts, no in-app tracking, no in-app analytics. All your watched services stay on your device. Note: this website (vultyr.app) uses cookieless Google Analytics for aggregate visitor counts \u2014 see the <a href=\"/privacy.html\">Privacy Policy</a> for details.</p>"),
            ("How do I sync my services across devices?",
             "Your watched services sync automatically via iCloud. Themes and settings also sync across all your Apple devices via iCloud Key-Value Store.",
             "<p>Your watched services sync automatically via iCloud. Themes and settings also sync across all your Apple devices via iCloud Key-Value Store.</p>"),
            ("What are the theme options?",
             "12 themes: Standard, Terminal, Amber, Blue, Neon, Dracula, Nord, Solarized, Catppuccin, Fossil, Monolith, and HAL. Standard and the three retro themes (Terminal, Amber, Blue) are included. Fossil, Monolith, HAL and the rest unlock through optional tip-jar IAPs ($0.99 / $4.99 / $9.99), which also helps fund development. Themes sync across all your devices automatically.",
             "<p>12 themes: Standard, Terminal, Amber, Blue, Neon, Dracula, Nord, Solarized, Catppuccin, Fossil, Monolith, and HAL. Standard and the three retro themes (Terminal, Amber, Blue) are included. Fossil, Monolith, HAL and the rest unlock through optional tip-jar IAPs ($0.99 / $4.99 / $9.99), which also helps fund development. Themes sync across all your devices automatically.</p>"),
            ("Can I mute notifications for a known incident?",
             "Yes. When viewing a service with an active incident, you can mute notifications for a set period so you're not repeatedly alerted about something you already know about. You can also mute by voice \u2014 \u201cHey Siri, mute GitHub for 2 hours\u201d \u2014 or from the Shortcuts app.",
             "<p>Yes. When viewing a service with an active incident, you can mute notifications for a set period so you're not repeatedly alerted about something you already know about. You can also mute by voice \u2014 \u201cHey Siri, mute GitHub for 2 hours\u201d \u2014 or from the Shortcuts app.</p>"),
            ("What platforms are supported?",
             "iPhone and iPad (with widgets and Live Activities), Mac (with a menu bar app plus full window), Apple Watch (with complications and Smart Stack), Apple TV, and Apple Vision Pro. The app is free to download on every platform.",
             "<p>iPhone and iPad (with widgets and Live Activities), Mac (with a menu bar app plus full window), Apple Watch (with complications and Smart Stack), Apple TV, and Apple Vision Pro. The app is free to download on every platform.</p>"),
            ("Can I request a new service?",
             "Yes! Email support@vultyr.app with the service name and its status page URL.",
             "<p>Yes! Email <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a> with the service name and its status page URL.</p>"),
        ],
    },
    "ru": {
        "html_lang": "ru",
        "og_locale": "ru_RU",
        "og_image_alt": "\u0418\u043a\u043e\u043d\u043a\u0430 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u044f Vultyr \u2014 \u043c\u043e\u043d\u0438\u0442\u043e\u0440 \u0441\u0442\u0430\u0442\u0443\u0441\u0430 \u0441\u0435\u0440\u0432\u0438\u0441\u043e\u0432",
        "devices": "iPhone, iPad, Mac, Apple Watch, Apple TV \u0438 Vision Pro",
        "skip_to_main": "\u041f\u0435\u0440\u0435\u0439\u0442\u0438 \u043a \u043e\u0441\u043d\u043e\u0432\u043d\u043e\u043c\u0443 \u0441\u043e\u0434\u0435\u0440\u0436\u0430\u043d\u0438\u044e",
        "topbar_brand_aria": "\u0413\u043b\u0430\u0432\u043d\u0430\u044f Vultyr",
        "nav_primary_aria": "\u041e\u0441\u043d\u043e\u0432\u043d\u0430\u044f",
        "nav_services": "\u0441\u0435\u0440\u0432\u0438\u0441\u044b",
        "nav_support": "\u043f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0430",
        "nav_download": "\u0421\u043a\u0430\u0447\u0430\u0442\u044c",
        "footer_nav_aria": "\u041d\u0430\u0432\u0438\u0433\u0430\u0446\u0438\u044f \u043f\u043e\u0434\u0432\u0430\u043b\u0430",
        "footer_home": "\u0413\u043b\u0430\u0432\u043d\u0430\u044f",
        "footer_services": "\u0421\u0435\u0440\u0432\u0438\u0441\u044b",
        "footer_privacy": "\u041a\u043e\u043d\u0444\u0438\u0434\u0435\u043d\u0446\u0438\u0430\u043b\u044c\u043d\u043e\u0441\u0442\u044c",
        "footer_support": "\u041f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0430",
        "footer_contact": "\u041a\u043e\u043d\u0442\u0430\u043a\u0442\u044b",
        "copyright": "\u00a9 2026 Vultyr. \u0412\u0441\u0435 \u043f\u0440\u0430\u0432\u0430 \u0437\u0430\u0449\u0438\u0449\u0435\u043d\u044b.",
        "breadcrumb_aria": "\u0425\u043b\u0435\u0431\u043d\u044b\u0435 \u043a\u0440\u043e\u0448\u043a\u0438",
        "breadcrumb_vultyr": "Vultyr",
        "breadcrumb_services": "\u0421\u0435\u0440\u0432\u0438\u0441\u044b",
        # services page
        "svcs_title": "Vultyr \u2014 200+ \u043f\u0440\u043e\u0432\u0435\u0440\u043e\u043a \u0441\u0442\u0430\u0442\u0443\u0441\u0430",
        "svcs_description": "200+ \u043f\u0440\u043e\u0432\u0435\u0440\u043e\u043a \u0441\u0442\u0430\u0442\u0443\u0441\u0430 \u043e\u0431\u043b\u0430\u0447\u043d\u044b\u0445 \u0441\u0435\u0440\u0432\u0438\u0441\u043e\u0432, \u0438\u043d\u0441\u0442\u0440\u0443\u043c\u0435\u043d\u0442\u043e\u0432 \u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0438, \u043a\u043e\u043c\u043c\u0443\u043d\u0438\u043a\u0430\u0446\u0438\u0439, \u0418\u0418 \u0438 \u0434\u0440\u0443\u0433\u0438\u0445 \u2014 \u0432\u0441\u0451 \u043f\u043e\u0434 \u043a\u043e\u043d\u0442\u0440\u043e\u043b\u0435\u043c Vultyr.",
        "svcs_h1_lead": "\u041f\u0440\u043e\u0432\u0435\u0440\u043a\u0438",
        "svcs_h1_highlight": "\u0441\u0442\u0430\u0442\u0443\u0441\u0430",
        "svcs_subtitle": "200+ \u043f\u0440\u043e\u0432\u0435\u0440\u043e\u043a \u0441\u0442\u0430\u0442\u0443\u0441\u0430, \u043a\u043e\u0442\u043e\u0440\u044b\u0435 vultyr \u0432\u044b\u043f\u043e\u043b\u043d\u044f\u0435\u0442 \u0434\u043b\u044f \u043e\u0431\u043b\u0430\u0447\u043d\u044b\u0445 \u0441\u0435\u0440\u0432\u0438\u0441\u043e\u0432, \u0438\u043d\u0441\u0442\u0440\u0443\u043c\u0435\u043d\u0442\u043e\u0432 \u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0438 \u0438 \u043f\u043b\u0430\u0442\u0444\u043e\u0440\u043c.",
        "svcs_categories_aria": "\u041f\u043e \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044f\u043c",
        "svc_row_status": "\u0421\u0442\u0430\u0442\u0443\u0441",
        "svc_row_homepage": "\u0421\u0430\u0439\u0442",
        "svcs_item_list_name": "\u0421\u0435\u0440\u0432\u0438\u0441\u044b \u043f\u043e\u0434 \u043c\u043e\u043d\u0438\u0442\u043e\u0440\u0438\u043d\u0433\u043e\u043c Vultyr",
        # service page
        "svcp_title_fmt": "{name} \u043d\u0435 \u0440\u0430\u0431\u043e\u0442\u0430\u0435\u0442? \u041c\u043e\u043d\u0438\u0442\u043e\u0440 \u0441\u0442\u0430\u0442\u0443\u0441\u0430 {name} | Vultyr",
        "svcp_description_fmt": "\u041f\u0440\u043e\u0432\u0435\u0440\u044c\u0442\u0435, \u0440\u0430\u0431\u043e\u0442\u0430\u0435\u0442 \u043b\u0438 {name} \u043f\u0440\u044f\u043c\u043e \u0441\u0435\u0439\u0447\u0430\u0441. \u0410\u043a\u0442\u0443\u0430\u043b\u044c\u043d\u044b\u0439 \u0441\u0442\u0430\u0442\u0443\u0441 {name} \u0438 \u043c\u043e\u043d\u0438\u0442\u043e\u0440\u0438\u043d\u0433 \u0441\u0431\u043e\u0435\u0432 \u0441 Vultyr. \u0411\u0435\u0441\u043f\u043b\u0430\u0442\u043d\u043e \u043d\u0430 {devices}.",
        "svcp_live_check": "\u041f\u0440\u043e\u0432\u0435\u0440\u043a\u0430 \u0432 \u0440\u0435\u0430\u043b\u044c\u043d\u043e\u043c \u0432\u0440\u0435\u043c\u0435\u043d\u0438",
        "svcp_view_current_status": "\u041f\u043e\u0441\u043c\u043e\u0442\u0440\u0435\u0442\u044c \u0442\u0435\u043a\u0443\u0449\u0438\u0439 \u0441\u0442\u0430\u0442\u0443\u0441 \u2192",
        "svcp_alert_hint_prefix": "\u0427\u0442\u043e\u0431\u044b \u043f\u043e\u043b\u0443\u0447\u0430\u0442\u044c \u043c\u0433\u043d\u043e\u0432\u0435\u043d\u043d\u044b\u0435 \u0443\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u044f, ",
        "svcp_alert_hint_link": "\u0441\u043a\u0430\u0447\u0430\u0439\u0442\u0435 Vultyr",
        "svcp_categories_label": "\u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0438:",
        "svcp_official_status": "\u041e\u0444\u0438\u0446\u0438\u0430\u043b\u044c\u043d\u0430\u044f \u0441\u0442\u0440\u0430\u043d\u0438\u0446\u0430 \u0441\u0442\u0430\u0442\u0443\u0441\u0430",
        "svcp_homepage_fmt": "\u0421\u0430\u0439\u0442 {name}",
        "svcp_faq_heading": "\u0412\u043e\u043f\u0440\u043e\u0441\u044b \u0438 \u043e\u0442\u0432\u0435\u0442\u044b",
        "svcp_faq_q1_fmt": "\u0420\u0430\u0431\u043e\u0442\u0430\u0435\u0442 \u043b\u0438 {name} \u043f\u0440\u044f\u043c\u043e \u0441\u0435\u0439\u0447\u0430\u0441?",
        "svcp_faq_a1_fmt": "\u041e\u0442\u043a\u0440\u043e\u0439\u0442\u0435 \u043e\u0444\u0438\u0446\u0438\u0430\u043b\u044c\u043d\u0443\u044e \u0441\u0442\u0440\u0430\u043d\u0438\u0446\u0443 \u0441\u0442\u0430\u0442\u0443\u0441\u0430 {name} \u043f\u043e \u0441\u0441\u044b\u043b\u043a\u0435 \u0432\u044b\u0448\u0435, \u0447\u0442\u043e\u0431\u044b \u0443\u0432\u0438\u0434\u0435\u0442\u044c \u0442\u0435\u043a\u0443\u0449\u0435\u0435 \u0441\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u0435. \u0414\u043b\u044f \u043d\u0435\u043f\u0440\u0435\u0440\u044b\u0432\u043d\u043e\u0433\u043e \u043c\u043e\u043d\u0438\u0442\u043e\u0440\u0438\u043d\u0433\u0430 \u0441 \u043c\u0433\u043d\u043e\u0432\u0435\u043d\u043d\u044b\u043c\u0438 \u0443\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u044f\u043c\u0438 \u043e \u0441\u0431\u043e\u044f\u0445 \u043d\u0430 \u0432\u0441\u0435\u0445 \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0430\u0445 Apple \u0441\u043a\u0430\u0447\u0430\u0439\u0442\u0435 \u0431\u0435\u0441\u043f\u043b\u0430\u0442\u043d\u043e\u0435 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 Vultyr.",
        "svcp_faq_a1_ld_fmt": "\u041e\u0442\u043a\u0440\u043e\u0439\u0442\u0435 \u043e\u0444\u0438\u0446\u0438\u0430\u043b\u044c\u043d\u0443\u044e \u0441\u0442\u0440\u0430\u043d\u0438\u0446\u0443 \u0441\u0442\u0430\u0442\u0443\u0441\u0430 {name} \u043f\u043e \u0430\u0434\u0440\u0435\u0441\u0443 {url}. \u0421\u043a\u0430\u0447\u0430\u0439\u0442\u0435 \u0431\u0435\u0441\u043f\u043b\u0430\u0442\u043d\u043e\u0435 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 Vultyr, \u0447\u0442\u043e\u0431\u044b \u043f\u043e\u043b\u0443\u0447\u0430\u0442\u044c \u043c\u0433\u043d\u043e\u0432\u0435\u043d\u043d\u044b\u0435 \u0443\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u044f \u043e \u0441\u0431\u043e\u044f\u0445 \u043d\u0430 \u0432\u0441\u0435\u0445 \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0430\u0445 Apple.",
        "svcp_faq_q2_fmt": "\u041a\u0430\u043a \u043e\u0442\u0441\u043b\u0435\u0436\u0438\u0432\u0430\u0442\u044c \u0441\u0442\u0430\u0442\u0443\u0441 {name}?",
        "svcp_faq_a2_fmt": "Vultyr \u043e\u0442\u0441\u043b\u0435\u0436\u0438\u0432\u0430\u0435\u0442 {name} \u0432 \u0441\u043e\u0441\u0442\u0430\u0432\u0435 200+ \u043f\u0440\u043e\u0432\u0435\u0440\u043e\u043a \u0441\u0442\u0430\u0442\u0443\u0441\u0430 \u0434\u043b\u044f \u043e\u0431\u043b\u0430\u0447\u043d\u044b\u0445 \u0441\u0435\u0440\u0432\u0438\u0441\u043e\u0432, \u0438\u043d\u0441\u0442\u0440\u0443\u043c\u0435\u043d\u0442\u043e\u0432 \u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0438 \u0438 \u043f\u043b\u0430\u0442\u0444\u043e\u0440\u043c. \u041f\u043e\u043b\u0443\u0447\u0430\u0439\u0442\u0435 \u043c\u0433\u043d\u043e\u0432\u0435\u043d\u043d\u044b\u0435 \u0443\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u044f \u043e \u0441\u0431\u043e\u044f\u0445 \u043d\u0430 {devices} \u2014 \u043f\u043e\u043b\u043d\u043e\u0441\u0442\u044c\u044e \u0431\u0435\u0441\u043f\u043b\u0430\u0442\u043d\u043e.",
        "svcp_faq_a2_ld_fmt": "\u0421\u043a\u0430\u0447\u0430\u0439\u0442\u0435 Vultyr (\u0431\u0435\u0441\u043f\u043b\u0430\u0442\u043d\u043e), \u0447\u0442\u043e\u0431\u044b \u043e\u0442\u0441\u043b\u0435\u0436\u0438\u0432\u0430\u0442\u044c {name} \u0432 \u0441\u043e\u0441\u0442\u0430\u0432\u0435 200+ \u043f\u0440\u043e\u0432\u0435\u0440\u043e\u043a \u0441\u0442\u0430\u0442\u0443\u0441\u0430 \u0441 \u043c\u0433\u043d\u043e\u0432\u0435\u043d\u043d\u044b\u043c\u0438 \u0443\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u044f\u043c\u0438 \u043d\u0430 {devices}. Vultyr \u0432\u044b\u043f\u043e\u043b\u043d\u044f\u0435\u0442 \u043a\u0430\u0436\u0434\u0443\u044e \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0443 \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438 \u0438 \u0443\u0432\u0435\u0434\u043e\u043c\u043b\u044f\u0435\u0442, \u043a\u0430\u043a \u0442\u043e\u043b\u044c\u043a\u043e \u043e\u0431\u043d\u0430\u0440\u0443\u0436\u0435\u043d \u0441\u0431\u043e\u0439.",
        "svcp_related_heading": "\u041f\u043e\u0445\u043e\u0436\u0438\u0435 \u0441\u0435\u0440\u0432\u0438\u0441\u044b",
        "svcp_related_aria": "\u041f\u043e\u0445\u043e\u0436\u0438\u0435 \u0441\u0435\u0440\u0432\u0438\u0441\u044b",
        "svcp_cta_heading_fmt": "\u041e\u0442\u0441\u043b\u0435\u0436\u0438\u0432\u0430\u0439\u0442\u0435 {name} \u043d\u0430 \u0432\u0441\u0435\u0445 \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0430\u0445",
        "svcp_cta_body_fmt": "\u041f\u043e\u043b\u0443\u0447\u0430\u0439\u0442\u0435 \u043c\u0433\u043d\u043e\u0432\u0435\u043d\u043d\u044b\u0435 \u0443\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u044f, \u043a\u043e\u0433\u0434\u0430 {name} \u043d\u0435\u0434\u043e\u0441\u0442\u0443\u043f\u0435\u043d. \u0411\u0435\u0441\u043f\u043b\u0430\u0442\u043d\u043e \u043d\u0430 \u0432\u0441\u0435\u0445 \u043f\u043b\u0430\u0442\u0444\u043e\u0440\u043c\u0430\u0445 Apple.",
        "cta_download_vultyr": "\u0421\u043a\u0430\u0447\u0430\u0442\u044c Vultyr",
        "cta_download_vultyr_aria": "\u0421\u043a\u0430\u0447\u0430\u0442\u044c Vultyr \u0432 App Store",
        # category page
        "catp_title_fmt": "\u041c\u043e\u043d\u0438\u0442\u043e\u0440\u0438\u043d\u0433 \u0441\u0442\u0430\u0442\u0443\u0441\u0430 \u00ab{name}\u00bb \u2014 {count_services} | Vultyr",
        "catp_description_fmt": "\u041e\u0442\u0441\u043b\u0435\u0436\u0438\u0432\u0430\u0439\u0442\u0435 \u0441\u0442\u0430\u0442\u0443\u0441 {count_services} \u0432 \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0438 \u00ab{name_lower}\u00bb. \u0423\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u044f \u043e \u0441\u0431\u043e\u044f\u0445 \u0432 \u0440\u0435\u0430\u043b\u044c\u043d\u043e\u043c \u0432\u0440\u0435\u043c\u0435\u043d\u0438 \u0434\u043b\u044f {sample} \u0438 \u0434\u0440\u0443\u0433\u0438\u0445.",
        "catp_item_list_name_fmt": "\u041c\u043e\u043d\u0438\u0442\u043e\u0440\u044b \u0441\u0442\u0430\u0442\u0443\u0441\u0430: {name}",
        "catp_subtitle_fmt": "{count_services} \u043f\u043e\u0434 \u043c\u043e\u043d\u0438\u0442\u043e\u0440\u0438\u043d\u0433\u043e\u043c Vultyr",
        "catp_services_aria_fmt": "\u0421\u0435\u0440\u0432\u0438\u0441\u044b \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0438 {name}",
        "catp_other_heading": "\u0414\u0440\u0443\u0433\u0438\u0435 \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0438",
        "catp_cta_heading_fmt": "\u041c\u043e\u043d\u0438\u0442\u043e\u0440\u044c\u0442\u0435 \u0432\u0441\u0435 {count_services} \u043c\u0433\u043d\u043e\u0432\u0435\u043d\u043d\u043e",
        "catp_cta_body": "\u041f\u043e\u043b\u0443\u0447\u0430\u0439\u0442\u0435 \u0443\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u044f \u043e \u0441\u0431\u043e\u044f\u0445 \u0432 \u0440\u0435\u0430\u043b\u044c\u043d\u043e\u043c \u0432\u0440\u0435\u043c\u0435\u043d\u0438 \u043d\u0430 \u0432\u0441\u0435\u0445 \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0430\u0445 Apple. \u0411\u0435\u0441\u043f\u043b\u0430\u0442\u043d\u043e.",
        # home page
        "home_title": "Vultyr \u2014 \u043c\u043e\u043d\u0438\u0442\u043e\u0440\u0438\u043d\u0433 \u0441\u0442\u0430\u0442\u0443\u0441\u0430 AWS, Slack, GitHub \u0438 \u0434\u0440\u0443\u0433\u0438\u0445",
        "home_description": "\u041d\u0435 \u0440\u0430\u0431\u043e\u0442\u0430\u0435\u0442? 200+ \u043f\u0440\u043e\u0432\u0435\u0440\u043e\u043a \u0441\u0442\u0430\u0442\u0443\u0441\u0430 \u043e\u0431\u043b\u0430\u0447\u043d\u044b\u0445 \u0441\u0435\u0440\u0432\u0438\u0441\u043e\u0432, \u0438\u043d\u0441\u0442\u0440\u0443\u043c\u0435\u043d\u0442\u043e\u0432 \u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0438 \u0438 \u043f\u043b\u0430\u0442\u0444\u043e\u0440\u043c \u0441 \u043c\u0433\u043d\u043e\u0432\u0435\u043d\u043d\u044b\u043c\u0438 \u0443\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u044f\u043c\u0438 \u043e \u0441\u0431\u043e\u044f\u0445. \u0411\u0435\u0441\u043f\u043b\u0430\u0442\u043d\u043e \u043d\u0430 iPhone, iPad, Mac, Apple Watch, Apple TV \u0438 Apple Vision Pro.",
        "home_og_title": "Vultyr \u2014 \u043c\u043e\u043d\u0438\u0442\u043e\u0440 \u0441\u0442\u0430\u0442\u0443\u0441\u0430 \u0441\u0435\u0440\u0432\u0438\u0441\u043e\u0432",
        "home_app_ld_description": "\u041e\u0442\u0441\u043b\u0435\u0436\u0438\u0432\u0430\u0439\u0442\u0435 200+ \u043f\u0440\u043e\u0432\u0435\u0440\u043e\u043a \u0441\u0442\u0430\u0442\u0443\u0441\u0430 \u043e\u0431\u043b\u0430\u0447\u043d\u044b\u0445 \u0441\u0435\u0440\u0432\u0438\u0441\u043e\u0432, \u0438\u043d\u0441\u0442\u0440\u0443\u043c\u0435\u043d\u0442\u043e\u0432 \u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0438 \u0438 \u043f\u043b\u0430\u0442\u0444\u043e\u0440\u043c \u0441 \u043c\u0433\u043d\u043e\u0432\u0435\u043d\u043d\u044b\u043c\u0438 \u0443\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u044f\u043c\u0438 \u043e \u0441\u0431\u043e\u044f\u0445.",
        "home_hero_tag": "200+ \u043f\u0440\u043e\u0432\u0435\u0440\u043e\u043a",
        "home_hero_question": "\u041d\u0435 \u0440\u0430\u0431\u043e\u0442\u0430\u0435\u0442?",
        "home_hero_answer": "\u0423\u0437\u043d\u0430\u0439\u0442\u0435 \u0440\u0430\u043d\u044c\u0448\u0435 \u0441\u0432\u043e\u0438\u0445 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439.",
        "home_hero_services": "200+ \u043f\u0440\u043e\u0432\u0435\u0440\u043e\u043a \u0441\u0442\u0430\u0442\u0443\u0441\u0430 \u2014 AWS, GitHub, Slack, Stripe \u0438 \u0434\u0440\u0443\u0433\u0438\u0435 \u2014 \u0441 \u043c\u0433\u043d\u043e\u0432\u0435\u043d\u043d\u044b\u043c\u0438 \u0443\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u044f\u043c\u0438 \u043e \u0441\u0431\u043e\u044f\u0445 \u043d\u0430 \u0432\u0441\u0435\u0445 \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0430\u0445 Apple.",
        "home_appstore_alt": "\u0421\u043a\u0430\u0447\u0430\u0442\u044c \u0432 App Store",
        "home_appstore_aria": "\u0421\u043a\u0430\u0447\u0430\u0442\u044c Vultyr \u0432 App Store",
        "home_free_on_prefix": "\u0411\u0435\u0441\u043f\u043b\u0430\u0442\u043d\u043e \u043d\u0430",
        "home_screenshots_aria": "\u0421\u043a\u0440\u0438\u043d\u0448\u043e\u0442\u044b \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u044f",
        "home_screenshot_dash_alt": "\u0414\u0430\u0448\u0431\u043e\u0440\u0434 Vultyr \u0441\u043e \u0441\u0442\u0430\u0442\u0443\u0441\u043e\u043c \u00ab\u0412\u0441\u0451 \u0440\u0430\u0431\u043e\u0442\u0430\u0435\u0442\u00bb \u0438 \u0441\u0435\u0440\u0432\u0438\u0441\u0430\u043c\u0438 AWS, GitHub \u0438 Slack \u043f\u043e\u0434 \u043c\u043e\u043d\u0438\u0442\u043e\u0440\u0438\u043d\u0433\u043e\u043c",
        "home_screenshot_settings_alt_fmt": "\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u043e\u0444\u043e\u0440\u043c\u043b\u0435\u043d\u0438\u044f Vultyr \u0441 {themes} \u0442\u0435\u043c\u0430\u043c\u0438, \u0432\u043a\u043b\u044e\u0447\u0430\u044f Terminal, Amber, Dracula \u0438 Nord",
        "home_screenshot_services_alt_fmt": "\u0411\u0440\u0430\u0443\u0437\u0435\u0440 \u0441\u0435\u0440\u0432\u0438\u0441\u043e\u0432 Vultyr \u0441 {categories} \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044f\u043c\u0438, \u0432\u043a\u043b\u044e\u0447\u0430\u044f Cloud, Dev Tools \u0438 AI",
        "home_stats_aria": "\u041a\u043b\u044e\u0447\u0435\u0432\u044b\u0435 \u0446\u0438\u0444\u0440\u044b",
        "home_stats_checks": "\u041f\u0440\u043e\u0432\u0435\u0440\u043e\u043a",
        "home_stats_categories": "\u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0439",
        "home_stats_platforms": "\u041f\u043b\u0430\u0442\u0444\u043e\u0440\u043c",
        "home_stats_languages": "\u042f\u0437\u044b\u043a\u043e\u0432",
        "home_features_heading": "\u0412\u0441\u0451 \u043d\u0435\u043e\u0431\u0445\u043e\u0434\u0438\u043c\u043e\u0435, \u0447\u0442\u043e\u0431\u044b \u043e\u043f\u0435\u0440\u0435\u0436\u0430\u0442\u044c \u0441\u0431\u043e\u0438",
        "home_features_sub": "\u0411\u0435\u0437 \u0430\u043a\u043a\u0430\u0443\u043d\u0442\u043e\u0432, \u0431\u0435\u0437 \u0432\u0441\u0442\u0440\u043e\u0435\u043d\u043d\u043e\u0433\u043e \u0442\u0440\u0435\u043a\u0438\u043d\u0433\u0430. \u0422\u043e\u043b\u044c\u043a\u043e \u0441\u0442\u0430\u0442\u0443\u0441.",
        "home_bottom_heading": "\u0413\u043e\u0442\u043e\u0432\u044b \u043c\u043e\u043d\u0438\u0442\u043e\u0440\u0438\u0442\u044c \u0441\u0432\u043e\u0439 \u0441\u0442\u0435\u043a?",
        "home_bottom_sub": "\u0411\u0435\u0441\u043f\u043b\u0430\u0442\u043d\u043e. \u0411\u0435\u0437 \u0430\u043a\u043a\u0430\u0443\u043d\u0442\u0430. \u0412\u0435\u0437\u0434\u0435 \u0434\u043e\u0441\u0442\u0443\u043f\u043d\u043e.",
        "home_bottom_button": "\u0421\u043a\u0430\u0447\u0430\u0442\u044c \u0431\u0435\u0441\u043f\u043b\u0430\u0442\u043d\u043e",
        "home_bottom_aria": "\u0421\u043a\u0430\u0447\u0430\u0442\u044c Vultyr \u0431\u0435\u0441\u043f\u043b\u0430\u0442\u043d\u043e \u0432 App Store",
        "home_languages_heading": "\u0414\u043e\u0441\u0442\u0443\u043f\u043d\u043e \u043d\u0430 17 \u044f\u0437\u044b\u043a\u0430\u0445",
        "home_features": [
            ("chart-bar-regular.svg", "Дашборд статуса в реальном времени",
             "AWS, GitHub, Cloudflare, Slack, Stripe, Discord, OpenAI, Anthropic и 200+ других — всё в одном месте. Индикаторы статуса синхронизируются с 120Гц ProMotion на iPhone Pro и iPad Pro."),
            ("bell-ringing-regular.svg", "Умные уведомления",
             "Уведомления о сбоях и восстановлении с favicon каждого сервиса на iOS. Крупные сбои пульсируют заметно сильнее мелких инцидентов — тяжесть видна с первого взгляда. Отключайте известные инциденты, отмечайте критичные сервисы."),
            ("microphone-regular.svg",
             "Siri и Команды",
             "Скажите Siri «отключи GitHub на 2 часа» или «покажи текущие проблемы». App Intents на каждое действие, плюс Focus Filter, который заглушает неважные сервисы."),
            ("squares-four-regular.svg",
             "Виджеты и Live Activities",
             "Виджеты на экране «Домой» и экране блокировки на iOS, плюс виджет в Пункте управления. Активные сбои закрепляются в Dynamic Island как Live Activities."),
            ("watch-regular.svg",
             "Осложнения на часах",
             "Закрепите важный сервис на циферблате или доверьте Smart Stack автоматически показывать активные проблемы."),
            ("cloud-check-regular.svg", "Mac — центр, iPhone — резерв",
             "Mac — самый надёжный центр: он проверяет с частотой до 60 секунд (настраивается до 15 мин) и рассылает изменения статуса на iPhone, iPad, Watch и Vision Pro через iCloud. Если Mac не в сети, ваш iPhone замещает его в качестве резервного издателя, чтобы другие устройства всё равно получали уведомления."),
            ("monitor-regular.svg", "Надёжность уведомлений",
             "С одного взгляда понятно, дойдут ли уведомления — heartbeat Mac, состояние фонового обновления, push через CloudKit и время последней проверки на каждом устройстве."),
            ("devices-regular.svg",
             "Все платформы Apple",
             "iPhone, iPad, строка меню Mac, Apple TV, Apple Watch и Vision Pro. Сервисы синхронизируются между устройствами."),
            ("lightning-regular.svg",
             "Детали инцидентов",
             "Затронутые компоненты, активные инциденты, плановые работы и обновления таймлайна \u2014 на вашем языке."),
            ("battery-charging-regular.svg", "Умный опрос с учётом батареи",
             "Умное автообновление адаптируется под батарею, питание и температуру. Каждую минуту на Mac, 5–15 на iPhone, с фоновым обновлением на iPad, Apple Watch, Vision Pro и Apple TV."),
            ("palette-regular.svg", f"{THEMES_COUNT} тем",
             "Standard и три ретро-темы включены. Fossil, Monolith, HAL и остальные открываются опциональными донатами через IAP."),
            ("shield-check-regular.svg",
             "Данные остаются на устройстве",
             "В приложении нет регистрации и встроенной аналитики. Отслеживаемые сервисы хранятся на вашем устройстве."),
            ("translate-regular.svg", f"{APP_LANGUAGE_COUNT} языков приложения",
             "Английский, немецкий, французский, испанский, японский, корейский, китайский, португальский, русский и другие."),
        ],
        # 404
        "err_title": "\u0421\u0442\u0440\u0430\u043d\u0438\u0446\u0430 \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u0430 \u2014 Vultyr",
        "err_description": "\u0417\u0430\u043f\u0440\u0430\u0448\u0438\u0432\u0430\u0435\u043c\u0430\u044f \u0441\u0442\u0440\u0430\u043d\u0438\u0446\u0430 \u043d\u0435 \u0441\u0443\u0449\u0435\u0441\u0442\u0432\u0443\u0435\u0442.",
        "err_heading": "\u0421\u0442\u0440\u0430\u043d\u0438\u0446\u0430 \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u0430",
        "err_message": "\u0417\u0430\u043f\u0440\u0430\u0448\u0438\u0432\u0430\u0435\u043c\u0430\u044f \u0441\u0442\u0440\u0430\u043d\u0438\u0446\u0430 \u043d\u0435 \u0441\u0443\u0449\u0435\u0441\u0442\u0432\u0443\u0435\u0442 \u0438\u043b\u0438 \u0431\u044b\u043b\u0430 \u043f\u0435\u0440\u0435\u043c\u0435\u0449\u0435\u043d\u0430.",
        "redirect_moved_fmt": "\u042d\u0442\u0430 \u0441\u0442\u0440\u0430\u043d\u0438\u0446\u0430 \u043f\u0435\u0440\u0435\u043c\u0435\u0449\u0435\u043d\u0430. \u041f\u0435\u0440\u0435\u043d\u0430\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u043d\u0430 {name}\u2026",
        "err_popular_heading": "\u041f\u043e\u043f\u0443\u043b\u044f\u0440\u043d\u044b\u0435 \u0441\u0435\u0440\u0432\u0438\u0441\u044b",
        "err_browse_heading": "\u041f\u0440\u043e\u0441\u043c\u043e\u0442\u0440 \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0439",
        # privacy
        "privacy_title": "\u041f\u043e\u043b\u0438\u0442\u0438\u043a\u0430 \u043a\u043e\u043d\u0444\u0438\u0434\u0435\u043d\u0446\u0438\u0430\u043b\u044c\u043d\u043e\u0441\u0442\u0438",
        "privacy_description": "\u041f\u043e\u043b\u0438\u0442\u0438\u043a\u0430 \u043a\u043e\u043d\u0444\u0438\u0434\u0435\u043d\u0446\u0438\u0430\u043b\u044c\u043d\u043e\u0441\u0442\u0438 Vultyr. \u041f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 \u043d\u0435 \u0441\u043e\u0431\u0438\u0440\u0430\u0435\u0442 \u043f\u0435\u0440\u0441\u043e\u043d\u0430\u043b\u044c\u043d\u044b\u0445 \u0434\u0430\u043d\u043d\u044b\u0445. \u0421\u0430\u0439\u0442 \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0435\u0442 Google Analytics \u0431\u0435\u0437 \u0444\u0430\u0439\u043b\u043e\u0432 cookie \u0434\u043b\u044f \u0430\u0433\u0440\u0435\u0433\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u043e\u0439 \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0438 \u043f\u043e\u0441\u0435\u0449\u0435\u043d\u0438\u0439.",
        "privacy_last_updated": "\u041e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u043e: 11 \u0430\u043f\u0440\u0435\u043b\u044f 2026 \u0433.",
        "privacy_sections": [
            ("\u041a\u0440\u0430\u0442\u043a\u043e\u0435 \u0441\u043e\u0434\u0435\u0440\u0436\u0430\u043d\u0438\u0435",
             "<p><strong>\u041f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435</strong> Vultyr \u043d\u0435 \u0441\u043e\u0431\u0438\u0440\u0430\u0435\u0442, \u043d\u0435 \u0445\u0440\u0430\u043d\u0438\u0442 \u0438 \u043d\u0435 \u043f\u0435\u0440\u0435\u0434\u0430\u0451\u0442 \u043d\u0438\u043a\u0430\u043a\u0438\u0445 \u043f\u0435\u0440\u0441\u043e\u043d\u0430\u043b\u044c\u043d\u044b\u0445 \u0434\u0430\u043d\u043d\u044b\u0445. <strong>\u0421\u0430\u0439\u0442</strong> Vultyr (vultyr.app) \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0435\u0442 Google Analytics \u0431\u0435\u0437 \u0444\u0430\u0439\u043b\u043e\u0432 cookie \u0434\u043b\u044f \u043f\u043e\u043d\u0438\u043c\u0430\u043d\u0438\u044f \u0430\u0433\u0440\u0435\u0433\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u043e\u0439 \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0438 \u043f\u043e\u0441\u0435\u0449\u0435\u043d\u0438\u0439. \u041d\u0438\u0436\u0435 \u043f\u043e\u0434\u0440\u043e\u0431\u043d\u043e\u0441\u0442\u0438 \u043f\u043e \u043e\u0431\u043e\u0438\u043c \u043f\u0443\u043d\u043a\u0442\u0430\u043c.</p>"),
            ("\u041f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 \u2014 \u0441\u0431\u043e\u0440 \u0434\u0430\u043d\u043d\u044b\u0445",
             "<p>\u041f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 vultyr \u043d\u0435 \u0441\u043e\u0431\u0438\u0440\u0430\u0435\u0442 \u043d\u0438\u043a\u0430\u043a\u043e\u0439 \u043f\u0435\u0440\u0441\u043e\u043d\u0430\u043b\u044c\u043d\u043e\u0439 \u0438\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u0438. \u041e\u043d\u043e \u043d\u0435 \u0442\u0440\u0435\u0431\u0443\u0435\u0442 \u0440\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u0438, \u043d\u0435 \u0441\u043e\u0434\u0435\u0440\u0436\u0438\u0442 \u0441\u0442\u043e\u0440\u043e\u043d\u043d\u0438\u0445 SDK \u0434\u043b\u044f \u0430\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0438 \u0438\u043b\u0438 \u0442\u0440\u0435\u043a\u0438\u043d\u0433\u0430 \u0438 \u043d\u0435 \u043e\u0442\u043f\u0440\u0430\u0432\u043b\u044f\u0435\u0442 \u0434\u0430\u043d\u043d\u044b\u0435 \u043d\u0430 \u043d\u0430\u0448\u0438 \u0441\u0435\u0440\u0432\u0435\u0440\u044b.</p>"),
            ("\u041f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 \u2014 \u0441\u0435\u0442\u0435\u0432\u044b\u0435 \u0437\u0430\u043f\u0440\u043e\u0441\u044b",
             "<p>\u041f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 \u0434\u0435\u043b\u0430\u0435\u0442 \u043f\u0440\u044f\u043c\u044b\u0435 HTTPS-\u0437\u0430\u043f\u0440\u043e\u0441\u044b \u043a \u043f\u0443\u0431\u043b\u0438\u0447\u043d\u044b\u043c API \u0441\u0442\u0430\u0442\u0443\u0441-\u0441\u0442\u0440\u0430\u043d\u0438\u0446 (\u0442\u0430\u043a\u0438\u043c \u043a\u0430\u043a Statuspage.io, Apple, Google Cloud \u0438 \u0434\u0440\u0443\u0433\u0438\u043c), \u0447\u0442\u043e\u0431\u044b \u043f\u0440\u043e\u0432\u0435\u0440\u044f\u0442\u044c \u0441\u0442\u0430\u0442\u0443\u0441 \u0441\u0435\u0440\u0432\u0438\u0441\u043e\u0432. \u042d\u0442\u0438 \u0437\u0430\u043f\u0440\u043e\u0441\u044b \u0438\u0434\u0443\u0442 \u043d\u0430\u043f\u0440\u044f\u043c\u0443\u044e \u0441 \u0432\u0430\u0448\u0435\u0433\u043e \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0430 \u043a \u043f\u0443\u0431\u043b\u0438\u0447\u043d\u043e\u043c\u0443 API \u0441\u0435\u0440\u0432\u0438\u0441\u0430 \u2014 \u043e\u043d\u0438 \u043d\u0435 \u043f\u0440\u043e\u0445\u043e\u0434\u044f\u0442 \u0447\u0435\u0440\u0435\u0437 \u043d\u0430\u0448\u0438 \u0441\u0435\u0440\u0432\u0435\u0440\u044b.</p>"),
            ("\u041f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 \u2014 \u0445\u0440\u0430\u043d\u0435\u043d\u0438\u0435 \u0434\u0430\u043d\u043d\u044b\u0445",
             "<p>\u0412\u0441\u0435 \u0434\u0430\u043d\u043d\u044b\u0435 \u0445\u0440\u0430\u043d\u044f\u0442\u0441\u044f \u043b\u043e\u043a\u0430\u043b\u044c\u043d\u043e \u043d\u0430 \u0432\u0430\u0448\u0435\u043c \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0435 \u0441 \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u043d\u0438\u0435\u043c SwiftData \u043e\u0442 Apple. \u0415\u0441\u043b\u0438 \u0432\u044b \u0432\u043a\u043b\u044e\u0447\u0438\u0442\u0435 \u0441\u0438\u043d\u0445\u0440\u043e\u043d\u0438\u0437\u0430\u0446\u0438\u044e iCloud, \u0441\u043f\u0438\u0441\u043e\u043a \u043e\u0442\u0441\u043b\u0435\u0436\u0438\u0432\u0430\u0435\u043c\u044b\u0445 \u0441\u0435\u0440\u0432\u0438\u0441\u043e\u0432 \u0441\u0438\u043d\u0445\u0440\u043e\u043d\u0438\u0437\u0438\u0440\u0443\u0435\u0442\u0441\u044f \u0447\u0435\u0440\u0435\u0437 iCloud Key-Value Store \u043e\u0442 Apple, \u0440\u0435\u0433\u0443\u043b\u0438\u0440\u0443\u0435\u043c\u044b\u0439 \u043f\u043e\u043b\u0438\u0442\u0438\u043a\u043e\u0439 \u043a\u043e\u043d\u0444\u0438\u0434\u0435\u043d\u0446\u0438\u0430\u043b\u044c\u043d\u043e\u0441\u0442\u0438 Apple. \u041c\u044b \u043d\u0438\u043a\u043e\u0433\u0434\u0430 \u043d\u0435 \u0432\u0438\u0434\u0438\u043c \u044d\u0442\u0438 \u0434\u0430\u043d\u043d\u044b\u0435.</p>"),
            ("\u041f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 \u2014 \u0443\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u044f \u043c\u0435\u0436\u0434\u0443 \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0430\u043c\u0438",
             "<p>\u0415\u0441\u043b\u0438 \u0432\u044b \u0432\u043a\u043b\u044e\u0447\u0438\u0442\u0435 \u0443\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u044f \u043c\u0435\u0436\u0434\u0443 \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0430\u043c\u0438, \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f \u0441\u0442\u0430\u0442\u0443\u0441\u0430 \u043f\u0435\u0440\u0435\u0434\u0430\u044e\u0442\u0441\u044f \u043c\u0435\u0436\u0434\u0443 \u0432\u0430\u0448\u0438\u043c\u0438 \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0430\u043c\u0438 \u0447\u0435\u0440\u0435\u0437 iCloud Key-Value Store \u043e\u0442 Apple. \u041a\u043e\u0433\u0434\u0430 Mac \u043e\u0431\u043d\u0430\u0440\u0443\u0436\u0438\u0432\u0430\u0435\u0442 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u0435 \u0441\u0442\u0430\u0442\u0443\u0441\u0430, \u043e\u043d \u0437\u0430\u043f\u0438\u0441\u044b\u0432\u0430\u0435\u0442 \u043b\u0451\u0433\u043a\u0438\u0439 \u0441\u0438\u0433\u043d\u0430\u043b \u0432 \u0432\u0430\u0448 \u0430\u043a\u043a\u0430\u0443\u043d\u0442 iCloud. \u0414\u0440\u0443\u0433\u0438\u0435 \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0430 \u0437\u0430\u043c\u0435\u0447\u0430\u044e\u0442 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u0435 \u0438 \u0432\u044b\u043f\u043e\u043b\u043d\u044f\u044e\u0442 \u0441\u0432\u043e\u044e \u043b\u043e\u043a\u0430\u043b\u044c\u043d\u0443\u044e \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0443. \u0421\u0442\u043e\u0440\u043e\u043d\u043d\u0438\u0435 \u0441\u0435\u0440\u0432\u0435\u0440\u044b \u043d\u0435 \u0437\u0430\u0434\u0435\u0439\u0441\u0442\u0432\u043e\u0432\u0430\u043d\u044b \u2014 \u0432\u0441\u044f \u043a\u043e\u043c\u043c\u0443\u043d\u0438\u043a\u0430\u0446\u0438\u044f \u0438\u0434\u0451\u0442 \u0447\u0435\u0440\u0435\u0437 \u0438\u043d\u0444\u0440\u0430\u0441\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u0443 iCloud \u043e\u0442 Apple. \u0412\u044b \u043c\u043e\u0436\u0435\u0442\u0435 \u0432\u043a\u043b\u044e\u0447\u0430\u0442\u044c \u0438 \u043e\u0442\u043a\u043b\u044e\u0447\u0430\u0442\u044c \u044d\u0442\u0443 \u0444\u0443\u043d\u043a\u0446\u0438\u044e \u0441 \u043b\u044e\u0431\u043e\u0433\u043e \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0430.</p>"),
            ("\u041f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 \u2014 \u0444\u0430\u0432\u0438\u043a\u043e\u043d\u044b",
             "<p>\u0424\u0430\u0432\u0438\u043a\u043e\u043d\u044b \u0441\u0435\u0440\u0432\u0438\u0441\u043e\u0432 \u0437\u0430\u0433\u0440\u0443\u0436\u0430\u044e\u0442\u0441\u044f \u0438\u0437 \u043f\u0443\u0431\u043b\u0438\u0447\u043d\u043e\u0439 \u0441\u043b\u0443\u0436\u0431\u044b \u0444\u0430\u0432\u0438\u043a\u043e\u043d\u043e\u0432 Google \u0438 \u043a\u044d\u0448\u0438\u0440\u0443\u044e\u0442\u0441\u044f \u043b\u043e\u043a\u0430\u043b\u044c\u043d\u043e \u043d\u0430 \u0432\u0430\u0448\u0435\u043c \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0435.</p>"),
            ("\u0421\u0430\u0439\u0442 \u2014 \u0430\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0430",
             "<p>\u042d\u0442\u043e\u0442 \u0441\u0430\u0439\u0442 (vultyr.app) \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0435\u0442 Google Analytics 4 \u0432 \u0440\u0435\u0436\u0438\u043c\u0435 \u0431\u0435\u0437 \u0444\u0430\u0439\u043b\u043e\u0432 cookie \u0441 \u0430\u043d\u043e\u043d\u0438\u043c\u0438\u0437\u0430\u0446\u0438\u0435\u0439 IP \u0434\u043b\u044f \u043f\u043e\u0434\u0441\u0447\u0451\u0442\u0430 \u0430\u0433\u0440\u0435\u0433\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u044b\u0445 \u043f\u0440\u043e\u0441\u043c\u043e\u0442\u0440\u043e\u0432 \u0441\u0442\u0440\u0430\u043d\u0438\u0446. \u041a\u043e\u043d\u043a\u0440\u0435\u0442\u043d\u043e \u043c\u044b \u043d\u0430\u0441\u0442\u0440\u0430\u0438\u0432\u0430\u0435\u043c gtag.js \u0441\u043e \u0441\u043b\u0435\u0434\u0443\u044e\u0449\u0438\u043c\u0438 \u043f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u0430\u043c\u0438: <code>anonymize_ip: true</code>, <code>client_storage: 'none'</code>, <code>allow_google_signals: false</code>, <code>allow_ad_personalization_signals: false</code>. \u042d\u0442\u043e \u043e\u0437\u043d\u0430\u0447\u0430\u0435\u0442, \u0447\u0442\u043e cookie <code>_ga</code> \u043d\u0435 \u0443\u0441\u0442\u0430\u043d\u0430\u0432\u043b\u0438\u0432\u0430\u0435\u0442\u0441\u044f, \u0432\u0430\u0448 IP \u0443\u0441\u0435\u043a\u0430\u0435\u0442\u0441\u044f \u0434\u043e \u0441\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u0438\u044f, \u0440\u0435\u043a\u043b\u0430\u043c\u043d\u044b\u0435 \u0438\u0434\u0435\u043d\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u043e\u0440\u044b \u043d\u0435 \u0441\u043e\u0431\u0438\u0440\u0430\u044e\u0442\u0441\u044f. \u0421\u0430\u043c\u043e \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 vultyr \u043d\u0438\u043a\u0430\u043a\u043e\u0439 \u0430\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0438 \u043d\u0435 \u0441\u043e\u0434\u0435\u0440\u0436\u0438\u0442.</p>"),
            ("\u0421\u0430\u0439\u0442 \u2014 \u0441\u0442\u043e\u0440\u043e\u043d\u043d\u0438\u0435 \u0434\u043e\u043c\u0435\u043d\u044b",
             "<p>\u0417\u0430\u0433\u0440\u0443\u0437\u043a\u0430 vultyr.app \u0441\u0432\u044f\u0437\u044b\u0432\u0430\u0435\u0442\u0441\u044f \u0441\u043e \u0441\u043b\u0435\u0434\u0443\u044e\u0449\u0438\u043c\u0438 \u0441\u0442\u043e\u0440\u043e\u043d\u043d\u0438\u043c\u0438 \u0434\u043e\u043c\u0435\u043d\u0430\u043c\u0438:</p>\n    <ul>\n        <li><strong>www.googletagmanager.com</strong> \u2014 \u0437\u0430\u0433\u0440\u0443\u0436\u0430\u0435\u0442 \u0441\u043a\u0440\u0438\u043f\u0442 gtag.js</li>\n        <li><strong>www.google-analytics.com</strong> / <strong>*.analytics.google.com</strong> \u2014 \u043f\u0440\u0438\u043d\u0438\u043c\u0430\u0435\u0442 \u0430\u043d\u043e\u043d\u0438\u043c\u0438\u0437\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u044b\u0435 \u0441\u0438\u0433\u043d\u0430\u043b\u044b \u043e \u043f\u0440\u043e\u0441\u043c\u043e\u0442\u0440\u0430\u0445</li>\n        <li><strong>www.google.com/g/collect</strong> \u2014 \u043f\u0440\u0438\u043d\u0438\u043c\u0430\u0435\u0442 \u0442\u0435 \u0436\u0435 \u0430\u043d\u043e\u043d\u0438\u043c\u0438\u0437\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u044b\u0435 \u0441\u0438\u0433\u043d\u0430\u043b\u044b (\u0440\u0435\u0437\u0435\u0440\u0432\u043d\u044b\u0439 \u044d\u043d\u0434\u043f\u043e\u0438\u043d\u0442 \u0441\u0431\u043e\u0440\u0430 \u0434\u0430\u043d\u043d\u044b\u0445 Google Analytics 4)</li>\n    </ul>\n    <p>\u041c\u044b \u043d\u0435 \u0437\u0430\u0433\u0440\u0443\u0436\u0430\u0435\u043c Google Fonts (\u0448\u0440\u0438\u0444\u0442 Audiowide \u0440\u0430\u0437\u043c\u0435\u0449\u0451\u043d \u043d\u0430 vultyr.app) \u0438 \u043d\u0435 \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0435\u043c \u0441\u0442\u043e\u0440\u043e\u043d\u043d\u0438\u0439 \u0441\u0435\u0440\u0432\u0438\u0441 \u0444\u0430\u0432\u0438\u043a\u043e\u043d\u043e\u0432 \u0434\u043b\u044f \u0441\u043e\u0431\u0441\u0442\u0432\u0435\u043d\u043d\u044b\u0445 \u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0439 \u0441\u0430\u0439\u0442\u0430.</p>"),
            ("\u041f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 \u2014 \u0441\u0442\u043e\u0440\u043e\u043d\u043d\u0438\u0435 \u0441\u0435\u0440\u0432\u0438\u0441\u044b",
             "<p>\u041f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 vultyr \u043d\u0435 \u0438\u043d\u0442\u0435\u0433\u0440\u0438\u0440\u0443\u0435\u0442\u0441\u044f \u043d\u0438 \u0441 \u043a\u0430\u043a\u0438\u043c\u0438 \u0441\u0442\u043e\u0440\u043e\u043d\u043d\u0438\u043c\u0438 \u0441\u0435\u0440\u0432\u0438\u0441\u0430\u043c\u0438 \u0430\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0438, \u0440\u0435\u043a\u043b\u0430\u043c\u044b \u0438\u043b\u0438 \u0442\u0440\u0435\u043a\u0438\u043d\u0433\u0430. \u0415\u0434\u0438\u043d\u0441\u0442\u0432\u0435\u043d\u043d\u044b\u0435 \u0432\u043d\u0435\u0448\u043d\u0438\u0435 \u0437\u0430\u043f\u0440\u043e\u0441\u044b \u2014 \u043a \u043f\u0443\u0431\u043b\u0438\u0447\u043d\u044b\u043c API \u0441\u0442\u0430\u0442\u0443\u0441-\u0441\u0442\u0440\u0430\u043d\u0438\u0446 \u0438 \u043a \u0441\u043b\u0443\u0436\u0431\u0435 \u0444\u0430\u0432\u0438\u043a\u043e\u043d\u043e\u0432 Google.</p>"),
            ("\u041a\u043e\u043d\u0444\u0438\u0434\u0435\u043d\u0446\u0438\u0430\u043b\u044c\u043d\u043e\u0441\u0442\u044c \u0434\u0435\u0442\u0435\u0439",
             "<p>\u041f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 vultyr \u043d\u0438 \u0443 \u043a\u043e\u0433\u043e \u043d\u0435 \u0441\u043e\u0431\u0438\u0440\u0430\u0435\u0442 \u0434\u0430\u043d\u043d\u044b\u0435, \u0432 \u0442\u043e\u043c \u0447\u0438\u0441\u043b\u0435 \u0443 \u0434\u0435\u0442\u0435\u0439 \u043c\u043b\u0430\u0434\u0448\u0435 13 \u043b\u0435\u0442. \u0421\u0430\u0439\u0442 \u0444\u0438\u043a\u0441\u0438\u0440\u0443\u0435\u0442 \u0442\u043e\u043b\u044c\u043a\u043e \u0430\u043d\u043e\u043d\u0438\u043c\u0438\u0437\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u044b\u0435 \u0430\u0433\u0440\u0435\u0433\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u044b\u0435 \u0441\u0447\u0451\u0442\u0447\u0438\u043a\u0438 \u043f\u043e\u0441\u0435\u0449\u0435\u043d\u0438\u0439.</p>"),
            ("\u0418\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f",
             "<p>\u0415\u0441\u043b\u0438 \u044d\u0442\u0430 \u043f\u043e\u043b\u0438\u0442\u0438\u043a\u0430 \u0438\u0437\u043c\u0435\u043d\u0438\u0442\u0441\u044f, \u043c\u044b \u043e\u0431\u043d\u043e\u0432\u0438\u043c \u0434\u0430\u0442\u0443 \u0432\u044b\u0448\u0435.</p>"),
            ("\u041a\u043e\u043d\u0442\u0430\u043a\u0442\u044b",
             "<p>\u0412\u043e\u043f\u0440\u043e\u0441\u044b? \u041f\u0438\u0448\u0438\u0442\u0435 \u043d\u0430 <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a></p>"),
        ],
        # support
        "support_title": "\u041f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0430",
        "support_description": "\u041f\u043e\u043c\u043e\u0449\u044c \u043f\u043e Vultyr \u2014 \u043c\u043e\u043d\u0438\u0442\u043e\u0440\u0438\u043d\u0433\u0443 \u0441\u0442\u0430\u0442\u0443\u0441\u0430 \u0441\u0435\u0440\u0432\u0438\u0441\u043e\u0432 \u0434\u043b\u044f iPhone, iPad, Mac, Apple Watch, Apple TV \u0438 Apple Vision Pro. \u0412\u043e\u043f\u0440\u043e\u0441\u044b \u0438 \u043e\u0442\u0432\u0435\u0442\u044b, \u043a\u043e\u043d\u0442\u0430\u043a\u0442\u044b, \u0434\u0438\u0430\u0433\u043d\u043e\u0441\u0442\u0438\u043a\u0430.",
        "support_contact_heading": "\u041a\u043e\u043d\u0442\u0430\u043a\u0442\u044b",
        "support_contact_html": "<p>\u0414\u043b\u044f \u043e\u0442\u0447\u0451\u0442\u043e\u0432 \u043e\u0431 \u043e\u0448\u0438\u0431\u043a\u0430\u0445, \u0437\u0430\u043f\u0440\u043e\u0441\u043e\u0432 \u0444\u0443\u043d\u043a\u0446\u0438\u0439 \u0438 \u0432\u043e\u043f\u0440\u043e\u0441\u043e\u0432:<br>\n    <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a></p>",
        "support_faq_heading": "\u0412\u043e\u043f\u0440\u043e\u0441\u044b \u0438 \u043e\u0442\u0432\u0435\u0442\u044b",
        "support_faqs": [
            ("\u041a\u0430\u043a \u0447\u0430\u0441\u0442\u043e vultyr \u043f\u0440\u043e\u0432\u0435\u0440\u044f\u0435\u0442 \u0441\u0442\u0430\u0442\u0443\u0441 \u0441\u0435\u0440\u0432\u0438\u0441\u043e\u0432?",
             "\u041d\u0430 Mac: \u0440\u0430\u0437 \u0432 60 \u0441\u0435\u043a\u0443\u043d\u0434 \u043f\u0440\u0438 \u043f\u043e\u0434\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u0438 \u043a \u043f\u0438\u0442\u0430\u043d\u0438\u044e. \u041d\u0430 iPhone: \u043a\u0430\u0436\u0434\u044b\u0435 5, 10 \u0438\u043b\u0438 15 \u043c\u0438\u043d\u0443\u0442 (\u043d\u0430\u0441\u0442\u0440\u0430\u0438\u0432\u0430\u0435\u0442\u0441\u044f), \u0441 \u043f\u0435\u0440\u0438\u043e\u0434\u0438\u0447\u0435\u0441\u043a\u0438\u043c\u0438 \u0444\u043e\u043d\u043e\u0432\u044b\u043c\u0438 \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0430\u043c\u0438. \u041d\u0430 Apple Watch: \u043a\u0430\u0436\u0434\u044b\u0435 15 \u043c\u0438\u043d\u0443\u0442. \u041d\u0430 Apple TV: \u043a\u0430\u0436\u0434\u044b\u0435 5 \u043c\u0438\u043d\u0443\u0442. \u041e\u043f\u0440\u043e\u0441 \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438 \u0430\u0434\u0430\u043f\u0442\u0438\u0440\u0443\u0435\u0442\u0441\u044f \u043a \u0437\u0430\u0440\u044f\u0434\u0443 \u0431\u0430\u0442\u0430\u0440\u0435\u0438, \u043f\u0438\u0442\u0430\u043d\u0438\u044e \u0438 \u0442\u0435\u043c\u043f\u0435\u0440\u0430\u0442\u0443\u0440\u0435.",
             "<p>\u041d\u0430 Mac: \u0440\u0430\u0437 \u0432 60 \u0441\u0435\u043a\u0443\u043d\u0434 \u043f\u0440\u0438 \u043f\u043e\u0434\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u0438 \u043a \u043f\u0438\u0442\u0430\u043d\u0438\u044e. \u041d\u0430 iPhone: \u043a\u0430\u0436\u0434\u044b\u0435 5, 10 \u0438\u043b\u0438 15 \u043c\u0438\u043d\u0443\u0442 (\u043d\u0430\u0441\u0442\u0440\u0430\u0438\u0432\u0430\u0435\u0442\u0441\u044f), \u0441 \u043f\u0435\u0440\u0438\u043e\u0434\u0438\u0447\u0435\u0441\u043a\u0438\u043c\u0438 \u0444\u043e\u043d\u043e\u0432\u044b\u043c\u0438 \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0430\u043c\u0438. \u041d\u0430 Apple Watch: \u043a\u0430\u0436\u0434\u044b\u0435 15 \u043c\u0438\u043d\u0443\u0442. \u041d\u0430 Apple TV: \u043a\u0430\u0436\u0434\u044b\u0435 5 \u043c\u0438\u043d\u0443\u0442. \u041e\u043f\u0440\u043e\u0441 \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438 \u0430\u0434\u0430\u043f\u0442\u0438\u0440\u0443\u0435\u0442\u0441\u044f \u043a \u0437\u0430\u0440\u044f\u0434\u0443 \u0431\u0430\u0442\u0430\u0440\u0435\u0438, \u043f\u0438\u0442\u0430\u043d\u0438\u044e \u0438 \u0442\u0435\u043c\u043f\u0435\u0440\u0430\u0442\u0443\u0440\u0435.</p>"),
            ("\u041a\u0430\u043a \u0440\u0430\u0431\u043e\u0442\u0430\u044e\u0442 \u0443\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u044f \u043c\u0435\u0436\u0434\u0443 \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0430\u043c\u0438?",
             "\u041f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 Mac \u2014 \u044d\u0442\u043e \u0446\u0435\u043d\u0442\u0440. \u0414\u0435\u0440\u0436\u0438\u0442\u0435 \u0435\u0433\u043e \u0437\u0430\u043f\u0443\u0449\u0435\u043d\u043d\u044b\u043c (\u0432 \u0441\u0442\u0440\u043e\u043a\u0435 \u043c\u0435\u043d\u044e \u0438\u043b\u0438 \u043f\u043e\u043b\u043d\u044b\u043c \u043e\u043a\u043d\u043e\u043c), \u0438 \u043e\u043d\u043e \u043e\u043f\u0440\u0430\u0448\u0438\u0432\u0430\u0435\u0442 \u043a\u0430\u0436\u0434\u044b\u0435 60 \u0441\u0435\u043a\u0443\u043d\u0434. \u041f\u0440\u0438 \u043e\u0431\u043d\u0430\u0440\u0443\u0436\u0435\u043d\u0438\u0438 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f \u0441\u0442\u0430\u0442\u0443\u0441\u0430 \u043e\u043d\u043e \u0437\u0430\u043f\u0438\u0441\u044b\u0432\u0430\u0435\u0442 \u043b\u0451\u0433\u043a\u0438\u0439 \u0441\u0438\u0433\u043d\u0430\u043b \u0432 iCloud Key-Value Store; \u0432\u0430\u0448\u0438 iPhone, iPad, Watch, Apple TV \u0438 Vision Pro \u043f\u043e\u0434\u0445\u0432\u0430\u0442\u044b\u0432\u0430\u044e\u0442 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u0435 \u0438 \u0432\u044b\u043f\u043e\u043b\u043d\u044f\u044e\u0442 \u0441\u0432\u043e\u044e \u043b\u043e\u043a\u0430\u043b\u044c\u043d\u0443\u044e \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0443. \u041d\u0438\u043a\u0430\u043a\u0438\u0445 \u043a\u043b\u044e\u0447\u0435\u0439, \u0442\u043e\u043a\u0435\u043d\u043e\u0432 \u0438 \u043d\u0430\u0441\u0442\u0440\u043e\u0435\u043a \u2014 \u043f\u0440\u043e\u0441\u0442\u043e \u0432\u043a\u043b\u044e\u0447\u0438\u0442\u0435 \u00ab\u0423\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u044f \u043c\u0435\u0436\u0434\u0443 \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0430\u043c\u0438\u00bb \u0432 \u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430\u0445 \u043d\u0430 \u043b\u044e\u0431\u043e\u043c \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0435. \u0411\u0435\u0437 Mac \u0432 \u0440\u043e\u043b\u0438 \u0446\u0435\u043d\u0442\u0440\u0430 \u043e\u043f\u043e\u0432\u0435\u0449\u0435\u043d\u0438\u044f \u0437\u0430\u0432\u0438\u0441\u044f\u0442 \u043e\u0442 \u0444\u043e\u043d\u043e\u0432\u043e\u0433\u043e \u0438\u0441\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u044f iOS \u0438 \u0431\u0443\u0434\u0443\u0442 \u0437\u0430\u0434\u0435\u0440\u0436\u0430\u043d\u044b \u0438\u043b\u0438 \u043f\u0440\u043e\u043f\u0443\u0449\u0435\u043d\u044b.",
             "<p>\u041f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 Mac \u2014 \u044d\u0442\u043e \u0446\u0435\u043d\u0442\u0440. \u0414\u0435\u0440\u0436\u0438\u0442\u0435 \u0435\u0433\u043e \u0437\u0430\u043f\u0443\u0449\u0435\u043d\u043d\u044b\u043c (\u0432 \u0441\u0442\u0440\u043e\u043a\u0435 \u043c\u0435\u043d\u044e \u0438\u043b\u0438 \u043f\u043e\u043b\u043d\u044b\u043c \u043e\u043a\u043d\u043e\u043c), \u0438 \u043e\u043d\u043e \u043e\u043f\u0440\u0430\u0448\u0438\u0432\u0430\u0435\u0442 \u043a\u0430\u0436\u0434\u044b\u0435 60 \u0441\u0435\u043a\u0443\u043d\u0434. \u041f\u0440\u0438 \u043e\u0431\u043d\u0430\u0440\u0443\u0436\u0435\u043d\u0438\u0438 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f \u0441\u0442\u0430\u0442\u0443\u0441\u0430 \u043e\u043d\u043e \u0437\u0430\u043f\u0438\u0441\u044b\u0432\u0430\u0435\u0442 \u043b\u0451\u0433\u043a\u0438\u0439 \u0441\u0438\u0433\u043d\u0430\u043b \u0432 iCloud Key-Value Store; \u0432\u0430\u0448\u0438 iPhone, iPad, Watch, Apple TV \u0438 Vision Pro \u043f\u043e\u0434\u0445\u0432\u0430\u0442\u044b\u0432\u0430\u044e\u0442 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u0435 \u0438 \u0432\u044b\u043f\u043e\u043b\u043d\u044f\u044e\u0442 \u0441\u0432\u043e\u044e \u043b\u043e\u043a\u0430\u043b\u044c\u043d\u0443\u044e \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0443. \u041d\u0438\u043a\u0430\u043a\u0438\u0445 \u043a\u043b\u044e\u0447\u0435\u0439, \u0442\u043e\u043a\u0435\u043d\u043e\u0432 \u0438 \u043d\u0430\u0441\u0442\u0440\u043e\u0435\u043a \u2014 \u043f\u0440\u043e\u0441\u0442\u043e \u0432\u043a\u043b\u044e\u0447\u0438\u0442\u0435 \u00ab\u0423\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u044f \u043c\u0435\u0436\u0434\u0443 \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0430\u043c\u0438\u00bb \u0432 \u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430\u0445 \u043d\u0430 \u043b\u044e\u0431\u043e\u043c \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0435. \u0411\u0435\u0437 Mac \u0432 \u0440\u043e\u043b\u0438 \u0446\u0435\u043d\u0442\u0440\u0430 \u043e\u043f\u043e\u0432\u0435\u0449\u0435\u043d\u0438\u044f \u0437\u0430\u0432\u0438\u0441\u044f\u0442 \u043e\u0442 \u0444\u043e\u043d\u043e\u0432\u043e\u0433\u043e \u0438\u0441\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u044f iOS \u0438 \u0431\u0443\u0434\u0443\u0442 \u0437\u0430\u0434\u0435\u0440\u0436\u0430\u043d\u044b \u0438\u043b\u0438 \u043f\u0440\u043e\u043f\u0443\u0449\u0435\u043d\u044b.</p>"),
            ("\u041d\u0443\u0436\u043d\u043e \u043b\u0438 \u043c\u043d\u0435 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 Mac \u0434\u043b\u044f \u043d\u0430\u0434\u0451\u0436\u043d\u044b\u0445 \u043e\u043f\u043e\u0432\u0435\u0449\u0435\u043d\u0438\u0439?",
             "\u0414\u0430 \u2014 \u043c\u044b \u043d\u0430\u0441\u0442\u043e\u044f\u0442\u0435\u043b\u044c\u043d\u043e \u0440\u0435\u043a\u043e\u043c\u0435\u043d\u0434\u0443\u0435\u043c. iOS \u043e\u0433\u0440\u0430\u043d\u0438\u0447\u0438\u0432\u0430\u0435\u0442 \u0444\u043e\u043d\u043e\u0432\u043e\u0435 \u0438\u0441\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u0435, \u043f\u043e\u044d\u0442\u043e\u043c\u0443 iPhone \u0438 iPad \u043c\u043e\u0433\u0443\u0442 \u043f\u0440\u043e\u0432\u0435\u0440\u044f\u0442\u044c \u0442\u043e\u043b\u044c\u043a\u043e \u043a\u0430\u0436\u0434\u044b\u0435 5\u201315 \u043c\u0438\u043d\u0443\u0442 (\u043d\u0430\u0441\u0442\u0440\u0430\u0438\u0432\u0430\u0435\u0442\u0441\u044f) \u0438 \u043c\u043e\u0433\u0443\u0442 \u043e\u0442\u043a\u043b\u0430\u0434\u044b\u0432\u0430\u0442\u044c \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0438 \u043f\u0440\u0438 \u043d\u0438\u0437\u043a\u043e\u043c \u0437\u0430\u0440\u044f\u0434\u0435, \u0440\u0435\u0436\u0438\u043c\u0435 \u044d\u043d\u0435\u0440\u0433\u043e\u0441\u0431\u0435\u0440\u0435\u0436\u0435\u043d\u0438\u044f \u0438\u043b\u0438 \u043f\u043b\u043e\u0445\u043e\u0439 \u0441\u0432\u044f\u0437\u0438. \u041f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 Mac \u043e\u043f\u0440\u0430\u0448\u0438\u0432\u0430\u0435\u0442 \u043d\u0435\u043f\u0440\u0435\u0440\u044b\u0432\u043d\u043e (\u0440\u0430\u0437 \u0432 60 \u0441\u0435\u043a\u0443\u043d\u0434 \u043f\u0440\u0438 \u043f\u043e\u0434\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u0438 \u043a \u043f\u0438\u0442\u0430\u043d\u0438\u044e) \u0438 \u0440\u0430\u0441\u0441\u044b\u043b\u0430\u0435\u0442 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f \u0441\u0442\u0430\u0442\u0443\u0441\u0430 \u043d\u0430 \u0434\u0440\u0443\u0433\u0438\u0435 \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0430 \u0447\u0435\u0440\u0435\u0437 iCloud. \u0411\u0435\u0437 Mac \u0441 Vultyr \u043e\u043f\u043e\u0432\u0435\u0449\u0435\u043d\u0438\u044f \u043d\u0430 iOS, watchOS \u0438 tvOS \u043f\u0440\u043e\u0434\u043e\u043b\u0436\u0430\u044e\u0442 \u0440\u0430\u0431\u043e\u0442\u0430\u0442\u044c, \u043d\u043e \u043c\u043e\u0433\u0443\u0442 \u0431\u044b\u0442\u044c \u0437\u043d\u0430\u0447\u0438\u0442\u0435\u043b\u044c\u043d\u043e \u0437\u0430\u0434\u0435\u0440\u0436\u0430\u043d\u044b \u0438\u043b\u0438 \u043f\u0440\u043e\u043f\u0443\u0449\u0435\u043d\u044b. \u0414\u043b\u044f \u043c\u043e\u043d\u0438\u0442\u043e\u0440\u0438\u043d\u0433\u0430 \u0432 \u0440\u0435\u0430\u043b\u044c\u043d\u043e\u043c \u0432\u0440\u0435\u043c\u0435\u043d\u0438 \u0434\u0435\u0440\u0436\u0438\u0442\u0435 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 Mac \u0437\u0430\u043f\u0443\u0449\u0435\u043d\u043d\u044b\u043c \u2014 \u043e\u043d\u043e \u043a\u043e\u043c\u043f\u0430\u043a\u0442\u043d\u043e \u0432 \u0441\u0442\u0440\u043e\u043a\u0435 \u043c\u0435\u043d\u044e \u0438 \u0438\u043c\u0435\u043d\u043d\u043e \u0442\u0430\u043a Vultyr \u0437\u0430\u0434\u0443\u043c\u0430\u043d \u043a \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u043d\u0438\u044e.",
             "<p>\u0414\u0430 \u2014 \u043c\u044b \u043d\u0430\u0441\u0442\u043e\u044f\u0442\u0435\u043b\u044c\u043d\u043e \u0440\u0435\u043a\u043e\u043c\u0435\u043d\u0434\u0443\u0435\u043c. iOS \u043e\u0433\u0440\u0430\u043d\u0438\u0447\u0438\u0432\u0430\u0435\u0442 \u0444\u043e\u043d\u043e\u0432\u043e\u0435 \u0438\u0441\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u0435, \u043f\u043e\u044d\u0442\u043e\u043c\u0443 iPhone \u0438 iPad \u043c\u043e\u0433\u0443\u0442 \u043f\u0440\u043e\u0432\u0435\u0440\u044f\u0442\u044c \u0442\u043e\u043b\u044c\u043a\u043e \u043a\u0430\u0436\u0434\u044b\u0435 5\u201315 \u043c\u0438\u043d\u0443\u0442 (\u043d\u0430\u0441\u0442\u0440\u0430\u0438\u0432\u0430\u0435\u0442\u0441\u044f) \u0438 \u043c\u043e\u0433\u0443\u0442 \u043e\u0442\u043a\u043b\u0430\u0434\u044b\u0432\u0430\u0442\u044c \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0438 \u043f\u0440\u0438 \u043d\u0438\u0437\u043a\u043e\u043c \u0437\u0430\u0440\u044f\u0434\u0435, \u0440\u0435\u0436\u0438\u043c\u0435 \u044d\u043d\u0435\u0440\u0433\u043e\u0441\u0431\u0435\u0440\u0435\u0436\u0435\u043d\u0438\u044f \u0438\u043b\u0438 \u043f\u043b\u043e\u0445\u043e\u0439 \u0441\u0432\u044f\u0437\u0438. \u041f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 Mac \u043e\u043f\u0440\u0430\u0448\u0438\u0432\u0430\u0435\u0442 \u043d\u0435\u043f\u0440\u0435\u0440\u044b\u0432\u043d\u043e (\u0440\u0430\u0437 \u0432 60 \u0441\u0435\u043a\u0443\u043d\u0434 \u043f\u0440\u0438 \u043f\u043e\u0434\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u0438 \u043a \u043f\u0438\u0442\u0430\u043d\u0438\u044e) \u0438 \u0440\u0430\u0441\u0441\u044b\u043b\u0430\u0435\u0442 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f \u0441\u0442\u0430\u0442\u0443\u0441\u0430 \u043d\u0430 \u0434\u0440\u0443\u0433\u0438\u0435 \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0430 \u0447\u0435\u0440\u0435\u0437 iCloud. \u0411\u0435\u0437 Mac \u0441 Vultyr \u043e\u043f\u043e\u0432\u0435\u0449\u0435\u043d\u0438\u044f \u043d\u0430 iOS, watchOS \u0438 tvOS \u043f\u0440\u043e\u0434\u043e\u043b\u0436\u0430\u044e\u0442 \u0440\u0430\u0431\u043e\u0442\u0430\u0442\u044c, \u043d\u043e \u043c\u043e\u0433\u0443\u0442 \u0431\u044b\u0442\u044c \u0437\u043d\u0430\u0447\u0438\u0442\u0435\u043b\u044c\u043d\u043e \u0437\u0430\u0434\u0435\u0440\u0436\u0430\u043d\u044b \u0438\u043b\u0438 \u043f\u0440\u043e\u043f\u0443\u0449\u0435\u043d\u044b. \u0414\u043b\u044f \u043c\u043e\u043d\u0438\u0442\u043e\u0440\u0438\u043d\u0433\u0430 \u0432 \u0440\u0435\u0430\u043b\u044c\u043d\u043e\u043c \u0432\u0440\u0435\u043c\u0435\u043d\u0438 \u0434\u0435\u0440\u0436\u0438\u0442\u0435 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 Mac \u0437\u0430\u043f\u0443\u0449\u0435\u043d\u043d\u044b\u043c \u2014 \u043e\u043d\u043e \u043a\u043e\u043c\u043f\u0430\u043a\u0442\u043d\u043e \u0432 \u0441\u0442\u0440\u043e\u043a\u0435 \u043c\u0435\u043d\u044e \u0438 \u0438\u043c\u0435\u043d\u043d\u043e \u0442\u0430\u043a Vultyr \u0437\u0430\u0434\u0443\u043c\u0430\u043d \u043a \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u043d\u0438\u044e.</p>"),
            ("Работает ли vultyr с Siri и Командами?",
             "Да. Встроенные App Intents позволяют сказать «Hey Siri, отключи GitHub на 2 часа», «проверь статус Stripe» или «покажи текущие проблемы», а те же действия можно добавить в приложение Команды. Есть и Focus Filter \u2014 режим «vultyr Focus» автоматически заглушает неважные сервисы.",
             "<p>Да. Встроенные App Intents позволяют сказать «Hey Siri, отключи GitHub на 2 часа», «проверь статус Stripe» или «покажи текущие проблемы», а те же действия можно добавить в приложение Команды. Есть и Focus Filter \u2014 режим «vultyr Focus» автоматически заглушает неважные сервисы.</p>"),
            ("Есть ли виджеты и Live Activities?",
             "На iOS \u2014 виджеты на экране «Домой» и экране блокировки (по одному сервису и сводка), плюс виджет в Пункте управления. Активные сбои закрепляются в Dynamic Island как Live Activities. На watchOS \u2014 осложнения для всех циферблатов с поддержкой Smart Stack: нужный сервис всплывает, когда что-то упало.",
             "<p>На iOS \u2014 виджеты на экране «Домой» и экране блокировки (по одному сервису и сводка), плюс виджет в Пункте управления. Активные сбои закрепляются в Dynamic Island как Live Activities. На watchOS \u2014 осложнения для всех циферблатов с поддержкой Smart Stack: нужный сервис всплывает, когда что-то упало.</p>"),
            ("\u0421\u043e\u0431\u0438\u0440\u0430\u0435\u0442 \u043b\u0438 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 vultyr \u043c\u043e\u0438 \u0434\u0430\u043d\u043d\u044b\u0435?",
             "\u041d\u0435\u0442. \u0423 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u044f \u043d\u0435\u0442 \u0430\u043a\u043a\u0430\u0443\u043d\u0442\u043e\u0432, \u0432\u0441\u0442\u0440\u043e\u0435\u043d\u043d\u043e\u0433\u043e \u0442\u0440\u0435\u043a\u0438\u043d\u0433\u0430 \u0438 \u0432\u0441\u0442\u0440\u043e\u0435\u043d\u043d\u043e\u0439 \u0430\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0438. \u0412\u0441\u0435 \u043e\u0442\u0441\u043b\u0435\u0436\u0438\u0432\u0430\u0435\u043c\u044b\u0435 \u0441\u0435\u0440\u0432\u0438\u0441\u044b \u043e\u0441\u0442\u0430\u044e\u0442\u0441\u044f \u043d\u0430 \u0432\u0430\u0448\u0435\u043c \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0435. \u0417\u0430\u043c\u0435\u0447\u0430\u043d\u0438\u0435: \u044d\u0442\u043e\u0442 \u0441\u0430\u0439\u0442 (vultyr.app) \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0435\u0442 Google Analytics \u0431\u0435\u0437 \u0444\u0430\u0439\u043b\u043e\u0432 cookie \u0434\u043b\u044f \u0430\u0433\u0440\u0435\u0433\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u044b\u0445 \u0441\u0447\u0451\u0442\u0447\u0438\u043a\u043e\u0432 \u043f\u043e\u0441\u0435\u0442\u0438\u0442\u0435\u043b\u0435\u0439 \u2014 \u043f\u043e\u0434\u0440\u043e\u0431\u043d\u0435\u0435 \u0432 \u041f\u043e\u043b\u0438\u0442\u0438\u043a\u0435 \u043a\u043e\u043d\u0444\u0438\u0434\u0435\u043d\u0446\u0438\u0430\u043b\u044c\u043d\u043e\u0441\u0442\u0438.",
             "<p>\u041d\u0435\u0442. \u0423 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u044f \u043d\u0435\u0442 \u0430\u043a\u043a\u0430\u0443\u043d\u0442\u043e\u0432, \u0432\u0441\u0442\u0440\u043e\u0435\u043d\u043d\u043e\u0433\u043e \u0442\u0440\u0435\u043a\u0438\u043d\u0433\u0430 \u0438 \u0432\u0441\u0442\u0440\u043e\u0435\u043d\u043d\u043e\u0439 \u0430\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0438. \u0412\u0441\u0435 \u043e\u0442\u0441\u043b\u0435\u0436\u0438\u0432\u0430\u0435\u043c\u044b\u0435 \u0441\u0435\u0440\u0432\u0438\u0441\u044b \u043e\u0441\u0442\u0430\u044e\u0442\u0441\u044f \u043d\u0430 \u0432\u0430\u0448\u0435\u043c \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0435. \u0417\u0430\u043c\u0435\u0447\u0430\u043d\u0438\u0435: \u044d\u0442\u043e\u0442 \u0441\u0430\u0439\u0442 (vultyr.app) \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0435\u0442 Google Analytics \u0431\u0435\u0437 \u0444\u0430\u0439\u043b\u043e\u0432 cookie \u0434\u043b\u044f \u0430\u0433\u0440\u0435\u0433\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u044b\u0445 \u0441\u0447\u0451\u0442\u0447\u0438\u043a\u043e\u0432 \u043f\u043e\u0441\u0435\u0442\u0438\u0442\u0435\u043b\u0435\u0439 \u2014 \u043f\u043e\u0434\u0440\u043e\u0431\u043d\u0435\u0435 \u0432 <a href=\"/ru/privacy.html\">\u041f\u043e\u043b\u0438\u0442\u0438\u043a\u0435 \u043a\u043e\u043d\u0444\u0438\u0434\u0435\u043d\u0446\u0438\u0430\u043b\u044c\u043d\u043e\u0441\u0442\u0438</a>.</p>"),
            ("\u041a\u0430\u043a \u0441\u0438\u043d\u0445\u0440\u043e\u043d\u0438\u0437\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u0441\u0435\u0440\u0432\u0438\u0441\u044b \u043c\u0435\u0436\u0434\u0443 \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0430\u043c\u0438?",
             "\u041e\u0442\u0441\u043b\u0435\u0436\u0438\u0432\u0430\u0435\u043c\u044b\u0435 \u0441\u0435\u0440\u0432\u0438\u0441\u044b \u0441\u0438\u043d\u0445\u0440\u043e\u043d\u0438\u0437\u0438\u0440\u0443\u044e\u0442\u0441\u044f \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438 \u0447\u0435\u0440\u0435\u0437 iCloud. \u0422\u0435\u043c\u044b \u0438 \u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u0442\u0430\u043a\u0436\u0435 \u0441\u0438\u043d\u0445\u0440\u043e\u043d\u0438\u0437\u0438\u0440\u0443\u044e\u0442\u0441\u044f \u043c\u0435\u0436\u0434\u0443 \u0432\u0441\u0435\u043c\u0438 \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0430\u043c\u0438 Apple \u0447\u0435\u0440\u0435\u0437 iCloud Key-Value Store.",
             "<p>\u041e\u0442\u0441\u043b\u0435\u0436\u0438\u0432\u0430\u0435\u043c\u044b\u0435 \u0441\u0435\u0440\u0432\u0438\u0441\u044b \u0441\u0438\u043d\u0445\u0440\u043e\u043d\u0438\u0437\u0438\u0440\u0443\u044e\u0442\u0441\u044f \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438 \u0447\u0435\u0440\u0435\u0437 iCloud. \u0422\u0435\u043c\u044b \u0438 \u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u0442\u0430\u043a\u0436\u0435 \u0441\u0438\u043d\u0445\u0440\u043e\u043d\u0438\u0437\u0438\u0440\u0443\u044e\u0442\u0441\u044f \u043c\u0435\u0436\u0434\u0443 \u0432\u0441\u0435\u043c\u0438 \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0430\u043c\u0438 Apple \u0447\u0435\u0440\u0435\u0437 iCloud Key-Value Store.</p>"),
            ("Какие есть темы оформления?",
             "12 тем: Standard, Terminal, Amber, Blue, Neon, Dracula, Nord, Solarized, Catppuccin, Fossil, Monolith и HAL. Standard и три ретро-темы (Terminal, Amber, Blue) включены. Fossil, Monolith, HAL и остальные открываются опциональными донатами через IAP ($0.99 / $4.99 / $9.99) \u2014 это же поддерживает разработку. Темы синхронизируются между всеми устройствами автоматически.",
             "<p>12 тем: Standard, Terminal, Amber, Blue, Neon, Dracula, Nord, Solarized, Catppuccin, Fossil, Monolith и HAL. Standard и три ретро-темы (Terminal, Amber, Blue) включены. Fossil, Monolith, HAL и остальные открываются опциональными донатами через IAP ($0.99 / $4.99 / $9.99) \u2014 это же поддерживает разработку. Темы синхронизируются между всеми устройствами автоматически.</p>"),
            ("Можно ли отключить уведомления о известном инциденте?",
             "Да. При просмотре сервиса с активным инцидентом вы можете отключить уведомления на заданный период, чтобы не получать повторные оповещения. Также можно отключить голосом \u2014 «Hey Siri, отключи GitHub на 2 часа» \u2014 или через приложение Команды.",
             "<p>Да. При просмотре сервиса с активным инцидентом вы можете отключить уведомления на заданный период, чтобы не получать повторные оповещения. Также можно отключить голосом \u2014 «Hey Siri, отключи GitHub на 2 часа» \u2014 или через приложение Команды.</p>"),
            ("Какие платформы поддерживаются?",
             "iPhone и iPad (с виджетами и Live Activities), Mac (с приложением в строке меню и полным окном), Apple Watch (с осложнениями и Smart Stack), Apple TV и Apple Vision Pro. Приложение можно скачать бесплатно на любой платформе.",
             "<p>iPhone и iPad (с виджетами и Live Activities), Mac (с приложением в строке меню и полным окном), Apple Watch (с осложнениями и Smart Stack), Apple TV и Apple Vision Pro. Приложение можно скачать бесплатно на любой платформе.</p>"),
            ("\u041c\u043e\u0436\u043d\u043e \u043b\u0438 \u0437\u0430\u043f\u0440\u043e\u0441\u0438\u0442\u044c \u0434\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u043d\u043e\u0432\u043e\u0433\u043e \u0441\u0435\u0440\u0432\u0438\u0441\u0430?",
             "\u0414\u0430! \u041d\u0430\u043f\u0438\u0448\u0438\u0442\u0435 \u043d\u0430 support@vultyr.app, \u0443\u043a\u0430\u0437\u0430\u0432 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0441\u0435\u0440\u0432\u0438\u0441\u0430 \u0438 URL \u0435\u0433\u043e \u0441\u0442\u0440\u0430\u043d\u0438\u0446\u044b \u0441\u0442\u0430\u0442\u0443\u0441\u0430.",
             "<p>\u0414\u0430! \u041d\u0430\u043f\u0438\u0448\u0438\u0442\u0435 \u043d\u0430 <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a>, \u0443\u043a\u0430\u0437\u0430\u0432 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0441\u0435\u0440\u0432\u0438\u0441\u0430 \u0438 URL \u0435\u0433\u043e \u0441\u0442\u0440\u0430\u043d\u0438\u0446\u044b \u0441\u0442\u0430\u0442\u0443\u0441\u0430.</p>"),
        ],
    },
    "da": {
    "html_lang": "da",
    "og_locale": "da_DK",
    "og_image_alt": "Vultyr app-ikon \u2014 overvågning af tjenestestatus",
    "devices": "iPhone, iPad, Mac, Apple Watch, Apple TV og Vision Pro",
    "skip_to_main": "Gå til hovedindhold",
    "topbar_brand_aria": "Vultyr forside",
    "nav_primary_aria": "Primær",
    "nav_services": "tjenester",
    "nav_support": "support",
    "nav_download": "Hent",
    "footer_nav_aria": "Sidefodsnavigation",
    "footer_home": "Forside",
    "footer_services": "Tjenester",
    "footer_privacy": "Privatliv",
    "footer_support": "Support",
    "footer_contact": "Kontakt",
    "copyright": "\u00a9 2026 Vultyr. Alle rettigheder forbeholdes.",
    "breadcrumb_aria": "Brødkrummer",
    "breadcrumb_vultyr": "Vultyr",
    "breadcrumb_services": "Tjenester",
    # services page
    "svcs_title": "Vultyr \u2014 200+ statustjek",
    "svcs_description": "200+ statustjek på tværs af cloud-tjenester, udviklerværktøjer, kommunikation, AI og meget mere \u2014 alt sammen overvåget af Vultyr.",
    "svcs_h1_lead": "Status",
    "svcs_h1_highlight": "tjek",
    "svcs_subtitle": "200+ statustjek som vultyr kører for cloud-tjenester, udviklerværktøjer og platforme.",
    "svcs_categories_aria": "Gennemse efter kategori",
    "svc_row_status": "Statusside",
    "svc_row_homepage": "Hjemmeside",
    "svcs_item_list_name": "Tjenester overvåget af Vultyr",
    # service page
    "svcp_title_fmt": "Er {name} nede? {name}-statusovervågning | Vultyr",
    "svcp_description_fmt": "Tjek om {name} er nede lige nu. Live {name}-statusopdateringer og nedbrudsovervågning med Vultyr. Gratis på {devices}.",
    "svcp_live_check": "Live-tjek",
    "svcp_view_current_status": "Se aktuel status \u2192",
    "svcp_alert_hint_prefix": "For øjeblikkelige underretninger, ",
    "svcp_alert_hint_link": "hent Vultyr",
    "svcp_categories_label": "Kategorier:",
    "svcp_official_status": "Officiel statusside",
    "svcp_homepage_fmt": "{name}-hjemmeside",
    "svcp_faq_heading": "Ofte stillede spørgsmål",
    "svcp_faq_q1_fmt": "Er {name} nede lige nu?",
    "svcp_faq_a1_fmt": "Se den officielle {name}-statusside linket ovenfor for aktuel status. For løbende overvågning med øjeblikkelige nedbrudsunderretninger på alle dine Apple-enheder kan du hente den gratis Vultyr-app.",
    "svcp_faq_a1_ld_fmt": "Se den officielle {name}-statusside på {url} for aktuel status. Hent den gratis Vultyr-app for øjeblikkelige nedbrudsunderretninger på alle dine Apple-enheder.",
    "svcp_faq_q2_fmt": "Hvordan kan jeg overvåge {name}-status?",
    "svcp_faq_a2_fmt": "Vultyr overvåger {name} som en del af 200+ statustjek på tværs af cloud-tjenester, udviklerværktøjer og platforme. Få øjeblikkelige nedbrudsunderretninger på {devices} \u2014 helt gratis.",
    "svcp_faq_a2_ld_fmt": "Hent Vultyr (gratis) for at overvåge {name} som en del af 200+ statustjek med realtidsunderretninger på {devices}. Vultyr kører hvert tjek automatisk og giver dig besked i det øjeblik, et nedbrud opdages.",
    "svcp_related_heading": "Relaterede tjenester",
    "svcp_related_aria": "Relaterede tjenester",
    "svcp_cta_heading_fmt": "Overvåg {name} på alle dine enheder",
    "svcp_cta_body_fmt": "Få øjeblikkelige underretninger, når {name} går ned. Gratis på alle Apple-platforme.",
    "cta_download_vultyr": "Hent Vultyr",
    "cta_download_vultyr_aria": "Hent Vultyr i App Store",
    # category page
    "catp_title_fmt": "{name}-statusovervågning \u2014 {count_services} | Vultyr",
    "catp_description_fmt": "Overvåg status for {count_services} i {name_lower}. Realtidsunderretninger om nedbrud for {sample} og flere.",
    "catp_item_list_name_fmt": "{name}-statusovervågning",
    "catp_subtitle_fmt": "{count_services} overvåget af Vultyr",
    "catp_services_aria_fmt": "{name}-tjenester",
    "catp_other_heading": "Andre kategorier",
    "catp_cta_heading_fmt": "Overvåg alle {count_services} med det samme",
    "catp_cta_body": "Få realtidsunderretninger om nedbrud på alle dine Apple-enheder. Gratis.",
    # home page
    "home_title": "Vultyr \u2014 statusovervågning for AWS, Slack, GitHub og flere",
    "home_description": "Er den nede? 200+ statustjek på tværs af cloud-tjenester, udviklerværktøjer og platforme med øjeblikkelige nedbrudsunderretninger. Gratis på iPhone, iPad, Mac, Apple Watch, Apple TV og Apple Vision Pro.",
    "home_og_title": "Vultyr \u2014 statusovervågning af tjenester",
    "home_app_ld_description": "Overvåg 200+ statustjek på tværs af cloud-tjenester, udviklerværktøjer og platforme med øjeblikkelige nedbrudsunderretninger.",
    "home_hero_tag": "200+ tjek",
    "home_hero_question": "Er den nede?",
    "home_hero_answer": "Vid det, før dine brugere gør.",
    "home_hero_services": "200+ statustjek \u2014 AWS, GitHub, Slack, Stripe &amp; flere \u2014 med øjeblikkelige nedbrudsunderretninger på alle Apple-enheder.",
    "home_appstore_alt": "Hent i App Store",
    "home_appstore_aria": "Hent Vultyr i App Store",
    "home_free_on_prefix": "Gratis på",
    "home_screenshots_aria": "App-skærmbilleder",
    "home_screenshot_dash_alt": "Vultyr-dashboard med status »Alt kører« og tjenester som AWS, GitHub og Slack under overvågning",
    "home_screenshot_settings_alt_fmt": "Vultyr udseende-indstillinger med {themes} temaer, herunder Terminal, Amber, Dracula og Nord",
    "home_screenshot_services_alt_fmt": "Vultyr tjenestebrowser med {categories} kategorier, herunder Cloud, Dev Tools og AI",
    "home_stats_aria": "Nøgletal",
    "home_stats_checks": "Tjek",
    "home_stats_categories": "Kategorier",
    "home_stats_platforms": "Platforme",
    "home_stats_languages": "Sprog",
    "home_features_heading": "Alt du har brug for, så du er på forkant med nedbrud",
    "home_features_sub": "Ingen app-konti, ingen sporing i appen. Bare status.",
    "home_bottom_heading": "Klar til at overvåge din stack?",
    "home_bottom_sub": "Gratis. Ingen app-konto nødvendig. Tilgængelig alle steder.",
    "home_bottom_button": "Hent gratis",
    "home_bottom_aria": "Hent Vultyr gratis i App Store",
    "home_languages_heading": "Tilgængelig på 17 sprog",
    "home_features": [
        ("chart-bar-regular.svg", "Live-statusdashboard",
         "AWS, GitHub, Cloudflare, Slack, Stripe, Discord, OpenAI, Anthropic og 200+ andre — alle ét sted. Statusindikatorerne synkroniseres med 120Hz ProMotion på iPhone Pro og iPad Pro."),
        ("bell-ringing-regular.svg", "Smarte underretninger",
         "Notifikationer om nedbrud og gendannelse med favicon for hver tjeneste på iOS. Store udfald pulserer markant større end mindre hændelser, så sværhedsgraden kan aflæses på et øjeblik. Slå kendte problemer fra, og marker kritiske tjenester med stjerne."),
        ("microphone-regular.svg", "Siri og Shortcuts",
         "Spørg Siri »sæt GitHub på lydløs i 2 timer« eller »vis aktuelle problemer«. App Intents for hver handling, plus et Focus-filter der dæmper ikke-kritiske tjenester."),
        ("squares-four-regular.svg", "Widgets og Live Activities",
         "Hjemmeskærms- og låseskærmswidgets på iOS, plus en Control Center-widget. Aktive nedbrud fastgøres i Dynamic Island."),
        ("watch-regular.svg", "Ur-komplikationer",
         "Fastgør en kritisk tjeneste på en urskive, eller lad Smart Stack automatisk vise aktive problemer."),
        ("cloud-check-regular.svg", "Mac-hub — iPhone som reserve",
         "Mac er den mest pålidelige hub: den poller så ofte som hvert 60. sekund (kan indstilles op til 15 min) og sender statusændringer til iPhone, iPad, Watch og Vision Pro via iCloud. Hvis ingen Mac er online, overtager din iPhone som reserveudgiver, så de andre enheder stadig får notifikationer."),
        ("monitor-regular.svg", "Visning af notifikationspålidelighed",
         "Se med ét blik, om notifikationer faktisk når frem — Mac-hjerteslag, status for baggrundsopdatering, CloudKit-push og hvornår hver enhed senest tjekkede."),
        ("devices-regular.svg", "Alle Apple-platforme",
         "iPhone, iPad, Mac-menubjælke, Apple TV, Apple Watch og Vision Pro. Tjenester synkroniseres på tværs af alle enheder."),
        ("lightning-regular.svg", "Hændelsesdetaljer",
         "Berørte komponenter, aktive hændelser, planlagt vedligeholdelse og tidslinjeopdateringer \u2014 oversat til dit sprog."),
        ("battery-charging-regular.svg", "Batterivenlig afstemning",
         "Smart auto-opdatering tilpasser sig batteri, strømtilstand og temperatur. Hvert minut på Mac, 5–15 minutter på iPhone, med baggrundsopdatering på iPad, Apple Watch, Vision Pro og Apple TV."),
        ("palette-regular.svg", f"{THEMES_COUNT} temaer",
         "Standard og tre retro-temaer er inkluderet. Fossil, Monolith, HAL og resten låses op via valgfri tip-jar-IAP'er."),
        ("shield-check-regular.svg", "App-data forbliver lokalt",
         "Appen har ingen tilmelding og ingen analytik i appen. Dine overvågede tjenester forbliver på din enhed."),
        ("translate-regular.svg", f"{APP_LANGUAGE_COUNT} app-sprog",
         "Engelsk, tysk, fransk, spansk, japansk, koreansk, kinesisk, portugisisk, russisk og flere."),
    ],
    # 404
    "err_title": "Siden blev ikke fundet \u2014 Vultyr",
    "err_description": "Siden du leder efter findes ikke.",
    "err_heading": "Siden blev ikke fundet",
    "err_message": "Siden du leder efter findes ikke eller er blevet flyttet.",
    "redirect_moved_fmt": "Denne side er flyttet. Omdirigerer til {name}…",
    "err_popular_heading": "Populære tjenester",
    "err_browse_heading": "Gennemse kategorier",
    # privacy
    "privacy_title": "Privatlivspolitik",
    "privacy_description": "Vultyrs privatlivspolitik. Appen indsamler ingen personlige data. Dette website bruger cookieløs Google Analytics til aggregeret besøgsstatistik.",
    "privacy_last_updated": "Sidst opdateret: 11. april 2026",
    "privacy_sections": [
        ("Resumé",
         "<p>Vultyr-<strong>appen</strong> indsamler, gemmer og sender ingen personlige data. Vultyr-<strong>websitet</strong> (vultyr.app) bruger cookieløs Google Analytics til at forstå aggregeret besøgstrafik. Denne side forklarer begge dele i detaljer.</p>"),
        ("App \u2014 dataindsamling",
         "<p>Vultyr-appen indsamler ingen personlige oplysninger. Den kræver ingen konto, indeholder ingen tredjepartsanalytik eller sporings-SDK'er og kontakter ingen server, som vi driver.</p>"),
        ("App \u2014 netværksanmodninger",
         "<p>Appen sender direkte HTTPS-anmodninger til offentlige statusside-API'er (f.eks. Statuspage.io, Apple, Google Cloud og andre) for at tjekke tjenestestatus. Disse anmodninger går direkte fra din enhed til tjenestens offentlige API \u2014 de passerer ikke gennem nogen server, vi driver.</p>"),
        ("App \u2014 datalagring",
         "<p>Alle data gemmes lokalt på din enhed ved hjælp af Apples SwiftData-framework. Hvis du aktiverer iCloud-synkronisering, synkroniseres din liste over overvågede tjenester via Apples iCloud Key-Value Store, som er underlagt Apples privatlivspolitik. Vi ser aldrig disse data.</p>"),
        ("App \u2014 underretninger på tværs af enheder",
         "<p>Hvis du aktiverer underretninger på tværs af enheder, deles statusændringer mellem dine enheder via Apples iCloud Key-Value Store. Når din Mac opdager en statusændring, skriver den et let signal til din iCloud-konto. Dine andre enheder bemærker ændringen og kører deres eget lokale tjek. Ingen tredjepartsserver er involveret \u2014 al kommunikation går gennem Apples iCloud-infrastruktur. Du kan slå dette til og fra fra enhver enhed.</p>"),
        ("App \u2014 favicons",
         "<p>Tjenesters favicons hentes fra Googles offentlige favicon-tjeneste og caches lokalt på din enhed.</p>"),
        ("Website \u2014 analytik",
         "<p>Dette website (vultyr.app) bruger Google Analytics 4 i cookieløs og IP-anonymiseret tilstand til at tælle aggregerede sidevisninger. Konkret konfigurerer vi gtag.js med <code>anonymize_ip: true</code>, <code>client_storage: 'none'</code>, <code>allow_google_signals: false</code> og <code>allow_ad_personalization_signals: false</code>. Det betyder, at der ikke sættes nogen <code>_ga</code>-cookie, din IP afkortes før lagring, og der indsamles ingen reklameidentifikatorer. Selve Vultyr-appen indeholder ingen analytik.</p>"),
        ("Website \u2014 tredjepartsdomæner",
         "<p>Indlæsning af vultyr.app kontakter følgende tredjepartsdomæner:</p>\n    <ul>\n        <li><strong>www.googletagmanager.com</strong> \u2014 indlæser gtag.js-scriptet</li>\n        <li><strong>www.google-analytics.com</strong> / <strong>*.analytics.google.com</strong> \u2014 modtager anonymiserede sidevisningssignaler</li>\n        <li><strong>www.google.com/g/collect</strong> \u2014 modtager de samme anonymiserede sidevisningssignaler (Google Analytics 4's reserve-indsamlingsendpoint)</li>\n    </ul>\n    <p>Vi indlæser ikke Google Fonts (Audiowide-skrifttypen er hostet på vultyr.app) og bruger ikke en tredjeparts favicon-tjeneste til websitets egne billeder.</p>"),
        ("App \u2014 tredjepartstjenester",
         "<p>Vultyr-appen integreres ikke med nogen tredjeparts analyse-, reklame- eller sporingstjenester. De eneste eksterne anmodninger går til offentlige status-API'er og Googles favicon-tjeneste.</p>"),
        ("Børns privatliv",
         "<p>Vultyr-appen indsamler ikke data fra nogen, inklusive børn under 13 år. Websitet logger kun anonymiserede, aggregerede besøgstal.</p>"),
        ("Ændringer",
         "<p>Hvis denne politik ændres, opdaterer vi datoen ovenfor.</p>"),
        ("Kontakt",
         "<p>Spørgsmål? Skriv til <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a></p>"),
    ],
    # support
    "support_title": "Support",
    "support_description": "Få hjælp til Vultyr, statusovervågningen for iPhone, iPad, Mac, Apple Watch, Apple TV og Apple Vision Pro. Ofte stillede spørgsmål, kontakt og fejlfinding.",
    "support_contact_heading": "Kontakt",
    "support_contact_html": "<p>Fejlrapporter, funktionsønsker eller spørgsmål:<br>\n    <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a></p>",
    "support_faq_heading": "Ofte stillede spørgsmål",
    "support_faqs": [
        ("Hvor ofte tjekker vultyr tjenestestatus?",
         "På Mac: så ofte som hvert 60. sekund, når enheden er tilsluttet strøm. På iPhone: hvert 5., 10. eller 15. minut (kan indstilles), med periodiske baggrundstjek, når forholdene tillader det. På Apple Watch: hvert 15. minut. På Apple TV: hvert 5. minut. Afstemningen tilpasser sig automatisk batteriniveau, strømtilstand og temperaturforhold.",
         "<p>På Mac: så ofte som hvert 60. sekund, når enheden er tilsluttet strøm. På iPhone: hvert 5., 10. eller 15. minut (kan indstilles), med periodiske baggrundstjek, når forholdene tillader det. På Apple Watch: hvert 15. minut. På Apple TV: hvert 5. minut. Afstemningen tilpasser sig automatisk batteriniveau, strømtilstand og temperaturforhold.</p>"),
        ("Hvordan fungerer underretninger på tværs af enheder?",
         "Mac-appen er centralen. Hold den kørende (i menubjælken eller som fuldt vindue), og den afstemmer så ofte som hvert 60. sekund (kan indstilles op til 15 min). Når en statusændring opdages, skriver den et let signal til iCloud Key-Value Store; din iPhone, iPad, Watch, Apple TV og Vision Pro opfanger ændringen og kører deres eget lokale tjek. Ingen nøgler, ingen tokens, ingen opsætning \u2014 slå blot »Underretninger på tværs af enheder« til i indstillingerne på en vilkårlig enhed. Uden en Mac som central er underretninger afhængige af iOS' baggrundsafvikling og vil blive forsinket eller gå tabt.",
         "<p>Mac-appen er centralen. Hold den kørende (i menubjælken eller som fuldt vindue), og den afstemmer så ofte som hvert 60. sekund (kan indstilles op til 15 min). Når en statusændring opdages, skriver den et let signal til iCloud Key-Value Store; din iPhone, iPad, Watch, Apple TV og Vision Pro opfanger ændringen og kører deres eget lokale tjek. Ingen nøgler, ingen tokens, ingen opsætning \u2014 slå blot »Underretninger på tværs af enheder« til i indstillingerne på en vilkårlig enhed. Uden en Mac som central er underretninger afhængige af iOS' baggrundsafvikling og vil blive forsinket eller gå tabt.</p>"),
        ("Har jeg brug for Mac-appen for at få pålidelige underretninger?",
         "Ja \u2014 vi anbefaler det kraftigt. iOS begrænser baggrundsafvikling, så iPhone og iPad kan kun tjekke hvert 5.-15. minut (kan indstilles) og kan udskyde yderligere ved lavt batteri, Low Power Mode eller dårlig forbindelse. Mac-appen afstemmer så ofte som hvert 60. sekund, når enheden er tilsluttet strøm (kan indstilles op til 15 min) og sender statusændringer til dine andre enheder via iCloud. Uden en Mac, der kører Vultyr, fungerer underretninger på iOS, watchOS og tvOS stadig, men de kan være væsentligt forsinkede eller gå tabt. For realtidsovervågning bør du holde Mac-appen kørende \u2014 den er minimal i menubjælken, og det er sådan, Vultyr er tænkt til at blive brugt.",
         "<p>Ja \u2014 vi anbefaler det kraftigt. iOS begrænser baggrundsafvikling, så iPhone og iPad kan kun tjekke hvert 5.-15. minut (kan indstilles) og kan udskyde yderligere ved lavt batteri, Low Power Mode eller dårlig forbindelse. Mac-appen afstemmer så ofte som hvert 60. sekund, når enheden er tilsluttet strøm (kan indstilles op til 15 min) og sender statusændringer til dine andre enheder via iCloud. Uden en Mac, der kører Vultyr, fungerer underretninger på iOS, watchOS og tvOS stadig, men de kan være væsentligt forsinkede eller gå tabt. For realtidsovervågning bør du holde Mac-appen kørende \u2014 den er minimal i menubjælken, og det er sådan, Vultyr er tænkt til at blive brugt.</p>"),
        ("Fungerer vultyr med Siri og Shortcuts?",
         "Ja. Indbyggede App Intents lader dig sige »Hey Siri, sæt GitHub på lydløs i 2 timer«, »tjek Stripe-status« eller »vis aktuelle problemer«, og du kan koble de samme handlinger ind i Shortcuts-appen. Der er også et Focus-filter, så en »vultyr Focus«-tilstand automatisk kan dæmpe ikke-kritiske tjenester.",
         "<p>Ja. Indbyggede App Intents lader dig sige »Hey Siri, sæt GitHub på lydløs i 2 timer«, »tjek Stripe-status« eller »vis aktuelle problemer«, og du kan koble de samme handlinger ind i Shortcuts-appen. Der er også et Focus-filter, så en »vultyr Focus«-tilstand automatisk kan dæmpe ikke-kritiske tjenester.</p>"),
        ("Er der widgets og Live Activities?",
         "På iOS er der hjemmeskærms- og låseskærmswidgets (enkelt tjeneste og statusoversigt) plus en Control Center-widget. Aktive nedbrud fastgøres i Dynamic Island som Live Activities. På watchOS er komplikationer tilgængelige for alle urskiver, med Smart Stack-relevans så den rigtige tjeneste dukker op, når noget er nede.",
         "<p>På iOS er der hjemmeskærms- og låseskærmswidgets (enkelt tjeneste og statusoversigt) plus en Control Center-widget. Aktive nedbrud fastgøres i Dynamic Island som Live Activities. På watchOS er komplikationer tilgængelige for alle urskiver, med Smart Stack-relevans så den rigtige tjeneste dukker op, når noget er nede.</p>"),
        ("Indsamler vultyr-appen mine data?",
         "Nej. Appen har ingen konti, ingen sporing i appen, ingen analytik i appen. Alle dine overvågede tjenester forbliver på din enhed. Bemærk: dette website (vultyr.app) bruger cookieløs Google Analytics til aggregerede besøgstal \u2014 se privatlivspolitikken for detaljer.",
         "<p>Nej. Appen har ingen konti, ingen sporing i appen, ingen analytik i appen. Alle dine overvågede tjenester forbliver på din enhed. Bemærk: dette website (vultyr.app) bruger cookieløs Google Analytics til aggregerede besøgstal \u2014 se <a href=\"/privacy.html\">privatlivspolitikken</a> for detaljer.</p>"),
        ("Hvordan synkroniserer jeg mine tjenester på tværs af enheder?",
         "Dine overvågede tjenester synkroniseres automatisk via iCloud. Temaer og indstillinger synkroniseres også på tværs af alle dine Apple-enheder via iCloud Key-Value Store.",
         "<p>Dine overvågede tjenester synkroniseres automatisk via iCloud. Temaer og indstillinger synkroniseres også på tværs af alle dine Apple-enheder via iCloud Key-Value Store.</p>"),
        ("Hvilke temaer er der?",
         "12 temaer: Standard, Terminal, Amber, Blue, Neon, Dracula, Nord, Solarized, Catppuccin, Fossil, Monolith og HAL. Standard og de tre retro-temaer (Terminal, Amber, Blue) er inkluderet. Fossil, Monolith, HAL og resten låses op via valgfri tip-jar-IAP'er ($0.99 / $4.99 / $9.99), som også hjælper med at finansiere udviklingen. Temaer synkroniseres automatisk på tværs af alle dine enheder.",
         "<p>12 temaer: Standard, Terminal, Amber, Blue, Neon, Dracula, Nord, Solarized, Catppuccin, Fossil, Monolith og HAL. Standard og de tre retro-temaer (Terminal, Amber, Blue) er inkluderet. Fossil, Monolith, HAL og resten låses op via valgfri tip-jar-IAP'er ($0.99 / $4.99 / $9.99), som også hjælper med at finansiere udviklingen. Temaer synkroniseres automatisk på tværs af alle dine enheder.</p>"),
        ("Kan jeg sætte underretninger på lydløs ved en kendt hændelse?",
         "Ja. Når du ser en tjeneste med en aktiv hændelse, kan du sætte underretninger på lydløs i en fastsat periode, så du ikke gentagne gange får besked om noget, du allerede er bekendt med. Du kan også gøre det med stemmen \u2014 »Hey Siri, sæt GitHub på lydløs i 2 timer« \u2014 eller via Shortcuts-appen.",
         "<p>Ja. Når du ser en tjeneste med en aktiv hændelse, kan du sætte underretninger på lydløs i en fastsat periode, så du ikke gentagne gange får besked om noget, du allerede er bekendt med. Du kan også gøre det med stemmen \u2014 »Hey Siri, sæt GitHub på lydløs i 2 timer« \u2014 eller via Shortcuts-appen.</p>"),
        ("Hvilke platforme understøttes?",
         "iPhone og iPad (med widgets og Live Activities), Mac (med en menubjælkeapp plus fuldt vindue), Apple Watch (med komplikationer og Smart Stack), Apple TV og Apple Vision Pro. Appen kan hentes gratis på alle platforme.",
         "<p>iPhone og iPad (med widgets og Live Activities), Mac (med en menubjælkeapp plus fuldt vindue), Apple Watch (med komplikationer og Smart Stack), Apple TV og Apple Vision Pro. Appen kan hentes gratis på alle platforme.</p>"),
        ("Kan jeg anmode om en ny tjeneste?",
         "Ja! Skriv til support@vultyr.app med tjenestens navn og URL'en til dens statusside.",
         "<p>Ja! Skriv til <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a> med tjenestens navn og URL'en til dens statusside.</p>"),
    ],
},
    "de": {
    "html_lang": "de",
    "og_locale": "de_DE",
    "og_image_alt": "Vultyr App-Icon \u2014 Service-Status-Monitor",
    "devices": "iPhone, iPad, Mac, Apple Watch, Apple TV und Vision Pro",
    "skip_to_main": "Zum Hauptinhalt springen",
    "topbar_brand_aria": "Vultyr Startseite",
    "nav_primary_aria": "Hauptnavigation",
    "nav_services": "Dienste",
    "nav_support": "Support",
    "nav_download": "Herunterladen",
    "footer_nav_aria": "Fußzeilen-Navigation",
    "footer_home": "Start",
    "footer_services": "Dienste",
    "footer_privacy": "Datenschutz",
    "footer_support": "Support",
    "footer_contact": "Kontakt",
    "copyright": "\u00a9 2026 Vultyr. Alle Rechte vorbehalten.",
    "breadcrumb_aria": "Brotkrumen-Navigation",
    "breadcrumb_vultyr": "Vultyr",
    "breadcrumb_services": "Dienste",
    # services page
    "svcs_title": "Vultyr \u2014 über 200 Status-Checks",
    "svcs_description": "Über 200 Status-Checks für Cloud-Dienste, Entwickler-Tools, Kommunikation, KI und mehr \u2014 alle von Vultyr überwacht.",
    "svcs_h1_lead": "Status-",
    "svcs_h1_highlight": "Checks",
    "svcs_subtitle": "Über 200 Status-Checks, die Vultyr für Cloud-Dienste, Entwickler-Tools und Plattformen durchführt.",
    "svcs_categories_aria": "Nach Kategorie durchsuchen",
    "svc_row_status": "Statusseite",
    "svc_row_homepage": "Website",
    "svcs_item_list_name": "Von Vultyr überwachte Dienste",
    # service page
    "svcp_title_fmt": "Ist {name} ausgefallen? {name} Status-Monitor | Vultyr",
    "svcp_description_fmt": "Prüfe, ob {name} gerade ausgefallen ist. Live-Status-Updates zu {name} und Ausfallüberwachung mit Vultyr. Kostenlos auf {devices}.",
    "svcp_live_check": "Live-Prüfung",
    "svcp_view_current_status": "Aktuellen Status ansehen \u2192",
    "svcp_alert_hint_prefix": "Für sofortige Benachrichtigungen ",
    "svcp_alert_hint_link": "Vultyr herunterladen",
    "svcp_categories_label": "Kategorien:",
    "svcp_official_status": "Offizielle Statusseite",
    "svcp_homepage_fmt": "{name} Website",
    "svcp_faq_heading": "FAQ",
    "svcp_faq_q1_fmt": "Ist {name} gerade ausgefallen?",
    "svcp_faq_a1_fmt": "Öffne die oben verlinkte offizielle {name}-Statusseite, um den aktuellen Status zu sehen. Für kontinuierliche Überwachung mit sofortigen Ausfallbenachrichtigungen auf allen deinen Apple-Geräten lade die kostenlose Vultyr-App herunter.",
    "svcp_faq_a1_ld_fmt": "Öffne die offizielle {name}-Statusseite unter {url}, um den aktuellen Status zu sehen. Lade die kostenlose Vultyr-App für sofortige Ausfallbenachrichtigungen auf allen deinen Apple-Geräten herunter.",
    "svcp_faq_q2_fmt": "Wie kann ich den Status von {name} überwachen?",
    "svcp_faq_a2_fmt": "Vultyr überwacht {name} als Teil von über 200 Status-Checks für Cloud-Dienste, Entwickler-Tools und Plattformen. Erhalte sofortige Ausfallbenachrichtigungen auf {devices} \u2014 völlig kostenlos.",
    "svcp_faq_a2_ld_fmt": "Lade Vultyr (kostenlos) herunter, um {name} als Teil von über 200 Status-Checks mit Echtzeit-Benachrichtigungen auf {devices} zu überwachen. Vultyr führt jede Prüfung automatisch aus und benachrichtigt dich in dem Moment, in dem ein Ausfall erkannt wird.",
    "svcp_related_heading": "Ähnliche Dienste",
    "svcp_related_aria": "Ähnliche Dienste",
    "svcp_cta_heading_fmt": "Überwache {name} auf allen deinen Geräten",
    "svcp_cta_body_fmt": "Erhalte sofortige Benachrichtigungen, wenn {name} ausfällt. Kostenlos auf allen Apple-Plattformen.",
    "cta_download_vultyr": "Vultyr herunterladen",
    "cta_download_vultyr_aria": "Vultyr im App Store herunterladen",
    # category page
    "catp_title_fmt": "{name} Status-Monitor \u2014 {count_services} | Vultyr",
    "catp_description_fmt": "Überwache den Status von {count_services} in {name_lower}. Echtzeit-Ausfallbenachrichtigungen für {sample} und weitere.",
    "catp_item_list_name_fmt": "{name} Status-Monitore",
    "catp_subtitle_fmt": "{count_services} von Vultyr überwacht",
    "catp_services_aria_fmt": "Dienste der Kategorie {name}",
    "catp_other_heading": "Weitere Kategorien",
    "catp_cta_heading_fmt": "Überwache alle {count_services} sofort",
    "catp_cta_body": "Erhalte Echtzeit-Ausfallbenachrichtigungen auf allen deinen Apple-Geräten. Kostenlos.",
    # home page
    "home_title": "Vultyr \u2014 Service-Status-Monitor für AWS, Slack, GitHub und mehr",
    "home_description": "Ist es ausgefallen? Über 200 Status-Checks für Cloud-Dienste, Entwickler-Tools und Plattformen mit sofortigen Ausfallbenachrichtigungen. Kostenlos auf iPhone, iPad, Mac, Apple Watch, Apple TV und Apple Vision Pro.",
    "home_og_title": "Vultyr \u2014 Service-Status-Monitor",
    "home_app_ld_description": "Überwache über 200 Status-Checks für Cloud-Dienste, Entwickler-Tools und Plattformen mit sofortigen Ausfallbenachrichtigungen.",
    "home_hero_tag": "200+ Checks",
    "home_hero_question": "Ist es ausgefallen?",
    "home_hero_answer": "Wisse es vor deinen Nutzern.",
    "home_hero_services": "Über 200 Status-Checks \u2014 AWS, GitHub, Slack, Stripe und mehr \u2014 mit sofortigen Ausfallbenachrichtigungen auf jedem Apple-Gerät.",
    "home_appstore_alt": "Im App Store laden",
    "home_appstore_aria": "Vultyr im App Store herunterladen",
    "home_free_on_prefix": "Kostenlos auf",
    "home_screenshots_aria": "App-Screenshots",
    "home_screenshot_dash_alt": "Vultyr-Dashboard mit Status \u201EAlles in Ordnung\u201C und überwachten Diensten wie AWS, GitHub und Slack",
    "home_screenshot_settings_alt_fmt": "Vultyr-Erscheinungseinstellungen mit {themes} Themes, darunter Terminal, Amber, Dracula und Nord",
    "home_screenshot_services_alt_fmt": "Vultyr-Service-Browser mit {categories} Kategorien, darunter Cloud, Dev Tools und AI",
    "home_stats_aria": "Kennzahlen",
    "home_stats_checks": "Checks",
    "home_stats_categories": "Kategorien",
    "home_stats_platforms": "Plattformen",
    "home_stats_languages": "Sprachen",
    "home_features_heading": "Alles, was du brauchst, um Ausfällen voraus zu sein",
    "home_features_sub": "Keine App-Konten, kein In-App-Tracking. Nur Status.",
    "home_bottom_heading": "Bereit, deinen Stack zu überwachen?",
    "home_bottom_sub": "Kostenlos. Kein App-Konto nötig. Überall verfügbar.",
    "home_bottom_button": "Kostenlos herunterladen",
    "home_bottom_aria": "Vultyr kostenlos im App Store herunterladen",
    "home_languages_heading": "Verfügbar in 17 Sprachen",
    "home_features": [
        ("chart-bar-regular.svg", "Live-Status-Dashboard",
         "AWS, GitHub, Cloudflare, Slack, Stripe, Discord, OpenAI, Anthropic und 200+ weitere — alles an einem Ort. Die Status-Orbs synchronisieren sich mit 120Hz ProMotion auf iPhone Pro und iPad Pro."),
        ("bell-ringing-regular.svg", "Intelligente Benachrichtigungen",
         "Ausfall- und Wiederherstellungsbenachrichtigungen mit dem Favicon jedes Dienstes unter iOS. Größere Ausfälle pulsieren merklich größer als kleinere Vorfälle, sodass der Schweregrad auf einen Blick erkennbar ist. Bekannte Probleme stummschalten, kritische Dienste markieren."),
        ("microphone-regular.svg",
         "Siri und Shortcuts",
         "Sage zu Siri \u201EGitHub für 2 Stunden stummschalten\u201C oder \u201Eaktuelle Probleme anzeigen\u201C. App Intents für jede Aktion, plus ein Focus-Filter, der unwichtige Dienste stummschaltet."),
        ("squares-four-regular.svg",
         "Widgets und Live Activities",
         "Home-Screen- und Sperrbildschirm-Widgets auf iOS, plus ein Control-Center-Widget. Aktive Ausfälle werden in der Dynamic Island angeheftet."),
        ("watch-regular.svg",
         "Watch-Komplikationen",
         "Hefte einen kritischen Dienst an ein Zifferblatt oder lass Smart Stack aktive Probleme automatisch einblenden."),
        ("cloud-check-regular.svg", "Mac-Hub — iPhone als Fallback",
         "Der Mac ist der zuverlässigste Hub: Er fragt bis zu alle 60 Sekunden ab (konfigurierbar bis 15 Min) und sendet Statusänderungen per iCloud an iPhone, iPad, Watch und Vision Pro. Wenn kein Mac online ist, übernimmt dein iPhone als Fallback-Publisher, damit die anderen Geräte weiterhin Benachrichtigungen erhalten."),
        ("monitor-regular.svg", "Ansicht der Benachrichtigungszuverlässigkeit",
         "Sieh auf einen Blick, ob Benachrichtigungen dich tatsächlich erreichen — Mac-Heartbeat, Status der Hintergrundaktualisierung, CloudKit-Push und wann jedes Gerät zuletzt geprüft hat."),
        ("devices-regular.svg",
         "Jede Apple-Plattform",
         "iPhone, iPad, Mac-Menüleiste, Apple TV, Apple Watch und Vision Pro. Dienste synchronisieren sich über alle Geräte."),
        ("lightning-regular.svg",
         "Vorfalldetails",
         "Betroffene Komponenten, aktive Vorfälle, geplante Wartungen und Timeline-Updates \u2014 in deiner Sprache lokalisiert."),
        ("battery-charging-regular.svg", "Akku-bewusstes Polling",
         "Die intelligente automatische Aktualisierung passt sich an Akku, Stromzustand und Temperatur an. Jede Minute auf Mac, 5–15 auf iPhone, mit Hintergrundaktualisierung auf iPad, Apple Watch, Vision Pro und Apple TV."),
        ("palette-regular.svg", f"{THEMES_COUNT} Themes",
         "Standard und drei Retro-Themes sind enthalten. Fossil, Monolith, HAL und die restlichen werden über optionale Trinkgeld-IAPs freigeschaltet."),
        ("shield-check-regular.svg",
         "App-Daten bleiben lokal",
         "Die App hat keine Registrierung und keine In-App-Analytik. Deine beobachteten Dienste bleiben auf deinem Gerät."),
        ("translate-regular.svg", f"{APP_LANGUAGE_COUNT} App-Sprachen",
         "Englisch, Deutsch, Französisch, Spanisch, Japanisch, Koreanisch, Chinesisch, Portugiesisch, Russisch und weitere."),
    ],
    # 404
    "err_title": "Seite nicht gefunden \u2014 Vultyr",
    "err_description": "Die gesuchte Seite existiert nicht.",
    "err_heading": "Seite nicht gefunden",
    "err_message": "Die Seite, die du suchst, existiert nicht oder wurde verschoben.",
    "redirect_moved_fmt": "Diese Seite wurde verschoben. Weiterleitung zu {name}…",
    "err_popular_heading": "Beliebte Dienste",
    "err_browse_heading": "Kategorien durchsuchen",
    # privacy
    "privacy_title": "Datenschutzerklärung",
    "privacy_description": "Datenschutzerklärung von Vultyr. Die App erfasst keine personenbezogenen Daten. Diese Website nutzt cookieloses Google Analytics für aggregierte Besucherstatistiken.",
    "privacy_last_updated": "Zuletzt aktualisiert: 11. April 2026",
    "privacy_sections": [
        ("Zusammenfassung",
         "<p>Die Vultyr-<strong>App</strong> erfasst, speichert und überträgt keinerlei personenbezogene Daten. Die Vultyr-<strong>Website</strong> (vultyr.app) nutzt cookieloses Google Analytics, um aggregierte Besucherstatistiken zu erfassen. Diese Seite erklärt beides im Detail.</p>"),
        ("App \u2014 Datenerfassung",
         "<p>Die Vultyr-App erfasst keinerlei personenbezogene Informationen. Sie erfordert kein Konto, enthält keine Analytik- oder Tracking-SDKs von Drittanbietern und sendet keine Daten an von uns betriebene Server.</p>"),
        ("App \u2014 Netzwerkanfragen",
         "<p>Die App stellt direkte HTTPS-Anfragen an öffentliche Statusseiten-APIs (etwa Statuspage.io, Apple, Google Cloud und andere), um den Dienststatus zu prüfen. Diese Anfragen gehen direkt von deinem Gerät an die öffentliche API des jeweiligen Dienstes \u2014 sie laufen nicht über einen von uns betriebenen Server.</p>"),
        ("App \u2014 Datenspeicherung",
         "<p>Alle Daten werden lokal auf deinem Gerät mit Apples SwiftData-Framework gespeichert. Wenn du die iCloud-Synchronisation aktivierst, wird deine Liste der beobachteten Dienste über Apples iCloud Key-Value Store synchronisiert, der den Datenschutzrichtlinien von Apple unterliegt. Wir sehen diese Daten nie.</p>"),
        ("App \u2014 Geräteübergreifende Benachrichtigungen",
         "<p>Wenn du geräteübergreifende Benachrichtigungen aktivierst, werden Statusänderungen zwischen deinen Geräten über Apples iCloud Key-Value Store geteilt. Wenn dein Mac eine Statusänderung erkennt, schreibt er ein leichtes Signal in dein iCloud-Konto. Deine anderen Geräte beobachten die Änderung und führen eine eigene lokale Prüfung durch. Kein Drittanbieter-Server ist beteiligt \u2014 die gesamte Kommunikation läuft über Apples iCloud-Infrastruktur. Du kannst dies von jedem Gerät aus umschalten.</p>"),
        ("App \u2014 Favicons",
         "<p>Service-Favicons werden über Googles öffentlichen Favicon-Dienst geladen und lokal auf deinem Gerät zwischengespeichert.</p>"),
        ("Website \u2014 Analytik",
         "<p>Diese Website (vultyr.app) nutzt Google Analytics 4 im cookielosen, IP-anonymisierten Modus zur Zählung aggregierter Seitenaufrufe. Konkret konfigurieren wir gtag.js mit <code>anonymize_ip: true</code>, <code>client_storage: 'none'</code>, <code>allow_google_signals: false</code> und <code>allow_ad_personalization_signals: false</code>. Das bedeutet: Es wird kein <code>_ga</code>-Cookie gesetzt, deine IP wird vor der Speicherung gekürzt und es werden keine Werbe-IDs erfasst. Die Vultyr-App selbst enthält keine Analytik.</p>"),
        ("Website \u2014 Drittanbieter-Domains",
         "<p>Beim Laden von vultyr.app werden folgende Drittanbieter-Domains kontaktiert:</p>\n    <ul>\n        <li><strong>www.googletagmanager.com</strong> \u2014 lädt das gtag.js-Skript</li>\n        <li><strong>www.google-analytics.com</strong> / <strong>*.analytics.google.com</strong> \u2014 empfängt anonymisierte Seitenaufruf-Beacons</li>\n        <li><strong>www.google.com/g/collect</strong> \u2014 empfängt dieselben anonymisierten Seitenaufruf-Beacons (Fallback-Endpoint für die Datenerfassung von Google Analytics 4)</li>\n    </ul>\n    <p>Wir laden keine Google Fonts (die Schriftart Audiowide wird selbst auf vultyr.app gehostet) und nutzen keinen Drittanbieter-Favicon-Dienst für die eigenen Bilder der Website.</p>"),
        ("App \u2014 Drittanbieter-Dienste",
         "<p>Die Vultyr-App ist nicht in Drittanbieter-Analytik-, Werbe- oder Tracking-Dienste eingebunden. Die einzigen externen Anfragen gehen an öffentliche Status-APIs und Googles Favicon-Dienst.</p>"),
        ("Datenschutz für Kinder",
         "<p>Die Vultyr-App erfasst von niemandem Daten, auch nicht von Kindern unter 13 Jahren. Die Website protokolliert nur anonymisierte, aggregierte Besucherzahlen.</p>"),
        ("Änderungen",
         "<p>Sollte sich diese Richtlinie ändern, aktualisieren wir das Datum oben.</p>"),
        ("Kontakt",
         "<p>Fragen? Schreib an <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a></p>"),
    ],
    # support
    "support_title": "Support",
    "support_description": "Hilfe zu Vultyr, dem Service-Status-Monitor für iPhone, iPad, Mac, Apple Watch, Apple TV und Apple Vision Pro. FAQs, Kontakt und Fehlerbehebung.",
    "support_contact_heading": "Kontakt",
    "support_contact_html": "<p>Für Fehlermeldungen, Feature-Wünsche oder Fragen:<br>\n    <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a></p>",
    "support_faq_heading": "FAQ",
    "support_faqs": [
        ("Wie oft prüft Vultyr den Dienststatus?",
         "Auf dem Mac: bis zu alle 60 Sekunden, wenn am Stromnetz. Auf dem iPhone: alle 5, 10 oder 15 Minuten (konfigurierbar), mit regelmäßigen Hintergrundprüfungen, sofern die Bedingungen es zulassen. Auf der Apple Watch: alle 15 Minuten. Auf dem Apple TV: alle 5 Minuten. Das Polling passt sich automatisch an Akkustand, Stromzustand und Temperatur an.",
         "<p>Auf dem Mac: bis zu alle 60 Sekunden, wenn am Stromnetz. Auf dem iPhone: alle 5, 10 oder 15 Minuten (konfigurierbar), mit regelmäßigen Hintergrundprüfungen, sofern die Bedingungen es zulassen. Auf der Apple Watch: alle 15 Minuten. Auf dem Apple TV: alle 5 Minuten. Das Polling passt sich automatisch an Akkustand, Stromzustand und Temperatur an.</p>"),
        ("Wie funktionieren geräteübergreifende Benachrichtigungen?",
         "Die Mac-App ist die Zentrale. Lass sie laufen (Menüleiste oder Vollfenster), dann fragt sie bis zu alle 60 Sekunden ab (konfigurierbar bis 15 Min). Wird eine Statusänderung erkannt, schreibt sie ein leichtes Signal in iCloud Key-Value Store; dein iPhone, iPad, Watch, Apple TV und Vision Pro greifen die Änderung auf und führen eine eigene lokale Prüfung durch. Keine Schlüssel, keine Tokens, keine Einrichtung \u2014 aktiviere einfach \u201EGeräteübergreifende Benachrichtigungen\u201C in den Einstellungen auf einem beliebigen Gerät. Ohne einen Mac als Zentrale hängen Benachrichtigungen von der iOS-Hintergrundausführung ab und werden verzögert oder verpasst.",
         "<p>Die Mac-App ist die Zentrale. Lass sie laufen (Menüleiste oder Vollfenster), dann fragt sie bis zu alle 60 Sekunden ab (konfigurierbar bis 15 Min). Wird eine Statusänderung erkannt, schreibt sie ein leichtes Signal in iCloud Key-Value Store; dein iPhone, iPad, Watch, Apple TV und Vision Pro greifen die Änderung auf und führen eine eigene lokale Prüfung durch. Keine Schlüssel, keine Tokens, keine Einrichtung \u2014 aktiviere einfach \u201EGeräteübergreifende Benachrichtigungen\u201C in den Einstellungen auf einem beliebigen Gerät. Ohne einen Mac als Zentrale hängen Benachrichtigungen von der iOS-Hintergrundausführung ab und werden verzögert oder verpasst.</p>"),
        ("Brauche ich die Mac-App für zuverlässige Benachrichtigungen?",
         "Ja \u2014 wir empfehlen sie dringend. iOS begrenzt die Hintergrundausführung, sodass iPhone und iPad nur alle 5 bis 15 Minuten prüfen können (konfigurierbar) und bei niedrigem Akku, Stromsparmodus oder schlechter Verbindung weiter verzögern können. Die Mac-App fragt bis zu alle 60 Sekunden am Stromnetz ab (konfigurierbar bis 15 Min) und sendet Statusänderungen per iCloud an deine anderen Geräte. Ohne einen Mac, der Vultyr ausführt, funktionieren Benachrichtigungen auf iOS, watchOS und tvOS zwar weiterhin, können aber deutlich verzögert oder verpasst werden. Für Echtzeit-Monitoring lass die Mac-App laufen \u2014 sie ist winzig in der Menüleiste und so ist Vultyr gedacht.",
         "<p>Ja \u2014 wir empfehlen sie dringend. iOS begrenzt die Hintergrundausführung, sodass iPhone und iPad nur alle 5 bis 15 Minuten prüfen können (konfigurierbar) und bei niedrigem Akku, Stromsparmodus oder schlechter Verbindung weiter verzögern können. Die Mac-App fragt bis zu alle 60 Sekunden am Stromnetz ab (konfigurierbar bis 15 Min) und sendet Statusänderungen per iCloud an deine anderen Geräte. Ohne einen Mac, der Vultyr ausführt, funktionieren Benachrichtigungen auf iOS, watchOS und tvOS zwar weiterhin, können aber deutlich verzögert oder verpasst werden. Für Echtzeit-Monitoring lass die Mac-App laufen \u2014 sie ist winzig in der Menüleiste und so ist Vultyr gedacht.</p>"),
        ("Funktioniert Vultyr mit Siri und Shortcuts?",
         "Ja. Eingebaute App Intents erlauben Befehle wie \u201EHey Siri, GitHub für 2 Stunden stummschalten\u201C, \u201EStripe-Status prüfen\u201C oder \u201Eaktuelle Probleme anzeigen\u201C, und dieselben Aktionen lassen sich in die Shortcuts-App einbinden. Es gibt außerdem einen Focus-Filter, damit ein \u201EVultyr-Focus\u201C unwichtige Dienste automatisch stummschaltet.",
         "<p>Ja. Eingebaute App Intents erlauben Befehle wie \u201EHey Siri, GitHub für 2 Stunden stummschalten\u201C, \u201EStripe-Status prüfen\u201C oder \u201Eaktuelle Probleme anzeigen\u201C, und dieselben Aktionen lassen sich in die Shortcuts-App einbinden. Es gibt außerdem einen Focus-Filter, damit ein \u201EVultyr-Focus\u201C unwichtige Dienste automatisch stummschaltet.</p>"),
        ("Gibt es Widgets und Live Activities?",
         "Auf iOS gibt es Home-Screen- und Sperrbildschirm-Widgets (einzelner Dienst und Status-Zusammenfassung) sowie ein Control-Center-Widget. Aktive Ausfälle werden als Live Activities in der Dynamic Island angeheftet. Auf watchOS stehen Komplikationen für alle Zifferblätter zur Verfügung, mit Smart-Stack-Relevanz, damit der richtige Dienst erscheint, wenn etwas ausfällt.",
         "<p>Auf iOS gibt es Home-Screen- und Sperrbildschirm-Widgets (einzelner Dienst und Status-Zusammenfassung) sowie ein Control-Center-Widget. Aktive Ausfälle werden als Live Activities in der Dynamic Island angeheftet. Auf watchOS stehen Komplikationen für alle Zifferblätter zur Verfügung, mit Smart-Stack-Relevanz, damit der richtige Dienst erscheint, wenn etwas ausfällt.</p>"),
        ("Erfasst die Vultyr-App meine Daten?",
         "Nein. Die App hat keine Konten, kein In-App-Tracking, keine In-App-Analytik. Alle deine beobachteten Dienste bleiben auf deinem Gerät. Hinweis: Diese Website (vultyr.app) nutzt cookieloses Google Analytics für aggregierte Besucherzahlen \u2014 Details in der Datenschutzerklärung.",
         "<p>Nein. Die App hat keine Konten, kein In-App-Tracking, keine In-App-Analytik. Alle deine beobachteten Dienste bleiben auf deinem Gerät. Hinweis: Diese Website (vultyr.app) nutzt cookieloses Google Analytics für aggregierte Besucherzahlen \u2014 Details in der <a href=\"/privacy.html\">Datenschutzerklärung</a>.</p>"),
        ("Wie synchronisiere ich meine Dienste zwischen Geräten?",
         "Deine beobachteten Dienste werden automatisch über iCloud synchronisiert. Themes und Einstellungen synchronisieren ebenfalls über iCloud Key-Value Store auf allen deinen Apple-Geräten.",
         "<p>Deine beobachteten Dienste werden automatisch über iCloud synchronisiert. Themes und Einstellungen synchronisieren ebenfalls über iCloud Key-Value Store auf allen deinen Apple-Geräten.</p>"),
        ("Welche Theme-Optionen gibt es?",
         "12 Themes: Standard, Terminal, Amber, Blue, Neon, Dracula, Nord, Solarized, Catppuccin, Fossil, Monolith und HAL. Standard und die drei Retro-Themes (Terminal, Amber, Blue) sind enthalten. Fossil, Monolith, HAL und die übrigen werden über optionale Trinkgeld-IAPs ($0.99 / $4.99 / $9.99) freigeschaltet, was auch die Entwicklung finanziert. Themes synchronisieren automatisch auf allen deinen Geräten.",
         "<p>12 Themes: Standard, Terminal, Amber, Blue, Neon, Dracula, Nord, Solarized, Catppuccin, Fossil, Monolith und HAL. Standard und die drei Retro-Themes (Terminal, Amber, Blue) sind enthalten. Fossil, Monolith, HAL und die übrigen werden über optionale Trinkgeld-IAPs ($0.99 / $4.99 / $9.99) freigeschaltet, was auch die Entwicklung finanziert. Themes synchronisieren automatisch auf allen deinen Geräten.</p>"),
        ("Kann ich Benachrichtigungen für einen bekannten Vorfall stummschalten?",
         "Ja. Beim Ansehen eines Dienstes mit aktivem Vorfall kannst du Benachrichtigungen für einen festgelegten Zeitraum stummschalten, damit du nicht wiederholt zu etwas benachrichtigt wirst, das du bereits kennst. Du kannst auch per Stimme stummschalten \u2014 \u201EHey Siri, GitHub für 2 Stunden stummschalten\u201C \u2014 oder über die Shortcuts-App.",
         "<p>Ja. Beim Ansehen eines Dienstes mit aktivem Vorfall kannst du Benachrichtigungen für einen festgelegten Zeitraum stummschalten, damit du nicht wiederholt zu etwas benachrichtigt wirst, das du bereits kennst. Du kannst auch per Stimme stummschalten \u2014 \u201EHey Siri, GitHub für 2 Stunden stummschalten\u201C \u2014 oder über die Shortcuts-App.</p>"),
        ("Welche Plattformen werden unterstützt?",
         "iPhone und iPad (mit Widgets und Live Activities), Mac (mit Menüleisten-App plus Vollfenster), Apple Watch (mit Komplikationen und Smart Stack), Apple TV und Apple Vision Pro. Die App ist auf jeder Plattform kostenlos zum Download verfügbar.",
         "<p>iPhone und iPad (mit Widgets und Live Activities), Mac (mit Menüleisten-App plus Vollfenster), Apple Watch (mit Komplikationen und Smart Stack), Apple TV und Apple Vision Pro. Die App ist auf jeder Plattform kostenlos zum Download verfügbar.</p>"),
        ("Kann ich einen neuen Dienst vorschlagen?",
         "Ja! Schreib an support@vultyr.app und gib den Namen des Dienstes und die URL seiner Statusseite an.",
         "<p>Ja! Schreib an <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a> und gib den Namen des Dienstes und die URL seiner Statusseite an.</p>"),
    ],
},
    "es": {
    "html_lang": "es",
    "og_locale": "es_ES",
    "og_image_alt": "Icono de la app Vultyr \u2014 monitor de estado de servicios",
    "devices": "iPhone, iPad, Mac, Apple Watch, Apple TV y Vision Pro",
    "skip_to_main": "Saltar al contenido principal",
    "topbar_brand_aria": "Inicio de Vultyr",
    "nav_primary_aria": "Principal",
    "nav_services": "servicios",
    "nav_support": "soporte",
    "nav_download": "Descargar",
    "footer_nav_aria": "Navegación del pie de página",
    "footer_home": "Inicio",
    "footer_services": "Servicios",
    "footer_privacy": "Privacidad",
    "footer_support": "Soporte",
    "footer_contact": "Contacto",
    "copyright": "\u00a9 2026 Vultyr. Todos los derechos reservados.",
    "breadcrumb_aria": "Ruta de navegación",
    "breadcrumb_vultyr": "Vultyr",
    "breadcrumb_services": "Servicios",
    # services page
    "svcs_title": "Vultyr \u2014 más de 200 comprobaciones de estado",
    "svcs_description": "Más de 200 comprobaciones de estado en servicios en la nube, herramientas para desarrolladores, comunicación, IA y más \u2014 todo monitoreado por Vultyr.",
    "svcs_h1_lead": "Comprobaciones",
    "svcs_h1_highlight": "de estado",
    "svcs_subtitle": "Más de 200 comprobaciones de estado que Vultyr ejecuta en servicios en la nube, herramientas para desarrolladores y plataformas.",
    "svcs_categories_aria": "Explorar por categoría",
    "svc_row_status": "Página de estado",
    "svc_row_homepage": "Sitio web",
    "svcs_item_list_name": "Servicios monitoreados por Vultyr",
    # service page
    "svcp_title_fmt": "¿{name} está caído? Monitor de estado de {name} | Vultyr",
    "svcp_description_fmt": "Comprueba si {name} está caído ahora mismo. Estado en tiempo real de {name} y monitoreo de caídas con Vultyr. Gratis en {devices}.",
    "svcp_live_check": "Comprobación en vivo",
    "svcp_view_current_status": "Ver estado actual \u2192",
    "svcp_alert_hint_prefix": "Para alertas instantáneas, ",
    "svcp_alert_hint_link": "descarga Vultyr",
    "svcp_categories_label": "Categorías:",
    "svcp_official_status": "Página de estado oficial",
    "svcp_homepage_fmt": "Sitio web de {name}",
    "svcp_faq_heading": "Preguntas frecuentes",
    "svcp_faq_q1_fmt": "¿{name} está caído ahora mismo?",
    "svcp_faq_a1_fmt": "Consulta la página de estado oficial de {name} enlazada arriba para ver el estado actual. Para un monitoreo continuo con alertas instantáneas de caídas en todos tus dispositivos Apple, descarga la app gratuita Vultyr.",
    "svcp_faq_a1_ld_fmt": "Consulta la página de estado oficial de {name} en {url} para ver el estado actual. Descarga la app gratuita Vultyr para recibir alertas instantáneas de caídas en todos tus dispositivos Apple.",
    "svcp_faq_q2_fmt": "¿Cómo puedo monitorear el estado de {name}?",
    "svcp_faq_a2_fmt": "Vultyr monitorea {name} como parte de más de 200 comprobaciones de estado en servicios en la nube, herramientas para desarrolladores y plataformas. Recibe alertas instantáneas de caídas en {devices} \u2014 completamente gratis.",
    "svcp_faq_a2_ld_fmt": "Descarga Vultyr (gratis) para monitorear {name} como parte de más de 200 comprobaciones de estado con alertas en tiempo real en {devices}. Vultyr ejecuta cada comprobación automáticamente y te avisa en el momento en que se detecta una caída.",
    "svcp_related_heading": "Servicios relacionados",
    "svcp_related_aria": "Servicios relacionados",
    "svcp_cta_heading_fmt": "Monitorea {name} en todos tus dispositivos",
    "svcp_cta_body_fmt": "Recibe alertas instantáneas cuando {name} se caiga. Gratis en todas las plataformas Apple.",
    "cta_download_vultyr": "Descargar Vultyr",
    "cta_download_vultyr_aria": "Descargar Vultyr en el App Store",
    # category page
    "catp_title_fmt": "Monitor de estado de {name} \u2014 {count_services} | Vultyr",
    "catp_description_fmt": "Monitorea el estado de {count_services} en {name_lower}. Alertas de caídas en tiempo real para {sample} y más.",
    "catp_item_list_name_fmt": "Monitores de estado de {name}",
    "catp_subtitle_fmt": "{count_services} monitoreados por Vultyr",
    "catp_services_aria_fmt": "Servicios de {name}",
    "catp_other_heading": "Otras categorías",
    "catp_cta_heading_fmt": "Monitorea {count_services} al instante",
    "catp_cta_body": "Recibe alertas de caídas en tiempo real en todos tus dispositivos Apple. Gratis.",
    # home page
    "home_title": "Vultyr \u2014 monitor de estado de servicios para AWS, Slack, GitHub y más",
    "home_description": "¿Está caído? Más de 200 comprobaciones de estado en servicios en la nube, herramientas para desarrolladores y plataformas con alertas instantáneas de caídas. Gratis en iPhone, iPad, Mac, Apple Watch, Apple TV y Apple Vision Pro.",
    "home_og_title": "Vultyr \u2014 monitor de estado de servicios",
    "home_app_ld_description": "Monitorea más de 200 comprobaciones de estado en servicios en la nube, herramientas para desarrolladores y plataformas con alertas instantáneas de caídas.",
    "home_hero_tag": "Más de 200 comprobaciones",
    "home_hero_question": "¿Está caído?",
    "home_hero_answer": "Entérate antes que tus usuarios.",
    "home_hero_services": "Más de 200 comprobaciones de estado \u2014 AWS, GitHub, Slack, Stripe y más \u2014 con alertas instantáneas de caídas en todos los dispositivos Apple.",
    "home_appstore_alt": "Descargar en el App Store",
    "home_appstore_aria": "Descargar Vultyr en el App Store",
    "home_free_on_prefix": "Gratis en",
    "home_screenshots_aria": "Capturas de pantalla de la app",
    "home_screenshot_dash_alt": "Panel de Vultyr mostrando el estado Todo Correcto con servicios como AWS, GitHub y Slack monitoreados",
    "home_screenshot_settings_alt_fmt": "Ajustes de apariencia de Vultyr con {themes} temas, incluidos Terminal, Amber, Dracula y Nord",
    "home_screenshot_services_alt_fmt": "Explorador de servicios de Vultyr mostrando {categories} categorías, incluidas Nube, Herramientas para desarrolladores e IA",
    "home_stats_aria": "Cifras clave",
    "home_stats_checks": "Comprobaciones",
    "home_stats_categories": "Categorías",
    "home_stats_platforms": "Plataformas",
    "home_stats_languages": "Idiomas",
    "home_features_heading": "Todo lo que necesitas para anticiparte a las caídas",
    "home_features_sub": "Sin cuentas de app, sin rastreo dentro de la app. Solo estado.",
    "home_bottom_heading": "¿Listo para monitorear tu stack?",
    "home_bottom_sub": "Gratis. Sin cuenta. Disponible en todas partes.",
    "home_bottom_button": "Descargar gratis",
    "home_bottom_aria": "Descargar Vultyr gratis en el App Store",
    "home_languages_heading": "Disponible en 17 idiomas",
    "home_features": [
        ("chart-bar-regular.svg", "Panel de estado en vivo",
         "AWS, GitHub, Cloudflare, Slack, Stripe, Discord, OpenAI, Anthropic y más de 200 — todo en un solo lugar. Los indicadores de estado se sincronizan con ProMotion de 120Hz en iPhone Pro y iPad Pro."),
        ("bell-ringing-regular.svg", "Alertas inteligentes",
         "Notificaciones de caída y recuperación con el favicon de cada servicio en iOS. Las interrupciones graves pulsan notablemente más grandes que los incidentes menores, para ver la gravedad de un vistazo. Silencia incidencias conocidas, marca servicios críticos."),
        ("microphone-regular.svg", "Siri y Shortcuts",
         "Dile a Siri \u201csilencia GitHub durante 2 horas\u201d o \u201cmuestra los problemas actuales\u201d. App Intents para cada acción, además de un Focus Filter que silencia los servicios no críticos."),
        ("squares-four-regular.svg", "Widgets y Live Activities",
         "Widgets de pantalla de inicio y pantalla de bloqueo en iOS, además de un widget en el Centro de control. Las caídas activas se fijan en la Dynamic Island."),
        ("watch-regular.svg", "Complicaciones para Watch",
         "Fija un servicio crítico en la esfera del reloj o deja que Smart Stack muestre los problemas activos automáticamente."),
        ("cloud-check-regular.svg", "Mac como hub — iPhone de respaldo",
         "El Mac es el hub más fiable: consulta tan a menudo como cada 60 segundos (configurable hasta 15 min) y difunde los cambios de estado al iPhone, iPad, Watch y Vision Pro mediante iCloud. Si ningún Mac está en línea, tu iPhone actúa como publicador de respaldo para que los demás dispositivos sigan recibiendo alertas."),
        ("monitor-regular.svg", "Vista de fiabilidad de alertas",
         "Consulta de un vistazo si las alertas te llegarán realmente — latido del Mac, estado de la actualización en segundo plano, envío por CloudKit y cuándo verificó cada dispositivo."),
        ("devices-regular.svg", "Todas las plataformas Apple",
         "iPhone, iPad, barra de menús del Mac, Apple TV, Apple Watch y Vision Pro. Los servicios se sincronizan entre todos los dispositivos."),
        ("lightning-regular.svg", "Detalles de incidentes",
         "Componentes afectados, incidentes activos, mantenimiento programado y actualizaciones de la cronología \u2014 localizados a tu idioma."),
        ("battery-charging-regular.svg", "Sondeo consciente de la batería",
         "La actualización automática se adapta a la batería, el estado de alimentación y la temperatura. Cada minuto en Mac, 5–15 en iPhone, con actualización en segundo plano en iPad, Apple Watch, Vision Pro y Apple TV."),
        ("palette-regular.svg", f"{THEMES_COUNT} temas",
         "Se incluyen Standard y tres temas retro. Fossil, Monolith, HAL y los demás se desbloquean con compras opcionales tipo propina dentro de la app."),
        ("shield-check-regular.svg", "Los datos de la app permanecen locales",
         "La app no requiere registro ni incluye analíticas dentro de ella. Los servicios que sigues se quedan en tu dispositivo."),
        ("translate-regular.svg", f"{APP_LANGUAGE_COUNT} idiomas en la app",
         "Inglés, alemán, francés, español, japonés, coreano, chino, portugués, ruso y más."),
    ],
    # 404
    "err_title": "Página no encontrada \u2014 Vultyr",
    "err_description": "La página que buscas no existe.",
    "err_heading": "Página no encontrada",
    "err_message": "La página que buscas no existe o ha sido movida.",
    "redirect_moved_fmt": "Esta página se ha movido. Redirigiendo a {name}…",
    "err_popular_heading": "Servicios populares",
    "err_browse_heading": "Explorar categorías",
    # privacy
    "privacy_title": "Política de privacidad",
    "privacy_description": "Política de privacidad de Vultyr. La app no recopila datos personales. Este sitio web usa Google Analytics sin cookies para tráfico agregado de visitantes.",
    "privacy_last_updated": "Última actualización: 11 de abril de 2026",
    "privacy_sections": [
        ("Resumen",
         "<p>La <strong>app</strong> Vultyr no recopila, almacena ni transmite datos personales. El <strong>sitio web</strong> Vultyr (vultyr.app) usa Google Analytics sin cookies para comprender el tráfico agregado de visitantes. Esta página explica ambos puntos en detalle.</p>"),
        ("App \u2014 recopilación de datos",
         "<p>La app vultyr no recopila ninguna información personal. No requiere una cuenta, no incluye SDK de análisis o seguimiento de terceros y no envía datos a ningún servidor operado por nosotros.</p>"),
        ("App \u2014 solicitudes de red",
         "<p>La app realiza solicitudes HTTPS directas a API públicas de páginas de estado (como Statuspage.io, Apple, Google Cloud y otras) para comprobar el estado de los servicios. Estas solicitudes van directamente desde tu dispositivo a la API pública del servicio \u2014 no pasan por ningún servidor operado por nosotros.</p>"),
        ("App \u2014 almacenamiento de datos",
         "<p>Todos los datos se almacenan localmente en tu dispositivo usando el framework SwiftData de Apple. Si activas la sincronización con iCloud, tu lista de servicios monitoreados se sincroniza mediante iCloud Key-Value Store de Apple, regido por la política de privacidad de Apple. Nosotros nunca vemos estos datos.</p>"),
        ("App \u2014 alertas entre dispositivos",
         "<p>Si activas las alertas entre dispositivos, los cambios de estado se comparten entre tus dispositivos mediante iCloud Key-Value Store de Apple. Cuando tu Mac detecta un cambio de estado, escribe una señal ligera en tu cuenta de iCloud. Tus otros dispositivos observan el cambio y ejecutan su propia comprobación local. No interviene ningún servidor de terceros \u2014 toda la comunicación pasa por la infraestructura iCloud de Apple. Puedes activar o desactivar esta función desde cualquier dispositivo.</p>"),
        ("App \u2014 favicons",
         "<p>Los favicons de los servicios se obtienen del servicio público de favicons de Google y se guardan en caché localmente en tu dispositivo.</p>"),
        ("Sitio web \u2014 analíticas",
         "<p>Este sitio web (vultyr.app) usa Google Analytics 4 en modo sin cookies y con IP anonimizada para contar vistas de página agregadas. Concretamente, configuramos gtag.js con <code>anonymize_ip: true</code>, <code>client_storage: 'none'</code>, <code>allow_google_signals: false</code> y <code>allow_ad_personalization_signals: false</code>. Esto significa que no se establece ninguna cookie <code>_ga</code>, tu IP se trunca antes de almacenarse y no se recopilan identificadores publicitarios. La propia app vultyr no incluye ningún tipo de analítica.</p>"),
        ("Sitio web \u2014 dominios de terceros",
         "<p>Al cargar vultyr.app se contactará con los siguientes dominios de terceros:</p>\n    <ul>\n        <li><strong>www.googletagmanager.com</strong> \u2014 carga el script gtag.js</li>\n        <li><strong>www.google-analytics.com</strong> / <strong>*.analytics.google.com</strong> \u2014 recibe beacons anonimizados de vistas de página</li>\n        <li><strong>www.google.com/g/collect</strong> \u2014 recibe los mismos beacons anonimizados de vistas de página (endpoint de recopilación de reserva de Google Analytics 4)</li>\n    </ul>\n    <p>No cargamos Google Fonts (la fuente Audiowide está autoalojada en vultyr.app) y no utilizamos un servicio de favicons de terceros para las imágenes propias del sitio web.</p>"),
        ("App \u2014 servicios de terceros",
         "<p>La app vultyr no se integra con ningún servicio de análisis, publicidad o seguimiento de terceros. Las únicas solicitudes externas son a API públicas de estado y al servicio de favicons de Google.</p>"),
        ("Privacidad de menores",
         "<p>La app vultyr no recopila datos de nadie, incluyendo menores de 13 años. El sitio web solo registra recuentos de visitantes anonimizados y agregados.</p>"),
        ("Cambios",
         "<p>Si esta política cambia, actualizaremos la fecha indicada arriba.</p>"),
        ("Contacto",
         "<p>¿Tienes preguntas? Escríbenos a <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a></p>"),
    ],
    # support
    "support_title": "Soporte",
    "support_description": "Obtén ayuda con Vultyr, el monitor de estado de servicios para iPhone, iPad, Mac, Apple Watch, Apple TV y Apple Vision Pro. Preguntas frecuentes, contacto y resolución de problemas.",
    "support_contact_heading": "Contacto",
    "support_contact_html": "<p>Para informes de errores, solicitudes de funciones o preguntas:<br>\n    <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a></p>",
    "support_faq_heading": "Preguntas frecuentes",
    "support_faqs": [
        ("¿Con qué frecuencia Vultyr comprueba el estado de los servicios?",
         "En Mac: tan a menudo como cada 60 segundos cuando está conectado a la corriente. En iPhone: cada 5, 10 o 15 minutos (configurable), con comprobaciones periódicas en segundo plano cuando las condiciones lo permitan. En Apple Watch: cada 15 minutos. En Apple TV: cada 5 minutos. El sondeo se adapta automáticamente al nivel de batería, al estado de alimentación y a las condiciones térmicas.",
         "<p>En Mac: tan a menudo como cada 60 segundos cuando está conectado a la corriente. En iPhone: cada 5, 10 o 15 minutos (configurable), con comprobaciones periódicas en segundo plano cuando las condiciones lo permitan. En Apple Watch: cada 15 minutos. En Apple TV: cada 5 minutos. El sondeo se adapta automáticamente al nivel de batería, al estado de alimentación y a las condiciones térmicas.</p>"),
        ("¿Cómo funcionan las alertas entre dispositivos?",
         "La app de Mac es el centro. Mantenla en ejecución (en la barra de menús o en ventana completa) y sondeará tan a menudo como cada 60 segundos (configurable hasta 15 min). Cuando detecta un cambio de estado, escribe una señal ligera en iCloud Key-Value Store; tu iPhone, iPad, Watch, Apple TV y Vision Pro captan el cambio y ejecutan su propia comprobación local. Sin claves, sin tokens, sin configuración \u2014 solo activa \u201cAlertas entre dispositivos\u201d en los ajustes desde cualquier dispositivo. Sin un Mac actuando como centro, las alertas dependen de la ejecución en segundo plano de iOS y se retrasarán o se perderán.",
         "<p>La app de Mac es el centro. Mantenla en ejecución (en la barra de menús o en ventana completa) y sondeará tan a menudo como cada 60 segundos (configurable hasta 15 min). Cuando detecta un cambio de estado, escribe una señal ligera en iCloud Key-Value Store; tu iPhone, iPad, Watch, Apple TV y Vision Pro captan el cambio y ejecutan su propia comprobación local. Sin claves, sin tokens, sin configuración \u2014 solo activa \u201cAlertas entre dispositivos\u201d en los ajustes desde cualquier dispositivo. Sin un Mac actuando como centro, las alertas dependen de la ejecución en segundo plano de iOS y se retrasarán o se perderán.</p>"),
        ("¿Necesito la app de Mac para alertas fiables?",
         "Sí \u2014 la recomendamos encarecidamente. iOS limita la ejecución en segundo plano, por lo que iPhone y iPad solo pueden comprobar cada 5-15 minutos (configurable) y pueden aplazarse aún más con batería baja, Modo de bajo consumo o conectividad deficiente. La app de Mac sondea tan a menudo como cada 60 segundos cuando está conectada a la corriente (configurable hasta 15 min) y difunde los cambios de estado a tus demás dispositivos mediante iCloud. Sin un Mac ejecutando Vultyr, las alertas en iOS, watchOS y tvOS siguen funcionando, pero pueden retrasarse o perderse notablemente. Para un monitoreo en tiempo real, mantén la app de Mac en ejecución \u2014 es minúscula en la barra de menús y es como se supone que hay que usar Vultyr.",
         "<p>Sí \u2014 la recomendamos encarecidamente. iOS limita la ejecución en segundo plano, por lo que iPhone y iPad solo pueden comprobar cada 5-15 minutos (configurable) y pueden aplazarse aún más con batería baja, Modo de bajo consumo o conectividad deficiente. La app de Mac sondea tan a menudo como cada 60 segundos cuando está conectada a la corriente (configurable hasta 15 min) y difunde los cambios de estado a tus demás dispositivos mediante iCloud. Sin un Mac ejecutando Vultyr, las alertas en iOS, watchOS y tvOS siguen funcionando, pero pueden retrasarse o perderse notablemente. Para un monitoreo en tiempo real, mantén la app de Mac en ejecución \u2014 es minúscula en la barra de menús y es como se supone que hay que usar Vultyr.</p>"),
        ("¿Vultyr funciona con Siri y Shortcuts?",
         "Sí. Los App Intents integrados te permiten decir \u201cOye Siri, silencia GitHub durante 2 horas\u201d, \u201ccomprueba el estado de Stripe\u201d o \u201cmuestra los problemas actuales\u201d, y puedes conectar esas mismas acciones a la app Shortcuts. También hay un Focus Filter para que un modo \u201cvultyr Focus\u201d silencie automáticamente los servicios no críticos.",
         "<p>Sí. Los App Intents integrados te permiten decir \u201cOye Siri, silencia GitHub durante 2 horas\u201d, \u201ccomprueba el estado de Stripe\u201d o \u201cmuestra los problemas actuales\u201d, y puedes conectar esas mismas acciones a la app Shortcuts. También hay un Focus Filter para que un modo \u201cvultyr Focus\u201d silencie automáticamente los servicios no críticos.</p>"),
        ("¿Hay widgets y Live Activities?",
         "En iOS hay widgets de pantalla de inicio y pantalla de bloqueo (de un solo servicio y de resumen de estado), además de un widget en el Centro de control. Las caídas activas se fijan en la Dynamic Island como Live Activities. En watchOS hay complicaciones disponibles para todas las esferas de reloj, con relevancia en Smart Stack para que el servicio adecuado aparezca cuando algo está caído.",
         "<p>En iOS hay widgets de pantalla de inicio y pantalla de bloqueo (de un solo servicio y de resumen de estado), además de un widget en el Centro de control. Las caídas activas se fijan en la Dynamic Island como Live Activities. En watchOS hay complicaciones disponibles para todas las esferas de reloj, con relevancia en Smart Stack para que el servicio adecuado aparezca cuando algo está caído.</p>"),
        ("¿La app vultyr recopila mis datos?",
         "No. La app no tiene cuentas, ni seguimiento dentro de la app, ni analíticas dentro de la app. Todos los servicios que sigues se quedan en tu dispositivo. Nota: este sitio web (vultyr.app) usa Google Analytics sin cookies para recuentos agregados de visitantes \u2014 consulta la Política de privacidad para más detalles.",
         "<p>No. La app no tiene cuentas, ni seguimiento dentro de la app, ni analíticas dentro de la app. Todos los servicios que sigues se quedan en tu dispositivo. Nota: este sitio web (vultyr.app) usa Google Analytics sin cookies para recuentos agregados de visitantes \u2014 consulta la <a href=\"/es/privacy.html\">Política de privacidad</a> para más detalles.</p>"),
        ("¿Cómo sincronizo mis servicios entre dispositivos?",
         "Los servicios que sigues se sincronizan automáticamente mediante iCloud. Los temas y los ajustes también se sincronizan entre todos tus dispositivos Apple mediante iCloud Key-Value Store.",
         "<p>Los servicios que sigues se sincronizan automáticamente mediante iCloud. Los temas y los ajustes también se sincronizan entre todos tus dispositivos Apple mediante iCloud Key-Value Store.</p>"),
        ("¿Qué opciones de temas hay?",
         "12 temas: Standard, Terminal, Amber, Blue, Neon, Dracula, Nord, Solarized, Catppuccin, Fossil, Monolith y HAL. Standard y los tres temas retro (Terminal, Amber, Blue) están incluidos. Fossil, Monolith, HAL y los demás se desbloquean mediante compras opcionales tipo propina ($0.99 / $4.99 / $9.99), que también ayudan a financiar el desarrollo. Los temas se sincronizan entre todos tus dispositivos automáticamente.",
         "<p>12 temas: Standard, Terminal, Amber, Blue, Neon, Dracula, Nord, Solarized, Catppuccin, Fossil, Monolith y HAL. Standard y los tres temas retro (Terminal, Amber, Blue) están incluidos. Fossil, Monolith, HAL y los demás se desbloquean mediante compras opcionales tipo propina ($0.99 / $4.99 / $9.99), que también ayudan a financiar el desarrollo. Los temas se sincronizan entre todos tus dispositivos automáticamente.</p>"),
        ("¿Puedo silenciar las notificaciones de un incidente conocido?",
         "Sí. Al ver un servicio con un incidente activo, puedes silenciar las notificaciones durante un periodo determinado para no recibir alertas repetidas sobre algo que ya conoces. También puedes silenciar por voz \u2014 \u201cOye Siri, silencia GitHub durante 2 horas\u201d \u2014 o desde la app Shortcuts.",
         "<p>Sí. Al ver un servicio con un incidente activo, puedes silenciar las notificaciones durante un periodo determinado para no recibir alertas repetidas sobre algo que ya conoces. También puedes silenciar por voz \u2014 \u201cOye Siri, silencia GitHub durante 2 horas\u201d \u2014 o desde la app Shortcuts.</p>"),
        ("¿Qué plataformas son compatibles?",
         "iPhone y iPad (con widgets y Live Activities), Mac (con app en la barra de menús y ventana completa), Apple Watch (con complicaciones y Smart Stack), Apple TV y Apple Vision Pro. La app se puede descargar gratis en todas las plataformas.",
         "<p>iPhone y iPad (con widgets y Live Activities), Mac (con app en la barra de menús y ventana completa), Apple Watch (con complicaciones y Smart Stack), Apple TV y Apple Vision Pro. La app se puede descargar gratis en todas las plataformas.</p>"),
        ("¿Puedo solicitar un nuevo servicio?",
         "¡Sí! Escribe a support@vultyr.app con el nombre del servicio y la URL de su página de estado.",
         "<p>¡Sí! Escribe a <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a> con el nombre del servicio y la URL de su página de estado.</p>"),
    ],
},
    "fr": {
    "html_lang": "fr",
    "og_locale": "fr_FR",
    "og_image_alt": "Ic\u00f4ne de l\u2019application Vultyr \u2014 moniteur d\u2019\u00e9tat des services",
    "devices": "iPhone, iPad, Mac, Apple Watch, Apple TV et Vision Pro",
    "skip_to_main": "Aller au contenu principal",
    "topbar_brand_aria": "Accueil Vultyr",
    "nav_primary_aria": "Principale",
    "nav_services": "services",
    "nav_support": "assistance",
    "nav_download": "T\u00e9l\u00e9charger",
    "footer_nav_aria": "Navigation du pied de page",
    "footer_home": "Accueil",
    "footer_services": "Services",
    "footer_privacy": "Confidentialit\u00e9",
    "footer_support": "Assistance",
    "footer_contact": "Contact",
    "copyright": "\u00a9 2026 Vultyr. Tous droits r\u00e9serv\u00e9s.",
    "breadcrumb_aria": "Fil d\u2019Ariane",
    "breadcrumb_vultyr": "Vultyr",
    "breadcrumb_services": "Services",
    # services page
    "svcs_title": "Vultyr \u2014 plus de 200 v\u00e9rifications d\u2019\u00e9tat",
    "svcs_description": "Plus de 200 v\u00e9rifications d\u2019\u00e9tat sur les services cloud, les outils de d\u00e9veloppement, la communication, l\u2019IA et plus encore \u2014 toutes surveill\u00e9es par Vultyr.",
    "svcs_h1_lead": "V\u00e9rifications",
    "svcs_h1_highlight": "d\u2019\u00e9tat",
    "svcs_subtitle": "Plus de 200 v\u00e9rifications d\u2019\u00e9tat que vultyr ex\u00e9cute sur les services cloud, les outils de d\u00e9veloppement et les plateformes.",
    "svcs_categories_aria": "Parcourir par cat\u00e9gorie",
    "svc_row_status": "Page d\u2019\u00e9tat",
    "svc_row_homepage": "Site officiel",
    "svcs_item_list_name": "Services surveill\u00e9s par Vultyr",
    # service page
    "svcp_title_fmt": "{name} est-il en panne\u00a0? Moniteur d\u2019\u00e9tat de {name} | Vultyr",
    "svcp_description_fmt": "V\u00e9rifiez si {name} est en panne en ce moment. Suivi en direct de l\u2019\u00e9tat de {name} et surveillance des pannes avec Vultyr. Gratuit sur {devices}.",
    "svcp_live_check": "V\u00e9rification en direct",
    "svcp_view_current_status": "Voir l\u2019\u00e9tat actuel \u2192",
    "svcp_alert_hint_prefix": "Pour des alertes instantan\u00e9es, ",
    "svcp_alert_hint_link": "t\u00e9l\u00e9chargez Vultyr",
    "svcp_categories_label": "Cat\u00e9gories\u00a0:",
    "svcp_official_status": "Page d\u2019\u00e9tat officielle",
    "svcp_homepage_fmt": "Site de {name}",
    "svcp_faq_heading": "FAQ",
    "svcp_faq_q1_fmt": "{name} est-il en panne en ce moment\u00a0?",
    "svcp_faq_a1_fmt": "Consultez la page d\u2019\u00e9tat officielle de {name} li\u00e9e ci-dessus pour conna\u00eetre l\u2019\u00e9tat actuel. Pour une surveillance continue avec des alertes de panne instantan\u00e9es sur tous vos appareils Apple, t\u00e9l\u00e9chargez l\u2019application gratuite Vultyr.",
    "svcp_faq_a1_ld_fmt": "Consultez la page d\u2019\u00e9tat officielle de {name} \u00e0 l\u2019adresse {url} pour conna\u00eetre l\u2019\u00e9tat actuel. T\u00e9l\u00e9chargez l\u2019application gratuite Vultyr pour recevoir des alertes de panne instantan\u00e9es sur tous vos appareils Apple.",
    "svcp_faq_q2_fmt": "Comment surveiller l\u2019\u00e9tat de {name}\u00a0?",
    "svcp_faq_a2_fmt": "Vultyr surveille {name} parmi plus de 200 v\u00e9rifications d\u2019\u00e9tat couvrant les services cloud, les outils de d\u00e9veloppement et les plateformes. Recevez des alertes de panne instantan\u00e9es sur {devices} \u2014 enti\u00e8rement gratuit.",
    "svcp_faq_a2_ld_fmt": "T\u00e9l\u00e9chargez Vultyr (gratuit) pour surveiller {name} parmi plus de 200 v\u00e9rifications d\u2019\u00e9tat avec des alertes en temps r\u00e9el sur {devices}. Vultyr ex\u00e9cute chaque v\u00e9rification automatiquement et vous avertit d\u00e8s qu\u2019une panne est d\u00e9tect\u00e9e.",
    "svcp_related_heading": "Services connexes",
    "svcp_related_aria": "Services connexes",
    "svcp_cta_heading_fmt": "Surveillez {name} sur tous vos appareils",
    "svcp_cta_body_fmt": "Recevez des alertes instantan\u00e9es lorsque {name} tombe en panne. Gratuit sur toutes les plateformes Apple.",
    "cta_download_vultyr": "T\u00e9l\u00e9charger Vultyr",
    "cta_download_vultyr_aria": "T\u00e9l\u00e9charger Vultyr sur l\u2019App Store",
    # category page
    "catp_title_fmt": "Moniteur d\u2019\u00e9tat \u00ab\u00a0{name}\u00a0\u00bb \u2014 {count_services} | Vultyr",
    "catp_description_fmt": "Surveillez l\u2019\u00e9tat de {count_services} dans la cat\u00e9gorie \u00ab\u00a0{name_lower}\u00a0\u00bb. Alertes de panne en temps r\u00e9el pour {sample}, et bien d\u2019autres.",
    "catp_item_list_name_fmt": "Moniteurs d\u2019\u00e9tat\u00a0: {name}",
    "catp_subtitle_fmt": "{count_services} surveill\u00e9s par Vultyr",
    "catp_services_aria_fmt": "Services de la cat\u00e9gorie {name}",
    "catp_other_heading": "Autres cat\u00e9gories",
    "catp_cta_heading_fmt": "Surveillez les {count_services} instantan\u00e9ment",
    "catp_cta_body": "Recevez des alertes de panne en temps r\u00e9el sur tous vos appareils Apple. Gratuit.",
    # home page
    "home_title": "Vultyr \u2014 moniteur d\u2019\u00e9tat pour AWS, Slack, GitHub et plus",
    "home_description": "En panne\u00a0? Plus de 200 v\u00e9rifications d\u2019\u00e9tat sur les services cloud, les outils de d\u00e9veloppement et les plateformes avec des alertes de panne instantan\u00e9es. Gratuit sur iPhone, iPad, Mac, Apple Watch, Apple TV et Apple Vision Pro.",
    "home_og_title": "Vultyr \u2014 moniteur d\u2019\u00e9tat des services",
    "home_app_ld_description": "Surveillez plus de 200 v\u00e9rifications d\u2019\u00e9tat sur les services cloud, les outils de d\u00e9veloppement et les plateformes avec des alertes de panne instantan\u00e9es.",
    "home_hero_tag": "200+ v\u00e9rifications",
    "home_hero_question": "En panne\u00a0?",
    "home_hero_answer": "Sachez-le avant vos utilisateurs.",
    "home_hero_services": "Plus de 200 v\u00e9rifications d\u2019\u00e9tat \u2014 AWS, GitHub, Slack, Stripe &amp; bien d\u2019autres \u2014 avec des alertes de panne instantan\u00e9es sur chaque appareil Apple.",
    "home_appstore_alt": "T\u00e9l\u00e9charger sur l\u2019App Store",
    "home_appstore_aria": "T\u00e9l\u00e9charger Vultyr sur l\u2019App Store",
    "home_free_on_prefix": "Gratuit sur",
    "home_screenshots_aria": "Captures d\u2019\u00e9cran de l\u2019application",
    "home_screenshot_dash_alt": "Tableau de bord Vultyr affichant l\u2019\u00e9tat \u00ab\u00a0Tout va bien\u00a0\u00bb avec des services comme AWS, GitHub et Slack sous surveillance",
    "home_screenshot_settings_alt_fmt": "Param\u00e8tres d\u2019apparence de Vultyr avec {themes} th\u00e8mes, dont Terminal, Amber, Dracula et Nord",
    "home_screenshot_services_alt_fmt": "Navigateur de services Vultyr affichant {categories} cat\u00e9gories, dont Cloud, Dev Tools et AI",
    "home_stats_aria": "Chiffres cl\u00e9s",
    "home_stats_checks": "V\u00e9rifications",
    "home_stats_categories": "Cat\u00e9gories",
    "home_stats_platforms": "Plateformes",
    "home_stats_languages": "Langues",
    "home_features_heading": "Tout ce qu\u2019il vous faut pour anticiper les pannes",
    "home_features_sub": "Aucun compte dans l\u2019app, aucun suivi int\u00e9gr\u00e9. Juste l\u2019\u00e9tat.",
    "home_bottom_heading": "Pr\u00eat \u00e0 surveiller votre stack\u00a0?",
    "home_bottom_sub": "Gratuit. Aucun compte requis. Disponible partout.",
    "home_bottom_button": "T\u00e9l\u00e9charger gratuitement",
    "home_bottom_aria": "T\u00e9l\u00e9charger Vultyr gratuitement sur l\u2019App Store",
    "home_languages_heading": "Disponible en 17 langues",
    "home_features": [
        ("chart-bar-regular.svg", "Tableau de bord d’état en direct",
         "AWS, GitHub, Cloudflare, Slack, Stripe, Discord, OpenAI, Anthropic et plus de 200 autres — tout au même endroit. Les orbes de statut se synchronisent avec ProMotion 120Hz sur iPhone Pro et iPad Pro."),
        ("bell-ringing-regular.svg", "Alertes intelligentes",
         "Notifications de panne et de rétablissement avec le favicon de chaque service sur iOS. Les pannes majeures pulsent nettement plus grandes que les incidents mineurs, pour saisir la gravité d’un coup d’œil. Mets en sourdine les incidents connus, marque les services critiques."),
        ("microphone-regular.svg", "Siri et Shortcuts",
         "Demandez \u00e0 Siri \u00ab\u00a0mets GitHub en sourdine pendant 2\u00a0heures\u00a0\u00bb ou \u00ab\u00a0affiche les probl\u00e8mes en cours\u00a0\u00bb. App Intents pour chaque action, plus un filtre Focus qui met en sourdine les services non critiques."),
        ("squares-four-regular.svg", "Widgets et Live Activities",
         "Widgets d\u2019\u00e9cran d\u2019accueil et d\u2019\u00e9cran verrouill\u00e9 sur iOS, plus un widget du Control Center. Les pannes actives s\u2019\u00e9pinglent \u00e0 la Dynamic Island."),
        ("watch-regular.svg", "Complications pour la montre",
         "\u00c9pinglez un service critique sur un cadran de montre ou laissez le Smart Stack faire remonter automatiquement les probl\u00e8mes actifs."),
        ("cloud-check-regular.svg", "Mac comme hub — iPhone en relais",
         "Le Mac est le hub le plus fiable : il interroge aussi souvent que toutes les 60 secondes (configurable jusqu’à 15 min) et diffuse les changements de statut vers iPhone, iPad, Watch et Vision Pro via iCloud. Si aucun Mac n’est en ligne, ton iPhone prend le relais en tant qu’émetteur de secours afin que les autres appareils continuent de recevoir les alertes."),
        ("monitor-regular.svg", "Vue de fiabilité des alertes",
         "Vois en un clin d’œil si les alertes te parviendront réellement — battement de cœur du Mac, état de l’actualisation en arrière-plan, push CloudKit et la dernière vérification de chaque appareil."),
        ("devices-regular.svg", "Toutes les plateformes Apple",
         "iPhone, iPad, barre de menus du Mac, Apple TV, Apple Watch et Vision Pro. Les services se synchronisent sur tous les appareils."),
        ("lightning-regular.svg", "D\u00e9tails des incidents",
         "Composants touch\u00e9s, incidents actifs, maintenance planifi\u00e9e et mises \u00e0 jour chronologiques \u2014 traduits dans votre langue."),
        ("battery-charging-regular.svg", "Interrogation adaptée à la batterie",
         "L’actualisation automatique s’adapte à la batterie, l’alimentation et la température. Chaque minute sur Mac, 5–15 sur iPhone, avec actualisation en arrière-plan sur iPad, Apple Watch, Vision Pro et Apple TV."),
        ("palette-regular.svg", f"{THEMES_COUNT} th\u00e8mes",
         "Standard et trois th\u00e8mes r\u00e9tro sont inclus. Fossil, Monolith, HAL et les autres se d\u00e9bloquent via des achats int\u00e9gr\u00e9s optionnels de type pourboire."),
        ("shield-check-regular.svg", "Les donn\u00e9es de l\u2019app restent en local",
         "L\u2019application n\u2019exige aucune inscription et ne contient aucune analyse int\u00e9gr\u00e9e. Vos services surveill\u00e9s restent sur votre appareil."),
        ("translate-regular.svg", f"{APP_LANGUAGE_COUNT} langues d\u2019application",
         "Anglais, allemand, fran\u00e7ais, espagnol, japonais, cor\u00e9en, chinois, portugais, russe et plus encore."),
    ],
    # 404
    "err_title": "Page introuvable \u2014 Vultyr",
    "err_description": "La page que vous recherchez n\u2019existe pas.",
    "err_heading": "Page introuvable",
    "err_message": "La page que vous recherchez n\u2019existe pas ou a \u00e9t\u00e9 d\u00e9plac\u00e9e.",
    "redirect_moved_fmt": "Cette page a \u00e9t\u00e9 d\u00e9plac\u00e9e. Redirection vers {name}\u2026",
    "err_popular_heading": "Services populaires",
    "err_browse_heading": "Parcourir les cat\u00e9gories",
    # privacy
    "privacy_title": "Politique de confidentialit\u00e9",
    "privacy_description": "Politique de confidentialit\u00e9 de Vultyr. L\u2019application ne collecte aucune donn\u00e9e personnelle. Ce site utilise Google Analytics sans cookies pour le trafic agr\u00e9g\u00e9 des visiteurs.",
    "privacy_last_updated": "Derni\u00e8re mise \u00e0 jour\u00a0: 11\u00a0avril 2026",
    "privacy_sections": [
        ("R\u00e9sum\u00e9",
         "<p>L\u2019<strong>application</strong> Vultyr ne collecte, ne stocke ni ne transmet aucune donn\u00e9e personnelle. Le <strong>site</strong> Vultyr (vultyr.app) utilise Google Analytics sans cookies pour comprendre le trafic agr\u00e9g\u00e9 des visiteurs. Cette page d\u00e9taille les deux.</p>"),
        ("Application \u2014 Collecte de donn\u00e9es",
         "<p>L\u2019application vultyr ne collecte aucune information personnelle. Elle ne n\u00e9cessite aucun compte, n\u2019inclut aucun SDK tiers d\u2019analyse ou de suivi, et ne contacte aucun serveur que nous exploitons.</p>"),
        ("Application \u2014 Requ\u00eates r\u00e9seau",
         "<p>L\u2019application effectue des requ\u00eates HTTPS directes vers les API publiques de pages d\u2019\u00e9tat (telles que Statuspage.io, Apple, Google Cloud et d\u2019autres) pour v\u00e9rifier l\u2019\u00e9tat des services. Ces requ\u00eates vont directement de votre appareil \u00e0 l\u2019API publique du service \u2014 elles ne transitent par aucun serveur que nous exploitons.</p>"),
        ("Application \u2014 Stockage des donn\u00e9es",
         "<p>Toutes les donn\u00e9es sont stock\u00e9es localement sur votre appareil \u00e0 l\u2019aide du framework SwiftData d\u2019Apple. Si vous activez la synchronisation iCloud, votre liste de services surveill\u00e9s est synchronis\u00e9e via l\u2019iCloud Key-Value Store d\u2019Apple, r\u00e9gi par la politique de confidentialit\u00e9 d\u2019Apple. Nous ne voyons jamais ces donn\u00e9es.</p>"),
        ("Application \u2014 Alertes entre appareils",
         "<p>Si vous activez les alertes entre appareils, les changements d\u2019\u00e9tat sont partag\u00e9s entre vos appareils via l\u2019iCloud Key-Value Store d\u2019Apple. Lorsque votre Mac d\u00e9tecte un changement d\u2019\u00e9tat, il \u00e9crit un signal l\u00e9ger dans votre compte iCloud. Vos autres appareils observent le changement et ex\u00e9cutent leur propre v\u00e9rification locale. Aucun serveur tiers n\u2019est impliqu\u00e9 \u2014 toute la communication passe par l\u2019infrastructure iCloud d\u2019Apple. Vous pouvez activer ou d\u00e9sactiver cette option depuis n\u2019importe quel appareil.</p>"),
        ("Application \u2014 Favicons",
         "<p>Les favicons des services sont r\u00e9cup\u00e9r\u00e9s depuis le service public de favicons de Google et mis en cache localement sur votre appareil.</p>"),
        ("Site \u2014 Analytique",
         "<p>Ce site (vultyr.app) utilise Google Analytics\u00a04 en mode sans cookies avec anonymisation d\u2019IP pour compter les vues de page agr\u00e9g\u00e9es. Plus pr\u00e9cis\u00e9ment, nous configurons gtag.js avec <code>anonymize_ip: true</code>, <code>client_storage: 'none'</code>, <code>allow_google_signals: false</code> et <code>allow_ad_personalization_signals: false</code>. Cela signifie qu\u2019aucun cookie <code>_ga</code> n\u2019est d\u00e9pos\u00e9, que votre IP est tronqu\u00e9e avant stockage et qu\u2019aucun identifiant publicitaire n\u2019est collect\u00e9. L\u2019application vultyr elle-m\u00eame ne contient aucune analyse.</p>"),
        ("Site \u2014 Domaines tiers",
         "<p>Le chargement de vultyr.app contacte les domaines tiers suivants\u00a0:</p>\n    <ul>\n        <li><strong>www.googletagmanager.com</strong> \u2014 charge le script gtag.js</li>\n        <li><strong>www.google-analytics.com</strong> / <strong>*.analytics.google.com</strong> \u2014 re\u00e7oit les signaux anonymis\u00e9s de vues de page</li>\n        <li><strong>www.google.com/g/collect</strong> \u2014 re\u00e7oit les m\u00eames signaux anonymis\u00e9s de vues de page (endpoint de collecte de secours de Google Analytics\u00a04)</li>\n    </ul>\n    <p>Nous ne chargeons pas Google Fonts (la police Audiowide est h\u00e9berg\u00e9e sur vultyr.app) et n\u2019utilisons pas de service tiers de favicons pour les images du site lui-m\u00eame.</p>"),
        ("Application \u2014 Services tiers",
         "<p>L\u2019application vultyr ne s\u2019int\u00e8gre \u00e0 aucun service tiers d\u2019analyse, de publicit\u00e9 ou de suivi. Les seules requ\u00eates externes vont vers les API publiques de pages d\u2019\u00e9tat et vers le service de favicons de Google.</p>"),
        ("Confidentialit\u00e9 des enfants",
         "<p>L\u2019application vultyr ne collecte de donn\u00e9es aupr\u00e8s de personne, y compris des enfants de moins de 13\u00a0ans. Le site n\u2019enregistre que des comptages de visiteurs anonymis\u00e9s et agr\u00e9g\u00e9s.</p>"),
        ("Modifications",
         "<p>Si cette politique change, nous mettrons \u00e0 jour la date ci-dessus.</p>"),
        ("Contact",
         "<p>Des questions\u00a0? \u00c9crivez \u00e0 <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a></p>"),
    ],
    # support
    "support_title": "Assistance",
    "support_description": "Obtenez de l\u2019aide pour Vultyr, le moniteur d\u2019\u00e9tat des services pour iPhone, iPad, Mac, Apple Watch, Apple TV et Apple Vision Pro. FAQ, contact et d\u00e9pannage.",
    "support_contact_heading": "Contact",
    "support_contact_html": "<p>Pour les rapports de bogues, les demandes de fonctionnalit\u00e9s ou les questions\u00a0:<br>\n    <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a></p>",
    "support_faq_heading": "FAQ",
    "support_faqs": [
        ("\u00c0 quelle fr\u00e9quence vultyr v\u00e9rifie-t-il l\u2019\u00e9tat des services\u00a0?",
         "Sur Mac\u00a0: toutes les 60\u00a0secondes lorsqu\u2019il est branch\u00e9. Sur iPhone\u00a0: toutes les 5, 10 ou 15\u00a0minutes (configurable), avec des v\u00e9rifications p\u00e9riodiques en arri\u00e8re-plan lorsque les conditions le permettent. Sur Apple Watch\u00a0: toutes les 15\u00a0minutes. Sur Apple TV\u00a0: toutes les 5\u00a0minutes. L\u2019interrogation s\u2019adapte automatiquement au niveau de batterie, \u00e0 l\u2019\u00e9tat d\u2019alimentation et aux conditions thermiques.",
         "<p>Sur Mac\u00a0: toutes les 60\u00a0secondes lorsqu\u2019il est branch\u00e9. Sur iPhone\u00a0: toutes les 5, 10 ou 15\u00a0minutes (configurable), avec des v\u00e9rifications p\u00e9riodiques en arri\u00e8re-plan lorsque les conditions le permettent. Sur Apple Watch\u00a0: toutes les 15\u00a0minutes. Sur Apple TV\u00a0: toutes les 5\u00a0minutes. L\u2019interrogation s\u2019adapte automatiquement au niveau de batterie, \u00e0 l\u2019\u00e9tat d\u2019alimentation et aux conditions thermiques.</p>"),
        ("Comment fonctionnent les alertes entre appareils\u00a0?",
         "L\u2019app Mac est le hub. Gardez-la en fonctionnement (barre de menus ou fen\u00eatre pleine) et elle interroge aussi souvent que toutes les 60\u00a0secondes (configurable jusqu\u2019\u00e0 15\u00a0min). Lorsqu\u2019un changement d\u2019\u00e9tat est d\u00e9tect\u00e9, elle \u00e9crit un signal l\u00e9ger dans l\u2019iCloud Key-Value Store\u00a0; vos iPhone, iPad, Watch, Apple TV et Vision Pro captent le changement et ex\u00e9cutent leur propre v\u00e9rification locale. Aucune cl\u00e9, aucun jeton, aucune configuration \u2014 activez simplement \u00ab\u00a0Alertes entre appareils\u00a0\u00bb dans les r\u00e9glages sur n\u2019importe quel appareil. Sans un Mac jouant le r\u00f4le de hub, les alertes reposent sur l\u2019ex\u00e9cution en arri\u00e8re-plan d\u2019iOS et seront retard\u00e9es ou manqu\u00e9es.",
         "<p>L\u2019app Mac est le hub. Gardez-la en fonctionnement (barre de menus ou fen\u00eatre pleine) et elle interroge aussi souvent que toutes les 60\u00a0secondes (configurable jusqu\u2019\u00e0 15\u00a0min). Lorsqu\u2019un changement d\u2019\u00e9tat est d\u00e9tect\u00e9, elle \u00e9crit un signal l\u00e9ger dans l\u2019iCloud Key-Value Store\u00a0; vos iPhone, iPad, Watch, Apple TV et Vision Pro captent le changement et ex\u00e9cutent leur propre v\u00e9rification locale. Aucune cl\u00e9, aucun jeton, aucune configuration \u2014 activez simplement \u00ab\u00a0Alertes entre appareils\u00a0\u00bb dans les r\u00e9glages sur n\u2019importe quel appareil. Sans un Mac jouant le r\u00f4le de hub, les alertes reposent sur l\u2019ex\u00e9cution en arri\u00e8re-plan d\u2019iOS et seront retard\u00e9es ou manqu\u00e9es.</p>"),
        ("Ai-je besoin de l\u2019app Mac pour des alertes fiables\u00a0?",
         "Oui \u2014 nous la recommandons vivement. iOS limite l\u2019ex\u00e9cution en arri\u00e8re-plan, donc l\u2019iPhone et l\u2019iPad ne peuvent v\u00e9rifier que toutes les 5 \u00e0 15\u00a0minutes (configurable) et peuvent reporter davantage en cas de batterie faible, de mode \u00c9conomie d\u2019\u00e9nergie ou de mauvaise connectivit\u00e9. L\u2019app Mac interroge en continu (toutes les 60\u00a0secondes lorsqu\u2019elle est branch\u00e9e) et diffuse les changements d\u2019\u00e9tat vers vos autres appareils via iCloud. Sans un Mac ex\u00e9cutant Vultyr, les alertes iOS, watchOS et tvOS fonctionnent toujours mais peuvent \u00eatre consid\u00e9rablement retard\u00e9es ou manqu\u00e9es. Pour une surveillance en temps r\u00e9el, gardez l\u2019app Mac en fonctionnement \u2014 elle est discr\u00e8te dans la barre de menus et c\u2019est ainsi que Vultyr est con\u00e7u pour \u00eatre utilis\u00e9.",
         "<p>Oui \u2014 nous la recommandons vivement. iOS limite l\u2019ex\u00e9cution en arri\u00e8re-plan, donc l\u2019iPhone et l\u2019iPad ne peuvent v\u00e9rifier que toutes les 5 \u00e0 15\u00a0minutes (configurable) et peuvent reporter davantage en cas de batterie faible, de mode \u00c9conomie d\u2019\u00e9nergie ou de mauvaise connectivit\u00e9. L\u2019app Mac interroge en continu (toutes les 60\u00a0secondes lorsqu\u2019elle est branch\u00e9e) et diffuse les changements d\u2019\u00e9tat vers vos autres appareils via iCloud. Sans un Mac ex\u00e9cutant Vultyr, les alertes iOS, watchOS et tvOS fonctionnent toujours mais peuvent \u00eatre consid\u00e9rablement retard\u00e9es ou manqu\u00e9es. Pour une surveillance en temps r\u00e9el, gardez l\u2019app Mac en fonctionnement \u2014 elle est discr\u00e8te dans la barre de menus et c\u2019est ainsi que Vultyr est con\u00e7u pour \u00eatre utilis\u00e9.</p>"),
        ("vultyr fonctionne-t-il avec Siri et Shortcuts\u00a0?",
         "Oui. Les App Intents int\u00e9gr\u00e9s vous permettent de dire \u00ab\u00a0Dis Siri, mets GitHub en sourdine pendant 2\u00a0heures\u00a0\u00bb, \u00ab\u00a0v\u00e9rifie l\u2019\u00e9tat de Stripe\u00a0\u00bb ou \u00ab\u00a0affiche les probl\u00e8mes en cours\u00a0\u00bb, et vous pouvez brancher ces m\u00eames actions dans l\u2019app Shortcuts. Il existe aussi un filtre Focus pour qu\u2019un mode \u00ab\u00a0vultyr Focus\u00a0\u00bb mette automatiquement en sourdine les services non critiques.",
         "<p>Oui. Les App Intents int\u00e9gr\u00e9s vous permettent de dire \u00ab\u00a0Dis Siri, mets GitHub en sourdine pendant 2\u00a0heures\u00a0\u00bb, \u00ab\u00a0v\u00e9rifie l\u2019\u00e9tat de Stripe\u00a0\u00bb ou \u00ab\u00a0affiche les probl\u00e8mes en cours\u00a0\u00bb, et vous pouvez brancher ces m\u00eames actions dans l\u2019app Shortcuts. Il existe aussi un filtre Focus pour qu\u2019un mode \u00ab\u00a0vultyr Focus\u00a0\u00bb mette automatiquement en sourdine les services non critiques.</p>"),
        ("Y a-t-il des widgets et des Live Activities\u00a0?",
         "Sur iOS, il y a des widgets d\u2019\u00e9cran d\u2019accueil et d\u2019\u00e9cran verrouill\u00e9 (service unique et r\u00e9sum\u00e9 d\u2019\u00e9tat) ainsi qu\u2019un widget du Control Center. Les pannes actives s\u2019\u00e9pinglent \u00e0 la Dynamic Island sous forme de Live Activities. Sur watchOS, des complications sont disponibles pour tous les cadrans, avec une pertinence Smart Stack pour que le bon service apparaisse lorsque quelque chose est en panne.",
         "<p>Sur iOS, il y a des widgets d\u2019\u00e9cran d\u2019accueil et d\u2019\u00e9cran verrouill\u00e9 (service unique et r\u00e9sum\u00e9 d\u2019\u00e9tat) ainsi qu\u2019un widget du Control Center. Les pannes actives s\u2019\u00e9pinglent \u00e0 la Dynamic Island sous forme de Live Activities. Sur watchOS, des complications sont disponibles pour tous les cadrans, avec une pertinence Smart Stack pour que le bon service apparaisse lorsque quelque chose est en panne.</p>"),
        ("L\u2019application vultyr collecte-t-elle mes donn\u00e9es\u00a0?",
         "Non. L\u2019application n\u2019a aucun compte, aucun suivi int\u00e9gr\u00e9, aucune analyse int\u00e9gr\u00e9e. Tous vos services surveill\u00e9s restent sur votre appareil. Remarque\u00a0: ce site (vultyr.app) utilise Google Analytics sans cookies pour compter les visiteurs agr\u00e9g\u00e9s \u2014 voir la Politique de confidentialit\u00e9 pour les d\u00e9tails.",
         "<p>Non. L\u2019application n\u2019a aucun compte, aucun suivi int\u00e9gr\u00e9, aucune analyse int\u00e9gr\u00e9e. Tous vos services surveill\u00e9s restent sur votre appareil. Remarque\u00a0: ce site (vultyr.app) utilise Google Analytics sans cookies pour compter les visiteurs agr\u00e9g\u00e9s \u2014 voir la <a href=\"/fr/privacy.html\">Politique de confidentialit\u00e9</a> pour les d\u00e9tails.</p>"),
        ("Comment synchroniser mes services entre appareils\u00a0?",
         "Vos services surveill\u00e9s se synchronisent automatiquement via iCloud. Les th\u00e8mes et les r\u00e9glages se synchronisent \u00e9galement sur tous vos appareils Apple via l\u2019iCloud Key-Value Store.",
         "<p>Vos services surveill\u00e9s se synchronisent automatiquement via iCloud. Les th\u00e8mes et les r\u00e9glages se synchronisent \u00e9galement sur tous vos appareils Apple via l\u2019iCloud Key-Value Store.</p>"),
        ("Quelles sont les options de th\u00e8me\u00a0?",
         "12 th\u00e8mes\u00a0: Standard, Terminal, Amber, Blue, Neon, Dracula, Nord, Solarized, Catppuccin, Fossil, Monolith et HAL. Standard et les trois th\u00e8mes r\u00e9tro (Terminal, Amber, Blue) sont inclus. Fossil, Monolith, HAL et les autres se d\u00e9bloquent via des achats int\u00e9gr\u00e9s optionnels de type pourboire (0,99\u00a0$ / 4,99\u00a0$ / 9,99\u00a0$), ce qui contribue \u00e9galement au financement du d\u00e9veloppement. Les th\u00e8mes se synchronisent automatiquement sur tous vos appareils.",
         "<p>12 th\u00e8mes\u00a0: Standard, Terminal, Amber, Blue, Neon, Dracula, Nord, Solarized, Catppuccin, Fossil, Monolith et HAL. Standard et les trois th\u00e8mes r\u00e9tro (Terminal, Amber, Blue) sont inclus. Fossil, Monolith, HAL et les autres se d\u00e9bloquent via des achats int\u00e9gr\u00e9s optionnels de type pourboire (0,99\u00a0$ / 4,99\u00a0$ / 9,99\u00a0$), ce qui contribue \u00e9galement au financement du d\u00e9veloppement. Les th\u00e8mes se synchronisent automatiquement sur tous vos appareils.</p>"),
        ("Puis-je couper les notifications pour un incident connu\u00a0?",
         "Oui. Lorsque vous consultez un service avec un incident actif, vous pouvez couper les notifications pendant une p\u00e9riode d\u00e9finie pour ne pas \u00eatre alert\u00e9 \u00e0 plusieurs reprises d\u2019un probl\u00e8me que vous connaissez d\u00e9j\u00e0. Vous pouvez aussi couper par la voix \u2014 \u00ab\u00a0Dis Siri, mets GitHub en sourdine pendant 2\u00a0heures\u00a0\u00bb \u2014 ou depuis l\u2019app Shortcuts.",
         "<p>Oui. Lorsque vous consultez un service avec un incident actif, vous pouvez couper les notifications pendant une p\u00e9riode d\u00e9finie pour ne pas \u00eatre alert\u00e9 \u00e0 plusieurs reprises d\u2019un probl\u00e8me que vous connaissez d\u00e9j\u00e0. Vous pouvez aussi couper par la voix \u2014 \u00ab\u00a0Dis Siri, mets GitHub en sourdine pendant 2\u00a0heures\u00a0\u00bb \u2014 ou depuis l\u2019app Shortcuts.</p>"),
        ("Quelles plateformes sont prises en charge\u00a0?",
         "iPhone et iPad (avec widgets et Live Activities), Mac (avec une app de barre de menus et une fen\u00eatre pleine), Apple Watch (avec complications et Smart Stack), Apple TV et Apple Vision Pro. L\u2019application est gratuite au t\u00e9l\u00e9chargement sur chaque plateforme.",
         "<p>iPhone et iPad (avec widgets et Live Activities), Mac (avec une app de barre de menus et une fen\u00eatre pleine), Apple Watch (avec complications et Smart Stack), Apple TV et Apple Vision Pro. L\u2019application est gratuite au t\u00e9l\u00e9chargement sur chaque plateforme.</p>"),
        ("Puis-je demander l\u2019ajout d\u2019un nouveau service\u00a0?",
         "Oui\u00a0! Envoyez un e\u2011mail \u00e0 support@vultyr.app avec le nom du service et l\u2019URL de sa page d\u2019\u00e9tat.",
         "<p>Oui\u00a0! Envoyez un e\u2011mail \u00e0 <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a> avec le nom du service et l\u2019URL de sa page d\u2019\u00e9tat.</p>"),
    ],
},
    "it": {
    "html_lang": "it",
    "og_locale": "it_IT",
    "og_image_alt": "Icona dell'app Vultyr \u2014 monitor dello stato dei servizi",
    "devices": "iPhone, iPad, Mac, Apple Watch, Apple TV e Vision Pro",
    "skip_to_main": "Vai al contenuto principale",
    "topbar_brand_aria": "Home Vultyr",
    "nav_primary_aria": "Principale",
    "nav_services": "servizi",
    "nav_support": "supporto",
    "nav_download": "Scarica",
    "footer_nav_aria": "Navigazione del footer",
    "footer_home": "Home",
    "footer_services": "Servizi",
    "footer_privacy": "Privacy",
    "footer_support": "Supporto",
    "footer_contact": "Contatti",
    "copyright": "\u00a9 2026 Vultyr. Tutti i diritti riservati.",
    "breadcrumb_aria": "Breadcrumb",
    "breadcrumb_vultyr": "Vultyr",
    "breadcrumb_services": "Servizi",
    # services page
    "svcs_title": "Vultyr \u2014 oltre 200 controlli di stato",
    "svcs_description": "Oltre 200 controlli di stato su servizi cloud, strumenti di sviluppo, comunicazione, IA e molto altro \u2014 tutti monitorati da Vultyr.",
    "svcs_h1_lead": "Controlli",
    "svcs_h1_highlight": "di stato",
    "svcs_subtitle": "Oltre 200 controlli di stato che vultyr esegue su servizi cloud, strumenti di sviluppo e piattaforme.",
    "svcs_categories_aria": "Sfoglia per categoria",
    "svc_row_status": "Pagina di stato",
    "svc_row_homepage": "Sito",
    "svcs_item_list_name": "Servizi monitorati da Vultyr",
    # service page
    "svcp_title_fmt": "{name} non funziona? Monitor dello stato di {name} | Vultyr",
    "svcp_description_fmt": "Controlla se {name} non funziona in questo momento. Aggiornamenti di stato in tempo reale e monitoraggio dei disservizi di {name} con Vultyr. Gratis su {devices}.",
    "svcp_live_check": "Controllo in tempo reale",
    "svcp_view_current_status": "Visualizza stato attuale \u2192",
    "svcp_alert_hint_prefix": "Per avvisi immediati, ",
    "svcp_alert_hint_link": "scarica Vultyr",
    "svcp_categories_label": "Categorie:",
    "svcp_official_status": "Pagina di stato ufficiale",
    "svcp_homepage_fmt": "Sito di {name}",
    "svcp_faq_heading": "FAQ",
    "svcp_faq_q1_fmt": "{name} non funziona in questo momento?",
    "svcp_faq_a1_fmt": "Consulta la pagina di stato ufficiale di {name} collegata qui sopra per lo stato attuale. Per un monitoraggio continuo con avvisi immediati sui disservizi su tutti i tuoi dispositivi Apple, scarica l'app gratuita Vultyr.",
    "svcp_faq_a1_ld_fmt": "Consulta la pagina di stato ufficiale di {name} all'indirizzo {url} per lo stato attuale. Scarica l'app gratuita Vultyr per ricevere avvisi immediati sui disservizi su tutti i tuoi dispositivi Apple.",
    "svcp_faq_q2_fmt": "Come posso monitorare lo stato di {name}?",
    "svcp_faq_a2_fmt": "Vultyr monitora {name} nell'ambito di oltre 200 controlli di stato su servizi cloud, strumenti di sviluppo e piattaforme. Ricevi avvisi immediati sui disservizi su {devices} \u2014 completamente gratis.",
    "svcp_faq_a2_ld_fmt": "Scarica Vultyr (gratis) per monitorare {name} nell'ambito di oltre 200 controlli di stato con avvisi in tempo reale su {devices}. Vultyr esegue ogni controllo automaticamente e ti avvisa nel momento in cui viene rilevato un disservizio.",
    "svcp_related_heading": "Servizi correlati",
    "svcp_related_aria": "Servizi correlati",
    "svcp_cta_heading_fmt": "Monitora {name} su tutti i tuoi dispositivi",
    "svcp_cta_body_fmt": "Ricevi avvisi immediati quando {name} va offline. Gratis su tutte le piattaforme Apple.",
    "cta_download_vultyr": "Scarica Vultyr",
    "cta_download_vultyr_aria": "Scarica Vultyr sull'App Store",
    # category page
    "catp_title_fmt": "Monitor dello stato di \u00ab{name}\u00bb \u2014 {count_services} | Vultyr",
    "catp_description_fmt": "Monitora lo stato di {count_services} nella categoria \u00ab{name_lower}\u00bb. Avvisi in tempo reale sui disservizi per {sample} e altri.",
    "catp_item_list_name_fmt": "Monitor dello stato: {name}",
    "catp_subtitle_fmt": "{count_services} monitorati da Vultyr",
    "catp_services_aria_fmt": "Servizi della categoria {name}",
    "catp_other_heading": "Altre categorie",
    "catp_cta_heading_fmt": "Monitora tutti i {count_services} all'istante",
    "catp_cta_body": "Ricevi avvisi in tempo reale sui disservizi su tutti i tuoi dispositivi Apple. Gratis.",
    # home page
    "home_title": "Vultyr \u2014 monitor dello stato dei servizi per AWS, Slack, GitHub e altri",
    "home_description": "Non funziona? Oltre 200 controlli di stato su servizi cloud, strumenti di sviluppo e piattaforme con avvisi immediati sui disservizi. Gratis su iPhone, iPad, Mac, Apple Watch, Apple TV e Apple Vision Pro.",
    "home_og_title": "Vultyr \u2014 monitor dello stato dei servizi",
    "home_app_ld_description": "Monitora oltre 200 controlli di stato su servizi cloud, strumenti di sviluppo e piattaforme con avvisi immediati sui disservizi.",
    "home_hero_tag": "Oltre 200 controlli",
    "home_hero_question": "Non funziona?",
    "home_hero_answer": "Scoprilo prima dei tuoi utenti.",
    "home_hero_services": "Oltre 200 controlli di stato \u2014 AWS, GitHub, Slack, Stripe e altri \u2014 con avvisi immediati sui disservizi su ogni dispositivo Apple.",
    "home_appstore_alt": "Scarica sull'App Store",
    "home_appstore_aria": "Scarica Vultyr sull'App Store",
    "home_free_on_prefix": "Gratis su",
    "home_screenshots_aria": "Screenshot dell'app",
    "home_screenshot_dash_alt": "Dashboard di Vultyr con stato \u00abTutto a posto\u00bb e servizi come AWS, GitHub e Slack monitorati",
    "home_screenshot_settings_alt_fmt": "Impostazioni di aspetto di Vultyr con {themes} temi, inclusi Terminal, Amber, Dracula e Nord",
    "home_screenshot_services_alt_fmt": "Browser dei servizi di Vultyr con {categories} categorie, incluse Cloud, Dev Tools e AI",
    "home_stats_aria": "Numeri chiave",
    "home_stats_checks": "Controlli",
    "home_stats_categories": "Categorie",
    "home_stats_platforms": "Piattaforme",
    "home_stats_languages": "Lingue",
    "home_features_heading": "Tutto quello che ti serve per anticipare i disservizi",
    "home_features_sub": "Nessun account, nessun tracciamento interno. Solo stato.",
    "home_bottom_heading": "Pronto a monitorare il tuo stack?",
    "home_bottom_sub": "Gratis. Nessun account richiesto. Disponibile ovunque.",
    "home_bottom_button": "Scarica gratis",
    "home_bottom_aria": "Scarica Vultyr gratis sull'App Store",
    "home_languages_heading": "Disponibile in 17 lingue",
    "home_features": [
        ("chart-bar-regular.svg", "Dashboard di stato in tempo reale",
         "AWS, GitHub, Cloudflare, Slack, Stripe, Discord, OpenAI, Anthropic e oltre 200 altri — tutti in un unico posto. Gli indicatori di stato si sincronizzano con ProMotion a 120Hz su iPhone Pro e iPad Pro."),
        ("bell-ringing-regular.svg", "Avvisi intelligenti",
         "Notifiche di interruzione e ripristino con il favicon di ciascun servizio su iOS. I guasti maggiori pulsano visibilmente più grandi degli incidenti minori, così la gravità si coglie a colpo d’occhio. Silenzia gli incidenti noti, aggiungi le stelle ai servizi critici."),
        ("microphone-regular.svg", "Siri e Shortcuts",
         "Chiedi a Siri \u00absilenzia GitHub per 2 ore\u00bb o \u00abmostra i problemi attuali\u00bb. App Intents per ogni azione, pi\u00f9 un Focus Filter che silenzia i servizi non critici."),
        ("squares-four-regular.svg", "Widget e Live Activities",
         "Widget per la schermata Home e la schermata di blocco su iOS, pi\u00f9 un widget per Control Center. I disservizi attivi vengono fissati nella Dynamic Island."),
        ("watch-regular.svg", "Complicazioni per Watch",
         "Fissa un servizio critico su un quadrante, oppure lascia che Smart Stack faccia emergere automaticamente i problemi attivi."),
        ("cloud-check-regular.svg", "Mac come hub — iPhone di riserva",
         "Mac è l’hub più affidabile: interroga fino a ogni 60 secondi (configurabile fino a 15 min) e trasmette i cambi di stato a iPhone, iPad, Watch e Vision Pro tramite iCloud. Se nessun Mac è online, il tuo iPhone subentra come publisher di riserva in modo che gli altri dispositivi ricevano comunque le notifiche."),
        ("monitor-regular.svg", "Visualizzazione affidabilità notifiche",
         "Scopri a colpo d’occhio se le notifiche ti raggiungeranno davvero — heartbeat del Mac, stato dell’aggiornamento in background, push CloudKit e l’ultimo controllo di ogni dispositivo."),
        ("devices-regular.svg", "Ogni piattaforma Apple",
         "iPhone, iPad, barra dei menu del Mac, Apple TV, Apple Watch e Vision Pro. I servizi si sincronizzano su tutti i dispositivi."),
        ("lightning-regular.svg", "Dettagli degli incidenti",
         "Componenti coinvolti, incidenti attivi, manutenzioni pianificate e aggiornamenti della timeline \u2014 localizzati nella tua lingua."),
        ("battery-charging-regular.svg", "Polling che rispetta la batteria",
         "L’aggiornamento automatico si adatta a batteria, alimentazione e temperatura. Ogni minuto su Mac, 5–15 su iPhone, con aggiornamento in background su iPad, Apple Watch, Vision Pro e Apple TV."),
        ("palette-regular.svg", f"{THEMES_COUNT} temi",
         "Standard e tre temi retro inclusi. Fossil, Monolith, HAL e gli altri si sbloccano tramite IAP opzionali a titolo di mancia."),
        ("shield-check-regular.svg", "I dati dell'app restano in locale",
         "L'app non richiede registrazione e non ha analytics integrati. I servizi che monitori restano sul tuo dispositivo."),
        ("translate-regular.svg", f"{APP_LANGUAGE_COUNT} lingue dell'app",
         "Inglese, tedesco, francese, spagnolo, giapponese, coreano, cinese, portoghese, russo e altre."),
    ],
    # 404
    "err_title": "Pagina non trovata \u2014 Vultyr",
    "err_description": "La pagina che stai cercando non esiste.",
    "err_heading": "Pagina non trovata",
    "err_message": "La pagina che stai cercando non esiste o \u00e8 stata spostata.",
    "redirect_moved_fmt": "Questa pagina \u00e8 stata spostata. Reindirizzamento a {name}\u2026",
    "err_popular_heading": "Servizi popolari",
    "err_browse_heading": "Sfoglia le categorie",
    # privacy
    "privacy_title": "Informativa sulla privacy",
    "privacy_description": "Informativa sulla privacy di Vultyr. L'app non raccoglie dati personali. Questo sito utilizza Google Analytics senza cookie per il traffico aggregato dei visitatori.",
    "privacy_last_updated": "Ultimo aggiornamento: 11 aprile 2026",
    "privacy_sections": [
        ("Sintesi",
         "<p>L'<strong>app</strong> Vultyr non raccoglie, non memorizza e non trasmette alcun dato personale. Il <strong>sito</strong> Vultyr (vultyr.app) utilizza Google Analytics senza cookie per comprendere il traffico aggregato dei visitatori. Questa pagina spiega entrambi gli aspetti in dettaglio.</p>"),
        ("App \u2014 Raccolta dei dati",
         "<p>L'app vultyr non raccoglie alcuna informazione personale. Non richiede un account, non include SDK di analytics o tracciamento di terze parti e non contatta alcun server gestito da noi.</p>"),
        ("App \u2014 Richieste di rete",
         "<p>L'app effettua richieste HTTPS dirette ad API pubbliche di pagine di stato (come Statuspage.io, Apple, Google Cloud e altre) per verificare lo stato dei servizi. Queste richieste vanno direttamente dal tuo dispositivo all'API pubblica del servizio \u2014 non transitano per alcun server gestito da noi.</p>"),
        ("App \u2014 Archiviazione dei dati",
         "<p>Tutti i dati vengono archiviati localmente sul tuo dispositivo tramite il framework SwiftData di Apple. Se abiliti la sincronizzazione iCloud, l'elenco dei servizi monitorati viene sincronizzato tramite iCloud Key-Value Store di Apple, soggetto all'informativa sulla privacy di Apple. Questi dati non sono mai visibili a noi.</p>"),
        ("App \u2014 Avvisi tra dispositivi",
         "<p>Se abiliti gli avvisi tra dispositivi, i cambi di stato vengono condivisi tra i tuoi dispositivi tramite iCloud Key-Value Store di Apple. Quando il tuo Mac rileva un cambio di stato, scrive un segnale leggero nel tuo account iCloud. Gli altri dispositivi rilevano il cambiamento ed eseguono il proprio controllo locale. Non \u00e8 coinvolto alcun server di terze parti \u2014 tutta la comunicazione passa attraverso l'infrastruttura iCloud di Apple. Puoi attivare o disattivare questa funzione da qualsiasi dispositivo.</p>"),
        ("App \u2014 Favicon",
         "<p>Le favicon dei servizi vengono scaricate dal servizio pubblico di favicon di Google e memorizzate nella cache locale del tuo dispositivo.</p>"),
        ("Sito \u2014 Analytics",
         "<p>Questo sito (vultyr.app) utilizza Google Analytics 4 in modalit\u00e0 senza cookie e con IP anonimizzato per contare le visualizzazioni di pagina aggregate. In particolare, configuriamo gtag.js con <code>anonymize_ip: true</code>, <code>client_storage: 'none'</code>, <code>allow_google_signals: false</code> e <code>allow_ad_personalization_signals: false</code>. Ci\u00f2 significa che non viene impostato alcun cookie <code>_ga</code>, il tuo IP viene troncato prima della memorizzazione e non vengono raccolti identificatori pubblicitari. L'app vultyr in s\u00e9 non include alcun analytics.</p>"),
        ("Sito \u2014 Domini di terze parti",
         "<p>Caricando vultyr.app vengono contattati i seguenti domini di terze parti:</p>\n    <ul>\n        <li><strong>www.googletagmanager.com</strong> \u2014 carica lo script gtag.js</li>\n        <li><strong>www.google-analytics.com</strong> / <strong>*.analytics.google.com</strong> \u2014 riceve i segnali anonimizzati delle visualizzazioni di pagina</li>\n        <li><strong>www.google.com/g/collect</strong> \u2014 riceve gli stessi segnali anonimizzati delle visualizzazioni di pagina (endpoint di raccolta di fallback di Google Analytics 4)</li>\n    </ul>\n    <p>Non carichiamo Google Fonts (il font Audiowide \u00e8 ospitato direttamente su vultyr.app) e non utilizziamo un servizio di favicon di terze parti per le immagini del sito.</p>"),
        ("App \u2014 Servizi di terze parti",
         "<p>L'app vultyr non si integra con alcun servizio di analytics, pubblicit\u00e0 o tracciamento di terze parti. Le uniche richieste esterne sono verso le API pubbliche di stato e il servizio di favicon di Google.</p>"),
        ("Privacy dei minori",
         "<p>L'app vultyr non raccoglie dati da nessuno, inclusi i bambini di et\u00e0 inferiore a 13 anni. Il sito registra solo conteggi aggregati e anonimizzati dei visitatori.</p>"),
        ("Modifiche",
         "<p>Se questa informativa cambia, aggiorneremo la data qui sopra.</p>"),
        ("Contatti",
         "<p>Domande? Scrivi a <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a></p>"),
    ],
    # support
    "support_title": "Supporto",
    "support_description": "Assistenza per Vultyr, il monitor dello stato dei servizi per iPhone, iPad, Mac, Apple Watch, Apple TV e Apple Vision Pro. FAQ, contatti e risoluzione dei problemi.",
    "support_contact_heading": "Contatti",
    "support_contact_html": "<p>Per segnalazioni di bug, richieste di funzionalit\u00e0 o domande:<br>\n    <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a></p>",
    "support_faq_heading": "FAQ",
    "support_faqs": [
        ("Con quale frequenza vultyr controlla lo stato dei servizi?",
         "Su Mac: anche ogni 60 secondi quando \u00e8 collegato alla rete elettrica. Su iPhone: ogni 5, 10 o 15 minuti (configurabile), con controlli periodici in background quando le condizioni lo permettono. Su Apple Watch: ogni 15 minuti. Su Apple TV: ogni 5 minuti. Il polling si adatta automaticamente a livello di batteria, alimentazione e condizioni termiche.",
         "<p>Su Mac: anche ogni 60 secondi quando \u00e8 collegato alla rete elettrica. Su iPhone: ogni 5, 10 o 15 minuti (configurabile), con controlli periodici in background quando le condizioni lo permettono. Su Apple Watch: ogni 15 minuti. Su Apple TV: ogni 5 minuti. Il polling si adatta automaticamente a livello di batteria, alimentazione e condizioni termiche.</p>"),
        ("Come funzionano gli avvisi tra dispositivi?",
         "L'app Mac \u00e8 il fulcro. Tienila in esecuzione (nella barra dei menu o a finestra piena) ed eseguir\u00e0 il polling fino a ogni 60 secondi (configurabile fino a 15 min). Quando viene rilevato un cambio di stato, scrive un segnale leggero in iCloud Key-Value Store; il tuo iPhone, iPad, Watch, Apple TV e Vision Pro rilevano il cambiamento ed eseguono il proprio controllo locale. Nessuna chiave, nessun token, nessuna configurazione \u2014 basta attivare \u00abAvvisi tra dispositivi\u00bb nelle impostazioni di qualsiasi dispositivo. Senza un Mac che funge da fulcro, gli avvisi dipendono dall'esecuzione in background di iOS e saranno ritardati o persi.",
         "<p>L'app Mac \u00e8 il fulcro. Tienila in esecuzione (nella barra dei menu o a finestra piena) ed eseguir\u00e0 il polling fino a ogni 60 secondi (configurabile fino a 15 min). Quando viene rilevato un cambio di stato, scrive un segnale leggero in iCloud Key-Value Store; il tuo iPhone, iPad, Watch, Apple TV e Vision Pro rilevano il cambiamento ed eseguono il proprio controllo locale. Nessuna chiave, nessun token, nessuna configurazione \u2014 basta attivare \u00abAvvisi tra dispositivi\u00bb nelle impostazioni di qualsiasi dispositivo. Senza un Mac che funge da fulcro, gli avvisi dipendono dall'esecuzione in background di iOS e saranno ritardati o persi.</p>"),
        ("Mi serve l'app Mac per avvisi affidabili?",
         "S\u00ec \u2014 lo raccomandiamo vivamente. iOS limita l'esecuzione in background, quindi iPhone e iPad possono controllare solo ogni 5\u201315 minuti (configurabile) e possono ritardare ulteriormente con batteria scarica, modalit\u00e0 Risparmio energetico o connettivit\u00e0 scarsa. L'app Mac esegue il polling in modo continuo (ogni 60 secondi quando \u00e8 collegato alla rete elettrica) e trasmette i cambi di stato agli altri dispositivi tramite iCloud. Senza un Mac con Vultyr in esecuzione, gli avvisi su iOS, watchOS e tvOS continuano a funzionare ma possono essere notevolmente ritardati o persi. Per un monitoraggio in tempo reale, tieni l'app Mac in esecuzione \u2014 \u00e8 minuscola nella barra dei menu ed \u00e8 il modo in cui Vultyr \u00e8 pensato per essere usato.",
         "<p>S\u00ec \u2014 lo raccomandiamo vivamente. iOS limita l'esecuzione in background, quindi iPhone e iPad possono controllare solo ogni 5\u201315 minuti (configurabile) e possono ritardare ulteriormente con batteria scarica, modalit\u00e0 Risparmio energetico o connettivit\u00e0 scarsa. L'app Mac esegue il polling in modo continuo (ogni 60 secondi quando \u00e8 collegato alla rete elettrica) e trasmette i cambi di stato agli altri dispositivi tramite iCloud. Senza un Mac con Vultyr in esecuzione, gli avvisi su iOS, watchOS e tvOS continuano a funzionare ma possono essere notevolmente ritardati o persi. Per un monitoraggio in tempo reale, tieni l'app Mac in esecuzione \u2014 \u00e8 minuscola nella barra dei menu ed \u00e8 il modo in cui Vultyr \u00e8 pensato per essere usato.</p>"),
        ("vultyr funziona con Siri e Shortcuts?",
         "S\u00ec. Gli App Intents integrati ti permettono di dire \u00abHey Siri, silenzia GitHub per 2 ore\u00bb, \u00abcontrolla lo stato di Stripe\u00bb o \u00abmostra i problemi attuali\u00bb, e puoi collegare le stesse azioni nell'app Shortcuts. C'\u00e8 anche un Focus Filter, quindi una modalit\u00e0 Focus \u00abvultyr\u00bb pu\u00f2 silenziare automaticamente i servizi non critici.",
         "<p>S\u00ec. Gli App Intents integrati ti permettono di dire \u00abHey Siri, silenzia GitHub per 2 ore\u00bb, \u00abcontrolla lo stato di Stripe\u00bb o \u00abmostra i problemi attuali\u00bb, e puoi collegare le stesse azioni nell'app Shortcuts. C'\u00e8 anche un Focus Filter, quindi una modalit\u00e0 Focus \u00abvultyr\u00bb pu\u00f2 silenziare automaticamente i servizi non critici.</p>"),
        ("Ci sono widget e Live Activities?",
         "Su iOS ci sono widget per la schermata Home e la schermata di blocco (per singolo servizio e riepilogo di stato) pi\u00f9 un widget per Control Center. I disservizi attivi vengono fissati nella Dynamic Island come Live Activities. Su watchOS le complicazioni sono disponibili per tutti i quadranti, con la rilevanza di Smart Stack che fa emergere il servizio giusto quando qualcosa va offline.",
         "<p>Su iOS ci sono widget per la schermata Home e la schermata di blocco (per singolo servizio e riepilogo di stato) pi\u00f9 un widget per Control Center. I disservizi attivi vengono fissati nella Dynamic Island come Live Activities. Su watchOS le complicazioni sono disponibili per tutti i quadranti, con la rilevanza di Smart Stack che fa emergere il servizio giusto quando qualcosa va offline.</p>"),
        ("L'app vultyr raccoglie i miei dati?",
         "No. L'app non ha account, non ha tracciamento interno, non ha analytics interni. Tutti i servizi che monitori restano sul tuo dispositivo. Nota: questo sito (vultyr.app) utilizza Google Analytics senza cookie per i conteggi aggregati dei visitatori \u2014 consulta l'Informativa sulla privacy per i dettagli.",
         "<p>No. L'app non ha account, non ha tracciamento interno, non ha analytics interni. Tutti i servizi che monitori restano sul tuo dispositivo. Nota: questo sito (vultyr.app) utilizza Google Analytics senza cookie per i conteggi aggregati dei visitatori \u2014 consulta l'<a href=\"/it/privacy.html\">Informativa sulla privacy</a> per i dettagli.</p>"),
        ("Come sincronizzo i miei servizi tra i dispositivi?",
         "I servizi che monitori si sincronizzano automaticamente tramite iCloud. Anche temi e impostazioni si sincronizzano su tutti i tuoi dispositivi Apple tramite iCloud Key-Value Store.",
         "<p>I servizi che monitori si sincronizzano automaticamente tramite iCloud. Anche temi e impostazioni si sincronizzano su tutti i tuoi dispositivi Apple tramite iCloud Key-Value Store.</p>"),
        ("Quali sono le opzioni di tema?",
         "12 temi: Standard, Terminal, Amber, Blue, Neon, Dracula, Nord, Solarized, Catppuccin, Fossil, Monolith e HAL. Standard e i tre temi retro (Terminal, Amber, Blue) sono inclusi. Fossil, Monolith, HAL e gli altri si sbloccano tramite IAP opzionali a titolo di mancia ($0.99 / $4.99 / $9.99), che contribuiscono anche a finanziare lo sviluppo. I temi si sincronizzano automaticamente su tutti i tuoi dispositivi.",
         "<p>12 temi: Standard, Terminal, Amber, Blue, Neon, Dracula, Nord, Solarized, Catppuccin, Fossil, Monolith e HAL. Standard e i tre temi retro (Terminal, Amber, Blue) sono inclusi. Fossil, Monolith, HAL e gli altri si sbloccano tramite IAP opzionali a titolo di mancia ($0.99 / $4.99 / $9.99), che contribuiscono anche a finanziare lo sviluppo. I temi si sincronizzano automaticamente su tutti i tuoi dispositivi.</p>"),
        ("Posso silenziare le notifiche di un incidente noto?",
         "S\u00ec. Quando visualizzi un servizio con un incidente attivo, puoi silenziare le notifiche per un periodo stabilito, cos\u00ec da non ricevere avvisi ripetuti per qualcosa di cui sei gi\u00e0 al corrente. Puoi silenziare anche con la voce \u2014 \u00abHey Siri, silenzia GitHub per 2 ore\u00bb \u2014 o dall'app Shortcuts.",
         "<p>S\u00ec. Quando visualizzi un servizio con un incidente attivo, puoi silenziare le notifiche per un periodo stabilito, cos\u00ec da non ricevere avvisi ripetuti per qualcosa di cui sei gi\u00e0 al corrente. Puoi silenziare anche con la voce \u2014 \u00abHey Siri, silenzia GitHub per 2 ore\u00bb \u2014 o dall'app Shortcuts.</p>"),
        ("Quali piattaforme sono supportate?",
         "iPhone e iPad (con widget e Live Activities), Mac (con app nella barra dei menu e finestra piena), Apple Watch (con complicazioni e Smart Stack), Apple TV e Apple Vision Pro. L'app \u00e8 gratuita su ogni piattaforma.",
         "<p>iPhone e iPad (con widget e Live Activities), Mac (con app nella barra dei menu e finestra piena), Apple Watch (con complicazioni e Smart Stack), Apple TV e Apple Vision Pro. L'app \u00e8 gratuita su ogni piattaforma.</p>"),
        ("Posso richiedere un nuovo servizio?",
         "S\u00ec! Scrivi a support@vultyr.app indicando il nome del servizio e l'URL della sua pagina di stato.",
         "<p>S\u00ec! Scrivi a <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a> indicando il nome del servizio e l'URL della sua pagina di stato.</p>"),
    ],
},
    "ja": {
    "html_lang": "ja",
    "og_locale": "ja_JP",
    "og_image_alt": "Vultyrアプリアイコン — サービスステータスモニター",
    "devices": "iPhone、iPad、Mac、Apple Watch、Apple TV、Vision Pro",
    "skip_to_main": "メインコンテンツへスキップ",
    "topbar_brand_aria": "Vultyrホーム",
    "nav_primary_aria": "メイン",
    "nav_services": "サービス",
    "nav_support": "サポート",
    "nav_download": "ダウンロード",
    "footer_nav_aria": "フッターナビゲーション",
    "footer_home": "ホーム",
    "footer_services": "サービス",
    "footer_privacy": "プライバシー",
    "footer_support": "サポート",
    "footer_contact": "お問い合わせ",
    "copyright": "\u00a9 2026 Vultyr. All rights reserved.",
    "breadcrumb_aria": "パンくずリスト",
    "breadcrumb_vultyr": "Vultyr",
    "breadcrumb_services": "サービス",
    # services page
    "svcs_title": "Vultyr — 200以上のステータスチェック",
    "svcs_description": "クラウドサービス、開発ツール、コミュニケーション、AIなど200以上のステータスチェック — すべてVultyrが監視します。",
    "svcs_h1_lead": "ステータス",
    "svcs_h1_highlight": "チェック",
    "svcs_subtitle": "Vultyrがクラウドサービス、開発ツール、プラットフォーム向けに実行する200以上のステータスチェック。",
    "svcs_categories_aria": "カテゴリから探す",
    "svc_row_status": "ステータスページ",
    "svc_row_homepage": "ホームページ",
    "svcs_item_list_name": "Vultyrが監視するサービス",
    # service page
    "svcp_title_fmt": "{name}は停止中ですか?{name}のステータスモニター | Vultyr",
    "svcp_description_fmt": "{name}が現在停止しているか確認できます。Vultyrによる{name}のリアルタイムステータスと障害監視。{devices}で無料。",
    "svcp_live_check": "リアルタイムチェック",
    "svcp_view_current_status": "現在のステータスを見る \u2192",
    "svcp_alert_hint_prefix": "即時通知を受け取るには、",
    "svcp_alert_hint_link": "Vultyrをダウンロード",
    "svcp_categories_label": "カテゴリ:",
    "svcp_official_status": "公式ステータスページ",
    "svcp_homepage_fmt": "{name}のホームページ",
    "svcp_faq_heading": "よくある質問",
    "svcp_faq_q1_fmt": "{name}は現在停止していますか?",
    "svcp_faq_a1_fmt": "現在のステータスについては、上記のリンクから{name}の公式ステータスページをご確認ください。Appleの全デバイスで障害通知を即時に受け取りたい場合は、無料のVultyrアプリをダウンロードしてください。",
    "svcp_faq_a1_ld_fmt": "現在のステータスについては、{name}の公式ステータスページ({url})をご確認ください。Appleの全デバイスで障害通知を即時に受け取るには、無料のVultyrアプリをダウンロードしてください。",
    "svcp_faq_q2_fmt": "{name}のステータスを監視するにはどうすればよいですか?",
    "svcp_faq_a2_fmt": "Vultyrは、クラウドサービス、開発ツール、プラットフォーム向けの200以上のステータスチェックの一部として{name}を監視します。{devices}で障害通知を即時に受け取れます — 完全無料。",
    "svcp_faq_a2_ld_fmt": "Vultyrをダウンロード(無料)すると、{name}を200以上のステータスチェックの一部として監視し、{devices}でリアルタイム通知を受け取れます。Vultyrは各チェックを自動で実行し、障害を検出した瞬間に通知します。",
    "svcp_related_heading": "関連サービス",
    "svcp_related_aria": "関連サービス",
    "svcp_cta_heading_fmt": "{name}をすべてのデバイスで監視",
    "svcp_cta_body_fmt": "{name}が停止したら即座に通知を受け取れます。すべてのAppleプラットフォームで無料。",
    "cta_download_vultyr": "Vultyrをダウンロード",
    "cta_download_vultyr_aria": "App StoreでVultyrをダウンロード",
    # category page
    "catp_title_fmt": "{name}のステータスモニター — {count_services} | Vultyr",
    "catp_description_fmt": "{name_lower}の{count_services}のステータスを監視。{sample}などのリアルタイム障害通知。",
    "catp_item_list_name_fmt": "{name}のステータスモニター",
    "catp_subtitle_fmt": "Vultyrが監視する{count_services}",
    "catp_services_aria_fmt": "{name}のサービス",
    "catp_other_heading": "その他のカテゴリ",
    "catp_cta_heading_fmt": "{count_services}すべてを即座に監視",
    "catp_cta_body": "すべてのAppleデバイスでリアルタイムの障害通知を受け取れます。無料。",
    # home page
    "home_title": "Vultyr — AWS、Slack、GitHubなどのサービスステータスモニター",
    "home_description": "停止中?クラウドサービス、開発ツール、プラットフォーム向けの200以上のステータスチェックと即時障害通知。iPhone、iPad、Mac、Apple Watch、Apple TV、Apple Vision Proで無料。",
    "home_og_title": "Vultyr — サービスステータスモニター",
    "home_app_ld_description": "クラウドサービス、開発ツール、プラットフォーム向けの200以上のステータスチェックを即時障害通知とともに監視。",
    "home_hero_tag": "200以上のチェック",
    "home_hero_question": "停止中?",
    "home_hero_answer": "ユーザーより先に気づく。",
    "home_hero_services": "200以上のステータスチェック — AWS、GitHub、Slack、Stripeなど — すべてのAppleデバイスで即時障害通知。",
    "home_appstore_alt": "App Storeからダウンロード",
    "home_appstore_aria": "App StoreでVultyrをダウンロード",
    "home_free_on_prefix": "無料で利用可能",
    "home_screenshots_aria": "アプリのスクリーンショット",
    "home_screenshot_dash_alt": "AWS、GitHub、Slackなどのサービスを監視し「すべて正常」ステータスを表示するVultyrダッシュボード",
    "home_screenshot_settings_alt_fmt": "Terminal、Amber、Dracula、Nordを含む{themes}種類のテーマを備えたVultyrの外観設定",
    "home_screenshot_services_alt_fmt": "クラウド、開発ツール、AIを含む{categories}カテゴリを表示するVultyrサービスブラウザ",
    "home_stats_aria": "主要な数値",
    "home_stats_checks": "チェック",
    "home_stats_categories": "カテゴリ",
    "home_stats_platforms": "プラットフォーム",
    "home_stats_languages": "言語",
    "home_features_heading": "障害に先回りするために必要なものすべて",
    "home_features_sub": "アプリアカウント不要、アプリ内トラッキングなし。ただステータスを。",
    "home_bottom_heading": "スタックを監視する準備はできましたか?",
    "home_bottom_sub": "無料。アプリアカウント不要。どこでも利用可能。",
    "home_bottom_button": "無料でダウンロード",
    "home_bottom_aria": "App StoreでVultyrを無料でダウンロード",
    "home_languages_heading": "17言語で利用可能",
    "home_features": [
        ("chart-bar-regular.svg", "リアルタイムステータスダッシュボード",
         "AWS、GitHub、Cloudflare、Slack、Stripe、Discord、OpenAI、Anthropicなど200以上のサービスを一ヶ所で。ステータスインジケーターはiPhone ProとiPad Proの120Hz ProMotionに同期します。"),
        ("bell-ringing-regular.svg", "スマートアラート",
         "iOSでは各サービスのfavicon付きで障害と復旧を通知。大規模な障害は軽微なインシデントよりも明らかに大きく脉動し、深刻度を一目で把握できます。既知の問題はミュートし、重要なサービスにはスターを付けましょう。"),
        ("microphone-regular.svg", "SiriとShortcuts",
         "Siriに「GitHubを2時間ミュート」や「現在の問題を表示」と話しかけられます。あらゆる操作にApp Intents対応、さらに重要でないサービスを静かにするFocus Filterも。"),
        ("squares-four-regular.svg", "ウィジェットとLive Activities",
         "iOSではホーム画面とロック画面のウィジェット、さらにControl Centerウィジェット。発生中の障害はDynamic Islandに表示されます。"),
        ("watch-regular.svg", "Watchコンプリケーション",
         "重要なサービスを文字盤にピン留めしたり、Smart Stackに発生中の問題を自動表示させたりできます。"),
        ("cloud-check-regular.svg", "Macがハブ — iPhoneがフォールバック",
         "Macは最も信頼性の高いハブです。最速60秒ごとにチェック(15分まで設定可能)し、状態変更をiCloud経由でiPhone、iPad、Watch、Vision Proにブロードキャストします。Macがオンラインになければ、iPhoneがフォールバックパブリッシャーとして代わりに、ほかのデバイスにアラートを届けます。"),
        ("monitor-regular.svg", "アラート信頼性ビュー",
         "アラートが実際に届くかどうかを一目で確認できます — Macのハートビート、バックグラウンド更新の状況、CloudKitプッシュ、各デバイスの最新チェック時刻。"),
        ("devices-regular.svg", "すべてのAppleプラットフォーム",
         "iPhone、iPad、Macのメニューバー、Apple TV、Apple Watch、Vision Pro。サービスは全デバイスで同期されます。"),
        ("lightning-regular.svg", "インシデントの詳細",
         "影響を受けるコンポーネント、発生中のインシデント、予定メンテナンス、タイムラインの更新 — あなたの言語にローカライズ済み。"),
        ("battery-charging-regular.svg", "バッテリーを考慮したポーリング",
         "スマート自動更新はバッテリー、電源状態、熱に適応します。Macでは毎分1回、iPhoneでは5～15分ごと。iPad、Apple Watch、Vision Pro、Apple TVでもバックグラウンド更新が有効です。"),
        ("palette-regular.svg", f"{THEMES_COUNT}種類のテーマ",
         "StandardとレトロなテーマのTerminal、Amber、Blueを同梱。Fossil、Monolith、HALなどはオプションのチップジャーIAPで解放されます。"),
        ("shield-check-regular.svg", "アプリデータはローカルに保存",
         "アプリにはサインアップもアプリ内分析もありません。監視中のサービスはあなたのデバイスに留まります。"),
        ("translate-regular.svg", f"{APP_LANGUAGE_COUNT}言語対応のアプリ",
         "英語、ドイツ語、フランス語、スペイン語、日本語、韓国語、中国語、ポルトガル語、ロシア語など。"),
    ],
    # 404
    "err_title": "ページが見つかりません — Vultyr",
    "err_description": "お探しのページは存在しません。",
    "err_heading": "ページが見つかりません",
    "err_message": "お探しのページは存在しないか、移動された可能性があります。",
    "redirect_moved_fmt": "このページは移動しました。{name}にリダイレクトしています…",
    "err_popular_heading": "人気のサービス",
    "err_browse_heading": "カテゴリを見る",
    # privacy
    "privacy_title": "プライバシーポリシー",
    "privacy_description": "Vultyrのプライバシーポリシー。アプリは個人データを収集しません。このウェブサイトは集計トラフィックのためにCookieを使用しないGoogle Analyticsを利用します。",
    "privacy_last_updated": "最終更新日: 2026年4月11日",
    "privacy_sections": [
        ("概要",
         "<p>Vultyr<strong>アプリ</strong>は個人データを一切収集、保存、送信しません。Vultyr<strong>ウェブサイト</strong>(vultyr.app)は集計された訪問者トラフィックを把握するためにCookieを使用しないGoogle Analyticsを利用します。以下、両方について詳しく説明します。</p>"),
        ("アプリ — データ収集",
         "<p>vultyrアプリは個人情報を一切収集しません。アカウントは不要で、サードパーティの分析やトラッキングSDKは含まれておらず、当社が運営するサーバーにデータを送信することもありません。</p>"),
        ("アプリ — ネットワークリクエスト",
         "<p>アプリはサービスのステータスを確認するため、公開されているステータスページAPI(Statuspage.io、Apple、Google Cloudなど)に直接HTTPSリクエストを送信します。これらのリクエストはお使いのデバイスからサービスの公開APIに直接送信され、当社が運営するサーバーを経由することはありません。</p>"),
        ("アプリ — データ保存",
         "<p>すべてのデータはAppleのSwiftDataフレームワークを使ってお使いのデバイス上にローカル保存されます。iCloud同期を有効にすると、監視中のサービスのリストはAppleのiCloud Key-Value Store経由で同期され、Appleのプライバシーポリシーの適用を受けます。当社はこのデータを一切閲覧しません。</p>"),
        ("アプリ — クロスデバイスアラート",
         "<p>クロスデバイスアラートを有効にすると、ステータスの変化はAppleのiCloud Key-Value Store経由でお使いのデバイス間で共有されます。Macがステータスの変化を検出すると、軽量なシグナルをお使いのiCloudアカウントに書き込みます。他のデバイスはその変化を検知し、それぞれローカルでチェックを実行します。サードパーティサーバーは関与せず、すべての通信はAppleのiCloudインフラストラクチャを経由します。この機能はどのデバイスからでも切り替えられます。</p>"),
        ("アプリ — ファビコン",
         "<p>サービスのファビコンはGoogleの公開ファビコンサービスから取得され、お使いのデバイスにローカルキャッシュされます。</p>"),
        ("ウェブサイト — 分析",
         "<p>このウェブサイト(vultyr.app)は、集計ページビューを計測するためにCookieを使用せずIPを匿名化したモードでGoogle Analytics 4を利用します。具体的には、gtag.jsを<code>anonymize_ip: true</code>、<code>client_storage: 'none'</code>、<code>allow_google_signals: false</code>、<code>allow_ad_personalization_signals: false</code>で設定しています。これにより<code>_ga</code>Cookieは設定されず、IPアドレスは保存前に切り詰められ、広告識別子は収集されません。vultyrアプリ自体には分析機能は含まれていません。</p>"),
        ("ウェブサイト — サードパーティドメイン",
         "<p>vultyr.appを読み込むと、以下のサードパーティドメインと通信します:</p>\n    <ul>\n        <li><strong>www.googletagmanager.com</strong> — gtag.jsスクリプトを読み込みます</li>\n        <li><strong>www.google-analytics.com</strong> / <strong>*.analytics.google.com</strong> — 匿名化されたページビュービーコンを受信します</li>\n        <li><strong>www.google.com/g/collect</strong> — 同じ匿名化ページビュービーコンを受信します(Google Analytics 4のフォールバック収集エンドポイント)</li>\n    </ul>\n    <p>Google Fontsは使用せず(Audiowideフォントはvultyr.appでセルフホストされています)、ウェブサイト自体の画像にサードパーティのファビコンサービスは使用していません。</p>"),
        ("アプリ — サードパーティサービス",
         "<p>vultyrアプリはサードパーティの分析、広告、トラッキングサービスとは一切連携しません。外部リクエストは公開ステータスAPIとGoogleのファビコンサービスのみです。</p>"),
        ("子どものプライバシー",
         "<p>vultyrアプリは誰からもデータを収集しません。13歳未満の子どもも例外ではありません。ウェブサイトは匿名化された集計訪問者数のみを記録します。</p>"),
        ("変更",
         "<p>このポリシーが変更された場合、上記の日付を更新します。</p>"),
        ("お問い合わせ",
         "<p>ご質問があれば <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a> までメールをお送りください。</p>"),
    ],
    # support
    "support_title": "サポート",
    "support_description": "iPhone、iPad、Mac、Apple Watch、Apple TV、Apple Vision Pro向けサービスステータスモニター Vultyr のヘルプ。よくある質問、お問い合わせ、トラブルシューティング。",
    "support_contact_heading": "お問い合わせ",
    "support_contact_html": "<p>バグ報告、機能リクエスト、ご質問はこちらまで:<br>\n    <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a></p>",
    "support_faq_heading": "よくある質問",
    "support_faqs": [
        ("vultyrはどのくらいの頻度でサービスのステータスを確認しますか?",
         "Macでは、電源接続時に最短60秒ごと。iPhoneでは5分、10分、または15分ごと(設定可能)に加え、条件が許せば定期的にバックグラウンドチェックを実行します。Apple Watchでは15分ごと、Apple TVでは5分ごと。ポーリングはバッテリー残量、電源状態、温度条件に応じて自動で調整されます。",
         "<p>Macでは、電源接続時に最短60秒ごと。iPhoneでは5分、10分、または15分ごと(設定可能)に加え、条件が許せば定期的にバックグラウンドチェックを実行します。Apple Watchでは15分ごと、Apple TVでは5分ごと。ポーリングはバッテリー残量、電源状態、温度条件に応じて自動で調整されます。</p>"),
        ("クロスデバイスアラートはどのように動作しますか?",
         "Macアプリがハブです。メニューバーまたはフルウィンドウで起動したままにしておけば、最速60秒ごとにポーリング(15分まで設定可能)します。ステータスの変化を検出すると、軽量なシグナルをiCloud Key-Value Storeに書き込み、iPhone、iPad、Watch、Apple TV、Vision Proがその変化を受け取ってそれぞれローカルでチェックを実行します。鍵もトークンもセットアップも不要 — どのデバイスの設定でも「クロスデバイスアラート」を有効にするだけです。Macをハブにしない場合、アラートはiOSのバックグラウンド実行に依存するため遅延または欠落します。",
         "<p>Macアプリがハブです。メニューバーまたはフルウィンドウで起動したままにしておけば、最速60秒ごとにポーリング(15分まで設定可能)します。ステータスの変化を検出すると、軽量なシグナルをiCloud Key-Value Storeに書き込み、iPhone、iPad、Watch、Apple TV、Vision Proがその変化を受け取ってそれぞれローカルでチェックを実行します。鍵もトークンもセットアップも不要 — どのデバイスの設定でも「クロスデバイスアラート」を有効にするだけです。Macをハブにしない場合、アラートはiOSのバックグラウンド実行に依存するため遅延または欠落します。</p>"),
        ("確実なアラートのためにMacアプリは必要ですか?",
         "はい — 強くお勧めします。iOSはバックグラウンド実行を制限するため、iPhoneとiPadは5〜15分ごと(設定可能)にしかチェックできず、バッテリー残量の低下、低電力モード、通信状況の悪化でさらに遅延することがあります。Macアプリは電源接続時に最速最速60秒ごとにポーリング(15分まで設定可能)し(15分まで設定可能)、iCloud経由で他のデバイスにステータスの変化をブロードキャストします。VultyrをMacで動かしていない場合、iOS、watchOS、tvOSのアラートは動作しますが大幅に遅延したり欠落したりする可能性があります。リアルタイム監視のためにはMacアプリを起動したままにしておいてください — メニューバーに小さく常駐し、これがVultyr本来の使い方です。",
         "<p>はい — 強くお勧めします。iOSはバックグラウンド実行を制限するため、iPhoneとiPadは5〜15分ごと(設定可能)にしかチェックできず、バッテリー残量の低下、低電力モード、通信状況の悪化でさらに遅延することがあります。Macアプリは電源接続時に最速最速60秒ごとにポーリング(15分まで設定可能)し(15分まで設定可能)、iCloud経由で他のデバイスにステータスの変化をブロードキャストします。VultyrをMacで動かしていない場合、iOS、watchOS、tvOSのアラートは動作しますが大幅に遅延したり欠落したりする可能性があります。リアルタイム監視のためにはMacアプリを起動したままにしておいてください — メニューバーに小さく常駐し、これがVultyr本来の使い方です。</p>"),
        ("vultyrはSiriやShortcutsと連携しますか?",
         "はい。ビルトインのApp Intentsによって、「Hey Siri、GitHubを2時間ミュート」「Stripeのステータスをチェック」「現在の問題を表示」と話しかけられます。同じ操作をShortcutsアプリにも組み込めます。Focus Filterもあり、「vultyr Focus」モードは重要でないサービスを自動で静かにします。",
         "<p>はい。ビルトインのApp Intentsによって、「Hey Siri、GitHubを2時間ミュート」「Stripeのステータスをチェック」「現在の問題を表示」と話しかけられます。同じ操作をShortcutsアプリにも組み込めます。Focus Filterもあり、「vultyr Focus」モードは重要でないサービスを自動で静かにします。</p>"),
        ("ウィジェットやLive Activitiesはありますか?",
         "iOSにはホーム画面とロック画面のウィジェット(単一サービスおよびステータスサマリー)があり、Control Centerウィジェットも備えています。発生中の障害はLive ActivitiesとしてDynamic Islandに表示されます。watchOSではすべての文字盤でコンプリケーションが利用可能で、Smart Stack対応により必要なサービスが障害時に自動で表示されます。",
         "<p>iOSにはホーム画面とロック画面のウィジェット(単一サービスおよびステータスサマリー)があり、Control Centerウィジェットも備えています。発生中の障害はLive ActivitiesとしてDynamic Islandに表示されます。watchOSではすべての文字盤でコンプリケーションが利用可能で、Smart Stack対応により必要なサービスが障害時に自動で表示されます。</p>"),
        ("vultyrアプリは私のデータを収集しますか?",
         "いいえ。アプリにはアカウントもアプリ内トラッキングもアプリ内分析もありません。監視中のサービスはすべてお使いのデバイスに留まります。注意: このウェブサイト(vultyr.app)は集計訪問者数のためにCookieを使用しないGoogle Analyticsを利用しています — 詳細はプライバシーポリシーをご覧ください。",
         "<p>いいえ。アプリにはアカウントもアプリ内トラッキングもアプリ内分析もありません。監視中のサービスはすべてお使いのデバイスに留まります。注意: このウェブサイト(vultyr.app)は集計訪問者数のためにCookieを使用しないGoogle Analyticsを利用しています — 詳細は<a href=\"/privacy.html\">プライバシーポリシー</a>をご覧ください。</p>"),
        ("デバイス間でサービスを同期するにはどうすればよいですか?",
         "監視中のサービスはiCloud経由で自動的に同期されます。テーマや設定もiCloud Key-Value Store経由ですべてのAppleデバイスで同期されます。",
         "<p>監視中のサービスはiCloud経由で自動的に同期されます。テーマや設定もiCloud Key-Value Store経由ですべてのAppleデバイスで同期されます。</p>"),
        ("テーマの選択肢は何がありますか?",
         "12種類のテーマ: Standard、Terminal、Amber、Blue、Neon、Dracula、Nord、Solarized、Catppuccin、Fossil、Monolith、HAL。Standardと3つのレトロテーマ(Terminal、Amber、Blue)は同梱されています。Fossil、Monolith、HALなどはオプションのチップジャーIAP(0.99ドル / 4.99ドル / 9.99ドル)で解放され、これが開発支援にもなります。テーマはすべてのデバイスで自動的に同期されます。",
         "<p>12種類のテーマ: Standard、Terminal、Amber、Blue、Neon、Dracula、Nord、Solarized、Catppuccin、Fossil、Monolith、HAL。Standardと3つのレトロテーマ(Terminal、Amber、Blue)は同梱されています。Fossil、Monolith、HALなどはオプションのチップジャーIAP(0.99ドル / 4.99ドル / 9.99ドル)で解放され、これが開発支援にもなります。テーマはすべてのデバイスで自動的に同期されます。</p>"),
        ("既知のインシデントの通知をミュートできますか?",
         "はい。発生中のインシデントがあるサービスを表示しているときに、一定期間通知をミュートできるので、すでに知っている事象について繰り返しアラートを受け取ることはありません。音声でもミュートできます — 「Hey Siri、GitHubを2時間ミュート」 — Shortcutsアプリからも可能です。",
         "<p>はい。発生中のインシデントがあるサービスを表示しているときに、一定期間通知をミュートできるので、すでに知っている事象について繰り返しアラートを受け取ることはありません。音声でもミュートできます — 「Hey Siri、GitHubを2時間ミュート」 — Shortcutsアプリからも可能です。</p>"),
        ("サポートされているプラットフォームは何ですか?",
         "iPhoneとiPad(ウィジェットとLive Activities対応)、Mac(メニューバーアプリとフルウィンドウ)、Apple Watch(コンプリケーションとSmart Stack対応)、Apple TV、Apple Vision Pro。アプリはすべてのプラットフォームで無料でダウンロードできます。",
         "<p>iPhoneとiPad(ウィジェットとLive Activities対応)、Mac(メニューバーアプリとフルウィンドウ)、Apple Watch(コンプリケーションとSmart Stack対応)、Apple TV、Apple Vision Pro。アプリはすべてのプラットフォームで無料でダウンロードできます。</p>"),
        ("新しいサービスをリクエストできますか?",
         "はい! サービス名とそのステータスページのURLを添えて support@vultyr.app までメールをお送りください。",
         "<p>はい! サービス名とそのステータスページのURLを添えて <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a> までメールをお送りください。</p>"),
    ],
},
    "ko": {
    "html_lang": "ko",
    "og_locale": "ko_KR",
    "og_image_alt": "Vultyr 앱 아이콘 — 서비스 상태 모니터",
    "devices": "iPhone, iPad, Mac, Apple Watch, Apple TV 및 Vision Pro",
    "skip_to_main": "본문으로 건너뛰기",
    "topbar_brand_aria": "Vultyr 홈",
    "nav_primary_aria": "기본",
    "nav_services": "서비스",
    "nav_support": "지원",
    "nav_download": "다운로드",
    "footer_nav_aria": "푸터 탐색",
    "footer_home": "홈",
    "footer_services": "서비스",
    "footer_privacy": "개인정보 처리방침",
    "footer_support": "지원",
    "footer_contact": "문의",
    "copyright": "© 2026 Vultyr. 모든 권리 보유.",
    "breadcrumb_aria": "경로 탐색",
    "breadcrumb_vultyr": "Vultyr",
    "breadcrumb_services": "서비스",
    # services page
    "svcs_title": "Vultyr — 200개 이상의 상태 점검",
    "svcs_description": "클라우드 서비스, 개발 도구, 커뮤니케이션, AI 등 200개 이상의 상태 점검을 Vultyr가 모두 모니터링합니다.",
    "svcs_h1_lead": "상태",
    "svcs_h1_highlight": "점검",
    "svcs_subtitle": "vultyr가 클라우드 서비스, 개발 도구, 플랫폼에서 실행하는 200개 이상의 상태 점검.",
    "svcs_categories_aria": "카테고리별 찾아보기",
    "svc_row_status": "상태 페이지",
    "svc_row_homepage": "홈페이지",
    "svcs_item_list_name": "Vultyr가 모니터링하는 서비스",
    # service page
    "svcp_title_fmt": "{name} 장애 발생? {name} 상태 모니터 | Vultyr",
    "svcp_description_fmt": "{name}의 현재 장애 여부를 확인하세요. {name}의 실시간 상태 업데이트 및 장애 모니터링을 Vultyr로 이용하세요. {devices}에서 무료로 사용 가능합니다.",
    "svcp_live_check": "실시간 점검",
    "svcp_view_current_status": "현재 상태 보기 →",
    "svcp_alert_hint_prefix": "즉시 알림을 받으려면 ",
    "svcp_alert_hint_link": "Vultyr 다운로드",
    "svcp_categories_label": "카테고리:",
    "svcp_official_status": "공식 상태 페이지",
    "svcp_homepage_fmt": "{name} 홈페이지",
    "svcp_faq_heading": "자주 묻는 질문",
    "svcp_faq_q1_fmt": "{name}이(가) 지금 장애 상태인가요?",
    "svcp_faq_a1_fmt": "현재 상태를 확인하려면 위에 링크된 공식 {name} 상태 페이지를 확인하십시오. 모든 Apple 기기에서 장애 즉시 알림을 받으며 지속적으로 모니터링하려면 무료 Vultyr 앱을 다운로드하십시오.",
    "svcp_faq_a1_ld_fmt": "현재 상태를 확인하려면 {url}의 공식 {name} 상태 페이지를 방문하십시오. 모든 Apple 기기에서 장애 즉시 알림을 받으려면 무료 Vultyr 앱을 다운로드하십시오.",
    "svcp_faq_q2_fmt": "{name} 상태를 어떻게 모니터링할 수 있나요?",
    "svcp_faq_a2_fmt": "Vultyr는 클라우드 서비스, 개발 도구, 플랫폼 전반의 200개 이상의 상태 점검의 일부로 {name}을(를) 모니터링합니다. {devices}에서 장애 즉시 알림을 받아보세요 — 완전 무료입니다.",
    "svcp_faq_a2_ld_fmt": "Vultyr를 무료로 다운로드하여 {devices}에서 실시간 알림과 함께 {name}을(를) 200개 이상의 상태 점검의 일부로 모니터링하십시오. Vultyr는 각 점검을 자동으로 실행하고 장애가 감지되는 순간 알려드립니다.",
    "svcp_related_heading": "관련 서비스",
    "svcp_related_aria": "관련 서비스",
    "svcp_cta_heading_fmt": "모든 기기에서 {name} 모니터링",
    "svcp_cta_body_fmt": "{name}에 장애가 발생하면 즉시 알림을 받으세요. 모든 Apple 플랫폼에서 무료로 이용 가능합니다.",
    "cta_download_vultyr": "Vultyr 다운로드",
    "cta_download_vultyr_aria": "App Store에서 Vultyr 다운로드",
    # category page
    "catp_title_fmt": "{name} 상태 모니터 — {count_services} | Vultyr",
    "catp_description_fmt": "{name_lower}의 {count_services} 상태를 모니터링하세요. {sample} 등에 대한 실시간 장애 알림을 제공합니다.",
    "catp_item_list_name_fmt": "{name} 상태 모니터",
    "catp_subtitle_fmt": "Vultyr가 모니터링하는 {count_services}",
    "catp_services_aria_fmt": "{name} 서비스",
    "catp_other_heading": "다른 카테고리",
    "catp_cta_heading_fmt": "{count_services} 모두를 즉시 모니터링",
    "catp_cta_body": "모든 Apple 기기에서 실시간 장애 알림을 받으세요. 무료입니다.",
    # home page
    "home_title": "Vultyr — AWS, Slack, GitHub 등을 위한 서비스 상태 모니터",
    "home_description": "장애가 발생했나요? 클라우드 서비스, 개발 도구, 플랫폼 전반의 200개 이상의 상태 점검과 즉시 장애 알림. iPhone, iPad, Mac, Apple Watch, Apple TV 및 Apple Vision Pro에서 무료로 이용하세요.",
    "home_og_title": "Vultyr — 서비스 상태 모니터",
    "home_app_ld_description": "클라우드 서비스, 개발 도구, 플랫폼 전반의 200개 이상의 상태 점검을 즉시 장애 알림과 함께 모니터링하세요.",
    "home_hero_tag": "200개 이상의 점검",
    "home_hero_question": "장애가 발생했나요?",
    "home_hero_answer": "사용자보다 먼저 알아차리세요.",
    "home_hero_services": "200개 이상의 상태 점검 — AWS, GitHub, Slack, Stripe 등 — 모든 Apple 기기에서 즉시 장애 알림을 받을 수 있습니다.",
    "home_appstore_alt": "App Store에서 다운로드",
    "home_appstore_aria": "App Store에서 Vultyr 다운로드",
    "home_free_on_prefix": "무료로 이용",
    "home_screenshots_aria": "앱 스크린샷",
    "home_screenshot_dash_alt": "AWS, GitHub, Slack 등을 모니터링하며 모두 정상 상태를 표시하는 Vultyr 대시보드",
    "home_screenshot_settings_alt_fmt": "Terminal, Amber, Dracula, Nord를 포함한 {themes}개 테마가 있는 Vultyr 외관 설정",
    "home_screenshot_services_alt_fmt": "Cloud, Dev Tools, AI를 포함한 {categories}개 카테고리가 있는 Vultyr 서비스 브라우저",
    "home_stats_aria": "주요 수치",
    "home_stats_checks": "점검",
    "home_stats_categories": "카테고리",
    "home_stats_platforms": "플랫폼",
    "home_stats_languages": "언어",
    "home_features_heading": "장애를 한발 앞서 파악하기 위한 모든 기능",
    "home_features_sub": "앱 계정도, 인앱 추적도 없습니다. 오직 상태만.",
    "home_bottom_heading": "스택을 모니터링할 준비가 되셨나요?",
    "home_bottom_sub": "무료. 앱 계정 불필요. 어디서나 이용 가능.",
    "home_bottom_button": "무료 다운로드",
    "home_bottom_aria": "App Store에서 Vultyr 무료 다운로드",
    "home_languages_heading": "17개 언어로 이용 가능",
    "home_features": [
        ("chart-bar-regular.svg", "실시간 상태 대시보드",
         "AWS, GitHub, Cloudflare, Slack, Stripe, Discord, OpenAI, Anthropic 등 200개 이상의 서비스를 한곳에서 확인하세요. 상태 표시등은 iPhone Pro와 iPad Pro의 120Hz ProMotion에 동기화됩니다."),
        ("bell-ringing-regular.svg", "스마트 알림",
         "iOS에서 각 서비스의 favicon과 함께 장애 및 복구 알림을 받습니다. 대규모 장애는 소규모 사고보다 눈에 띄게 더 크게 맥동하여 심각도를 한눈에 알 수 있습니다. 이미 알고 있는 문제는 음소거하고 중요한 서비스는 별표로 표시하세요."),
        ("microphone-regular.svg",
         "Siri 및 Shortcuts",
         "Siri에게 「GitHub을 2시간 동안 음소거해」 또는 「현재 문제를 보여줘」라고 말하세요. 모든 작업에 대한 App Intents와 중요하지 않은 서비스를 조용히 하는 Focus Filter를 제공합니다."),
        ("squares-four-regular.svg",
         "위젯 및 Live Activities",
         "iOS의 홈 화면 및 잠금 화면 위젯과 Control Center 위젯을 제공합니다. 활성 장애는 Dynamic Island에 고정됩니다."),
        ("watch-regular.svg",
         "Watch 컴플리케이션",
         "중요한 서비스를 시계 페이스에 고정하거나 Smart Stack이 활성 문제를 자동으로 표시하도록 맡기세요."),
        ("cloud-check-regular.svg", "Mac 허브 — iPhone 폴백",
         "Mac은 가장 안정적인 허브입니다. 최단 60초마다 상태를 폴링(15분까지 설정 가능)하고 iCloud를 통해 iPhone, iPad, Watch, Vision Pro에 상태 변경을 전파합니다. Mac이 오프라인이면 iPhone이 폴백 퍼블리셔로 나서서 다른 기기들이 여전히 알림을 받도록 합니다."),
        ("monitor-regular.svg", "알림 신뢰성 보기",
         "알림이 실제로 도착할지 한눈에 확인하세요 — Mac 하트비트, 백그라운드 새로고침 상태, CloudKit 푸시, 각 기기의 마지막 확인 시간을 표시합니다."),
        ("devices-regular.svg",
         "모든 Apple 플랫폼",
         "iPhone, iPad, Mac 메뉴 막대, Apple TV, Apple Watch, Vision Pro. 서비스가 모든 기기에서 동기화됩니다."),
        ("lightning-regular.svg",
         "장애 상세 정보",
         "영향을 받은 구성 요소, 활성 장애, 예정된 점검, 타임라인 업데이트 — 모두 사용자의 언어로 현지화됩니다."),
        ("battery-charging-regular.svg", "배터리 인식 폴링",
         "스마트 자동 새로고침이 배터리, 전원 상태, 열에 적응합니다. Mac에서는 1분마다, iPhone에서는 5–15분, iPad, Apple Watch, Vision Pro, Apple TV에서는 백그라운드 새로고침이 지원됩니다."),
        ("palette-regular.svg", f"{THEMES_COUNT}개 테마",
         "Standard와 세 가지 레트로 테마가 기본 포함되어 있습니다. Fossil, Monolith, HAL 등은 선택적인 팁 자 인앱 구매를 통해 잠금 해제됩니다."),
        ("shield-check-regular.svg",
         "앱 데이터는 기기에 남습니다",
         "앱에는 가입이 없고 인앱 분석도 없습니다. 모니터링 중인 서비스는 사용자 기기에 남아있습니다."),
        ("translate-regular.svg", f"{APP_LANGUAGE_COUNT}개 앱 언어",
         "영어, 독일어, 프랑스어, 스페인어, 일본어, 한국어, 중국어, 포르투갈어, 러시아어 등."),
    ],
    # 404
    "err_title": "페이지를 찾을 수 없음 — Vultyr",
    "err_description": "찾고 계신 페이지가 존재하지 않습니다.",
    "err_heading": "페이지를 찾을 수 없음",
    "err_message": "찾고 계신 페이지가 존재하지 않거나 이동되었습니다.",
    "redirect_moved_fmt": "이 페이지는 이동되었습니다. {name}(으)로 리디렉션 중…",
    "err_popular_heading": "인기 서비스",
    "err_browse_heading": "카테고리 둘러보기",
    # privacy
    "privacy_title": "개인정보 처리방침",
    "privacy_description": "Vultyr 개인정보 처리방침. 앱은 개인 데이터를 수집하지 않습니다. 웹사이트는 집계 방문자 트래픽 분석을 위해 쿠키 없는 Google Analytics를 사용합니다.",
    "privacy_last_updated": "최종 업데이트: 2026년 4월 11일",
    "privacy_sections": [
        ("요약",
         "<p>Vultyr <strong>앱</strong>은 개인 데이터를 수집, 저장, 전송하지 않습니다. Vultyr <strong>웹사이트</strong>(vultyr.app)는 집계 방문자 트래픽을 이해하기 위해 쿠키 없는 Google Analytics를 사용합니다. 본 페이지에서 두 가지를 상세히 설명합니다.</p>"),
        ("앱 — 데이터 수집",
         "<p>vultyr 앱은 어떠한 개인 정보도 수집하지 않습니다. 계정이 필요 없고, 타사 분석 또는 추적 SDK를 포함하지 않으며, 저희가 운영하는 서버로 정보를 전송하지 않습니다.</p>"),
        ("앱 — 네트워크 요청",
         "<p>앱은 서비스 상태를 확인하기 위해 공개 상태 페이지 API(Statuspage.io, Apple, Google Cloud 등)로 직접 HTTPS 요청을 보냅니다. 이 요청은 사용자 기기에서 서비스의 공개 API로 직접 전송되며 — 저희가 운영하는 서버를 거치지 않습니다.</p>"),
        ("앱 — 데이터 저장",
         "<p>모든 데이터는 Apple의 SwiftData 프레임워크를 사용하여 사용자 기기에 로컬로 저장됩니다. iCloud 동기화를 활성화하면 모니터링 중인 서비스 목록이 Apple의 iCloud Key-Value Store를 통해 동기화되며, 이는 Apple의 개인정보 처리방침의 적용을 받습니다. 저희는 이 데이터를 절대 볼 수 없습니다.</p>"),
        ("앱 — 기기 간 알림",
         "<p>기기 간 알림을 활성화하면 Apple의 iCloud Key-Value Store를 통해 기기 간에 상태 변경이 공유됩니다. Mac이 상태 변경을 감지하면 사용자의 iCloud 계정에 경량 신호를 기록합니다. 다른 기기는 이 변경을 감지하고 자체적인 로컬 점검을 실행합니다. 타사 서버는 관여하지 않으며 — 모든 통신은 Apple의 iCloud 인프라를 통해 이루어집니다. 이 기능은 어느 기기에서나 설정을 통해 켜고 끌 수 있습니다.</p>"),
        ("앱 — 파비콘",
         "<p>서비스 파비콘은 Google의 공개 파비콘 서비스에서 가져와 사용자 기기에 로컬로 캐시됩니다.</p>"),
        ("웹사이트 — 분석",
         "<p>본 웹사이트(vultyr.app)는 쿠키 없는 IP 익명화 모드에서 Google Analytics 4를 사용하여 집계 페이지 조회수를 카운트합니다. 구체적으로 gtag.js를 <code>anonymize_ip: true</code>, <code>client_storage: 'none'</code>, <code>allow_google_signals: false</code>, <code>allow_ad_personalization_signals: false</code>로 구성합니다. 이는 <code>_ga</code> 쿠키가 설정되지 않고, IP가 저장 전에 잘리며, 광고 식별자가 수집되지 않음을 의미합니다. vultyr 앱 자체에는 어떠한 분석도 포함되어 있지 않습니다.</p>"),
        ("웹사이트 — 타사 도메인",
         "<p>vultyr.app을 로드하면 다음 타사 도메인에 연결됩니다:</p>\n    <ul>\n        <li><strong>www.googletagmanager.com</strong> — gtag.js 스크립트를 로드합니다</li>\n        <li><strong>www.google-analytics.com</strong> / <strong>*.analytics.google.com</strong> — 익명화된 페이지 조회 비콘을 수신합니다</li>\n        <li><strong>www.google.com/g/collect</strong> — 동일한 익명화된 페이지 조회 비콘을 수신합니다(Google Analytics 4 폴백 수집 엔드포인트)</li>\n    </ul>\n    <p>Google Fonts는 로드하지 않으며(Audiowide 글꼴은 vultyr.app에 자체 호스팅됨), 웹사이트 자체 이미지를 위한 타사 파비콘 서비스도 사용하지 않습니다.</p>"),
        ("앱 — 타사 서비스",
         "<p>vultyr 앱은 어떠한 타사 분석, 광고 또는 추적 서비스와도 통합되지 않습니다. 유일한 외부 요청은 공개 상태 API와 Google의 파비콘 서비스에 대한 것입니다.</p>"),
        ("아동 개인정보",
         "<p>vultyr 앱은 13세 미만 아동을 포함하여 누구에게서도 데이터를 수집하지 않습니다. 웹사이트는 익명화된 집계 방문자 수만 기록합니다.</p>"),
        ("변경 사항",
         "<p>이 방침이 변경되는 경우 상단의 날짜를 업데이트합니다.</p>"),
        ("문의",
         "<p>질문이 있으신가요? <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a>으로 이메일을 보내주세요.</p>"),
    ],
    # support
    "support_title": "지원",
    "support_description": "iPhone, iPad, Mac, Apple Watch, Apple TV 및 Apple Vision Pro를 위한 서비스 상태 모니터 Vultyr에 대한 도움말. 자주 묻는 질문, 연락처 및 문제 해결.",
    "support_contact_heading": "문의",
    "support_contact_html": "<p>버그 리포트, 기능 요청 또는 질문:<br>\n    <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a></p>",
    "support_faq_heading": "자주 묻는 질문",
    "support_faqs": [
        ("vultyr는 서비스 상태를 얼마나 자주 점검하나요?",
         "Mac에서는 전원 연결 시 최단 60초마다 점검합니다(15분까지 설정 가능). iPhone에서는 5, 10 또는 15분마다(설정 가능)이며, 조건이 허용될 때 주기적인 백그라운드 점검도 수행됩니다. Apple Watch에서는 15분마다, Apple TV에서는 5분마다 점검합니다. 폴링은 배터리 수준, 전원 상태, 발열 조건에 따라 자동으로 적응합니다.",
         "<p>Mac에서는 전원 연결 시 최단 60초마다 점검합니다(15분까지 설정 가능). iPhone에서는 5, 10 또는 15분마다(설정 가능)이며, 조건이 허용될 때 주기적인 백그라운드 점검도 수행됩니다. Apple Watch에서는 15분마다, Apple TV에서는 5분마다 점검합니다. 폴링은 배터리 수준, 전원 상태, 발열 조건에 따라 자동으로 적응합니다.</p>"),
        ("기기 간 알림은 어떻게 작동하나요?",
         "Mac 앱이 허브입니다. Mac 앱을 실행 상태로 유지(메뉴 막대 또는 전체 창)하면 최단 60초마다 폴링합니다(15분까지 설정 가능). 상태 변경이 감지되면 iCloud Key-Value Store에 경량 신호를 기록하며, iPhone, iPad, Watch, Apple TV, Vision Pro가 변경을 감지하고 자체적인 로컬 점검을 실행합니다. 키도, 토큰도, 설정도 필요 없습니다 — 어느 기기에서나 설정에서 「기기 간 알림」을 켜기만 하면 됩니다. Mac이 허브 역할을 하지 않으면 알림은 iOS 백그라운드 실행에 의존하며 지연되거나 누락됩니다.",
         "<p>Mac 앱이 허브입니다. Mac 앱을 실행 상태로 유지(메뉴 막대 또는 전체 창)하면 최단 60초마다 폴링합니다(15분까지 설정 가능). 상태 변경이 감지되면 iCloud Key-Value Store에 경량 신호를 기록하며, iPhone, iPad, Watch, Apple TV, Vision Pro가 변경을 감지하고 자체적인 로컬 점검을 실행합니다. 키도, 토큰도, 설정도 필요 없습니다 — 어느 기기에서나 설정에서 「기기 간 알림」을 켜기만 하면 됩니다. Mac이 허브 역할을 하지 않으면 알림은 iOS 백그라운드 실행에 의존하며 지연되거나 누락됩니다.</p>"),
        ("안정적인 알림에 Mac 앱이 필요한가요?",
         "네 — 강력히 권장합니다. iOS는 백그라운드 실행을 제한하므로 iPhone과 iPad는 5~15분마다(설정 가능)만 점검할 수 있으며, 낮은 배터리, 저전력 모드 또는 연결 상태가 나쁠 때 추가로 지연될 수 있습니다. Mac 앱은 전원 연결 시 최단 60초마다 폴링하며(15분까지 설정 가능) iCloud를 통해 다른 기기에 상태 변경을 방송합니다. Vultyr를 실행하는 Mac이 없으면 iOS, watchOS, tvOS 알림은 여전히 작동하지만 상당히 지연되거나 누락될 수 있습니다. 실시간 모니터링을 위해 Mac 앱을 실행 상태로 유지하세요 — 메뉴 막대에서 매우 작으며 이것이 Vultyr가 사용되도록 의도된 방식입니다.",
         "<p>네 — 강력히 권장합니다. iOS는 백그라운드 실행을 제한하므로 iPhone과 iPad는 5~15분마다(설정 가능)만 점검할 수 있으며, 낮은 배터리, 저전력 모드 또는 연결 상태가 나쁠 때 추가로 지연될 수 있습니다. Mac 앱은 전원 연결 시 최단 60초마다 폴링하며(15분까지 설정 가능) iCloud를 통해 다른 기기에 상태 변경을 방송합니다. Vultyr를 실행하는 Mac이 없으면 iOS, watchOS, tvOS 알림은 여전히 작동하지만 상당히 지연되거나 누락될 수 있습니다. 실시간 모니터링을 위해 Mac 앱을 실행 상태로 유지하세요 — 메뉴 막대에서 매우 작으며 이것이 Vultyr가 사용되도록 의도된 방식입니다.</p>"),
        ("vultyr는 Siri와 Shortcuts와 함께 작동하나요?",
         "네. 내장된 App Intents를 통해 「Siri야, GitHub을 2시간 동안 음소거해」, 「Stripe 상태를 확인해」 또는 「현재 문제를 보여줘」라고 말할 수 있으며, 이러한 동일한 작업을 Shortcuts 앱에 연결할 수 있습니다. 「vultyr Focus」 모드가 중요하지 않은 서비스를 자동으로 조용히 할 수 있도록 Focus Filter도 제공됩니다.",
         "<p>네. 내장된 App Intents를 통해 「Siri야, GitHub을 2시간 동안 음소거해」, 「Stripe 상태를 확인해」 또는 「현재 문제를 보여줘」라고 말할 수 있으며, 이러한 동일한 작업을 Shortcuts 앱에 연결할 수 있습니다. 「vultyr Focus」 모드가 중요하지 않은 서비스를 자동으로 조용히 할 수 있도록 Focus Filter도 제공됩니다.</p>"),
        ("위젯과 Live Activities가 있나요?",
         "iOS에는 홈 화면 및 잠금 화면 위젯(단일 서비스 및 상태 요약)과 Control Center 위젯이 있습니다. 활성 장애는 Live Activities로 Dynamic Island에 고정됩니다. watchOS에는 모든 시계 페이스에서 사용할 수 있는 컴플리케이션이 있으며, Smart Stack 관련성 덕분에 장애가 발생했을 때 적절한 서비스가 자동으로 표시됩니다.",
         "<p>iOS에는 홈 화면 및 잠금 화면 위젯(단일 서비스 및 상태 요약)과 Control Center 위젯이 있습니다. 활성 장애는 Live Activities로 Dynamic Island에 고정됩니다. watchOS에는 모든 시계 페이스에서 사용할 수 있는 컴플리케이션이 있으며, Smart Stack 관련성 덕분에 장애가 발생했을 때 적절한 서비스가 자동으로 표시됩니다.</p>"),
        ("vultyr 앱은 제 데이터를 수집하나요?",
         "아니요. 앱에는 계정도, 인앱 추적도, 인앱 분석도 없습니다. 모니터링 중인 모든 서비스는 사용자 기기에 남아있습니다. 참고: 본 웹사이트(vultyr.app)는 집계 방문자 수를 위해 쿠키 없는 Google Analytics를 사용합니다 — 자세한 내용은 개인정보 처리방침을 참조하세요.",
         "<p>아니요. 앱에는 계정도, 인앱 추적도, 인앱 분석도 없습니다. 모니터링 중인 모든 서비스는 사용자 기기에 남아있습니다. 참고: 본 웹사이트(vultyr.app)는 집계 방문자 수를 위해 쿠키 없는 Google Analytics를 사용합니다 — 자세한 내용은 <a href=\"/ko/privacy.html\">개인정보 처리방침</a>을 참조하세요.</p>"),
        ("기기 간에 서비스를 어떻게 동기화하나요?",
         "모니터링 중인 서비스는 iCloud를 통해 자동으로 동기화됩니다. 테마와 설정도 iCloud Key-Value Store를 통해 모든 Apple 기기 간에 동기화됩니다.",
         "<p>모니터링 중인 서비스는 iCloud를 통해 자동으로 동기화됩니다. 테마와 설정도 iCloud Key-Value Store를 통해 모든 Apple 기기 간에 동기화됩니다.</p>"),
        ("어떤 테마 옵션이 있나요?",
         "12가지 테마: Standard, Terminal, Amber, Blue, Neon, Dracula, Nord, Solarized, Catppuccin, Fossil, Monolith, HAL. Standard와 세 가지 레트로 테마(Terminal, Amber, Blue)가 기본 포함되어 있습니다. Fossil, Monolith, HAL 등은 선택적인 팁 자 인앱 구매($0.99 / $4.99 / $9.99)를 통해 잠금 해제되며, 이는 또한 개발 자금 조달에 도움이 됩니다. 테마는 모든 기기에서 자동으로 동기화됩니다.",
         "<p>12가지 테마: Standard, Terminal, Amber, Blue, Neon, Dracula, Nord, Solarized, Catppuccin, Fossil, Monolith, HAL. Standard와 세 가지 레트로 테마(Terminal, Amber, Blue)가 기본 포함되어 있습니다. Fossil, Monolith, HAL 등은 선택적인 팁 자 인앱 구매($0.99 / $4.99 / $9.99)를 통해 잠금 해제되며, 이는 또한 개발 자금 조달에 도움이 됩니다. 테마는 모든 기기에서 자동으로 동기화됩니다.</p>"),
        ("이미 알고 있는 장애의 알림을 음소거할 수 있나요?",
         "네. 활성 장애가 있는 서비스를 볼 때 정해진 기간 동안 알림을 음소거하여 이미 알고 있는 사항에 대해 반복적으로 알림을 받지 않도록 할 수 있습니다. 음성으로도 음소거할 수 있습니다 — 「Siri야, GitHub을 2시간 동안 음소거해」 — 또는 Shortcuts 앱을 통해서도 가능합니다.",
         "<p>네. 활성 장애가 있는 서비스를 볼 때 정해진 기간 동안 알림을 음소거하여 이미 알고 있는 사항에 대해 반복적으로 알림을 받지 않도록 할 수 있습니다. 음성으로도 음소거할 수 있습니다 — 「Siri야, GitHub을 2시간 동안 음소거해」 — 또는 Shortcuts 앱을 통해서도 가능합니다.</p>"),
        ("어떤 플랫폼이 지원되나요?",
         "iPhone 및 iPad(위젯 및 Live Activities 포함), Mac(메뉴 막대 앱 및 전체 창), Apple Watch(컴플리케이션 및 Smart Stack 포함), Apple TV 및 Apple Vision Pro. 앱은 모든 플랫폼에서 무료로 다운로드할 수 있습니다.",
         "<p>iPhone 및 iPad(위젯 및 Live Activities 포함), Mac(메뉴 막대 앱 및 전체 창), Apple Watch(컴플리케이션 및 Smart Stack 포함), Apple TV 및 Apple Vision Pro. 앱은 모든 플랫폼에서 무료로 다운로드할 수 있습니다.</p>"),
        ("새 서비스를 요청할 수 있나요?",
         "네! support@vultyr.app으로 서비스 이름과 상태 페이지 URL을 포함하여 이메일을 보내주세요.",
         "<p>네! <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a>으로 서비스 이름과 상태 페이지 URL을 포함하여 이메일을 보내주세요.</p>"),
    ],
},
    "nb": {
    "html_lang": "nb",
    "og_locale": "nb_NO",
    "og_image_alt": "Vultyr-appikon — tjenestestatusmonitor",
    "devices": "iPhone, iPad, Mac, Apple Watch, Apple TV og Vision Pro",
    "skip_to_main": "Hopp til hovedinnhold",
    "topbar_brand_aria": "Vultyr hjem",
    "nav_primary_aria": "Hoved",
    "nav_services": "tjenester",
    "nav_support": "støtte",
    "nav_download": "Last ned",
    "footer_nav_aria": "Bunntekstnavigasjon",
    "footer_home": "Hjem",
    "footer_services": "Tjenester",
    "footer_privacy": "Personvern",
    "footer_support": "Støtte",
    "footer_contact": "Kontakt",
    "copyright": "© 2026 Vultyr. Alle rettigheter forbeholdt.",
    "breadcrumb_aria": "Brødsmulesti",
    "breadcrumb_vultyr": "Vultyr",
    "breadcrumb_services": "Tjenester",
    # services page
    "svcs_title": "Vultyr — 200+ statussjekker",
    "svcs_description": "200+ statussjekker på tvers av skytjenester, utviklerverktøy, kommunikasjon, KI og mer — alle overvåket av Vultyr.",
    "svcs_h1_lead": "Status",
    "svcs_h1_highlight": "sjekker",
    "svcs_subtitle": "200+ statussjekker som vultyr kjører på tvers av skytjenester, utviklerverktøy og plattformer.",
    "svcs_categories_aria": "Bla etter kategori",
    "svc_row_status": "Statusside",
    "svc_row_homepage": "Nettsted",
    "svcs_item_list_name": "Tjenester overvåket av Vultyr",
    # service page
    "svcp_title_fmt": "Er {name} nede? {name} statusmonitor | Vultyr",
    "svcp_description_fmt": "Sjekk om {name} er nede akkurat nå. Sanntidsoppdateringer av {name}-status og nedetidsovervåkning med Vultyr. Gratis på {devices}.",
    "svcp_live_check": "Sanntidssjekk",
    "svcp_view_current_status": "Se nåværende status →",
    "svcp_alert_hint_prefix": "For øyeblikkelige varsler, ",
    "svcp_alert_hint_link": "last ned Vultyr",
    "svcp_categories_label": "Kategorier:",
    "svcp_official_status": "Offisiell statusside",
    "svcp_homepage_fmt": "{name}-nettsted",
    "svcp_faq_heading": "Vanlige spørsmål",
    "svcp_faq_q1_fmt": "Er {name} nede akkurat nå?",
    "svcp_faq_a1_fmt": "Åpne den offisielle {name}-statussiden lenket ovenfor for gjeldende status. For kontinuerlig overvåkning med øyeblikkelige nedetidsvarsler på alle Apple-enhetene dine, last ned den gratis Vultyr-appen.",
    "svcp_faq_a1_ld_fmt": "Sjekk den offisielle {name}-statussiden på {url} for gjeldende status. Last ned den gratis Vultyr-appen for øyeblikkelige nedetidsvarsler på alle Apple-enhetene dine.",
    "svcp_faq_q2_fmt": "Hvordan kan jeg overvåke statusen til {name}?",
    "svcp_faq_a2_fmt": "Vultyr overvåker {name} som del av 200+ statussjekker på tvers av skytjenester, utviklerverktøy og plattformer. Få øyeblikkelige nedetidsvarsler på {devices} — helt gratis.",
    "svcp_faq_a2_ld_fmt": "Last ned Vultyr (gratis) for å overvåke {name} som del av 200+ statussjekker med sanntidsvarsler på {devices}. Vultyr kjører hver sjekk automatisk og varsler deg i det øyeblikket en nedetid oppdages.",
    "svcp_related_heading": "Relaterte tjenester",
    "svcp_related_aria": "Relaterte tjenester",
    "svcp_cta_heading_fmt": "Overvåk {name} på alle enhetene dine",
    "svcp_cta_body_fmt": "Få øyeblikkelige varsler når {name} går ned. Gratis på alle Apple-plattformer.",
    "cta_download_vultyr": "Last ned Vultyr",
    "cta_download_vultyr_aria": "Last ned Vultyr i App Store",
    # category page
    "catp_title_fmt": "{name} statusmonitor — {count_services} | Vultyr",
    "catp_description_fmt": "Overvåk statusen til {count_services} innen {name_lower}. Sanntidsvarsler om nedetid for {sample} og flere.",
    "catp_item_list_name_fmt": "{name} statusmonitorer",
    "catp_subtitle_fmt": "{count_services} overvåket av Vultyr",
    "catp_services_aria_fmt": "{name}-tjenester",
    "catp_other_heading": "Andre kategorier",
    "catp_cta_heading_fmt": "Overvåk alle {count_services} umiddelbart",
    "catp_cta_body": "Få sanntidsvarsler om nedetid på alle Apple-enhetene dine. Gratis.",
    # home page
    "home_title": "Vultyr — tjenestestatusmonitor for AWS, Slack, GitHub og mer",
    "home_description": "Er det nede? 200+ statussjekker på tvers av skytjenester, utviklerverktøy og plattformer med øyeblikkelige nedetidsvarsler. Gratis på iPhone, iPad, Mac, Apple Watch, Apple TV og Apple Vision Pro.",
    "home_og_title": "Vultyr — tjenestestatusmonitor",
    "home_app_ld_description": "Overvåk 200+ statussjekker på tvers av skytjenester, utviklerverktøy og plattformer med øyeblikkelige nedetidsvarsler.",
    "home_hero_tag": "200+ sjekker",
    "home_hero_question": "Er det nede?",
    "home_hero_answer": "Få vite det før brukerne dine gjør det.",
    "home_hero_services": "200+ statussjekker — AWS, GitHub, Slack, Stripe &amp; flere — med øyeblikkelige nedetidsvarsler på alle Apple-enheter.",
    "home_appstore_alt": "Last ned i App Store",
    "home_appstore_aria": "Last ned Vultyr i App Store",
    "home_free_on_prefix": "Gratis på",
    "home_screenshots_aria": "Skjermbilder av appen",
    "home_screenshot_dash_alt": "Vultyr-dashbordet viser «Alt klart»-status med tjenester som AWS, GitHub og Slack overvåket",
    "home_screenshot_settings_alt_fmt": "Vultyr utseendeinnstillinger med {themes} temaer, inkludert Terminal, Amber, Dracula og Nord",
    "home_screenshot_services_alt_fmt": "Vultyr tjenesteoversikt med {categories} kategorier, inkludert Cloud, Dev Tools og AI",
    "home_stats_aria": "Nøkkeltall",
    "home_stats_checks": "Sjekker",
    "home_stats_categories": "Kategorier",
    "home_stats_platforms": "Plattformer",
    "home_stats_languages": "Språk",
    "home_features_heading": "Alt du trenger for å ligge i forkant av nedetid",
    "home_features_sub": "Ingen appkontoer, ingen sporing i appen. Bare status.",
    "home_bottom_heading": "Klar til å overvåke stakken din?",
    "home_bottom_sub": "Gratis. Ingen appkonto nødvendig. Tilgjengelig overalt.",
    "home_bottom_button": "Last ned gratis",
    "home_bottom_aria": "Last ned Vultyr gratis i App Store",
    "home_languages_heading": "Tilgjengelig på 17 språk",
    "home_features": [
        ("chart-bar-regular.svg", "Sanntids statusdashbord",
         "AWS, GitHub, Cloudflare, Slack, Stripe, Discord, OpenAI, Anthropic og 200+ andre — alle på ett sted. Statusindikatorene synkroniseres med 120Hz ProMotion på iPhone Pro og iPad Pro."),
        ("bell-ringing-regular.svg", "Smarte varsler",
         "Varsler om nedetid og gjenoppretting med favicon for hver tjeneste på iOS. Store utfall pulserer merkbart større enn små hendelser, så alvorlighetsgraden er lett å se. Demp kjente hendelser og marker kritiske tjenester."),
        ("microphone-regular.svg",
         "Siri og Shortcuts",
         "Si til Siri «demp GitHub i 2 timer» eller «vis gjeldende problemer». App Intents for alle handlinger, pluss et Focus-filter som demper mindre kritiske tjenester."),
        ("squares-four-regular.svg",
         "Widgets og Live Activities",
         "Widgets på Hjem-skjermen og låseskjermen på iOS, pluss en widget i Control Center. Aktive nedetider festes til Dynamic Island."),
        ("watch-regular.svg",
         "Komplikasjoner på Apple Watch",
         "Fest en kritisk tjeneste til en urskive, eller la Smart Stack løfte fram aktive problemer automatisk."),
        ("cloud-check-regular.svg", "Mac-hub — iPhone som reserve",
         "Mac er den mest pålitelige huben: den sjekker så ofte som hvert 60. sekund (kan stilles inn opp til 15 min) og sender statusendringer til iPhone, iPad, Watch og Vision Pro via iCloud. Hvis ingen Mac er online, tar iPhone over som reserveutgiver slik at de andre enhetene fortsatt får varsler."),
        ("monitor-regular.svg", "Visning av varselpålitelighet",
         "Se med ett blikk om varsler faktisk når frem — Mac-hjerteslag, status for bakgrunnsoppdatering, CloudKit-push og når hver enhet sist sjekket."),
        ("devices-regular.svg",
         "Alle Apple-plattformer",
         "iPhone, iPad, Mac-menylinje, Apple TV, Apple Watch og Vision Pro. Tjenester synkroniseres mellom alle enheter."),
        ("lightning-regular.svg",
         "Hendelsesdetaljer",
         "Berørte komponenter, aktive hendelser, planlagt vedlikehold og tidslinjeoppdateringer — oversatt til ditt språk."),
        ("battery-charging-regular.svg", "Batteribevisst opprop",
         "Smart auto-oppdatering tilpasses batteri, strømtilstand og temperatur. Hvert minutt på Mac, 5–15 på iPhone, med bakgrunnsoppdatering på iPad, Apple Watch, Vision Pro og Apple TV."),
        ("palette-regular.svg", f"{THEMES_COUNT} temaer",
         "Standard og tre retrotemaer er inkludert. Fossil, Monolith, HAL og resten låses opp via valgfrie tippejar-IAP-er."),
        ("shield-check-regular.svg",
         "Appdata forblir lokalt",
         "Appen har ingen registrering og ingen innebygd analyse. Tjenestene du følger, blir værende på enheten din."),
        ("translate-regular.svg", f"{APP_LANGUAGE_COUNT} appspråk",
         "Engelsk, tysk, fransk, spansk, japansk, koreansk, kinesisk, portugisisk, russisk og flere."),
    ],
    # 404
    "err_title": "Siden ble ikke funnet — Vultyr",
    "err_description": "Siden du leter etter, finnes ikke.",
    "err_heading": "Siden ble ikke funnet",
    "err_message": "Siden du leter etter, finnes ikke eller er flyttet.",
    "redirect_moved_fmt": "Denne siden er flyttet. Omdirigerer til {name}…",
    "err_popular_heading": "Populære tjenester",
    "err_browse_heading": "Bla i kategorier",
    # privacy
    "privacy_title": "Personvernerklæring",
    "privacy_description": "Vultyrs personvernerklæring. Appen samler ingen personopplysninger. Dette nettstedet bruker Google Analytics uten informasjonskapsler for aggregert besøksstatistikk.",
    "privacy_last_updated": "Sist oppdatert: 11. april 2026",
    "privacy_sections": [
        ("Sammendrag",
         "<p>Vultyr-<strong>appen</strong> samler, lagrer og overfører ingen personopplysninger. Vultyr-<strong>nettstedet</strong> (vultyr.app) bruker Google Analytics uten informasjonskapsler for å forstå aggregert besøkstrafikk. Denne siden forklarer begge deler i detalj.</p>"),
        ("App — datainnsamling",
         "<p>Vultyr-appen samler ikke inn noen personlig informasjon. Den krever ingen konto, inkluderer ingen tredjeparts analyse- eller sporings-SDK-er, og sender ikke data til noen server vi drifter.</p>"),
        ("App — nettverksforespørsler",
         "<p>Appen sender direkte HTTPS-forespørsler til offentlige statusside-API-er (som Statuspage.io, Apple, Google Cloud og andre) for å sjekke tjenestestatus. Disse forespørslene går direkte fra enheten din til tjenestens offentlige API — de passerer ikke noen server vi drifter.</p>"),
        ("App — datalagring",
         "<p>Alle data lagres lokalt på enheten din med Apples SwiftData-rammeverk. Hvis du aktiverer iCloud-synkronisering, synkroniseres listen din over overvåkede tjenester via Apples iCloud Key-Value Store, som styres av Apples personvernerklæring. Vi ser aldri disse dataene.</p>"),
        ("App — varsler mellom enheter",
         "<p>Hvis du aktiverer varsler mellom enheter, deles statusendringer mellom enhetene dine via Apples iCloud Key-Value Store. Når Mac-en din oppdager en statusendring, skriver den et lett signal til iCloud-kontoen din. De andre enhetene dine observerer endringen og kjører sin egen lokale sjekk. Ingen tredjepartsserver er involvert — all kommunikasjon går gjennom Apples iCloud-infrastruktur. Du kan slå dette av og på fra hvilken som helst enhet.</p>"),
        ("App — favikoner",
         "<p>Tjenestefavikoner hentes fra Googles offentlige favikontjeneste og bufres lokalt på enheten din.</p>"),
        ("Nettstedet — analyse",
         "<p>Dette nettstedet (vultyr.app) bruker Google Analytics 4 i modus uten informasjonskapsler, med anonymisert IP, for å telle aggregerte sidevisninger. Nærmere bestemt konfigurerer vi gtag.js med <code>anonymize_ip: true</code>, <code>client_storage: 'none'</code>, <code>allow_google_signals: false</code> og <code>allow_ad_personalization_signals: false</code>. Dette betyr at ingen <code>_ga</code>-informasjonskapsel settes, IP-adressen din kortes ned før lagring, og ingen annonseidentifikatorer samles inn. Selve Vultyr-appen inneholder ingen analyse.</p>"),
        ("Nettstedet — tredjepartsdomener",
         "<p>Når vultyr.app lastes inn, kontaktes følgende tredjepartsdomener:</p>\n    <ul>\n        <li><strong>www.googletagmanager.com</strong> — laster gtag.js-skriptet</li>\n        <li><strong>www.google-analytics.com</strong> / <strong>*.analytics.google.com</strong> — mottar anonymiserte signaler om sidevisninger</li>\n        <li><strong>www.google.com/g/collect</strong> — mottar de samme anonymiserte signalene om sidevisninger (reservesamlingsendepunktet for Google Analytics 4)</li>\n    </ul>\n    <p>Vi laster ikke inn Google Fonts (Audiowide-fonten er selvhostet på vultyr.app) og bruker ingen tredjeparts favikontjeneste for nettstedets egne bilder.</p>"),
        ("App — tredjepartstjenester",
         "<p>Vultyr-appen integrerer ikke med noen tredjeparts analyse-, reklame- eller sporingstjenester. De eneste eksterne forespørslene går til offentlige status-API-er og Googles favikontjeneste.</p>"),
        ("Barns personvern",
         "<p>Vultyr-appen samler ikke inn data fra noen, inkludert barn under 13 år. Nettstedet logger kun anonymiserte, aggregerte besøkstellinger.</p>"),
        ("Endringer",
         "<p>Hvis denne erklæringen endres, oppdaterer vi datoen ovenfor.</p>"),
        ("Kontakt",
         "<p>Spørsmål? Send e-post til <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a></p>"),
    ],
    # support
    "support_title": "Støtte",
    "support_description": "Få hjelp med Vultyr, tjenestestatusmonitoren for iPhone, iPad, Mac, Apple Watch, Apple TV og Apple Vision Pro. Vanlige spørsmål, kontakt og feilsøking.",
    "support_contact_heading": "Kontakt",
    "support_contact_html": "<p>For feilrapporter, funksjonsønsker eller spørsmål:<br>\n    <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a></p>",
    "support_faq_heading": "Vanlige spørsmål",
    "support_faqs": [
        ("Hvor ofte sjekker vultyr tjenestestatus?",
         "På Mac: så ofte som hvert 60. sekund når den er koblet til strøm. På iPhone: hvert 5., 10. eller 15. minutt (konfigurerbart), med jevnlige bakgrunnssjekker når forholdene tillater det. På Apple Watch: hvert 15. minutt. På Apple TV: hvert 5. minutt. Oppropet tilpasser seg automatisk til batterinivå, strømtilstand og temperatur.",
         "<p>På Mac: så ofte som hvert 60. sekund når den er koblet til strøm. På iPhone: hvert 5., 10. eller 15. minutt (konfigurerbart), med jevnlige bakgrunnssjekker når forholdene tillater det. På Apple Watch: hvert 15. minutt. På Apple TV: hvert 5. minutt. Oppropet tilpasser seg automatisk til batterinivå, strømtilstand og temperatur.</p>"),
        ("Hvordan fungerer varsler mellom enheter?",
         "Mac-appen er navet. Hold den i gang (menylinje eller fullt vindu), så opprører den så ofte som hvert 60. sekund (kan stilles inn opp til 15 min). Når en statusendring oppdages, skriver den et lett signal til iCloud Key-Value Store; iPhone, iPad, Watch, Apple TV og Vision Pro plukker opp endringen og kjører sin egen lokale sjekk. Ingen nøkler, ingen tokener, ingen oppsett — bare aktiver «Varsler mellom enheter» i innstillingene på en hvilken som helst enhet. Uten en Mac som nav er varsler avhengige av iOS-bakgrunnseksekvering, og vil bli forsinket eller gå tapt.",
         "<p>Mac-appen er navet. Hold den i gang (menylinje eller fullt vindu), så opprører den så ofte som hvert 60. sekund (kan stilles inn opp til 15 min). Når en statusendring oppdages, skriver den et lett signal til iCloud Key-Value Store; iPhone, iPad, Watch, Apple TV og Vision Pro plukker opp endringen og kjører sin egen lokale sjekk. Ingen nøkler, ingen tokener, ingen oppsett — bare aktiver «Varsler mellom enheter» i innstillingene på en hvilken som helst enhet. Uten en Mac som nav er varsler avhengige av iOS-bakgrunnseksekvering, og vil bli forsinket eller gå tapt.</p>"),
        ("Trenger jeg Mac-appen for pålitelige varsler?",
         "Ja — vi anbefaler det sterkt. iOS begrenser bakgrunnseksekvering, så iPhone og iPad kan bare sjekke hvert 5.–15. minutt (konfigurerbart) og kan utsette ytterligere ved lavt batteri, strømsparingsmodus eller dårlig dekning. Mac-appen opprører så ofte som hvert 60. sekund når den er koblet til strøm (kan stilles inn opp til 15 min) og kringkaster statusendringer til de andre enhetene dine via iCloud. Uten en Mac som kjører Vultyr, fungerer varsler på iOS, watchOS og tvOS fortsatt, men kan bli betydelig forsinket eller gå tapt. For sanntidsovervåkning, hold Mac-appen i gang — den er bitte liten i menylinjen, og det er slik Vultyr er ment å brukes.",
         "<p>Ja — vi anbefaler det sterkt. iOS begrenser bakgrunnseksekvering, så iPhone og iPad kan bare sjekke hvert 5.–15. minutt (konfigurerbart) og kan utsette ytterligere ved lavt batteri, strømsparingsmodus eller dårlig dekning. Mac-appen opprører så ofte som hvert 60. sekund når den er koblet til strøm (kan stilles inn opp til 15 min) og kringkaster statusendringer til de andre enhetene dine via iCloud. Uten en Mac som kjører Vultyr, fungerer varsler på iOS, watchOS og tvOS fortsatt, men kan bli betydelig forsinket eller gå tapt. For sanntidsovervåkning, hold Mac-appen i gang — den er bitte liten i menylinjen, og det er slik Vultyr er ment å brukes.</p>"),
        ("Fungerer vultyr med Siri og Shortcuts?",
         "Ja. Innebygde App Intents lar deg si «Hei Siri, demp GitHub i 2 timer», «sjekk Stripe-status» eller «vis gjeldende problemer», og du kan koble de samme handlingene til Shortcuts-appen. Det finnes også et Focus-filter, slik at en «vultyr Focus»-modus automatisk kan dempe mindre kritiske tjenester.",
         "<p>Ja. Innebygde App Intents lar deg si «Hei Siri, demp GitHub i 2 timer», «sjekk Stripe-status» eller «vis gjeldende problemer», og du kan koble de samme handlingene til Shortcuts-appen. Det finnes også et Focus-filter, slik at en «vultyr Focus»-modus automatisk kan dempe mindre kritiske tjenester.</p>"),
        ("Finnes det widgets og Live Activities?",
         "På iOS finnes widgets på Hjem-skjermen og låseskjermen (enkelt­tjeneste og statussammendrag) pluss en widget i Control Center. Aktive nedetider festes til Dynamic Island som Live Activities. På watchOS er komplikasjoner tilgjengelige for alle urskiver, med Smart Stack-relevans slik at riktig tjeneste dukker opp når noe er nede.",
         "<p>På iOS finnes widgets på Hjem-skjermen og låseskjermen (enkelt­tjeneste og statussammendrag) pluss en widget i Control Center. Aktive nedetider festes til Dynamic Island som Live Activities. På watchOS er komplikasjoner tilgjengelige for alle urskiver, med Smart Stack-relevans slik at riktig tjeneste dukker opp når noe er nede.</p>"),
        ("Samler vultyr-appen inn dataene mine?",
         "Nei. Appen har ingen kontoer, ingen sporing i appen, ingen analyse i appen. Alle tjenestene du følger, blir værende på enheten din. Merk: dette nettstedet (vultyr.app) bruker Google Analytics uten informasjonskapsler for aggregerte besøkstellinger — se personvernerklæringen for detaljer.",
         "<p>Nei. Appen har ingen kontoer, ingen sporing i appen, ingen analyse i appen. Alle tjenestene du følger, blir værende på enheten din. Merk: dette nettstedet (vultyr.app) bruker Google Analytics uten informasjonskapsler for aggregerte besøkstellinger — se <a href=\"/nb/privacy.html\">personvernerklæringen</a> for detaljer.</p>"),
        ("Hvordan synkroniserer jeg tjenestene mine mellom enheter?",
         "Tjenestene du følger, synkroniseres automatisk via iCloud. Temaer og innstillinger synkroniseres også på alle Apple-enhetene dine via iCloud Key-Value Store.",
         "<p>Tjenestene du følger, synkroniseres automatisk via iCloud. Temaer og innstillinger synkroniseres også på alle Apple-enhetene dine via iCloud Key-Value Store.</p>"),
        ("Hva er temaalternativene?",
         "12 temaer: Standard, Terminal, Amber, Blue, Neon, Dracula, Nord, Solarized, Catppuccin, Fossil, Monolith og HAL. Standard og de tre retrotemaene (Terminal, Amber, Blue) er inkludert. Fossil, Monolith, HAL og resten låses opp via valgfrie tippejar-IAP-er ($0,99 / $4,99 / $9,99), som også bidrar til å finansiere utviklingen. Temaer synkroniseres automatisk på alle enhetene dine.",
         "<p>12 temaer: Standard, Terminal, Amber, Blue, Neon, Dracula, Nord, Solarized, Catppuccin, Fossil, Monolith og HAL. Standard og de tre retrotemaene (Terminal, Amber, Blue) er inkludert. Fossil, Monolith, HAL og resten låses opp via valgfrie tippejar-IAP-er ($0,99 / $4,99 / $9,99), som også bidrar til å finansiere utviklingen. Temaer synkroniseres automatisk på alle enhetene dine.</p>"),
        ("Kan jeg dempe varsler for en kjent hendelse?",
         "Ja. Når du ser på en tjeneste med en aktiv hendelse, kan du dempe varsler for en angitt periode, slik at du ikke blir varslet gjentatte ganger om noe du allerede vet om. Du kan også dempe med stemmen — «Hei Siri, demp GitHub i 2 timer» — eller fra Shortcuts-appen.",
         "<p>Ja. Når du ser på en tjeneste med en aktiv hendelse, kan du dempe varsler for en angitt periode, slik at du ikke blir varslet gjentatte ganger om noe du allerede vet om. Du kan også dempe med stemmen — «Hei Siri, demp GitHub i 2 timer» — eller fra Shortcuts-appen.</p>"),
        ("Hvilke plattformer støttes?",
         "iPhone og iPad (med widgets og Live Activities), Mac (med en menylinjeapp pluss fullt vindu), Apple Watch (med komplikasjoner og Smart Stack), Apple TV og Apple Vision Pro. Appen er gratis å laste ned på alle plattformer.",
         "<p>iPhone og iPad (med widgets og Live Activities), Mac (med en menylinjeapp pluss fullt vindu), Apple Watch (med komplikasjoner og Smart Stack), Apple TV og Apple Vision Pro. Appen er gratis å laste ned på alle plattformer.</p>"),
        ("Kan jeg be om en ny tjeneste?",
         "Ja! Send e-post til support@vultyr.app med tjenestens navn og URL-en til statussiden.",
         "<p>Ja! Send e-post til <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a> med tjenestens navn og URL-en til statussiden.</p>"),
    ],
},
    "nl": {
    "html_lang": "nl",
    "og_locale": "nl_NL",
    "og_image_alt": "Vultyr-app\u2011icoon \u2014 monitor voor servicestatus",
    "devices": "iPhone, iPad, Mac, Apple Watch, Apple TV en Vision Pro",
    "skip_to_main": "Ga naar hoofdinhoud",
    "topbar_brand_aria": "Vultyr home",
    "nav_primary_aria": "Hoofdnavigatie",
    "nav_services": "services",
    "nav_support": "support",
    "nav_download": "Downloaden",
    "footer_nav_aria": "Footernavigatie",
    "footer_home": "Home",
    "footer_services": "Services",
    "footer_privacy": "Privacy",
    "footer_support": "Support",
    "footer_contact": "Contact",
    "copyright": "\u00a9 2026 Vultyr. Alle rechten voorbehouden.",
    "breadcrumb_aria": "Kruimelpad",
    "breadcrumb_vultyr": "Vultyr",
    "breadcrumb_services": "Services",
    # services page
    "svcs_title": "Vultyr \u2014 200+ statuscontroles",
    "svcs_description": "200+ statuscontroles voor cloudservices, ontwikkeltools, communicatie, AI en meer \u2014 allemaal gemonitord door Vultyr.",
    "svcs_h1_lead": "Status",
    "svcs_h1_highlight": "Controles",
    "svcs_subtitle": "200+ statuscontroles die Vultyr uitvoert voor cloudservices, ontwikkeltools en platforms.",
    "svcs_categories_aria": "Bladeren op categorie",
    "svc_row_status": "Statuspagina",
    "svc_row_homepage": "Homepage",
    "svcs_item_list_name": "Services gemonitord door Vultyr",
    # service page
    "svcp_title_fmt": "Is {name} offline? Statusmonitor voor {name} | Vultyr",
    "svcp_description_fmt": "Controleer of {name} nu offline is. Live statusupdates voor {name} en storingsmonitoring met Vultyr. Gratis op {devices}.",
    "svcp_live_check": "Live controle",
    "svcp_view_current_status": "Bekijk huidige status \u2192",
    "svcp_alert_hint_prefix": "Voor directe meldingen, ",
    "svcp_alert_hint_link": "download Vultyr",
    "svcp_categories_label": "Categorie\u00ebn:",
    "svcp_official_status": "Offici\u00eble statuspagina",
    "svcp_homepage_fmt": "Homepage van {name}",
    "svcp_faq_heading": "Veelgestelde vragen",
    "svcp_faq_q1_fmt": "Is {name} nu offline?",
    "svcp_faq_a1_fmt": "Raadpleeg de offici\u00eble statuspagina van {name} via de link hierboven voor de actuele status. Voor continue monitoring met directe storingsmeldingen op al je Apple\u2011apparaten kun je de gratis Vultyr\u2011app downloaden.",
    "svcp_faq_a1_ld_fmt": "Raadpleeg de offici\u00eble statuspagina van {name} op {url} voor de actuele status. Download de gratis Vultyr\u2011app voor directe storingsmeldingen op al je Apple\u2011apparaten.",
    "svcp_faq_q2_fmt": "Hoe kan ik de status van {name} monitoren?",
    "svcp_faq_a2_fmt": "Vultyr monitort {name} als onderdeel van 200+ statuscontroles voor cloudservices, ontwikkeltools en platforms. Ontvang directe storingsmeldingen op {devices} \u2014 volledig gratis.",
    "svcp_faq_a2_ld_fmt": "Download Vultyr (gratis) om {name} te monitoren als onderdeel van 200+ statuscontroles met realtime meldingen op {devices}. Vultyr voert elke controle automatisch uit en meldt het zodra er een storing wordt gedetecteerd.",
    "svcp_related_heading": "Gerelateerde services",
    "svcp_related_aria": "Gerelateerde services",
    "svcp_cta_heading_fmt": "Monitor {name} op al je apparaten",
    "svcp_cta_body_fmt": "Ontvang directe meldingen wanneer {name} offline gaat. Gratis op alle Apple\u2011platforms.",
    "cta_download_vultyr": "Download Vultyr",
    "cta_download_vultyr_aria": "Download Vultyr in de App Store",
    # category page
    "catp_title_fmt": "Statusmonitor voor {name} \u2014 {count_services} | Vultyr",
    "catp_description_fmt": "Monitor de status van {count_services} in {name_lower}. Realtime storingsmeldingen voor {sample} en meer.",
    "catp_item_list_name_fmt": "Statusmonitors voor {name}",
    "catp_subtitle_fmt": "{count_services} gemonitord door Vultyr",
    "catp_services_aria_fmt": "{name}\u2011services",
    "catp_other_heading": "Andere categorie\u00ebn",
    "catp_cta_heading_fmt": "Monitor alle {count_services} in \u00e9\u00e9n keer",
    "catp_cta_body": "Ontvang realtime storingsmeldingen op al je Apple\u2011apparaten. Gratis.",
    # home page
    "home_title": "Vultyr \u2014 Servicestatusmonitor voor AWS, Slack, GitHub en meer",
    "home_description": "Is het offline? 200+ statuscontroles voor cloudservices, ontwikkeltools en platforms met directe storingsmeldingen. Gratis op iPhone, iPad, Mac, Apple Watch, Apple TV en Apple Vision Pro.",
    "home_og_title": "Vultyr \u2014 Servicestatusmonitor",
    "home_app_ld_description": "Monitor 200+ statuscontroles voor cloudservices, ontwikkeltools en platforms met directe storingsmeldingen.",
    "home_hero_tag": "200+ controles",
    "home_hero_question": "Is het offline?",
    "home_hero_answer": "Weet het voordat je gebruikers het weten.",
    "home_hero_services": "200+ statuscontroles \u2014 AWS, GitHub, Slack, Stripe &amp; meer \u2014 met directe storingsmeldingen op elk Apple\u2011apparaat.",
    "home_appstore_alt": "Download in de App Store",
    "home_appstore_aria": "Download Vultyr in de App Store",
    "home_free_on_prefix": "Gratis op",
    "home_screenshots_aria": "App\u2011screenshots",
    "home_screenshot_dash_alt": "Vultyr\u2011dashboard met de status \u201eAlles in orde\u201d en services als AWS, GitHub en Slack onder monitoring",
    "home_screenshot_settings_alt_fmt": "Weergave\u2011instellingen van Vultyr met {themes} thema\u2019s, waaronder Terminal, Amber, Dracula en Nord",
    "home_screenshot_services_alt_fmt": "Servicebrowser van Vultyr met {categories} categorie\u00ebn, waaronder Cloud, Dev Tools en AI",
    "home_stats_aria": "Kerncijfers",
    "home_stats_checks": "Controles",
    "home_stats_categories": "Categorie\u00ebn",
    "home_stats_platforms": "Platforms",
    "home_stats_languages": "Talen",
    "home_features_heading": "Alles wat je nodig hebt om storingen voor te zijn",
    "home_features_sub": "Geen accounts, geen tracking in de app. Alleen status.",
    "home_bottom_heading": "Klaar om je stack te monitoren?",
    "home_bottom_sub": "Gratis. Geen account nodig. Overal beschikbaar.",
    "home_bottom_button": "Gratis downloaden",
    "home_bottom_aria": "Download Vultyr gratis in de App Store",
    "home_languages_heading": "Beschikbaar in 17 talen",
    "home_features": [
        ("chart-bar-regular.svg", "Live statusdashboard",
         "AWS, GitHub, Cloudflare, Slack, Stripe, Discord, OpenAI, Anthropic en 200+ meer — allemaal op één plek. De status-orbs synchroniseren met 120Hz ProMotion op iPhone Pro en iPad Pro."),
        ("bell-ringing-regular.svg", "Slimme meldingen",
         "Storings- en herstelmeldingen met het favicon van elke dienst op iOS. Grote storingen pulseren merkbaar groter dan kleine incidenten, zodat de ernst in één oogopslag zichtbaar is. Demp bekende problemen, markeer kritieke diensten."),
        ("microphone-regular.svg", "Siri en Shortcuts",
         "Vraag Siri om \u201eGitHub 2 uur te dempen\u201d of \u201ehuidige problemen te tonen\u201d. App Intents voor elke actie, plus een Focus\u2011filter dat niet\u2011kritieke services stil houdt."),
        ("squares-four-regular.svg", "Widgets en Live Activities",
         "Widgets voor het beginscherm en toegangsscherm op iOS, plus een widget in het Bedieningspaneel. Actieve storingen worden vastgezet in de Dynamic Island."),
        ("watch-regular.svg", "Watch\u2011complicaties",
         "Zet een kritieke service vast op een wijzerplaat of laat Smart Stack actieve problemen automatisch tonen."),
        ("cloud-check-regular.svg", "Mac-hub — iPhone als reserve",
         "Mac is de betrouwbaarste hub: peilt zo vaak als elke 60 seconden (instelbaar tot 15 min) en stuurt statuswijzigingen via iCloud door naar iPhone, iPad, Watch en Vision Pro. Als er geen Mac online is, neemt je iPhone het als reserve-publisher over zodat de andere apparaten toch meldingen krijgen."),
        ("monitor-regular.svg", "Overzicht meldingsbetrouwbaarheid",
         "Zie in één oogopslag of meldingen je daadwerkelijk bereiken — Mac-hartslag, status van achtergrondverversing, CloudKit-push en wanneer elk apparaat voor het laatst controleerde."),
        ("devices-regular.svg", "Elk Apple\u2011platform",
         "iPhone, iPad, Mac\u2011menubalk, Apple TV, Apple Watch en Vision Pro. Services synchroniseren over alle apparaten."),
        ("lightning-regular.svg", "Incidentdetails",
         "Betrokken componenten, actieve incidenten, geplande onderhoudswerken en tijdlijn\u2011updates \u2014 in jouw taal."),
        ("battery-charging-regular.svg", "Batterijbewust pollen",
         "Slimme auto-verversing past zich aan batterij, voeding en temperatuur aan. Elke minuut op Mac, 5–15 op iPhone, met achtergrondverversing op iPad, Apple Watch, Vision Pro en Apple TV."),
        ("palette-regular.svg", f"{THEMES_COUNT} thema\u2019s",
         "Standard en drie retrothema\u2019s zijn inbegrepen. Fossil, Monolith, HAL en de rest zijn te ontgrendelen via optionele fooi\u2011IAP\u2019s."),
        ("shield-check-regular.svg", "App\u2011gegevens blijven lokaal",
         "De app heeft geen registratie en geen analytics in de app. Je gevolgde services blijven op je apparaat."),
        ("translate-regular.svg", f"{APP_LANGUAGE_COUNT} app\u2011talen",
         "Engels, Duits, Frans, Spaans, Japans, Koreaans, Chinees, Portugees, Russisch en meer."),
    ],
    # 404
    "err_title": "Pagina niet gevonden \u2014 Vultyr",
    "err_description": "De pagina die je zoekt bestaat niet.",
    "err_heading": "Pagina niet gevonden",
    "err_message": "De pagina die je zoekt bestaat niet of is verplaatst.",
    "redirect_moved_fmt": "Deze pagina is verplaatst. Wordt doorgestuurd naar {name}…",
    "err_popular_heading": "Populaire services",
    "err_browse_heading": "Bladeren door categorie\u00ebn",
    # privacy
    "privacy_title": "Privacybeleid",
    "privacy_description": "Privacybeleid van Vultyr. De app verzamelt geen persoonsgegevens. Deze website gebruikt cookieloze Google Analytics voor geaggregeerde bezoekersstatistieken.",
    "privacy_last_updated": "Laatst bijgewerkt: 11 april 2026",
    "privacy_sections": [
        ("Samenvatting",
         "<p>De Vultyr\u2011<strong>app</strong> verzamelt, bewaart en verzendt geen persoonsgegevens. De Vultyr\u2011<strong>website</strong> (vultyr.app) gebruikt cookieloze Google Analytics om geaggregeerd bezoekersverkeer te begrijpen. Deze pagina legt beide in detail uit.</p>"),
        ("App \u2014 Gegevensverzameling",
         "<p>De Vultyr\u2011app verzamelt geen persoonlijke informatie. Er is geen account nodig, er zijn geen analytics\u2011 of trackings\u2011SDK\u2019s van derden, en de app belt niet naar een server die wij beheren.</p>"),
        ("App \u2014 Netwerkverzoeken",
         "<p>De app stuurt directe HTTPS\u2011verzoeken naar openbare API\u2019s van statuspagina\u2019s (zoals Statuspage.io, Apple, Google Cloud en andere) om de servicestatus te controleren. Deze verzoeken gaan rechtstreeks van je apparaat naar de openbare API van de service \u2014 ze lopen niet via een server die wij beheren.</p>"),
        ("App \u2014 Gegevensopslag",
         "<p>Alle gegevens worden lokaal op je apparaat opgeslagen met Apple\u2019s SwiftData\u2011framework. Als je iCloud\u2011synchronisatie inschakelt, wordt je lijst met gevolgde services gesynchroniseerd via Apple\u2019s iCloud Key\u2011Value Store, dat onder Apple\u2019s privacybeleid valt. Wij zien deze gegevens nooit.</p>"),
        ("App \u2014 Meldingen tussen apparaten",
         "<p>Als je meldingen tussen apparaten inschakelt, worden statuswijzigingen gedeeld tussen je apparaten via Apple\u2019s iCloud Key\u2011Value Store. Zodra je Mac een statuswijziging detecteert, schrijft die een klein signaal naar je iCloud\u2011account. Je andere apparaten merken de wijziging op en voeren hun eigen lokale controle uit. Er is geen server van derden bij betrokken \u2014 alle communicatie loopt via Apple\u2019s iCloud\u2011infrastructuur. Je kunt deze functie vanaf elk apparaat aan\u2011 of uitzetten.</p>"),
        ("App \u2014 Favicons",
         "<p>Service\u2011favicons worden opgehaald uit de openbare favicondienst van Google en lokaal op je apparaat in de cache bewaard.</p>"),
        ("Website \u2014 Analytics",
         "<p>Deze website (vultyr.app) gebruikt Google Analytics 4 in cookieloze, IP\u2011geanonimiseerde modus om geaggregeerde paginaweergaven te tellen. Specifiek configureren we gtag.js met <code>anonymize_ip: true</code>, <code>client_storage: 'none'</code>, <code>allow_google_signals: false</code> en <code>allow_ad_personalization_signals: false</code>. Dit betekent dat er geen <code>_ga</code>\u2011cookie wordt geplaatst, je IP wordt ingekort voordat het wordt opgeslagen en er geen advertentie\u2011ID\u2019s worden verzameld. De Vultyr\u2011app zelf bevat geen enkele vorm van analytics.</p>"),
        ("Website \u2014 Domeinen van derden",
         "<p>Het laden van vultyr.app maakt verbinding met de volgende domeinen van derden:</p>\n    <ul>\n        <li><strong>www.googletagmanager.com</strong> \u2014 laadt het gtag.js\u2011script</li>\n        <li><strong>www.google-analytics.com</strong> / <strong>*.analytics.google.com</strong> \u2014 ontvangt geanonimiseerde paginaweergave\u2011beacons</li>\n        <li><strong>www.google.com/g/collect</strong> \u2014 ontvangt dezelfde geanonimiseerde paginaweergave\u2011beacons (fallback\u2011verzamelendpoint van Google Analytics 4)</li>\n    </ul>\n    <p>We laden geen Google Fonts (het Audiowide\u2011lettertype wordt zelf gehost op vultyr.app) en gebruiken geen favicondienst van derden voor het beeldmateriaal van de website zelf.</p>"),
        ("App \u2014 Diensten van derden",
         "<p>De Vultyr\u2011app integreert niet met analyse\u2011, reclame\u2011 of trackingsdiensten van derden. De enige externe verzoeken gaan naar openbare status\u2011API\u2019s en Google\u2019s favicondienst.</p>"),
        ("Privacy van kinderen",
         "<p>De Vultyr\u2011app verzamelt van niemand gegevens, ook niet van kinderen onder de 13. De website registreert alleen geanonimiseerde, geaggregeerde bezoekersaantallen.</p>"),
        ("Wijzigingen",
         "<p>Als dit beleid verandert, werken we de datum hierboven bij.</p>"),
        ("Contact",
         "<p>Vragen? Mail <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a></p>"),
    ],
    # support
    "support_title": "Support",
    "support_description": "Hulp bij Vultyr, de servicestatusmonitor voor iPhone, iPad, Mac, Apple Watch, Apple TV en Apple Vision Pro. Veelgestelde vragen, contact en probleemoplossing.",
    "support_contact_heading": "Contact",
    "support_contact_html": "<p>Voor bugmeldingen, functieverzoeken of vragen:<br>\n    <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a></p>",
    "support_faq_heading": "Veelgestelde vragen",
    "support_faqs": [
        ("Hoe vaak controleert Vultyr de servicestatus?",
         "Op Mac: zo vaak als elke 60 seconden bij een stroomaansluiting (instelbaar tot 15 min). Op iPhone: elke 5, 10 of 15 minuten (instelbaar), met periodieke achtergrondcontroles waar dat kan. Op Apple Watch: elke 15 minuten. Op Apple TV: elke 5 minuten. Het pollen past zich automatisch aan batterijniveau, stroomvoorziening en temperatuur aan.",
         "<p>Op Mac: zo vaak als elke 60 seconden bij een stroomaansluiting (instelbaar tot 15 min). Op iPhone: elke 5, 10 of 15 minuten (instelbaar), met periodieke achtergrondcontroles waar dat kan. Op Apple Watch: elke 15 minuten. Op Apple TV: elke 5 minuten. Het pollen past zich automatisch aan batterijniveau, stroomvoorziening en temperatuur aan.</p>"),
        ("Hoe werken meldingen tussen apparaten?",
         "De Mac\u2011app is het centrum. Houd die draaiend (in de menubalk of als volledig venster) en die peilt zo vaak als elke 60 seconden (instelbaar tot 15 min). Zodra een statuswijziging wordt gedetecteerd, schrijft de app een klein signaal naar de iCloud Key\u2011Value Store; je iPhone, iPad, Watch, Apple TV en Vision Pro pikken de wijziging op en voeren hun eigen lokale controle uit. Geen sleutels, geen tokens, geen setup \u2014 zet gewoon \u201eMeldingen tussen apparaten\u201d aan in de instellingen op een willekeurig apparaat. Zonder Mac als centrum leunen meldingen op iOS\u2011achtergronduitvoering en zullen ze vertraagd of gemist worden.",
         "<p>De Mac\u2011app is het centrum. Houd die draaiend (in de menubalk of als volledig venster) en die peilt zo vaak als elke 60 seconden (instelbaar tot 15 min). Zodra een statuswijziging wordt gedetecteerd, schrijft de app een klein signaal naar de iCloud Key\u2011Value Store; je iPhone, iPad, Watch, Apple TV en Vision Pro pikken de wijziging op en voeren hun eigen lokale controle uit. Geen sleutels, geen tokens, geen setup \u2014 zet gewoon \u201eMeldingen tussen apparaten\u201d aan in de instellingen op een willekeurig apparaat. Zonder Mac als centrum leunen meldingen op iOS\u2011achtergronduitvoering en zullen ze vertraagd of gemist worden.</p>"),
        ("Heb ik de Mac\u2011app nodig voor betrouwbare meldingen?",
         "Ja \u2014 we raden het sterk aan. iOS beperkt achtergronduitvoering, dus iPhone en iPad kunnen alleen elke 5\u201315 minuten controleren (instelbaar) en kunnen verder uitstellen bij een lage batterij, Energiebesparingsmodus of slechte verbinding. De Mac\u2011app peilt zo vaak als elke 60 seconden bij een stroomaansluiting (instelbaar tot 15 min) en verspreidt statuswijzigingen naar je andere apparaten via iCloud. Zonder een Mac waarop Vultyr draait, werken meldingen op iOS, watchOS en tvOS nog steeds, maar kunnen ze aanzienlijk vertraagd of gemist worden. Voor realtime monitoring laat je de Mac\u2011app draaien \u2014 hij is klein in de menubalk en zo is Vultyr bedoeld om gebruikt te worden.",
         "<p>Ja \u2014 we raden het sterk aan. iOS beperkt achtergronduitvoering, dus iPhone en iPad kunnen alleen elke 5\u201315 minuten controleren (instelbaar) en kunnen verder uitstellen bij een lage batterij, Energiebesparingsmodus of slechte verbinding. De Mac\u2011app peilt zo vaak als elke 60 seconden bij een stroomaansluiting (instelbaar tot 15 min) en verspreidt statuswijzigingen naar je andere apparaten via iCloud. Zonder een Mac waarop Vultyr draait, werken meldingen op iOS, watchOS en tvOS nog steeds, maar kunnen ze aanzienlijk vertraagd of gemist worden. Voor realtime monitoring laat je de Mac\u2011app draaien \u2014 hij is klein in de menubalk en zo is Vultyr bedoeld om gebruikt te worden.</p>"),
        ("Werkt Vultyr met Siri en Shortcuts?",
         "Ja. Ingebouwde App Intents laten je zeggen: \u201eHey Siri, demp GitHub 2 uur\u201d, \u201echeck de status van Stripe\u201d of \u201etoon huidige problemen\u201d, en dezelfde acties kun je vastleggen in de Shortcuts\u2011app. Er is ook een Focus\u2011filter zodat een \u201eVultyr Focus\u201d\u2011modus niet\u2011kritieke services automatisch kan stilhouden.",
         "<p>Ja. Ingebouwde App Intents laten je zeggen: \u201eHey Siri, demp GitHub 2 uur\u201d, \u201echeck de status van Stripe\u201d of \u201etoon huidige problemen\u201d, en dezelfde acties kun je vastleggen in de Shortcuts\u2011app. Er is ook een Focus\u2011filter zodat een \u201eVultyr Focus\u201d\u2011modus niet\u2011kritieke services automatisch kan stilhouden.</p>"),
        ("Zijn er widgets en Live Activities?",
         "Op iOS zijn er widgets voor het beginscherm en toegangsscherm (per service en als statussamenvatting) plus een widget in het Bedieningspaneel. Actieve storingen worden als Live Activities vastgezet in de Dynamic Island. Op watchOS zijn complicaties beschikbaar voor alle wijzerplaten, met Smart Stack\u2011relevantie zodat de juiste service opduikt zodra er iets offline is.",
         "<p>Op iOS zijn er widgets voor het beginscherm en toegangsscherm (per service en als statussamenvatting) plus een widget in het Bedieningspaneel. Actieve storingen worden als Live Activities vastgezet in de Dynamic Island. Op watchOS zijn complicaties beschikbaar voor alle wijzerplaten, met Smart Stack\u2011relevantie zodat de juiste service opduikt zodra er iets offline is.</p>"),
        ("Verzamelt de Vultyr\u2011app mijn gegevens?",
         "Nee. De app heeft geen accounts, geen tracking in de app en geen analytics in de app. Al je gevolgde services blijven op je apparaat. Let op: deze website (vultyr.app) gebruikt cookieloze Google Analytics voor geaggregeerde bezoekersaantallen \u2014 zie het Privacybeleid voor details.",
         "<p>Nee. De app heeft geen accounts, geen tracking in de app en geen analytics in de app. Al je gevolgde services blijven op je apparaat. Let op: deze website (vultyr.app) gebruikt cookieloze Google Analytics voor geaggregeerde bezoekersaantallen \u2014 zie het <a href=\"/privacy.html\">Privacybeleid</a> voor details.</p>"),
        ("Hoe synchroniseer ik mijn services tussen apparaten?",
         "Je gevolgde services synchroniseren automatisch via iCloud. Thema\u2019s en instellingen synchroniseren ook tussen al je Apple\u2011apparaten via de iCloud Key\u2011Value Store.",
         "<p>Je gevolgde services synchroniseren automatisch via iCloud. Thema\u2019s en instellingen synchroniseren ook tussen al je Apple\u2011apparaten via de iCloud Key\u2011Value Store.</p>"),
        ("Welke thema\u2019s zijn er?",
         "12 thema\u2019s: Standard, Terminal, Amber, Blue, Neon, Dracula, Nord, Solarized, Catppuccin, Fossil, Monolith en HAL. Standard en de drie retrothema\u2019s (Terminal, Amber, Blue) zijn inbegrepen. Fossil, Monolith, HAL en de rest worden ontgrendeld via optionele fooi\u2011IAP\u2019s ($0.99 / $4.99 / $9.99), die ook de ontwikkeling ondersteunen. Thema\u2019s synchroniseren automatisch tussen al je apparaten.",
         "<p>12 thema\u2019s: Standard, Terminal, Amber, Blue, Neon, Dracula, Nord, Solarized, Catppuccin, Fossil, Monolith en HAL. Standard en de drie retrothema\u2019s (Terminal, Amber, Blue) zijn inbegrepen. Fossil, Monolith, HAL en de rest worden ontgrendeld via optionele fooi\u2011IAP\u2019s ($0.99 / $4.99 / $9.99), die ook de ontwikkeling ondersteunen. Thema\u2019s synchroniseren automatisch tussen al je apparaten.</p>"),
        ("Kan ik meldingen dempen voor een bekend incident?",
         "Ja. Bij een service met een actief incident kun je meldingen voor een ingestelde periode dempen, zodat je niet telkens gewaarschuwd wordt over iets dat je al weet. Dempen kan ook met je stem \u2014 \u201eHey Siri, demp GitHub 2 uur\u201d \u2014 of via de Shortcuts\u2011app.",
         "<p>Ja. Bij een service met een actief incident kun je meldingen voor een ingestelde periode dempen, zodat je niet telkens gewaarschuwd wordt over iets dat je al weet. Dempen kan ook met je stem \u2014 \u201eHey Siri, demp GitHub 2 uur\u201d \u2014 of via de Shortcuts\u2011app.</p>"),
        ("Welke platforms worden ondersteund?",
         "iPhone en iPad (met widgets en Live Activities), Mac (met een menubalk\u2011app plus volledig venster), Apple Watch (met complicaties en Smart Stack), Apple TV en Apple Vision Pro. De app is gratis te downloaden op elk platform.",
         "<p>iPhone en iPad (met widgets en Live Activities), Mac (met een menubalk\u2011app plus volledig venster), Apple Watch (met complicaties en Smart Stack), Apple TV en Apple Vision Pro. De app is gratis te downloaden op elk platform.</p>"),
        ("Kan ik een nieuwe service aanvragen?",
         "Ja! Mail naar support@vultyr.app met de naam van de service en de URL van de statuspagina.",
         "<p>Ja! Mail naar <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a> met de naam van de service en de URL van de statuspagina.</p>"),
    ],
},
    "pt-BR": {
    "html_lang": "pt-BR",
    "og_locale": "pt_BR",
    "og_image_alt": "Ícone do app Vultyr — Monitor de status de serviços",
    "devices": "iPhone, iPad, Mac, Apple Watch, Apple TV e Vision Pro",
    "skip_to_main": "Ir para o conteúdo principal",
    "topbar_brand_aria": "Página inicial do Vultyr",
    "nav_primary_aria": "Principal",
    "nav_services": "serviços",
    "nav_support": "suporte",
    "nav_download": "Baixar",
    "footer_nav_aria": "Navegação do rodapé",
    "footer_home": "Início",
    "footer_services": "Serviços",
    "footer_privacy": "Privacidade",
    "footer_support": "Suporte",
    "footer_contact": "Contato",
    "copyright": "© 2026 Vultyr. Todos os direitos reservados.",
    "breadcrumb_aria": "Trilha de navegação",
    "breadcrumb_vultyr": "Vultyr",
    "breadcrumb_services": "Serviços",
    # services page
    "svcs_title": "Vultyr — 200+ verificações de status",
    "svcs_description": "200+ verificações de status de serviços de nuvem, ferramentas de desenvolvimento, comunicação, IA e muito mais — tudo monitorado pelo Vultyr.",
    "svcs_h1_lead": "Verificações",
    "svcs_h1_highlight": "de status",
    "svcs_subtitle": "200+ verificações de status que o vultyr executa em serviços de nuvem, ferramentas de desenvolvimento e plataformas.",
    "svcs_categories_aria": "Navegar por categoria",
    "svc_row_status": "Página de status",
    "svc_row_homepage": "Site",
    "svcs_item_list_name": "Serviços monitorados pelo Vultyr",
    # service page
    "svcp_title_fmt": "{name} está fora do ar? Monitor de status de {name} | Vultyr",
    "svcp_description_fmt": "Verifique se {name} está fora do ar agora. Atualizações de status em tempo real e monitoramento de quedas de {name} com o Vultyr. Grátis em {devices}.",
    "svcp_live_check": "Verificação em tempo real",
    "svcp_view_current_status": "Ver status atual →",
    "svcp_alert_hint_prefix": "Para receber alertas instantâneos, ",
    "svcp_alert_hint_link": "baixe o Vultyr",
    "svcp_categories_label": "Categorias:",
    "svcp_official_status": "Página de status oficial",
    "svcp_homepage_fmt": "Site de {name}",
    "svcp_faq_heading": "Perguntas frequentes",
    "svcp_faq_q1_fmt": "{name} está fora do ar agora?",
    "svcp_faq_a1_fmt": "Consulte a página de status oficial de {name} no link acima para ver o estado atual. Para monitoramento contínuo com alertas instantâneos de quedas em todos os seus dispositivos Apple, baixe o app Vultyr grátis.",
    "svcp_faq_a1_ld_fmt": "Consulte a página de status oficial de {name} em {url} para ver o estado atual. Baixe o app Vultyr grátis para receber alertas instantâneos de quedas em todos os seus dispositivos Apple.",
    "svcp_faq_q2_fmt": "Como posso monitorar o status de {name}?",
    "svcp_faq_a2_fmt": "O Vultyr monitora {name} como parte de mais de 200 verificações de status em serviços de nuvem, ferramentas de desenvolvimento e plataformas. Receba alertas instantâneos de quedas em {devices} — totalmente grátis.",
    "svcp_faq_a2_ld_fmt": "Baixe o Vultyr (grátis) para monitorar {name} como parte de mais de 200 verificações de status com alertas em tempo real em {devices}. O Vultyr executa cada verificação automaticamente e avisa você assim que uma queda é detectada.",
    "svcp_related_heading": "Serviços relacionados",
    "svcp_related_aria": "Serviços relacionados",
    "svcp_cta_heading_fmt": "Monitore {name} em todos os seus dispositivos",
    "svcp_cta_body_fmt": "Receba alertas instantâneos quando {name} sair do ar. Grátis em todas as plataformas Apple.",
    "cta_download_vultyr": "Baixar o Vultyr",
    "cta_download_vultyr_aria": "Baixar o Vultyr na App Store",
    # category page
    "catp_title_fmt": "Monitor de status de {name} — {count_services} | Vultyr",
    "catp_description_fmt": "Monitore o status de {count_services} em {name_lower}. Alertas de quedas em tempo real para {sample} e muito mais.",
    "catp_item_list_name_fmt": "Monitores de status: {name}",
    "catp_subtitle_fmt": "{count_services} monitorados pelo Vultyr",
    "catp_services_aria_fmt": "Serviços de {name}",
    "catp_other_heading": "Outras categorias",
    "catp_cta_heading_fmt": "Monitore todos os {count_services} instantaneamente",
    "catp_cta_body": "Receba alertas de quedas em tempo real em todos os seus dispositivos Apple. Grátis.",
    # home page
    "home_title": "Vultyr — Monitor de status para AWS, Slack, GitHub e outros",
    "home_description": "Está fora do ar? 200+ verificações de status em serviços de nuvem, ferramentas de desenvolvimento e plataformas com alertas instantâneos de quedas. Grátis no iPhone, iPad, Mac, Apple Watch, Apple TV e Apple Vision Pro.",
    "home_og_title": "Vultyr — Monitor de status de serviços",
    "home_app_ld_description": "Monitore mais de 200 verificações de status em serviços de nuvem, ferramentas de desenvolvimento e plataformas com alertas instantâneos de quedas.",
    "home_hero_tag": "200+ verificações",
    "home_hero_question": "Está fora do ar?",
    "home_hero_answer": "Saiba antes dos seus usuários.",
    "home_hero_services": "200+ verificações de status — AWS, GitHub, Slack, Stripe e muito mais — com alertas instantâneos de quedas em todos os dispositivos Apple.",
    "home_appstore_alt": "Baixar na App Store",
    "home_appstore_aria": "Baixar o Vultyr na App Store",
    "home_free_on_prefix": "Grátis no",
    "home_screenshots_aria": "Capturas de tela do app",
    "home_screenshot_dash_alt": "Painel do Vultyr mostrando o status \"Tudo certo\" com serviços como AWS, GitHub e Slack monitorados",
    "home_screenshot_settings_alt_fmt": "Configurações de aparência do Vultyr com {themes} temas, incluindo Terminal, Amber, Dracula e Nord",
    "home_screenshot_services_alt_fmt": "Navegador de serviços do Vultyr mostrando {categories} categorias, incluindo Cloud, Dev Tools e AI",
    "home_stats_aria": "Números-chave",
    "home_stats_checks": "Verificações",
    "home_stats_categories": "Categorias",
    "home_stats_platforms": "Plataformas",
    "home_stats_languages": "Idiomas",
    "home_features_heading": "Tudo o que você precisa para se antecipar às quedas",
    "home_features_sub": "Sem contas, sem rastreamento no app. Apenas status.",
    "home_bottom_heading": "Pronto para monitorar sua stack?",
    "home_bottom_sub": "Grátis. Sem conta no app. Disponível em todos os lugares.",
    "home_bottom_button": "Baixar grátis",
    "home_bottom_aria": "Baixar o Vultyr grátis na App Store",
    "home_languages_heading": "Disponível em 17 idiomas",
    "home_features": [
        ("chart-bar-regular.svg", "Painel de status em tempo real",
         "AWS, GitHub, Cloudflare, Slack, Stripe, Discord, OpenAI, Anthropic e mais de 200 — tudo em um só lugar. Os indicadores de status sincronizam com ProMotion de 120Hz no iPhone Pro e iPad Pro."),
        ("bell-ringing-regular.svg", "Alertas inteligentes",
         "Notificações de queda e recuperação com o favicon de cada serviço no iOS. Interrupções graves pulsam visivelmente maiores que incidentes menores, para você identificar a gravidade num piscar. Silencie problemas conhecidos e destaque serviços críticos."),
        ("microphone-regular.svg",
         "Siri e Shortcuts",
         "Diga à Siri \"silencie o GitHub por 2 horas\" ou \"mostre os problemas atuais\". App Intents para cada ação, além de um Focus Filter que silencia serviços não críticos."),
        ("squares-four-regular.svg",
         "Widgets e Live Activities",
         "Widgets na Tela de Início e na Tela Bloqueada do iOS, além de um widget na Control Center. Quedas ativas são fixadas na Dynamic Island."),
        ("watch-regular.svg",
         "Complicações no Apple Watch",
         "Fixe um serviço crítico em um mostrador ou deixe a Smart Stack mostrar automaticamente os problemas ativos."),
        ("cloud-check-regular.svg", "Hub no Mac — iPhone como reserva",
         "O Mac é o hub mais confiável: consulta com frequência de até 60 segundos (configurável até 15 min) e transmite mudanças de status ao iPhone, iPad, Watch e Vision Pro via iCloud. Se nenhum Mac estiver online, seu iPhone assume como publicador reserva para que os outros dispositivos continuem recebendo alertas."),
        ("monitor-regular.svg", "Visão de confiabilidade de alertas",
         "Veja de relance se os alertas realmente vão chegar até você — heartbeat do Mac, status da atualização em segundo plano, push do CloudKit e quando cada dispositivo verificou pela última vez."),
        ("devices-regular.svg",
         "Todas as plataformas Apple",
         "iPhone, iPad, barra de menus do Mac, Apple TV, Apple Watch e Vision Pro. Os serviços são sincronizados entre todos os dispositivos."),
        ("lightning-regular.svg",
         "Detalhes dos incidentes",
         "Componentes afetados, incidentes ativos, manutenções programadas e atualizações da linha do tempo — tudo no seu idioma."),
        ("battery-charging-regular.svg", "Verificação consciente da bateria",
         "A atualização automática se adapta à bateria, estado de energia e temperatura. A cada minuto no Mac, 5–15 no iPhone, com atualização em segundo plano no iPad, Apple Watch, Vision Pro e Apple TV."),
        ("palette-regular.svg", f"{THEMES_COUNT} temas",
         "O tema Standard e três temas retrô estão inclusos. Fossil, Monolith, HAL e os demais são desbloqueados por meio de compras dentro do app opcionais, no estilo \"gorjeta\"."),
        ("shield-check-regular.svg",
         "Os dados do app ficam no dispositivo",
         "O app não tem cadastro nem análise interna. Os serviços que você acompanha ficam no seu dispositivo."),
        ("translate-regular.svg", f"{APP_LANGUAGE_COUNT} idiomas do app",
         "Inglês, alemão, francês, espanhol, japonês, coreano, chinês, português, russo e outros."),
    ],
    # 404
    "err_title": "Página não encontrada — Vultyr",
    "err_description": "A página que você está procurando não existe.",
    "err_heading": "Página não encontrada",
    "err_message": "A página que você está procurando não existe ou foi movida.",
    "redirect_moved_fmt": "Esta página foi movida. Redirecionando para {name}…",
    "err_popular_heading": "Serviços populares",
    "err_browse_heading": "Ver categorias",
    # privacy
    "privacy_title": "Política de privacidade",
    "privacy_description": "Política de privacidade do Vultyr. O app não coleta dados pessoais. Este site usa Google Analytics sem cookies para estatísticas agregadas de visitantes.",
    "privacy_last_updated": "Atualizado em: 11 de abril de 2026",
    "privacy_sections": [
        ("Resumo",
         "<p>O <strong>app</strong> Vultyr não coleta, não armazena nem transmite nenhum dado pessoal. O <strong>site</strong> do Vultyr (vultyr.app) usa Google Analytics sem cookies para entender estatísticas agregadas de visitantes. Esta página detalha os dois pontos.</p>"),
        ("App — Coleta de dados",
         "<p>O app vultyr não coleta nenhuma informação pessoal. Ele não exige cadastro, não inclui nenhum SDK de análise ou rastreamento de terceiros e não envia dados para nenhum servidor operado por nós.</p>"),
        ("App — Requisições de rede",
         "<p>O app faz requisições HTTPS diretas para APIs públicas de páginas de status (como Statuspage.io, Apple, Google Cloud e outras) para verificar o status dos serviços. Essas requisições vão direto do seu dispositivo para a API pública do serviço — elas não passam por nenhum servidor operado por nós.</p>"),
        ("App — Armazenamento de dados",
         "<p>Todos os dados são armazenados localmente no seu dispositivo usando o framework SwiftData da Apple. Se você ativar a sincronização via iCloud, sua lista de serviços acompanhados é sincronizada pelo iCloud Key-Value Store da Apple, regido pela política de privacidade da Apple. Nós nunca vemos esses dados.</p>"),
        ("App — Alertas entre dispositivos",
         "<p>Se você ativar os Alertas entre dispositivos, as mudanças de status são compartilhadas entre seus dispositivos pelo iCloud Key-Value Store da Apple. Quando seu Mac detecta uma mudança de status, ele grava um sinal leve na sua conta do iCloud. Seus outros dispositivos observam a mudança e fazem sua própria verificação local. Nenhum servidor de terceiros é envolvido — toda a comunicação passa pela infraestrutura do iCloud da Apple. Você pode ativar ou desativar esse recurso em qualquer dispositivo.</p>"),
        ("App — Favicons",
         "<p>Os favicons dos serviços são obtidos pelo serviço público de favicons do Google e armazenados em cache localmente no seu dispositivo.</p>"),
        ("Site — Analytics",
         "<p>Este site (vultyr.app) usa o Google Analytics 4 no modo sem cookies e com IP anonimizado para contar visualizações agregadas de página. Especificamente, configuramos o gtag.js com <code>anonymize_ip: true</code>, <code>client_storage: 'none'</code>, <code>allow_google_signals: false</code> e <code>allow_ad_personalization_signals: false</code>. Isso significa que nenhum cookie <code>_ga</code> é definido, seu IP é truncado antes do armazenamento e nenhum identificador de anúncios é coletado. O próprio app vultyr não inclui nenhum tipo de analytics.</p>"),
        ("Site — Domínios de terceiros",
         "<p>Carregar o vultyr.app entra em contato com os seguintes domínios de terceiros:</p>\n    <ul>\n        <li><strong>www.googletagmanager.com</strong> — carrega o script do gtag.js</li>\n        <li><strong>www.google-analytics.com</strong> / <strong>*.analytics.google.com</strong> — recebe os beacons anônimos de visualização de página</li>\n        <li><strong>www.google.com/g/collect</strong> — recebe os mesmos beacons anônimos de visualização de página (endpoint de coleta de fallback do Google Analytics 4)</li>\n    </ul>\n    <p>Não carregamos o Google Fonts (a fonte Audiowide é hospedada no próprio vultyr.app) e não usamos um serviço de favicons de terceiros para as imagens do site.</p>"),
        ("App — Serviços de terceiros",
         "<p>O app vultyr não se integra com nenhum serviço de terceiros de análise, publicidade ou rastreamento. As únicas requisições externas são para APIs públicas de páginas de status e para o serviço de favicons do Google.</p>"),
        ("Privacidade de crianças",
         "<p>O app vultyr não coleta dados de ninguém, incluindo crianças com menos de 13 anos. O site registra apenas contagens anônimas e agregadas de visitantes.</p>"),
        ("Alterações",
         "<p>Se esta política mudar, atualizaremos a data acima.</p>"),
        ("Contato",
         "<p>Dúvidas? Escreva para <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a></p>"),
    ],
    # support
    "support_title": "Suporte",
    "support_description": "Receba ajuda com o Vultyr, o monitor de status de serviços para iPhone, iPad, Mac, Apple Watch, Apple TV e Apple Vision Pro. Perguntas frequentes, contato e solução de problemas.",
    "support_contact_heading": "Contato",
    "support_contact_html": "<p>Para relatar bugs, sugerir recursos ou tirar dúvidas:<br>\n    <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a></p>",
    "support_faq_heading": "Perguntas frequentes",
    "support_faqs": [
        ("Com que frequência o vultyr verifica o status dos serviços?",
         "No Mac: com a frequência de até 60 segundos quando está conectado à tomada (configurável até 15 min). No iPhone: a cada 5, 10 ou 15 minutos (configurável), com verificações periódicas em segundo plano quando as condições permitem. No Apple Watch: a cada 15 minutos. Na Apple TV: a cada 5 minutos. A frequência de verificação se adapta automaticamente ao nível da bateria, ao estado de energia e às condições térmicas.",
         "<p>No Mac: com a frequência de até 60 segundos quando está conectado à tomada (configurável até 15 min). No iPhone: a cada 5, 10 ou 15 minutos (configurável), com verificações periódicas em segundo plano quando as condições permitem. No Apple Watch: a cada 15 minutos. Na Apple TV: a cada 5 minutos. A frequência de verificação se adapta automaticamente ao nível da bateria, ao estado de energia e às condições térmicas.</p>"),
        ("Como funcionam os Alertas entre dispositivos?",
         "O app para Mac é o hub. Mantenha-o em execução (na barra de menus ou em janela completa) e ele faz verificações com frequência de até 60 segundos (configurável até 15 min). Quando detecta uma mudança de status, grava um sinal leve no iCloud Key-Value Store; seu iPhone, iPad, Watch, Apple TV e Vision Pro captam a mudança e fazem sua própria verificação local. Sem chaves, sem tokens, sem configuração — basta ativar \"Alertas entre dispositivos\" nos ajustes em qualquer dispositivo. Sem um Mac atuando como hub, os alertas dependem da execução em segundo plano do iOS e podem atrasar ou ser perdidos.",
         "<p>O app para Mac é o hub. Mantenha-o em execução (na barra de menus ou em janela completa) e ele faz verificações com frequência de até 60 segundos (configurável até 15 min). Quando detecta uma mudança de status, grava um sinal leve no iCloud Key-Value Store; seu iPhone, iPad, Watch, Apple TV e Vision Pro captam a mudança e fazem sua própria verificação local. Sem chaves, sem tokens, sem configuração — basta ativar \"Alertas entre dispositivos\" nos ajustes em qualquer dispositivo. Sem um Mac atuando como hub, os alertas dependem da execução em segundo plano do iOS e podem atrasar ou ser perdidos.</p>"),
        ("Eu preciso do app para Mac para ter alertas confiáveis?",
         "Sim — recomendamos fortemente. O iOS limita a execução em segundo plano, então iPhone e iPad só podem verificar a cada 5 a 15 minutos (configurável) e podem adiar ainda mais com bateria fraca, Modo de Pouca Energia ou conectividade ruim. O app para Mac faz verificações com frequência de até 60 segundos quando está conectado à tomada (configurável até 15 min) e transmite mudanças de status para seus outros dispositivos via iCloud. Sem um Mac rodando o Vultyr, os alertas no iOS, watchOS e tvOS ainda funcionam, mas podem atrasar bastante ou ser perdidos. Para monitoramento em tempo real, mantenha o app para Mac em execução — ele é minúsculo na barra de menus e é assim que o Vultyr foi feito para ser usado.",
         "<p>Sim — recomendamos fortemente. O iOS limita a execução em segundo plano, então iPhone e iPad só podem verificar a cada 5 a 15 minutos (configurável) e podem adiar ainda mais com bateria fraca, Modo de Pouca Energia ou conectividade ruim. O app para Mac faz verificações com frequência de até 60 segundos quando está conectado à tomada (configurável até 15 min) e transmite mudanças de status para seus outros dispositivos via iCloud. Sem um Mac rodando o Vultyr, os alertas no iOS, watchOS e tvOS ainda funcionam, mas podem atrasar bastante ou ser perdidos. Para monitoramento em tempo real, mantenha o app para Mac em execução — ele é minúsculo na barra de menus e é assim que o Vultyr foi feito para ser usado.</p>"),
        ("O vultyr funciona com Siri e Shortcuts?",
         "Sim. Os App Intents integrados permitem dizer \"E aí Siri, silencie o GitHub por 2 horas\", \"verifique o status do Stripe\" ou \"mostre os problemas atuais\", e você pode conectar essas mesmas ações ao app Shortcuts. Também há um Focus Filter para que um modo \"Focus do vultyr\" silencie serviços não críticos automaticamente.",
         "<p>Sim. Os App Intents integrados permitem dizer \"E aí Siri, silencie o GitHub por 2 horas\", \"verifique o status do Stripe\" ou \"mostre os problemas atuais\", e você pode conectar essas mesmas ações ao app Shortcuts. Também há um Focus Filter para que um modo \"Focus do vultyr\" silencie serviços não críticos automaticamente.</p>"),
        ("Existem widgets e Live Activities?",
         "No iOS, há widgets de Tela de Início e Tela Bloqueada (de serviço único e resumo de status), além de um widget de Control Center. Quedas ativas são fixadas na Dynamic Island como Live Activities. No watchOS, há complicações para todos os mostradores, com relevância para a Smart Stack, então o serviço certo aparece quando algo cai.",
         "<p>No iOS, há widgets de Tela de Início e Tela Bloqueada (de serviço único e resumo de status), além de um widget de Control Center. Quedas ativas são fixadas na Dynamic Island como Live Activities. No watchOS, há complicações para todos os mostradores, com relevância para a Smart Stack, então o serviço certo aparece quando algo cai.</p>"),
        ("O app vultyr coleta meus dados?",
         "Não. O app não tem contas, rastreamento interno nem análise interna. Todos os serviços que você acompanha ficam no seu dispositivo. Observação: este site (vultyr.app) usa Google Analytics sem cookies para contagens agregadas de visitantes — veja a Política de privacidade para detalhes.",
         "<p>Não. O app não tem contas, rastreamento interno nem análise interna. Todos os serviços que você acompanha ficam no seu dispositivo. Observação: este site (vultyr.app) usa Google Analytics sem cookies para contagens agregadas de visitantes — veja a <a href=\"/pt-BR/privacy.html\">Política de privacidade</a> para detalhes.</p>"),
        ("Como sincronizo meus serviços entre dispositivos?",
         "Os serviços que você acompanha são sincronizados automaticamente via iCloud. Temas e ajustes também são sincronizados entre todos os seus dispositivos Apple pelo iCloud Key-Value Store.",
         "<p>Os serviços que você acompanha são sincronizados automaticamente via iCloud. Temas e ajustes também são sincronizados entre todos os seus dispositivos Apple pelo iCloud Key-Value Store.</p>"),
        ("Quais são as opções de tema?",
         "12 temas: Standard, Terminal, Amber, Blue, Neon, Dracula, Nord, Solarized, Catppuccin, Fossil, Monolith e HAL. O Standard e os três temas retrô (Terminal, Amber, Blue) estão inclusos. Fossil, Monolith, HAL e os demais são desbloqueados por compras dentro do app opcionais no estilo \"gorjeta\" ($0,99 / $4,99 / $9,99), o que também ajuda a financiar o desenvolvimento. Os temas são sincronizados entre todos os seus dispositivos automaticamente.",
         "<p>12 temas: Standard, Terminal, Amber, Blue, Neon, Dracula, Nord, Solarized, Catppuccin, Fossil, Monolith e HAL. O Standard e os três temas retrô (Terminal, Amber, Blue) estão inclusos. Fossil, Monolith, HAL e os demais são desbloqueados por compras dentro do app opcionais no estilo \"gorjeta\" ($0,99 / $4,99 / $9,99), o que também ajuda a financiar o desenvolvimento. Os temas são sincronizados entre todos os seus dispositivos automaticamente.</p>"),
        ("Posso silenciar notificações de um incidente conhecido?",
         "Sim. Ao visualizar um serviço com um incidente ativo, você pode silenciar as notificações por um período definido para não receber alertas repetidos sobre algo que já sabe. Também dá para silenciar por voz — \"E aí Siri, silencie o GitHub por 2 horas\" — ou pelo app Shortcuts.",
         "<p>Sim. Ao visualizar um serviço com um incidente ativo, você pode silenciar as notificações por um período definido para não receber alertas repetidos sobre algo que já sabe. Também dá para silenciar por voz — \"E aí Siri, silencie o GitHub por 2 horas\" — ou pelo app Shortcuts.</p>"),
        ("Quais plataformas são suportadas?",
         "iPhone e iPad (com widgets e Live Activities), Mac (com app na barra de menus e em janela completa), Apple Watch (com complicações e Smart Stack), Apple TV e Apple Vision Pro. O app é gratuito para baixar em todas as plataformas.",
         "<p>iPhone e iPad (com widgets e Live Activities), Mac (com app na barra de menus e em janela completa), Apple Watch (com complicações e Smart Stack), Apple TV e Apple Vision Pro. O app é gratuito para baixar em todas as plataformas.</p>"),
        ("Posso sugerir um novo serviço?",
         "Sim! Escreva para support@vultyr.app com o nome do serviço e a URL da página de status dele.",
         "<p>Sim! Escreva para <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a> com o nome do serviço e a URL da página de status dele.</p>"),
    ],
},
    "sv": {
    "html_lang": "sv",
    "og_locale": "sv_SE",
    "og_image_alt": "Vultyr-appikon — tjänstestatusövervakare",
    "devices": "iPhone, iPad, Mac, Apple Watch, Apple TV och Vision Pro",
    "skip_to_main": "Hoppa till huvudinnehåll",
    "topbar_brand_aria": "Vultyr start",
    "nav_primary_aria": "Primär",
    "nav_services": "tjänster",
    "nav_support": "support",
    "nav_download": "Ladda ner",
    "footer_nav_aria": "Sidfotsnavigering",
    "footer_home": "Start",
    "footer_services": "Tjänster",
    "footer_privacy": "Integritet",
    "footer_support": "Support",
    "footer_contact": "Kontakt",
    "copyright": "© 2026 Vultyr. Alla rättigheter förbehållna.",
    "breadcrumb_aria": "Brödsmulor",
    "breadcrumb_vultyr": "Vultyr",
    "breadcrumb_services": "Tjänster",
    # services page
    "svcs_title": "Vultyr — 200+ statuskontroller",
    "svcs_description": "200+ statuskontroller av molntjänster, utvecklarverktyg, kommunikation, AI och mycket mer — allt övervakat av Vultyr.",
    "svcs_h1_lead": "Status-",
    "svcs_h1_highlight": "kontroller",
    "svcs_subtitle": "200+ statuskontroller som vultyr kör för molntjänster, utvecklarverktyg och plattformar.",
    "svcs_categories_aria": "Bläddra efter kategori",
    "svc_row_status": "Statussida",
    "svc_row_homepage": "Webbplats",
    "svcs_item_list_name": "Tjänster som övervakas av Vultyr",
    # service page
    "svcp_title_fmt": "Är {name} nere? Statusövervakare för {name} | Vultyr",
    "svcp_description_fmt": "Kontrollera om {name} är nere just nu. Live-uppdateringar av {name}-status och övervakning av driftstörningar med Vultyr. Gratis på {devices}.",
    "svcp_live_check": "Live-kontroll",
    "svcp_view_current_status": "Visa aktuell status →",
    "svcp_alert_hint_prefix": "För direkta aviseringar, ",
    "svcp_alert_hint_link": "ladda ner Vultyr",
    "svcp_categories_label": "Kategorier:",
    "svcp_official_status": "Officiell statussida",
    "svcp_homepage_fmt": "Webbplats för {name}",
    "svcp_faq_heading": "Vanliga frågor",
    "svcp_faq_q1_fmt": "Är {name} nere just nu?",
    "svcp_faq_a1_fmt": "Kontrollera den officiella statussidan för {name} som är länkad ovan för att se aktuell status. För kontinuerlig övervakning med direkta aviseringar om driftstörningar på alla dina Apple-enheter, ladda ner den kostnadsfria Vultyr-appen.",
    "svcp_faq_a1_ld_fmt": "Kontrollera den officiella statussidan för {name} på {url} för aktuell status. Ladda ner den kostnadsfria Vultyr-appen för direkta aviseringar om driftstörningar på alla dina Apple-enheter.",
    "svcp_faq_q2_fmt": "Hur kan jag övervaka statusen för {name}?",
    "svcp_faq_a2_fmt": "Vultyr övervakar {name} som en del av 200+ statuskontroller för molntjänster, utvecklarverktyg och plattformar. Få direkta aviseringar om driftstörningar på {devices} — helt gratis.",
    "svcp_faq_a2_ld_fmt": "Ladda ner Vultyr (gratis) för att övervaka {name} som en del av 200+ statuskontroller med realtidsaviseringar på {devices}. Vultyr kör varje kontroll automatiskt och meddelar dig i samma ögonblick som en driftstörning upptäcks.",
    "svcp_related_heading": "Relaterade tjänster",
    "svcp_related_aria": "Relaterade tjänster",
    "svcp_cta_heading_fmt": "Övervaka {name} på alla dina enheter",
    "svcp_cta_body_fmt": "Få direkta aviseringar när {name} ligger nere. Gratis på alla Apple-plattformar.",
    "cta_download_vultyr": "Ladda ner Vultyr",
    "cta_download_vultyr_aria": "Ladda ner Vultyr från App Store",
    # category page
    "catp_title_fmt": "Statusövervakare för {name} — {count_services} | Vultyr",
    "catp_description_fmt": "Övervaka status för {count_services} inom {name_lower}. Realtidsaviseringar om driftstörningar för {sample} med flera.",
    "catp_item_list_name_fmt": "Statusövervakare för {name}",
    "catp_subtitle_fmt": "{count_services} övervakade av Vultyr",
    "catp_services_aria_fmt": "Tjänster i {name}",
    "catp_other_heading": "Andra kategorier",
    "catp_cta_heading_fmt": "Övervaka alla {count_services} direkt",
    "catp_cta_body": "Få realtidsaviseringar om driftstörningar på alla dina Apple-enheter. Gratis.",
    # home page
    "home_title": "Vultyr — statusövervakare för AWS, Slack, GitHub och mer",
    "home_description": "Ligger det nere? 200+ statuskontroller av molntjänster, utvecklarverktyg och plattformar med direkta aviseringar om driftstörningar. Gratis på iPhone, iPad, Mac, Apple Watch, Apple TV och Apple Vision Pro.",
    "home_og_title": "Vultyr — tjänstestatusövervakare",
    "home_app_ld_description": "Övervaka 200+ statuskontroller av molntjänster, utvecklarverktyg och plattformar med direkta aviseringar om driftstörningar.",
    "home_hero_tag": "200+ kontroller",
    "home_hero_question": "Ligger det nere?",
    "home_hero_answer": "Vet det före dina användare.",
    "home_hero_services": "200+ statuskontroller — AWS, GitHub, Slack, Stripe &amp; mer — med direkta aviseringar om driftstörningar på varje Apple-enhet.",
    "home_appstore_alt": "Ladda ner från App Store",
    "home_appstore_aria": "Ladda ner Vultyr från App Store",
    "home_free_on_prefix": "Gratis på",
    "home_screenshots_aria": "Skärmbilder från appen",
    "home_screenshot_dash_alt": "Vultyr-instrumentpanel som visar statusen Allt klart med tjänster som AWS, GitHub och Slack under övervakning",
    "home_screenshot_settings_alt_fmt": "Vultyrs utseendeinställningar med {themes} teman inklusive Terminal, Amber, Dracula och Nord",
    "home_screenshot_services_alt_fmt": "Vultyrs tjänstebläddrare som visar {categories} kategorier inklusive Cloud, Dev Tools och AI",
    "home_stats_aria": "Nyckeltal",
    "home_stats_checks": "Kontroller",
    "home_stats_categories": "Kategorier",
    "home_stats_platforms": "Plattformar",
    "home_stats_languages": "Språk",
    "home_features_heading": "Allt du behöver för att ligga steget före driftstörningar",
    "home_features_sub": "Inga appkonton, ingen spårning i appen. Bara status.",
    "home_bottom_heading": "Redo att övervaka din stack?",
    "home_bottom_sub": "Gratis. Inget appkonto krävs. Tillgängligt överallt.",
    "home_bottom_button": "Ladda ner gratis",
    "home_bottom_aria": "Ladda ner Vultyr gratis från App Store",
    "home_languages_heading": "Tillgänglig på 17 språk",
    "home_features": [
        ("chart-bar-regular.svg", "Live-statusinstrumentpanel",
         "AWS, GitHub, Cloudflare, Slack, Stripe, Discord, OpenAI, Anthropic och 200+ till — allt på ett ställe. Statusindikatorerna synkroniseras med 120Hz ProMotion på iPhone Pro och iPad Pro."),
        ("bell-ringing-regular.svg", "Smarta aviseringar",
         "Aviseringar om avbrott och återställning med varje tjänsts favicon på iOS. Stora avbrott pulserar tydligt större än små incidenter så allvarlighetsgraden syns direkt. Tysta kända incidenter, stjärnmärk kritiska tjänster."),
        ("microphone-regular.svg", "Siri och Shortcuts",
         "Be Siri ”tysta GitHub i 2 timmar” eller ”visa aktuella problem”. App Intents för varje åtgärd, plus ett Focus-filter som tystar icke-kritiska tjänster."),
        ("squares-four-regular.svg", "Widgets och Live Activities",
         "Widgets på hemskärmen och låsskärmen på iOS, plus en widget i Control Center. Aktiva driftstörningar fästs i Dynamic Island."),
        ("watch-regular.svg", "Klockkomplikationer",
         "Fäst en kritisk tjänst på en urtavla eller låt Smart Stack automatiskt lyfta fram aktiva problem."),
        ("cloud-check-regular.svg", "Mac-hub — iPhone som reserv",
         "Mac är den pålitligaste huben: den pollar så ofta som var 60:e sekund (kan ställas in upp till 15 min) och skickar statusförändringar till iPhone, iPad, Watch och Vision Pro via iCloud. Om ingen Mac är online tar din iPhone över som reservavsändare så att de andra enheterna fortfarande får aviseringar."),
        ("monitor-regular.svg", "Vy över aviseringarnas tillförlitlighet",
         "Se med en blick om aviseringarna verkligen når fram — Mac-hjärtslag, status för bakgrundsuppdatering, CloudKit-push och när varje enhet senast kollade."),
        ("devices-regular.svg", "Varje Apple-plattform",
         "iPhone, iPad, Mac-menyrad, Apple TV, Apple Watch och Vision Pro. Tjänster synkroniseras mellan alla enheter."),
        ("lightning-regular.svg", "Incidentdetaljer",
         "Berörda komponenter, aktiva incidenter, planerat underhåll och tidslinjeuppdateringar — lokaliserade till ditt språk."),
        ("battery-charging-regular.svg", "Batterismart avsökning",
         "Smart automatisk uppdatering anpassas efter batteri, strömtillstånd och temperatur. Varje minut på Mac, 5–15 på iPhone, med bakgrundsuppdatering på iPad, Apple Watch, Vision Pro och Apple TV."),
        ("palette-regular.svg", f"{THEMES_COUNT} teman",
         "Standard och tre retroteman ingår. Fossil, Monolith, HAL och de övriga låses upp via valfria dricksburks-IAP:er."),
        ("shield-check-regular.svg", "Appdata stannar lokalt",
         "Appen har ingen registrering och ingen analys i appen. Dina bevakade tjänster stannar på din enhet."),
        ("translate-regular.svg", f"{APP_LANGUAGE_COUNT} appspråk",
         "Engelska, tyska, franska, spanska, japanska, koreanska, kinesiska, portugisiska, ryska och fler."),
    ],
    # 404
    "err_title": "Sidan hittades inte — Vultyr",
    "err_description": "Sidan du letar efter finns inte.",
    "err_heading": "Sidan hittades inte",
    "err_message": "Sidan du letar efter finns inte eller har flyttats.",
    "redirect_moved_fmt": "Den här sidan har flyttats. Omdirigerar till {name}…",
    "err_popular_heading": "Populära tjänster",
    "err_browse_heading": "Bläddra bland kategorier",
    # privacy
    "privacy_title": "Integritetspolicy",
    "privacy_description": "Integritetspolicy för Vultyr. Appen samlar inte in några personuppgifter. Den här webbplatsen använder cookielös Google Analytics för aggregerad besökstrafik.",
    "privacy_last_updated": "Senast uppdaterad: 11 april 2026",
    "privacy_sections": [
        ("Sammanfattning",
         "<p>Vultyr-<strong>appen</strong> samlar inte in, lagrar eller överför några personuppgifter. Vultyr-<strong>webbplatsen</strong> (vultyr.app) använder cookielös Google Analytics för att förstå aggregerad besökstrafik. Denna sida förklarar båda i detalj.</p>"),
        ("Appen — datainsamling",
         "<p>Vultyr-appen samlar inte in någon personlig information. Den kräver inget konto, innehåller inga tredjeparts-SDK:er för analys eller spårning och ringer inte hem till någon server som vi driver.</p>"),
        ("Appen — nätverksförfrågningar",
         "<p>Appen gör direkta HTTPS-förfrågningar till offentliga statussides-API:er (såsom Statuspage.io, Apple, Google Cloud och andra) för att kontrollera tjänsternas status. Dessa förfrågningar går direkt från din enhet till tjänstens offentliga API — de passerar inte via någon server som vi driver.</p>"),
        ("Appen — datalagring",
         "<p>All data lagras lokalt på din enhet med Apples SwiftData-ramverk. Om du aktiverar iCloud-synkronisering synkroniseras din lista med bevakade tjänster via Apples iCloud Key-Value Store, som styrs av Apples integritetspolicy. Vi ser aldrig dessa data.</p>"),
        ("Appen — aviseringar mellan enheter",
         "<p>Om du aktiverar aviseringar mellan enheter delas statusändringar mellan dina enheter via Apples iCloud Key-Value Store. När din Mac upptäcker en statusändring skriver den en lättviktssignal till ditt iCloud-konto. Dina andra enheter observerar ändringen och kör sin egen lokala kontroll. Ingen tredjepartsserver är inblandad — all kommunikation går via Apples iCloud-infrastruktur. Du kan slå på eller av detta från valfri enhet.</p>"),
        ("Appen — favikoner",
         "<p>Tjänsternas favikoner hämtas från Googles offentliga favikontjänst och cachas lokalt på din enhet.</p>"),
        ("Webbplatsen — analys",
         "<p>Den här webbplatsen (vultyr.app) använder Google Analytics 4 i cookielöst, IP-anonymiserat läge för att räkna aggregerade sidvisningar. Mer specifikt konfigurerar vi gtag.js med <code>anonymize_ip: true</code>, <code>client_storage: 'none'</code>, <code>allow_google_signals: false</code> och <code>allow_ad_personalization_signals: false</code>. Det innebär att ingen <code>_ga</code>-cookie sätts, din IP trunkeras före lagring och inga annonsidentifierare samlas in. Själva Vultyr-appen innehåller ingen analys.</p>"),
        ("Webbplatsen — tredjepartsdomäner",
         "<p>Att ladda vultyr.app kontaktar följande tredjepartsdomäner:</p>\n    <ul>\n        <li><strong>www.googletagmanager.com</strong> — laddar gtag.js-skriptet</li>\n        <li><strong>www.google-analytics.com</strong> / <strong>*.analytics.google.com</strong> — tar emot anonymiserade sidvisningssignaler</li>\n        <li><strong>www.google.com/g/collect</strong> — tar emot samma anonymiserade sidvisningssignaler (reserv-endpoint för Google Analytics 4)</li>\n    </ul>\n    <p>Vi laddar inte Google Fonts (typsnittet Audiowide är självhostat på vultyr.app) och använder inte en tredjeparts favikontjänst för webbplatsens eget bildmaterial.</p>"),
        ("Appen — tredjepartstjänster",
         "<p>Vultyr-appen integrerar inte med några tredjepartstjänster för analys, annonsering eller spårning. De enda externa förfrågningarna går till offentliga status-API:er och Googles favikontjänst.</p>"),
        ("Barns integritet",
         "<p>Vultyr-appen samlar inte in data från någon, inklusive barn under 13 år. Webbplatsen loggar endast anonymiserade, aggregerade besöksräkningar.</p>"),
        ("Ändringar",
         "<p>Om denna policy ändras uppdaterar vi datumet ovan.</p>"),
        ("Kontakt",
         "<p>Frågor? Mejla <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a></p>"),
    ],
    # support
    "support_title": "Support",
    "support_description": "Få hjälp med Vultyr, tjänstestatusövervakaren för iPhone, iPad, Mac, Apple Watch, Apple TV och Apple Vision Pro. Vanliga frågor, kontakt och felsökning.",
    "support_contact_heading": "Kontakt",
    "support_contact_html": "<p>För felrapporter, funktionsförfrågningar eller frågor:<br>\n    <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a></p>",
    "support_faq_heading": "Vanliga frågor",
    "support_faqs": [
        ("Hur ofta kontrollerar vultyr tjänsternas status?",
         "På Mac: så ofta som var 60:e sekund när den är ansluten till ström (kan ställas in upp till 15 min). På iPhone: var 5:e, 10:e eller 15:e minut (kan konfigureras), med periodiska bakgrundskontroller när förhållandena tillåter. På Apple Watch: var 15:e minut. På Apple TV: var 5:e minut. Avsökningen anpassas automatiskt efter batterinivå, strömförsörjning och värmeförhållanden.",
         "<p>På Mac: så ofta som var 60:e sekund när den är ansluten till ström (kan ställas in upp till 15 min). På iPhone: var 5:e, 10:e eller 15:e minut (kan konfigureras), med periodiska bakgrundskontroller när förhållandena tillåter. På Apple Watch: var 15:e minut. På Apple TV: var 5:e minut. Avsökningen anpassas automatiskt efter batterinivå, strömförsörjning och värmeförhållanden.</p>"),
        ("Hur fungerar aviseringar mellan enheter?",
         "Mac-appen är navet. Håll den igång (i menyraden eller i ett fullständigt fönster) så avsöker den så ofta som var 60:e sekund (kan ställas in upp till 15 min). När en statusändring upptäcks skriver den en lättviktssignal till iCloud Key-Value Store; din iPhone, iPad, Watch, Apple TV och Vision Pro uppfattar ändringen och kör sin egen lokala kontroll. Inga nycklar, inga tokens, ingen inställning — aktivera bara ”Aviseringar mellan enheter” i inställningarna på valfri enhet. Utan en Mac som nav förlitar sig aviseringarna på iOS bakgrundsexekvering och kommer att fördröjas eller missas.",
         "<p>Mac-appen är navet. Håll den igång (i menyraden eller i ett fullständigt fönster) så avsöker den så ofta som var 60:e sekund (kan ställas in upp till 15 min). När en statusändring upptäcks skriver den en lättviktssignal till iCloud Key-Value Store; din iPhone, iPad, Watch, Apple TV och Vision Pro uppfattar ändringen och kör sin egen lokala kontroll. Inga nycklar, inga tokens, ingen inställning — aktivera bara ”Aviseringar mellan enheter” i inställningarna på valfri enhet. Utan en Mac som nav förlitar sig aviseringarna på iOS bakgrundsexekvering och kommer att fördröjas eller missas.</p>"),
        ("Behöver jag Mac-appen för tillförlitliga aviseringar?",
         "Ja — vi rekommenderar det starkt. iOS begränsar bakgrundsexekvering, så iPhone och iPad kan bara kontrollera var 5:e till 15:e minut (kan konfigureras) och kan fördröja ytterligare vid låg batterinivå, lågenergiläge eller dålig uppkoppling. Mac-appen avsöker så ofta som var 60:e sekund när den är ansluten till ström (kan ställas in upp till 15 min) och skickar statusändringar till dina andra enheter via iCloud. Utan en Mac som kör Vultyr fungerar aviseringar på iOS, watchOS och tvOS fortfarande men kan fördröjas betydligt eller missas. För realtidsövervakning, håll Mac-appen igång — den är liten i menyraden och är så Vultyr är avsedd att användas.",
         "<p>Ja — vi rekommenderar det starkt. iOS begränsar bakgrundsexekvering, så iPhone och iPad kan bara kontrollera var 5:e till 15:e minut (kan konfigureras) och kan fördröja ytterligare vid låg batterinivå, lågenergiläge eller dålig uppkoppling. Mac-appen avsöker så ofta som var 60:e sekund när den är ansluten till ström (kan ställas in upp till 15 min) och skickar statusändringar till dina andra enheter via iCloud. Utan en Mac som kör Vultyr fungerar aviseringar på iOS, watchOS och tvOS fortfarande men kan fördröjas betydligt eller missas. För realtidsövervakning, håll Mac-appen igång — den är liten i menyraden och är så Vultyr är avsedd att användas.</p>"),
        ("Fungerar vultyr med Siri och Shortcuts?",
         "Ja. Inbyggda App Intents låter dig säga ”Hey Siri, tysta GitHub i 2 timmar”, ”kolla Stripe-status” eller ”visa aktuella problem”, och du kan koppla samma åtgärder till Shortcuts-appen. Det finns även ett Focus-filter så att ett ”vultyr Focus”-läge automatiskt kan tysta icke-kritiska tjänster.",
         "<p>Ja. Inbyggda App Intents låter dig säga ”Hey Siri, tysta GitHub i 2 timmar”, ”kolla Stripe-status” eller ”visa aktuella problem”, och du kan koppla samma åtgärder till Shortcuts-appen. Det finns även ett Focus-filter så att ett ”vultyr Focus”-läge automatiskt kan tysta icke-kritiska tjänster.</p>"),
        ("Finns det widgets och Live Activities?",
         "På iOS finns widgets på hemskärmen och låsskärmen (enskild tjänst och statussammanfattning) plus en widget i Control Center. Aktiva driftstörningar fästs i Dynamic Island som Live Activities. På watchOS finns komplikationer för alla urtavlor, med Smart Stack-relevans så att rätt tjänst lyfts fram när något ligger nere.",
         "<p>På iOS finns widgets på hemskärmen och låsskärmen (enskild tjänst och statussammanfattning) plus en widget i Control Center. Aktiva driftstörningar fästs i Dynamic Island som Live Activities. På watchOS finns komplikationer för alla urtavlor, med Smart Stack-relevans så att rätt tjänst lyfts fram när något ligger nere.</p>"),
        ("Samlar vultyr-appen in mina data?",
         "Nej. Appen har inga konton, ingen spårning i appen och ingen analys i appen. Alla dina bevakade tjänster stannar på din enhet. Observera: denna webbplats (vultyr.app) använder cookielös Google Analytics för aggregerade besöksräkningar — se integritetspolicyn för detaljer.",
         "<p>Nej. Appen har inga konton, ingen spårning i appen och ingen analys i appen. Alla dina bevakade tjänster stannar på din enhet. Observera: denna webbplats (vultyr.app) använder cookielös Google Analytics för aggregerade besöksräkningar — se <a href=\"/sv/privacy.html\">integritetspolicyn</a> för detaljer.</p>"),
        ("Hur synkroniserar jag mina tjänster mellan enheter?",
         "Dina bevakade tjänster synkroniseras automatiskt via iCloud. Teman och inställningar synkroniseras också mellan alla dina Apple-enheter via iCloud Key-Value Store.",
         "<p>Dina bevakade tjänster synkroniseras automatiskt via iCloud. Teman och inställningar synkroniseras också mellan alla dina Apple-enheter via iCloud Key-Value Store.</p>"),
        ("Vilka temaalternativ finns det?",
         "12 teman: Standard, Terminal, Amber, Blue, Neon, Dracula, Nord, Solarized, Catppuccin, Fossil, Monolith och HAL. Standard och de tre retrotemana (Terminal, Amber, Blue) ingår. Fossil, Monolith, HAL och de övriga låses upp via valfria dricksburks-IAP:er ($0.99 / $4.99 / $9.99), vilket också hjälper till att finansiera utvecklingen. Teman synkroniseras automatiskt mellan alla dina enheter.",
         "<p>12 teman: Standard, Terminal, Amber, Blue, Neon, Dracula, Nord, Solarized, Catppuccin, Fossil, Monolith och HAL. Standard och de tre retrotemana (Terminal, Amber, Blue) ingår. Fossil, Monolith, HAL och de övriga låses upp via valfria dricksburks-IAP:er ($0.99 / $4.99 / $9.99), vilket också hjälper till att finansiera utvecklingen. Teman synkroniseras automatiskt mellan alla dina enheter.</p>"),
        ("Kan jag tysta aviseringar för en känd incident?",
         "Ja. När du visar en tjänst med en aktiv incident kan du tysta aviseringar under en viss period så att du inte upprepade gånger meddelas om något du redan känner till. Du kan också tysta med rösten — ”Hey Siri, tysta GitHub i 2 timmar” — eller från Shortcuts-appen.",
         "<p>Ja. När du visar en tjänst med en aktiv incident kan du tysta aviseringar under en viss period så att du inte upprepade gånger meddelas om något du redan känner till. Du kan också tysta med rösten — ”Hey Siri, tysta GitHub i 2 timmar” — eller från Shortcuts-appen.</p>"),
        ("Vilka plattformar stöds?",
         "iPhone och iPad (med widgets och Live Activities), Mac (med en app i menyraden plus ett fullständigt fönster), Apple Watch (med komplikationer och Smart Stack), Apple TV och Apple Vision Pro. Appen är gratis att ladda ner på varje plattform.",
         "<p>iPhone och iPad (med widgets och Live Activities), Mac (med en app i menyraden plus ett fullständigt fönster), Apple Watch (med komplikationer och Smart Stack), Apple TV och Apple Vision Pro. Appen är gratis att ladda ner på varje plattform.</p>"),
        ("Kan jag begära en ny tjänst?",
         "Ja! Mejla support@vultyr.app med tjänstens namn och URL till dess statussida.",
         "<p>Ja! Mejla <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a> med tjänstens namn och URL till dess statussida.</p>"),
    ],
},
    "tr": {
    "html_lang": "tr",
    "og_locale": "tr_TR",
    "og_image_alt": "Vultyr uygulama simgesi \u2014 Servis Durumu İzleyicisi",
    "devices": "iPhone, iPad, Mac, Apple Watch, Apple TV ve Vision Pro",
    "skip_to_main": "Ana içeriğe geç",
    "topbar_brand_aria": "Vultyr ana sayfa",
    "nav_primary_aria": "Birincil",
    "nav_services": "servisler",
    "nav_support": "destek",
    "nav_download": "İndir",
    "footer_nav_aria": "Alt bilgi gezintisi",
    "footer_home": "Ana sayfa",
    "footer_services": "Servisler",
    "footer_privacy": "Gizlilik",
    "footer_support": "Destek",
    "footer_contact": "İletişim",
    "copyright": "\u00a9 2026 Vultyr. Tüm hakları saklıdır.",
    "breadcrumb_aria": "İçerik haritası",
    "breadcrumb_vultyr": "Vultyr",
    "breadcrumb_services": "Servisler",
    # services page
    "svcs_title": "Vultyr \u2014 200+ durum kontrolü",
    "svcs_description": "Bulut servisleri, geliştirici araçları, iletişim, yapay zekâ ve daha fazlası için 200+ durum kontrolü \u2014 hepsi Vultyr tarafından izleniyor.",
    "svcs_h1_lead": "Durum",
    "svcs_h1_highlight": "Kontrolleri",
    "svcs_subtitle": "Vultyr'ın bulut servisleri, geliştirici araçları ve platformlar için çalıştırdığı 200+ durum kontrolü.",
    "svcs_categories_aria": "Kategoriye göre gözat",
    "svc_row_status": "Durum sayfası",
    "svc_row_homepage": "Ana sayfa",
    "svcs_item_list_name": "Vultyr tarafından izlenen servisler",
    # service page
    "svcp_title_fmt": "{name} çalışmıyor mu? {name} durum izleyicisi | Vultyr",
    "svcp_description_fmt": "{name} şu anda çalışıyor mu kontrol edin. Canlı {name} durum güncellemeleri ve kesinti izleme, Vultyr ile. {devices} cihazlarında ücretsiz.",
    "svcp_live_check": "Canlı kontrol",
    "svcp_view_current_status": "Mevcut durumu görüntüle \u2192",
    "svcp_alert_hint_prefix": "Anında uyarılar için ",
    "svcp_alert_hint_link": "Vultyr'ı indirin",
    "svcp_categories_label": "Kategoriler:",
    "svcp_official_status": "Resmi durum sayfası",
    "svcp_homepage_fmt": "{name} ana sayfa",
    "svcp_faq_heading": "SSS",
    "svcp_faq_q1_fmt": "{name} şu anda çalışmıyor mu?",
    "svcp_faq_a1_fmt": "Mevcut durumu görmek için yukarıda bağlantısı verilen resmi {name} durum sayfasını kontrol edin. Tüm Apple cihazlarınızda anında kesinti uyarılarıyla sürekli izleme için ücretsiz Vultyr uygulamasını indirin.",
    "svcp_faq_a1_ld_fmt": "Mevcut durum için {url} adresindeki resmi {name} durum sayfasını kontrol edin. Tüm Apple cihazlarınızda anında kesinti uyarıları almak için ücretsiz Vultyr uygulamasını indirin.",
    "svcp_faq_q2_fmt": "{name} durumunu nasıl izleyebilirim?",
    "svcp_faq_a2_fmt": "Vultyr, bulut servisleri, geliştirici araçları ve platformlar için 200+ durum kontrolünün bir parçası olarak {name} servisini izler. {devices} cihazlarında anında kesinti uyarıları alın \u2014 tamamen ücretsiz.",
    "svcp_faq_a2_ld_fmt": "{name} dahil 200+ durum kontrolünü {devices} cihazlarında gerçek zamanlı uyarılarla izlemek için Vultyr'ı (ücretsiz) indirin. Vultyr her kontrolü otomatik olarak çalıştırır ve kesinti algılandığı anda size haber verir.",
    "svcp_related_heading": "İlgili servisler",
    "svcp_related_aria": "İlgili servisler",
    "svcp_cta_heading_fmt": "{name} servisini tüm cihazlarınızda izleyin",
    "svcp_cta_body_fmt": "{name} çöktüğünde anında uyarılar alın. Tüm Apple platformlarında ücretsiz.",
    "cta_download_vultyr": "Vultyr'ı indir",
    "cta_download_vultyr_aria": "Vultyr'ı App Store'dan indir",
    # category page
    "catp_title_fmt": "{name} durum izleyicisi \u2014 {count_services} | Vultyr",
    "catp_description_fmt": "{name_lower} kategorisindeki {count_services} servisinin durumunu izleyin. {sample} ve daha fazlası için gerçek zamanlı kesinti uyarıları.",
    "catp_item_list_name_fmt": "{name} durum izleyicileri",
    "catp_subtitle_fmt": "Vultyr tarafından izlenen {count_services}",
    "catp_services_aria_fmt": "{name} servisleri",
    "catp_other_heading": "Diğer kategoriler",
    "catp_cta_heading_fmt": "Tüm {count_services} servisini anında izleyin",
    "catp_cta_body": "Tüm Apple cihazlarınızda gerçek zamanlı kesinti uyarıları alın. Ücretsiz.",
    # home page
    "home_title": "Vultyr \u2014 AWS, Slack, GitHub ve daha fazlası için servis durumu izleyicisi",
    "home_description": "Çalışmıyor mu? Bulut servisleri, geliştirici araçları ve platformlar için 200+ durum kontrolü, anında kesinti uyarılarıyla birlikte. iPhone, iPad, Mac, Apple Watch, Apple TV ve Apple Vision Pro'da ücretsiz.",
    "home_og_title": "Vultyr \u2014 Servis Durumu İzleyicisi",
    "home_app_ld_description": "Bulut servisleri, geliştirici araçları ve platformlar için 200+ durum kontrolünü anında kesinti uyarılarıyla izleyin.",
    "home_hero_tag": "200+ kontrol",
    "home_hero_question": "Çalışmıyor mu?",
    "home_hero_answer": "Kullanıcılarınızdan önce öğrenin.",
    "home_hero_services": "200+ durum kontrolü \u2014 AWS, GitHub, Slack, Stripe &amp; daha fazlası \u2014 her Apple cihazında anında kesinti uyarılarıyla.",
    "home_appstore_alt": "App Store'dan indir",
    "home_appstore_aria": "Vultyr'ı App Store'dan indir",
    "home_free_on_prefix": "Ücretsiz",
    "home_screenshots_aria": "Uygulama ekran görüntüleri",
    "home_screenshot_dash_alt": "AWS, GitHub ve Slack gibi servislerin izlendiği ve \u201cHer şey yolunda\u201d durumunu gösteren Vultyr kontrol paneli",
    "home_screenshot_settings_alt_fmt": "Terminal, Amber, Dracula ve Nord dahil {themes} temayla Vultyr görünüm ayarları",
    "home_screenshot_services_alt_fmt": "Cloud, Dev Tools ve AI dahil {categories} kategoriyle Vultyr servis tarayıcısı",
    "home_stats_aria": "Temel rakamlar",
    "home_stats_checks": "Kontrol",
    "home_stats_categories": "Kategori",
    "home_stats_platforms": "Platform",
    "home_stats_languages": "Dil",
    "home_features_heading": "Kesintilerin önüne geçmek için ihtiyacınız olan her şey",
    "home_features_sub": "Uygulama hesabı yok, uygulama içi takip yok. Yalnızca durum.",
    "home_bottom_heading": "Yığınınızı izlemeye hazır mısınız?",
    "home_bottom_sub": "Ücretsiz. Uygulama hesabı gerekmez. Her yerde kullanılabilir.",
    "home_bottom_button": "Ücretsiz indir",
    "home_bottom_aria": "Vultyr'ı App Store'dan ücretsiz indir",
    "home_languages_heading": "17 dilde kullanılabilir",
    "home_features": [
        ("chart-bar-regular.svg", "Canlı durum kontrol paneli",
         "AWS, GitHub, Cloudflare, Slack, Stripe, Discord, OpenAI, Anthropic ve 200+ daha fazlası — hepsi tek yerde. Durum göstergeleri iPhone Pro ve iPad Pro'daki 120Hz ProMotion ile senkronize olur."),
        ("bell-ringing-regular.svg", "Akıllı uyarılar",
         "iOS'ta her servisin favicon'u ile kesinti ve kurtarma bildirimleri. Büyük kesintiler küçük olaylardan belirgin şekilde daha büyük nabız atar, böylece şiddeti tek bakışta anlarsınız. Bilinen olayları sessize alın, kritik servislere yıldız koyun."),
        ("microphone-regular.svg", "Siri ve Shortcuts",
         "Siri'ye \u201cGitHub'ı 2 saatliğine sessize al\u201d veya \u201cgüncel sorunları göster\u201d deyin. Her eylem için App Intents, ayrıca kritik olmayan servisleri susturan bir Focus Filter."),
        ("squares-four-regular.svg", "Widget'lar ve Live Activities",
         "iOS'ta Ana Ekran ve Kilit Ekranı widget'ları, ayrıca bir Control Center widget'ı. Aktif kesintiler Dynamic Island'a sabitlenir."),
        ("watch-regular.svg", "Saat komplikasyonları",
         "Kritik bir servisi saat kadranına sabitleyin veya aktif sorunları Smart Stack'in otomatik olarak yüzeye çıkarmasına izin verin."),
        ("cloud-check-regular.svg", "Mac hub — iPhone yedek",
         "Mac en güvenilir hub'dır: en sık en sık 60 saniyede bir sorgular (15 dakikaya kadar yapılandırılabilir) (15 dakikaya kadar yapılandırılabilir) ve durum değişikliklerini iCloud üzerinden iPhone, iPad, Watch ve Vision Pro'ya yayınlar. Çevrimiçi Mac yoksa iPhone'unuz yedek yayıncı olarak devreye girer, böylece diğer cihazlar yine de uyarı alır."),
        ("monitor-regular.svg", "Uyarı Güvenilirliği Görünümü",
         "Uyarıların size gerçekten ulaşıp ulaşmayacağını bir bakışta görün — Mac kalp atışı, arka plan yenileme durumu, CloudKit push ve her cihazın son kontrol zamanı."),
        ("devices-regular.svg", "Her Apple platformu",
         "iPhone, iPad, Mac menü çubuğu, Apple TV, Apple Watch ve Vision Pro. Servisler tüm cihazlar arasında senkronize olur."),
        ("lightning-regular.svg", "Olay ayrıntıları",
         "Etkilenen bileşenler, aktif olaylar, planlı bakımlar ve zaman çizelgesi güncellemeleri \u2014 kendi dilinizde."),
        ("battery-charging-regular.svg", "Pile duyarlı yoklama",
         "Akıllı otomatik yenileme batarya, güç durumu ve ısıya uyum sağlar. Mac'te dakika başı, iPhone'da 5–15 dakika, iPad, Apple Watch, Vision Pro ve Apple TV'de arka plan yenilemesi ile."),
        ("palette-regular.svg", f"{THEMES_COUNT} tema",
         "Standard ve üç retro tema dahildir. Fossil, Monolith, HAL ve diğerleri isteğe bağlı bahşiş IAP'larıyla açılır."),
        ("shield-check-regular.svg", "Uygulama verisi cihazınızda kalır",
         "Uygulamada kayıt yok ve uygulama içi analitik yok. İzlediğiniz servisler cihazınızda kalır."),
        ("translate-regular.svg", f"{APP_LANGUAGE_COUNT} uygulama dili",
         "İngilizce, Almanca, Fransızca, İspanyolca, Japonca, Korece, Çince, Portekizce, Rusça ve daha fazlası."),
    ],
    # 404
    "err_title": "Sayfa bulunamadı \u2014 Vultyr",
    "err_description": "Aradığınız sayfa mevcut değil.",
    "err_heading": "Sayfa bulunamadı",
    "err_message": "Aradığınız sayfa mevcut değil veya taşınmış.",
    "redirect_moved_fmt": "Bu sayfa taşındı. {name} sayfasına yönlendiriliyor…",
    "err_popular_heading": "Popüler servisler",
    "err_browse_heading": "Kategorilere göz at",
    # privacy
    "privacy_title": "Gizlilik politikası",
    "privacy_description": "Vultyr gizlilik politikası. Uygulama hiçbir kişisel veri toplamaz. Bu web sitesi, toplu ziyaretçi trafiği için çerezsiz Google Analytics kullanır.",
    "privacy_last_updated": "Son güncelleme: 11 Nisan 2026",
    "privacy_sections": [
        ("Özet",
         "<p>Vultyr <strong>uygulaması</strong> hiçbir kişisel veri toplamaz, saklamaz veya iletmez. Vultyr <strong>web sitesi</strong> (vultyr.app) toplu ziyaretçi trafiğini anlamak için çerezsiz Google Analytics kullanır. Bu sayfa her ikisini de ayrıntılı olarak açıklar.</p>"),
        ("Uygulama \u2014 Veri toplama",
         "<p>Vultyr uygulaması hiçbir kişisel bilgi toplamaz. Hesap gerektirmez, herhangi bir üçüncü taraf analitik veya takip SDK'sı içermez ve tarafımızca işletilen hiçbir sunucuya bilgi göndermez.</p>"),
        ("Uygulama \u2014 Ağ istekleri",
         "<p>Uygulama, servis durumunu kontrol etmek için kamuya açık durum sayfası API'lerine (Statuspage.io, Apple, Google Cloud ve diğerleri gibi) doğrudan HTTPS istekleri yapar. Bu istekler cihazınızdan doğrudan servisin kamuya açık API'sine gider \u2014 tarafımızca işletilen hiçbir sunucudan geçmez.</p>"),
        ("Uygulama \u2014 Veri depolama",
         "<p>Tüm veriler Apple'ın SwiftData çerçevesi kullanılarak cihazınızda yerel olarak saklanır. iCloud Senkronizasyonunu etkinleştirirseniz, izlenen servis listeniz Apple'ın iCloud Anahtar-Değer Deposu aracılığıyla senkronize edilir; bu da Apple'ın gizlilik politikasına tabidir. Bu verileri asla görmeyiz.</p>"),
        ("Uygulama \u2014 Cihazlar arası uyarılar",
         "<p>Cihazlar Arası Uyarıları etkinleştirirseniz, durum değişiklikleri Apple'ın iCloud Anahtar-Değer Deposu aracılığıyla cihazlarınız arasında paylaşılır. Mac'iniz bir durum değişikliği algıladığında, iCloud hesabınıza hafif bir sinyal yazar. Diğer cihazlarınız bu değişikliği gözlemler ve kendi yerel kontrolünü çalıştırır. Üçüncü taraf bir sunucu söz konusu değildir \u2014 tüm iletişim Apple'ın iCloud altyapısı üzerinden geçer. Bu özelliği herhangi bir cihazdan açıp kapatabilirsiniz.</p>"),
        ("Uygulama \u2014 Favicon'lar",
         "<p>Servis favicon'ları, Google'ın herkese açık favicon servisinden alınır ve cihazınızda yerel olarak önbelleğe alınır.</p>"),
        ("Web sitesi \u2014 Analitik",
         "<p>Bu web sitesi (vultyr.app), toplu sayfa görüntülemelerini saymak için çerezsiz ve IP anonimleştirilmiş modda Google Analytics 4 kullanır. Özellikle gtag.js'yi <code>anonymize_ip: true</code>, <code>client_storage: 'none'</code>, <code>allow_google_signals: false</code> ve <code>allow_ad_personalization_signals: false</code> ile yapılandırırız. Bu, hiçbir <code>_ga</code> çerezinin ayarlanmadığı, IP'nizin saklanmadan önce kısaltıldığı ve hiçbir reklam kimliğinin toplanmadığı anlamına gelir. Vultyr uygulamasının kendisi herhangi bir analitik içermez.</p>"),
        ("Web sitesi \u2014 Üçüncü taraf alanlar",
         "<p>vultyr.app'i yüklemek aşağıdaki üçüncü taraf alanlarla iletişim kurar:</p>\n    <ul>\n        <li><strong>www.googletagmanager.com</strong> \u2014 gtag.js betiğini yükler</li>\n        <li><strong>www.google-analytics.com</strong> / <strong>*.analytics.google.com</strong> \u2014 anonimleştirilmiş sayfa görüntüleme sinyallerini alır</li>\n        <li><strong>www.google.com/g/collect</strong> \u2014 aynı anonimleştirilmiş sayfa görüntüleme sinyallerini alır (Google Analytics 4 yedek toplama uç noktası)</li>\n    </ul>\n    <p>Google Fonts yüklemeyiz (Audiowide yazı tipi vultyr.app'te kendi sunucumuzda barındırılır) ve web sitesinin kendi görselleri için üçüncü taraf bir favicon servisi kullanmayız.</p>"),
        ("Uygulama \u2014 Üçüncü taraf servisler",
         "<p>Vultyr uygulaması hiçbir üçüncü taraf analitik, reklam veya takip servisiyle entegre olmaz. Tek dış istekler, kamuya açık durum API'lerine ve Google'ın favicon servisinedir.</p>"),
        ("Çocukların gizliliği",
         "<p>Vultyr uygulaması 13 yaşın altındakiler de dahil olmak üzere hiç kimseden veri toplamaz. Web sitesi yalnızca anonimleştirilmiş, toplu ziyaretçi sayılarını kaydeder.</p>"),
        ("Değişiklikler",
         "<p>Bu politika değişirse, yukarıdaki tarihi güncelleriz.</p>"),
        ("İletişim",
         "<p>Sorularınız mı var? <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a> adresine e-posta gönderin</p>"),
    ],
    # support
    "support_title": "Destek",
    "support_description": "iPhone, iPad, Mac, Apple Watch, Apple TV ve Apple Vision Pro için servis durumu izleyicisi Vultyr hakkında yardım alın. SSS, iletişim ve sorun giderme.",
    "support_contact_heading": "İletişim",
    "support_contact_html": "<p>Hata raporları, özellik istekleri veya sorular için:<br>\n    <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a></p>",
    "support_faq_heading": "SSS",
    "support_faqs": [
        ("Vultyr servis durumunu ne sıklıkta kontrol eder?",
         "Mac'te: şarja bağlıyken en sık 60 saniyede bir (15 dakikaya kadar yapılandırılabilir). iPhone'da: her 5, 10 veya 15 dakikada bir (yapılandırılabilir), koşullar izin verdiğinde periyodik arka plan kontrolleriyle birlikte. Apple Watch'ta: 15 dakikada bir. Apple TV'de: 5 dakikada bir. Yoklama; pil seviyesi, güç durumu ve termal koşullara otomatik olarak uyum sağlar.",
         "<p>Mac'te: şarja bağlıyken en sık 60 saniyede bir (15 dakikaya kadar yapılandırılabilir). iPhone'da: her 5, 10 veya 15 dakikada bir (yapılandırılabilir), koşullar izin verdiğinde periyodik arka plan kontrolleriyle birlikte. Apple Watch'ta: 15 dakikada bir. Apple TV'de: 5 dakikada bir. Yoklama; pil seviyesi, güç durumu ve termal koşullara otomatik olarak uyum sağlar.</p>"),
        ("Cihazlar Arası Uyarılar nasıl çalışır?",
         "Merkez Mac uygulamasıdır. Çalışır durumda tutun (menü çubuğunda veya tam pencerede) ve en sık 60 saniyede bir yoklama yapar (15 dakikaya kadar yapılandırılabilir). Bir durum değişikliği algılandığında, iCloud Anahtar-Değer Deposu'na hafif bir sinyal yazar; iPhone'unuz, iPad'iniz, Watch'ınız, Apple TV'niz ve Vision Pro'nuz değişikliği alır ve kendi yerel kontrolünü çalıştırır. Anahtar yok, jeton yok, kurulum yok \u2014 herhangi bir cihazdaki ayarlardan \u201cCihazlar Arası Uyarılar\u201d seçeneğini etkinleştirmeniz yeter. Merkez görevi gören bir Mac olmadan, uyarılar iOS arka plan çalışmasına bağlı kalır ve gecikir ya da kaçırılır.",
         "<p>Merkez Mac uygulamasıdır. Çalışır durumda tutun (menü çubuğunda veya tam pencerede) ve en sık 60 saniyede bir yoklama yapar (15 dakikaya kadar yapılandırılabilir). Bir durum değişikliği algılandığında, iCloud Anahtar-Değer Deposu'na hafif bir sinyal yazar; iPhone'unuz, iPad'iniz, Watch'ınız, Apple TV'niz ve Vision Pro'nuz değişikliği alır ve kendi yerel kontrolünü çalıştırır. Anahtar yok, jeton yok, kurulum yok \u2014 herhangi bir cihazdaki ayarlardan \u201cCihazlar Arası Uyarılar\u201d seçeneğini etkinleştirmeniz yeter. Merkez görevi gören bir Mac olmadan, uyarılar iOS arka plan çalışmasına bağlı kalır ve gecikir ya da kaçırılır.</p>"),
        ("Güvenilir uyarılar için Mac uygulamasına ihtiyacım var mı?",
         "Evet \u2014 kesinlikle öneriyoruz. iOS arka plan çalışmasını kısıtlar, bu nedenle iPhone ve iPad yalnızca 5\u201315 dakikada bir kontrol edebilir (yapılandırılabilir) ve düşük pil, Düşük Güç Modu veya zayıf bağlantıda daha fazla geciktirebilir. Mac uygulaması en sık 60 saniyede bir yoklama yapar (15 dakikaya kadar yapılandırılabilir, şarja bağlıyken) ve durum değişikliklerini iCloud üzerinden diğer cihazlarınıza yayınlar. Vultyr çalıştıran bir Mac olmadan iOS, watchOS ve tvOS uyarıları çalışmaya devam eder ama önemli ölçüde gecikebilir veya kaçırılabilir. Gerçek zamanlı izleme için Mac uygulamasını çalışır durumda tutun \u2014 menü çubuğunda çok az yer kaplar ve Vultyr'ın bu şekilde kullanılması amaçlanmıştır.",
         "<p>Evet \u2014 kesinlikle öneriyoruz. iOS arka plan çalışmasını kısıtlar, bu nedenle iPhone ve iPad yalnızca 5\u201315 dakikada bir kontrol edebilir (yapılandırılabilir) ve düşük pil, Düşük Güç Modu veya zayıf bağlantıda daha fazla geciktirebilir. Mac uygulaması en sık 60 saniyede bir yoklama yapar (15 dakikaya kadar yapılandırılabilir, şarja bağlıyken) ve durum değişikliklerini iCloud üzerinden diğer cihazlarınıza yayınlar. Vultyr çalıştıran bir Mac olmadan iOS, watchOS ve tvOS uyarıları çalışmaya devam eder ama önemli ölçüde gecikebilir veya kaçırılabilir. Gerçek zamanlı izleme için Mac uygulamasını çalışır durumda tutun \u2014 menü çubuğunda çok az yer kaplar ve Vultyr'ın bu şekilde kullanılması amaçlanmıştır.</p>"),
        ("Vultyr, Siri ve Shortcuts ile çalışır mı?",
         "Evet. Yerleşik App Intents sayesinde \u201cHey Siri, GitHub'ı 2 saatliğine sessize al\u201d, \u201cStripe durumunu kontrol et\u201d veya \u201cgüncel sorunları göster\u201d diyebilir ve aynı eylemleri Shortcuts uygulamasına bağlayabilirsiniz. Ayrıca bir Focus Filter vardır; \u201cVultyr Focus\u201d modu kritik olmayan servisleri otomatik olarak susturur.",
         "<p>Evet. Yerleşik App Intents sayesinde \u201cHey Siri, GitHub'ı 2 saatliğine sessize al\u201d, \u201cStripe durumunu kontrol et\u201d veya \u201cgüncel sorunları göster\u201d diyebilir ve aynı eylemleri Shortcuts uygulamasına bağlayabilirsiniz. Ayrıca bir Focus Filter vardır; \u201cVultyr Focus\u201d modu kritik olmayan servisleri otomatik olarak susturur.</p>"),
        ("Widget'lar ve Live Activities var mı?",
         "iOS'ta Ana Ekran ve Kilit Ekranı widget'ları (tek servis ve durum özeti) ile bir Control Center widget'ı vardır. Aktif kesintiler Dynamic Island'a Live Activities olarak sabitlenir. watchOS'ta, tüm saat kadranları için komplikasyonlar mevcuttur; Smart Stack uyumluluğu sayesinde bir şeyler çöktüğünde ilgili servis öne çıkar.",
         "<p>iOS'ta Ana Ekran ve Kilit Ekranı widget'ları (tek servis ve durum özeti) ile bir Control Center widget'ı vardır. Aktif kesintiler Dynamic Island'a Live Activities olarak sabitlenir. watchOS'ta, tüm saat kadranları için komplikasyonlar mevcuttur; Smart Stack uyumluluğu sayesinde bir şeyler çöktüğünde ilgili servis öne çıkar.</p>"),
        ("Vultyr uygulaması verilerimi topluyor mu?",
         "Hayır. Uygulamanın hesabı, uygulama içi takibi veya uygulama içi analitiği yoktur. İzlediğiniz tüm servisler cihazınızda kalır. Not: Bu web sitesi (vultyr.app) toplu ziyaretçi sayıları için çerezsiz Google Analytics kullanır \u2014 ayrıntılar için Gizlilik Politikası'na bakın.",
         "<p>Hayır. Uygulamanın hesabı, uygulama içi takibi veya uygulama içi analitiği yoktur. İzlediğiniz tüm servisler cihazınızda kalır. Not: Bu web sitesi (vultyr.app) toplu ziyaretçi sayıları için çerezsiz Google Analytics kullanır \u2014 ayrıntılar için <a href=\"/privacy.html\">Gizlilik Politikası</a>'na bakın.</p>"),
        ("Servislerimi cihazlarım arasında nasıl senkronize ederim?",
         "İzlediğiniz servisler iCloud üzerinden otomatik olarak senkronize olur. Temalar ve ayarlar da iCloud Anahtar-Değer Deposu aracılığıyla tüm Apple cihazlarınızda senkronize olur.",
         "<p>İzlediğiniz servisler iCloud üzerinden otomatik olarak senkronize olur. Temalar ve ayarlar da iCloud Anahtar-Değer Deposu aracılığıyla tüm Apple cihazlarınızda senkronize olur.</p>"),
        ("Tema seçenekleri nelerdir?",
         "12 tema: Standard, Terminal, Amber, Blue, Neon, Dracula, Nord, Solarized, Catppuccin, Fossil, Monolith ve HAL. Standard ile üç retro tema (Terminal, Amber, Blue) dahildir. Fossil, Monolith, HAL ve diğerleri isteğe bağlı bahşiş IAP'larıyla açılır (0,99 $ / 4,99 $ / 9,99 $); bu ayrıca geliştirmeye destek olur. Temalar tüm cihazlarınızda otomatik olarak senkronize olur.",
         "<p>12 tema: Standard, Terminal, Amber, Blue, Neon, Dracula, Nord, Solarized, Catppuccin, Fossil, Monolith ve HAL. Standard ile üç retro tema (Terminal, Amber, Blue) dahildir. Fossil, Monolith, HAL ve diğerleri isteğe bağlı bahşiş IAP'larıyla açılır (0,99 $ / 4,99 $ / 9,99 $); bu ayrıca geliştirmeye destek olur. Temalar tüm cihazlarınızda otomatik olarak senkronize olur.</p>"),
        ("Bilinen bir olay için bildirimleri sessize alabilir miyim?",
         "Evet. Aktif olayı olan bir servisi görüntülerken, zaten bildiğiniz bir konuda tekrar tekrar uyarı almamak için bildirimleri belirli bir süre sessize alabilirsiniz. Ayrıca sesle de sessize alabilirsiniz \u2014 \u201cHey Siri, GitHub'ı 2 saatliğine sessize al\u201d \u2014 ya da Shortcuts uygulamasından.",
         "<p>Evet. Aktif olayı olan bir servisi görüntülerken, zaten bildiğiniz bir konuda tekrar tekrar uyarı almamak için bildirimleri belirli bir süre sessize alabilirsiniz. Ayrıca sesle de sessize alabilirsiniz \u2014 \u201cHey Siri, GitHub'ı 2 saatliğine sessize al\u201d \u2014 ya da Shortcuts uygulamasından.</p>"),
        ("Hangi platformlar destekleniyor?",
         "iPhone ve iPad (widget'lar ve Live Activities ile), Mac (menü çubuğu uygulaması ile birlikte tam pencere), Apple Watch (komplikasyonlar ve Smart Stack ile), Apple TV ve Apple Vision Pro. Uygulama her platformda ücretsiz indirilebilir.",
         "<p>iPhone ve iPad (widget'lar ve Live Activities ile), Mac (menü çubuğu uygulaması ile birlikte tam pencere), Apple Watch (komplikasyonlar ve Smart Stack ile), Apple TV ve Apple Vision Pro. Uygulama her platformda ücretsiz indirilebilir.</p>"),
        ("Yeni bir servis talebinde bulunabilir miyim?",
         "Evet! Servisin adını ve durum sayfası URL'sini support@vultyr.app adresine e-posta ile gönderin.",
         "<p>Evet! Servisin adını ve durum sayfası URL'sini <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a> adresine e-posta ile gönderin.</p>"),
    ],
},
    "vi": {
    "html_lang": "vi",
    "og_locale": "vi_VN",
    "og_image_alt": "Biểu tượng ứng dụng Vultyr \u2014 Trình theo dõi trạng thái dịch vụ",
    "devices": "iPhone, iPad, Mac, Apple Watch, Apple TV và Vision Pro",
    "skip_to_main": "Chuyển đến nội dung chính",
    "topbar_brand_aria": "Trang chủ Vultyr",
    "nav_primary_aria": "Chính",
    "nav_services": "dịch vụ",
    "nav_support": "hỗ trợ",
    "nav_download": "Tải xuống",
    "footer_nav_aria": "Điều hướng chân trang",
    "footer_home": "Trang chủ",
    "footer_services": "Dịch vụ",
    "footer_privacy": "Quyền riêng tư",
    "footer_support": "Hỗ trợ",
    "footer_contact": "Liên hệ",
    "copyright": "\u00a9 2026 Vultyr. Bảo lưu mọi quyền.",
    "breadcrumb_aria": "Đường dẫn",
    "breadcrumb_vultyr": "Vultyr",
    "breadcrumb_services": "Dịch vụ",
    # services page
    "svcs_title": "Vultyr \u2014 200+ kiểm tra trạng thái",
    "svcs_description": "200+ kiểm tra trạng thái cho các dịch vụ đám mây, công cụ lập trình, liên lạc, AI và nhiều hơn nữa \u2014 tất cả đều được Vultyr theo dõi.",
    "svcs_h1_lead": "Kiểm tra",
    "svcs_h1_highlight": "trạng thái",
    "svcs_subtitle": "200+ kiểm tra trạng thái mà vultyr thực hiện cho các dịch vụ đám mây, công cụ lập trình và nền tảng.",
    "svcs_categories_aria": "Duyệt theo danh mục",
    "svc_row_status": "Trang trạng thái",
    "svc_row_homepage": "Trang chủ",
    "svcs_item_list_name": "Các dịch vụ được Vultyr theo dõi",
    # service page
    "svcp_title_fmt": "{name} có gặp sự cố không? Trình theo dõi trạng thái {name} | Vultyr",
    "svcp_description_fmt": "Kiểm tra xem {name} có đang gặp sự cố hay không. Cập nhật trạng thái {name} trực tiếp và theo dõi sự cố với Vultyr. Miễn phí trên {devices}.",
    "svcp_live_check": "Kiểm tra trực tiếp",
    "svcp_view_current_status": "Xem trạng thái hiện tại \u2192",
    "svcp_alert_hint_prefix": "Để nhận cảnh báo tức thì, ",
    "svcp_alert_hint_link": "tải xuống Vultyr",
    "svcp_categories_label": "Danh mục:",
    "svcp_official_status": "Trang trạng thái chính thức",
    "svcp_homepage_fmt": "Trang chủ {name}",
    "svcp_faq_heading": "Câu hỏi thường gặp",
    "svcp_faq_q1_fmt": "{name} có đang gặp sự cố không?",
    "svcp_faq_a1_fmt": "Hãy xem trang trạng thái chính thức của {name} được liên kết ở trên để biết tình trạng hiện tại. Để theo dõi liên tục và nhận cảnh báo sự cố tức thì trên tất cả các thiết bị Apple của bạn, hãy tải ứng dụng Vultyr miễn phí.",
    "svcp_faq_a1_ld_fmt": "Hãy xem trang trạng thái chính thức của {name} tại {url} để biết tình trạng hiện tại. Tải ứng dụng Vultyr miễn phí để nhận cảnh báo sự cố tức thì trên tất cả các thiết bị Apple của bạn.",
    "svcp_faq_q2_fmt": "Làm cách nào để theo dõi trạng thái {name}?",
    "svcp_faq_a2_fmt": "Vultyr theo dõi {name} như một phần của hơn 200 kiểm tra trạng thái dành cho các dịch vụ đám mây, công cụ lập trình và nền tảng. Nhận cảnh báo sự cố tức thì trên {devices} \u2014 hoàn toàn miễn phí.",
    "svcp_faq_a2_ld_fmt": "Tải Vultyr (miễn phí) để theo dõi {name} như một phần của hơn 200 kiểm tra trạng thái với cảnh báo theo thời gian thực trên {devices}. Vultyr tự động chạy từng kiểm tra và thông báo cho bạn ngay khi phát hiện sự cố.",
    "svcp_related_heading": "Dịch vụ liên quan",
    "svcp_related_aria": "Dịch vụ liên quan",
    "svcp_cta_heading_fmt": "Theo dõi {name} trên tất cả thiết bị của bạn",
    "svcp_cta_body_fmt": "Nhận cảnh báo tức thì khi {name} gặp sự cố. Miễn phí trên tất cả nền tảng Apple.",
    "cta_download_vultyr": "Tải xuống Vultyr",
    "cta_download_vultyr_aria": "Tải Vultyr trên App Store",
    # category page
    "catp_title_fmt": "Trình theo dõi trạng thái {name} \u2014 {count_services} | Vultyr",
    "catp_description_fmt": "Theo dõi trạng thái của {count_services} trong {name_lower}. Cảnh báo sự cố theo thời gian thực cho {sample} và nhiều dịch vụ khác.",
    "catp_item_list_name_fmt": "Trình theo dõi trạng thái {name}",
    "catp_subtitle_fmt": "{count_services} được Vultyr theo dõi",
    "catp_services_aria_fmt": "Dịch vụ {name}",
    "catp_other_heading": "Danh mục khác",
    "catp_cta_heading_fmt": "Theo dõi toàn bộ {count_services} ngay lập tức",
    "catp_cta_body": "Nhận cảnh báo sự cố theo thời gian thực trên tất cả thiết bị Apple của bạn. Miễn phí.",
    # home page
    "home_title": "Vultyr \u2014 Trình theo dõi trạng thái dịch vụ cho AWS, Slack, GitHub và nhiều hơn nữa",
    "home_description": "Có gặp sự cố không? 200+ kiểm tra trạng thái cho các dịch vụ đám mây, công cụ lập trình và nền tảng cùng cảnh báo sự cố tức thì. Miễn phí trên iPhone, iPad, Mac, Apple Watch, Apple TV và Apple Vision Pro.",
    "home_og_title": "Vultyr \u2014 Trình theo dõi trạng thái dịch vụ",
    "home_app_ld_description": "Theo dõi 200+ kiểm tra trạng thái cho các dịch vụ đám mây, công cụ lập trình và nền tảng cùng cảnh báo sự cố tức thì.",
    "home_hero_tag": "200+ kiểm tra",
    "home_hero_question": "Có gặp sự cố không?",
    "home_hero_answer": "Biết trước cả người dùng của bạn.",
    "home_hero_services": "200+ kiểm tra trạng thái \u2014 AWS, GitHub, Slack, Stripe &amp; nhiều hơn nữa \u2014 với cảnh báo sự cố tức thì trên mọi thiết bị Apple.",
    "home_appstore_alt": "Tải xuống trên App Store",
    "home_appstore_aria": "Tải Vultyr trên App Store",
    "home_free_on_prefix": "Miễn phí trên",
    "home_screenshots_aria": "Ảnh chụp màn hình ứng dụng",
    "home_screenshot_dash_alt": "Bảng điều khiển Vultyr hiển thị trạng thái \u201cTất cả đều ổn\u201d với các dịch vụ như AWS, GitHub và Slack đang được theo dõi",
    "home_screenshot_settings_alt_fmt": "Cài đặt giao diện Vultyr với {themes} chủ đề bao gồm Terminal, Amber, Dracula và Nord",
    "home_screenshot_services_alt_fmt": "Trình duyệt dịch vụ của Vultyr hiển thị {categories} danh mục bao gồm Cloud, Dev Tools và AI",
    "home_stats_aria": "Những con số chính",
    "home_stats_checks": "Kiểm tra",
    "home_stats_categories": "Danh mục",
    "home_stats_platforms": "Nền tảng",
    "home_stats_languages": "Ngôn ngữ",
    "home_features_heading": "Mọi thứ bạn cần để đón đầu sự cố",
    "home_features_sub": "Không tài khoản ứng dụng, không theo dõi trong ứng dụng. Chỉ có trạng thái.",
    "home_bottom_heading": "Sẵn sàng theo dõi hệ thống của bạn?",
    "home_bottom_sub": "Miễn phí. Không cần tài khoản ứng dụng. Có sẵn ở mọi nơi.",
    "home_bottom_button": "Tải miễn phí",
    "home_bottom_aria": "Tải Vultyr miễn phí trên App Store",
    "home_languages_heading": "Có sẵn bằng 17 ngôn ngữ",
    "home_features": [
        ("chart-bar-regular.svg", "Bảng điều khiển trạng thái trực tiếp",
         "AWS, GitHub, Cloudflare, Slack, Stripe, Discord, OpenAI, Anthropic và 200+ dịch vụ khác — tất cả ở một nơi. Các chỉ báo trạng thái đồng bộ với ProMotion 120Hz trên iPhone Pro và iPad Pro."),
        ("bell-ringing-regular.svg", "Cảnh báo thông minh",
         "Thông báo sự cố và khôi phục với favicon của từng dịch vụ trên iOS. Sự cố lớn đập nhịp lớn hơn rõ rệt so với sự cố nhỏ, giúp bạn nắm mức độ nghiêm trọng ngay tức thì. Tắt tiếng các sự cố đã biết, đánh dấu sao dịch vụ quan trọng."),
        ("microphone-regular.svg", "Siri và Shortcuts",
         "Nói với Siri \u201ctắt tiếng GitHub trong 2 giờ\u201d hoặc \u201chiển thị sự cố hiện tại.\u201d App Intents cho mọi thao tác, cộng với Focus Filter giúp làm im các dịch vụ không quan trọng."),
        ("squares-four-regular.svg", "Widget và Live Activities",
         "Widget trên Màn hình chính và Màn hình khóa của iOS, cộng với widget trong Control Center. Các sự cố đang diễn ra được ghim vào Dynamic Island."),
        ("watch-regular.svg", "Complication cho Apple Watch",
         "Ghim một dịch vụ quan trọng lên mặt đồng hồ, hoặc để Smart Stack tự động đưa các sự cố đang hoạt động lên trước."),
        ("cloud-check-regular.svg", "Mac làm trung tâm — iPhone dự phòng",
         "Mac là trung tâm đáng tin cậy nhất: kiểm tra thường xuyên như mỗi 60 giây (có thể cài đặt lên 15 phút) và phát thay đổi trạng thái tới iPhone, iPad, Watch và Vision Pro qua iCloud. Nếu không có Mac nào trực tuyến, iPhone của bạn sẽ thay thế làm nhà xuất bản dự phòng để các thiết bị khác vẫn nhận được cảnh báo."),
        ("monitor-regular.svg", "Xem độ tin cậy của cảnh báo",
         "Biết ngay liệu cảnh báo có thực sự tới tay bạn — nhịp tim của Mac, trạng thái làm mới nền, push CloudKit và thời điểm kiểm tra gần nhất của từng thiết bị."),
        ("devices-regular.svg", "Mọi nền tảng Apple",
         "iPhone, iPad, thanh menu Mac, Apple TV, Apple Watch và Vision Pro. Dịch vụ đồng bộ trên tất cả thiết bị."),
        ("lightning-regular.svg", "Chi tiết sự cố",
         "Thành phần bị ảnh hưởng, sự cố đang diễn ra, bảo trì theo lịch và cập nhật dòng thời gian \u2014 bản địa hóa sang ngôn ngữ của bạn."),
        ("battery-charging-regular.svg", "Truy vấn theo pin",
         "Tự động làm mới thông minh thích ứng với pin, trạng thái nguồn và nhiệt độ. Mỗi phút trên Mac, 5–15 phút trên iPhone, với làm mới nền trên iPad, Apple Watch, Vision Pro và Apple TV."),
        ("palette-regular.svg", f"{THEMES_COUNT} chủ đề",
         "Standard và ba chủ đề retro đã bao gồm sẵn. Fossil, Monolith, HAL và các chủ đề còn lại được mở khóa qua IAP ủng hộ tùy chọn."),
        ("shield-check-regular.svg", "Dữ liệu ứng dụng lưu trên máy",
         "Ứng dụng không yêu cầu đăng ký và không có phân tích tích hợp. Các dịch vụ bạn theo dõi vẫn ở trên thiết bị của bạn."),
        ("translate-regular.svg", f"{APP_LANGUAGE_COUNT} ngôn ngữ ứng dụng",
         "Tiếng Anh, tiếng Đức, tiếng Pháp, tiếng Tây Ban Nha, tiếng Nhật, tiếng Hàn, tiếng Trung, tiếng Bồ Đào Nha, tiếng Nga và nhiều ngôn ngữ khác."),
    ],
    # 404
    "err_title": "Không tìm thấy trang \u2014 Vultyr",
    "err_description": "Trang bạn đang tìm không tồn tại.",
    "err_heading": "Không tìm thấy trang",
    "err_message": "Trang bạn đang tìm không tồn tại hoặc đã bị di chuyển.",
    "redirect_moved_fmt": "Trang này đã được di chuyển. Đang chuyển hướng đến {name}…",
    "err_popular_heading": "Dịch vụ phổ biến",
    "err_browse_heading": "Duyệt danh mục",
    # privacy
    "privacy_title": "Chính sách quyền riêng tư",
    "privacy_description": "Chính sách quyền riêng tư của Vultyr. Ứng dụng không thu thập dữ liệu cá nhân. Trang web này sử dụng Google Analytics không dùng cookie để thống kê lưu lượng truy cập tổng hợp.",
    "privacy_last_updated": "Cập nhật lần cuối: 11 tháng 4 năm 2026",
    "privacy_sections": [
        ("Tóm tắt",
         "<p><strong>Ứng dụng</strong> Vultyr không thu thập, lưu trữ hay truyền đi bất kỳ dữ liệu cá nhân nào. <strong>Trang web</strong> Vultyr (vultyr.app) sử dụng Google Analytics không dùng cookie để hiểu lưu lượng khách truy cập tổng hợp. Trang này giải thích chi tiết cả hai.</p>"),
        ("Ứng dụng \u2014 Thu thập dữ liệu",
         "<p>Ứng dụng vultyr không thu thập bất kỳ thông tin cá nhân nào. Ứng dụng không yêu cầu tài khoản, không tích hợp SDK phân tích hay theo dõi của bên thứ ba nào, và không kết nối về bất kỳ máy chủ nào do chúng tôi vận hành.</p>"),
        ("Ứng dụng \u2014 Yêu cầu mạng",
         "<p>Ứng dụng gửi yêu cầu HTTPS trực tiếp đến các API trang trạng thái công khai (như Statuspage.io, Apple, Google Cloud và những dịch vụ khác) để kiểm tra trạng thái dịch vụ. Các yêu cầu này đi thẳng từ thiết bị của bạn đến API công khai của dịch vụ \u2014 chúng không đi qua bất kỳ máy chủ nào do chúng tôi vận hành.</p>"),
        ("Ứng dụng \u2014 Lưu trữ dữ liệu",
         "<p>Toàn bộ dữ liệu được lưu cục bộ trên thiết bị của bạn bằng framework SwiftData của Apple. Nếu bạn bật Đồng bộ iCloud, danh sách các dịch vụ bạn theo dõi sẽ được đồng bộ qua iCloud Key-Value Store của Apple, vốn tuân theo chính sách quyền riêng tư của Apple. Chúng tôi không bao giờ thấy dữ liệu này.</p>"),
        ("Ứng dụng \u2014 Cảnh báo giữa các thiết bị",
         "<p>Nếu bạn bật Cảnh báo giữa các thiết bị, các thay đổi trạng thái sẽ được chia sẻ giữa các thiết bị của bạn qua iCloud Key-Value Store của Apple. Khi Mac của bạn phát hiện một thay đổi trạng thái, nó ghi một tín hiệu nhẹ vào tài khoản iCloud của bạn. Các thiết bị khác quan sát thay đổi đó và tự thực hiện kiểm tra cục bộ. Không có máy chủ bên thứ ba nào tham gia \u2014 toàn bộ liên lạc đi qua hạ tầng iCloud của Apple. Bạn có thể bật/tắt tính năng này từ bất kỳ thiết bị nào.</p>"),
        ("Ứng dụng \u2014 Favicon",
         "<p>Favicon của dịch vụ được lấy từ dịch vụ favicon công khai của Google và được lưu đệm cục bộ trên thiết bị của bạn.</p>"),
        ("Trang web \u2014 Phân tích",
         "<p>Trang web này (vultyr.app) sử dụng Google Analytics 4 ở chế độ không cookie, ẩn danh IP để đếm lượt xem trang tổng hợp. Cụ thể, chúng tôi cấu hình gtag.js với <code>anonymize_ip: true</code>, <code>client_storage: 'none'</code>, <code>allow_google_signals: false</code> và <code>allow_ad_personalization_signals: false</code>. Điều này có nghĩa là không cookie <code>_ga</code> nào được đặt, IP của bạn bị cắt ngắn trước khi lưu trữ, và không có mã định danh quảng cáo nào được thu thập. Bản thân ứng dụng vultyr không chứa bất kỳ phân tích nào.</p>"),
        ("Trang web \u2014 Tên miền bên thứ ba",
         "<p>Khi tải vultyr.app, trang web sẽ liên hệ với các tên miền bên thứ ba sau:</p>\n    <ul>\n        <li><strong>www.googletagmanager.com</strong> \u2014 tải script gtag.js</li>\n        <li><strong>www.google-analytics.com</strong> / <strong>*.analytics.google.com</strong> \u2014 tiếp nhận tín hiệu lượt xem trang đã ẩn danh</li>\n        <li><strong>www.google.com/g/collect</strong> \u2014 tiếp nhận cùng tín hiệu lượt xem trang đã ẩn danh (điểm cuối thu thập dự phòng của Google Analytics 4)</li>\n    </ul>\n    <p>Chúng tôi không tải Google Fonts (phông Audiowide được tự lưu trên vultyr.app) và không sử dụng dịch vụ favicon của bên thứ ba cho hình ảnh của chính trang web.</p>"),
        ("Ứng dụng \u2014 Dịch vụ bên thứ ba",
         "<p>Ứng dụng vultyr không tích hợp với bất kỳ dịch vụ phân tích, quảng cáo hay theo dõi của bên thứ ba nào. Các yêu cầu ra ngoài duy nhất là đến API trạng thái công khai và dịch vụ favicon của Google.</p>"),
        ("Quyền riêng tư của trẻ em",
         "<p>Ứng dụng vultyr không thu thập dữ liệu từ bất kỳ ai, kể cả trẻ em dưới 13 tuổi. Trang web chỉ ghi nhận số lượt truy cập tổng hợp đã được ẩn danh.</p>"),
        ("Thay đổi",
         "<p>Nếu chính sách này thay đổi, chúng tôi sẽ cập nhật ngày ở trên.</p>"),
        ("Liên hệ",
         "<p>Có câu hỏi? Gửi email tới <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a></p>"),
    ],
    # support
    "support_title": "Hỗ trợ",
    "support_description": "Nhận trợ giúp với Vultyr, trình theo dõi trạng thái dịch vụ cho iPhone, iPad, Mac, Apple Watch, Apple TV và Apple Vision Pro. Câu hỏi thường gặp, liên hệ và khắc phục sự cố.",
    "support_contact_heading": "Liên hệ",
    "support_contact_html": "<p>Để báo lỗi, yêu cầu tính năng hoặc đặt câu hỏi:<br>\n    <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a></p>",
    "support_faq_heading": "Câu hỏi thường gặp",
    "support_faqs": [
        ("vultyr kiểm tra trạng thái dịch vụ thường xuyên đến mức nào?",
         "Trên Mac: nhanh tới mỗi 60 giây khi cắm sạc. Trên iPhone: mỗi 5, 10 hoặc 15 phút (có thể cấu hình), với các kiểm tra nền định kỳ khi điều kiện cho phép. Trên Apple Watch: mỗi 15 phút. Trên Apple TV: mỗi 5 phút. Việc truy vấn tự động thích ứng theo mức pin, trạng thái nguồn và điều kiện nhiệt.",
         "<p>Trên Mac: nhanh tới mỗi 60 giây khi cắm sạc. Trên iPhone: mỗi 5, 10 hoặc 15 phút (có thể cấu hình), với các kiểm tra nền định kỳ khi điều kiện cho phép. Trên Apple Watch: mỗi 15 phút. Trên Apple TV: mỗi 5 phút. Việc truy vấn tự động thích ứng theo mức pin, trạng thái nguồn và điều kiện nhiệt.</p>"),
        ("Cảnh báo giữa các thiết bị hoạt động như thế nào?",
         "Ứng dụng Mac là trung tâm. Hãy giữ nó chạy (trong thanh menu hoặc cửa sổ đầy đủ) và nó sẽ truy vấn thường xuyên như mỗi 60 giây (có thể cài đặt lên 15 phút). Khi phát hiện thay đổi trạng thái, nó ghi một tín hiệu nhẹ vào iCloud Key-Value Store; iPhone, iPad, Watch, Apple TV và Vision Pro của bạn sẽ nhận thay đổi và tự thực hiện kiểm tra cục bộ. Không cần khóa, không token, không phải thiết lập \u2014 chỉ cần bật \u201cCảnh báo giữa các thiết bị\u201d trong cài đặt trên bất kỳ thiết bị nào. Không có Mac đóng vai trò trung tâm, cảnh báo sẽ phụ thuộc vào thực thi nền của iOS và sẽ bị trễ hoặc bỏ lỡ.",
         "<p>Ứng dụng Mac là trung tâm. Hãy giữ nó chạy (trong thanh menu hoặc cửa sổ đầy đủ) và nó sẽ truy vấn thường xuyên như mỗi 60 giây (có thể cài đặt lên 15 phút). Khi phát hiện thay đổi trạng thái, nó ghi một tín hiệu nhẹ vào iCloud Key-Value Store; iPhone, iPad, Watch, Apple TV và Vision Pro của bạn sẽ nhận thay đổi và tự thực hiện kiểm tra cục bộ. Không cần khóa, không token, không phải thiết lập \u2014 chỉ cần bật \u201cCảnh báo giữa các thiết bị\u201d trong cài đặt trên bất kỳ thiết bị nào. Không có Mac đóng vai trò trung tâm, cảnh báo sẽ phụ thuộc vào thực thi nền của iOS và sẽ bị trễ hoặc bỏ lỡ.</p>"),
        ("Tôi có cần ứng dụng Mac để có cảnh báo đáng tin cậy không?",
         "Có \u2014 chúng tôi đặc biệt khuyến nghị. iOS giới hạn thực thi nền, nên iPhone và iPad chỉ có thể kiểm tra mỗi 5\u201315 phút (có thể cấu hình) và có thể bị trì hoãn thêm khi pin yếu, Chế độ tiết kiệm năng lượng hoặc kết nối kém. Ứng dụng Mac truy vấn liên tục (mỗi 60 giây khi cắm sạc) và phát các thay đổi trạng thái đến các thiết bị khác qua iCloud. Nếu không có Mac chạy Vultyr, cảnh báo trên iOS, watchOS và tvOS vẫn hoạt động nhưng có thể bị trễ đáng kể hoặc bỏ lỡ. Để theo dõi theo thời gian thực, hãy giữ ứng dụng Mac chạy \u2014 nó nhỏ gọn trong thanh menu và đó chính là cách Vultyr được thiết kế để sử dụng.",
         "<p>Có \u2014 chúng tôi đặc biệt khuyến nghị. iOS giới hạn thực thi nền, nên iPhone và iPad chỉ có thể kiểm tra mỗi 5\u201315 phút (có thể cấu hình) và có thể bị trì hoãn thêm khi pin yếu, Chế độ tiết kiệm năng lượng hoặc kết nối kém. Ứng dụng Mac truy vấn liên tục (mỗi 60 giây khi cắm sạc) và phát các thay đổi trạng thái đến các thiết bị khác qua iCloud. Nếu không có Mac chạy Vultyr, cảnh báo trên iOS, watchOS và tvOS vẫn hoạt động nhưng có thể bị trễ đáng kể hoặc bỏ lỡ. Để theo dõi theo thời gian thực, hãy giữ ứng dụng Mac chạy \u2014 nó nhỏ gọn trong thanh menu và đó chính là cách Vultyr được thiết kế để sử dụng.</p>"),
        ("vultyr có hoạt động với Siri và Shortcuts không?",
         "Có. App Intents tích hợp sẵn cho phép bạn nói \u201cHey Siri, tắt tiếng GitHub trong 2 giờ,\u201d \u201ckiểm tra trạng thái Stripe,\u201d hoặc \u201chiển thị sự cố hiện tại,\u201d và bạn có thể đưa những thao tác tương tự vào ứng dụng Shortcuts. Cũng có Focus Filter để chế độ \u201cvultyr Focus\u201d tự động làm im các dịch vụ không quan trọng.",
         "<p>Có. App Intents tích hợp sẵn cho phép bạn nói \u201cHey Siri, tắt tiếng GitHub trong 2 giờ,\u201d \u201ckiểm tra trạng thái Stripe,\u201d hoặc \u201chiển thị sự cố hiện tại,\u201d và bạn có thể đưa những thao tác tương tự vào ứng dụng Shortcuts. Cũng có Focus Filter để chế độ \u201cvultyr Focus\u201d tự động làm im các dịch vụ không quan trọng.</p>"),
        ("Có widget và Live Activities không?",
         "Trên iOS có widget cho Màn hình chính và Màn hình khóa (một dịch vụ và bản tóm tắt trạng thái) cộng với widget trong Control Center. Các sự cố đang diễn ra được ghim vào Dynamic Island dưới dạng Live Activities. Trên watchOS có complication cho tất cả các mặt đồng hồ, với độ phù hợp Smart Stack để dịch vụ đúng lúc xuất hiện khi có vấn đề.",
         "<p>Trên iOS có widget cho Màn hình chính và Màn hình khóa (một dịch vụ và bản tóm tắt trạng thái) cộng với widget trong Control Center. Các sự cố đang diễn ra được ghim vào Dynamic Island dưới dạng Live Activities. Trên watchOS có complication cho tất cả các mặt đồng hồ, với độ phù hợp Smart Stack để dịch vụ đúng lúc xuất hiện khi có vấn đề.</p>"),
        ("Ứng dụng vultyr có thu thập dữ liệu của tôi không?",
         "Không. Ứng dụng không có tài khoản, không theo dõi trong ứng dụng, không phân tích trong ứng dụng. Tất cả các dịch vụ bạn theo dõi vẫn ở trên thiết bị của bạn. Lưu ý: trang web này (vultyr.app) sử dụng Google Analytics không dùng cookie để đếm lượt khách truy cập tổng hợp \u2014 xem Chính sách quyền riêng tư để biết chi tiết.",
         "<p>Không. Ứng dụng không có tài khoản, không theo dõi trong ứng dụng, không phân tích trong ứng dụng. Tất cả các dịch vụ bạn theo dõi vẫn ở trên thiết bị của bạn. Lưu ý: trang web này (vultyr.app) sử dụng Google Analytics không dùng cookie để đếm lượt khách truy cập tổng hợp \u2014 xem <a href=\"/privacy.html\">Chính sách quyền riêng tư</a> để biết chi tiết.</p>"),
        ("Làm cách nào để đồng bộ dịch vụ giữa các thiết bị?",
         "Các dịch vụ bạn theo dõi tự động đồng bộ qua iCloud. Chủ đề và cài đặt cũng đồng bộ trên tất cả thiết bị Apple của bạn qua iCloud Key-Value Store.",
         "<p>Các dịch vụ bạn theo dõi tự động đồng bộ qua iCloud. Chủ đề và cài đặt cũng đồng bộ trên tất cả thiết bị Apple của bạn qua iCloud Key-Value Store.</p>"),
        ("Có những tùy chọn chủ đề nào?",
         "12 chủ đề: Standard, Terminal, Amber, Blue, Neon, Dracula, Nord, Solarized, Catppuccin, Fossil, Monolith và HAL. Standard và ba chủ đề retro (Terminal, Amber, Blue) được bao gồm sẵn. Fossil, Monolith, HAL và các chủ đề còn lại được mở khóa qua IAP ủng hộ tùy chọn ($0.99 / $4.99 / $9.99), đồng thời giúp tài trợ cho việc phát triển. Chủ đề tự động đồng bộ trên tất cả thiết bị của bạn.",
         "<p>12 chủ đề: Standard, Terminal, Amber, Blue, Neon, Dracula, Nord, Solarized, Catppuccin, Fossil, Monolith và HAL. Standard và ba chủ đề retro (Terminal, Amber, Blue) được bao gồm sẵn. Fossil, Monolith, HAL và các chủ đề còn lại được mở khóa qua IAP ủng hộ tùy chọn ($0.99 / $4.99 / $9.99), đồng thời giúp tài trợ cho việc phát triển. Chủ đề tự động đồng bộ trên tất cả thiết bị của bạn.</p>"),
        ("Tôi có thể tắt tiếng thông báo cho một sự cố đã biết không?",
         "Có. Khi xem một dịch vụ có sự cố đang diễn ra, bạn có thể tắt tiếng thông báo trong một khoảng thời gian nhất định để không bị cảnh báo lặp lại về điều đã biết. Bạn cũng có thể tắt tiếng bằng giọng nói \u2014 \u201cHey Siri, tắt tiếng GitHub trong 2 giờ\u201d \u2014 hoặc từ ứng dụng Shortcuts.",
         "<p>Có. Khi xem một dịch vụ có sự cố đang diễn ra, bạn có thể tắt tiếng thông báo trong một khoảng thời gian nhất định để không bị cảnh báo lặp lại về điều đã biết. Bạn cũng có thể tắt tiếng bằng giọng nói \u2014 \u201cHey Siri, tắt tiếng GitHub trong 2 giờ\u201d \u2014 hoặc từ ứng dụng Shortcuts.</p>"),
        ("Những nền tảng nào được hỗ trợ?",
         "iPhone và iPad (với widget và Live Activities), Mac (với ứng dụng thanh menu cộng với cửa sổ đầy đủ), Apple Watch (với complication và Smart Stack), Apple TV và Apple Vision Pro. Ứng dụng được tải miễn phí trên mọi nền tảng.",
         "<p>iPhone và iPad (với widget và Live Activities), Mac (với ứng dụng thanh menu cộng với cửa sổ đầy đủ), Apple Watch (với complication và Smart Stack), Apple TV và Apple Vision Pro. Ứng dụng được tải miễn phí trên mọi nền tảng.</p>"),
        ("Tôi có thể yêu cầu thêm một dịch vụ mới không?",
         "Có! Hãy gửi email tới support@vultyr.app với tên dịch vụ và URL trang trạng thái của nó.",
         "<p>Có! Hãy gửi email tới <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a> với tên dịch vụ và URL trang trạng thái của nó.</p>"),
    ],
},
    "zh-Hans": {
    "html_lang": "zh-Hans",
    "og_locale": "zh_CN",
    "og_image_alt": "Vultyr 应用图标 —— 服务状态监测",
    "devices": "iPhone、iPad、Mac、Apple Watch、Apple TV 和 Vision Pro",
    "skip_to_main": "跳至主要内容",
    "topbar_brand_aria": "Vultyr 首页",
    "nav_primary_aria": "主导航",
    "nav_services": "服务",
    "nav_support": "支持",
    "nav_download": "下载",
    "footer_nav_aria": "页脚导航",
    "footer_home": "首页",
    "footer_services": "服务",
    "footer_privacy": "隐私",
    "footer_support": "支持",
    "footer_contact": "联系我们",
    "copyright": "\u00a9 2026 Vultyr。保留所有权利。",
    "breadcrumb_aria": "面包屑导航",
    "breadcrumb_vultyr": "Vultyr",
    "breadcrumb_services": "服务",
    # services page
    "svcs_title": "Vultyr —— 200+ 状态检查",
    "svcs_description": "200+ 状态检查,覆盖云服务、开发者工具、通讯、AI 等领域 —— 全部由 Vultyr 监测。",
    "svcs_h1_lead": "状态",
    "svcs_h1_highlight": "检查",
    "svcs_subtitle": "Vultyr 为云服务、开发者工具和平台运行的 200+ 状态检查。",
    "svcs_categories_aria": "按类别浏览",
    "svc_row_status": "状态页面",
    "svc_row_homepage": "官方网站",
    "svcs_item_list_name": "Vultyr 监测的服务",
    # service page
    "svcp_title_fmt": "{name} 宕机了吗?{name} 状态监测 | Vultyr",
    "svcp_description_fmt": "立即查看 {name} 是否宕机。通过 Vultyr 获取实时 {name} 状态更新与故障监测。在 {devices} 上免费使用。",
    "svcp_live_check": "实时检查",
    "svcp_view_current_status": "查看当前状态 \u2192",
    "svcp_alert_hint_prefix": "如需即时提醒,请",
    "svcp_alert_hint_link": "下载 Vultyr",
    "svcp_categories_label": "类别:",
    "svcp_official_status": "官方状态页面",
    "svcp_homepage_fmt": "{name} 官方网站",
    "svcp_faq_heading": "常见问题",
    "svcp_faq_q1_fmt": "{name} 现在宕机了吗?",
    "svcp_faq_a1_fmt": "请通过上方链接查看 {name} 官方状态页面以了解当前状态。若需要持续监测并在所有 Apple 设备上接收即时故障提醒,请下载免费的 Vultyr 应用。",
    "svcp_faq_a1_ld_fmt": "请访问 {url} 查看 {name} 官方状态页面以了解当前状态。下载免费的 Vultyr 应用,在所有 Apple 设备上接收即时故障提醒。",
    "svcp_faq_q2_fmt": "如何监测 {name} 的状态?",
    "svcp_faq_a2_fmt": "Vultyr 将 {name} 纳入 200+ 状态检查的一部分,覆盖云服务、开发者工具和平台。在 {devices} 上获取即时故障提醒 —— 完全免费。",
    "svcp_faq_a2_ld_fmt": "下载 Vultyr(免费)即可将 {name} 作为 200+ 状态检查的一部分,在 {devices} 上获得实时提醒。Vultyr 自动运行每项检查,一旦检测到故障立即通知您。",
    "svcp_related_heading": "相关服务",
    "svcp_related_aria": "相关服务",
    "svcp_cta_heading_fmt": "在所有设备上监测 {name}",
    "svcp_cta_body_fmt": "{name} 宕机时即刻收到提醒。在所有 Apple 平台上免费使用。",
    "cta_download_vultyr": "下载 Vultyr",
    "cta_download_vultyr_aria": "在 App Store 下载 Vultyr",
    # category page
    "catp_title_fmt": "{name} 状态监测 —— {count_services} | Vultyr",
    "catp_description_fmt": "监测 {name_lower} 分类下 {count_services} 的状态。为 {sample} 等提供实时故障提醒。",
    "catp_item_list_name_fmt": "{name} 状态监测",
    "catp_subtitle_fmt": "Vultyr 监测中的 {count_services}",
    "catp_services_aria_fmt": "{name} 服务",
    "catp_other_heading": "其他类别",
    "catp_cta_heading_fmt": "即刻监测全部 {count_services}",
    "catp_cta_body": "在所有 Apple 设备上获取实时故障提醒。免费。",
    # home page
    "home_title": "Vultyr —— 面向 AWS、Slack、GitHub 等服务的状态监测",
    "home_description": "宕机了吗?200+ 状态检查覆盖云服务、开发者工具和平台,提供即时故障提醒。在 iPhone、iPad、Mac、Apple Watch、Apple TV 和 Apple Vision Pro 上免费使用。",
    "home_og_title": "Vultyr —— 服务状态监测",
    "home_app_ld_description": "监测 200+ 状态检查,覆盖云服务、开发者工具和平台,提供即时故障提醒。",
    "home_hero_tag": "200+ 检查",
    "home_hero_question": "宕机了吗?",
    "home_hero_answer": "抢在用户之前知晓。",
    "home_hero_services": "200+ 状态检查 —— AWS、GitHub、Slack、Stripe 等 —— 在每一台 Apple 设备上提供即时故障提醒。",
    "home_appstore_alt": "在 App Store 下载",
    "home_appstore_aria": "在 App Store 下载 Vultyr",
    "home_free_on_prefix": "免费,支持",
    "home_screenshots_aria": "应用截图",
    "home_screenshot_dash_alt": "Vultyr 仪表板显示「一切正常」状态,监测中的服务包括 AWS、GitHub 和 Slack",
    "home_screenshot_settings_alt_fmt": "Vultyr 外观设置,包含 {themes} 款主题,其中有 Terminal、Amber、Dracula 和 Nord",
    "home_screenshot_services_alt_fmt": "Vultyr 服务浏览器显示 {categories} 个类别,包括 Cloud、Dev Tools 和 AI",
    "home_stats_aria": "关键数据",
    "home_stats_checks": "检查项",
    "home_stats_categories": "类别",
    "home_stats_platforms": "平台",
    "home_stats_languages": "语言",
    "home_features_heading": "应对故障所需的一切",
    "home_features_sub": "无需应用账号,无内置追踪。只有状态。",
    "home_bottom_heading": "准备好监测你的技术栈了吗?",
    "home_bottom_sub": "免费。无需应用账号。全平台可用。",
    "home_bottom_button": "免费下载",
    "home_bottom_aria": "在 App Store 免费下载 Vultyr",
    "home_languages_heading": "支持 17 种语言",
    "home_features": [
        ("chart-bar-regular.svg", "实时状态仪表板",
         "AWS、GitHub、Cloudflare、Slack、Stripe、Discord、OpenAI、Anthropic 和 200+ 服务 — 一个地方尽览。状态图标与 iPhone Pro 和 iPad Pro 的 120Hz ProMotion 同步。"),
        ("bell-ringing-regular.svg", "智能提醒",
         "iOS 上带各服务图标的故障与恢复通知。重大故障的脉动明显大于轻微事件，严重程度一目了然。静音已知事件，给关键服务标星。"),
        ("microphone-regular.svg", "Siri 与 Shortcuts",
         "对 Siri 说「将 GitHub 静音 2 小时」或「显示当前问题」。每项操作都有对应的 App Intents,并提供「专注过滤器」以自动静音非关键服务。"),
        ("squares-four-regular.svg", "小组件与 Live Activities",
         "iOS 上的主屏幕和锁屏小组件,以及控制中心小组件。正在发生的故障会固定显示在 Dynamic Island 中。"),
        ("watch-regular.svg", "手表复杂功能",
         "将关键服务固定到表盘上,或让 Smart Stack 自动浮现正在发生的问题。"),
        ("cloud-check-regular.svg", "Mac 作为中心 — iPhone 作为备用",
         "Mac 是最可靠的中心：最快每 60 秒轮询一次（可配置至 15 分钟），并通过 iCloud 将状态变化广播至 iPhone、iPad、Watch 和 Vision Pro。如果没有 Mac 在线，你的 iPhone 会接替成为备用发布者，让其他设备仍然能收到告警。"),
        ("monitor-regular.svg", "告警可靠性视图",
         "一目了然地查看告警是否能真正到达你 — Mac 心跳、后台刷新状态、CloudKit 推送及每台设备的最后检查时间。"),
        ("devices-regular.svg", "覆盖每个 Apple 平台",
         "iPhone、iPad、Mac 菜单栏、Apple TV、Apple Watch 和 Vision Pro。服务在所有设备间同步。"),
        ("lightning-regular.svg", "事件详情",
         "受影响的组件、正在发生的事件、计划维护和时间线更新 —— 已本地化为您的语言。"),
        ("battery-charging-regular.svg", "感知电量的轮询",
         "智能自动刷新根据电量、电源状态和温度自适应。Mac 上每分钟一次，iPhone 上 5–15 分钟一次，iPad、Apple Watch、Vision Pro 和 Apple TV 支持后台刷新。"),
        ("palette-regular.svg", f"{THEMES_COUNT} 款主题",
         "内置 Standard 与三款复古主题。Fossil、Monolith、HAL 等其余主题可通过可选的打赏式 IAP 解锁。"),
        ("shield-check-regular.svg", "应用数据留在本地",
         "应用无需注册,也没有内置分析。您关注的服务只保存在设备上。"),
        ("translate-regular.svg", f"{APP_LANGUAGE_COUNT} 种应用语言",
         "英语、德语、法语、西班牙语、日语、韩语、中文、葡萄牙语、俄语等。"),
    ],
    # 404
    "err_title": "页面未找到 —— Vultyr",
    "err_description": "您访问的页面不存在。",
    "err_heading": "页面未找到",
    "err_message": "您访问的页面不存在或已被移动。",
    "redirect_moved_fmt": "此页面已移动。正在重定向到 {name}…",
    "err_popular_heading": "热门服务",
    "err_browse_heading": "浏览类别",
    # privacy
    "privacy_title": "隐私政策",
    "privacy_description": "Vultyr 隐私政策。应用不收集任何个人数据。本网站使用无 Cookie 的 Google Analytics 统计聚合访问量。",
    "privacy_last_updated": "最后更新:2026 年 4 月 11 日",
    "privacy_sections": [
        ("摘要",
         "<p>Vultyr <strong>应用</strong>不收集、存储或传输任何个人数据。Vultyr <strong>网站</strong>(vultyr.app)使用无 Cookie 的 Google Analytics 了解聚合访问量。本页面将对两者分别进行详细说明。</p>"),
        ("应用 —— 数据收集",
         "<p>Vultyr 应用不收集任何个人信息。它无需账号,不包含任何第三方分析或追踪 SDK,也不会向我们运营的任何服务器回传数据。</p>"),
        ("应用 —— 网络请求",
         "<p>应用会直接向公共状态页面 API(如 Statuspage.io、Apple、Google Cloud 等)发送 HTTPS 请求以检查服务状态。这些请求从您的设备直接发送至该服务的公共 API —— 不会经过我们运营的任何服务器。</p>"),
        ("应用 —— 数据存储",
         "<p>所有数据均使用 Apple 的 SwiftData 框架存储在您的设备本地。如果您启用了 iCloud 同步,您关注的服务列表会通过 Apple 的 iCloud Key-Value Store 同步,并遵循 Apple 的隐私政策。我们永远不会看到这些数据。</p>"),
        ("应用 —— 跨设备提醒",
         "<p>如果您启用跨设备提醒,状态变更会通过 Apple 的 iCloud Key-Value Store 在您的设备之间共享。当 Mac 检测到状态变化时,会向您的 iCloud 账户写入一个轻量信号。其他设备观察到该变化后会各自执行本地检查。其中不涉及任何第三方服务器 —— 全部通信均通过 Apple 的 iCloud 基础设施。您可以在任一设备上开启或关闭该功能。</p>"),
        ("应用 —— 站点图标",
         "<p>服务站点图标从 Google 的公共图标服务中获取,并在您的设备本地缓存。</p>"),
        ("网站 —— 分析",
         "<p>本网站(vultyr.app)使用 Google Analytics 4 的无 Cookie、匿名化 IP 模式来统计聚合页面浏览量。具体而言,我们将 gtag.js 配置为 <code>anonymize_ip: true</code>、<code>client_storage: 'none'</code>、<code>allow_google_signals: false</code> 和 <code>allow_ad_personalization_signals: false</code>。这意味着不会设置 <code>_ga</code> Cookie,您的 IP 在存储前会被截断,也不会收集广告标识符。Vultyr 应用本身不包含任何分析功能。</p>"),
        ("网站 —— 第三方域名",
         "<p>加载 vultyr.app 会访问以下第三方域名:</p>\n    <ul>\n        <li><strong>www.googletagmanager.com</strong> —— 加载 gtag.js 脚本</li>\n        <li><strong>www.google-analytics.com</strong> / <strong>*.analytics.google.com</strong> —— 接收匿名化的页面浏览信标</li>\n        <li><strong>www.google.com/g/collect</strong> —— 接收同样匿名化的页面浏览信标(Google Analytics 4 备用收集端点)</li>\n    </ul>\n    <p>我们不加载 Google Fonts(Audiowide 字体由 vultyr.app 自行托管),也不使用第三方站点图标服务来展示网站自身的图像。</p>"),
        ("应用 —— 第三方服务",
         "<p>Vultyr 应用不集成任何第三方分析、广告或追踪服务。唯一的外部请求指向公共状态 API 以及 Google 的站点图标服务。</p>"),
        ("儿童隐私",
         "<p>Vultyr 应用不向任何人(包括 13 岁以下儿童)收集数据。本网站仅记录匿名化的聚合访问量。</p>"),
        ("政策变更",
         "<p>如果本政策发生变更,我们将更新上方日期。</p>"),
        ("联系我们",
         "<p>有疑问?请发送邮件至 <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a></p>"),
    ],
    # support
    "support_title": "支持",
    "support_description": "获取 Vultyr 使用帮助 —— Vultyr 是面向 iPhone、iPad、Mac、Apple Watch、Apple TV 和 Apple Vision Pro 的服务状态监测应用。常见问题、联系方式与故障排查。",
    "support_contact_heading": "联系我们",
    "support_contact_html": "<p>如需提交故障反馈、功能建议或咨询问题:<br>\n    <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a></p>",
    "support_faq_heading": "常见问题",
    "support_faqs": [
        ("Vultyr 多久检查一次服务状态?",
         "在 Mac 上:连接电源时可低至每 60 秒一次。在 iPhone 上:每 5、10 或 15 分钟一次(可配置),并在条件允许时进行周期性后台检查。在 Apple Watch 上:每 15 分钟一次。在 Apple TV 上:每 5 分钟一次。轮询会根据电量、供电状态和温度条件自动调整。",
         "<p>在 Mac 上:连接电源时可低至每 60 秒一次。在 iPhone 上:每 5、10 或 15 分钟一次(可配置),并在条件允许时进行周期性后台检查。在 Apple Watch 上:每 15 分钟一次。在 Apple TV 上:每 5 分钟一次。轮询会根据电量、供电状态和温度条件自动调整。</p>"),
        ("跨设备提醒是如何工作的?",
         "Mac 应用是枢纽。让它保持运行(菜单栏或完整窗口),它会最快每 60 秒轮询一次（可配置至 15 分钟）。一旦检测到状态变化,它会向 iCloud Key-Value Store 写入一个轻量信号;您的 iPhone、iPad、Watch、Apple TV 和 Vision Pro 会接收到该变化并各自执行本地检查。无需密钥、令牌或配置 —— 只需在任一设备的设置中启用「跨设备提醒」。如果没有 Mac 作为枢纽,提醒将依赖 iOS 的后台执行,可能被延迟或遗漏。",
         "<p>Mac 应用是枢纽。让它保持运行(菜单栏或完整窗口),它会最快每 60 秒轮询一次（可配置至 15 分钟）。一旦检测到状态变化,它会向 iCloud Key-Value Store 写入一个轻量信号;您的 iPhone、iPad、Watch、Apple TV 和 Vision Pro 会接收到该变化并各自执行本地检查。无需密钥、令牌或配置 —— 只需在任一设备的设置中启用「跨设备提醒」。如果没有 Mac 作为枢纽,提醒将依赖 iOS 的后台执行,可能被延迟或遗漏。</p>"),
        ("要获得可靠的提醒,是否必须使用 Mac 应用?",
         "是的 —— 我们强烈推荐。iOS 限制后台执行,因此 iPhone 和 iPad 只能每 5–15 分钟检查一次(可配置),并且在低电量、低电量模式或网络状况不佳时,还可能进一步延迟。Mac 应用会持续轮询(接入电源时每 60 秒一次),并通过 iCloud 将状态变化广播给您的其他设备。如果没有运行 Vultyr 的 Mac,iOS、watchOS 和 tvOS 的提醒仍可工作,但可能会显著延迟或遗漏。如需实时监测,请保持 Mac 应用运行 —— 它在菜单栏里占用极小,这正是 Vultyr 的设计用法。",
         "<p>是的 —— 我们强烈推荐。iOS 限制后台执行,因此 iPhone 和 iPad 只能每 5–15 分钟检查一次(可配置),并且在低电量、低电量模式或网络状况不佳时,还可能进一步延迟。Mac 应用会持续轮询(接入电源时每 60 秒一次),并通过 iCloud 将状态变化广播给您的其他设备。如果没有运行 Vultyr 的 Mac,iOS、watchOS 和 tvOS 的提醒仍可工作,但可能会显著延迟或遗漏。如需实时监测,请保持 Mac 应用运行 —— 它在菜单栏里占用极小,这正是 Vultyr 的设计用法。</p>"),
        ("Vultyr 支持 Siri 和 Shortcuts 吗?",
         "支持。内置 App Intents 让您可以说「嘿 Siri,将 GitHub 静音 2 小时」、「查看 Stripe 状态」或「显示当前问题」,同样的操作还可以接入 Shortcuts 应用。另外提供专注过滤器,启用「Vultyr 专注」模式即可自动静音非关键服务。",
         "<p>支持。内置 App Intents 让您可以说「嘿 Siri,将 GitHub 静音 2 小时」、「查看 Stripe 状态」或「显示当前问题」,同样的操作还可以接入 Shortcuts 应用。另外提供专注过滤器,启用「Vultyr 专注」模式即可自动静音非关键服务。</p>"),
        ("是否有小组件和 Live Activities?",
         "在 iOS 上,提供主屏幕和锁屏小组件(单服务与状态汇总),以及控制中心小组件。正在发生的故障会作为 Live Activities 固定在 Dynamic Island。在 watchOS 上,所有表盘均提供复杂功能,并借助 Smart Stack 的相关性在服务出故障时自动浮现。",
         "<p>在 iOS 上,提供主屏幕和锁屏小组件(单服务与状态汇总),以及控制中心小组件。正在发生的故障会作为 Live Activities 固定在 Dynamic Island。在 watchOS 上,所有表盘均提供复杂功能,并借助 Smart Stack 的相关性在服务出故障时自动浮现。</p>"),
        ("Vultyr 应用会收集我的数据吗?",
         "不会。应用没有账号、没有内置追踪,也没有内置分析。您关注的所有服务仅保存在您的设备上。注意:本网站(vultyr.app)使用无 Cookie 的 Google Analytics 统计聚合访问量 —— 详情请参阅隐私政策。",
         "<p>不会。应用没有账号、没有内置追踪,也没有内置分析。您关注的所有服务仅保存在您的设备上。注意:本网站(vultyr.app)使用无 Cookie 的 Google Analytics 统计聚合访问量 —— 详情请参阅<a href=\"/privacy.html\">隐私政策</a>。</p>"),
        ("如何在多台设备间同步我的服务?",
         "您关注的服务会通过 iCloud 自动同步。主题和设置也会通过 iCloud Key-Value Store 在您所有的 Apple 设备之间同步。",
         "<p>您关注的服务会通过 iCloud 自动同步。主题和设置也会通过 iCloud Key-Value Store 在您所有的 Apple 设备之间同步。</p>"),
        ("主题有哪些选项?",
         "12 款主题:Standard、Terminal、Amber、Blue、Neon、Dracula、Nord、Solarized、Catppuccin、Fossil、Monolith 和 HAL。Standard 和三款复古主题(Terminal、Amber、Blue)已包含在内。Fossil、Monolith、HAL 等其余主题可通过可选的打赏式 IAP($0.99 / $4.99 / $9.99)解锁,这也是在资助开发。主题会自动在您所有设备之间同步。",
         "<p>12 款主题:Standard、Terminal、Amber、Blue、Neon、Dracula、Nord、Solarized、Catppuccin、Fossil、Monolith 和 HAL。Standard 和三款复古主题(Terminal、Amber、Blue)已包含在内。Fossil、Monolith、HAL 等其余主题可通过可选的打赏式 IAP($0.99 / $4.99 / $9.99)解锁,这也是在资助开发。主题会自动在您所有设备之间同步。</p>"),
        ("能否为已知事件静音通知?",
         "可以。查看存在正在发生事件的服务时,您可以在指定时段内静音通知,以免重复收到您已经知晓的提醒。您也可以通过语音静音 —— 「嘿 Siri,将 GitHub 静音 2 小时」—— 或通过 Shortcuts 应用进行操作。",
         "<p>可以。查看存在正在发生事件的服务时,您可以在指定时段内静音通知,以免重复收到您已经知晓的提醒。您也可以通过语音静音 —— 「嘿 Siri,将 GitHub 静音 2 小时」—— 或通过 Shortcuts 应用进行操作。</p>"),
        ("支持哪些平台?",
         "iPhone 和 iPad(支持小组件与 Live Activities)、Mac(提供菜单栏应用与完整窗口)、Apple Watch(支持复杂功能与 Smart Stack)、Apple TV 以及 Apple Vision Pro。应用在每个平台上均可免费下载。",
         "<p>iPhone 和 iPad(支持小组件与 Live Activities)、Mac(提供菜单栏应用与完整窗口)、Apple Watch(支持复杂功能与 Smart Stack)、Apple TV 以及 Apple Vision Pro。应用在每个平台上均可免费下载。</p>"),
        ("可以申请新增服务吗?",
         "可以!请发送邮件至 support@vultyr.app,并提供服务名称及其状态页面的 URL。",
         "<p>可以!请发送邮件至 <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a>,并提供服务名称及其状态页面的 URL。</p>"),
    ],
},
    "zh-Hant": {
    "html_lang": "zh-Hant",
    "og_locale": "zh_TW",
    "og_image_alt": "Vultyr 應用程式圖示 — 服務狀態監控器",
    "devices": "iPhone、iPad、Mac、Apple Watch、Apple TV 與 Vision Pro",
    "skip_to_main": "跳至主要內容",
    "topbar_brand_aria": "Vultyr 首頁",
    "nav_primary_aria": "主要導覽",
    "nav_services": "服務",
    "nav_support": "支援",
    "nav_download": "下載",
    "footer_nav_aria": "頁尾導覽",
    "footer_home": "首頁",
    "footer_services": "服務",
    "footer_privacy": "隱私權",
    "footer_support": "支援",
    "footer_contact": "聯絡我們",
    "copyright": "© 2026 Vultyr。保留所有權利。",
    "breadcrumb_aria": "麵包屑",
    "breadcrumb_vultyr": "Vultyr",
    "breadcrumb_services": "服務",
    # services page
    "svcs_title": "Vultyr — 200+ 項狀態檢查",
    "svcs_description": "涵蓋雲端服務、開發者工具、通訊、AI 等 200+ 項狀態檢查,全由 Vultyr 監控。",
    "svcs_h1_lead": "狀態",
    "svcs_h1_highlight": "檢查",
    "svcs_subtitle": "Vultyr 針對雲端服務、開發者工具與平台執行的 200+ 項狀態檢查。",
    "svcs_categories_aria": "依類別瀏覽",
    "svc_row_status": "狀態頁面",
    "svc_row_homepage": "官方網站",
    "svcs_item_list_name": "Vultyr 監控的服務",
    # service page
    "svcp_title_fmt": "{name} 故障了嗎?{name} 狀態監控器 | Vultyr",
    "svcp_description_fmt": "立即查看 {name} 是否故障。透過 Vultyr 取得即時 {name} 狀態更新與中斷監控。在 {devices} 上免費使用。",
    "svcp_live_check": "即時檢查",
    "svcp_view_current_status": "檢視目前狀態 →",
    "svcp_alert_hint_prefix": "若要取得即時通知,請",
    "svcp_alert_hint_link": "下載 Vultyr",
    "svcp_categories_label": "類別:",
    "svcp_official_status": "官方狀態頁面",
    "svcp_homepage_fmt": "{name} 官方網站",
    "svcp_faq_heading": "常見問題",
    "svcp_faq_q1_fmt": "{name} 現在故障了嗎?",
    "svcp_faq_a1_fmt": "請查看上方連結的 {name} 官方狀態頁面以確認目前狀況。若需要持續監控並在所有 Apple 裝置上取得即時中斷通知,請下載免費的 Vultyr 應用程式。",
    "svcp_faq_a1_ld_fmt": "請至 {url} 查看 {name} 的官方狀態頁面以確認目前狀況。下載免費的 Vultyr 應用程式,即可在所有 Apple 裝置上取得即時中斷通知。",
    "svcp_faq_q2_fmt": "如何監控 {name} 的狀態?",
    "svcp_faq_a2_fmt": "Vultyr 將 {name} 納入涵蓋雲端服務、開發者工具與平台的 200+ 項狀態檢查中。在 {devices} 上取得即時中斷通知 — 完全免費。",
    "svcp_faq_a2_ld_fmt": "下載 Vultyr(免費),將 {name} 納入 200+ 項狀態檢查中,並在 {devices} 上取得即時通知。Vultyr 會自動執行每一項檢查,並在偵測到中斷的當下通知您。",
    "svcp_related_heading": "相關服務",
    "svcp_related_aria": "相關服務",
    "svcp_cta_heading_fmt": "在所有裝置上監控 {name}",
    "svcp_cta_body_fmt": "當 {name} 故障時立即取得通知。在所有 Apple 平台上免費使用。",
    "cta_download_vultyr": "下載 Vultyr",
    "cta_download_vultyr_aria": "在 App Store 下載 Vultyr",
    # category page
    "catp_title_fmt": "{name} 狀態監控器 — {count_services} | Vultyr",
    "catp_description_fmt": "監控「{name_lower}」分類中 {count_services} 的狀態。提供 {sample} 等服務的即時中斷通知。",
    "catp_item_list_name_fmt": "{name} 狀態監控器",
    "catp_subtitle_fmt": "由 Vultyr 監控的 {count_services}",
    "catp_services_aria_fmt": "{name} 服務",
    "catp_other_heading": "其他類別",
    "catp_cta_heading_fmt": "立即監控全部 {count_services}",
    "catp_cta_body": "在所有 Apple 裝置上取得即時中斷通知。免費。",
    # home page
    "home_title": "Vultyr — AWS、Slack、GitHub 等服務狀態監控器",
    "home_description": "故障了嗎?涵蓋雲端服務、開發者工具與平台的 200+ 項狀態檢查,並提供即時中斷通知。在 iPhone、iPad、Mac、Apple Watch、Apple TV 與 Apple Vision Pro 上免費使用。",
    "home_og_title": "Vultyr — 服務狀態監控器",
    "home_app_ld_description": "監控涵蓋雲端服務、開發者工具與平台的 200+ 項狀態檢查,並取得即時中斷通知。",
    "home_hero_tag": "200+ 項檢查",
    "home_hero_question": "故障了嗎?",
    "home_hero_answer": "在使用者發現之前就先一步掌握。",
    "home_hero_services": "200+ 項狀態檢查 — AWS、GitHub、Slack、Stripe 等 — 並在每部 Apple 裝置上提供即時中斷通知。",
    "home_appstore_alt": "在 App Store 下載",
    "home_appstore_aria": "在 App Store 下載 Vultyr",
    "home_free_on_prefix": "免費提供於",
    "home_screenshots_aria": "應用程式截圖",
    "home_screenshot_dash_alt": "Vultyr 儀表板顯示「一切正常」狀態,監控 AWS、GitHub、Slack 等服務",
    "home_screenshot_settings_alt_fmt": "Vultyr 外觀設定提供 {themes} 種主題,包含 Terminal、Amber、Dracula 與 Nord",
    "home_screenshot_services_alt_fmt": "Vultyr 服務瀏覽器顯示 {categories} 個類別,包含 Cloud、Dev Tools 與 AI",
    "home_stats_aria": "關鍵數據",
    "home_stats_checks": "項檢查",
    "home_stats_categories": "個類別",
    "home_stats_platforms": "個平台",
    "home_stats_languages": "種語言",
    "home_features_heading": "掌握中斷狀況所需的一切",
    "home_features_sub": "不需應用程式帳號、無應用程式內追蹤。只有狀態。",
    "home_bottom_heading": "準備好監控您的技術堆疊了嗎?",
    "home_bottom_sub": "免費。不需應用程式帳號。隨處可用。",
    "home_bottom_button": "免費下載",
    "home_bottom_aria": "在 App Store 免費下載 Vultyr",
    "home_languages_heading": "提供 17 種語言",
    "home_features": [
        ("chart-bar-regular.svg", "即時狀態儀表板",
         "AWS、GitHub、Cloudflare、Slack、Stripe、Discord、OpenAI、Anthropic 和 200+ 服務 — 一個地方盡覽。狀態圖示與 iPhone Pro 和 iPad Pro 的 120Hz ProMotion 同步。"),
        ("bell-ringing-regular.svg", "智慧通知",
         "iOS 上有各服務圖示的故障與復原通知。重大故障的脈動明顯大於輕微事件，嚴重程度一目瞭然。靜音已知事件，為關鍵服務標星。"),
        ("microphone-regular.svg", "Siri 與 Shortcuts",
         "對 Siri 說「將 GitHub 靜音 2 小時」或「顯示目前問題」。每個動作皆有 App Intents,並提供 Focus Filter 以靜音非關鍵服務。"),
        ("squares-four-regular.svg", "小工具與 Live Activities",
         "iOS 上提供主畫面與鎖定畫面小工具,以及 Control Center 小工具。進行中的中斷會固定於 Dynamic Island。"),
        ("watch-regular.svg", "手錶複雜功能",
         "將關鍵服務固定於錶面,或讓 Smart Stack 自動顯示進行中的問題。"),
        ("cloud-check-regular.svg", "Mac 作為中心 — iPhone 作為備用",
         "Mac 是最可靠的中心：最快每 60 秒輪詢一次（可設定至 15 分鐘），並透過 iCloud 將狀態變化廣播至 iPhone、iPad、Watch 和 Vision Pro。如果沒有 Mac 在線，你的 iPhone 會接替成為備用發布者，讓其他設備仍然能收到警報。"),
        ("monitor-regular.svg", "警報可靠性檢視",
         "一目瞭然地檢視警報是否能真正送至你 — Mac 心跳、背景重新整理狀態、CloudKit 推送以及每台裝置的最後檢查時間。"),
        ("devices-regular.svg", "所有 Apple 平台",
         "iPhone、iPad、Mac 選單列、Apple TV、Apple Watch 與 Vision Pro。服務在所有裝置間同步。"),
        ("lightning-regular.svg", "事件詳情",
         "受影響的元件、進行中的事件、排定的維護與時間軸更新 — 皆以您的語言顯示。"),
        ("battery-charging-regular.svg", "電量感知輪詢",
         "智能自動重新整理根據電量、電源狀態和溫度自適應。Mac 上每分鐘一次，iPhone 上 5–15 分鐘一次，iPad、Apple Watch、Vision Pro 和 Apple TV 支援背景重新整理。"),
        ("palette-regular.svg", f"{THEMES_COUNT} 種主題",
         "內建 Standard 與三款復古主題。Fossil、Monolith、HAL 與其他主題則透過選擇性的小費罐 App 內購解鎖。"),
        ("shield-check-regular.svg", "應用程式資料保留於本機",
         "應用程式無需註冊,亦無應用程式內分析。您所關注的服務會留在您的裝置上。"),
        ("translate-regular.svg", f"{APP_LANGUAGE_COUNT} 種應用程式語言",
         "英文、德文、法文、西班牙文、日文、韓文、中文、葡萄牙文、俄文等。"),
    ],
    # 404
    "err_title": "找不到頁面 — Vultyr",
    "err_description": "您所尋找的頁面不存在。",
    "err_heading": "找不到頁面",
    "err_message": "您所尋找的頁面不存在或已被移動。",
    "redirect_moved_fmt": "此頁面已移動。正在重新導向至 {name}…",
    "err_popular_heading": "熱門服務",
    "err_browse_heading": "瀏覽類別",
    # privacy
    "privacy_title": "隱私權政策",
    "privacy_description": "Vultyr 隱私權政策。應用程式不收集任何個人資料。本網站使用無 Cookie 的 Google Analytics 以彙總訪客流量資料。",
    "privacy_last_updated": "最後更新:2026 年 4 月 11 日",
    "privacy_sections": [
        ("摘要",
         "<p>Vultyr <strong>應用程式</strong>不收集、儲存或傳輸任何個人資料。Vultyr <strong>網站</strong>(vultyr.app)使用無 Cookie 的 Google Analytics 以瞭解彙總訪客流量。本頁將詳細說明兩者。</p>"),
        ("應用程式 — 資料收集",
         "<p>vultyr 應用程式不收集任何個人資訊。不需註冊帳號、未內建任何第三方分析或追蹤 SDK,亦不會回報至我方所營運的伺服器。</p>"),
        ("應用程式 — 網路請求",
         "<p>應用程式會直接向公開的狀態頁面 API(例如 Statuspage.io、Apple、Google Cloud 等)發送 HTTPS 請求,以檢查服務狀態。這些請求會自您的裝置直接送往服務的公開 API — 不會經過我方營運的任何伺服器。</p>"),
        ("應用程式 — 資料儲存",
         "<p>所有資料皆使用 Apple 的 SwiftData 框架儲存於您的裝置本機。若您啟用 iCloud 同步,您所關注的服務清單會透過 Apple 的 iCloud Key-Value Store 同步,該服務受 Apple 的隱私權政策規範。我方永遠無法看見這些資料。</p>"),
        ("應用程式 — 跨裝置通知",
         "<p>若您啟用「跨裝置通知」,狀態變更會透過 Apple 的 iCloud Key-Value Store 在您的裝置間共享。當您的 Mac 偵測到狀態變更時,會在您的 iCloud 帳號中寫入一個輕量訊號。其他裝置會觀察到此變更並各自執行本機檢查。過程中不涉及任何第三方伺服器 — 所有通訊皆透過 Apple 的 iCloud 基礎架構進行。您可在任一裝置上切換此功能。</p>"),
        ("應用程式 — Favicon",
         "<p>服務的 favicon 會自 Google 公開的 favicon 服務抓取,並快取於您的裝置本機。</p>"),
        ("網站 — 分析",
         "<p>本網站(vultyr.app)使用無 Cookie、IP 匿名化模式的 Google Analytics 4,以統計彙總網頁瀏覽數。具體而言,我們以下列參數設定 gtag.js:<code>anonymize_ip: true</code>、<code>client_storage: 'none'</code>、<code>allow_google_signals: false</code>、<code>allow_ad_personalization_signals: false</code>。這表示不會設定 <code>_ga</code> Cookie、您的 IP 會在儲存前被截短,亦不會收集廣告識別碼。vultyr 應用程式本身不包含任何分析機制。</p>"),
        ("網站 — 第三方網域",
         "<p>載入 vultyr.app 會連線至下列第三方網域:</p>\n    <ul>\n        <li><strong>www.googletagmanager.com</strong> — 載入 gtag.js 指令碼</li>\n        <li><strong>www.google-analytics.com</strong> / <strong>*.analytics.google.com</strong> — 接收匿名化的網頁瀏覽信標</li>\n        <li><strong>www.google.com/g/collect</strong> — 接收相同的匿名化網頁瀏覽信標(Google Analytics 4 備援收集端點)</li>\n    </ul>\n    <p>我們不載入 Google Fonts(Audiowide 字型自行寄存於 vultyr.app),亦不使用第三方 favicon 服務來提供網站本身的圖像。</p>"),
        ("應用程式 — 第三方服務",
         "<p>vultyr 應用程式未整合任何第三方分析、廣告或追蹤服務。唯一的外部請求僅限於公開狀態 API 與 Google 的 favicon 服務。</p>"),
        ("兒童隱私",
         "<p>vultyr 應用程式不會自任何人(包含 13 歲以下的兒童)收集資料。網站僅記錄匿名化的彙總訪客計數。</p>"),
        ("異動",
         "<p>若本政策有所變更,我們將更新上方的日期。</p>"),
        ("聯絡我們",
         "<p>有任何問題嗎?請來信至 <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a></p>"),
    ],
    # support
    "support_title": "支援",
    "support_description": "取得 Vultyr 的協助 — 適用於 iPhone、iPad、Mac、Apple Watch、Apple TV 與 Apple Vision Pro 的服務狀態監控器。常見問題、聯絡方式與疑難排解。",
    "support_contact_heading": "聯絡我們",
    "support_contact_html": "<p>如需回報錯誤、提出功能建議或詢問問題,請來信:<br>\n    <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a></p>",
    "support_faq_heading": "常見問題",
    "support_faqs": [
        ("vultyr 多久檢查一次服務狀態?",
         "Mac 上:接上電源時,最短可每 60 秒一次。iPhone 上:每 5、10 或 15 分鐘(可設定),並在條件允許時進行週期性的背景檢查。Apple Watch 上:每 15 分鐘。Apple TV 上:每 5 分鐘。輪詢會自動依電量、電源狀態與機身溫度調整。",
         "<p>Mac 上:接上電源時,最短可每 60 秒一次。iPhone 上:每 5、10 或 15 分鐘(可設定),並在條件允許時進行週期性的背景檢查。Apple Watch 上:每 15 分鐘。Apple TV 上:每 5 分鐘。輪詢會自動依電量、電源狀態與機身溫度調整。</p>"),
        ("跨裝置通知如何運作?",
         "Mac 應用程式是中樞。讓它持續執行(選單列或完整視窗皆可),它會最快每 60 秒輪詢一次（可設定至 15 分鐘）。偵測到狀態變更時,它會寫入一個輕量訊號至 iCloud Key-Value Store;您的 iPhone、iPad、Watch、Apple TV 與 Vision Pro 會接收此變更並各自執行本機檢查。無需金鑰、無需權杖、無需設定 — 只要在任一裝置的設定中啟用「跨裝置通知」即可。若沒有 Mac 擔任中樞,通知將仰賴 iOS 背景執行,會被延遲或錯過。",
         "<p>Mac 應用程式是中樞。讓它持續執行(選單列或完整視窗皆可),它會最快每 60 秒輪詢一次（可設定至 15 分鐘）。偵測到狀態變更時,它會寫入一個輕量訊號至 iCloud Key-Value Store;您的 iPhone、iPad、Watch、Apple TV 與 Vision Pro 會接收此變更並各自執行本機檢查。無需金鑰、無需權杖、無需設定 — 只要在任一裝置的設定中啟用「跨裝置通知」即可。若沒有 Mac 擔任中樞,通知將仰賴 iOS 背景執行,會被延遲或錯過。</p>"),
        ("我需要 Mac 應用程式才能取得可靠的通知嗎?",
         "需要 — 我們強烈建議使用。iOS 會限制背景執行,因此 iPhone 與 iPad 僅能每 5 至 15 分鐘檢查一次(可設定),且在低電量、低耗電模式或連線不佳時可能進一步延後。Mac 應用程式會持續輪詢(接上電源時每 60 秒一次),並透過 iCloud 將狀態變更廣播至其他裝置。若沒有執行 Vultyr 的 Mac,iOS、watchOS 與 tvOS 上的通知仍可運作,但可能會顯著延遲或被錯過。若要進行即時監控,請讓 Mac 應用程式持續執行 — 它在選單列上占用極小,正是 Vultyr 原本設計的使用方式。",
         "<p>需要 — 我們強烈建議使用。iOS 會限制背景執行,因此 iPhone 與 iPad 僅能每 5 至 15 分鐘檢查一次(可設定),且在低電量、低耗電模式或連線不佳時可能進一步延後。Mac 應用程式會持續輪詢(接上電源時每 60 秒一次),並透過 iCloud 將狀態變更廣播至其他裝置。若沒有執行 Vultyr 的 Mac,iOS、watchOS 與 tvOS 上的通知仍可運作,但可能會顯著延遲或被錯過。若要進行即時監控,請讓 Mac 應用程式持續執行 — 它在選單列上占用極小,正是 Vultyr 原本設計的使用方式。</p>"),
        ("vultyr 支援 Siri 與 Shortcuts 嗎?",
         "支援。內建 App Intents 讓您可以說「嘿 Siri,將 GitHub 靜音 2 小時」、「檢查 Stripe 狀態」或「顯示目前問題」,您也可以將這些相同動作串接至 Shortcuts 應用程式。此外還提供 Focus Filter,讓「vultyr Focus」模式可自動靜音非關鍵服務。",
         "<p>支援。內建 App Intents 讓您可以說「嘿 Siri,將 GitHub 靜音 2 小時」、「檢查 Stripe 狀態」或「顯示目前問題」,您也可以將這些相同動作串接至 Shortcuts 應用程式。此外還提供 Focus Filter,讓「vultyr Focus」模式可自動靜音非關鍵服務。</p>"),
        ("有小工具與 Live Activities 嗎?",
         "iOS 上提供主畫面與鎖定畫面小工具(單一服務與狀態摘要)以及 Control Center 小工具。進行中的中斷會以 Live Activities 形式固定於 Dynamic Island。watchOS 上所有錶面皆可使用複雜功能,並具備 Smart Stack 相關性,讓有問題的服務在適當時機自動顯示。",
         "<p>iOS 上提供主畫面與鎖定畫面小工具(單一服務與狀態摘要)以及 Control Center 小工具。進行中的中斷會以 Live Activities 形式固定於 Dynamic Island。watchOS 上所有錶面皆可使用複雜功能,並具備 Smart Stack 相關性,讓有問題的服務在適當時機自動顯示。</p>"),
        ("vultyr 應用程式會收集我的資料嗎?",
         "不會。應用程式沒有帳號、沒有應用程式內追蹤、沒有應用程式內分析。您所關注的服務全部留在您的裝置上。請注意:本網站(vultyr.app)使用無 Cookie 的 Google Analytics 以彙總訪客計數 — 詳情請參閱隱私權政策。",
         "<p>不會。應用程式沒有帳號、沒有應用程式內追蹤、沒有應用程式內分析。您所關注的服務全部留在您的裝置上。請注意:本網站(vultyr.app)使用無 Cookie 的 Google Analytics 以彙總訪客計數 — 詳情請參閱<a href=\"/privacy.html\">隱私權政策</a>。</p>"),
        ("如何在各裝置間同步我的服務?",
         "您所關注的服務會透過 iCloud 自動同步。主題與設定也會透過 iCloud Key-Value Store 在所有 Apple 裝置間同步。",
         "<p>您所關注的服務會透過 iCloud 自動同步。主題與設定也會透過 iCloud Key-Value Store 在所有 Apple 裝置間同步。</p>"),
        ("有哪些主題可以選擇?",
         "共 12 種主題:Standard、Terminal、Amber、Blue、Neon、Dracula、Nord、Solarized、Catppuccin、Fossil、Monolith 與 HAL。Standard 與三款復古主題(Terminal、Amber、Blue)為內建提供。Fossil、Monolith、HAL 與其他主題則透過選擇性的小費罐 App 內購($0.99 / $4.99 / $9.99)解鎖,同時也有助於支持開發。主題會自動在所有裝置間同步。",
         "<p>共 12 種主題:Standard、Terminal、Amber、Blue、Neon、Dracula、Nord、Solarized、Catppuccin、Fossil、Monolith 與 HAL。Standard 與三款復古主題(Terminal、Amber、Blue)為內建提供。Fossil、Monolith、HAL 與其他主題則透過選擇性的小費罐 App 內購($0.99 / $4.99 / $9.99)解鎖,同時也有助於支持開發。主題會自動在所有裝置間同步。</p>"),
        ("我能為已知的事件靜音通知嗎?",
         "可以。檢視有進行中事件的服務時,您可將通知靜音一段時間,避免反覆收到您已知問題的通知。您也可以透過語音靜音 — 「嘿 Siri,將 GitHub 靜音 2 小時」 — 或從 Shortcuts 應用程式執行。",
         "<p>可以。檢視有進行中事件的服務時,您可將通知靜音一段時間,避免反覆收到您已知問題的通知。您也可以透過語音靜音 — 「嘿 Siri,將 GitHub 靜音 2 小時」 — 或從 Shortcuts 應用程式執行。</p>"),
        ("支援哪些平台?",
         "iPhone 與 iPad(含小工具與 Live Activities)、Mac(含選單列應用程式與完整視窗)、Apple Watch(含複雜功能與 Smart Stack)、Apple TV 以及 Apple Vision Pro。應用程式在每個平台上皆可免費下載。",
         "<p>iPhone 與 iPad(含小工具與 Live Activities)、Mac(含選單列應用程式與完整視窗)、Apple Watch(含複雜功能與 Smart Stack)、Apple TV 以及 Apple Vision Pro。應用程式在每個平台上皆可免費下載。</p>"),
        ("我可以提議新的服務嗎?",
         "當然可以!請來信 support@vultyr.app 並附上服務名稱與其狀態頁面網址。",
         "<p>當然可以!請來信 <a href=\"mailto:support@vultyr.app\">support@vultyr.app</a> 並附上服務名稱與其狀態頁面網址。</p>"),
    ],
},
}

# Per-locale translations of category names, keyed by slug. Locales without
# an entry fall back to the source name in data/services.json.
CATEGORY_NAMES = {}
CATEGORY_NAMES["ru"] = {
    "cloud-infrastructure": "\u041e\u0431\u043b\u0430\u043a\u043e \u0438 \u0438\u043d\u0444\u0440\u0430\u0441\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u0430",
    "developer-tools": "\u0418\u043d\u0441\u0442\u0440\u0443\u043c\u0435\u043d\u0442\u044b \u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u0447\u0438\u043a\u0430",
    "communication": "\u041a\u043e\u043c\u043c\u0443\u043d\u0438\u043a\u0430\u0446\u0438\u0438",
    "productivity-saas": "\u041f\u0440\u043e\u0434\u0443\u043a\u0442\u0438\u0432\u043d\u043e\u0441\u0442\u044c \u0438 SaaS",
    "payments-commerce": "\u041f\u043b\u0430\u0442\u0435\u0436\u0438 \u0438 \u043a\u043e\u043c\u043c\u0435\u0440\u0446\u0438\u044f",
    "apple": "Apple",
    "google": "Google",
    "microsoft": "Microsoft",
    "amazon": "Amazon",
    "ai-machine-learning": "\u0418\u0418 \u0438 \u043c\u0430\u0448\u0438\u043d\u043d\u043e\u0435 \u043e\u0431\u0443\u0447\u0435\u043d\u0438\u0435",
    "social-media": "\u0421\u043e\u0446\u0438\u0430\u043b\u044c\u043d\u044b\u0435 \u0441\u0435\u0442\u0438",
    "streaming-media": "\u0421\u0442\u0440\u0438\u043c\u0438\u043d\u0433 \u0438 \u043c\u0435\u0434\u0438\u0430",
    "gaming": "\u0418\u0433\u0440\u044b",
    "telecom-isp": "\u0422\u0435\u043b\u0435\u043a\u043e\u043c \u0438 \u043f\u0440\u043e\u0432\u0430\u0439\u0434\u0435\u0440\u044b",
    "security": "\u0411\u0435\u0437\u043e\u043f\u0430\u0441\u043d\u043e\u0441\u0442\u044c",
    "email-marketing": "Email \u0438 \u043c\u0430\u0440\u043a\u0435\u0442\u0438\u043d\u0433",
}

CATEGORY_NAMES["da"] = {
    "cloud-infrastructure": "Cloud og infrastruktur",
    "developer-tools": "Udviklerværktøjer",
    "communication": "Kommunikation",
    "productivity-saas": "Produktivitet og SaaS",
    "payments-commerce": "Betalinger og handel",
    "apple": "Apple",
    "google": "Google",
    "microsoft": "Microsoft",
    "amazon": "Amazon",
    "ai-machine-learning": "AI og maskinlæring",
    "social-media": "Sociale medier",
    "streaming-media": "Streaming og medier",
    "gaming": "Gaming",
    "telecom-isp": "Telekom og internetudbydere",
    "security": "Sikkerhed",
    "email-marketing": "E-mail og marketing",
}

CATEGORY_NAMES["de"] = {
    "cloud-infrastructure": "Cloud und Infrastruktur",
    "developer-tools": "Entwickler-Tools",
    "communication": "Kommunikation",
    "productivity-saas": "Produktivität und SaaS",
    "payments-commerce": "Zahlungen und Commerce",
    "apple": "Apple",
    "google": "Google",
    "microsoft": "Microsoft",
    "amazon": "Amazon",
    "ai-machine-learning": "KI und maschinelles Lernen",
    "social-media": "Soziale Medien",
    "streaming-media": "Streaming und Medien",
    "gaming": "Gaming",
    "telecom-isp": "Telekom und Provider",
    "security": "Sicherheit",
    "email-marketing": "E-Mail und Marketing",
}

CATEGORY_NAMES["es"] = {
    "cloud-infrastructure": "Nube e infraestructura",
    "developer-tools": "Herramientas para desarrolladores",
    "communication": "Comunicación",
    "productivity-saas": "Productividad y SaaS",
    "payments-commerce": "Pagos y comercio",
    "apple": "Apple",
    "google": "Google",
    "microsoft": "Microsoft",
    "amazon": "Amazon",
    "ai-machine-learning": "IA y aprendizaje automático",
    "social-media": "Redes sociales",
    "streaming-media": "Streaming y multimedia",
    "gaming": "Videojuegos",
    "telecom-isp": "Telecomunicaciones y proveedores de internet",
    "security": "Seguridad",
    "email-marketing": "Correo y marketing",
}

CATEGORY_NAMES["fr"] = {
    "cloud-infrastructure": "Cloud et infrastructure",
    "developer-tools": "Outils pour d\u00e9veloppeurs",
    "communication": "Communication",
    "productivity-saas": "Productivit\u00e9 et SaaS",
    "payments-commerce": "Paiements et commerce",
    "apple": "Apple",
    "google": "Google",
    "microsoft": "Microsoft",
    "amazon": "Amazon",
    "ai-machine-learning": "IA et apprentissage automatique",
    "social-media": "R\u00e9seaux sociaux",
    "streaming-media": "Streaming et m\u00e9dias",
    "gaming": "Jeux vid\u00e9o",
    "telecom-isp": "T\u00e9l\u00e9coms et FAI",
    "security": "S\u00e9curit\u00e9",
    "email-marketing": "E\u2011mail et marketing",
}

CATEGORY_NAMES["it"] = {
    "cloud-infrastructure": "Cloud e infrastruttura",
    "developer-tools": "Strumenti per sviluppatori",
    "communication": "Comunicazione",
    "productivity-saas": "Produttività e SaaS",
    "payments-commerce": "Pagamenti ed e-commerce",
    "apple": "Apple",
    "google": "Google",
    "microsoft": "Microsoft",
    "amazon": "Amazon",
    "ai-machine-learning": "IA e machine learning",
    "social-media": "Social media",
    "streaming-media": "Streaming e media",
    "gaming": "Videogiochi",
    "telecom-isp": "Telecomunicazioni e provider",
    "security": "Sicurezza",
    "email-marketing": "Email e marketing",
}

CATEGORY_NAMES["ja"] = {
    "cloud-infrastructure": "クラウドとインフラ",
    "developer-tools": "開発者向けツール",
    "communication": "コミュニケーション",
    "productivity-saas": "生産性とSaaS",
    "payments-commerce": "決済とコマース",
    "apple": "Apple",
    "google": "Google",
    "microsoft": "Microsoft",
    "amazon": "Amazon",
    "ai-machine-learning": "AIと機械学習",
    "social-media": "ソーシャルメディア",
    "streaming-media": "ストリーミングとメディア",
    "gaming": "ゲーム",
    "telecom-isp": "通信とISP",
    "security": "セキュリティ",
    "email-marketing": "メールとマーケティング",
}

CATEGORY_NAMES["ko"] = {
    "cloud-infrastructure": "클라우드 및 인프라",
    "developer-tools": "개발자 도구",
    "communication": "커뮤니케이션",
    "productivity-saas": "생산성 및 SaaS",
    "payments-commerce": "결제 및 커머스",
    "apple": "Apple",
    "google": "Google",
    "microsoft": "Microsoft",
    "amazon": "Amazon",
    "ai-machine-learning": "AI 및 머신러닝",
    "social-media": "소셜 미디어",
    "streaming-media": "스트리밍 및 미디어",
    "gaming": "게이밍",
    "telecom-isp": "통신 및 ISP",
    "security": "보안",
    "email-marketing": "이메일 및 마케팅",
}

CATEGORY_NAMES["nb"] = {
    "cloud-infrastructure": "Sky og infrastruktur",
    "developer-tools": "Utviklerverktøy",
    "communication": "Kommunikasjon",
    "productivity-saas": "Produktivitet og SaaS",
    "payments-commerce": "Betaling og handel",
    "apple": "Apple",
    "google": "Google",
    "microsoft": "Microsoft",
    "amazon": "Amazon",
    "ai-machine-learning": "KI og maskinlæring",
    "social-media": "Sosiale medier",
    "streaming-media": "Strømming og media",
    "gaming": "Spill",
    "telecom-isp": "Telekom og nettleverandører",
    "security": "Sikkerhet",
    "email-marketing": "E-post og markedsføring",
}

CATEGORY_NAMES["nl"] = {
    "cloud-infrastructure": "Cloud en infrastructuur",
    "developer-tools": "Ontwikkeltools",
    "communication": "Communicatie",
    "productivity-saas": "Productiviteit en SaaS",
    "payments-commerce": "Betalingen en handel",
    "apple": "Apple",
    "google": "Google",
    "microsoft": "Microsoft",
    "amazon": "Amazon",
    "ai-machine-learning": "AI en machine learning",
    "social-media": "Sociale media",
    "streaming-media": "Streaming en media",
    "gaming": "Games",
    "telecom-isp": "Telecom en providers",
    "security": "Beveiliging",
    "email-marketing": "E-mail en marketing",
}

CATEGORY_NAMES["pt-BR"] = {
    "cloud-infrastructure": "Nuvem e infraestrutura",
    "developer-tools": "Ferramentas de desenvolvimento",
    "communication": "Comunicação",
    "productivity-saas": "Produtividade e SaaS",
    "payments-commerce": "Pagamentos e comércio",
    "apple": "Apple",
    "google": "Google",
    "microsoft": "Microsoft",
    "amazon": "Amazon",
    "ai-machine-learning": "IA e aprendizado de máquina",
    "social-media": "Redes sociais",
    "streaming-media": "Streaming e mídia",
    "gaming": "Jogos",
    "telecom-isp": "Telecom e provedores",
    "security": "Segurança",
    "email-marketing": "E-mail e marketing",
}

CATEGORY_NAMES["sv"] = {
    "cloud-infrastructure": "Moln och infrastruktur",
    "developer-tools": "Utvecklarverktyg",
    "communication": "Kommunikation",
    "productivity-saas": "Produktivitet och SaaS",
    "payments-commerce": "Betalningar och e-handel",
    "apple": "Apple",
    "google": "Google",
    "microsoft": "Microsoft",
    "amazon": "Amazon",
    "ai-machine-learning": "AI och maskininlärning",
    "social-media": "Sociala medier",
    "streaming-media": "Streaming och media",
    "gaming": "Spel",
    "telecom-isp": "Telekom och internetleverantörer",
    "security": "Säkerhet",
    "email-marketing": "E-post och marknadsföring",
}

CATEGORY_NAMES["tr"] = {
    "cloud-infrastructure": "Bulut ve altyapı",
    "developer-tools": "Geliştirici araçları",
    "communication": "İletişim",
    "productivity-saas": "Üretkenlik ve SaaS",
    "payments-commerce": "Ödemeler ve ticaret",
    "apple": "Apple",
    "google": "Google",
    "microsoft": "Microsoft",
    "amazon": "Amazon",
    "ai-machine-learning": "Yapay zekâ ve makine öğrenmesi",
    "social-media": "Sosyal medya",
    "streaming-media": "Yayın ve medya",
    "gaming": "Oyun",
    "telecom-isp": "Telekom ve internet sağlayıcılar",
    "security": "Güvenlik",
    "email-marketing": "E-posta ve pazarlama",
}

CATEGORY_NAMES["vi"] = {
    "cloud-infrastructure": "Đám mây và hạ tầng",
    "developer-tools": "Công cụ lập trình",
    "communication": "Liên lạc",
    "productivity-saas": "Năng suất và SaaS",
    "payments-commerce": "Thanh toán và thương mại",
    "apple": "Apple",
    "google": "Google",
    "microsoft": "Microsoft",
    "amazon": "Amazon",
    "ai-machine-learning": "AI và học máy",
    "social-media": "Mạng xã hội",
    "streaming-media": "Truyền phát và đa phương tiện",
    "gaming": "Trò chơi",
    "telecom-isp": "Viễn thông và nhà mạng",
    "security": "Bảo mật",
    "email-marketing": "Email và tiếp thị",
}

CATEGORY_NAMES["zh-Hans"] = {
    "cloud-infrastructure": "云服务与基础设施",
    "developer-tools": "开发者工具",
    "communication": "通讯协作",
    "productivity-saas": "生产力与 SaaS",
    "payments-commerce": "支付与电商",
    "apple": "Apple",
    "google": "Google",
    "microsoft": "Microsoft",
    "amazon": "Amazon",
    "ai-machine-learning": "AI 与机器学习",
    "social-media": "社交媒体",
    "streaming-media": "流媒体",
    "gaming": "游戏",
    "telecom-isp": "电信与网络服务商",
    "security": "安全",
    "email-marketing": "邮件与营销",
}

CATEGORY_NAMES["zh-Hant"] = {
    "cloud-infrastructure": "雲端與基礎架構",
    "developer-tools": "開發者工具",
    "communication": "通訊協作",
    "productivity-saas": "生產力與 SaaS",
    "payments-commerce": "支付與電商",
    "apple": "Apple",
    "google": "Google",
    "microsoft": "Microsoft",
    "amazon": "Amazon",
    "ai-machine-learning": "AI 與機器學習",
    "social-media": "社群媒體",
    "streaming-media": "串流與媒體",
    "gaming": "遊戲",
    "telecom-isp": "電信與網路服務",
    "security": "資安",
    "email-marketing": "電子郵件與行銷",
}


def t(locale, key):
    """Fetch a string for a locale, falling back to English if missing.
    Locales not yet present in STRINGS fall back wholesale to English so the
    site still renders while translations are filled in."""
    bundle = STRINGS.get(locale, STRINGS[DEFAULT_LOCALE])
    if key in bundle:
        return bundle[key]
    return STRINGS[DEFAULT_LOCALE][key]


def category_display_name(cat, locale):
    """Return the display name for a category in the given locale, falling
    back to the source name from data/services.json when no translation exists."""
    names = CATEGORY_NAMES.get(locale, {})
    return names.get(cat["slug"], cat["name"])


def count_services_phrase(locale, n):
    """Return '{n} Services' / '{n} сервиса' with correct Russian plural form."""
    if locale == "ru":
        mod10 = n % 10
        mod100 = n % 100
        if 11 <= mod100 <= 14:
            word = "\u0441\u0435\u0440\u0432\u0438\u0441\u043e\u0432"
        elif mod10 == 1:
            word = "\u0441\u0435\u0440\u0432\u0438\u0441"
        elif 2 <= mod10 <= 4:
            word = "\u0441\u0435\u0440\u0432\u0438\u0441\u0430"
        else:
            word = "\u0441\u0435\u0440\u0432\u0438\u0441\u043e\u0432"
        return f"{n} {word}"
    word = "Service" if n == 1 else "Services"
    return f"{n} {word}"


# ─── PATH / URL HELPERS ────────────────────────────────────────────────────────

def locale_prefix(locale):
    return "" if locale == DEFAULT_LOCALE else f"/{locale}"


def home_url_path(locale):
    return "/" if locale == DEFAULT_LOCALE else f"/{locale}/"


def services_path(locale):
    return f"{locale_prefix(locale)}/services.html"


def service_path(locale, slug):
    return f"{locale_prefix(locale)}/status/{slug}.html"


def category_path(locale, slug):
    return f"{locale_prefix(locale)}/categories/{slug}.html"


def privacy_path(locale):
    return f"{locale_prefix(locale)}/privacy.html"


def support_path(locale):
    return f"{locale_prefix(locale)}/support.html"


def absolute(url_path):
    return f"{SITE_ORIGIN}{url_path}"


# ─── HELPERS ───────────────────────────────────────────────────────────────────

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
    """Build a CSP that avoids unsafe-inline while allowing hashed JSON-LD.

    Note: directives like frame-ancestors, form-action, sandbox, and report-uri
    are silently ignored when CSP is delivered via <meta http-equiv> (per CSP3
    spec). GitHub Pages cannot set HTTP headers, so we omit them here rather
    than create a false sense of security.
    """
    script_src = ["'self'", "https://www.googletagmanager.com", *script_hashes]
    directives = [
        "default-src 'self'",
        f"script-src {' '.join(script_src)}",
        "style-src 'self'",
        "font-src 'self'",
        "img-src 'self' data:",
        "connect-src 'self' https://www.google-analytics.com https://*.analytics.google.com https://www.googletagmanager.com https://www.google.com/g/collect",
        "object-src 'none'",
        "base-uri 'self'",
    ]
    return "; ".join(directives)


def hreflang_links(alt_urls):
    """Build <link rel="alternate" hreflang=...> tags for each locale.
    alt_urls is a dict locale -> url-path (relative). x-default points at en."""
    lines = []
    for loc in LOCALES:
        if loc in alt_urls:
            lines.append(f'    <link rel="alternate" hreflang="{loc}" href="{absolute(alt_urls[loc])}">')
    if DEFAULT_LOCALE in alt_urls:
        lines.append(f'    <link rel="alternate" hreflang="x-default" href="{absolute(alt_urls[DEFAULT_LOCALE])}">')
    return "\n".join(lines)


def head_common(script_hashes=()):
    """Shared head tags: charset, viewport, CSP, preconnects, font preload,
    and the locale-detect script (loaded synchronously so it can redirect
    before the page paints if the user's preferred locale differs)."""
    return "\n".join([
        '    <meta charset="UTF-8">',
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f'    <meta http-equiv="Content-Security-Policy" content="{build_csp(script_hashes=script_hashes)}">',
        '    <link rel="preconnect" href="https://www.googletagmanager.com">',
        '    <link rel="preconnect" href="https://www.google-analytics.com" crossorigin>',
        '    <link rel="preload" as="font" type="font/woff2" href="/assets/fonts/audiowide.woff2" crossorigin>',
        f'    <script src="/assets/js/locale-detect.js?v={ASSET_VERSION}"></script>',
        f'    <script defer src="/assets/js/lang-switch.js?v={ASSET_VERSION}"></script>',
    ])


def topbar_html(locale):
    """Top navigation. Language selection lives in the bottom languages
    section, not here."""
    return f"""    <nav class="topbar" aria-label="{e(t(locale, 'nav_primary_aria'))}">
        <div class="topbar-inner">
            <a href="{home_url_path(locale)}" class="topbar-brand" aria-label="{e(t(locale, 'topbar_brand_aria'))}">
                <img src="/assets/icon-256.png?v={ICON_VERSION}" alt="" width="24" height="24" decoding="async">
                <span>vultyr</span>
            </a>
            <div class="topbar-nav">
                <a href="{services_path(locale)}">{e(t(locale, 'nav_services'))}</a>
                <a href="{support_path(locale)}">{e(t(locale, 'nav_support'))}</a>
                <a href="{APP_STORE_URL}" target="_blank" rel="noopener noreferrer" class="topbar-cta">{e(t(locale, 'nav_download'))}</a>
            </div>
        </div>
    </nav>"""


def languages_section_html(locale, page_alt_urls):
    """Klosyt-style languages section: native-name links to every locale's
    version of this page. Used near the bottom of the home page (and any
    other page where it makes sense). page_alt_urls maps locale -> path."""
    items = []
    for loc in LOCALES:
        href = page_alt_urls.get(loc, home_url_path(loc))
        native = LOCALE_NATIVE_NAMES[loc]
        active = ' aria-current="page"' if loc == locale else ""
        items.append(
            f'                <li><a href="{href}" lang="{loc}" data-locale="{loc}"{active}>{e(native)}</a></li>'
        )
    items_html = "\n".join(items)
    heading = e(t(locale, "home_languages_heading"))
    return f"""    <section class="languages-section" aria-labelledby="lang-heading">
        <h2 id="lang-heading" class="lang-heading">{heading}</h2>
        <nav aria-labelledby="lang-heading">
            <ul class="lang-row" role="list">
{items_html}
            </ul>
        </nav>
    </section>"""


def footer_html(locale):
    return f"""    <footer>
        <nav aria-label="{e(t(locale, 'footer_nav_aria'))}">
            <a href="{home_url_path(locale)}">{e(t(locale, 'footer_home'))}</a>
            <a href="{services_path(locale)}">{e(t(locale, 'footer_services'))}</a>
            <a href="{privacy_path(locale)}">{e(t(locale, 'footer_privacy'))}</a>
            <a href="{support_path(locale)}">{e(t(locale, 'footer_support'))}</a>
            <a href="mailto:support@vultyr.app">{e(t(locale, 'footer_contact'))}</a>
        </nav>
        <p class="copyright">{e(t(locale, 'copyright'))}</p>
    </footer>"""


def json_ld_block(obj):
    """Return a JSON-LD block and matching CSP hash."""
    body = json.dumps(obj, indent=2, ensure_ascii=False).replace("</", "<\\/")
    content = f"\n{body}\n"
    return f'    <script type="application/ld+json">{content}</script>', csp_hash(content)


def load_data():
    """Load and validate services data. Fails fast on schema problems."""
    try:
        with open(JSON_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Error loading {JSON_PATH}: {exc}")
        raise SystemExit(1)

    errors = []
    services = data.get("services")
    categories = data.get("categories")
    if not isinstance(services, list):
        errors.append("'services' must be a list")
    if not isinstance(categories, list):
        errors.append("'categories' must be a list")
    if errors:
        _schema_fail(errors)

    required_svc = ("name", "slug", "faviconDomain", "statusUrl", "homepageUrl", "categories")
    seen_slugs = set()
    for i, svc in enumerate(services):
        if not isinstance(svc, dict):
            errors.append(f"services[{i}] is not an object")
            continue
        for key in required_svc:
            if not svc.get(key):
                errors.append(f"services[{i}] ({svc.get('slug', '?')}) missing required field {key!r}")
        slug = svc.get("slug")
        if slug and slug in seen_slugs:
            errors.append(f"duplicate service slug: {slug!r}")
        elif slug:
            seen_slugs.add(slug)

    required_cat = ("name", "slug", "serviceSlugs")
    seen_cat_slugs = set()
    for i, cat in enumerate(categories):
        if not isinstance(cat, dict):
            errors.append(f"categories[{i}] is not an object")
            continue
        for key in required_cat:
            if cat.get(key) is None:
                errors.append(f"categories[{i}] ({cat.get('slug', '?')}) missing required field {key!r}")
        cslug = cat.get("slug")
        if cslug and cslug in seen_cat_slugs:
            errors.append(f"duplicate category slug: {cslug!r}")
        elif cslug:
            seen_cat_slugs.add(cslug)
        for ss in cat.get("serviceSlugs", []) or []:
            if ss not in seen_slugs:
                errors.append(f"category {cslug!r} references unknown service slug {ss!r}")

    if errors:
        _schema_fail(errors)
    return data


def _schema_fail(errors):
    print(f"Schema validation failed for {JSON_PATH}:")
    for err in errors:
        print(f"  - {err}")
    raise SystemExit(1)


def write_file(path, content):
    """Write content to a file as UTF-8."""
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(content, encoding="utf-8")
    except OSError as exc:
        print(f"Error writing {path}: {exc}")
        raise SystemExit(1)


def prune_generated_dir(directory, expected_names):
    """Remove generated HTML files that no longer exist in the source data."""
    removed = []
    if not directory.is_dir():
        return removed
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
    back to an inline SVG data URL placeholder if no local PNG exists."""
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

def generate_services_page(data, favicon, locale):
    services_by_slug = {s["slug"]: s for s in data["services"]}
    categories = data["categories"]
    total = len(data["services"])

    title = t(locale, "svcs_title")
    description = t(locale, "svcs_description")

    alt_urls = {loc: services_path(loc) for loc in LOCALES}

    cat_pills = "\n".join(
        f'        <a class="cat-pill" href="{category_path(locale, cat["slug"])}">'
        f'{e(category_display_name(cat, locale))} <span>{len(cat["serviceSlugs"])}</span></a>'
        for cat in categories
    )

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
                f'                <div class="service-name"><a href="{service_path(locale, svc["slug"])}">{e(svc["name"])}</a></div>\n'
                f'                <div class="service-links">\n'
                f'                    <a href="{status_href}" target="_blank" rel="noopener noreferrer">{e(t(locale, "svc_row_status"))}</a>\n'
                f'                    <a href="{home_href}" target="_blank" rel="noopener noreferrer">{e(t(locale, "svc_row_homepage"))}</a>\n'
                f'                </div>\n'
                f'            </div>'
            )
        rows_html = "\n".join(rows)
        sections.append(
            f'        <div class="category">\n'
            f'            <h2><a href="{category_path(locale, cat["slug"])}">{e(category_display_name(cat, locale))}</a>'
            f'<span class="count">{len(cat["serviceSlugs"])}</span></h2>\n'
            f'{rows_html}\n'
            f'        </div>'
        )
    sections_html = "\n\n".join(sections)

    item_list_ld = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": t(locale, "svcs_item_list_name"),
        "numberOfItems": total,
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": svc["name"],
                "url": absolute(service_path(locale, svc["slug"])),
            }
            for i, svc in enumerate(data["services"])
        ],
    }

    item_list_ld_html, item_list_ld_hash = json_ld_block(item_list_ld)
    canonical = absolute(services_path(locale))

    return f"""<!DOCTYPE html>
<html lang="{html_lang(locale)}">
<head>
{head_common(script_hashes=(item_list_ld_hash,))}
    <title>{e(title)}</title>
    <meta name="description" content="{e(description)}">
    <meta name="theme-color" content="#000000">
    <meta property="og:title" content="{e(title)}">
    <meta property="og:description" content="{e(description)}">
    <meta property="og:image" content="{OG_IMAGE}">
    <meta property="og:image:alt" content="{e(t(locale, 'og_image_alt'))}">
    <meta property="og:url" content="{canonical}">
    <meta property="og:type" content="website">
    <meta property="og:locale" content="{og_locale(locale)}">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{e(title)}">
    <meta name="twitter:description" content="{e(description)}">
    <meta name="twitter:image" content="{OG_IMAGE}">
    <link rel="canonical" href="{canonical}">
{hreflang_links(alt_urls)}
    <link rel="apple-touch-icon" href="/icon.png">
    <link rel="icon" type="image/png" sizes="64x64" href="{FAVICON_HREF}">
    <link rel="stylesheet" href="/assets/css/shared.css?v={ASSET_VERSION}">
    <link rel="stylesheet" href="/assets/css/services-list.css?v={ASSET_VERSION}">
{item_list_ld_html}
{GA_SNIPPET}
</head>
<body>
    <a href="#main" class="sr-only">{e(t(locale, 'skip_to_main'))}</a>
{topbar_html(locale)}
    <main id="main">
    <div class="header">
        <h1>{e(t(locale, 'svcs_h1_lead'))} <span class="highlight-orange">{e(t(locale, 'svcs_h1_highlight'))}</span></h1>
        <p class="subtitle">{e(t(locale, 'svcs_subtitle'))}</p>
    </div>

    <nav class="content categories-nav" aria-label="{e(t(locale, 'svcs_categories_aria'))}">
{cat_pills}
    </nav>

    <div class="content">
        <div class="sections">
{sections_html}
        </div>
    </div>
    </main>

{footer_html(locale)}
</body>
</html>
"""


# ─── SERVICE PAGE ──────────────────────────────────────────────────────────────

def generate_service_page(svc, categories_lookup, all_services_by_slug, favicon, locale):
    name = svc["name"]
    slug = svc["slug"]
    favicon_domain = svc["faviconDomain"]
    status_url = svc["statusUrl"]
    homepage_url = svc["homepageUrl"]
    cat_slugs = svc["categories"] or []

    if not cat_slugs:
        print(f"Error: service {slug!r} has no categories")
        raise SystemExit(1)

    primary_cat = categories_lookup.get(cat_slugs[0], {"name": cat_slugs[0], "slug": cat_slugs[0], "serviceSlugs": []})
    primary_cat_name = category_display_name(primary_cat, locale)

    related = []
    for rs in primary_cat.get("serviceSlugs", []):
        if rs != slug and rs in all_services_by_slug:
            related.append(all_services_by_slug[rs])
            if len(related) >= 6:
                break

    devices = t(locale, "devices")
    alt_urls = {loc: service_path(loc, slug) for loc in LOCALES}

    breadcrumb_ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": t(locale, "breadcrumb_vultyr"), "item": absolute(home_url_path(locale))},
            {"@type": "ListItem", "position": 2, "name": t(locale, "breadcrumb_services"), "item": absolute(services_path(locale))},
            {"@type": "ListItem", "position": 3, "name": primary_cat_name,
             "item": absolute(category_path(locale, primary_cat["slug"]))},
            {"@type": "ListItem", "position": 4, "name": name},
        ],
    }

    faq_ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": t(locale, "svcp_faq_q1_fmt").format(name=name),
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": t(locale, "svcp_faq_a1_ld_fmt").format(name=name, url=status_url),
                },
            },
            {
                "@type": "Question",
                "name": t(locale, "svcp_faq_q2_fmt").format(name=name),
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": t(locale, "svcp_faq_a2_ld_fmt").format(name=name, devices=devices),
                },
            },
        ],
    }

    breadcrumb_html = f'''        <nav class="breadcrumb" aria-label="{e(t(locale, 'breadcrumb_aria'))}">
            <a href="{home_url_path(locale)}">{e(t(locale, 'breadcrumb_vultyr'))}</a><span class="sep" aria-hidden="true">&rsaquo;</span>
            <a href="{services_path(locale)}">{e(t(locale, 'breadcrumb_services'))}</a><span class="sep" aria-hidden="true">&rsaquo;</span>
            <a href="{category_path(locale, primary_cat["slug"])}">{e(primary_cat_name)}</a><span class="sep" aria-hidden="true">&rsaquo;</span>
            <span class="breadcrumb-current" aria-current="page">{e(name)}</span>
        </nav>'''

    related_html = ""
    if related:
        cards = ""
        for rs in related:
            cards += (
                f'                <a class="related-card" href="{service_path(locale, rs["slug"])}">\n'
                f'                    <img src="{favicon(rs["faviconDomain"], 32)}" alt="" width="20" height="20" loading="lazy" decoding="async" aria-hidden="true">\n'
                f'                    {e(rs["name"])}\n'
                f'                </a>\n'
            )
        related_html = (
            f'        <h2 class="section-title">{e(t(locale, "svcp_related_heading"))}</h2>\n'
            f'        <nav class="related-grid" aria-label="{e(t(locale, "svcp_related_aria"))}">\n'
            f'{cards}        </nav>'
        )

    cat_links_html = ""
    if len(cat_slugs) > 1:
        links = ", ".join(
            f'<a href="{category_path(locale, cs)}" class="highlight-orange">'
            f'{e(category_display_name(categories_lookup.get(cs, {"slug": cs, "name": cs}), locale))}</a>'
            for cs in cat_slugs
        )
        cat_links_html = f'        <p class="category-note">{e(t(locale, "svcp_categories_label"))} {links}</p>'

    title = t(locale, "svcp_title_fmt").format(name=name)
    description = t(locale, "svcp_description_fmt").format(name=name, devices=devices)

    status_href = safe_url(status_url)
    home_href = safe_url(homepage_url)
    breadcrumb_ld_html, breadcrumb_ld_hash = json_ld_block(breadcrumb_ld)
    faq_ld_html, faq_ld_hash = json_ld_block(faq_ld)
    canonical = absolute(service_path(locale, slug))

    faq_q1 = t(locale, "svcp_faq_q1_fmt").format(name=e(name))
    faq_a1 = t(locale, "svcp_faq_a1_fmt").format(name=e(name))
    faq_q2 = t(locale, "svcp_faq_q2_fmt").format(name=e(name))
    faq_a2 = t(locale, "svcp_faq_a2_fmt").format(name=e(name), devices=devices)
    alert_prefix = t(locale, "svcp_alert_hint_prefix")
    alert_link_text = t(locale, "svcp_alert_hint_link")

    return f"""<!DOCTYPE html>
<html lang="{html_lang(locale)}">
<head>
{head_common(script_hashes=(breadcrumb_ld_hash, faq_ld_hash))}
    <title>{e(title)}</title>
    <meta name="description" content="{e(description)}">
    <meta name="theme-color" content="#000000">
    <meta property="og:title" content="{e(title)}">
    <meta property="og:description" content="{e(description)}">
    <meta property="og:image" content="{OG_IMAGE}">
    <meta property="og:image:alt" content="{e(t(locale, 'og_image_alt'))}">
    <meta property="og:url" content="{canonical}">
    <meta property="og:type" content="website">
    <meta property="og:locale" content="{og_locale(locale)}">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{e(title)}">
    <meta name="twitter:description" content="{e(description)}">
    <meta name="twitter:image" content="{OG_IMAGE}">
    <link rel="canonical" href="{canonical}">
{hreflang_links(alt_urls)}
    <link rel="apple-touch-icon" href="/icon.png">
    <link rel="icon" type="image/png" sizes="64x64" href="{FAVICON_HREF}">
    <link rel="stylesheet" href="/assets/css/shared.css?v={ASSET_VERSION}">
    <link rel="stylesheet" href="/assets/css/service.css?v={ASSET_VERSION}">
{breadcrumb_ld_html}
{faq_ld_html}
{GA_SNIPPET}
</head>
<body>
    <a href="#main" class="sr-only">{e(t(locale, 'skip_to_main'))}</a>
{topbar_html(locale)}
    <main id="main">
    <div class="container">
{breadcrumb_html}
        <div class="service-header">
            <img src="{favicon(favicon_domain, 64)}" alt="" width="48" height="48" decoding="async" aria-hidden="true">
            <h1>{e(name)}</h1>
        </div>

        <div class="status-card">
            <div class="status-live" aria-hidden="true">
                <span class="pulse-dot"></span>
                {e(t(locale, 'svcp_live_check'))}
            </div>
            <a href="{status_href}" target="_blank" rel="noopener noreferrer" class="status-badge">
                <span class="status-text">{e(t(locale, 'svcp_view_current_status'))}</span>
            </a>
            <p class="status-time">{e(alert_prefix)}<a href="{APP_STORE_URL}">{e(alert_link_text)}</a></p>
        </div>
{cat_links_html}
        <div class="links-row">
            <a href="{status_href}" target="_blank" rel="noopener noreferrer">
                <img src="/assets/icons/chart-bar-regular.svg" alt="" width="16" height="16" aria-hidden="true">
                {e(t(locale, 'svcp_official_status'))}
            </a>
            <a href="{home_href}" target="_blank" rel="noopener noreferrer">
                <img src="/assets/icons/globe-regular.svg" alt="" width="16" height="16" aria-hidden="true">
                {e(t(locale, 'svcp_homepage_fmt').format(name=name))}
            </a>
        </div>

        <h2 class="section-title">{e(t(locale, 'svcp_faq_heading'))}</h2>
        <div class="faq">
            <h3>{faq_q1}</h3>
            <p>{faq_a1}</p>
        </div>
        <div class="faq">
            <h3>{faq_q2}</h3>
            <p>{faq_a2}</p>
        </div>

{related_html}
        <div class="cta">
            <h2>{e(t(locale, 'svcp_cta_heading_fmt').format(name=name))}</h2>
            <p>{e(t(locale, 'svcp_cta_body_fmt').format(name=name))}</p>
            <a href="{APP_STORE_URL}" aria-label="{e(t(locale, 'cta_download_vultyr_aria'))}">{e(t(locale, 'cta_download_vultyr'))}</a>
        </div>
    </div>
    </main>
{footer_html(locale)}
</body>
</html>
"""


# ─── CATEGORY PAGE ─────────────────────────────────────────────────────────────

def generate_category_page(cat, all_services_by_slug, all_categories, favicon, locale):
    slug = cat["slug"]
    name = category_display_name(cat, locale)
    icon = cat.get("icon", "")
    service_slugs = cat["serviceSlugs"]
    count = len(service_slugs)
    count_services = count_services_phrase(locale, count)

    alt_urls = {loc: category_path(loc, slug) for loc in LOCALES}

    cards = ""
    for ss in service_slugs:
        svc = all_services_by_slug.get(ss)
        if not svc:
            continue
        cards += (
            f'            <a class="service-card" href="{service_path(locale, svc["slug"])}">\n'
            f'                <img src="{favicon(svc["faviconDomain"], 32)}" alt="" width="24" height="24" loading="lazy" decoding="async" aria-hidden="true">\n'
            f'                <span>{e(svc["name"])}</span>\n'
            f'            </a>\n'
        )

    other_cats = ""
    for oc in all_categories:
        if oc["slug"] != slug:
            other_cats += (
                f'                <a class="cat-link" href="{category_path(locale, oc["slug"])}">'
                f'{e(category_display_name(oc, locale))}</a>\n'
            )

    icon_html = ""
    if icon:
        icon_path = ICONS_DIR / icon
        if icon_path.exists():
            try:
                svg = icon_path.read_text(encoding="utf-8")
                svg = svg.replace(
                    "<svg",
                    '<svg class="cat-icon" width="36" height="36" aria-hidden="true" focusable="false"',
                    1,
                )
                icon_html = svg
            except OSError as exc:
                print(f"Warning: could not read icon {icon_path}: {exc}")

    breadcrumb_ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": t(locale, "breadcrumb_vultyr"), "item": absolute(home_url_path(locale))},
            {"@type": "ListItem", "position": 2, "name": t(locale, "breadcrumb_services"), "item": absolute(services_path(locale))},
            {"@type": "ListItem", "position": 3, "name": name},
        ],
    }

    item_list_ld = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": t(locale, "catp_item_list_name_fmt").format(name=name),
        "numberOfItems": count,
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": all_services_by_slug[ss]["name"],
                "url": absolute(service_path(locale, all_services_by_slug[ss]["slug"])),
            }
            for i, ss in enumerate(service_slugs)
            if ss in all_services_by_slug
        ],
    }

    title = t(locale, "catp_title_fmt").format(name=name, count_services=count_services)
    sample_names = ", ".join(
        all_services_by_slug[s]["name"]
        for s in service_slugs[:4]
        if s in all_services_by_slug
    )
    description = t(locale, "catp_description_fmt").format(
        count_services=count_services,
        name_lower=name.lower(),
        sample=sample_names,
    )

    breadcrumb_ld_html, breadcrumb_ld_hash = json_ld_block(breadcrumb_ld)
    item_list_ld_html, item_list_ld_hash = json_ld_block(item_list_ld)
    canonical = absolute(category_path(locale, slug))

    return f"""<!DOCTYPE html>
<html lang="{html_lang(locale)}">
<head>
{head_common(script_hashes=(breadcrumb_ld_hash, item_list_ld_hash))}
    <title>{e(title)}</title>
    <meta name="description" content="{e(description)}">
    <meta name="theme-color" content="#000000">
    <meta property="og:title" content="{e(title)}">
    <meta property="og:description" content="{e(description)}">
    <meta property="og:image" content="{OG_IMAGE}">
    <meta property="og:image:alt" content="{e(t(locale, 'og_image_alt'))}">
    <meta property="og:url" content="{canonical}">
    <meta property="og:type" content="website">
    <meta property="og:locale" content="{og_locale(locale)}">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{e(title)}">
    <meta name="twitter:description" content="{e(description)}">
    <meta name="twitter:image" content="{OG_IMAGE}">
    <link rel="canonical" href="{canonical}">
{hreflang_links(alt_urls)}
    <link rel="apple-touch-icon" href="/icon.png">
    <link rel="icon" type="image/png" sizes="64x64" href="{FAVICON_HREF}">
    <link rel="stylesheet" href="/assets/css/shared.css?v={ASSET_VERSION}">
    <link rel="stylesheet" href="/assets/css/category.css?v={ASSET_VERSION}">
{breadcrumb_ld_html}
{item_list_ld_html}
{GA_SNIPPET}
</head>
<body>
    <a href="#main" class="sr-only">{e(t(locale, 'skip_to_main'))}</a>
{topbar_html(locale)}
    <main id="main">
    <div class="container">
        <nav class="breadcrumb" aria-label="{e(t(locale, 'breadcrumb_aria'))}">
            <a href="{home_url_path(locale)}">{e(t(locale, 'breadcrumb_vultyr'))}</a><span class="sep" aria-hidden="true">&rsaquo;</span>
            <a href="{services_path(locale)}">{e(t(locale, 'breadcrumb_services'))}</a><span class="sep" aria-hidden="true">&rsaquo;</span>
            <span class="breadcrumb-current" aria-current="page">{e(name)}</span>
        </nav>

        <div class="cat-header">
            <div class="cat-icon-box">{icon_html}</div>
            <h1>{e(name)}</h1>
        </div>
        <p class="cat-subtitle"><span class="pulse-dot" aria-hidden="true"></span>{e(t(locale, 'catp_subtitle_fmt').format(count_services=count_services))}</p>

        <nav class="services-grid" aria-label="{e(t(locale, 'catp_services_aria_fmt').format(name=name))}">
{cards}        </nav>

        <nav class="other-categories" aria-labelledby="other-cats-heading">
            <h2 id="other-cats-heading">{e(t(locale, 'catp_other_heading'))}</h2>
            <div class="cat-links">
{other_cats}            </div>
        </nav>

        <div class="cta">
            <h2>{e(t(locale, 'catp_cta_heading_fmt').format(count_services=count_services))}</h2>
            <p>{e(t(locale, 'catp_cta_body'))}</p>
            <a href="{APP_STORE_URL}" aria-label="{e(t(locale, 'cta_download_vultyr_aria'))}">{e(t(locale, 'cta_download_vultyr'))}</a>
        </div>
    </div>
    </main>
{footer_html(locale)}
</body>
</html>
"""


# ─── HOME PAGE ─────────────────────────────────────────────────────────────────

PLATFORM_BADGES = ["iPhone", "iPad", "Mac", "Apple TV", "Apple Watch", "Vision Pro"]


def generate_home_page(data, locale):
    title = t(locale, "home_title")
    description = t(locale, "home_description")
    og_title = t(locale, "home_og_title")
    alt_urls = {loc: home_url_path(loc) for loc in LOCALES}

    app_ld = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "Vultyr",
        "alternateName": "vultyr",
        "applicationCategory": "UtilitiesApplication",
        "operatingSystem": ["iOS", "iPadOS", "macOS", "tvOS", "watchOS", "visionOS"],
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "description": t(locale, "home_app_ld_description"),
        "url": absolute(home_url_path(locale)),
        "downloadUrl": APP_STORE_URL,
        "screenshot": [
            f"{SITE_ORIGIN}/assets/dash.webp",
            f"{SITE_ORIGIN}/assets/settings.webp",
            f"{SITE_ORIGIN}/assets/services.webp",
        ],
        "author": {"@type": "Organization", "name": "Vultyr", "url": f"{SITE_ORIGIN}/"},
        "publisher": {"@type": "Organization", "name": "Vultyr", "url": f"{SITE_ORIGIN}/"},
    }

    org_ld = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Vultyr",
        "url": f"{SITE_ORIGIN}/",
        "logo": f"{SITE_ORIGIN}/icon.png",
        "sameAs": [APP_STORE_URL],
        "contactPoint": {
            "@type": "ContactPoint",
            "email": "support@vultyr.app",
            "contactType": "customer support",
        },
    }

    app_ld_html, app_ld_hash = json_ld_block(app_ld)
    org_ld_html, org_ld_hash = json_ld_block(org_ld)

    category_count = len(data["categories"])

    # Polish: a few flagship features span two grid columns to break the
    # "all cards same size" rhythm. Every card also gets its own unique
    # icon color so the grid reads as a varied palette, not a wall of
    # one accent. Colors stay bright/saturated to fit the dark+phosphor
    # aesthetic; chosen so adjacent cards in the grid don't collide.
    # Per-card color comes from a data-icon attribute; the actual --icon-color
    # and --icon-svg custom properties are set by matching CSS rules in
    # home.css. Keeps the page CSP-clean (no inline style="" attributes).
    flagship_icons = {"chart-bar-regular.svg", "cloud-check-regular.svg",
                      "monitor-regular.svg"}

    def render_feature_card(icon, name, body):
        card_classes = "feature-card"
        if icon in flagship_icons:
            card_classes += " feature-card-wide"
        return (
            f'            <div class="{card_classes}" data-icon="{icon}">\n'
            f'                <div class="feature-icon" aria-hidden="true"></div>\n'
            f'                <div>\n'
            f'                    <h3>{e(name)}</h3>\n'
            f'                    <p>{e(body)}</p>\n'
            f'                </div>\n'
            f'            </div>'
        )

    feature_cards = "\n".join(
        render_feature_card(icon, name, body)
        for icon, name, body in t(locale, "home_features")
    )

    def section_marker(label):
        return (
            f'    <div class="section-marker" aria-hidden="true">'
            f'<span class="marker-tag">[ §{label} ]</span></div>'
        )

    platforms_html = " &middot; ".join(f"<span>{e(p)}</span>" for p in PLATFORM_BADGES)
    canonical = absolute(home_url_path(locale))

    return f"""<!DOCTYPE html>
<html lang="{html_lang(locale)}">
<head>
{head_common(script_hashes=(app_ld_hash, org_ld_hash))}
    <title>{e(title)}</title>
    <meta name="description" content="{e(description)}">
    <meta name="theme-color" content="#000000">
    <meta property="og:title" content="{e(og_title)}">
    <meta property="og:description" content="{e(description)}">
    <meta property="og:image" content="{OG_IMAGE}">
    <meta property="og:image:alt" content="{e(t(locale, 'og_image_alt'))}">
    <meta property="og:url" content="{canonical}">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="Vultyr">
    <meta property="og:locale" content="{og_locale(locale)}">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{e(og_title)}">
    <meta name="twitter:description" content="{e(description)}">
    <meta name="twitter:image" content="{OG_IMAGE}">
    <link rel="canonical" href="{canonical}">
{hreflang_links(alt_urls)}
    <link rel="apple-touch-icon" href="/icon.png">
    <link rel="icon" type="image/png" sizes="64x64" href="{FAVICON_HREF}">
    <link rel="stylesheet" href="/assets/css/shared.css?v={ASSET_VERSION}">
    <link rel="stylesheet" href="/assets/css/home.css?v={ASSET_VERSION}">
{app_ld_html}
{org_ld_html}
{GA_SNIPPET}
</head>
<body>
    <a href="#main" class="sr-only">{e(t(locale, 'skip_to_main'))}</a>
{topbar_html(locale)}

    <main id="main">
    <header class="hero">
        <div class="hero-inner">
            <div class="hero-tag fade-up fade-up-1" aria-hidden="true">{e(t(locale, 'home_hero_tag'))}</div>
            <img src="/assets/icon-256.png?v={ICON_VERSION}" alt="" class="icon" width="144" height="144" fetchpriority="high" decoding="async">
            <h1 class="fade-up fade-up-2">vultyr</h1>
            <p class="tagline fade-up fade-up-3">{e(t(locale, 'home_hero_question'))} <span class="highlight">{e(t(locale, 'home_hero_answer'))}</span></p>
            <p class="tagline-services fade-up fade-up-3">{t(locale, 'home_hero_services')}</p>
            <div class="cta-group fade-up fade-up-4">
                <a href="{APP_STORE_URL}" target="_blank" rel="noopener noreferrer" class="badge-link" aria-label="{e(t(locale, 'home_appstore_aria'))}">
                    <img src="/assets/app-store-badge.svg" alt="{e(t(locale, 'home_appstore_alt'))}" class="badge-img" width="180" height="54" decoding="async">
                </a>
                <p class="platforms">{e(t(locale, 'home_free_on_prefix'))} {platforms_html}</p>
            </div>
        </div>
    </header>

    <section class="screenshots fade-up fade-up-5" aria-labelledby="screenshots-heading">
        <h2 id="screenshots-heading" class="sr-only">{e(t(locale, 'home_screenshots_aria'))}</h2>
        <div class="screenshots-track">
            <div class="phone-frame">
                <img src="/assets/dash.webp" alt="{e(t(locale, 'home_screenshot_dash_alt'))}" width="390" height="844" decoding="async">
            </div>
            <div class="phone-frame">
                <img src="/assets/settings.webp" alt="{e(t(locale, 'home_screenshot_settings_alt_fmt').format(themes=THEMES_COUNT))}" width="390" height="844" decoding="async">
            </div>
            <div class="phone-frame">
                <img src="/assets/services.webp" alt="{e(t(locale, 'home_screenshot_services_alt_fmt').format(categories=category_count))}" width="390" height="844" decoding="async">
            </div>
        </div>
    </section>

{section_marker("01 stats")}

    <section class="stats" aria-labelledby="stats-heading">
        <h2 id="stats-heading" class="sr-only">{e(t(locale, 'home_stats_aria'))}</h2>
        <div class="stats-strip">
            <div class="stat">
                <span class="stat-value">200+</span>
                <span class="stat-label">{e(t(locale, 'home_stats_checks'))}</span>
            </div>
            <div class="stat">
                <span class="stat-value">{category_count}</span>
                <span class="stat-label">{e(t(locale, 'home_stats_categories'))}</span>
            </div>
            <div class="stat">
                <span class="stat-value">6</span>
                <span class="stat-label">{e(t(locale, 'home_stats_platforms'))}</span>
            </div>
            <div class="stat">
                <span class="stat-value">{APP_LANGUAGE_COUNT}</span>
                <span class="stat-label">{e(t(locale, 'home_stats_languages'))}</span>
            </div>
        </div>
    </section>

{section_marker("02 features")}

    <section class="features" aria-labelledby="features-heading">
        <div class="features-heading">
            <h2 id="features-heading">{e(t(locale, 'home_features_heading'))}</h2>
            <p>{e(t(locale, 'home_features_sub'))}</p>
        </div>
        <div class="features-grid">
{feature_cards}
        </div>
    </section>

{section_marker("03 install")}

    <section class="bottom-cta" aria-labelledby="bottom-cta-heading">
        <h2 id="bottom-cta-heading">{e(t(locale, 'home_bottom_heading'))}</h2>
        <p>{e(t(locale, 'home_bottom_sub'))}</p>
        <a href="{APP_STORE_URL}" target="_blank" rel="noopener noreferrer" class="cta-button" aria-label="{e(t(locale, 'home_bottom_aria'))}">
            <img src="/assets/icons/download-simple-regular.svg" alt="" width="18" height="18" aria-hidden="true">
            {e(t(locale, 'home_bottom_button'))}
        </a>
    </section>

{section_marker("04 i18n")}

{languages_section_html(locale, alt_urls)}
    </main>

{footer_html(locale)}
</body>
</html>
"""


# ─── REDIRECT STUB ─────────────────────────────────────────────────────────────

def generate_redirect_stub(old_slug, new_slug, locale, services_by_slug):
    """Static-hosting-friendly redirect from a renamed status page to its new
    URL. Uses <meta http-equiv="refresh"> (GitHub Pages can't issue 301s),
    <link rel="canonical"> so search engines consolidate ranking onto the new
    URL, and <meta name="robots" content="noindex"> so the stub itself drops
    from the index."""
    svc = services_by_slug[new_slug]
    target = service_path(locale, new_slug)
    absolute_target = absolute(target)
    name = svc["name"]
    # Split the localized "{name}" phrase around the placeholder so the service
    # name stays a real anchor (good for screen readers + non-JS fallback).
    message = t(locale, "redirect_moved_fmt").format(name="{{NAME}}")
    before, _, after = message.partition("{{NAME}}")
    body_html = f"{e(before)}<a href=\"{target}\">{e(name)}</a>{e(after)}"
    # Minimal head — no CSS or favicons — but keep the CSP meta so the generator's
    # validator passes, and include <html lang> + closing tags for the same reason.
    return f"""<!DOCTYPE html>
<html lang="{html_lang(locale)}">
<head>
    <meta charset="utf-8">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'">
    <meta http-equiv="refresh" content="0; url={absolute_target}">
    <meta name="robots" content="noindex">
    <link rel="canonical" href="{absolute_target}">
    <title>{e(name)} — Vultyr</title>
    <style>body{{font-family:system-ui,sans-serif;padding:2rem;color:#ccc;background:#0a0a0a}}a{{color:#6af}}</style>
</head>
<body>
    <p>{body_html}</p>
</body>
</html>
"""


# ─── 404 PAGE ──────────────────────────────────────────────────────────────────

def generate_404(data, favicon, locale):
    popular = ["aws", "github", "cloudflare", "slack", "stripe", "discord", "openai", "anthropic"]
    services_by_slug = {s["slug"]: s for s in data["services"]}
    missing = [slug for slug in popular if slug not in services_by_slug]
    if missing:
        print(f"Error: 404 page references missing services: {missing}")
        raise SystemExit(1)

    alt_urls = {loc: home_url_path(loc) for loc in LOCALES}

    popular_links = []
    for slug in popular:
        svc = services_by_slug[slug]
        popular_links.append(
            f'            <a href="{service_path(locale, slug)}">'
            f'<img src="{favicon(svc["faviconDomain"], 32)}" alt="" width="20" height="20" loading="lazy" decoding="async" aria-hidden="true"> '
            f'{e(svc["name"])}</a>'
        )
    popular_html = "\n".join(popular_links)

    cat_links = "\n".join(
        f'            <a class="cat-link" href="{category_path(locale, c["slug"])}">{e(category_display_name(c, locale))}</a>'
        for c in data["categories"]
    )

    return f"""<!DOCTYPE html>
<html lang="{html_lang(locale)}">
<head>
{head_common()}
    <title>{e(t(locale, 'err_title'))}</title>
    <meta name="description" content="{e(t(locale, 'err_description'))}">
    <meta name="theme-color" content="#000000">
    <meta name="robots" content="noindex">
    <link rel="apple-touch-icon" href="/icon.png">
    <link rel="icon" type="image/png" sizes="64x64" href="{FAVICON_HREF}">
    <link rel="stylesheet" href="/assets/css/shared.css?v={ASSET_VERSION}">
    <link rel="stylesheet" href="/assets/css/404.css?v={ASSET_VERSION}">
{GA_SNIPPET}
</head>
<body>
    <a href="#main" class="sr-only">{e(t(locale, 'skip_to_main'))}</a>
{topbar_html(locale)}
    <main id="main" class="error-main">
        <p class="error-code" aria-hidden="true">404</p>
        <h1 class="error-title">{e(t(locale, 'err_heading'))}</h1>
        <p class="error-message">{e(t(locale, 'err_message'))}</p>

        <div class="error-section">
            <h2>{e(t(locale, 'err_popular_heading'))}</h2>
            <div class="popular">
{popular_html}
            </div>
        </div>

        <div class="error-section">
            <h2>{e(t(locale, 'err_browse_heading'))}</h2>
            <div class="cat-links">
{cat_links}
            </div>
        </div>
    </main>
{footer_html(locale)}
</body>
</html>
"""


# ─── PRIVACY / SUPPORT PAGES ───────────────────────────────────────────────────

def _docs_page(locale, page_key, alt_urls, title, description, body_html, extra_head=""):
    """Shared shell for the privacy and support docs pages."""
    canonical = absolute(alt_urls[locale])
    return f"""<!DOCTYPE html>
<html lang="{html_lang(locale)}">
<head>
{head_common()}
{extra_head}    <title>{e(title)}</title>
    <meta name="description" content="{e(description)}">
    <meta name="theme-color" content="#000000">
    <meta property="og:title" content="{e(title)}">
    <meta property="og:description" content="{e(description)}">
    <meta property="og:image" content="{OG_IMAGE}">
    <meta property="og:image:alt" content="{e(t(locale, 'og_image_alt'))}">
    <meta property="og:url" content="{canonical}">
    <meta property="og:type" content="website">
    <meta property="og:locale" content="{og_locale(locale)}">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{e(title)}">
    <meta name="twitter:description" content="{e(description)}">
    <meta name="twitter:image" content="{OG_IMAGE}">
    <link rel="canonical" href="{canonical}">
{hreflang_links(alt_urls)}
    <link rel="apple-touch-icon" href="/icon.png">
    <link rel="icon" type="image/png" sizes="64x64" href="{FAVICON_HREF}">
    <link rel="stylesheet" href="/assets/css/shared.css?v={ASSET_VERSION}">
    <link rel="stylesheet" href="/assets/css/docs.css?v={ASSET_VERSION}">
{GA_SNIPPET}
</head>
<body>
    <a href="#main" class="sr-only">{e(t(locale, 'skip_to_main'))}</a>
{topbar_html(locale)}
    <main id="main" class="docs">
{body_html}
    </main>
{footer_html(locale)}
</body>
</html>
"""


def generate_privacy_page(locale):
    alt_urls = {loc: privacy_path(loc) for loc in LOCALES}
    title = t(locale, "privacy_title")
    description = t(locale, "privacy_description")
    sections = "".join(
        f"\n    <h2>{e(heading)}</h2>\n    {body}"
        for heading, body in t(locale, "privacy_sections")
    )
    body_html = (
        f'    <h1>{e(title)}</h1>\n'
        f'    <p class="date">{e(t(locale, "privacy_last_updated"))}</p>'
        f'{sections}\n'
    )
    return _docs_page(locale, "privacy", alt_urls, title, description, body_html)


def generate_support_page(locale):
    alt_urls = {loc: support_path(loc) for loc in LOCALES}
    title = t(locale, "support_title")
    description = t(locale, "support_description")
    faqs = t(locale, "support_faqs")

    faq_ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a_text},
            }
            for q, a_text, _ in faqs
        ],
    }
    faq_ld_html, faq_ld_hash = json_ld_block(faq_ld)
    extra_head = f"{faq_ld_html}\n"

    contact_html = t(locale, "support_contact_html")
    faq_blocks = "".join(
        f'\n    <div class="faq">\n        <h3>{e(q)}</h3>\n        {a_html}\n    </div>'
        for q, _, a_html in faqs
    )
    body_html = (
        f'    <h1>{e(title)}</h1>\n\n'
        f'    <h2>{e(t(locale, "support_contact_heading"))}</h2>\n'
        f'    {contact_html}\n\n'
        f'    <h2>{e(t(locale, "support_faq_heading"))}</h2>\n'
        f'{faq_blocks}\n'
    )

    canonical = absolute(alt_urls[locale])
    return f"""<!DOCTYPE html>
<html lang="{html_lang(locale)}">
<head>
{head_common(script_hashes=(faq_ld_hash,))}
    <title>{e(title)}</title>
    <meta name="description" content="{e(description)}">
    <meta name="theme-color" content="#000000">
    <meta property="og:title" content="{e(title)}">
    <meta property="og:description" content="{e(description)}">
    <meta property="og:image" content="{OG_IMAGE}">
    <meta property="og:image:alt" content="{e(t(locale, 'og_image_alt'))}">
    <meta property="og:url" content="{canonical}">
    <meta property="og:type" content="website">
    <meta property="og:locale" content="{og_locale(locale)}">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{e(title)}">
    <meta name="twitter:description" content="{e(description)}">
    <meta name="twitter:image" content="{OG_IMAGE}">
    <link rel="canonical" href="{canonical}">
{hreflang_links(alt_urls)}
    <link rel="apple-touch-icon" href="/icon.png">
    <link rel="icon" type="image/png" sizes="64x64" href="{FAVICON_HREF}">
    <link rel="stylesheet" href="/assets/css/shared.css?v={ASSET_VERSION}">
    <link rel="stylesheet" href="/assets/css/docs.css?v={ASSET_VERSION}">
{faq_ld_html}
{GA_SNIPPET}
</head>
<body>
    <a href="#main" class="sr-only">{e(t(locale, 'skip_to_main'))}</a>
{topbar_html(locale)}
    <main id="main" class="docs">
{body_html}
    </main>
{footer_html(locale)}
</body>
</html>
"""


# ─── SITEMAP ───────────────────────────────────────────────────────────────────

def generate_sitemap(services, categories):
    """Single sitemap covering both locales with <xhtml:link> alternates so
    search engines can discover the Russian translations."""
    def build_entries(locale):
        return [
            home_url_path(locale),
            services_path(locale),
            support_path(locale),
            privacy_path(locale),
            *[category_path(locale, c["slug"]) for c in categories],
            *[service_path(locale, s["slug"]) for s in services],
        ]

    en_entries = build_entries("en")
    ru_entries = build_entries("ru")
    # The two lists align index-for-index so the alternates match up.
    assert len(en_entries) == len(ru_entries), "locale sitemap entries out of sync"

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">',
    ]
    for en_path, ru_path in zip(en_entries, ru_entries):
        for primary, alt in ((en_path, ru_path), (ru_path, en_path)):
            lines.append("  <url>")
            lines.append(f"    <loc>{absolute(primary)}</loc>")
            lines.append(f"    <lastmod>{TODAY}</lastmod>")
            lines.append(f'    <xhtml:link rel="alternate" hreflang="en" href="{absolute(en_path)}" />')
            lines.append(f'    <xhtml:link rel="alternate" hreflang="ru" href="{absolute(ru_path)}" />')
            lines.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{absolute(en_path)}" />')
            lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


# ─── MAIN ──────────────────────────────────────────────────────────────────────

def validate_html(paths):
    """Light-weight sanity check: parses each generated HTML file and verifies
    basic well-formedness plus a few invariants."""
    from html.parser import HTMLParser

    class _Counter(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.errors = []

        def error(self, message):
            self.errors.append(message)

    failed = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        parser = _Counter()
        try:
            parser.feed(text)
            parser.close()
        except Exception as exc:
            failed.append((path, f"parse error: {exc}"))
            continue
        if parser.errors:
            failed.append((path, "; ".join(parser.errors)))
            continue
        if not any(f'<html lang="{loc}">' in text for loc in LOCALES):
            failed.append((path, "missing recognised <html lang> attribute"))
            continue
        if "</body>" not in text or "</html>" not in text:
            failed.append((path, "missing closing body/html tag"))
            continue
        if "Content-Security-Policy" not in text:
            failed.append((path, "missing CSP meta tag"))
            continue

    if failed:
        print("\nHTML validation failures:")
        for path, msg in failed:
            print(f"  {path.relative_to(ROOT_DIR)}: {msg}")
        raise SystemExit(1)


def main():
    data = load_data()
    services = data["services"]
    categories = data["categories"]

    services_by_slug = {s["slug"]: s for s in services}
    categories_by_slug = {c["slug"]: c for c in categories}
    favicon = build_favicon_lookup()

    written_paths = []
    total_services = len(services)

    for locale in LOCALES:
        prefix = locale_prefix(locale)
        status_dir = ROOT_DIR / prefix.lstrip("/") / "status" if prefix else STATUS_DIR
        categories_dir = ROOT_DIR / prefix.lstrip("/") / "categories" if prefix else CATEGORIES_DIR
        status_dir.mkdir(parents=True, exist_ok=True)
        categories_dir.mkdir(parents=True, exist_ok=True)

        print(f"[{locale}] Generating home page...")
        home_path = (ROOT_DIR / prefix.lstrip("/") / "index.html") if prefix else (ROOT_DIR / "index.html")
        write_file(home_path, generate_home_page(data, locale))
        written_paths.append(home_path)

        print(f"[{locale}] Generating services.html...")
        services_html_path = (ROOT_DIR / prefix.lstrip("/") / "services.html") if prefix else (ROOT_DIR / "services.html")
        write_file(services_html_path, generate_services_page(data, favicon, locale))
        written_paths.append(services_html_path)

        print(f"[{locale}] Generating {total_services} service pages...")
        for svc in services:
            path = status_dir / f"{svc['slug']}.html"
            html = generate_service_page(svc, categories_by_slug, services_by_slug, favicon, locale)
            write_file(path, html)
            written_paths.append(path)

        for old_slug, new_slug in SLUG_ALIASES.items():
            if new_slug not in services_by_slug:
                print(f"Error: SLUG_ALIASES points {old_slug!r} at missing service {new_slug!r}")
                raise SystemExit(1)
            path = status_dir / f"{old_slug}.html"
            write_file(path, generate_redirect_stub(old_slug, new_slug, locale, services_by_slug))
            written_paths.append(path)

        expected_status = {f"{svc['slug']}.html" for svc in services}
        expected_status |= {f"{old}.html" for old in SLUG_ALIASES}
        prune_generated_dir(status_dir, expected_status)

        print(f"[{locale}] Generating {len(categories)} category pages...")
        for cat in categories:
            path = categories_dir / f"{cat['slug']}.html"
            html = generate_category_page(cat, services_by_slug, categories, favicon, locale)
            write_file(path, html)
            written_paths.append(path)
        prune_generated_dir(categories_dir, {f"{cat['slug']}.html" for cat in categories})

        print(f"[{locale}] Generating 404.html...")
        path_404 = (ROOT_DIR / prefix.lstrip("/") / "404.html") if prefix else (ROOT_DIR / "404.html")
        write_file(path_404, generate_404(data, favicon, locale))
        written_paths.append(path_404)

        print(f"[{locale}] Generating privacy.html...")
        privacy_file = (ROOT_DIR / prefix.lstrip("/") / "privacy.html") if prefix else (ROOT_DIR / "privacy.html")
        write_file(privacy_file, generate_privacy_page(locale))
        written_paths.append(privacy_file)

        print(f"[{locale}] Generating support.html...")
        support_file = (ROOT_DIR / prefix.lstrip("/") / "support.html") if prefix else (ROOT_DIR / "support.html")
        write_file(support_file, generate_support_page(locale))
        written_paths.append(support_file)

    print("Generating sitemap.xml...")
    write_file(ROOT_DIR / "sitemap.xml", generate_sitemap(services, categories))

    print(f"Validating {len(written_paths)} HTML files...")
    validate_html(written_paths)

    print(f"\nDone! Generated {len(written_paths)} HTML files across {len(LOCALES)} locales.")

    if favicon.missing:
        print(f"\nWarning: {len(favicon.missing)} missing favicon(s), using placeholder:")
        for m in sorted(favicon.missing):
            print(f"  {m}")
        print("Run scripts/download_favicons.py to fetch them.")


if __name__ == "__main__":
    main()
