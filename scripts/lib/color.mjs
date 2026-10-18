// M3 color roles from a source color with Google's color library, brand first: locked brand values stay
// exact, generated roles come from the brand's own palettes, and every required pair is proved for contrast.
import mcu from './mcu.mjs';
import { colorRoles, colorRoleRefs } from './google.mjs';

const {
  Hct, DynamicScheme, TonalPalette, MaterialDynamicColors, argbFromHex, hexFromArgb,
  SchemeTonalSpot, SchemeNeutral, SchemeVibrant, SchemeExpressive, SchemeFidelity, SchemeContent,
  SchemeMonochrome, SchemeRainbow, SchemeFruitSalad,
} = mcu;

export const VARIANTS = {
  tonalSpot: SchemeTonalSpot, neutral: SchemeNeutral, vibrant: SchemeVibrant, expressive: SchemeExpressive,
  fidelity: SchemeFidelity, content: SchemeContent, monochrome: SchemeMonochrome, rainbow: SchemeRainbow,
  fruitSalad: SchemeFruitSalad,
};

const mdc = new MaterialDynamicColors();
export const dynamicColor = (role) => mdc[role]();

// --- colors as values -------------------------------------------------------------------------------------

// '#RRGGBB' or '#RRGGBBAA' -> { r, g, b, a } with channels 0..255 and a 0..1.
export function parseHex(hex) {
  const h = hex.replace('#', '');
  if (!/^([0-9a-f]{6}|[0-9a-f]{8})$/i.test(h)) throw new Error(`not a hex color: ${hex}`);
  const n = (i) => Number.parseInt(h.slice(i, i + 2), 16);
  return { r: n(0), g: n(2), b: n(4), a: h.length === 8 ? n(6) / 255 : 1 };
}

export const toHex = ({ r, g, b, a = 1 }) => {
  const c = (v) => Math.round(v).toString(16).padStart(2, '0');
  return `#${c(r)}${c(g)}${c(b)}${a < 1 ? c(a * 255) : ''}`.toUpperCase();
};

// A translucent color laid over an opaque one.
export function over(top, bottom) {
  const t = parseHex(top);
  const b = parseHex(bottom);
  return toHex({ r: t.r * t.a + b.r * (1 - t.a), g: t.g * t.a + b.g * (1 - t.a), b: t.b * t.a + b.b * (1 - t.a) });
}

// WCAG 2.x relative luminance and contrast ratio (the standard, not the library's own tone math).
function luminance(hex) {
  const { r, g, b } = parseHex(hex);
  const lin = (v) => {
    const s = v / 255;
    return s <= 0.04045 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
  };
  return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
}

// `backdrop` is what a translucent background sits on (the page's surface in a scheme).
export function contrastRatio(fg, bg, backdrop = '#FFFFFF') {
  const opaqueBg = parseHex(bg).a < 1 ? over(bg, backdrop) : bg;
  const opaqueFg = parseHex(fg).a < 1 ? over(fg, opaqueBg) : fg;
  const [l1, l2] = [luminance(opaqueFg), luminance(opaqueBg)].sort((x, y) => y - x);
  return (l1 + 0.05) / (l2 + 0.05);
}

// --- the scheme -------------------------------------------------------------------------------------------

const SURFACES = ['surface', 'surfaceDim', 'surfaceBright', 'surfaceContainerLowest', 'surfaceContainerLow',
  'surfaceContainer', 'surfaceContainerHigh', 'surfaceContainerHighest'];

