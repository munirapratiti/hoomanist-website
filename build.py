#!/usr/bin/env python3
"""Assembles the static site from src/ into the deployable HTML files.

Nav and footer live in one place here rather than being copy-pasted into every
page, so a menu change is a one-line edit instead of seven.

Run after editing anything in src/:

    python3 build.py
"""

import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone

from site_config import BASE, PATHS
SRC = "src"
RAW = os.path.join(SRC, "raw")

# Nav order. Add a page here and it appears in the header and footer.
NAV = [
    ("Services", "/services"),
    ("Why us", "/why-us"),
    ("Proof", "/proof"),
    ("For Creatives", "/for-creatives"),
    ("FAQ", "/faq"),
]

# Each page: output path, <title>, meta description, and the raw blocks it is
# built from (in order).
PAGES = [
    {
        "path": "/",
        "out": "index.html",
        "title": "Creative Recruitment in Indonesia | Hoomanist",
        "desc": "Hoomanist is a creative workforce partner in Indonesia. We help "
                "agencies and brands hire, grow and keep the people behind "
                "great work.",
        "blocks": ["top", "_section2", "_section3", "home-cta"],
    },
    {
        "path": "/services",
        "out": "services/index.html",
        "title": "Creative Recruitment & People Systems | Hoomanist",
        "desc": "Creative recruitment, people growth and performance systems for "
                "studios and brands in Indonesia. Culture-fit hiring, backed by "
                "a 90-day guarantee.",
        "blocks": ["services", "pricing"],
    },
    {
        "path": "/why-us",
        "out": "why-us/index.html",
        "title": "Why Creative Teams Choose Hoomanist",
        "desc": "Your people are the one thing nobody can copy. Why creative "
                "teams in Indonesia work with Hoomanist, and the people "
                "behind it.",
        "blocks": ["why", "team"],
    },
    {
        "path": "/proof",
        "out": "proof/index.html",
        "title": "Creative Recruitment Case Studies | Hoomanist",
        "desc": "15+ roles filled for By.U in three weeks. Results from the "
                "creative teams we've built since 2023.",
        "blocks": ["proof"],
    },
    {
        "path": "/for-creatives",
        "out": "for-creatives/index.html",
        "title": "Creative Jobs in Indonesia | Hoomanist",
        "desc": "Looking for a team that actually fits? Share your portfolio "
                "with Hoomanist and we'll keep you in mind for roles at "
                "studios and brands.",
        "blocks": ["creatives"],
    },
    {
        "path": "/faq",
        "out": "faq/index.html",
        "title": "Recruitment FAQ — Fees, Timeline & Guarantee | Hoomanist",
        "desc": "How long a creative hire takes, when we invoice, and what "
                "happens if the fit doesn't work out. Honest answers about how "
                "Hoomanist works.",
        "blocks": ["faq"],
    },
    {
        "path": "/contact",
        "out": "contact/index.html",
        "title": "Contact Hoomanist — Creative Recruitment in Indonesia",
        "desc": "Tell us where your team is today and what feels challenging. "
                "Start a discovery conversation with Hoomanist.",
        "blocks": ["contact"],
    },
]

# The single-page anchors become real page URLs.
ANCHORS = {
    "#top": "/",
    "#contact": "/contact",
    "#services": "/services",
    "#pricing": "/services#pricing",
    "#why": "/why-us",
    "#proof": "/proof",
    "#creatives": "/for-creatives",
    "#faq": "/faq",
}


def read(path):
    with open(path) as fh:
        return fh.read()


def load_content(stem):
    """Wording for a section, split out so the CMS can edit it."""
    path = os.path.join("content", stem + ".json")
    if not os.path.exists(path):
        return {}
    with open(path) as fh:
        return json.load(fh)


def render_block(stem):
    """Section markup with its {{placeholders}} filled from content/."""
    html = clean(read(os.path.join(RAW, stem + ".html")))
    fields = load_content(stem)

    def sub(m):
        field = fields.get(m.group(1))
        # An unknown key means content/ and src/raw/ drifted apart. Leave the
        # placeholder visible rather than silently dropping the text.
        return field if field is not None else m.group(0)

    return re.sub(r"\{\{([a-z0-9_]+)\}\}", sub, html)


