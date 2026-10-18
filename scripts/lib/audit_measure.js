// Runs inside the audited page. window.__m3audit.collect(ignoreSelector) returns what the audit measures:
// visible text with its colors, interactive targets with their real hit areas, corner radii, spacing, fonts,
// videos and the page's sideways overflow. The Python side (scripts/audit_web.py) turns this into findings.
(() => {
  const canvas = document.createElement('canvas');
  canvas.width = 1;
  canvas.height = 1;
  const ctx = canvas.getContext('2d', { willReadFrequently: true });

  // Any CSS color (rgb, color(srgb ...), oklch, color-mix results) -> [r, g, b, a] in sRGB bytes and 0..1.
  function rgba(str) {
    if (!str || str === 'transparent') return [0, 0, 0, 0];
    ctx.clearRect(0, 0, 1, 1);
    ctx.fillStyle = '#000';
    ctx.fillStyle = str;
    ctx.fillRect(0, 0, 1, 1);
    const d = ctx.getImageData(0, 0, 1, 1).data;
    return [d[0], d[1], d[2], d[3] / 255];
  }
  const over = (top, bottom) => {
    const a = top[3] + bottom[3] * (1 - top[3]);
    if (a === 0) return [0, 0, 0, 0];
    const c = (i) => (top[i] * top[3] + bottom[i] * bottom[3] * (1 - top[3])) / a;
    return [c(0), c(1), c(2), a];
  };
  const hex = (c) => `#${c.slice(0, 3).map((v) => Math.round(v).toString(16).padStart(2, '0')).join('')}`.toUpperCase();

  function selectorOf(el) {
    if (el.id) return `#${CSS.escape(el.id)}`;
    const parts = [];
    let node = el;
    while (node && node.nodeType === 1 && parts.length < 4) {
      let part = node.tagName.toLowerCase();
      const cls = [...node.classList].filter((c) => !c.startsWith('is-')).slice(0, 2);
      if (cls.length) part += `.${cls.map((c) => CSS.escape(c)).join('.')}`;
      const parent = node.parentElement;
      if (parent) {
        const same = [...parent.children].filter((c) => c.tagName === node.tagName);
        if (same.length > 1) part += `:nth-of-type(${same.indexOf(node) + 1})`;
      }
      parts.unshift(part);
      if (node.id) { parts[0] = `#${CSS.escape(node.id)}`; break; }
      node = parent;
    }
    return parts.join(' > ');
  }

  const rectOf = (r) => ({ x: r.left + scrollX, y: r.top + scrollY, w: r.width, h: r.height });
  const scrollToY = (y) => window.scrollTo({ top: y, left: 0, behavior: 'instant' });
  const visible = (el) => {
    if (!el.getClientRects().length) return false;
    const s = getComputedStyle(el);
    if (s.visibility === 'hidden' || s.display === 'none') return false;
    const r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) return false;
    let n = el;
    while (n && n.nodeType === 1) {
      if (Number(getComputedStyle(n).opacity) === 0) return false;
      n = n.parentElement;
    }
    return true;
  };
  const nameOf = (el) => (el.getAttribute('aria-label') || el.labels?.[0]?.textContent || el.getAttribute('title')
    || el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 40);
  // A fixed element stays put when the page scrolls: the audit never scrolls the page to reach it.
  const inFixed = (el) => {
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) if (getComputedStyle(n).position === 'fixed') return true;
    return false;
  };

  // What the audit leaves out: the caller's selector, its own overlay, inert content, and everything outside an open
  // modal (the page behind a scrim cannot be used, so it is not measured).
  function scopeOf() {
    let modal = null;
    try { modal = document.querySelector('dialog:modal'); } catch (e) { /* no :modal support */ }
    return modal ?? [...document.querySelectorAll('[aria-modal="true"]')].filter(visible).pop() ?? null;
  }
  function makeIgnored(ignoreSelector) {
    const scope = scopeOf();
    const ignored = (el) => !!(ignoreSelector && el.closest(ignoreSelector))
      || !!el.closest('[data-audit-ignore], #__m3audit_overlay, [inert]') || (!!scope && !scope.contains(el));
    return { scope, ignored };
  }

  // The color behind an element: its own and its ancestors' backgrounds composited. Unknown when an image, a video
  // or a gradient is in the stack (the Python side then samples the page with its text hidden).
  // A container drawn by a pseudo-element (an M3 button's ::before inside its 48 px box) counts as background,
  // at its own opacity; a transparent state layer adds nothing.
  function pseudoLayers(n) {
    const out = [];
    const box = n.getBoundingClientRect();
    for (const which of ['::after', '::before']) {
      const p = getComputedStyle(n, which);
      if (!p.content || p.content === 'none' || p.position !== 'absolute') continue;
      // Only a layer that covers most of the element sits behind its text (not a 3 px tab indicator).
      if (Number.parseFloat(p.width) < box.width * 0.5 || Number.parseFloat(p.height) < box.height * 0.5) continue;
      const c = rgba(p.backgroundColor);
      const o = Number(p.opacity);
      if (c[3] > 0 && o > 0) out.push({ color: [c[0], c[1], c[2], c[3] * o], image: p.backgroundImage !== 'none' });
    }
    return out;
  }

  // The elements painted under the middle of the text, top first, as axe-core does. The window scrolls there when the
  // text is below the first screen, so a layer beside it in the DOM (a card's image, a section's video) is found
  // too. The ancestors when the point is clipped away (text in a scrolled container).
  // `r` is the text's box in page coordinates, measured at the top of the page.
  function under(el, r) {
    const cx = r.x - scrollX + r.w / 2;
    const py = r.y + r.h / 2;
    if (cx >= 0 && cx < innerWidth) {
      const top = py < innerHeight ? 0 : py - innerHeight / 2;
      if (Math.abs(scrollY - top) > 0.5) scrollToY(top);
      const stack = document.elementsFromPoint(cx, py - scrollY);
      const i = stack.indexOf(el);
      if (i >= 0) return stack.slice(i);
    }
    const chain = [];
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) chain.push(n);
    return chain;
  }

  const MEDIA = 'img, video, canvas, picture, iframe, object, embed';
  let videoCount = 0;
  const videoId = (v) => {
    if (!v.dataset.m3aVideo) { v.dataset.m3aVideo = String(videoCount); videoCount += 1; }
    return v.dataset.m3aVideo;
  };

  function background(el, r) {
    const layers = [];
    let known = true;
    let video = null;
    for (const n of under(el, r)) {
      if (n !== el && (n instanceof SVGElement || n.matches(MEDIA))) {
        // A picture or a video behind the text: only pixels can tell.
        known = false;
        if (n.tagName === 'VIDEO') video = videoId(n);
        break;
      }
      const s = getComputedStyle(n);
      for (const p of pseudoLayers(n)) {
        if (p.image) known = false;
        layers.push(p.color);
      }
      if (s.backgroundImage && s.backgroundImage !== 'none') known = false;
      const c = rgba(s.backgroundColor);
      if (c[3] > 0) layers.push(c);
      if (c[3] >= 1) break;
    }
    let base = [255, 255, 255, 1];
    for (let i = layers.length - 1; i >= 0; i -= 1) base = over(layers[i], base);
    return { color: base, known, video };
  }

  function opacityChain(el) {
    let o = 1;
    let n = el;
    while (n && n.nodeType === 1) { o *= Number(getComputedStyle(n).opacity); n = n.parentElement; }
    return o;
  }

  const ICON_FONT = /material (symbols|icons)/i;

  function texts(ignored) {
    const items = [];
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const seen = new Set();
    scrollToY(0);
    while (walker.nextNode()) {
      const t = walker.currentNode;
      if (!t.nodeValue.trim()) continue;
      const el = t.parentElement;
      if (!el || seen.has(el) || ignored(el)) continue;
      seen.add(el);
      if (['SCRIPT', 'STYLE', 'NOSCRIPT', 'TITLE', 'OPTION'].includes(el.tagName) || el instanceof SVGElement) continue;
      if (!visible(el)) continue;
      const range = document.createRange();
      range.selectNodeContents(el);
      const tr = range.getBoundingClientRect();
      items.push({ el, rect: rectOf(tr.width ? tr : el.getBoundingClientRect()) });
    }
    const out = items.map(({ el, rect }) => {
      const s = getComputedStyle(el);
      const bg = background(el, rect);
      const c = rgba(s.color);
      const op = opacityChain(el);
      const fg = [c[0], c[1], c[2], c[3] * op];
      return {
        selector: selectorOf(el),
        text: el.textContent.trim().replace(/\s+/g, ' ').slice(0, 60),
        rect,
        fg: hex(over(fg, bg.color)),
        fgRaw: fg,
        bg: hex(bg.color),
        bgKnown: bg.known,
        bgVideo: bg.video,
        size: Number.parseFloat(s.fontSize),
        weight: Number(s.fontWeight),
        lineHeight: s.lineHeight === 'normal' ? null : Number.parseFloat(s.lineHeight),
        family: s.fontFamily.split(',')[0].replace(/["']/g, '').trim(),
        isIcon: ICON_FONT.test(s.fontFamily),
        disabled: !!el.closest(':disabled, [aria-disabled="true"], [inert]'),
        // Under an element with opacity below 1 the text and its background blend as one group: measured from pixels.
        group: op < 1,
      };
    });
    scrollToY(0);
    return out;
  }

  // Controls a pointer uses. A focusable container (a tab panel, a scroll region with tabindex) is not one: it is
  // checked for visible focus, but it is neither a target nor a parent that hides the controls inside it.
  const CONTROLS = 'a[href], button, input:not([type=hidden]), select, textarea, summary, [role=button], [role=link], [role=tab], [role=menuitem], [role=checkbox], [role=switch], [role=radio], [role=option], [role=slider], [role=combobox]';
  const TARGETS = `${CONTROLS}, [tabindex]:not([tabindex="-1"])`;
  const isControl = (el) => el.matches(CONTROLS) || getComputedStyle(el).cursor === 'pointer';
  // The box a person sees and uses: the element, or the label of a visually hidden input (a styled file drop zone).
  const shownOf = (el) => {
    if (visible(el)) return el;
    const label = el.matches('input, select, textarea') ? el.labels?.[0] : null;
    return label && visible(label) ? label : null;
  };

  function union(a, b) {
    const x = Math.min(a.x, b.x);
    const y = Math.min(a.y, b.y);
    return { x, y, w: Math.max(a.x + a.w, b.x + b.w) - x, h: Math.max(a.y + a.h, b.y + b.h) - y };
  }

  function targets(ignored) {
    const out = [];
    for (const el of document.querySelectorAll(TARGETS)) {
      if (ignored(el) || el.matches(':disabled, [aria-disabled="true"]') || !isControl(el)) continue;
      const shown = shownOf(el);
      if (!shown) continue;
      // A control inside another control (an icon inside a button) is not a target of its own.
      if (el.parentElement?.closest(CONTROLS) && !el.matches('input, select, textarea')) continue;
      let box = rectOf(shown.getBoundingClientRect());
      for (const d of shown.querySelectorAll('*')) if (d.getClientRects().length) box = union(box, rectOf(d.getBoundingClientRect()));
      const label = el.labels?.[0];
      if (label && label !== shown && visible(label)) box = union(box, rectOf(label.getBoundingClientRect()));
      const s = getComputedStyle(shown);
      const parentText = [...(shown.parentElement?.childNodes ?? [])].some((n) => n !== shown && n.nodeType === 3 && n.nodeValue.trim());
      el.setAttribute('data-m3a-t', String(out.length));
      out.push({
        i: out.length,
        selector: selectorOf(shown),
        tag: el.tagName.toLowerCase(),
        role: el.getAttribute('role'),
        name: nameOf(el),
        rect: rectOf(shown.getBoundingClientRect()),
        target: box,
        inline: s.display === 'inline' && parentText,
        buttonLike: el.matches('button, [role=button], input[type=submit], input[type=button]') || (el.tagName === 'A' && s.display !== 'inline'),
      });
    }
    return out;
  }

  function radii(ignored) {
    const out = [];
    for (const el of document.querySelectorAll('body *')) {
      if (ignored(el) || !visible(el) || el.matches('input[type=checkbox], input[type=radio]')) continue;
      const s = getComputedStyle(el);
      const hasSurface = rgba(s.backgroundColor)[3] > 0 || Number.parseFloat(s.borderTopWidth) > 0 || s.boxShadow !== 'none';
      if (!hasSurface) continue;
      const r = Number.parseFloat(s.borderTopLeftRadius);
      if (!r && !Number.parseFloat(s.borderBottomRightRadius)) continue;
      const box = el.getBoundingClientRect();
      const pill = r >= Math.min(box.width, box.height) / 2 - 1;
      out.push({ selector: selectorOf(el), radius: pill ? 'full' : Math.round(r * 2) / 2, h: box.height, w: box.width,
        buttonLike: el.matches('button, [role=button], a.md-button, a[class*=button], a[class*=btn]'), rect: rectOf(box) });
    }
    return out;
  }

  function spacing(ignored) {
    const values = new Map();
    for (const el of document.querySelectorAll('body *')) {
      if (ignored(el) || !visible(el)) continue;
      const s = getComputedStyle(el);
      if (!/(flex|grid|block)/.test(s.display)) continue;
      for (const p of ['paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft', 'rowGap', 'columnGap']) {
        const v = Number.parseFloat(s[p]);
        if (!v || v <= 2) continue;
        if (!values.has(v)) values.set(v, { selector: selectorOf(el), rect: rectOf(el.getBoundingClientRect()) });
      }
    }
    return [...values.entries()].map(([v, at]) => ({ value: v, ...at }));
  }

  // SVG icons that carry meaning alone: the only visible content of a control (an icon button). Measured from pixels;
  // an icon beside a visible label is decoration.
  function svgIcons(ignored) {
    const out = [];
    for (const svg of document.querySelectorAll('svg')) {
      if (svg.parentElement?.closest('svg') || ignored(svg) || !visible(svg)) continue;
      const r = svg.getBoundingClientRect();
      const control = svg.closest(CONTROLS);
      if (r.width > 64 || r.height > 64 || !control || control.innerText.trim()) continue;
      out.push({ selector: selectorOf(svg), name: nameOf(control), rect: rectOf(r) });
    }
    return out;
  }

  // Videos that play by themselves (WCAG 2.2.2 Pause, Stop, Hide), and whether the page offers a way to stop them.
  const PAUSE_WORDS = /\b(pause|stop|play|resume)\b|pysäytä|tauko|toista/i;
  function videos(ignored) {
    const pauseControl = [...document.querySelectorAll('button, [role=button], [role=switch], input[type=checkbox], input[type=button]')]
      .some((el) => !ignored(el) && visible(el) && !el.matches(':disabled, [aria-disabled="true"]') && PAUSE_WORDS.test(`${el.getAttribute('aria-label') ?? ''} ${el.getAttribute('title') ?? ''} ${el.textContent ?? ''}`));
    return [...document.querySelectorAll('video')].filter((v) => !ignored(v) && visible(v)).map((v) => ({
      selector: selectorOf(v),
      rect: rectOf(v.getBoundingClientRect()),
      played: v.dataset.m3aPlayed === '1' || !v.paused,
      loop: v.loop,
      duration: Number.isFinite(v.duration) ? Math.round(v.duration * 10) / 10 : null,
      controls: v.controls,
      pauseControl,
    }));
  }

  window.__m3audit = {
    collect(ignoreSelector) {
      const { scope, ignored } = makeIgnored(ignoreSelector);
      // Every element answers elementsFromPoint while measuring: a container painted by an element with
      // pointer-events: none is still the background its text sits on.
      const hit = document.createElement('style');
      hit.textContent = '* { pointer-events: auto !important; }';
      document.head.append(hit);
      try {
        scrollToY(0);
        const nav = [...document.querySelectorAll('nav, [role=navigation]')].filter((n) => !ignored(n) && visible(n)).map((n) => ({
          selector: selectorOf(n), items: [...n.querySelectorAll('a, button')].filter(visible).length, rect: rectOf(n.getBoundingClientRect()),
        }));
        return {
          viewport: { w: innerWidth, h: innerHeight },
          scrollWidth: document.scrollingElement.scrollWidth,
          scope: scope ? selectorOf(scope) : null,
          overflowing: [...document.querySelectorAll('body *')].filter((el) => !ignored(el) && visible(el)
            && el.getBoundingClientRect().right > innerWidth + 1 && getComputedStyle(el).position !== 'fixed').slice(0, 5).map(selectorOf),
          texts: texts(ignored),
          targets: targets(ignored),
          radii: radii(ignored),
          spacing: spacing(ignored),
          videos: videos(ignored),
          icons: svgIcons(ignored),
          nav,
        };
      } finally {
        hit.remove();
        scrollToY(0);
      }
    },
    // Everything keyboard focus can reach, numbered in DOM order (data-m3a-focus).
    focusables(ignoreSelector) {
      const { ignored } = makeIgnored(ignoreSelector);
      let n = 0;
      for (const el of document.querySelectorAll(TARGETS)) {
        if (ignored(el) || el.matches(':disabled') || el.tabIndex < 0 || !shownOf(el)) continue;
        el.setAttribute('data-m3a-focus', String(n));
        n += 1;
      }
      return n;
    },
    // Before a focus or hover check: where the marker goes (the element's box on the page at the top, which is also
    // where a fixed element sits in the full-page screenshot), then the element brought to the middle of the window.
    prepare(sel) {
      const el = document.querySelector(sel);
      const shown = el && shownOf(el);
      if (!shown) return null;
      scrollToY(0);
      const page = rectOf(shown.getBoundingClientRect());
      if (!inFixed(shown)) shown.scrollIntoView({ block: 'center', inline: 'nearest', behavior: 'instant' });
      return { page, selector: selectorOf(shown), name: nameOf(el) };
    },
    // The box a check photographs, in window coordinates, with the scroll position it was read at.
    view(sel) {
      const el = document.querySelector(sel);
      const shown = el && shownOf(el);
      if (!shown) return null;
      const r = shown.getBoundingClientRect();
      return { vx: r.left, vy: r.top, w: r.width, h: r.height, sx: scrollX, sy: scrollY };
    },
    // Whether the pointer at (x, y) lands on the element (and not on something covering it).
    hits(sel, x, y) {
      const el = document.querySelector(sel);
      const top = document.elementFromPoint(x, y);
      return !!(el && top && (el.contains(top) || shownOf(el)?.contains(top)));
    },
    // Two frames (a style change from a hover or a focus starts its transitions), then wait until the transitions
    // and finite animations running are done (at most 1.2 s), then two frames more.
    async quiet() {
      const frames = () => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
      await frames();
      const running = document.getAnimations().filter((a) => a.playState === 'running'
        && a.timeline === document.timeline && a.effect?.getComputedTiming().endTime !== Infinity);
      await Promise.race([Promise.all(running.map((a) => a.finished.catch(() => {}))), new Promise((r) => setTimeout(r, 1200))]);
      await frames();
    },
    // Fonts and the images the page has started loading (at most 3 s).
    async loaded() {
      await document.fonts.ready;
      const pending = [...document.images].filter((i) => !i.complete);
      await Promise.race([
        Promise.all(pending.map((i) => new Promise((r) => { i.addEventListener('load', r, { once: true }); i.addEventListener('error', r, { once: true }); }))),
        new Promise((r) => setTimeout(r, 3000))]);
    },
    markPlaying() {
      for (const v of document.querySelectorAll('video')) if (!v.paused) v.dataset.m3aPlayed = '1';
    },
    // A still page: finite animations finished, looping ones and videos paused (scroll-driven ones left alone),
    // nothing focused, the window at the top.
    settle() {
      for (const a of document.getAnimations()) {
        if (a.timeline !== document.timeline) continue;
        try {
          if (a.effect?.getComputedTiming().endTime === Infinity) a.pause();
          else a.finish();
        } catch (e) { /* an animation that cannot finish stays as it is */ }
      }
      this.markPlaying();
      for (const v of document.querySelectorAll('video')) v.pause();
      document.activeElement?.blur?.();
      scrollToY(0);
    },
    // Show one frame of a video (a fraction of its length), loading it first if the page has not.
    async seek(id, frac) {
      const v = document.querySelector(`[data-m3a-video="${id}"]`);
      if (!v) return false;
      const wait = (ev, ms) => new Promise((res) => {
        const t = setTimeout(res, ms);
        v.addEventListener(ev, () => { clearTimeout(t); res(); }, { once: true });
      });
      if (v.readyState < 2) {
        v.muted = true;
        v.play().catch(() => {});
        await wait('loadeddata', 3000);
        v.pause();
      }
      if (!Number.isFinite(v.duration) || v.duration <= 0) return false;
      const seeked = wait('seeked', 2000);
      v.currentTime = v.duration * frac;
      await seeked;
      return v.readyState >= 2;
    },
    // What still moves when the visitor asked for reduced motion: animations that loop or run over 5 s, and videos
    // that loop or run over 5 s; the audit's exclusions and an open modal's scope apply. Each with its box on the page.
    stillMoving(ignoreSelector) {
      const { ignored } = makeIgnored(ignoreSelector);
      const MOVES = ['transform', 'translate', 'rotate', 'scale', 'left', 'top', 'right', 'bottom'];
      scrollToY(0);
      const anims = document.getAnimations().filter((a) => a.playState === 'running').flatMap((a) => {
        const kf = a.effect?.getKeyframes?.() ?? [];
        const t = a.effect?.getComputedTiming?.() ?? {};
        const el = a.effect?.target;
        const moves = kf.some((k) => MOVES.some((p) => k[p] && k[p] !== 'none'));
        if (!moves || !el || ignored(el) || !visible(el) || !(t.iterations === Infinity || t.activeDuration > 5000)) return [];
        return [{ kind: 'animation', selector: selectorOf(el), rect: rectOf(el.getBoundingClientRect()) }];
      });
      const videos = [...document.querySelectorAll('video')].filter((v) => visible(v) && !ignored(v)
        && (v.dataset.m3aPlayed === '1' || !v.paused) && (v.loop || v.duration > 5))
        .map((v) => ({ kind: 'video', selector: selectorOf(v), rect: rectOf(v.getBoundingClientRect()) }));
      return [...anims, ...videos];
    },
    selectorOf,
    visible,
  };
})();
