# Components

Checked 2026-10-18: every component's overview, guidelines and specs on m3.material.io; Flutter, Compose and Material
Web token files; Flutter and Compose APIs; the Material Web repository. Sources: `sources.md`. Picking between similar components: `screen-design.md`.

## M3 Expressive (2025) in one table

| New | Updated | Retired (no longer recommended) → replacement |
|---|---|---|
| button groups (standard and connected), FAB menu, loading indicator, split button, toolbars (docked and floating) | buttons (five sizes, round or square, toggle, shape morph), icon buttons (sizes, widths), FABs (medium 80 dp, color styles), extended FAB (three sizes), app bars (flexible), navigation bar (flexible, 64 dp), navigation rail (collapsed and expanded), progress indicators (wavy), sliders (sizes), search (contained), vertical menus, expressive lists | segmented button → connected button group · navigation drawer → expanded navigation rail · baseline navigation bar → flexible bar · baseline rail → collapsed rail · bottom app bar → docked toolbar · medium and large app bars → medium and large flexible · center-aligned app bar → small with centered text · small FAB → FAB or medium FAB · surface FABs → container color styles · indeterminate circular progress for short waits → loading indicator · stacked small FABs → FAB menu · divided search → contained |

Unchanged by Expressive: badges, bottom and side sheets, cards, carousel, checkbox, chips (Compose added shape morph in
2026), date and time pickers, dialogs, divider, radio, snackbar, switch, tabs, text fields, tooltips.

## The catalog

| Component | For | Key rules | Key specs |
|---|---|---|---|
| **Buttons** | most actions | filled ideally once per page; label 1–3 words, sentence case, never wrapped or truncated; leading icon only; keep their order across layouts | 40 dp (S) high, full corners, label-large; Expressive XS 32, S 40, M 56, L 96, XL 136; square 12/12/16/28/28; pressed 8/8/12/16/16; toggle (selected): filled and elevated take primary, tonal secondary, outlined inverse-surface, and round turns square (square turns round) |
| **Icon buttons** | one-tap icon actions | filled > tonal > outlined > standard; tooltip on hover on the web naming the action; toggle: outlined off, filled on | 40 dp container in a 48 dp target; sizes 32–136 dp; widths narrow, default, wide |
| **FAB** | the single most important constructive action | one per screen; never destructive or minor; lower right on compact and medium, in the rail on expanded | 56 dp (corner 16), medium 80 (20), large 96 (28); primary-container; level 3 |
| **Extended FAB** | a primary action that needs a label | one per screen; 1–2 word label; collapses to a FAB on scroll | small 56, medium 80, large 96 dp |
| **FAB menu** | 2–6 related actions from a FAB | only from a FAB; not with a toolbar or rail; on the web use a menu | items 56 dp, full corners |
| **Button group** | related buttons that react to each other | standard: hug content; connected: single or multi-select toggles, replaces segmented buttons | connected gap 2 dp, inner corners 4–20 dp |
| **Split button** | a main action plus related actions in a menu | trailing part always the expand icon | XS–XL; 2 dp gap |
| **Cards** | content and actions about one subject | elevated, filled, outlined by style only; collections at one elevation; no scrolling inside on mobile | corner medium 12; 16 dp padding; at most 8 dp apart |
| **Carousel** | a scrolling collection of visual items | multi-browse, uncontained, hero, full-screen; a "Show all" on vertical pages | item corner 28 |
| **Lists** | scannable indexes | one selection mode per list; gaps for contained lists, dividers for uncontained; Expressive segmented style recommended | rows 56 / 72 / 88 dp; body-large headline, body-medium supporting |
| **Dialogs** | critical information or a decision that blocks | headline a statement or question; two actions at most, confirm nearest the edge; no "Are you sure?" | surface-container-high, corner 28, 280–560 dp wide, 24 dp padding |
| **Bottom sheets** | secondary content from the bottom (compact, medium) | modal at most half height; scrim closes it; a non-drag way to resize | top corners 28; drag handle 32×4 in a 48 target |
| **Side sheets** | secondary content from the side (expanded up) | close button; usually trailing edge | max 400 dp |
| **Snackbar** | brief, non-blocking updates | one at a time; one text action; no icons; auto-dismiss after 4–10 s only without an action; on the web also inline feedback | inverse-surface; 48 dp one line |
| **Tooltips** | labels for icon-only buttons (plain) or short explanations (rich) | never critical information; hover on desktop, long-press on mobile | plain: inverse-surface, 24 dp |
| **Progress indicators** | a process with known or long progress (over 5 s) | one per group; switch indeterminate to determinate when known; stop indicator | 4 dp track; wavy in Expressive |
| **Loading indicator** | short waits, 200 ms – 5 s | centered where content will appear; never decorative | 48 dp, morphing shapes |
| **Navigation bar** | 3–5 top-level destinations on compact and medium | labels always; filled icon when active; never on desktop; never with a rail | baseline 80 dp; flexible 64 dp |
| **Navigation rail** | 3–7 destinations from medium up | leading edge, outside panes; FAB at the top; expanded rail replaces the drawer | baseline 80 dp; collapsed 96; expanded 220–360 |
| **App bars** | title, navigation and 1–2 actions | one filled or tonal icon button at most; no overflow menu (use a toolbar); fills with a color on scroll, no shadow | small 64 dp title-large; medium flexible 112 headline-medium; large flexible 120 display-small |
| **Tabs** | related content at one level inside a page | primary under the app bar; at most four fixed tabs; icons on all or none | 48 dp (64 with icon); 3 dp indicator |
| **Toolbars** | frequent actions for the page | docked (global, bottom) or floating (contextual); never with a navigation bar; one emphasized action | 64 dp |
| **Search** | finding by keyword | search bar (one view), search app bar (search-first home), search icon (secondary); hint names what is searched | 56 dp, full corners, surface-container-high |
| **Checkbox / radio / switch** | several options / one option / one setting applied at once | radio: five or fewer, vertical, one preselected; switch: never needs Save | 18 / 20 dp visual, 40 dp state layer, 48 dp target; switch 52×32 |
| **Sliders** | a value or range, applied at once | stops for fixed values; a text field for exact entry | Expressive track 16–96 dp |
| **Chips** | assist, filter, input, suggestion | always in a set; 20 characters or less; 8 dp apart; outline on plain backgrounds | 32 dp, corner 8, outline-variant border |
| **Menus** | temporary choices | keep unavailable items visible but disabled; standard or vibrant (tertiary) colors in Expressive | 48 dp items; baseline corner 4, Expressive grouped corner 16 |
| **Text fields** | text entry | filled or outlined, never mixed in one form; label always visible; error text replaces supporting text; asterisk for required | 56 dp, corner 4, body-large input, body-small supporting |
| **Date and time pickers** | dates, ranges, times | docked on larger windows, modal on mobile; input mode for distant dates | — |

