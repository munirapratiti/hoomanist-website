/* Hoomanist — site runtime.
   Replaces the Claude Design canvas runtime with plain JS. No dependencies. */
(function () {
  'use strict';

  /* ---- contact address -------------------------------------------------
     Assembled at runtime rather than written into the HTML, so it doesn't
     sit in the markup as plain text for scrapers. Same approach the design
     used. Change it here and it updates everywhere on the page. */
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

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var f = e.target;
      var val = function (name) {
        return ((f[name] && f[name].value) || '').trim();
      };

      var name = val('name');
      var company = val('company');
      var subject = 'New enquiry from ' + (name || 'the website') +
                    (company ? ' (' + company + ')' : '');
      var body = 'Name: ' + name +
                 '\nCompany: ' + company +
                 '\nEmail: ' + val('email') +
                 '\n\n' + val('message');

      window.location.href = MAILTO + EMAIL +
        '?subject=' + encodeURIComponent(subject) +
        '&body=' + encodeURIComponent(body);

      formState.hidden = true;
      sentState.hidden = false;
    });
  }

  function init() {
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
