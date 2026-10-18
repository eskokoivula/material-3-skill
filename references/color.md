# Color

Checked 2026-10-18: m3.material.io color pages, material-color-utilities (npm 0.4.0 and GitHub main), Flutter token
database v6.1.0, Compose and Material Web token files. Sources: `sources.md`.

## The roles

49 roles in Google's token list (Flutter v6.1.0 and Material Web agree; Compose has 48, no `shadow`). Name parts:
**container** is a fill for foreground elements, never a text color; **on-X** is text and icons on X; **-variant** is
the lower-emphasis twin; **surface** is backgrounds and large low-emphasis areas.

| Role | For | Pair | Baseline tone light / dark |
|---|---|---|---|
| `primary` | the most important actions and elements: FAB, high-emphasis buttons, active states | `on-primary` | 40 / 80 |
| `primary-container` | standout fills for key components | `on-primary-container` | 90 / 30 |
| `secondary` | less prominent elements | `on-secondary` | 40 / 80 |
| `secondary-container` | recessive fills: tonal buttons, the selected navigation indicator, selected filter chips | `on-secondary-container` | 90 / 30 |
| `tertiary` | contrasting accents, at the designer's choice | `on-tertiary` | 40 / 80 |
| `tertiary-container` | complementary containers (input areas, accents) | `on-tertiary-container` | 90 / 30 |
| `error`, `error-container` | urgent fills, icons, text | `on-error`, `on-error-container` | 40 / 80, 90 / 30 |
| `surface` | the default background | `on-surface`, `on-surface-variant` | 98 / 6 |
| `surface-container-lowest … -highest` | the container ladder (lowest, low, default, high, highest) | `on-surface` | 100, 96, 94, 92, 90 / 4, 10, 12, 17, 22 |
| `surface-dim`, `surface-bright` | the dimmest and brightest surfaces in both themes | `on-surface` | 87, 98 / 6, 24 |
| `on-surface`, `on-surface-variant` | text and icons on any surface; variant for lower emphasis | — | 10, NV30 / 90, NV80 |
| `inverse-surface`, `inverse-on-surface`, `inverse-primary` | contrast-reversed elements such as snackbars | each other | 20, 95, P80 / 90, 20, P40 |
| `outline` | important boundaries (text field outlines, target edges); needs 3:1 | against surface | NV50 / NV60 |
| `outline-variant` | decorative lines (dividers) | against surface | NV80 / NV30 |
| `X-fixed`, `X-fixed-dim`, `on-X-fixed`, `on-X-fixed-variant` | fills that keep one tone in light and dark (add-ons; most products need none; no component uses them) | each other | 90, 80, 10, 30 |
| `scrim` | under modals and expanded navigation, at 32% opacity | — | 0 |
| `shadow` | shadows | — | 0 |
| `background`, `on-background`, `surface-variant` | legacy: aliases of surface, on-surface, surface-container-highest | — | — |
| `surface-tint` | deprecated: alias of primary (the old elevation tint) | — | — |

Common component mappings (Flutter v6.1.0 tokens): filled button primary / on-primary; tonal button secondary-container;
outlined button outline-variant border (Expressive) with on-surface-variant label; FAB primary-container; navigation bar
surface-container with a secondary-container indicator; rail surface; cards: filled surface-container-highest,
elevated surface-container-low, outlined surface with outline-variant; dialog surface-container-high; menu
surface-container; search bar surface-container-high; bottom sheet surface-container-low; snackbar inverse-surface;
badge error; progress primary on a secondary-container track.

## Usage rules

- Body on `surface`; navigation on `surface-container`; keep each region's role the same at every breakpoint.
- Text and icons on surfaces: `on-surface` and `on-surface-variant`. On a filled element, its own on-color.
- Use roles only in their pairs. Pairing `primary` with `primary-container`, or `on-surface` on
  `secondary-container`, turns illegible when contrast level or dynamic color changes the values.
- `outline` for boundaries people must see (3:1); `outline-variant` only for decoration, never for target edges.
- Overlapping containers need different roles to read as separate (tonal difference first; shadows only to protect or
  invite interaction).