// Pairs a role set must pass: text pairs at 4.5:1 (WCAG body text), UI pairs at 3:1 (M3's minimum for its
// pairs and WCAG 1.4.11 for components). outlineVariant is decorative and is reported, never required.
export function requiredPairs() {
  const pairs = [];
  const text = (fg, bg) => pairs.push({ fg, bg, kind: 'text', min: 4.5 });
  const ui = (fg, bg) => pairs.push({ fg, bg, kind: 'ui', min: 3 });
  for (const c of ['primary', 'secondary', 'tertiary', 'error']) {
    const C = c[0].toUpperCase() + c.slice(1);
    text(`on${C}`, c);
    text(`on${C}Container`, `${c}Container`);
    if (c !== 'error') {
      for (const bg of [`${c}Fixed`, `${c}FixedDim`]) {
        text(`on${C}Fixed`, bg);
        text(`on${C}FixedVariant`, bg);
      }
    }
  }
  for (const bg of SURFACES) {
    text('onSurface', bg);
    text('onSurfaceVariant', bg);
  }
  text('inverseOnSurface', 'inverseSurface');
  text('onBackground', 'background');
  for (const bg of ['surface', 'surfaceContainerLow', 'surfaceContainer', 'surfaceContainerHigh']) ui('primary', bg);
  for (const c of ['secondary', 'tertiary', 'error']) ui(c, 'surface');
  ui('outline', 'surface');
  ui('outline', 'surfaceContainerHighest');
  ui('inversePrimary', 'inverseSurface');
  return pairs;
}

// Build the library's scheme for one mode. `palettes` (optional) replaces a palette with one made from a brand
// color: { secondary: '#1C2897', neutral: '#050829', ... }.
export function buildScheme({ source, variant = 'tonalSpot', contrast = 0, spec = '2021', isDark, palettes = {} }) {
  const Scheme = VARIANTS[variant];
  if (!Scheme) throw new Error(`unknown variant ${variant}; one of ${Object.keys(VARIANTS).join(', ')}`);
  const hct = Hct.fromInt(argbFromHex(source));
  const base = new Scheme(hct, isDark, contrast, spec);
  if (!Object.keys(palettes).length) return base;
  const pal = (key, fallback) => (palettes[key] ? TonalPalette.fromInt(argbFromHex(palettes[key])) : fallback);
  return new DynamicScheme({
    sourceColorHct: hct, variant: base.variant, contrastLevel: contrast, isDark, specVersion: spec,
    platform: 'phone',
    primaryPalette: pal('primary', base.primaryPalette),
    secondaryPalette: pal('secondary', base.secondaryPalette),
    tertiaryPalette: pal('tertiary', base.tertiaryPalette),
    neutralPalette: pal('neutral', base.neutralPalette),
    neutralVariantPalette: pal('neutralVariant', base.neutralVariantPalette),
    errorPalette: pal('error', base.errorPalette),
  });
}

// Which palette and tone the library picked for each role: { primary: 'primary40', surfaceTint: 'primary' }.
export function roleTones(scheme) {
  const names = { primary: scheme.primaryPalette, secondary: scheme.secondaryPalette, tertiary: scheme.tertiaryPalette,
    neutral: scheme.neutralPalette, 'neutral-variant': scheme.neutralVariantPalette, error: scheme.errorPalette };
  const refs = colorRoleRefs('light');
  const out = {};
  for (const role of colorRoles()) {
    if (!/\d$/.test(refs[role])) { out[role] = refs[role]; continue; } // an alias of another role
    const dc = dynamicColor(role);
    const palette = Object.entries(names).find(([, p]) => p === dc.palette(scheme))?.[0] ?? '?';
    out[role] = `${palette}${Math.round(dc.getTone(scheme) * 10) / 10}`;
  }
  return out;
}

// The library's own colors for every role, before any brand locking or adjustment.
export function rawColors(scheme) {
  return Object.fromEntries(colorRoles().map((r) => [r, generatedHex(scheme, r)]));
}

function generatedHex(scheme, role) {
  if (role === 'surfaceTint') return hexFromArgb(dynamicColor('primary').getArgb(scheme)).toUpperCase();
  return hexFromArgb(dynamicColor(role).getArgb(scheme)).toUpperCase();
}

// Move a generated role along its own palette, away from its partner, until every required pair it is in
// passes. Returns the new hex, or null when no tone in the palette passes.
function adjustRole(scheme, role, colors, pairs, ratio) {
  if (role === 'surfaceTint') return null;
  const dc = dynamicColor(role);
  const palette = dc.palette(scheme);
  const start = dc.getTone(scheme);
  const mine = pairs.filter((p) => p.fg === role || p.bg === role);
  const passes = (hex) => mine.every((p) => ratio(p.fg === role ? hex : colors[p.fg], p.bg === role ? hex : colors[p.bg], p.bg) >= p.min + 0.01);
  for (let step = 0.5; step <= 100; step += 0.5) {
    for (const t of [start + step, start - step]) {
      if (t < 0 || t > 100) continue;
      const hex = hexFromArgb(palette.tone(t)).toUpperCase();
      if (passes(hex)) return { hex, from: start, to: t };
    }
  }
  return null;
}

