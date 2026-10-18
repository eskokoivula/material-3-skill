// M3's Emphasized easing is a two-segment path that no single cubic-bezier matches (the web token files use
// cubic-bezier(0.2, 0, 0, 1) as a stand-in, off by up to 16% of the travel). Sample the path into CSS linear().
// The path is Android's: M 0,0 C 0.05,0 0.133333,0.06 0.166666,0.4 C 0.208333,0.82 0.25,1 1,1.
const SEGMENTS = [
  [[0, 0], [0.05, 0], [0.133333, 0.06], [0.166666, 0.4]],
  [[0.166666, 0.4], [0.208333, 0.82], [0.25, 1], [1, 1]],
];

const bez = (p0, p1, p2, p3, t) => {
  const u = 1 - t;
  return u * u * u * p0 + 3 * u * u * t * p1 + 3 * u * t * t * p2 + t * t * t * p3;
};

// y at time x along the path (x grows with t on both segments, so bisection works).
export function emphasizedAt(x) {
  const seg = x <= SEGMENTS[0][3][0] ? SEGMENTS[0] : SEGMENTS[1];
  let lo = 0;
  let hi = 1;
  for (let i = 0; i < 60; i += 1) {
    const mid = (lo + hi) / 2;
    if (bez(seg[0][0], seg[1][0], seg[2][0], seg[3][0], mid) < x) lo = mid; else hi = mid;
  }
  const t = (lo + hi) / 2;
  return bez(seg[0][1], seg[1][1], seg[2][1], seg[3][1], t);
}

// linear() with only the points needed to stay within `tolerance` of the path.
export function emphasizedLinear(tolerance = 0.002) {
  const n = 2000;
  const pts = Array.from({ length: n + 1 }, (_, i) => [i / n, i === n ? 1 : emphasizedAt(i / n)]);
  const keep = [pts[0]];
  let start = 0;
  for (let end = 2; end <= n; end += 1) {
    const [x0, y0] = pts[start];
    const [x1, y1] = pts[end];
    const ok = pts.slice(start + 1, end).every(([x, y]) => Math.abs(y0 + ((y1 - y0) * (x - x0)) / (x1 - x0) - y) <= tolerance);
    if (!ok) {
      keep.push(pts[end - 1]);
      start = end - 1;
    }
  }
  keep.push(pts[n]);
  const fmt = ([x, y], i) => (i === 0 || i === keep.length - 1 ? `${Number(y.toFixed(4))}` : `${Number(y.toFixed(4))} ${Number((x * 100).toFixed(2))}%`);
  return `linear(${keep.map(fmt).join(', ')})`;
}
