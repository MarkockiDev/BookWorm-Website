(function () {
  var root = document.documentElement;
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var THEMES = ['light', 'dark', 'retro', 'marginalia'];
  var store = function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} };
  var saved = function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } };

  /* ---- analytics: one helper, named events only (see README, "Website events") ----
     A no-op when PostHog isn't loaded (local preview, blockers), so nothing here can break the page. */
  var track = window.bwTrack = function (name, props) {
    if (window.posthog && window.posthog.capture) window.posthog.capture(name, props || {});
  };
  // every App Store button says where it sat; links without a tag are reported by their section
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href*="apps.apple.com"]');
    if (!a) return;
    var spot = a.getAttribute('data-placement') || ((a.closest('section, header, footer') || {}).id) || 'other';
    track('website_app_store_clicked', { placement: spot, theme: root.getAttribute('data-theme') });
  });
  // printable reading log downloads
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[data-printable]');
    if (a) track('website_printable_downloaded', { size: a.getAttribute('data-printable') });
  });
  // which questions people open
  document.querySelectorAll('details').forEach(function (d, i) {
    d.addEventListener('toggle', function () { if (d.open) track('website_faq_opened', { question: i + 1 }); });
  });

  /* ---- screenshots follow the theme ---- */
  function srcset(img, theme) {
    return img.getAttribute('data-w').split(' ').map(function (w) {
      return '/assets/shots/' + theme + '/' + img.getAttribute('data-shot') + '-' + w + '.webp ' + w + 'w';
    }).join(', ');
  }
  function paintShots(theme, animate) {
    document.querySelectorAll('img[data-shot]').forEach(function (img) {
      // the hero ships with light/dark sources so it can load before this script; once the theme is known, the script owns it
      if (img.parentNode.tagName === 'PICTURE') img.parentNode.querySelectorAll('source').forEach(function (s) { s.remove(); });
      var next = srcset(img, theme);
      if (img.getAttribute('srcset') === next) return;
      if (!animate || reduce || !img.complete) { img.setAttribute('srcset', next); return; }
      img.classList.add('swapping');
      var pre = new Image(); pre.sizes = img.sizes; pre.srcset = next;
      var done = function () { img.setAttribute('srcset', next); img.classList.remove('swapping'); };
      (pre.decode ? pre.decode() : Promise.resolve()).then(done, done);
    });
  }

  /* ---- one theme for the whole page ---- */
  var swatch = document.getElementById('theme-swatch');
  var desc = document.getElementById('look-desc');
  function setTheme(theme, opts) {
    opts = opts || {};
    root.setAttribute('data-theme', theme);
    swatch.className = 'swatch sw-' + theme;
    document.querySelectorAll('[data-set-theme]').forEach(function (b) { b.setAttribute('aria-checked', String(b.getAttribute('data-set-theme') === theme)); });
    var picked = document.querySelector('.look[data-set-theme="' + theme + '"]');
    if (picked && desc) desc.textContent = picked.getAttribute('data-desc');
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', getComputedStyle(root).getPropertyValue('--paper').trim());
    paintShots(theme, opts.animate);
    if (opts.save) store('bw-theme', theme);
  }
  setTheme(root.getAttribute('data-theme'), {});
  // whatever changes the theme, the screenshots follow it, so a page can never show the app in the wrong look
  new MutationObserver(function () { paintShots(root.getAttribute('data-theme'), true); })
    .observe(root, { attributes: true, attributeFilter: ['data-theme'] });
  // until someone picks a look, follow the system's light or dark
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
    if (!saved('bw-theme')) setTheme(e.matches ? 'dark' : 'light', { animate: true });
  });
  document.querySelectorAll('[data-set-theme]').forEach(function (b) {
    b.addEventListener('click', function () {
      var from = root.getAttribute('data-theme'), to = b.getAttribute('data-set-theme');
      setTheme(to, { animate: true, save: true });
      if (from !== to) track('website_theme_changed', { theme: to, from: from, source: b.closest('.menu') ? 'nav' : 'section' });
      if (b.closest('.menu')) closeMenus(true);
    });
  });
  // the looks are a radio group: arrow keys move and choose
  var looks = Array.prototype.slice.call(document.querySelectorAll('.look'));
  looks.forEach(function (b, i) {
    b.addEventListener('keydown', function (e) {
      var d = (e.key === 'ArrowRight' || e.key === 'ArrowDown') ? 1 : (e.key === 'ArrowLeft' || e.key === 'ArrowUp') ? -1 : 0;
      if (!d) return; e.preventDefault();
      var n = looks[(i + d + looks.length) % looks.length]; n.focus(); n.click();
    });
  });

  /* ---- nav menus ---- */
  var menus = [['theme-btn', 'theme-menu'], ['lang-btn', 'lang-menu']];
  function closeMenus(refocus) {
    menus.forEach(function (m) {
      var btn = document.getElementById(m[0]), menu = document.getElementById(m[1]);
      if (btn.getAttribute('aria-expanded') === 'true' && refocus) btn.focus();
      btn.setAttribute('aria-expanded', 'false'); menu.classList.remove('open');
    });
  }
  menus.forEach(function (m) {
    var btn = document.getElementById(m[0]), menu = document.getElementById(m[1]);
    var items = function () { return Array.prototype.slice.call(menu.querySelectorAll('button, a')); };
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = btn.getAttribute('aria-expanded') === 'true';
      closeMenus(false);
      if (!open) {
        btn.setAttribute('aria-expanded', 'true'); menu.classList.add('open');
        var cur = menu.querySelector('[aria-checked="true"], [aria-current="page"]') || items()[0];
        setTimeout(function () { cur.focus(); }, 30);
      }
    });
    menu.addEventListener('keydown', function (e) {
      var list = items(), i = list.indexOf(document.activeElement);
      if (e.key === 'ArrowDown') { e.preventDefault(); list[(i + 1) % list.length].focus(); }
      if (e.key === 'ArrowUp') { e.preventDefault(); list[(i - 1 + list.length) % list.length].focus(); }
      if (e.key === 'Home') { e.preventDefault(); list[0].focus(); }
      if (e.key === 'End') { e.preventDefault(); list[list.length - 1].focus(); }
      if (e.key === 'Tab') closeMenus(false);
    });
  });
  document.addEventListener('click', function (e) { if (!e.target.closest('.menu-wrap')) closeMenus(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeMenus(true); });
  document.querySelectorAll('#lang-menu a').forEach(function (a) {
    a.addEventListener('click', function () {
      store('bw-lang', a.getAttribute('hreflang'));
      track('website_language_changed', { to: a.getAttribute('hreflang'), from: root.lang });
    });
  });

  /* ---- nav tightens once the page moves; marks the section in view ---- */
  var nav = document.getElementById('nav');
  var lastY = window.scrollY;
  var onScroll = function () {
    var y = window.scrollY;
    nav.classList.toggle('compact', y > 40);
    // the phone link row steps aside while reading down and comes back on any scroll up
    if (y > 160 && y > lastY + 6) nav.classList.add('tuck');
    else if (y < lastY - 6 || y <= 160) nav.classList.remove('tuck');
    if (Math.abs(y - lastY) > 6) lastY = y;
  };
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();
  // a link to another page is "current" while you are on it (or inside it, for guides);
  // a link to a section of this page is current while that section fills the middle of the screen
  var links = Array.prototype.slice.call(document.querySelectorAll('.nav-links a'));
  var here = location.pathname;
  var pageLinks = links.filter(function (a) { return a.hash === ''; });
  var sectionLinks = links.filter(function (a) { return a.hash !== '' && a.pathname === here; });
  pageLinks.forEach(function (a) { if (here.indexOf(a.pathname) === 0) a.setAttribute('aria-current', 'page'); });
  var spy = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      sectionLinks.forEach(function (a) { a.setAttribute('aria-current', String(a.hash === '#' + e.target.id)); });
    });
  }, { rootMargin: '-50% 0px -50% 0px' });
  sectionLinks.forEach(function (a) { var s = document.getElementById(a.hash.slice(1)); if (s) spy.observe(s); });

  /* ---- reveal on scroll ---- */
  var reveal = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); reveal.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -10% 0px' });
  document.querySelectorAll('.reveal').forEach(function (el) { reveal.observe(el); });

  /* ---- the three beats ---- */
  var beats = document.querySelectorAll('.beat');
  var stage = document.querySelectorAll('.stage .shot');
  var beatObs = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      e.target.classList.add('lit');
      var step = e.target.getAttribute('data-step');
      beats.forEach(function (b) { b.classList.toggle('active', b === e.target); });
      stage.forEach(function (s) { s.classList.toggle('active', s.getAttribute('data-for') === step); });
    });
  }, { rootMargin: '-45% 0px -45% 0px' });
  beats.forEach(function (b) { beatObs.observe(b); });
  if (beats[0]) beats[0].classList.add('active');

  /* ---- the Live Activity clock keeps running while the section is on screen ---- */
  var ticks = document.querySelectorAll('.tick-time');
  if (!reduce && ticks.length && document.querySelector('.screen.lock')) {
    var secs = 24 * 60 + 17, timer = null;
    var fmt = function (s) { return Math.floor(s / 60) + ':' + ('0' + s % 60).slice(-2); };
    new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting && !timer) timer = setInterval(function () { secs++; ticks.forEach(function (t) { t.textContent = fmt(secs); }); }, 1000);
        if (!e.isIntersecting && timer) { clearInterval(timer); timer = null; }
      });
    }).observe(document.querySelector('.screen.lock'));
  }

  /* ---- session replay, only with consent (README, "Session replay") ----
     Unanswered: the card asks once per visit, a few seconds in. Allow: storage and recording start now,
     and the snippet in the head starts recording on later visits. No thanks: never asked again.
     "Recording choices" in the footer reopens the card; saying no there stops recording and forgets the session. */
  var card = document.getElementById('consent');
  var choices = document.getElementById('replay-choices');
  var ph = function () { return window.posthog && window.posthog.__loaded ? window.posthog : null; };
  function openCard() {
    if (!card || !card.hidden) return;
    card.hidden = false; card.classList.add('enter');
    requestAnimationFrame(function () { requestAnimationFrame(function () { card.classList.remove('enter'); }); });
  }
  function closeCard() { if (card) card.hidden = true; }
  function answer(yes) {
    var was = saved('bw-replay');
    store('bw-replay', yes ? 'yes' : 'no');
    track('website_replay_consent', { choice: yes ? 'allow' : 'decline' });
    closeCard();
    var p = ph();
    if (yes && p) {
      p.set_config({ persistence: 'localStorage+cookie' });
      p.register({ replay: 'on' });
      p.startSessionRecording();
    } else if (!yes && was === 'yes') {
      // forget the session: stop recording, stop PostHog writing, and reload; the head snippet then
      // clears whatever PostHog stored before it starts again, cookieless
      if (p) { p.stopSessionRecording(); p.set_config({ persistence: 'memory' }); }
      location.reload();
    }
  }
  if (card) {
    card.querySelectorAll('[data-replay]').forEach(function (b) {
      b.addEventListener('click', function () { answer(b.getAttribute('data-replay') === 'yes'); });
    });
    card.addEventListener('keydown', function (e) { if (e.key === 'Escape') { answer(false); if (choices) choices.focus(); } });
    if (choices) choices.addEventListener('click', function () { openCard(); card.querySelector('.consent-allow').focus(); });
    // ask only where analytics actually runs, and only someone who hasn't answered
    if (!saved('bw-replay') && (location.hostname === 'ilovebookworm.com' || /[?&]ph=1\b/.test(location.search))) {
      var asked = false, ask = function () { if (asked) return; asked = true; window.removeEventListener('scroll', onFirstScroll); openCard(); };
      var onFirstScroll = function () { if (window.scrollY > 200) ask(); };
      setTimeout(ask, 6000);
      window.addEventListener('scroll', onFirstScroll, { passive: true });
    }
  }
})();
