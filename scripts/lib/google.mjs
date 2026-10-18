// Readers for Google's token files in tests/fixtures/google (see its manifest.json for commits and dates).
// flutter/: the baseline M3 token database (v6.1.0); compose/: the only source with Expressive values;
// web/: Material Web's md-sys-* tokens.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const GOOGLE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../tests/fixtures/google');
const read = (f) => fs.readFileSync(path.join(GOOGLE, f), 'utf8');
const json = (f) => JSON.parse(read(f));
export const camel = (s) => s.replace(/-([a-z])/g, (_, c) => c.toUpperCase());
export const kebab = (s) => s.replace(/[A-Z]/g, (c) => `-${c.toLowerCase()}`);

export const TYPE_ROLES = ['display', 'headline', 'title', 'body', 'label']
  .flatMap((g) => ['large', 'medium', 'small'].map((s) => `${g}-${s}`));

export function manifest() {
  return json('manifest.json');
}

// Every color role in Google's list, in its order, camelCase: { primary: 'primary40', ... }.
// A role that points at another role (surface-tint -> primary) maps to that role's name with no tone.
export function colorRoleRefs(mode) {
  const data = json(`flutter/color_${mode}.json`);
  const out = {};
  for (const [k, v] of Object.entries(data)) {
    if (!k.startsWith('md.sys.color.')) continue;
    out[camel(k.slice('md.sys.color.'.length))] = String(v).replace('md.ref.palette.', '').replace('md.sys.color.', '');
  }
  return out;
}

export function colorRoles() {
  return Object.keys(colorRoleRefs('light'));
}

// Roles Google lists but marks for retirement in Flutter (kept in JSON and CSS, left out of Dart).
export const LEGACY_ROLES = ['background', 'onBackground', 'surfaceVariant'];

export function typeface() {
  const t = json('flutter/typeface.json');
  return {
    brand: t['md.ref.typeface.brand'],
    plain: t['md.ref.typeface.plain'],
    weights: {
      regular: t['md.ref.typeface.weight-regular'],
      medium: t['md.ref.typeface.weight-medium'],
      bold: t['md.ref.typeface.weight-bold'],
    },
  };
}

const WEIGHT_REF = { 'weight-regular': 'regular', 'weight-medium': 'medium', 'weight-bold': 'bold' };

// The 15 baseline type roles: { 'body-large': { face: 'plain', size, lineHeight, tracking, weight: 'regular' } }.
export function typescale() {
  const t = json('flutter/text_style.json');
  const faces = typeface();
  const out = {};
  for (const role of TYPE_ROLES) {
    const p = `md.sys.typescale.${role}`;
    const weightRef = WEIGHT_REF[t[`${p}.weight`].replace('md.ref.typeface.', '')];
    out[role] = {
      face: t[`${p}.font`].replace('md.ref.typeface.', ''),
      size: t[`${p}.size`],
      lineHeight: t[`${p}.line-height`],
      tracking: t[`${p}.tracking`],
      weight: faces.weights[weightRef],
    };
  }
  return out;
}

const KOTLIN_WEIGHT = { WeightRegular: 'regular', WeightMedium: 'medium', WeightBold: 'bold' };
const pascalToKebab = (s) => s.replace(/([a-z])([A-Z])/g, '$1-$2').toLowerCase();

// Compose's type roles. `emphasized` true gives M3 Expressive's emphasized styles. Compose marks those values
// as hand-written until generated tokens exist ("TODO update with the generated tokens once available").
export function composeTypescale({ emphasized }) {
  const src = read('compose/TypeScaleTokens.kt');
  const faces = typeface();
  const re = /inline val (\w+?)(Emphasized)?(Font|LineHeight|Size|Tracking|Weight):[^\n]*\n\s*get\(\) = ([^\n]+)/g;
  const out = {};
  for (const m of src.matchAll(re)) {
    if (Boolean(m[2]) !== emphasized) continue;
    const role = pascalToKebab(m[1]);
    const r = (out[role] ??= {});
    const v = m[4].trim();
    if (m[3] === 'Font') r.face = v.endsWith('Brand') ? 'brand' : 'plain';
    else if (m[3] === 'Weight') r.weight = faces.weights[KOTLIN_WEIGHT[v.replace('TypefaceTokens.', '')]];
    else r[{ LineHeight: 'lineHeight', Size: 'size', Tracking: 'tracking' }[m[3]]] = Number.parseFloat(v);
  }
  return out;
}

