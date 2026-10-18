#!/usr/bin/env node
// Material 3 tokens for a project, brand first.
// Usage: node scripts/tokens.mjs <config.json> --out <dir>
// Colors come from Google's color library; type, shape, elevation, state and motion values come from Google's
// token files in tests/fixtures/google. The config format is documented in references/brand-first.md.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildScheme, resolveMode } from './lib/color.mjs';
import { springToCss } from './lib/spring.mjs';
import { emphasizedLinear } from './lib/easing.mjs';
import {
  easingAndDuration, elevationLevels, focusIndicator, manifest, shapeScale, springs, stateOpacities, typeface, typescale,
  webLatestTypescale,
} from './lib/google.mjs';
import { toCss, toDart, toReport } from './lib/emit.mjs';

const FALLBACK = 'system-ui, -apple-system, "Segoe UI", sans-serif';
const stack = (family) => (family ? `"${family}", ${FALLBACK}` : FALLBACK);
// The local date: a file generated at 01:00 in Helsinki says today, not yesterday.
const today = () => {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
};

export function buildTokens(config) {
  const modes = config.modes ?? ['light', 'dark'];
  const firstLockedPrimary = Object.values(config.locked ?? {}).map((m) => m.primary).find(Boolean);
  const source = (config.source ?? firstLockedPrimary ?? '#6750A4').slice(0, 7);
  const base = {
    source, variant: config.variant ?? 'tonalSpot', contrast: config.contrast ?? 0, spec: config.spec ?? '2021',
    palettes: config.palettes ?? {},
  };
  const color = {};
  for (const mode of ['light', 'dark']) {
    if (!modes.includes(mode)) { color[mode] = null; continue; }
    const scheme = buildScheme({ ...base, isDark: mode === 'dark' });
    color[mode] = resolveMode({ scheme, locked: config.locked?.[mode] ?? {} });
  }
  const google = typeface();
  const faces = {
    brand: config.type?.brand ?? google.brand,
    plain: config.type?.plain ?? config.type?.brand ?? google.plain,
    weights: { ...google.weights, ...(config.type?.weights ?? {}) },
  };
  const baseline = typescale();
  // Emphasized styles from Material Web's newest generated set: the baseline values with a heavier weight. A variable
  // face takes them from the wght axis, as M3 specifies (600 where static fonts use 700).
  const emphasized = webLatestTypescale('_md-sys-typescale-emphasized.scss');
  const variable = config.type?.variable === true;
  if (variable) for (const s of Object.values(emphasized)) s.weight = s.wght;
  // The brand's weights replace Google's regular, medium and bold (400, 500, 700) in every style.
  const weightOf = { [google.weights.regular]: faces.weights.regular, [google.weights.medium]: faces.weights.medium,
    [google.weights.bold]: faces.weights.bold };
  for (const set of [baseline, emphasized]) {
    for (const s of Object.values(set)) {
      s.weight = weightOf[s.weight] ?? s.weight;
      if (s.wght !== undefined) s.wght = weightOf[s.wght] ?? s.wght;
    }
  }
  const typeOverrides = Object.entries(config.type?.scale ?? {});
  for (const [role, v] of typeOverrides) {
    if (!(role in baseline)) throw new Error(`unknown type role ${role}; one of ${Object.keys(baseline).join(', ')}`);
    for (const key of Object.keys(v)) {
      if (!['size', 'lineHeight', 'tracking'].includes(key)) throw new Error(`type.scale.${role}.${key}: only size, lineHeight and tracking`);
    }
    Object.assign(baseline[role], v);
    Object.assign(emphasized[role], v);
  }
  const scale = shapeScale();
  const overrides = Object.entries(config.shape ?? {});
  for (const [step, val] of overrides) {
    if (!(step in scale)) throw new Error(`unknown corner step ${step}; one of ${Object.keys(scale).join(', ')}`);
    scale[step] = val;
  }
  const motionScheme = config.motion ?? 'standard';
  const springSet = springs();
  for (const set of Object.values(springSet)) for (const s of Object.values(set)) s.css = springToCss(s.stiffness, s.damping);
  return {
    meta: { name: config.name ?? 'project', generated: today(), ...base,
      google: manifest().sources },
    color,
    typeface: { ...faces, brandStack: stack(faces.brand), plainStack: stack(faces.plain) },
    typescale: { baseline, emphasized, variable, overrides: typeOverrides },
    shape: { scale, overridden: overrides.length > 0, overrides },
    elevation: elevationLevels(),
    state: stateOpacities(),
    focus: focusIndicator(),
    motion: (() => {
      const ed = easingAndDuration();
      // The token files carry a cubic-bezier stand-in for Emphasized; keep it, and give the real path as linear().
      ed.easing['emphasized-cubic-stand-in'] = ed.easing.emphasized;
      ed.easing.emphasized = emphasizedLinear();
      return { scheme: motionScheme, springs: springSet, ...ed };
    })(),
  };
}

function main(argv) {
  const configPath = argv[0];
  const outIdx = argv.indexOf('--out');
  if (!configPath || outIdx < 0) {
    console.error('usage: node scripts/tokens.mjs <config.json> --out <dir>');
    return 2;
  }
  const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  const tokens = buildTokens(config);
  const out = argv[outIdx + 1];
  fs.mkdirSync(out, { recursive: true });
  fs.writeFileSync(path.join(out, 'tokens.json'), `${JSON.stringify(tokens, null, 1)}\n`);
  fs.writeFileSync(path.join(out, 'tokens.css'), toCss(tokens));
  fs.writeFileSync(path.join(out, 'm3_tokens.dart'), toDart(tokens));
  fs.writeFileSync(path.join(out, 'report.md'), toReport(tokens));
  const fails = Object.values(tokens.color).filter(Boolean).flatMap((m) => m.contrast.filter((c) => !c.pass));
  console.log(`wrote ${out}/tokens.{json,css} m3_tokens.dart report.md; failing pairs: ${fails.length}`);
  return 0;
}

if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) {
  process.exitCode = main(process.argv.slice(2));
}
