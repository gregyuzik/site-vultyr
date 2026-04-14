# site-vultyr — project notes for Claude

This is a **static website** (HTML/CSS/JS, no build framework) for the Vultyr
iOS/macOS/visionOS app. Hosted on **GitHub Pages** at <https://vultyr.app>.

The shared `~/git/CLAUDE.md` is Swift-focused — most of it does not apply
here. Use the conventions in this file instead.

## Architecture

```
site-vultyr/
├── data/services.json       # Source of truth: services + categories
├── scripts/
│   ├── generate.py          # Static site generator (run after editing services.json)
│   ├── download_favicons.py # Fetch favicons from google.com/s2/favicons
│   └── probe_statuspage.py  # Detect Statuspage.io API endpoints
├── assets/
│   ├── css/                 # Per-page-type stylesheets + shared.css
│   ├── icons/               # Phosphor SVG icons (see ICONS.md)
│   ├── favicons/            # Cached service favicons (PNG, 32 + 64 px)
│   ├── fonts/               # Audiowide.woff2 (only font)
│   └── *.webp, *.png        # Hero images, screenshots
├── index.html               # GENERATED — do not hand-edit
├── services.html            # GENERATED
├── 404.html                 # GENERATED
├── sitemap.xml              # GENERATED
├── status/*.html            # GENERATED — one per service
├── categories/*.html        # GENERATED — one per category
├── privacy.html             # HAND-WRITTEN content page
└── support.html             # HAND-WRITTEN content page
```

**Generated pages**: `index.html`, `services.html`, `404.html`, `sitemap.xml`,
`status/*.html`, `categories/*.html`. All come from `scripts/generate.py`. **Do
not hand-edit them** — the generator overwrites them on the next run. Edit
`generate.py` instead, then re-run.

**Hand-written pages**: `privacy.html`, `support.html`. Edit directly. Keep
their `<head>` (CSP, preconnects, font preload, GA snippet) in sync with what
`scripts/generate.py:head_common()` produces.

## Workflow

After any change to `data/services.json`, **always re-run the generator**:

```sh
python3 scripts/generate.py
```

The generator validates each output file (basic HTML well-formedness, presence
of CSP meta and `<html lang>`) and exits non-zero on failure.

To fetch favicons for newly added services:

```sh
python3 scripts/download_favicons.py
```

To re-detect Statuspage.io APIs across the catalog (rarely needed):

```sh
python3 scripts/probe_statuspage.py
```

## Branching & PRs

- **Never commit directly to `main`.** Create a feature branch first:
  `git checkout -b <short-topic>` (kebab-case, no `claude/` prefix).
- One branch per logical change. Don't mix unrelated fixes.
- Open a PR with `gh pr create` and let the user merge.
- Read-only tasks (audits, exploration) don't need a branch.

## Code style

- **Python**: stdlib only, no external deps, no type hints needed (script-level
  code), prefer pure functions, escape user/data input (`html.escape`,
  `safe_url`). The generator is run by hand, not in CI.
- **HTML**: 4-space indent, lowercase tags, double-quoted attributes. The
  generator emits this style — match it when hand-editing.
- **CSS**: Custom properties live in `:root` in `shared.css`. Per-page-type
  stylesheets are small and focused. Avoid `!important` except in the
  reduced-motion override.
- **JS**: Only `analytics.js`. Keep it small, no frameworks, no `eval`/`new
  Function`. Must be CSP-safe (no inline scripts allowed except hashed JSON-LD).

## Security

- **CSP**: Generated via `build_csp()`. Delivered via `<meta http-equiv>`,
  which means **`frame-ancestors`, `form-action`, `report-uri`, and `sandbox`
  are silently ignored**. To get those protections we'd need a CDN that can
  inject HTTP headers (Cloudflare Pages, Netlify, etc.). GitHub Pages can't.
- **Inline scripts**: All inline `<script>` blocks are JSON-LD with their
  sha256 hash auto-computed by `json_ld_block()` and included in the per-page
  CSP. Adding a new inline script means computing its hash too — easier to
  use a separate file in `assets/js/` and add it to `script-src 'self'`.
- **External resources**: Only `googletagmanager.com` and `*.analytics.google.com`
  are allowed (for cookieless GA4). No fonts, no CDNs, no images from third
  parties.
- **GA4 privacy config**: `analytics.js` must run before `gtag.js` so the
  privacy params (`anonymize_ip`, `client_storage: 'none'`) populate
  `dataLayer` before gtag.js processes the queue. Both scripts are `defer`
  (in document order) — never `async`.

## Privacy claims

The privacy policy says: app collects no data; website uses cookieless GA4.
Both must remain true. If you add a new external dependency or analytics
service, **update `privacy.html`** in the same PR.

## Common gotchas

- **Service slug rename**: rename in `data/services.json` (both the service
  entry AND any `categories[].serviceSlugs` references), then regenerate. The
  generator's `prune_generated_dir()` deletes orphan HTML files automatically.
- **Adding a service to the 404 "popular" list**: edit
  `scripts/generate.py:generate_404()`. The generator asserts each popular
  slug exists in `services.json` and aborts if not.
- **Stat numbers on home page**: `total_services`, category count, etc. are
  computed from `services.json` — don't hardcode them.
- **CSP hash mismatch on regen**: if you edit a JSON-LD block in
  `generate.py`, the hash changes automatically. If you ever hand-edit a
  generated HTML file, you'll break the CSP. Re-run the generator.
- **`privacy.html` / `support.html` drift**: when `head_common()` changes in
  the generator, mirror the change in these two hand-written files.