def clean(block):
    """Drop the trailing section comment that belongs to the next block."""
    return re.sub(r'\s*<!--[^>]*-->\s*$', '\n', block).rstrip()


def rewrite_links(html):
    """Anchors to page URLs, and relative asset paths to absolute ones.

    Relative "assets/..." would resolve against /services/ on a subpage and
    404, so every asset reference has to be rooted.
    """
    for anchor, url in ANCHORS.items():
        html = html.replace('href="%s"' % anchor, 'href="%s"' % url)
    html = html.replace('src="assets/', 'src="/assets/')
    return html


def build_nav(current):
    links = []
    for label, url in NAV:
        cls = "navlink active" if url == current else "navlink"
        links.append('<a href="%s" class="%s">%s</a>' % (url, cls, label))
    return (
        '<nav style="position:sticky;top:0;z-index:50;'
        'background:rgba(246,242,232,0.86);backdrop-filter:blur(10px);'
        'border-bottom:1px solid #E5DCC8;">\n'
        '    <div class="pad-x" style="max-width:1180px;margin:0 auto;'
        'padding:0 40px;height:76px;display:flex;align-items:center;'
        'justify-content:space-between;">\n'
        '      <a href="/" style="display:flex;align-items:center;gap:12px;">'
        '<img src="/assets/logo-icon.png" alt="Hoomanist" '
        'style="height:44px;width:44px;display:block;object-fit:contain;">'
        '<span style="font-size:23px;font-weight:700;letter-spacing:-0.02em;'
        'color:#2C1E2E;">hoomanist</span></a>\n'
        '      <div id="nav-links" class="nav-links" style="display:flex;'
        'align-items:center;gap:38px;font-size:16px;font-weight:500;'
        'color:#42485A;">\n        '
        + "\n        ".join(links) +
        '\n      </div>\n'
        '      <div style="display:flex;align-items:center;gap:12px;">\n'
        '        <a href="/contact" class="btn-primary" '
        'style="background:#3B2145;color:#F6F2E8;font-size:16px;'
        'font-weight:600;padding:13px 26px;border-radius:999px;">'
        "Let's talk</a>\n"
        '        <button type="button" class="nav-toggle" aria-expanded="false" '
        'aria-controls="nav-links" aria-label="Buka menu navigasi">'
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round">'
        '<path d="M3 6h18"></path><path d="M3 12h18"></path>'
        '<path d="M3 18h18"></path></svg></button>\n'
        '      </div>\n'
        '    </div>\n  </nav>\n'
    )


def build_footer():
    footer = render_block("_footer12")
    footer = rewrite_links(footer)
    # The footer's "Explore" column still lists the old duplicate menu.
    footer = footer.replace(
        '<a href="/services" class="navlink">What We Do</a>\n          ', '')
    footer = footer.replace(
        '<a href="/services#pricing" class="navlink">Pricing</a>',
        '<a href="/faq" class="navlink">FAQ</a>')
    return footer


def esc(text):
    """Aman untuk ditaruh di <title> maupun di atribut content="...".

    Apostrof sengaja dibiarkan: setiap atribut di sini dibatasi tanda kutip
    ganda, jadi meng-escape-nya hanya membuat markup lebih berisik.
    """
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))


def strip_tags(html):
    """Teks polos dari sepotong markup — untuk isi JSON-LD."""
    text = re.sub(r"<[^>]+>", "", html)
    for entity, char in (("&amp;", "&"), ("&nbsp;", " "), ("&#39;", "'"),
                         ("&quot;", '"'), ("&lt;", "<"), ("&gt;", ">")):
        text = text.replace(entity, char)
    return re.sub(r"\s+", " ", text).strip()


