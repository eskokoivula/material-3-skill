# Surfaces, elevation and states

Checked 2026-10-18: m3.material.io elevation and states pages; Flutter v6.1.0, Compose and Material Web latest tokens.
Sources: `sources.md`.

## Elevation

| Level | dp | Use |
|---|---|---|
| level0 | 0 | most components at rest: filled, tonal and outlined buttons, filled and outlined cards, chips, lists, rails, tabs, unscrolled app bars |
| level1 | 1 | elevated button and card, elevated chips, modal bottom sheet, modal drawer, modal side sheet, banner |
| level2 | 3 | scrolled app bar, menu, navigation bar, rich tooltip, toolbar, modal expanded rail |
| level3 | 6 | FAB, extended FAB, dialogs, date and time pickers, search, snackbar |
| level4 | 8 | interaction only (hover, drag) |
| level5 | 12 | interaction only |

- M3 separates surfaces by **tonal difference** first (the surface container ladder); shadows only to protect an element
  on a busy background or to invite interaction. Fewer levels make each shadow mean more.
- Overlapping areas need different surface roles. Interactive edges must meet 3:1 against the surface below.
- Interaction raises elevation one level: buttons +1 on hover, FAB 3 → 4, cards +1; pressed returns to rest; disabled
  drops to 0; dragged cards and chips rise to 3–4.
- The scrim under modals and expanded navigation is the scrim color at 32%.
- The surface tint (the old elevation overlay) is deprecated; use the surface roles.
- Web shadows (Material Web's formula): a key shadow at 30% opacity plus an ambient shadow at 15% of the shadow color.
  `m3.css` has them as `.md-elevation-1` … `-5`.

## States

Six: enabled, disabled, hover, focused, pressed, dragged. They combine (selected and hovered) and apply the same way on
every component. Each state shows by two cues, never color alone.

**State layers:** a translucent overlay in the content's color (the on-color of the icon or label), stacked container →
state layer → content; one at a time; a 40 dp layer inside a 48 dp target.

| State | Opacity |
|---|---|
| hover | 0.08 |
| focus | 0.10 |
| pressed | 0.10 |
| dragged | 0.16 |
| disabled content | on-surface at 0.38 |
| disabled container | on-surface at 0.12 (0.10 for Expressive buttons) |

Material Web's older v0.192 tokens say 0.12 for focus and pressed; the site, Flutter, Compose and Material Web's latest
set say 0.10. The skill uses 0.10.

- **Hover:** low emphasis; fades in and out; one at a time. App bars, dialogs, menus, navigation and sheets do not take
  it themselves; their actionable children do.
- **Focus:** higher emphasis than hover; on every interactive component; one at a time. On the web keyboard focus shows a
  **focus ring**, not only a layer: 3 px thick, the secondary color, 2 px outside the container
  (`md.sys.state.focus-indicator.thickness` 3, `outer-offset` 2). Menus, lists, the navigation bar and drawer and tabs
  draw the ring inside the edge (`inner-offset` -3). An outlined text field in error rings in the error color.
- **Pressed:** high emphasis; a ripple; buttons and cards may also rise.
- **Dragged:** low-emphasis overlay; list items, chips and cards may lift.
- **Disabled:** shown by color and lower elevation; exempt from contrast targets; cannot be focused, pressed or dragged.
  An unavailable FAB is hidden, not shown disabled.

Flutter 3.44's Material widgets show keyboard focus only as the 10% layer, with no ring: weak against WCAG 2.4.7 on
desktop and web. Add a visible focus decoration in the theme for keyboard-heavy Flutter apps.

## The tokens

CSS: `--md-sys-elevation-level0…5` (dp numbers), `--md-sys-state-<state>-state-layer-opacity`,
`--md-sys-state-focus-indicator-thickness | -outer-offset | -inner-offset`. `m3.css` applies the state layer and the focus
ring to every interactive component.
