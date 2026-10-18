# Layout

Checked 2026-10-18. M3 rewrote its layout guidance in May 2026 ("Expressive layout"): window size classes became
**breakpoints**, a new **scaffold** of bars, rails and panes, and an **8 dp spacing system**. The old layout URLs now
redirect. Sources: `sources.md`.

## Breakpoints

| Breakpoint | Width (dp = CSS px) | Panes | Navigation | Margins | Spacer |
|---|---|---|---|---|---|
| Compact | under 600 | 1 | navigation bar (3–5 destinations), or a modal expanded rail from a menu icon | 16 | — |
| Medium | 600–839 | 1 recommended, 2 for low-density content (50/50) | navigation bar or collapsed rail (the pages disagree; rail for one pane, bar for two) | 24 | 24 |
| Expanded | 840–1199 | 2 recommended (a fixed 360 dp pane allowed) | collapsed or expanded rail, standard or modal | 24 | 24 |
| Large | 1200–1599 | 2 recommended (fixed 412 dp allowed) | collapsed or expanded rail | 24 | 24 |
| Extra-large | 1600 and up | 2; 1 or 3 allowed (a standard side sheet as the third) | expanded rail fits best | 24 | 24 |

- Design for breakpoints, not devices: windows change with split screen, unfolding and rotation. Large and extra-large
  matter most for the web on laptops and desktops.
- Height classes exist on Android (compact under 480, medium 480–899, expanded 900+); most layouts scroll, so they are
  rarely needed. A phone in landscape is medium width but compact height: no two panes there.
- Moving up a breakpoint, ask five questions: **reveal** (show what smaller sizes hid), **divide** (one pane or two),
  **resize** (cards, feeds, panes grow), **reposition** (bottom actions move to the leading side; a FAB can sit in the
  rail), **swap** (exchange only components with the same function: navigation bar ↔ rail, bottom sheet ↔ menu or side
  sheet).
- Line length stays 40–60 characters; set a maximum width on content and components rather than stretching them.

## The scaffold (2026)

- **Bars** frame the screen: the app bar at the top, the navigation bar at the bottom; a bar spans one pane or the
  window. Bars stay out of the system's safety regions.
- **Rails** are the next layer: the navigation rail on the leading edge, a companion rail or a vertical toolbar on the
  trailing edge, toolbars and FABs in the top and bottom rail regions on compact.
- **Panes** hold all content: 1–3 per layout, at least one flexible. Fixed panes keep their width (360 or 412 dp);
  flexible panes take the rest. Panes are permanent or temporary, co-planar, floating or docked.
- Adaptive strategies: **show and hide** (panes enter and leave), **levitate** (a docked pane floats on large screens),
  **reflow** (a supporting pane moves below the primary one when space runs out).
- Accessibility: focus order follows the visual arrangement; a modal floating pane takes focus and returns it on close.

## Canonical layouts

| Layout | For | Compact | Medium | Expanded and up |
|---|---|---|---|---|
| Feed | browsing lots of content (news, photos, social) | cards stacked, full width | columns of mixed widths | more columns |
| List-detail | parent and child (inbox and mail, settings and category) | list or detail, one at a time | one pane recommended, two allowed | list and detail side by side; placeholder detail when nothing is selected |
| Supporting pane | secondary content that means something only next to the primary | below the primary pane (or a bottom sheet) | below the primary pane | a fixed 360 dp side pane; primary about two-thirds |

In list-detail the back button appears only in the single-pane detail; the selected state only in the two-pane list;
keep each view's state (scroll, read status) when switching.

## Spacing

The 8 dp scale (2026): space0 0, space25 2, space50 4, space75 6, space100 8, space125 10, space150 12, space175 14,
space200 16, space250 20, space300 24, space400 32, space450 36, space500 40, space600 48, space700 56, space800 64,
space900 72 (`md.sys.measurement.space100` = 8 dp). Steps off the 8 multiple are "nested units" for components.

- Padding inside an element, gaps between elements, margins outside; prefer padding and gaps on the parent; margins for
  layout.
- Leading and trailing (not left and right), so RTL mirrors them.
- Text at 200% does not scale spacing.
- The tokens ship only in Compose; on the web, use the values (the skill's CSS uses px multiples of 4 and 8).
- Spacing is expressive too: dense feels serious, spacious feels calm; the most important content gets generous space
  and the brightest surface; negative space frames emphasis.

## Density and targets

- Density scale 0 (default), -1, -2, -3; each step removes 4 dp of padding or height. Never by default, never on menus,
  snackbars or dialogs, and never if it pushes targets below 48×48. Text size does not change with density.
- Touch targets at least 48×48 dp, pointer targets at least 44×44, 8 dp between targets.
- Higher density suits scanning and comparing (tables, dashboards); lower density suits sites with one message.

## Grids

M3 publishes no column counts or widths per breakpoint (Android's doc says four columns on phones is common). Any column
count you use is a design choice: say so. Lay the grid first, then bars and rails at the edges, then panes; rulers keep
margins and the title line aligned.

## RTL

Navigation sits on the right; layouts mirror; directional icons (back, forward, send) mirror; media controls, clocks
and charts do not; linear progress fills from the right except in Hebrew; leading and trailing spacing swaps.

## In the prototype

`m3.css` reads the window from the `.md-window` container: `md-only-compact` (under 600), `md-from-medium` (600 up),
`md-from-expanded` (840 up), `md-margin` (16 / 24 px margins) and `md-list-detail` (two panes from 840).
