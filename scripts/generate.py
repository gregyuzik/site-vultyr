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
ASSET_VERSION = "20260417f"
# Bump when icon-256.png changes so CDN edges pick up the new asset.
ICON_VERSION = "20260417e"
OG_IMAGE = f"{SITE_ORIGIN}/icon.png"

THEMES_COUNT = 12
APP_LANGUAGE_COUNT = 17

LOCALES = (
    "en", "da", "de", "es", "fr", "it", "ja", "ko", "nb", "nl",
    "pt-BR", "ru", "sv", "tr", "vi", "zh-Hans", "zh-Hant",
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

# Short code shown on the closed topbar language dropdown.
LOCALE_SHORT_CODES = {
    "en": "EN", "da": "DA", "de": "DE", "es": "ES", "fr": "FR",
    "it": "IT", "ja": "JA", "ko": "KO", "nb": "NB", "nl": "NL",
    "pt-BR": "PT", "ru": "RU", "sv": "SV", "tr": "TR", "vi": "VI",
    "zh-Hans": "\u7b80", "zh-Hant": "\u7e41",
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
        "lang_switch_aria": "Language",
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
        "home_features_sub": "No app accounts, no servers, no in-app tracking. Just status.",
        "home_bottom_heading": "Ready to monitor your stack?",
        "home_bottom_sub": "Free. No app account required. Available everywhere.",
        "home_bottom_button": "Download Free",
        "home_bottom_aria": "Download Vultyr free on the App Store",
        "home_languages_heading": "Available in 17 languages",
        "home_features": [
            ("chart-bar-regular.svg", "Live Status Dashboard",
             "AWS, GitHub, Cloudflare, Slack, Stripe, Discord, OpenAI, Anthropic and 200+ more \u2014 all in one place."),
            ("bell-ringing-regular.svg", "Smart Alerts",
             "Down and recovery notifications with each service's favicon attached on iOS. Mute known incidents, star critical services."),
            ("microphone-regular.svg", "Siri & Shortcuts",
             "Ask Siri \u201cmute GitHub for 2 hours\u201d or \u201cshow current issues.\u201d App Intents for every action, plus a Focus Filter that quiets non-critical services."),
            ("squares-four-regular.svg", "Widgets & Live Activities",
             "Home Screen and Lock Screen widgets on iOS, plus a Control Center widget. Active outages pin to the Dynamic Island."),
            ("watch-regular.svg", "Watch Complications",
             "Pin a critical service to a watch face, or let Smart Stack surface active issues automatically."),
            ("cloud-check-regular.svg", "Cross-Device Sync",
             "Your Mac monitors continuously and pushes status changes to all your devices via iCloud. No setup needed."),
            ("devices-regular.svg", "Every Apple Platform",
             "iPhone, iPad, Mac menu bar, Apple TV, Apple Watch, and Vision Pro. Services sync across all devices."),
            ("lightning-regular.svg", "Incident Details",
             "Affected components, active incidents, scheduled maintenance, and timeline updates \u2014 localized into your language."),
            ("battery-charging-regular.svg", "Battery-Aware Polling",
             "Smart auto-refresh adapts to battery, power state, and thermals. Every minute on Mac, 5-15 on iPhone."),
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
             "When your Mac detects a status change, it writes a lightweight signal to iCloud Key-Value Store. Your other devices pick up the change and run their own local check. No keys, no tokens, no setup \u2014 just enable \"Cross-Device Alerts\" in settings on any device. Keep the Mac app running for real-time monitoring.",
             "<p>When your Mac detects a status change, it writes a lightweight signal to iCloud Key-Value Store. Your other devices pick up the change and run their own local check. No keys, no tokens, no setup \u2014 just enable \"Cross-Device Alerts\" in settings on any device. Keep the Mac app running for real-time monitoring.</p>"),
            ("Does vultyr work with Siri and Shortcuts?",
             "Yes. Built-in App Intents let you say \u201cHey Siri, mute GitHub for 2 hours,\u201d \u201ccheck Stripe status,\u201d or \u201cshow current issues,\u201d and you can wire those same actions into the Shortcuts app. There's also a Focus Filter so a \u201cvultyr Focus\u201d mode can quiet non-critical services automatically.",
             "<p>Yes. Built-in App Intents let you say \u201cHey Siri, mute GitHub for 2 hours,\u201d \u201ccheck Stripe status,\u201d or \u201cshow current issues,\u201d and you can wire those same actions into the Shortcuts app. There's also a Focus Filter so a \u201cvultyr Focus\u201d mode can quiet non-critical services automatically.</p>"),
            ("Are there widgets and Live Activities?",
             "On iOS, there are Home Screen and Lock Screen widgets (single-service and status summary) plus a Control Center widget. Active outages pin to the Dynamic Island as Live Activities. On watchOS, complications are available for all watch faces, with Smart Stack relevance so the right service surfaces when something is down.",
             "<p>On iOS, there are Home Screen and Lock Screen widgets (single-service and status summary) plus a Control Center widget. Active outages pin to the Dynamic Island as Live Activities. On watchOS, complications are available for all watch faces, with Smart Stack relevance so the right service surfaces when something is down.</p>"),
            ("Does the vultyr app collect my data?",
             "No. The app has no accounts, no servers, no in-app tracking, no in-app analytics. All your watched services stay on your device. Note: this website (vultyr.app) uses cookieless Google Analytics for aggregate visitor counts \u2014 see the Privacy Policy for details.",
             "<p>No. The app has no accounts, no servers, no in-app tracking, no in-app analytics. All your watched services stay on your device. Note: this website (vultyr.app) uses cookieless Google Analytics for aggregate visitor counts \u2014 see the <a href=\"/privacy.html\">Privacy Policy</a> for details.</p>"),
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
        "lang_switch_aria": "\u042f\u0437\u044b\u043a",
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
        "home_features_sub": "\u0411\u0435\u0437 \u0430\u043a\u043a\u0430\u0443\u043d\u0442\u043e\u0432, \u0431\u0435\u0437 \u0441\u0435\u0440\u0432\u0435\u0440\u043e\u0432, \u0431\u0435\u0437 \u0432\u0441\u0442\u0440\u043e\u0435\u043d\u043d\u043e\u0433\u043e \u0442\u0440\u0435\u043a\u0438\u043d\u0433\u0430. \u0422\u043e\u043b\u044c\u043a\u043e \u0441\u0442\u0430\u0442\u0443\u0441.",
        "home_bottom_heading": "\u0413\u043e\u0442\u043e\u0432\u044b \u043c\u043e\u043d\u0438\u0442\u043e\u0440\u0438\u0442\u044c \u0441\u0432\u043e\u0439 \u0441\u0442\u0435\u043a?",
        "home_bottom_sub": "\u0411\u0435\u0441\u043f\u043b\u0430\u0442\u043d\u043e. \u0411\u0435\u0437 \u0430\u043a\u043a\u0430\u0443\u043d\u0442\u0430. \u0412\u0435\u0437\u0434\u0435 \u0434\u043e\u0441\u0442\u0443\u043f\u043d\u043e.",
        "home_bottom_button": "\u0421\u043a\u0430\u0447\u0430\u0442\u044c \u0431\u0435\u0441\u043f\u043b\u0430\u0442\u043d\u043e",
        "home_bottom_aria": "\u0421\u043a\u0430\u0447\u0430\u0442\u044c Vultyr \u0431\u0435\u0441\u043f\u043b\u0430\u0442\u043d\u043e \u0432 App Store",
        "home_languages_heading": "\u0414\u043e\u0441\u0442\u0443\u043f\u043d\u043e \u043d\u0430 17 \u044f\u0437\u044b\u043a\u0430\u0445",
        "home_features": [
            ("chart-bar-regular.svg",
             "Дашборд статуса в реальном времени",
             "AWS, GitHub, Cloudflare, Slack, Stripe, Discord, OpenAI, Anthropic и 200+ других \u2014 всё в одном месте."),
            ("bell-ringing-regular.svg",
             "Умные уведомления",
             "Оповещения о падениях и восстановлениях \u2014 на iOS с фавиконом каждого сервиса. Отключайте известные инциденты, отмечайте важные сервисы."),
            ("microphone-regular.svg",
             "Siri и Команды",
             "Скажите Siri «отключи GitHub на 2 часа» или «покажи текущие проблемы». App Intents на каждое действие, плюс Focus Filter, который заглушает неважные сервисы."),
            ("squares-four-regular.svg",
             "Виджеты и Live Activities",
             "Виджеты на экране «Домой» и экране блокировки на iOS, плюс виджет в Пункте управления. Активные сбои закрепляются в Dynamic Island как Live Activities."),
            ("watch-regular.svg",
             "Осложнения на часах",
             "Закрепите важный сервис на циферблате или доверьте Smart Stack автоматически показывать активные проблемы."),
            ("cloud-check-regular.svg",
             "Синхронизация между устройствами",
             "Mac ведёт непрерывный мониторинг и передаёт изменения статуса на все устройства через iCloud. Настройка не нужна."),
            ("devices-regular.svg",
             "Все платформы Apple",
             "iPhone, iPad, строка меню Mac, Apple TV, Apple Watch и Vision Pro. Сервисы синхронизируются между устройствами."),
            ("lightning-regular.svg",
             "Детали инцидентов",
             "Затронутые компоненты, активные инциденты, плановые работы и обновления таймлайна \u2014 на вашем языке."),
            ("battery-charging-regular.svg",
             "Умный опрос с учётом батареи",
             "Автообновление адаптируется к заряду, питанию и температуре. Раз в минуту на Mac, 5\u201315 минут на iPhone."),
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
             "\u041a\u043e\u0433\u0434\u0430 Mac \u043e\u0431\u043d\u0430\u0440\u0443\u0436\u0438\u0432\u0430\u0435\u0442 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u0435 \u0441\u0442\u0430\u0442\u0443\u0441\u0430, \u043e\u043d \u0437\u0430\u043f\u0438\u0441\u044b\u0432\u0430\u0435\u0442 \u043b\u0451\u0433\u043a\u0438\u0439 \u0441\u0438\u0433\u043d\u0430\u043b \u0432 iCloud Key-Value Store. \u0414\u0440\u0443\u0433\u0438\u0435 \u0432\u0430\u0448\u0438 \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0430 \u043f\u043e\u0434\u0445\u0432\u0430\u0442\u044b\u0432\u0430\u044e\u0442 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u0435 \u0438 \u0432\u044b\u043f\u043e\u043b\u043d\u044f\u044e\u0442 \u0441\u0432\u043e\u044e \u043b\u043e\u043a\u0430\u043b\u044c\u043d\u0443\u044e \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0443. \u041d\u0438\u043a\u0430\u043a\u0438\u0445 \u043a\u043b\u044e\u0447\u0435\u0439, \u0442\u043e\u043a\u0435\u043d\u043e\u0432 \u0438 \u043d\u0430\u0441\u0442\u0440\u043e\u0435\u043a \u2014 \u043f\u0440\u043e\u0441\u0442\u043e \u0432\u043a\u043b\u044e\u0447\u0438\u0442\u0435 \u00ab\u0423\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u044f \u043c\u0435\u0436\u0434\u0443 \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0430\u043c\u0438\u00bb \u0432 \u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430\u0445 \u043d\u0430 \u043b\u044e\u0431\u043e\u043c \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0435. \u0414\u0435\u0440\u0436\u0438\u0442\u0435 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 Mac \u0437\u0430\u043f\u0443\u0449\u0435\u043d\u043d\u044b\u043c \u0434\u043b\u044f \u043c\u043e\u043d\u0438\u0442\u043e\u0440\u0438\u043d\u0433\u0430 \u0432 \u0440\u0435\u0430\u043b\u044c\u043d\u043e\u043c \u0432\u0440\u0435\u043c\u0435\u043d\u0438.",
             "<p>\u041a\u043e\u0433\u0434\u0430 Mac \u043e\u0431\u043d\u0430\u0440\u0443\u0436\u0438\u0432\u0430\u0435\u0442 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u0435 \u0441\u0442\u0430\u0442\u0443\u0441\u0430, \u043e\u043d \u0437\u0430\u043f\u0438\u0441\u044b\u0432\u0430\u0435\u0442 \u043b\u0451\u0433\u043a\u0438\u0439 \u0441\u0438\u0433\u043d\u0430\u043b \u0432 iCloud Key-Value Store. \u0414\u0440\u0443\u0433\u0438\u0435 \u0432\u0430\u0448\u0438 \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0430 \u043f\u043e\u0434\u0445\u0432\u0430\u0442\u044b\u0432\u0430\u044e\u0442 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u0435 \u0438 \u0432\u044b\u043f\u043e\u043b\u043d\u044f\u044e\u0442 \u0441\u0432\u043e\u044e \u043b\u043e\u043a\u0430\u043b\u044c\u043d\u0443\u044e \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0443. \u041d\u0438\u043a\u0430\u043a\u0438\u0445 \u043a\u043b\u044e\u0447\u0435\u0439, \u0442\u043e\u043a\u0435\u043d\u043e\u0432 \u0438 \u043d\u0430\u0441\u0442\u0440\u043e\u0435\u043a \u2014 \u043f\u0440\u043e\u0441\u0442\u043e \u0432\u043a\u043b\u044e\u0447\u0438\u0442\u0435 \u00ab\u0423\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u044f \u043c\u0435\u0436\u0434\u0443 \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0430\u043c\u0438\u00bb \u0432 \u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430\u0445 \u043d\u0430 \u043b\u044e\u0431\u043e\u043c \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0435. \u0414\u0435\u0440\u0436\u0438\u0442\u0435 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 Mac \u0437\u0430\u043f\u0443\u0449\u0435\u043d\u043d\u044b\u043c \u0434\u043b\u044f \u043c\u043e\u043d\u0438\u0442\u043e\u0440\u0438\u043d\u0433\u0430 \u0432 \u0440\u0435\u0430\u043b\u044c\u043d\u043e\u043c \u0432\u0440\u0435\u043c\u0435\u043d\u0438.</p>"),
            ("Работает ли vultyr с Siri и Командами?",
             "Да. Встроенные App Intents позволяют сказать «Hey Siri, отключи GitHub на 2 часа», «проверь статус Stripe» или «покажи текущие проблемы», а те же действия можно добавить в приложение Команды. Есть и Focus Filter \u2014 режим «vultyr Focus» автоматически заглушает неважные сервисы.",
             "<p>Да. Встроенные App Intents позволяют сказать «Hey Siri, отключи GitHub на 2 часа», «проверь статус Stripe» или «покажи текущие проблемы», а те же действия можно добавить в приложение Команды. Есть и Focus Filter \u2014 режим «vultyr Focus» автоматически заглушает неважные сервисы.</p>"),
            ("Есть ли виджеты и Live Activities?",
             "На iOS \u2014 виджеты на экране «Домой» и экране блокировки (по одному сервису и сводка), плюс виджет в Пункте управления. Активные сбои закрепляются в Dynamic Island как Live Activities. На watchOS \u2014 осложнения для всех циферблатов с поддержкой Smart Stack: нужный сервис всплывает, когда что-то упало.",
             "<p>На iOS \u2014 виджеты на экране «Домой» и экране блокировки (по одному сервису и сводка), плюс виджет в Пункте управления. Активные сбои закрепляются в Dynamic Island как Live Activities. На watchOS \u2014 осложнения для всех циферблатов с поддержкой Smart Stack: нужный сервис всплывает, когда что-то упало.</p>"),
            ("\u0421\u043e\u0431\u0438\u0440\u0430\u0435\u0442 \u043b\u0438 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 vultyr \u043c\u043e\u0438 \u0434\u0430\u043d\u043d\u044b\u0435?",
             "\u041d\u0435\u0442. \u0423 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u044f \u043d\u0435\u0442 \u0430\u043a\u043a\u0430\u0443\u043d\u0442\u043e\u0432, \u0441\u0435\u0440\u0432\u0435\u0440\u043e\u0432, \u0432\u0441\u0442\u0440\u043e\u0435\u043d\u043d\u043e\u0433\u043e \u0442\u0440\u0435\u043a\u0438\u043d\u0433\u0430 \u0438 \u0432\u0441\u0442\u0440\u043e\u0435\u043d\u043d\u043e\u0439 \u0430\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0438. \u0412\u0441\u0435 \u043e\u0442\u0441\u043b\u0435\u0436\u0438\u0432\u0430\u0435\u043c\u044b\u0435 \u0441\u0435\u0440\u0432\u0438\u0441\u044b \u043e\u0441\u0442\u0430\u044e\u0442\u0441\u044f \u043d\u0430 \u0432\u0430\u0448\u0435\u043c \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0435. \u0417\u0430\u043c\u0435\u0447\u0430\u043d\u0438\u0435: \u044d\u0442\u043e\u0442 \u0441\u0430\u0439\u0442 (vultyr.app) \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0435\u0442 Google Analytics \u0431\u0435\u0437 \u0444\u0430\u0439\u043b\u043e\u0432 cookie \u0434\u043b\u044f \u0430\u0433\u0440\u0435\u0433\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u044b\u0445 \u0441\u0447\u0451\u0442\u0447\u0438\u043a\u043e\u0432 \u043f\u043e\u0441\u0435\u0442\u0438\u0442\u0435\u043b\u0435\u0439 \u2014 \u043f\u043e\u0434\u0440\u043e\u0431\u043d\u0435\u0435 \u0432 \u041f\u043e\u043b\u0438\u0442\u0438\u043a\u0435 \u043a\u043e\u043d\u0444\u0438\u0434\u0435\u043d\u0446\u0438\u0430\u043b\u044c\u043d\u043e\u0441\u0442\u0438.",
             "<p>\u041d\u0435\u0442. \u0423 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u044f \u043d\u0435\u0442 \u0430\u043a\u043a\u0430\u0443\u043d\u0442\u043e\u0432, \u0441\u0435\u0440\u0432\u0435\u0440\u043e\u0432, \u0432\u0441\u0442\u0440\u043e\u0435\u043d\u043d\u043e\u0433\u043e \u0442\u0440\u0435\u043a\u0438\u043d\u0433\u0430 \u0438 \u0432\u0441\u0442\u0440\u043e\u0435\u043d\u043d\u043e\u0439 \u0430\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0438. \u0412\u0441\u0435 \u043e\u0442\u0441\u043b\u0435\u0436\u0438\u0432\u0430\u0435\u043c\u044b\u0435 \u0441\u0435\u0440\u0432\u0438\u0441\u044b \u043e\u0441\u0442\u0430\u044e\u0442\u0441\u044f \u043d\u0430 \u0432\u0430\u0448\u0435\u043c \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0435. \u0417\u0430\u043c\u0435\u0447\u0430\u043d\u0438\u0435: \u044d\u0442\u043e\u0442 \u0441\u0430\u0439\u0442 (vultyr.app) \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0435\u0442 Google Analytics \u0431\u0435\u0437 \u0444\u0430\u0439\u043b\u043e\u0432 cookie \u0434\u043b\u044f \u0430\u0433\u0440\u0435\u0433\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u044b\u0445 \u0441\u0447\u0451\u0442\u0447\u0438\u043a\u043e\u0432 \u043f\u043e\u0441\u0435\u0442\u0438\u0442\u0435\u043b\u0435\u0439 \u2014 \u043f\u043e\u0434\u0440\u043e\u0431\u043d\u0435\u0435 \u0432 <a href=\"/ru/privacy.html\">\u041f\u043e\u043b\u0438\u0442\u0438\u043a\u0435 \u043a\u043e\u043d\u0444\u0438\u0434\u0435\u043d\u0446\u0438\u0430\u043b\u044c\u043d\u043e\u0441\u0442\u0438</a>.</p>"),
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


def topbar_html(locale, alt_urls):
    """Top navigation. Includes a compact language dropdown that links to the
    equivalent page in every supported locale; falls back to each locale's home
    if a mapping for the current page isn't present."""
    items = []
    for loc in LOCALES:
        href = alt_urls.get(loc, home_url_path(loc))
        native = LOCALE_NATIVE_NAMES[loc]
        short = LOCALE_SHORT_CODES[loc]
        attrs = ' aria-current="page"' if loc == locale else ""
        items.append(
            f'                    <a href="{href}" lang="{loc}" data-locale="{loc}" role="menuitem"{attrs}>'
            f'<span class="lang-native">{e(native)}</span>'
            f'<span class="lang-code" aria-hidden="true">{e(short)}</span>'
            f'</a>'
        )
    items_html = "\n".join(items)
    lang_aria = e(t(locale, 'lang_switch_aria'))
    current_short = LOCALE_SHORT_CODES[locale]
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
                <details class="lang-menu" data-lang-menu>
                    <summary class="lang-summary" aria-label="{lang_aria}" aria-haspopup="menu">
                        <span class="lang-summary-code">{e(current_short)}</span>
                        <span class="lang-summary-caret" aria-hidden="true">\u25be</span>
                    </summary>
                    <div class="lang-menu-panel" role="menu" aria-label="{lang_aria}">
{items_html}
                    </div>
                </details>
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
{topbar_html(locale, alt_urls)}
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
{topbar_html(locale, alt_urls)}
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
{topbar_html(locale, alt_urls)}
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

    feature_cards = "\n".join(
        f'            <div class="feature-card">\n'
        f'                <div class="feature-icon"><img src="/assets/icons/{icon}" alt="" width="22" height="22" aria-hidden="true"></div>\n'
        f'                <div>\n'
        f'                    <h3>{e(name)}</h3>\n'
        f'                    <p>{e(body)}</p>\n'
        f'                </div>\n'
        f'            </div>'
        for icon, name, body in t(locale, "home_features")
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
{topbar_html(locale, alt_urls)}

    <main id="main">
    <header class="hero">
        <div class="hero-inner">
            <div class="hero-tag fade-up fade-up-1" aria-hidden="true">{e(t(locale, 'home_hero_tag'))}</div>
            <img src="/assets/icon-256.png?v={ICON_VERSION}" alt="" class="icon" width="120" height="120" fetchpriority="high" decoding="async">
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

    <div class="divider" aria-hidden="true"></div>

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

    <div class="divider" aria-hidden="true"></div>

    <section class="features" aria-labelledby="features-heading">
        <div class="features-heading">
            <h2 id="features-heading">{e(t(locale, 'home_features_heading'))}</h2>
            <p>{e(t(locale, 'home_features_sub'))}</p>
        </div>
        <div class="features-grid">
{feature_cards}
        </div>
    </section>

    <div class="divider" aria-hidden="true"></div>

    <section class="bottom-cta" aria-labelledby="bottom-cta-heading">
        <h2 id="bottom-cta-heading">{e(t(locale, 'home_bottom_heading'))}</h2>
        <p>{e(t(locale, 'home_bottom_sub'))}</p>
        <a href="{APP_STORE_URL}" target="_blank" rel="noopener noreferrer" class="cta-button" aria-label="{e(t(locale, 'home_bottom_aria'))}">
            <img src="/assets/icons/download-simple-regular.svg" alt="" width="18" height="18" aria-hidden="true">
            {e(t(locale, 'home_bottom_button'))}
        </a>
    </section>

    <div class="divider" aria-hidden="true"></div>

{languages_section_html(locale, alt_urls)}
    </main>

{footer_html(locale)}
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
{topbar_html(locale, alt_urls)}
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
{topbar_html(locale, alt_urls)}
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
{topbar_html(locale, alt_urls)}
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
        prune_generated_dir(status_dir, {f"{svc['slug']}.html" for svc in services})

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
