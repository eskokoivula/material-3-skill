// A damped spring (mass 1) moving from 0 to 1 from rest, as M3's motion physics defines it by stiffness and
// damping ratio, sampled into a CSS linear() easing plus the duration it needs to settle.

export function springPosition(stiffness, damping, t) {
  const w0 = Math.sqrt(stiffness);
  if (damping < 1) {
    const wd = w0 * Math.sqrt(1 - damping * damping);
    return 1 - Math.exp(-damping * w0 * t) * (Math.cos(wd * t) + ((damping * w0) / wd) * Math.sin(wd * t));
  }
  if (damping === 1) return 1 - (1 + w0 * t) * Math.exp(-w0 * t);
  const r1 = -w0 * (damping - Math.sqrt(damping * damping - 1));
  const r2 = -w0 * (damping + Math.sqrt(damping * damping - 1));
  // x(t) = 1 + c1 e^{r1 t} + c2 e^{r2 t}, with x(0) = 0 and x'(0) = 0.
  const c2 = r1 / (r2 - r1);
  const c1 = -1 - c2;
  return 1 + c1 * Math.exp(r1 * t) + c2 * Math.exp(r2 * t);
}

// The time after which the spring stays within `epsilon` of its target (seconds).
export function settleTime(stiffness, damping, epsilon = 0.001) {
  const dt = 0.0005;
  let last = 0;
  for (let t = 0; t < 10; t += dt) if (Math.abs(springPosition(stiffness, damping, t) - 1) >= epsilon) last = t;
  return last + dt;
}

// { duration (ms, rounded up to 10), easing: 'linear(...)', overshoot (fraction past the target) }.
export function springToCss(stiffness, damping, { points = 48, epsilon = 0.001 } = {}) {
  const total = settleTime(stiffness, damping, epsilon);
  const duration = Math.ceil((total * 1000) / 10) * 10;
  const samples = [];
  let peak = 1;
  for (let i = 0; i <= points; i += 1) {
    const t = (i / points) * (duration / 1000);
    const x = i === points ? 1 : springPosition(stiffness, damping, t);
    peak = Math.max(peak, x);
    samples.push(Number(x.toFixed(4)));
  }
  return { duration, easing: `linear(${samples.join(', ')})`, overshoot: Number((peak - 1).toFixed(4)) };
}
