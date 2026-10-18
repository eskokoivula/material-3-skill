# Typography

Checked 2026-10-18: m3.material.io typography pages; Flutter token database v6.1.0 and Material Web's latest token set
(Version 34) agree on all 60 baseline values. Sources: `sources.md`.

## The scale: 15 roles, plus 15 emphasized

Sizes and line heights in dp = logical px (Flutter) = CSS px; the web uses rem (px / 16). Tracking in px.

| Role | Face | Size / line height | Weight | Tracking |
|---|---|---|---|---|
| display-large | brand | 57 / 64 | 400 | -0.25 |
| display-medium | brand | 45 / 52 | 400 | 0 |
| display-small | brand | 36 / 44 | 400 | 0 |
| headline-large | brand | 32 / 40 | 400 | 0 |
| headline-medium | brand | 28 / 36 | 400 | 0 |
| headline-small | brand | 24 / 32 | 400 | 0 |
| title-large | brand | 22 / 28 | 400 | 0 |
| title-medium | plain | 16 / 24 | 500 | 0.15 |
| title-small | plain | 14 / 20 | 500 | 0.1 |
| body-large | plain | 16 / 24 | 400 | 0.5 |
| body-medium | plain | 14 / 20 | 400 | 0.25 |
| body-small | plain | 12 / 16 | 400 | 0.4 |
| label-large | plain | 14 / 20 | 500 (prominent 700) | 0.1 |
| label-medium | plain | 12 / 16 | 500 (prominent 700) | 0.5 |
| label-small | plain | 11 / 16 | 500 | 0.5 |

**Emphasized styles (M3 Expressive, 2025):** the same size, line height and tracking with a heavier weight: 500 for
display, headline, title-large and body; 700 (static fonts) or `wght` 600 (variable fonts) for title-medium, title-small
and labels. Components use the baseline styles by default; swap in the emphasized twin to show hierarchy or state
(selected items, unread messages, primary buttons, headlines, editorial moments). Material Web's latest tokens carry
them; Compose's hand-written set differs in tracking and is not used here; Flutter has no emphasized slots
(`m3_tokens.dart` adds them as constants).

The scale is a Major Second (1.125) anchored on 14; keep clear jumps between sizes and use a subset.

## Roles in use

- **Display:** the largest text: short, important lines or numerals, best on large screens; an expressive face fits.
- **Headline:** short, high-emphasis text on smaller screens; primary passages and regions (a dialog title).
- **Title:** medium emphasis, fairly short; secondary passages and regions (app bars, card titles, section headers).
- **Body:** reading text; faces made for small sizes; nothing decorative.
- **Label:** small utility text inside components and captions; buttons use label-large.
- Default text color on-surface; on-surface-variant for lower emphasis. Links use primary (tertiary when quieter) and
  are underlined.
- Contrast: 4.5:1 for small text, 3:1 for large text. In px, "large" means 24 px regular or 18.66 px bold, so only
  headline-small and larger count as large; every title, body and label style needs 4.5:1.
- Line length 40–60 characters at every breakpoint; on large windows widen margins, not lines.
- Tabular figures in tables and changing values (clocks, counters).

## Fonts

- `md.ref.typeface.brand` drives display, headline and title-large; `md.ref.typeface.plain` drives title-medium,
  title-small, body and label. Both default to Roboto (weights 400, 500, 700). M3's intent: the brand face for
  expression on large styles, the plain face for reading on small ones.
- Variable faces on the page: Roboto Flex (variable plain and brand), Google Sans Flex (featured with Expressive; its
  roundness echoes M3 shapes). All OFL.
- The font files must cover every weight the scale uses: 400, 500 and 700 (or a variable file, `"variable": true` in
  the config). A missing weight is faked or swapped for the nearest one.
- Swapping in a brand font: change the brand and plain typeface tokens; adjust line height and letter spacing for the
  face; leave the sizes alone (components are built around them); repeat for the emphasized set. Heavier faces may need
  more letter spacing; faces with long ascenders or descenders need other line heights.
- In the token config: `"type": { "brand": "IBM Plex Sans", "plain": "IBM Plex Sans" }`.

## Editorial treatments and hero moments (Expressive)

Standalone, type-led showcase moments with custom sizes inside a product: celebrate content, voice the user, highlight
a unique function. Never in labels or plain information; keep similar moments consistent (tokenize them); one or two
hero moments per product. On a website these inform the interface layer's key lines by analogy (`scope.md`).

## Variable-font axes

Weight: avoid very light weights at small sizes. Grade: changes stroke weight without reflow; a negative grade in dark
mode compensates for the heavier look. Width: narrow fits more characters; avoid wide styles in tight spaces. Optical
size: match it to the type size.

## Language height (2026)

Line heights can follow the script's height: small (Latin, Cyrillic, Greek, Hebrew), medium (about 7% taller: Arabic,
CJK, Thai, Vietnamese, Hindi), large (Burmese, Telugu), extra large (Nastaliq). Default to medium and switch by
language. The values exist only on the page; no token file has them yet. Arabic text on a site (an Arabic-speaking
market) needs the medium line heights.

## The tokens

CSS: `--md-sys-typescale-<role>-font`, `-size`, `-line-height`, `-weight`, `-tracking`, and
`--md-sys-typescale-emphasized-<role>-*`; the `.md-<role>` classes in `m3.css` apply them (`.md-emphasized` adds the
emphasized weight). Material Web's own typescale properties carry no tracking; ours do. Keep sizes in rem so browser text
settings scale them. Flutter: `TextTheme` names match the roles (`titleLarge` ↔ title-large).