// Material Web's newest generated set (tokens/versions/latest/sass, Version 34): one style per role, values in rem.
// `file` is _md-sys-typescale.scss (baseline) or _md-sys-typescale-emphasized.scss (M3 Expressive). Weights resolve
// through md-ref-typeface; `wght` is the variable-font axis value, which differs for the bold emphasized styles.
export function webLatestTypescale(file) {
  const src = read(`web-latest/${file}`);
  const faces = typeface();
  const val = (role, prop) => src.match(new RegExp(`^\\$${role}-${prop}:\\s*([^;]+);`, 'm'))?.[1].trim();
  const out = {};
  for (const role of TYPE_ROLES) {
    const rem = (v) => Number.parseFloat(v) * 16;
    const weightRef = val(role, 'weight')?.match(/weight-(regular|medium|bold)/)?.[1];
    out[role] = {
      face: /brand/.test(val(role, 'font') ?? '') ? 'brand' : 'plain',
      size: rem(val(role, 'size')),
      lineHeight: rem(val(role, 'line-height')),
      tracking: Number((rem(val(role, 'tracking')) ).toFixed(4)),
      weight: faces.weights[weightRef],
      wght: Number(val(role, 'wght')?.match(/(\d+)/)?.[1]) || faces.weights[weightRef],
    };
  }
  return out;
}

export function focusIndicator() {
  const src = read('web-latest/_md-sys-state-focus-indicator.scss');
  const px = (name) => Number.parseFloat(src.match(new RegExp(`^\\$${name}:\\s*([-\\d.]+)px;`, 'm'))?.[1]);
  return { thickness: px('thickness'), outerOffset: px('outer-offset'), innerOffset: px('inner-offset') };
}

// Corner steps in dp, Expressive steps included: { none: 0, 'extra-small': 4, ..., full: 'full' }.
export function shapeScale() {
  const src = read('compose/ShapeTokens.kt');
  const out = {};
  for (const m of src.matchAll(/val CornerValue(\w+) = CornerSize\(([\d.]+)\.dp\)/g)) out[pascalToKebab(m[1])] = Number(m[2]);
  out.full = 'full';
  return out;
}

export function elevationLevels() {
  const e = json('flutter/elevation.json');
  return Object.fromEntries(Object.entries(e).filter(([k]) => k.startsWith('md.sys.elevation.'))
    .map(([k, v]) => [k.replace('md.sys.elevation.', ''), v]));
}

export function stateOpacities() {
  const s = json('flutter/state.json');
  return Object.fromEntries(Object.entries(s).filter(([k]) => k.startsWith('md.sys.state.'))
    .map(([k, v]) => [k.replace('md.sys.state.', '').replace('.state-layer-opacity', ''), v]));
}

// Springs for both motion schemes: { standard: { 'default-spatial': { stiffness, damping } , ... }, expressive: {...} }.
export function springs() {
  const out = {};
  for (const [scheme, file] of [['standard', 'StandardMotionTokens.kt'], ['expressive', 'ExpressiveMotionTokens.kt']]) {
    const src = read(`compose/${file}`);
    const s = (out[scheme] = {});
    for (const m of src.matchAll(/const val Spring(Fast|Default|Slow)(Spatial|Effects)(Damping|Stiffness) = ([\d.]+)f/g)) {
      const key = `${m[1].toLowerCase()}-${m[2].toLowerCase()}`;
      (s[key] ??= {})[m[3].toLowerCase()] = Number(m[4]);
    }
  }
  return out;
}

// The older easing and duration tokens: { easing: { standard: 'cubic-bezier(...)' }, duration: { short1: 50 } }.
export function easingAndDuration() {
  const src = read('web/_md-sys-motion.scss');
  const easing = {};
  const duration = {};
  for (const m of src.matchAll(/'easing-([\w-]+)':\s*if\(\$exclude-hardcoded-values,\s*null,\s*(cubic-bezier\([^)]*\))\)/g)) easing[m[1]] = m[2];
  for (const m of src.matchAll(/'duration-([\w-]+)':\s*if\(\$exclude-hardcoded-values,\s*null,\s*(\d+)ms\)/g)) duration[m[1]] = Number(m[2]);
  return { easing, duration };
}
