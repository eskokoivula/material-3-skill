# Brand first: a brand's values on M3's roles

M3 assigns every color, type style, corner and motion to a named role. Brand first means the brand's fixed values fill
the roles they belong to, exactly, and Google's color library fills the rest from the brand's own hues; then every pair
is proved for contrast. M3 is the structure; the brand is the look.

## The token config

`scripts/tokens.mjs` and `scripts/prototype.mjs` read one JSON file:

```json
{
  "name": "Example brand",
  "source": "#FF8A3D",
  "variant": "fidelity",
  "contrast": 0,
  "spec": "2021",
  "modes": ["dark"],
  "palettes": { "secondary": "#3D5AFE", "tertiary": "#00BFA5", "neutral": "#101418", "neutralVariant": "#1F2933", "error": "#FF5252" },
  "locked": {
    "dark": { "surface": "#101418", "onSurface": "#F2F5F8", "primary": "#FF8A3D", "onPrimary": "#1A0A00", "outline": "#3D5AFE4D" }
  },
  "type": { "brand": "Inter", "plain": "Inter", "weights": { "regular": 400, "medium": 500, "bold": 700 } },
  "shape": { "extra-small": 2, "small": 2, "medium": 2 },
  "motion": "standard"
}
```

| Field | Meaning | Default |
|---|---|---|
| `name` | shown in the generated files | `project` |
| `source` | the seed color the scheme grows from (usually the brand's primary) | the first locked `primary`, else `#6750A4` |
| `variant` | scheme variant: `tonalSpot`, `neutral`, `vibrant`, `expressive`, `fidelity`, `content`, `monochrome`, `rainbow`, `fruitSalad` | `tonalSpot` |
| `contrast` | contrast level, -1 to 1 (0 standard, 0.5 medium, 1 high) | `0` |
| `spec` | color spec, `2021` or `2025` (Flutter's `fromSeed` uses 2021) | `2021` |
| `modes` | `light`, `dark` or both | both |
| `palettes` | brand colors that replace a whole tonal palette (its hue and chroma) | the variant's own |
| `locked` | exact values per mode and role (`#RRGGBB` or `#RRGGBBAA`) | none |
| `type` | the brand and plain typefaces and weights (M3's ref typefaces; `weights` replaces Google's regular, medium and bold, 400, 500 and 700, in every style); `"variable": true` for variable font files; `"scale": { "display-large": { "size": 52, "lineHeight": 60 } }` to change a role's size, line height or tracking (each one a departure, listed in the report) | Roboto |
| `shape` | overrides of corner steps in dp (each one a departure from M3) | M3's scale |
| `motion` | `standard` or `expressive` motion scheme | `standard` |

Role names are camelCase (`surfaceContainerHigh`, `onPrimaryFixedVariant`); the 49 roles are in `color.md`.

## Mapping a brand onto roles

Brands rarely name their colors like M3. Map by job, not by name, and show the mapping before building on it:

| A brand's word | Usually | Note |
|---|---|---|
| background, ground, canvas | `surface` (and the legacy `background`) | the page's base |
| card, panel, raised surface | a step of the surface ladder (`surfaceContainer` … `Highest`) | choose by how raised it looks |
| menu, popover, sheet | `surfaceContainer` (menus), `surfaceContainerLow` (sheets), `surfaceContainerHigh` (dialogs) | M3's component defaults |
| text, foreground, ink | `onSurface` | |
| muted text, secondary text | `onSurfaceVariant` | |
| brand or action color | `primary` | key actions, active states, links |
| text on the brand color | `onPrimary` | |
| a supporting brand color | `secondary` or `tertiary`, or its palette only | accents, chips, contrast moments |
| error, destructive | `error` | |
| success, warning | not an M3 role | keep as a custom color, harmonized (see `color.md`); in Flutter a `ThemeExtension` with the color, its on-color and a container pair, so it switches with the theme like a role |
| border, divider | `outline` (needs 3:1) or `outlineVariant` (decorative) | translucent brand borders usually fail 3:1 |

Lock only what the brand truly fixes. Every unlocked role is generated from the brand's palettes, which keeps M3's tonal
hierarchy (containers, the surface ladder, fixed and inverse roles) in the brand's own hue. Locking a brand gray into
several surface roles flattens that ladder: three surfaces become one tone and cards, sheets and menus lose their
edges. Lock the brand's one background and let the other surfaces generate from its neutral palette.

## What the script does with it

1. Builds the scheme from `source` and `variant`; replaces palettes listed in `palettes`.
2. Puts every locked value in its role exactly.
3. Checks the required pairs: text pairs at 4.5:1 (every `on-X` on its `X`, `onSurface` and `onSurfaceVariant` on every
   surface, inverse text), UI pairs at 3:1 (`primary`, `secondary`, `tertiary`, `error` on surface; `outline` on surface;
   `inversePrimary` on inverse surface). `outlineVariant` is decorative and only reported.
4. Moves a generated role along its own palette until its pairs pass, and notes the change in the report.
5. A pair of two locked values that fails is **brand-locked**: reported, never hidden, with the nearest passing tone of
   the same hue as a departure for the owner to decide.

Read `report.md`: locked, generated and adjusted counts, every adjustment, every failing pair, the role table.

## Departures from a brand book

Where M3's way and the brand's rule differ (a pill button against a square one, one corner radius against M3's scale, a
single typeface against M3's brand and plain pair), do not choose. Show both, side by side, on the same screen, with one
sentence each, and ask. Record the answer where the project records decisions; if the brand book is the project's own
draft, the approved version updates it (the project's rules say how). A departure M3 itself allows (a brand typeface
is M3's own advice) is still shown as a choice, in one line with your recommendation: the owner confirms it; never
declare "no collision" on their behalf.

## Expressive and the brand

M3 Expressive (2025) adds emphasized type, bigger shape contrast, springier motion and new components. A calm brand may
take the type and shape parts and keep the standard motion scheme; an energetic one may take all of it. Flutter has the
tokens but almost none of the Expressive components (`platform-flutter.md`); the web has no library for them, so
`m3.css` builds them.
