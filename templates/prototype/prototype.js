// The prototype's router and viewer. Screens are <section class="screen" data-screen="name"> inside #app.
// Go to a screen with <a href="#name"> or any element with data-go="name"; pick the move with
// data-transition="forward" | "backward" | "top-level" | "fade" (M3 transition patterns). Open a dialog or a
// snackbar with data-open="id"; close a dialog with data-close. Motion values come from tokens.css; with reduced
// motion every move becomes a short crossfade without movement.
(() => {
  const root = document.documentElement;
  const app = document.getElementById('app');
  const stage = document.querySelector('.proto-stage');
  const screens = [...app.querySelectorAll('.screen')];
  const byName = new Map(screens.map((s) => [s.dataset.screen, s]));
  const params = new URLSearchParams(location.search);
  const css = (name) => getComputedStyle(root).getPropertyValue(name).trim();
  const ms = (name, fallback) => Number.parseFloat(css(name)) || fallback;
  const reduced = () => root.hasAttribute('data-reduced-motion') || matchMedia('(prefers-reduced-motion: reduce)').matches;
  const log = [];
  let current = null;
  let lastFocus = null;

  // Navigation transitions run on M3's easing and duration tokens (Google has not moved them to springs; no bounce
  // in frequent moves). Durations and curves follow Material Components' own transition classes.
  const easing = (name, fallback) => css(`--md-sys-motion-easing-${name}`) || fallback;
  const dur = (name, fallback) => ms(`--md-sys-motion-duration-${name}`, fallback);

  function markNav(name) {
    for (const el of app.querySelectorAll('[data-nav]')) {
      if (el.dataset.nav === name || (byName.get(name)?.dataset.section === el.dataset.nav)) el.setAttribute('aria-current', 'page');
      else el.removeAttribute('aria-current');
    }
  }

  function show(name, kind = 'fade', { instant = false } = {}) {
    const next = byName.get(name);
    if (!next || next === current) return;
    const prev = current;
    current = next;
    next.hidden = false;
    next.scrollTop = 0;
    markNav(name);
    const pick = document.querySelector('.proto-bar [name=screen]');
    if (pick) pick.value = name;  // the viewer's screen menu follows every move
    if (location.hash.slice(1) !== name) history.replaceState(null, '', `${location.pathname}${location.search}#${name}`);
    if (!prev || instant) {
      for (const s of screens) s.hidden = s !== next;
      return;
    }
    run(prev, next, kind);
  }

  function run(prev, next, kind) {
    prev.style.zIndex = '0';
    next.style.zIndex = '1';
    const anims = [];
    const T = dur('long1', 450);
    const ease = easing('emphasized', 'cubic-bezier(0.2, 0, 0, 1)');
    const out = Math.round(T * 0.35); // the old screen fades out over the first 35%, the new one fades in after
    if (reduced()) {
      // Reduced motion: a short, subtle fade; no slide, no scale.
      anims.push(next.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 100, easing: 'linear' }));
      log.push({ kind, reduced: true, transform: false });
    } else if (kind === 'forward' || kind === 'backward') {
      // Forward and backward (shared axis X): a 30 px slide with a fade, 450 ms, Emphasized.
      const d = kind === 'forward' ? 1 : -1;
      anims.push(prev.animate([{ transform: 'translateX(0)' }, { transform: `translateX(${-30 * d}px)` }], { duration: T, easing: ease, fill: 'forwards' }));
      anims.push(prev.animate([{ opacity: 1 }, { opacity: 0 }], { duration: out, easing: 'linear', fill: 'forwards' }));
      anims.push(next.animate([{ transform: `translateX(${30 * d}px)` }, { transform: 'translateX(0)' }], { duration: T, easing: ease }));
      anims.push(next.animate([{ opacity: 0 }, { opacity: 1 }], { duration: T - out, delay: out, easing: 'linear', fill: 'backwards' }));
      log.push({ kind, reduced: false, transform: true });
    } else if (kind === 'top-level') {
      // Top level (fade through): out over the first 35%, then in while growing from 92%.
      anims.push(prev.animate([{ opacity: 1 }, { opacity: 0 }], { duration: out, easing: 'linear', fill: 'forwards' }));
      anims.push(next.animate([{ opacity: 0, transform: 'scale(0.92)' }, { opacity: 1, transform: 'scale(1)' }], { duration: T - out, delay: out, easing: ease, fill: 'backwards' }));
      log.push({ kind, reduced: false, transform: true });
    } else {
      anims.push(prev.animate([{ opacity: 1 }, { opacity: 0 }], { duration: dur('short3', 150), easing: 'linear', fill: 'forwards' }));
      anims.push(next.animate([{ opacity: 0 }, { opacity: 1 }], { duration: dur('medium1', 250), easing: 'linear' }));
      log.push({ kind, reduced: false, transform: false });
    }
    Promise.allSettled(anims.map((a) => a.finished)).then(() => {
      if (current !== prev) prev.hidden = true;
      for (const a of anims) a.cancel();
      prev.style.zIndex = '';
      next.style.zIndex = '';
    });
  }

  // While a modal layer is open, everything else in the window and the viewer's bar is inert: Tab and the pointer
  // reach the dialog only. Restored when it closes.
  let inerted = [];
  function setInert(layer, on) {
    if (on) {
      const app = layer.closest('#app') ?? document.body;
      inerted = [...app.children, document.querySelector('.proto-bar')]
        .filter((n) => n && n !== layer && !n.contains(layer) && !n.inert);
      for (const n of inerted) n.inert = true;
    } else {
      for (const n of inerted) n.inert = false;
      inerted = [];
    }
  }

  // Single-select segmented buttons (a group with data-multi keeps several), and tabs with the arrow keys.
  function selectTab(tab) {
    const list = tab.closest('[role=tablist]');
    for (const t of list.querySelectorAll('[role=tab]')) {
      const on = t === tab;
      t.setAttribute('aria-selected', String(on));
      t.tabIndex = on ? 0 : -1;
      const panel = t.getAttribute('aria-controls') && document.getElementById(t.getAttribute('aria-controls'));
      if (panel) panel.hidden = !on;
    }
  }
  for (const list of document.querySelectorAll('[role=tablist]')) {
    const sel = list.querySelector('[role=tab][aria-selected=true]') ?? list.querySelector('[role=tab]');
    if (sel) selectTab(sel);
  }

  function open(id, opener) {
    const el = document.getElementById(id);
    if (!el) return;
    if (el.classList.contains('md-snackbar')) {
      el.hidden = false;
      // Enter: rises from the bottom edge it is nearest to, Emphasized decelerate.
      if (!reduced()) el.animate([{ opacity: 0, transform: 'translateY(16px)' }, { opacity: 1, transform: 'none' }], { duration: dur('medium4', 400), easing: easing('emphasized-decelerate', 'ease-out') });
      clearTimeout(el._timer);
      el._timer = setTimeout(() => { el.hidden = true; }, 6000);
      return;
    }
    lastFocus = opener;
    el.hidden = false;
    setInert(el, true);
    const box = el.querySelector('.md-dialog, .md-sheet') ?? el;
    if (!reduced()) {
      // Enter (Material Components' MaterialFade): 400 ms Emphasized decelerate, from 80% scale.
      const enter = { duration: dur('medium4', 400), easing: easing('emphasized-decelerate', 'ease-out') };
      el.animate([{ opacity: 0 }, { opacity: 1 }], { duration: dur('short3', 150), easing: 'linear' });
      box.animate([{ opacity: 0, transform: 'scale(0.8)' }, { opacity: 1, transform: 'none' }], enter);
    }
    (box.querySelector('[autofocus], button, a, input, [tabindex="0"]') ?? box).focus();
  }

  function close(el) {
    const layer = el.closest('.md-scrim, .proto-dialog') ?? el;
    layer.hidden = true;
    setInert(layer, false);
    lastFocus?.focus();
  }

  document.addEventListener('click', (ev) => {
    const go = ev.target.closest('[data-go], a[href^="#"]');
    const opener = ev.target.closest('[data-open]');
    const closer = ev.target.closest('[data-close]');
    if (opener) { ev.preventDefault(); open(opener.dataset.open, opener); return; }
    if (closer) { ev.preventDefault(); close(closer); return; }
    if (ev.target.classList?.contains('md-scrim')) { close(ev.target); return; }
    const seg = ev.target.closest('.md-segmented__button');
    if (seg) {
      const group = seg.closest('.md-segmented');
      if (group?.hasAttribute('data-multi')) seg.setAttribute('aria-pressed', String(seg.getAttribute('aria-pressed') !== 'true'));
      else for (const b of (group ?? seg.parentElement).querySelectorAll('.md-segmented__button')) b.setAttribute('aria-pressed', String(b === seg));
    }
    const tab = ev.target.closest('[role=tab]');
    if (tab) selectTab(tab);
    if (go) {
      const name = go.dataset.go ?? go.getAttribute('href').slice(1);
      if (!byName.has(name)) return;
      ev.preventDefault();
      show(name, go.dataset.transition ?? 'fade');
    }
  });
  document.addEventListener('keydown', (ev) => {
    const tab = ev.target.closest?.('[role=tab]');
    if (tab && ['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(ev.key)) {
      const tabs = [...tab.closest('[role=tablist]').querySelectorAll('[role=tab]')];
      const i = tabs.indexOf(tab);
      const rtl = getComputedStyle(tab).direction === 'rtl';
      const step = (ev.key === 'ArrowRight') !== rtl ? 1 : -1;
      const next = ev.key === 'Home' ? tabs[0] : ev.key === 'End' ? tabs.at(-1) : tabs[(i + step + tabs.length) % tabs.length];
      ev.preventDefault();
      selectTab(next);
      next.focus();
      return;
    }
    if (ev.key !== 'Escape') return;
    const openLayer = [...document.querySelectorAll('.md-scrim')].find((s) => !s.hidden);
    if (openLayer) close(openLayer);
  });
  // A top app bar takes the scrolled color once its screen scrolls.
  for (const s of screens) {
    s.addEventListener('scroll', () => {
      for (const bar of s.querySelectorAll('.md-top-app-bar')) bar.dataset.scrolled = String(s.scrollTop > 0);
    }, { passive: true });
  }

  // --- the viewer -------------------------------------------------------------------------------------------
  const bar = document.querySelector('.proto-bar');
  const frameSel = bar?.querySelector('[name=frame]');
  const themeSel = bar?.querySelector('[name=theme]');
  const motionSel = bar?.querySelector('[name=motion]');
  const screenSel = bar?.querySelector('[name=screen]');
  const small = matchMedia('(max-width: 599px)').matches;

  function setFrame(f) { stage.dataset.frame = f; if (frameSel) frameSel.value = f; }
  function setTheme(t) {
    if (t === 'system') root.removeAttribute('data-theme'); else root.dataset.theme = t;
    if (themeSel) themeSel.value = t;
  }
  function setMotion(m) {
    if (m === 'reduced') root.setAttribute('data-reduced-motion', ''); else root.removeAttribute('data-reduced-motion');
    if (motionSel) motionSel.value = m;
  }
  if (screenSel) {
    for (const s of screens) screenSel.add(new Option(s.dataset.title ?? s.dataset.screen, s.dataset.screen));
    screenSel.addEventListener('change', () => show(screenSel.value, 'fade'));
  }
  frameSel?.addEventListener('change', () => setFrame(frameSel.value));
  themeSel?.addEventListener('change', () => setTheme(themeSel.value));
  motionSel?.addEventListener('change', () => setMotion(motionSel.value));

  setFrame(params.get('frame') ?? (small ? 'full' : 'phone'));
  setTheme(params.get('theme') ?? 'system');
  setMotion(params.get('motion') ?? 'normal');
  if (params.get('chrome') === '0' && bar) bar.hidden = true;
  show(location.hash.slice(1) || params.get('screen') || screens[0]?.dataset.screen, 'fade', { instant: true });
  window.addEventListener('hashchange', () => show(location.hash.slice(1), 'fade'));
  window.addEventListener('popstate', () => show(location.hash.slice(1), 'fade'));
  window.m3proto = { show, open, current: () => current?.dataset.screen, screens: () => [...byName.keys()], log };
})();
