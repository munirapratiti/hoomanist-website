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
  var FORM_ENDPOINT = 'https://formspree.io/f/xvkoqkdg';

  var AT = String.fromCharCode(64);
  var EMAIL = 'hoomanist' + '.id' + AT + 'gmail' + '.com';
  var MAILTO = 'mail' + 'to:';

  /* ---- WhatsApp -------------------------------------------------------
     Selama WA_NUMBER kosong, tombol WhatsApp tidak muncul sama sekali —
     jadi kode ini aman ada di situs sebelum nomornya diputuskan.
     Format internasional, angka saja: tanpa +, spasi, atau strip.
     Contoh: 081234567890 ditulis '6281234567890'.
     Nomornya disusun di sini, bukan ditulis di HTML, dengan alasan yang
     sama seperti EMAIL. */
  var WA_NUMBER = '';

  /* Label konversi SEKUNDER untuk klik WhatsApp (AW-18452142367/xxxx).
     Sengaja dipisah dari ADS_CONVERSION_LABEL: klik tombol belum tentu
     jadi pesan terkirim, jadi Google Ads tidak boleh belajar dari angka
     ini — di dashboard, setel conversion action-nya sebagai Secondary. */
  var ADS_WA_LABEL = '';

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

  /* ---- lapor konversi ke platform iklan ---------------------------------
     Dipanggil hanya saat pesan benar-benar terkirim, bukan saat halaman
     dibuka. Ini bedanya lead yang terhitung dengan kunjungan yang terhitung —
     kalau tag dipasang di halaman, Google akan mengira setiap pengunjung
     adalah lead dan mengoptimalkan ke arah yang salah.

     Aman dipanggil sebelum tag apa pun terpasang: kalau gtag/fbq belum ada,
     fungsi ini tidak melakukan apa-apa dan tidak melempar error. */
  var ADS_CONVERSION_LABEL = 'AW-18452142367/IUdiCNWxoPgcEJ-y1d5E';

  function reportLead(via) {
    try {
      if (typeof window.gtag === 'function') {
        // Peristiwa untuk GA4 — terbaca walau konversi iklan belum disetel.
        window.gtag('event', 'generate_lead', {
          method: via,
          form_id: 'contact-form',
        });
        if (ADS_CONVERSION_LABEL) {
          window.gtag('event', 'conversion', {
            send_to: ADS_CONVERSION_LABEL,
            value: 1.0,
            currency: 'IDR',
          });
        }
      }
      if (typeof window.fbq === 'function') {
        window.fbq('track', 'Lead', { content_name: 'contact-form' });
      }
    } catch (e) {
      // Pelaporan tidak boleh menggagalkan pengiriman pesan.
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
          reportLead('form');
          showSent(false);
        }).catch(function () {
          // Jangan biarkan pesannya hilang: tawarkan jalur manual.
          showSent(true);
        }).then(function () {
          if (btn) { btn.disabled = false; btn.textContent = label; }
        });
        return;
      }

      reportLead('mailto');
      window.location.href = MAILTO + EMAIL +
        '?subject=' + encodeURIComponent(d.subject) +
        '&body=' + encodeURIComponent(body);
      showSent(true);
    });
  }

  function waDisplay(num) {
    // 6281234567890 -> +62 812-3456-7890 (kelompok 3 lalu per 4 angka)
    var cc = num.slice(0, 2), rest = num.slice(2), parts = [rest.slice(0, 3)];
    for (var i = 3; i < rest.length; i += 4) parts.push(rest.slice(i, i + 4));
    return '+' + cc + ' ' + parts.join('-');
  }

  function reportWhatsApp(place) {
    try {
      if (typeof window.gtag === 'function') {
        window.gtag('event', 'whatsapp_click', { placement: place });
        if (ADS_WA_LABEL) {
          window.gtag('event', 'conversion', { send_to: ADS_WA_LABEL });
        }
      }
    } catch (e) { /* Pelaporan tidak boleh menghalangi chat dibuka. */ }
  }

  var WA_ICON =
    '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" ' +
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" ' +
    'stroke-linejoin="round" aria-hidden="true"><path d="M3.5 20.5l1.3-4.1' +
    'A8.5 8.5 0 1 1 8 19.6z"></path><path d="M9 8.6c.2 2.8 3.1 5.8 6 6' +
    'l1.1-1.4-2-1.1-.9.8c-1-.4-2-1.4-2.4-2.4l.8-.9-1.1-2z"></path></svg>';

  function wireWhatsApp() {
    if (!WA_NUMBER) return;

    var isId = document.documentElement.lang === 'id';
    var text = isId
      ? 'Halo Hoomanist, saya mau tanya soal rekrutmen untuk tim saya.'
      : "Hi Hoomanist, I'd like to ask about hiring for my team.";
    var href = 'https://wa.me/' + WA_NUMBER + '?text=' + encodeURIComponent(text);

    // Baris di halaman kontak: kerangkanya ada di template, isinya dari sini.
    var rows = document.querySelectorAll('.js-wa');
    for (var i = 0; i < rows.length; i++) {
      rows[i].href = href;
      rows[i].innerHTML =
        '<span style="width:52px;height:52px;border-radius:14px;' +
        'background:rgba(255,255,255,0.08);display:flex;align-items:center;' +
        'justify-content:center;flex:none;color:#EE7E52;">' + WA_ICON + '</span>' +
        '<span><span style="display:block;font-size:14px;color:#6A7385;' +
        'text-transform:uppercase;letter-spacing:0.1em;font-weight:600;">' +
        'WhatsApp</span><span style="font-size:21px;font-weight:600;">' +
        waDisplay(WA_NUMBER) + '</span></span>';
      rows[i].style.display = 'flex';
      rows[i].addEventListener('click', function () { reportWhatsApp('contact'); });
    }

    // Tombol melayang hanya di halaman yang tidak punya baris WhatsApp,
    // supaya halaman kontak tidak menampilkan dua tombol untuk hal yang sama.
    if (rows.length) return;
    var fab = document.createElement('a');
    fab.className = 'wa-float';
    fab.href = href;
    fab.target = '_blank';
    fab.rel = 'noopener';
    fab.setAttribute('aria-label', isId ? 'Chat lewat WhatsApp' : 'Chat on WhatsApp');
    fab.innerHTML = WA_ICON;
    fab.addEventListener('click', function () { reportWhatsApp('float'); });
    document.body.appendChild(fab);
  }

  function init() {
    wireNav();
    wireEmail();
    wireReveals();
    wireCounters();
    wireForm();
    wireWhatsApp();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
