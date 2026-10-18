# Designing a screen the M3 way

Checked 2026-10-18. M3 publishes no single step list; this order is assembled from its layout, usability, component and
writing pages (the content of each step is M3's; the order is ours). Values: `layout.md`, `components.md`.

## The steps

1. **Name the goals.** Primary, secondary, tertiary. One primary task per screen; it gets the strongest emphasis and
   the most space.
2. **Start at compact** (mobile first), designed for touch, pointer and keyboard alike, then walk up the breakpoints.
3. **Pick a canonical layout** by how the content relates:
   - **Feed:** browse lots of content (news, photos, social); cards in a grid from one column to many.
   - **List-detail:** parent and child (inbox and email, files and folder, settings and category); one pane on compact,
     two from expanded; back button only in the single-pane detail; selected state only in the two-pane list.
   - **Supporting pane:** secondary content that only means something next to the primary (comments beside a
     document); below the focus pane on compact and medium, a 360 dp side pane on expanded.
   - **Single pane:** anything else, and immersive content (video, games).
4. **Build from the scaffold** (2026): bars (app bar top, navigation bar bottom), rails (leading navigation rail,
   trailing companion rail, toolbars), panes (1–3; at least one flexible).
5. **Set margins and spacing:** 16 dp margins on compact, 24 dp above; spacing on the 8 dp scale (4 dp steps inside
   components); padding and gaps before margins.
6. **Pick navigation for the breakpoint** and the number of destinations: navigation bar for 3–5 destinations on compact
   (and medium with two panes); a rail (3–7) from medium up; tabs for related content inside one page; never a bar and a
   rail together; never a navigation bar on desktop.
7. **Pick the app bar:** search app bar when search leads; small for dense or scrolled pages; medium or large flexible
   for a bigger headline (M3 Expressive; the baseline medium and large bars are no longer recommended). One or two
   actions there; more go in a toolbar.
8. **Build the hierarchy:** the main action is the largest and highest-emphasis element; contrast ranks actions; type
   roles mark levels (display and headline for page titles, title for sections and cards, body for reading, label for
   controls); containment groups related things.
9. **Emphasize one action at a time.** One FAB at most; ideally one filled button per page; at most three buttons in a
   group; two actions in a dialog; never a bold button and a FAB together.
10. **Keep lines readable:** 40–60 characters; widen margins on large windows instead of stretching text.
11. **Walk up the breakpoints** with five questions: reveal (what can now show), divide (one pane or two), resize
    (cards and lists grow), reposition (bottom actions move to the leading side), swap (navigation bar to rail, bottom
    sheet to menu or side sheet).
12. **Add a hero moment only where it earns it:** one or two per product, at key, emotional interactions.
13. **Check structure:** reading and focus order match the visual order; initial focus on the most common goal; every
    control labelled; 48 dp targets.
14. **Check text at 200%:** stack side-by-side buttons, let containers grow, scroll in one direction only, never lose
    text to truncation without a way to read it.

## The emphasis ladder

| Level | Component | For |
|---|---|---|
| Highest | FAB (56, medium 80, large 96 dp) | the screen's single most important constructive action |
| Highest, with words | extended FAB | a primary action that needs a label, on long pages |
| High | filled button | the important final action (Save, Confirm); ideally one per page |
| Medium-high | tonal button | needs more weight than an outline (Next) |
| Medium | outlined button | important but not primary; pairs with a filled button |
| Medium, on busy backgrounds | elevated button | only where a button must stand off a busy surface |
| Low | text button | least important; inside dialogs, cards, snackbars |
| Icon actions | filled > tonal > outlined > standard icon button | the same ladder for icon-only actions |

In M3 Expressive, size is emphasis too: buttons come in XS 32, S 40, M 56, L 96 and XL 136 dp; the primary action may
be bigger than its neighbours; mixed sizes in one group only for hero moments.

## Choosing between similar components

| Need | Use | Not |
|---|---|---|
| Switch top-level destinations | navigation bar (compact), rail (medium up) | tabs, a drawer (Expressive retired it) |
| Related content inside one page | tabs | a navigation bar |
| Pick one of 2–5 options, or toggle views | connected button group (Expressive) or segmented button (baseline) | radio buttons in a row |
| Filter a collection | filter chips | checkboxes in a toolbar |
| Turn one setting on or off at once | switch | a checkbox that needs Save |
| Several related options | checkboxes | switches |
| A critical decision that blocks | dialog (two actions at most) | a snackbar |
| A short, low-priority update | snackbar (one text action) | a dialog |
| Temporary choices from a control | menu | a dialog |
| Secondary content from the bottom | bottom sheet (compact, medium) | a side sheet on phones |
| Secondary content from the side | side sheet (expanded up) | a bottom sheet on desktop |
| A short wait (200 ms – 5 s) | loading indicator (Expressive) | a progress bar |
| A longer process with known progress | progress indicator | a loading indicator |

## M3 Expressive's tactics (2025)

The launch post names seven; the usability page groups them differently. Their purpose: steer the eye to the most
important element. Research behind them: 46 studies, over 18,000 people; key elements found up to four times faster.

1. **Variety of shapes:** mix round and square; let one element depart from the shapes around it to pull the eye.
2. **Rich, nuanced color:** primary, secondary and tertiary on key components; surface tones for hierarchy; enough
   contrast that elements do not blend.
3. **Typography that guides:** emphasized styles on headlines and key actions; editorial-like moments inside the product.
4. **Containment for emphasis:** logical groups and containers; the brightest surface and the most space for the most
   important content.
5. **Fluid, natural motion:** shape morph, springs, micro-animations; sparingly.
6. **Component flexibility:** shift components to the context and the window size.
7. **Hero moments:** combine tactics at one or two key interactions per product; brief, delightful, surprising.

Build a strong hierarchy first (color, size, spacing, placement, containment); layer special emphasis on top. Not every
tactic at once: too many distract.

## UI text basics (M3 content design)

- Sentence case for every UI label, heading, button and menu item.
- Specific headings people can scan; key information first (people skim in an F shape).
- Button labels 1–3 words, verbs first; navigation labels 1–2 words (one on a rail).
- Address the user as "you"; never mix "my" and "your" on one screen.
- No period after a single sentence in labels, tooltips, list items, dialog text and links.
- Links on a surface use primary (tertiary for less emphasis) and are always underlined.
- The words themselves are copy: take them from the project's copy, or route them (SKILL.md, rule 4).
