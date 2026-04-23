# Phosphor Icons Catalog

Icons from [Phosphor Icons](https://phosphoricons.com) v2.1.1 (MIT License).
Chosen for visual consistency with SF Symbols used in the Vultyr app.

## Naming Convention

- `{name}-regular.svg` — outline style (the only style used on this site)

## Website Features Section (`index.html`)

| Feature | File |
|---------|------|
| Live Status Dashboard | `chart-bar-regular.svg` |
| Smart Alerts | `bell-ringing-regular.svg` |
| Siri & Shortcuts | `microphone-regular.svg` |
| Widgets & Live Activities | `squares-four-regular.svg` |
| Watch Complications | `watch-regular.svg` |
| Mac Hub — iPhone Fallback | `cloud-check-regular.svg` |
| Alert Reliability View | `monitor-regular.svg` |
| Every Apple Platform | `devices-regular.svg` |
| Incident Details | `lightning-regular.svg` |
| Battery-Aware Polling | `battery-charging-regular.svg` |
| 12 Themes | `palette-regular.svg` |
| App Data Stays Local | `shield-check-regular.svg` |
| 17 App Languages | `translate-regular.svg` |
| Download CTA | `download-simple-regular.svg` |

## Service Categories (`categories/*.html`)

The category icon for each category is set in `data/services.json` via the
`icon` field, then inlined into the page by `scripts/generate.py`.

| Category | File |
|----------|------|
| Cloud & Infrastructure | `cloud-check-regular.svg` |
| Developer Tools | `code-regular.svg` |
| Communication | `chat-circle-regular.svg` |
| Productivity & SaaS | `gear-regular.svg` |
| Payments & Commerce | `credit-card-regular.svg` |
| Apple | `apple-logo-regular.svg` |
| Google | `globe-regular.svg` |
| Microsoft | `monitor-regular.svg` |
| Amazon | `database-regular.svg` |
| AI & Machine Learning | `robot-regular.svg` |
| Social Media | `users-regular.svg` |
| Streaming & Media | `play-circle-regular.svg` |
| Gaming | `game-controller-regular.svg` |
| Telecom & ISP | `wifi-high-regular.svg` |
| Security | `shield-check-regular.svg` |
| Email & Marketing | `envelope-simple-regular.svg` |

## Status Page Link Buttons (`status/*.html`)

| Purpose | File |
|---------|------|
| Official Status Page link | `chart-bar-regular.svg` |
| Service Homepage link | `globe-regular.svg` |

## Adding a New Icon

1. Download the regular weight from <https://phosphoricons.com> as SVG.
2. Save as `assets/icons/{name}-regular.svg`.
3. Reference it from HTML as `<img src="/assets/icons/{name}-regular.svg" alt="" width="22" height="22" aria-hidden="true">`.
4. If the icon needs to be tinted, add a CSS `filter:` rule (see `assets/css/home.css` `.feature-icon img` for the accent-green example, or `assets/css/service.css` `.links-row a img` for white).
5. Keep this catalog in sync.

## License

Phosphor Icons are licensed under the MIT License.
<https://github.com/phosphor-icons/core/blob/main/LICENSE>