def faq_pairs(body):
    """Pasangan tanya-jawab dari blok FAQ yang sudah dirender.

    Dibaca dari markup hasil render, bukan ditulis ulang tangan, supaya
    schema tidak pernah berbeda dari yang dibaca pengunjung.
    """
    pairs = []
    for block in re.findall(r"<details.*?</details>", body, re.S):
        q = re.search(r"<summary[^>]*>(.*?)</summary>", block, re.S)
        a = re.search(r"<p[^>]*>(.*?)</p>", block, re.S)
        if q and a:
            question, answer = strip_tags(q.group(1)), strip_tags(a.group(1))
            if question and answer:
                pairs.append((question, answer))
    return pairs


def build_schema(page, body):
    """JSON-LD per halaman.

    Hanya memuat fakta yang memang sudah tampil di situs. Alamat email
    sengaja tidak ikut — situs ini menyusunnya saat runtime di main.js
    sebagai penghambat scraper, dan schema akan membocorkannya kembali.
    """
    org = {
        "@type": "Organization",
        "@id": BASE + "/#organization",
        "name": "Hoomanist",
        "url": BASE + "/",
        "logo": BASE + "/assets/logo-icon.png",
        "image": BASE + "/assets/og-image.png",
        "description": PAGES[0]["desc"],
        "sameAs": ["https://www.instagram.com/hoomanist.id/"],
        # Negara saja, tanpa alamat jalan — itu fakta tentang di mana bisnis
        # ini berada, bukan klaim soal wilayah yang dilayani. FAQ situs sendiri
        # menyebut mereka bekerja remote dengan tim mana pun.
        "address": {"@type": "PostalAddress", "addressCountry": "ID"},
    }

    graph = [org, {
        "@type": "WebPage",
        "@id": BASE + (page["path"] if page["path"] != "/" else "/") + "#webpage",
        "url": BASE + ("" if page["path"] == "/" else page["path"]),
        "name": page["title"],
        "description": page["desc"],
        "isPartOf": {"@id": BASE + "/#website"},
        "publisher": {"@id": BASE + "/#organization"},
    }]

    if page["path"] == "/":
        graph.append({
            "@type": "WebSite",
            "@id": BASE + "/#website",
            "url": BASE + "/",
            "name": "Hoomanist",
            "publisher": {"@id": BASE + "/#organization"},
        })

    if page["path"] == "/faq":
        pairs = faq_pairs(body)
        if pairs:
            graph.append({
                "@type": "FAQPage",
                "@id": BASE + "/faq#faqpage",
                "mainEntity": [
                    {"@type": "Question", "name": q,
                     "acceptedAnswer": {"@type": "Answer", "text": a}}
                    for q, a in pairs
                ],
            })

    payload = json.dumps({"@context": "https://schema.org", "@graph": graph},
                         ensure_ascii=False, indent=2)
    return '<script type="application/ld+json">\n%s\n</script>' % payload


