# Phosphor Icons Catalog

Icons from [Phosphor Icons](https://phosphoricons.com) v2.1.1 (MIT License).
Chosen for visual consistency with SF Symbols used in the Vultyr app.

## Naming Convention

- `{name}-regular.svg` — outline style (default for UI)
- `{name}-fill.svg` — solid fill (for emphasis/status)

## Website Features Section

| Feature | Icon | File |
|---------|------|------|
| Live Status Dashboard | chart-bar | `chart-bar-regular.svg` |
| Smart Alerts | bell-ringing | `bell-ringing-regular.svg` |
| Cross-Device Alerts | cloud-check | `cloud-check-regular.svg` |
| Every Apple Platform | devices | `devices-regular.svg` |
| Incident Details | lightning | `lightning-regular.svg` |
| Battery-Aware Polling | battery-charging | `battery-charging-regular.svg` |
| Retro Themes | palette | `palette-regular.svg` |
| No Account Needed | shield-check | `shield-check-regular.svg` |
| 16 Languages | translate | `translate-regular.svg` |

## Status Indicators

| Status | Icon | File |
|--------|------|------|
| Operational | check-circle | `check-circle-fill.svg` |
| Degraded | minus-circle | `minus-circle-fill.svg` |
| Outage | x-circle | `x-circle-fill.svg` |
| Incident | warning-circle | `warning-circle-fill.svg` |
| Maintenance | wrench | `wrench-regular.svg` |

## Service Categories

| Category | Icon | File |
|----------|------|------|
| Cloud / Infrastructure | database | `database-regular.svg` |
| Dev Tools | code | `code-regular.svg` |
| Communication | chat-circle | `chat-circle-regular.svg` |
| Productivity / SaaS | list-bullets | `list-bullets-regular.svg` |
| Payments | credit-card | `credit-card-regular.svg` |
| Apple | apple-logo | `apple-logo-regular.svg` |
| AI / ML | robot | `robot-regular.svg` |
| Social | users | `users-regular.svg` |
| Streaming | play-circle | `play-circle-regular.svg` |
| Gaming | game-controller | `game-controller-regular.svg` |
| Telecom | wifi-high | `wifi-high-regular.svg` |
| Security | key | `key-regular.svg` |
| Email | envelope-simple | `envelope-simple-regular.svg` |

## Navigation & UI

| Purpose | Icon | File |
|---------|------|------|
| Download CTA | download-simple | `download-simple-regular.svg` |
| Arrow / CTA | arrow-right | `arrow-right-regular.svg` |
| Chevron | caret-right | `caret-right-regular.svg` |
| Search | magnifying-glass | `magnifying-glass-regular.svg` |
| Settings | gear | `gear-regular.svg` |
| Support / FAQ | question | `question-regular.svg` |
| Privacy | lock | `lock-regular.svg` |
| Contact | envelope-simple | `envelope-simple-regular.svg` |
| Info | info | `info-regular.svg` |
| Refresh | arrow-clockwise | `arrow-clockwise-regular.svg` |
| Globe | globe | `globe-regular.svg` |
| Uptime / Clock | clock | `clock-regular.svg` |
| Tip Jar / Support | heart | `heart-regular.svg` |
| Star / Favorite | star | `star-regular.svg` |

## Platform Icons

| Platform | Icon | File |
|----------|------|------|
| iPhone | device-mobile | `device-mobile-regular.svg` |
| Mac | monitor | `monitor-regular.svg` |
| Apple Watch | watch | `watch-regular.svg` |
| Apple TV | television-simple | `television-simple-regular.svg` |
| All devices | devices | `devices-regular.svg` |

## Branding

| Purpose | Icon | File |
|---------|------|------|
| App identity (eye) | eye | `eye-regular.svg` / `eye-fill.svg` |
| Notifications | bell-ringing | `bell-ringing-fill.svg` |
| Trust / Privacy | shield-check | `shield-check-fill.svg` |
| Starred | star | `star-fill.svg` |
| Tip jar | heart | `heart-fill.svg` |

## Usage in HTML

```html
<!-- Inline SVG (recommended for styling) -->
<img src="assets/icons/chart-bar-regular.svg" alt="" class="icon" width="24" height="24">

<!-- With CSS color override (add class to SVG) -->
<style>
  .icon { filter: brightness(0) invert(1); } /* white */
  .icon-accent { filter: invert(48%) sepia(90%) saturate(1000%) hue-rotate(360deg); } /* orange-ish */
</style>
```

## License

Phosphor Icons are licensed under the MIT License.
https://github.com/phosphor-icons/core/blob/main/LICENSE
