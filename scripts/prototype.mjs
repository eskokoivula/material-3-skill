#!/usr/bin/env node
// Assemble a clickable prototype folder: the template (viewer, router, example screens), m3.css, and the
// project's tokens.css. Re-running refreshes tokens.css, m3.css and the viewer files but keeps an existing
// index.html (the project's own screens) unless --force is given.
// Usage: node scripts/prototype.mjs <config.json> --out <dir> [--force]
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildTokens } from './tokens.mjs';
import { toCss, toReport } from './lib/emit.mjs';

const SKILL = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

export function assemble(config, out, { force = false } = {}) {
  fs.mkdirSync(out, { recursive: true });
  const tokens = buildTokens(config);
  fs.writeFileSync(path.join(out, 'tokens.css'), toCss(tokens));
  fs.writeFileSync(path.join(out, 'tokens-report.md'), toReport(tokens));
  fs.copyFileSync(path.join(SKILL, 'templates/m3.css'), path.join(out, 'm3.css'));
  for (const f of ['prototype.css', 'prototype.js']) fs.copyFileSync(path.join(SKILL, 'templates/prototype', f), path.join(out, f));
  const index = path.join(out, 'index.html');
  if (force || !fs.existsSync(index)) fs.copyFileSync(path.join(SKILL, 'templates/prototype/index.html'), index);
  return tokens;
}

function main(argv) {
  const outIdx = argv.indexOf('--out');
  if (!argv[0] || outIdx < 0) {
    console.error('usage: node scripts/prototype.mjs <config.json> --out <dir> [--force]');
    return 2;
  }
  const config = JSON.parse(fs.readFileSync(argv[0], 'utf8'));
  const out = argv[outIdx + 1];
  assemble(config, out, { force: argv.includes('--force') });
  console.log(`prototype in ${out}: index.html, tokens.css, m3.css, prototype.css, prototype.js`);
  return 0;
}

if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) process.exitCode = main(process.argv.slice(2));