def main():
    head_tpl = read(os.path.join(SRC, "head.html"))
    footer = build_footer()

    for page in PAGES:
        body = "\n\n".join(
            rewrite_links(render_block(b)) for b in page["blocks"])

        html = (head_tpl
                .replace("{{BUILT}}", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
                # Judul dan deskripsi masuk ke markup, jadi harus di-escape.
                # Versi mentahnya tetap dipakai di JSON-LD, yang aturan
                # pelolosannya beda (JSON, bukan HTML).
                .replace("{{TITLE}}", esc(page["title"]))
                .replace("{{DESC}}", esc(page["desc"]))
                .replace("{{SCHEMA}}", build_schema(page, body))
                .replace("{{BASE}}", BASE)
                # Beranda memakai garis miring agar canonical, og:url dan
                # sitemap menuliskan URL yang sama persis. Sebelumnya
                # canonical menulis tanpa garis miring sementara sitemap
                # dengan — dua ejaan untuk satu halaman.
                .replace("{{PATH}}", "/" if page["path"] == "/" else page["path"]))

        html += build_nav(page["path"]) + "\n" + body + "\n\n" + footer
        html += '\n\n</div>\n<script src="/main.js" defer></script>\n</body>\n</html>\n'

        out = page["out"]
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        with open(out, "w") as fh:
            fh.write(html)
        print("  %-28s %6d bytes" % (out, len(html)))


def _shallow_clone(_cache=[]):
    """Benar kalau repo ini hasil clone dangkal.

    Penting karena pada clone dangkal `git log -1 -- berkas` mengembalikan
    tanggal commit terakhir untuk berkas apa pun — riwayat sebelumnya tidak
    ada. Hasilnya setiap halaman akan mengaku berubah pada tanggal deploy,
    yaitu kebohongan yang justru ingin dihindari lastmod. Lebih baik seluruh
    ruas lastmod dilewati. Vercel meng-clone dengan kedalaman terbatas, jadi
    ini bukan kasus teoretis.
    """
    if not _cache:
        try:
            out = subprocess.run(
                ["git", "rev-parse", "--is-shallow-repository"],
                capture_output=True, text=True, timeout=10)
            _cache.append(out.stdout.strip() != "false")
        except (OSError, subprocess.SubprocessError):
            _cache.append(True)
    return _cache[0]


def last_changed(path):
    """Tanggal commit terakhir yang menyentuh isi sebuah halaman, atau None.

    Sengaja memakai riwayat git, bukan waktu build: kalau lastmod diisi
    waktu build, setiap halaman akan mengaku berubah pada setiap deploy.
    Tanggal yang keliru lebih buruk daripada tidak ada tanggal — mesin
    telusur belajar mengabaikan lastmod yang terbukti tidak bisa dipercaya.
    Kalau riwayatnya tidak terbaca (checkout dangkal, git tidak ada),
    fungsi ini mengembalikan None dan ruas lastmod dilewati saja.
    """
    page = next((p for p in PAGES if p["path"] == (path or "/")), None)
    if page is None or _shallow_clone():
        return None

    sources = [os.path.join(SRC, "head.html")]
    for block in page["blocks"]:
        sources.append(os.path.join(RAW, block + ".html"))
        sources.append(os.path.join("content", block + ".json"))

    dates = []
    for src in sources:
        if not os.path.exists(src):
            continue
        try:
            out = subprocess.run(
                ["git", "log", "-1", "--format=%cI", "--", src],
                capture_output=True, text=True, timeout=10)
        except (OSError, subprocess.SubprocessError):
            return None
        if out.returncode == 0 and out.stdout.strip():
            dates.append(out.stdout.strip())

    return max(dates) if dates else None


def write_seo_files():
    """robots.txt dan sitemap.xml ikut BASE, jadi tidak ketinggalan saat
    pindah domain — dulu keduanya berkas statis yang mudah terlupakan."""
    with open("robots.txt", "w") as fh:
        fh.write("User-agent: *\nDisallow: /admin\nDisallow: /api\n\n"
                 "Sitemap: %s/sitemap.xml\n" % BASE)

    urls = ""
    for p in PATHS:
        urls += "  <url>\n    <loc>%s%s</loc>\n" % (BASE, p or "/")
        stamp = last_changed(p)
        if stamp:
            urls += "    <lastmod>%s</lastmod>\n" % stamp
        urls += "  </url>\n"
    with open("sitemap.xml", "w") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                 '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                 + urls + "</urlset>\n")
    print("  robots.txt + sitemap.xml (%d halaman)" % len(PATHS))


if __name__ == "__main__":
    print("Membangun situs...")
    main()
    write_seo_files()

    # Form admin dibangkitkan ulang di sini, bukan hanya di laptop, supaya
    # keterangan tiap ruas selalu memantulkan isi terbaru. Kalau hanya dibuat
    # sekali, keterangannya basi begitu teksnya disunting dari /admin.
    try:
        import gen_admin
        gen_admin.main()
    except Exception as err:  # jangan sampai situsnya gagal terbit
        print("  (lewati pembangkitan form admin: %s)" % err)

    print("Selesai.")