// The nearest color with the same hue and chroma as `hex` that reaches `min` against `against` (for a pair of
// two locked brand colors that fails). Returns null if none.
export function nearestPassing(hex, against, min, backdrop = '#FFFFFF') {
  const h = Hct.fromInt(argbFromHex(hex.slice(0, 7)));
  for (let step = 0.5; step <= 100; step += 0.5) {
    for (const t of [h.tone + step, h.tone - step]) {
      if (t < 0 || t > 100) continue;
      const cand = hexFromArgb(Hct.from(h.hue, h.chroma, t).toInt()).toUpperCase();
      if (contrastRatio(cand, against, backdrop) >= min + 0.01) return { hex: cand, tone: Math.round(t * 10) / 10 };
    }
  }
  return null;
}

// One mode's full role set: { colors, origin: { role: 'locked'|'generated'|'adjusted' }, notes, contrast }.
export function resolveMode({ scheme, locked = {} }) {
  const pairs = requiredPairs();
  const colors = {};
  const origin = {};
  const notes = [];
  for (const role of colorRoles()) {
    if (locked[role]) {
      colors[role] = locked[role].toUpperCase();
      origin[role] = 'locked';
    } else {
      colors[role] = generatedHex(scheme, role);
      origin[role] = 'generated';
    }
  }
  for (const role of Object.keys(locked)) {
    if (!(role in colors)) throw new Error(`unknown color role in locked: ${role}`);
  }
  // A translucent background is measured over what is under it: the page's surface, which itself sits on black in a
  // dark scheme and on white in a light one.
  const base = scheme.isDark ? '#000000' : '#FFFFFF';
  const backdrop = (bgRole) => {
    if (bgRole === 'surface' || bgRole === 'background') return base;
    return parseHex(colors.surface).a < 1 ? over(colors.surface, base) : colors.surface;
  };
  const ratio = (fg, bg, bgRole) => contrastRatio(fg, bg, backdrop(bgRole));
  // Two passes: an adjusted role can change a partner's needs.
  for (let pass = 0; pass < 2; pass += 1) {
    for (const p of pairs) {
      if (ratio(colors[p.fg], colors[p.bg], p.bg) >= p.min) continue;
      for (const role of [p.fg, p.bg]) {
        if (origin[role] === 'locked') continue;
        const fix = adjustRole(scheme, role, colors, pairs, ratio);
        if (fix) {
          colors[role] = fix.hex;
          origin[role] = 'adjusted';
          notes.push(`${role}: tone ${fix.from.toFixed(1)} -> ${fix.to.toFixed(1)} so its pairs pass against the brand's locked colors`);
          break;
        }
      }
    }
  }
  // M3 defines surfaceTint as the primary color: it follows a locked or adjusted primary.
  if (!locked.surfaceTint && colors.surfaceTint !== colors.primary) {
    colors.surfaceTint = colors.primary;
    notes.push(`surfaceTint follows primary (${colors.primary})`);
  }
  const contrast = pairs.map((p) => {
    const r = ratio(colors[p.fg], colors[p.bg], p.bg);
    const row = { ...p, ratio: Math.round(r * 100) / 100, pass: r >= p.min };
    if (!row.pass && origin[p.fg] === 'locked' && origin[p.bg] === 'locked') {
      row.brandLocked = true;
      row.suggestion = nearestPassing(colors[p.fg], colors[p.bg], p.min, backdrop(p.bg));
    }
    return row;
  });
  const decorative = { fg: 'outlineVariant', bg: 'surface', ratio: Math.round(ratio(colors.outlineVariant, colors.surface, 'surface') * 100) / 100 };
  return { colors, origin, notes, contrast, decorative };
}