Material 2 → 3 names: bottom navigation → navigation bar; dropdown and exposed dropdown → menu; action chip → assist
and suggestion chips; choice chip → single-select filter chip; speed dial → FAB menu; the top app bar's shadow → a color
fill on scroll.

## Where each exists

| | Web (Material Web) | Flutter (`package:flutter/material.dart`, 3.44) | Compose (1.5 with Expressive) |
|---|---|---|---|
| Status | maintenance mode; Expressive only in experimental "labs" | baseline M3 (token set v6.1); Expressive arriving in the separate `material_ui` package (icon buttons only so far) | everything first; Expressive stable in 1.5.0 later in 2026 |
| Missing | app bars, badges, sheets, cards, carousel, pickers, navigation bar, rail and drawer, search, snackbar, toolbars, tooltips, every Expressive component | side sheets, tooltips (M3 style), FAB menu, button groups, split button, loading indicator, toolbars (only the old bottom app bar), the 80 dp medium FAB, flexible app bars and nav bar | side sheets |

So on the web the skill builds components in its own CSS (`m3.css`, `platform-web.md`); in Flutter it themes the
built-in widgets and builds Expressive pieces by hand when a design needs them (`platform-flutter.md`).

## Contradictions to know

- The buttons page lists "elevated, filled, tonal, outlined, text" as the order of emphasis yet calls filled the
  strongest after the FAB; the skill follows filled-first.
- Elevated is "tonal plus a shadow" in words but surface-container-low with a primary label in the tokens.
- Material Web's "medium" FAB is 56 dp; Expressive's medium FAB is 80 dp.
