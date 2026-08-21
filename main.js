/* Hoomanist — site runtime.
   Replaces the Claude Design canvas runtime with plain JS. No dependencies. */
(function () {
  'use strict';

  /* ---- contact address -------------------------------------------------
     Assembled at runtime rather than written into the HTML, so it doesn't
     sit in the markup as plain text for scrapers. Same approach the design
     used. Change it here and it updates everywhere on the page. */
  // Isi dengan endpoint Formspree (atau layanan sejenis) agar kiriman form
  // benar-benar masuk ke inbox. Selama kosong, form memakai aplikasi email
  // pengunjung, dengan panel salin-tempel sebagai jaring pengaman.
  var FORM_ENDPOINT = '';

  var AT = String.fromCharCode(64);
  var EMAIL = 'hoomanist' + '.id' + AT + 'gmail' + '.com';
  var MAILTO = 'mail' + 'to:';

  function mailtoMain() {
    return MAILTO + EMAIL;
  }

  function mailtoTalent() {
    return MAILTO + EMAIL +
      '?subject=' + encodeURIComponent('Portfolio submission') +
      '&body=' + encodeURIComponent(
        "Hi Hoomanist,\n\nHere's my portfolio and what I'm looking for:\n");
  }

  /* Fill in the address text and every mailto link. */
  function wireEmail() {
    var i, els;
    els = document.querySelectorAll('.js-email');
    for (i = 0; i < els.length; i++) els[i].textContent = EMAIL;

    els = document.querySelectorAll('[data-mailto]');
    for (i = 0; i < els.length; i++) {
      els[i].href = els[i].getAttribute('data-mailto') === 'talent'
        ? mailtoTalent()
        : mailtoMain();
    }
  }

  /* ---- menu di layar sempit -------------------------------------------
     Di bawah 980px daftar tautan disembunyikan CSS dan hanya muncul saat
     tombol ditekan. Tanpa ini lima halaman tidak bisa dijangkau dari ponsel. */
  function wireNav() {
    var btn = document.querySelector('.nav-toggle');
    var links = document.getElementById('nav-links');
    if (!btn || !links) return;

    function setOpen(open) {
      links.classList.toggle('open', open);
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.setAttribute('aria-label', open ? 'Tutup menu navigasi' : 'Buka menu navigasi');
    }

    btn.addEventListener('click', function () {
      setOpen(!links.classList.contains('open'));
    });

    // Menutup sendiri setelah sebuah tautan dipilih.
    links.addEventListener('click', function (e) {
      if (e.target.closest('a')) setOpen(false);
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && links.classList.contains('open')) {
        setOpen(false);
        btn.focus();
      }
    });
  }

  /* ---- scroll reveals -------------------------------------------------- */
  function wireReveals() {
    var targets = document.querySelectorAll('.reveal');
    if (!('IntersectionObserver' in window)) {
      // No observer support: just show everything rather than hiding content.
      for (var i = 0; i < targets.length; i++) targets[i].classList.add('in');
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add('in');
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    for (var j = 0; j < targets.length; j++) io.observe(targets[j]);
  }

  /* ---- count-up numbers ------------------------------------------------ */
  function wireCounters() {
    var targets = document.querySelectorAll('[data-to]');
    if (!('IntersectionObserver' in window)) return;

    var reduced = window.matchMedia &&
                  window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    var cu = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var el = e.target;
        var to = parseFloat(el.getAttribute('data-to'));
        cu.unobserve(el);

        if (reduced) { el.textContent = String(to); return; }

        var t0 = performance.now();
        var tick = function (t) {
          var p = Math.min(1, (t - t0) / 1100);
          el.textContent = Math.round(to * (1 - Math.pow(1 - p, 3))).toString();
          if (p < 1) requestAnimationFrame(tick);
          else el.textContent = String(to);
        };
        el.textContent = '0';
        requestAnimationFrame(tick);
      });
    }, { threshold: 0.6 });

    for (var i = 0; i < targets.length; i++) cu.observe(targets[i]);
  }

  /* ---- contact form ----------------------------------------------------
     There is no backend. The form composes a mailto: and hands off to the
     visitor's mail client, then swaps in the confirmation panel. */
  function wireForm() {
    var form = document.getElementById('contact-form');
    var formState = document.getElementById('form-state');
    var sentState = document.getElementById('sent-state');
    if (!form || !formState || !sentState) return;

    var fallbackPanel = document.getElementById('fallback-panel');
    var fallbackBox = document.getElementById('fallback-message');
    var copyBtn = document.getElementById('copy-message');

    function compose(f) {
      var val = function (name) {
        return ((f[name] && f[name].value) || '').trim();
      };
      var name = val('name');
      var company = val('company');
      return {
        name: name,
        company: company,
        email: val('email'),
        message: val('message'),
        subject: 'New enquiry from ' + (name || 'the website') +
                 (company ? ' (' + company + ')' : ''),
      };
    }

    function asText(d) {
      return 'Name: ' + d.name +
             '\nCompany: ' + d.company +
             '\nEmail: ' + d.email +
             '\n\n' + d.message;
    }

    function showSent(withFallback) {
      formState.hidden = true;
      sentState.hidden = false;
      if (fallbackPanel) fallbackPanel.hidden = !withFallback;
    }

    if (copyBtn && fallbackBox) {
      copyBtn.addEventListener('click', function () {
        var done = function () {
          var was = copyBtn.textContent;
          copyBtn.textContent = 'Copied';
          setTimeout(function () { copyBtn.textContent = was; }, 1800);
        };
        // Clipboard API needs a secure context; select-and-copy is the
        // fallback so the button still works everywhere.
        if (navigator.clipboard && window.isSecureContext) {
          navigator.clipboard.writeText(fallbackBox.value).then(done, function () {
            fallbackBox.select();
          });
        } else {
          fallbackBox.select();
          try { document.execCommand('copy'); done(); } catch (e) { /* biar dipilih */ }
        }
      });
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var d = compose(e.target);
      var body = asText(d);
      if (fallbackBox) fallbackBox.value = body;

      if (FORM_ENDPOINT) {
        var btn = form.querySelector('button[type="submit"]');
        var label = btn ? btn.textContent : '';
        if (btn) { btn.disabled = true; btn.textContent = 'Sending…'; }

        fetch(FORM_ENDPOINT, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
          body: JSON.stringify(d),
        }).then(function (r) {
          if (!r.ok) throw new Error('gagal');
          showSent(false);
        }).catch(function () {
          // Jangan biarkan pesannya hilang: tawarkan jalur manual.
          showSent(true);
        }).then(function () {
          if (btn) { btn.disabled = false; btn.textContent = label; }
        });
        return;
      }

      window.location.href = MAILTO + EMAIL +
        '?subject=' + encodeURIComponent(d.subject) +
        '&body=' + encodeURIComponent(body);
      showSent(true);
    });
  }

  function init() {
    wireNav();
    wireEmail();
    wireReveals();
    wireCounters();
    wireForm();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