- Work with roles, never with hex values or palette tones, wherever colors may be generated, themed or contrast-adjusted.
- Expressive: mix primary, secondary and tertiary on key components and keep enough contrast between them; give the key
  content the brightest surface.

## Scheme variants

A variant sets each palette's hue and chroma; the spec version sets each role's tone. Flutter's `DynamicSchemeVariant`
has the same nine.

| Variant | Character | Keeps the brand color? |
|---|---|---|
| `tonalSpot` | the default: calm, low to medium colorfulness | hue yes, chroma cut (a strong red becomes muted) |
| `neutral` | nearly gray, a hint of color | no |
| `vibrant` | primary as colorful as each tone allows; loud | close for light seeds (2025 spec) |
| `expressive` | playful; 2021 moves primary's hue about 120° off the seed, 2025 keeps it | 2021 no, 2025 hue yes |
| `fidelity` | palettes follow the seed; the seed lands in `primary-container`; tertiary is its complement | yes, as the container |
| `content` | as fidelity, tertiary analogous; for colors taken from images | yes, as the container |
| `monochrome` | pure gray; primary black in light, white in dark | no |
| `rainbow`, `fruitSalad` | playful, hue moved | no |

No variant puts an arbitrary seed into `primary` itself (primary sits at tone 40 / 80, or the peak-chroma tone in 2025),
and roles with tones 50–59 are always moved to 49 or 60. To keep an exact brand hex in a role, lock it (`brand-first.md`)
and prove its pairs; a palette seeded from the hex returns the exact hex at the hex's own tone.

## Contrast levels

`contrast` runs from -1 to 1: 0 standard (the default), 0.5 medium, 1 high. Standard keeps hierarchy by mixing high- and
low-contrast elements and guarantees 4.5:1 text and 3:1 required non-text; medium guarantees 3:1 for all non-text;
high raises text to 7:1 and non-text to 4.5:1. Levels apply to light and dark. Custom components get them only by using
role pairs. In the 2021 spec surfaces move with the level; in 2025 they stay fixed. Flutter 3.44 sets the level through
`ColorScheme.fromSeed(contrastLevel:)`; `ThemeData(colorSchemeSeed:)` cannot.

## The 2021 and 2025 specs

The site never names spec versions; the library does. The default and Flutter's engine is 2021. The 2025 spec (the code
side of M3 Expressive's "vibrant color", phone platform) applies only to tonal spot, neutral, vibrant and expressive;
other variants fall back to 2021. What changes in 2025: tones follow each palette's peak chroma instead of fixed tones;
dark surfaces go deeper (surface 4, ladder 0–15); surfaces are more tinted; text and outline roles draw from the neutral
palette; on-colors target 6:1; the error hue follows the seed; legacy roles become aliases. Use 2025 only when the
platform that ships it can match (the web, through these tokens); Flutter's `fromSeed` stays on 2021.

Since August 2024 the light on-container roles use tone 30 (Flutter, the site, the library); Compose and Material Web
token files still say tone 10. The skill follows the library.

## Brand colors

- One brand color: make it the source. More brand colors: give them as palettes (secondary, tertiary, neutral, neutral
  variant, error) in their matching slots.
- Fidelity ("color match" in Google's Theme Builder) keeps role tones near the inputs.
- Static colors (formerly custom colors) stay fixed while the scheme changes, for brand expression or meaning (a green
  success); each needs four roles (color, on-color, container, on-container) and a contrast check. They are the last
  resort, after the roles.
- Harmonization nudges a static color's hue toward primary (at most 15°) so it sits with the scheme. Never harmonize
  brand colors or colors tied to the real world (signage, flags).
- Android's rule worth keeping everywhere: change each on-color together with its container.

## The tokens

- Three tiers: reference (`md.ref.palette.primary40`), system (`md.sys.color.primary`), component
  (`md.comp.filled-button.container.color`). Components read system tokens; system tokens read references.
- CSS custom properties: `--md-sys-color-<role>` in kebab case (Material Web's names); Flutter: `ColorScheme`
  properties in camel case (`onInverseSurface` for `inverse-on-surface`).
