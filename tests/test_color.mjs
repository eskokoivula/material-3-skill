// Checks 1-3: the color engine against Google's own values. Prints one line per check: "CHECK <n> PASS|FAIL <detail>".
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildScheme, rawColors, resolveMode, roleTones } from '../scripts/lib/color.mjs';
import { colorRoleRefs, TYPE_ROLES, typescale, webLatestTypescale } from '../scripts/lib/google.mjs';
import { buildTokens } from '../scripts/tokens.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const report = (n, ok, detail) => console.log(`CHECK ${n} ${ok ? 'PASS' : 'FAIL'} ${detail}`);

// 1. Every role maps to the palette and tone Google's token database names (baseline seed, 2021 spec).
{
  const bad = [];
  let total = 0;
  for (const mode of ['light', 'dark']) {
    const tones = roleTones(buildScheme({ source: '#6750A4', isDark: mode === 'dark' }));
    for (const [role, ref] of Object.entries(colorRoleRefs(mode))) {
      total += 1;
      if (tones[role] !== ref) bad.push(`${mode} ${role}: google ${ref}, ours ${tones[role]}`);
    }
  }
  report(1, bad.length === 0, `${total - bad.length}/${total} roles map to Google's palette and tone${bad.length ? `; ${bad.slice(0, 5).join('; ')}` : ''}`);
}

// 2. Exact hex values equal Flutter's own ColorScheme.fromSeed (Google's Dart implementation).
{
  const ref = JSON.parse(fs.readFileSync(path.join(HERE, 'fixtures/flutter-fromseed.json'), 'utf8'));
  let same = 0;
  const bad = [];
  for (const r of ref) {
    const ours = rawColors(buildScheme({ source: r.seed, variant: r.variant, contrast: r.contrast, isDark: r.mode === 'dark' }));
    for (const [role, hex] of Object.entries(r.colors)) {
      if (ours[role] === hex) same += 1;
      else bad.push(`${r.seed} ${r.variant} ${r.mode} c${r.contrast} ${role}: flutter ${hex}, ours ${ours[role]}`);
    }
  }
  const seeds = new Set(ref.map((r) => r.seed)).size;
  const variants = new Set(ref.map((r) => r.variant)).size;
  report(2, bad.length === 0, `${same}/${same + bad.length} colors equal Flutter's fromSeed (${seeds} seeds, ${variants} variants, both modes, contrast 0/0.5/1)${bad.length ? `; ${bad.slice(0, 3).join('; ')}` : ''}`);
}

// 3. The sample brand's locked colors stay exact; every pair with a generated side passes; failures are brand-locked only.
{
  const config = JSON.parse(fs.readFileSync(path.join(HERE, 'fixtures/sample-app/brand.tokens.json'), 'utf8'));
  const t = buildTokens(config);
  const dark = t.color.dark;
  const locked = config.locked.dark;
  const notExact = Object.entries(locked).filter(([r, hex]) => dark.colors[r] !== hex.toUpperCase()).map(([r]) => r);
  const fails = dark.contrast.filter((c) => !c.pass);
  const generatedFails = fails.filter((c) => !c.brandLocked);
  const noSuggestion = fails.filter((c) => c.brandLocked && !c.suggestion);
  const ok = notExact.length === 0 && generatedFails.length === 0 && noSuggestion.length === 0;
  report(3, ok, `${Object.keys(locked).length - notExact.length}/${Object.keys(locked).length} locked colors exact; ${dark.contrast.length - fails.length}/${dark.contrast.length} pairs pass; ${fails.length} brand-locked failures, each with a nearest passing tone${generatedFails.length ? `; generated failures: ${generatedFails.map((c) => `${c.fg}/${c.bg}`).join(', ')}` : ''}${notExact.length ? `; not exact: ${notExact.join(', ')}` : ''}`);
}

// Not a numbered check: unlocked schemes never need adjusting (the pair rules agree with the library).
{
  const ref = JSON.parse(fs.readFileSync(path.join(HERE, 'fixtures/flutter-fromseed.json'), 'utf8'));
  const adjusted = ref.reduce((n, r) => n + Object.values(resolveMode({ scheme: buildScheme({ source: r.seed, variant: r.variant, contrast: r.contrast, isDark: r.mode === 'dark' }) }).origin).filter((o) => o !== 'generated').length, 0);
  console.log(`INFO unlocked schemes adjusted roles: ${adjusted}`);
}

// Not a numbered check: Google's two newest type-scale sources agree (Flutter v6.1.0 and Material Web v34).
{
  const a = typescale();
  const b = webLatestTypescale('_md-sys-typescale.scss');
  const keys = ['size', 'lineHeight', 'tracking', 'weight'];
  const off = TYPE_ROLES.flatMap((r) => keys.filter((k) => Math.abs(a[r][k] - b[r][k]) > 0.001).map((k) => `${r}.${k}`));
  console.log(`INFO type scale: Flutter v6.1.0 and Material Web v34 agree on ${TYPE_ROLES.length * keys.length - off.length}/${TYPE_ROLES.length * keys.length} values${off.length ? `; differ: ${off.join(', ')}` : ''}`);
}
