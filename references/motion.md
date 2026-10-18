# Motion

Checked 2026-10-18: m3.material.io motion pages; Compose, Material Components Android, Material Web and Flutter
`material_ui` token data (all agree). Sources: `sources.md`.

## Two systems, two jobs

- **Springs (motion physics, M3 Expressive 2025)** move components and interactions: a switch's handle, a button's
  shape, a sheet opening, a chip's selection.
- **Easing and duration tokens** still run **navigation transitions** (screen to screen). Google says transitions will
  move to physics later; until then, no bouncy springs in frequent, large transitions.

## Motion schemes

- **Standard:** functional, minimal bounce (0.15%); utilitarian products, dense tools, controls hit many times a minute.
- **Expressive:** overshoots and bounces; Material's recommended scheme for most products, above all hero moments and
  key interactions.
- One scheme per product for most motion. Every code default (Compose `MaterialTheme`, Android's `Theme.Material3`,
  Material Web's tokens) is standard; name the scheme you choose. The config's `motion` field picks it; the CSS also
  carries both sets.

## Springs

`Damping` is the damping ratio; mass is 1.

| Slot | Standard (ratio / stiffness) | Expressive | Animates | Settles in (0.1%) |
|---|---|---|---|---|
| fast spatial | 0.9 / 1400 | 0.6 / 800 | position, size, rotation, corner radius of small parts | 230 / 360 ms |
| default spatial | 0.9 / 700 | 0.8 / 380 | the same for medium areas (sheets, an expanding rail) | 320 / 440 ms |
| slow spatial | 0.9 / 300 | 0.8 / 200 | full-screen movement | 490 / 600 ms |
| fast effects | 1.0 / 3800 | same | color and opacity of small parts | 160 ms |
| default effects | 1.0 / 1600 | same | color and opacity of medium areas | 240 ms |
| slow effects | 1.0 / 800 | same | full-screen fades | 330 ms |

- Spatial springs for anything that moves or changes shape; effects springs for color and opacity, where overshoot must
  never happen (an alpha past 100%). Every state change of color or opacity animates on an effects spring (fast effects
  for small parts); an instant swap is a missing transition, and reduced motion keeps these fades.
- Pick the speed by size or distance (fast for small parts, slow for full screen), the kind by the property.
- Google bends its own rule once: Compose's button press morph uses default effects, to avoid any bounce.

## Easing and duration (for transitions)

| Easing | Value | For |
|---|---|---|
| emphasized | a two-segment path; on the web `linear()` sampled from it (the token files' `cubic-bezier(0.2, 0, 0, 1)` misses it by up to 16%) | starts and ends on screen; the default for most transitions |
| emphasized decelerate | `cubic-bezier(0.05, 0.7, 0.1, 1)` | enters |
| emphasized accelerate | `cubic-bezier(0.3, 0, 0.8, 0.15)` | leaves for good |
| standard (+ decelerate, accelerate) | `cubic-bezier(0.2, 0, 0, 1)`, `(0, 0, 0, 1)`, `(0.3, 0, 1, 1)` | small, quick utility transitions |

Durations: short 50 / 100 / 150 / 200, medium 250 / 300 / 350 / 400, long 450 / 500 / 550 / 600, extra-long 700–1000 ms.
Default pairs: emphasized 500 ms, emphasized decelerate 400 ms (enter), emphasized accelerate 200 ms (exit). Duration
follows area; exits are shorter than enters.

## Transition patterns

| Pattern | When | How (Material Components' defaults) |
|---|---|---|
| Container transform | an element opens into its detail (card to page, FAB to sheet, search box); hero moments, shallow hierarchies | the container carries into the new view; emphasized, 500 ms in, 400 ms back |
| Forward and backward | down or up one hierarchy level (inbox to thread) | a 30 dp horizontal slide with a fade; emphasized, 450 ms; the old view fades over the first 35% |
| Lateral | between peers (swiping tabs) | a slide without fade or parallax |
| Top level | switching navigation destinations | fade through: the old view fades out quickly, the new one fades in from 92% scale; 450 ms |
| Enter and exit | components appearing (dialogs, menus, snackbars, sheets) | grow away from the nearest edge; dialogs fade in from 80% scale over 400 ms (emphasized decelerate), exit 150 ms (emphasized accelerate) |
| Skeleton loaders | content loading | content fades in quickly over the skeleton |

Use the same transition for the same job everywhere. Don't use lateral between hierarchy levels, or between navigation
destinations. The prototype's router implements forward/backward, top level and fade (`prototype.md`).

## Reduced motion

With the platform's reduced-motion setting on, replace slides and scales with subtle fades and turn off decorative
effects (parallax, shape morph, carousel expansion). Opacity and color changes are not "motion" in WCAG's sense.
In CSS: `@media (prefers-reduced-motion: reduce)`; `m3.css` and the router do it. In Flutter, check two flags
yourself: `MediaQuery.disableAnimationsOf(context)` (Android's Remove animations) and
`View.of(context).platformDispatcher.accessibilityFeatures.reduceMotion` (iOS's Reduce Motion, which Flutter 3.44 does
not fold into `disableAnimations`). `AnimationController` only shortens animations to 5% of their duration, and
`animateWith` ignores the setting.

A progress value (a bar filling, a ring closing) moves on a spring that never bounces: Compose's
`ProgressIndicatorDefaults.ProgressAnimationSpec` is damping 1 with stiffness 50 (`Spring.StiffnessVeryLow`). In
Flutter, `SpringDescription.withDampingRatio(mass: 1, stiffness: 50, ratio: 1)`.

## Springs on the web

- A mass-1 spring from 0 to 1 at rest: with ω0 = √stiffness and ratio ζ < 1,
  x(t) = 1 − e^(−ζω0t)·(cos ωd·t + (ζω0/ωd)·sin ωd·t), ωd = ω0√(1−ζ²); for ζ = 1, x(t) = 1 − (1 + ω0t)·e^(−ω0t).
- `scripts/lib/spring.mjs` samples it into a CSS `linear()` easing and a duration (until it stays within 0.1% of the
  end); `tokens.css` carries every spring as `--md-sys-motion-<scheme>-spring-<slot>` with `-duration`, and the chosen
  scheme under `--md-sys-motion-spring-<slot>`.
- `linear()` is supported in Chrome 113, Firefox 112 and Safari 17.2 (Baseline since December 2023); values above 1 carry
  the overshoot.
- A CSS transition restarts its easing from the current value and forgets velocity; for drag-release or retargeting,
  run the spring formula in JavaScript.

## Springs in Flutter

`SpringDescription.withDampingRatio(mass: 1, stiffness: k, ratio: ζ)` maps a token exactly (`m3_tokens.dart` has every
spring). Run it with `AnimationController.unbounded` and `animateWith(SpringSimulation(...))`: a bounded controller clips
the overshoot, and `fling()` rejects under-damped springs (every M3 spatial spring is under-damped). Flutter has no M3
spring API yet (the `material_ui` package holds the data, not an API).
