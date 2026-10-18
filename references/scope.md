# Where M3 applies and where it stops

Checked 2026-10-18 against m3.material.io (layout, components, develop pages). Sources: `sources.md`.

## What M3 is for

- M3 is Google's open-source design system for **product interfaces**: Android apps, Google's own apps, web apps,
  desktop apps, watches and XR. Its guidance is about screens people operate: navigation, controls, forms, lists,
  feedback, layout by window size, states, motion and accessibility.
- It treats the web as a platform for products and web apps. None of its pages gives guidance for marketing sites,
  landing pages or editorial websites as page types: nothing on a site's hero section, page sections, long-scroll
  storytelling, footers or conversion.
- "Editorial treatments" and "hero moments" in M3 are moments inside a product (a type-led showcase, one or two
  delightful interactions per product), not a website's editorial layout or hero section. They can inform a website's
  interface layer by analogy; that use is ours, not M3's, and should be said.

## How far the skill goes

| Kind of work | M3's reach | What the skill does |
|---|---|---|
| A phone, tablet or desktop app | almost everything | designs it whole: screens, navigation, components, states, motion |
| A web app, dashboard, internal tool, admin panel | almost everything | designs it whole; builds the components in its own CSS (`platform-web.md`) |
| A company website or landing page | the interface layer | designs the interface layer and type moments; leaves story and pictures to the creative direction |
| A logo, brand identity, illustration, video, print, slides | none | says so; does not invent M3 rules |

## Mapping a website: the interface layer

For a website, list the page's parts and sort them before designing. A worked example (a company home page with a film,
a story and a contact form) shows the pattern:

| The page's part | Whose |
|---|---|
| Header and section menu, on phone and desktop | M3: navigation by window size, app bar rules, targets, states |
| Buttons and links (the main action, the header button, skip links) | M3: the emphasis ladder, shapes, states, focus |
| Forms (fields, choices, upload, errors, sending, confirmation) | M3: text fields, chips or radio, buttons, snackbar or inline feedback |
| Cards for people, capabilities, items | M3: card types, containment, spacing |
| Every text's size, weight and line height | M3: the type scale; Expressive emphasized styles for a few key lines |
| Color roles, contrast, dark theme | M3: roles from the brand's colors |
| Breakpoints, margins, spacing | M3: breakpoints (compact to extra-large), 16 / 24 dp margins, the spacing scale |
| Interface motion (menus, button and form states) | M3: motion scheme, transitions, reduced motion |
| Icons; decorative shapes | M3: Material Symbols (self-hosted on privacy-minded sites); the shape library as candidates |
| The story, its order, the hero, film, photographs, illustration, the mark | not M3: the creative direction |
| The words | not M3: the project's copy process (M3's content-design basics still apply to UI labels) |

When a page part is ambiguous (a statement set in a film frame, say), the composition is the creative direction's and
the type scale step is M3's. Say which half you are designing.

## Saying it

- When asked for something outside M3's reach, answer in one line that M3 does not cover it, and offer the part it does.
- In a website prototype the creative areas stay plain, labelled slots ("Hero: from the creative direction"): never
  composed, never filled with pictures, film stills or invented lines.
- When the user wants "the whole site in M3 style", explain the boundary once, then design the interface layer; do not
  dress invented rules as Google's.
