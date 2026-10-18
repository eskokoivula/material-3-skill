# Accessibility

Checked 2026-10-18: m3.material.io foundations (accessibility, designing, writing) and component accessibility pages;
WCAG 2.2 (W3C Recommendation, December 2024). M3 never cites WCAG numbers; the mappings below are ours. Sources: `sources.md`.

## The rules and their numbers

| Topic | M3 says | WCAG 2.2 | The audit's rule |
|---|---|---|---|
| Text contrast | 4.5:1 small text, 3:1 large (14 pt bold / 18 pt) | 1.4.3 AA | 4.5:1; 3:1 at 24 px or 18.66 px bold → Broken |
| Non-text contrast | icons 3:1; clustered containers 3:1 against the background; a FAB container is exempt; outlines of targets 3:1 | 1.4.11 AA | icons 3:1 → Broken |
| Buttons | 3:1 on the container (filled, tonal, elevated) or the label (outlined, text) | 1.4.3 needs 4.5:1 for the label text (label-large is small text) | 4.5:1 for button labels (stricter than M3) |
| Disabled | exempt | exempt | not measured |
| Touch targets | 48×48 dp (24 dp icon inside); pointer 44×44; 8 dp apart | 2.5.8 AA: 24×24 CSS px or the spacing exception; 2.5.5 AAA: 44×44 | under 24 (no spacing) → Broken major; under 48 on a phone → Broken minor |
| Focus | a visible indicator; the web's focus ring 3 px secondary, 2 px out | 2.4.7 AA; 2.4.13 AAA wants a 2 px perimeter and 3:1 change | no visible pixel change on keyboard focus → Broken |
| Focus order | source order; initial focus per screen; dialogs take focus and return it | 2.4.3 A | design reading |
| Text scaling | 200% without loss; spacing stays 1×; one scroll direction | 1.4.4, 1.4.10 AA | sideways scroll on a phone → Broken |
| Motion | reduced motion: subtle fades, no parallax, no shape morph | 2.3.3 AAA (and 2.2.2 A for auto-playing motion) | moving animation under reduce → Broken |
| Labels | icons, images and visual cues labelled by purpose, never by look; no role word in the label; label matches visible text | 1.1.1, 2.5.3, 4.1.2 A | axe-core rules |
| Structure (web) | landmarks (one main, one banner, one contentinfo; label repeated ones); headings by hierarchy, no skipped levels, one H1 | 1.3.1, 2.4.1, 2.4.6 | axe-core rules + design reading |
| Color alone | selected states with a second cue (filled icon, bold label, checkmark) | 1.4.1 A | design reading |
| Gestures | pull-to-refresh needs a button alternative; dragging needs a single-pointer way | 2.5.1, 2.5.7 | design reading |
| Shortcuts | two or more keys; a single-key shortcut must be remappable or scoped | 2.1.4 A | design reading |

Contrast levels: standard guarantees 4.5:1 text and 3:1 required non-text; medium 3:1 for all non-text; high 7:1 text
and 4.5:1 non-text (`color.md`).

## Practical rules for designs

- Every interactive component: a 48 dp target (draw a smaller visual inside it), a visible keyboard focus ring, a hover
  state on pointer devices, a pressed state.
- Never rely on color for state; pair it with an icon change, weight or a mark.
- Text in rem on the web; let containers grow at 200%; stack side-by-side buttons when they no longer fit.
- Navigation bar labels stay visible and grow with text size (M3 says up to 2×; Flutter clamps them at 1.3×).
- Snackbars that disappear need inline feedback too on the web.
- Every image: alt text that states its purpose (up to about 125 characters), or empty alt when decorative.
- Dialogs: focus on open, trapped inside, returned to the trigger on close; Escape closes.
- Under reduced motion: fades only.

## Platform notes

- **Web:** semantic HTML first; ARIA roles where HTML has none; the focus ring on `:focus-visible`.
- **Flutter 3.44:** default targets are 48 on Android and iOS but 40 (icon buttons) and 32 (button height) on desktop
  platforms, below M3's 44 and 48 (`platform-flutter.md`); keyboard focus shows only as a 10% layer with no ring; web
  semantics are off until the user enables them or the app calls `SemanticsBinding.instance.ensureSemantics()`.
  Flutter's own test guidelines: `androidTapTargetGuideline` (48), `iOSTapTargetGuideline` (44),
  `labeledTapTargetGuideline`, `textContrastGuideline`.
