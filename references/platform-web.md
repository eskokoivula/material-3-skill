# M3 on the web

Checked 2026-10-18. Sources: `sources.md`.

## The state of Google's web library

- Material Web (`@material/web`) is in **maintenance mode** pending new maintainers: no new features or components; M3
  Expressive "not implemented on web" (the M3 site) and "not planned" (the maintainers, May 2025).
- Releases continue: v2.5.0 (July 2026) added experimental "labs" pieces, some Expressive; labs are not for production
  and may break without a major version.
- It never built: app bars, badges, sheets, cards, carousel, date and time pickers, navigation bar, rail and drawer,
  search, snackbar, toolbars, tooltips.
- Angular Material is another M3 web implementation; it may differ from the guidelines.

So a web project builds M3 itself: Google's token names and values in CSS, components in CSS on those tokens. That is
what `scripts/tokens.mjs` and `templates/m3.css` do.

## Tokens as CSS custom properties

The names follow Material Web, so its components would pick them up if a project uses any:

| Group | Custom properties |
|---|---|
| Color | `--md-sys-color-<role>` (49 roles, kebab case), per theme under `:root` / `[data-theme]` / `prefers-color-scheme` |
| Typefaces | `--md-ref-typeface-brand`, `--md-ref-typeface-plain`, `--md-ref-typeface-weight-regular | medium | bold` |
| Type scale | `--md-sys-typescale-<role>-font | size | line-height | weight | tracking` and `--md-sys-typescale-emphasized-<role>-*` (Material Web itself has no tracking property; ours do) |
| Shape | `--md-sys-shape-corner-<step>` (none … extra-extra-large, full = 9999px) |
| Elevation | `--md-sys-elevation-level0 … 5` (dp numbers; shadows in `m3.css`) |
| State | `--md-sys-state-<hover | focus | pressed | dragged>-state-layer-opacity`, `--md-sys-state-focus-indicator-*` |
| Motion | `--md-sys-motion-easing-*`, `--md-sys-motion-duration-*`, springs `--md-sys-motion-<standard | expressive>-spring-<slot>` with `-duration`, and the chosen scheme's `--md-sys-motion-spring-<slot>` |

Sizes are in rem so browser text settings scale them (WCAG 1.4.4). Material Web does not support palette (`--md-ref-palette-*`)
or motion properties; ours are an extension with the same naming.

## m3.css

Components on the tokens, values from Google's component token files. What it adds beyond Material Web: letter spacing,
state layers on every control, a `:focus-visible` ring (3 px secondary, 2 px out), 48 px targets with smaller visuals
drawn inside, reduced-motion handling, Expressive button sizes and shapes, window-size classes through container
queries. Class names start with `md-`; the list is in `prototype.md`. For a production site, copy the parts the design
uses into the site's own styles (keep the token names); do not depend on the template's viewer.

## Motion on the web

- Springs as `linear()` easings with their durations (`motion.md`); Baseline since December 2023.
- The Emphasized easing as `linear()` sampled from its real path; the token files' cubic-bezier is a stand-in.
- `@media (prefers-reduced-motion: reduce)`: fades only.

## Icons

Material Symbols (Outlined, Rounded, Sharp), variable axes FILL 0–1, wght 100–700, GRAD -50–200 (−25 for light-on-dark
in M3's advice), opsz 20–48. One style and weight per product. On Google Fonts for prototypes; on a privacy-minded
production site (no third-party requests) self-host a subset of the font or use SVGs of only the icons used
(`@material-design-icons/svg` or the font files in google/material-design-icons, Apache 2.0). The npm `material-symbols`
packages are third-party.

## Fonts

Load the brand faces with only the weights the type scale uses (400, 500, 700, or a variable font). Self-host when the
site promises no third-party calls.

## Dark theme and contrast levels

Generate light and dark (and medium or high contrast if offered) with `tokens.mjs`; switch with `data-theme` or
`prefers-color-scheme`; `prefers-contrast: more` is the obvious hook for a high-contrast scheme (M3 names none).
