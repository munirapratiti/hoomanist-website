#!/usr/bin/env python3
"""Assembles the static site from src/ into the deployable HTML files.

Nav and footer live in one place here rather than being copy-pasted into every
page, so a menu change is a one-line edit instead of seven.

Run after editing anything in src/:

    python3 build.py
"""

import os
import re
import shutil

BASE = "https://hoomanist-website.vercel.app"
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
        "title": "Hoomanist — Creative people. Placed with purpose.",
        "desc": "Hoomanist is a creative workforce partner. We help teams hire, "
                "build and keep the people behind great work.",
        "blocks": ["top", "_section2", "_section3", "home-cta"],
    },
    {
        "path": "/services",
        "out": "services/index.html",
        "title": "Services — Hoomanist",
        "desc": "Recruitment, team building and people systems for creative "
                "studios and brands. Pricing that fits the work.",
        "blocks": ["services", "pricing"],
    },
    {
        "path": "/why-us",
        "out": "why-us/index.html",
        "title": "Why Us — Hoomanist",
        "desc": "Your people are the one thing nobody can copy. Why creative "
                "teams work with Hoomanist, and the people behind it.",
        "blocks": ["why", "team"],
    },
    {
        "path": "/proof",
        "out": "proof/index.html",
        "title": "Proof — Hoomanist",
        "desc": "We'd rather show you than tell you. Results from the creative "
                "teams we've built.",
        "blocks": ["proof"],
    },
    {
        "path": "/for-creatives",
        "out": "for-creatives/index.html",
        "title": "For Creatives — Hoomanist",
        "desc": "Looking for a team that actually fits? Share your portfolio "
                "with Hoomanist.",
        "blocks": ["creatives"],
    },
    {
        "path": "/faq",
        "out": "faq/index.html",
        "title": "FAQ — Hoomanist",
        "desc": "Good questions, honest answers about how Hoomanist works.",
        "blocks": ["faq"],
    },
    {
        "path": "/contact",
        "out": "contact/index.html",
        "title": "Contact — Hoomanist",
        "desc": "Let's build better ways of working. Start a discovery "
                "conversation with Hoomanist.",
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
        '      <div class="nav-links" style="display:flex;align-items:center;'
        'gap:38px;font-size:16px;font-weight:500;color:#42485A;">\n        '
        + "\n        ".join(links) +
        '\n      </div>\n'
        '      <a href="/contact" class="btn-primary" '
        'style="background:#3B2145;color:#F6F2E8;font-size:16px;'
        'font-weight:600;padding:13px 26px;border-radius:999px;">'
        "Let's talk</a>\n"
        '    </div>\n  </nav>\n'
    )


def build_footer():
    footer = clean(read(os.path.join(RAW, "_footer12.html")))
    footer = rewrite_links(footer)
    # The footer's "Explore" column still lists the old duplicate menu.
    footer = footer.replace(
        '<a href="/services" class="navlink">What We Do</a>\n          ', '')
    footer = footer.replace(
        '<a href="/services#pricing" class="navlink">Pricing</a>',
        '<a href="/faq" class="navlink">FAQ</a>')
    return footer


def main():
    head_tpl = read(os.path.join(SRC, "head.html"))
    footer = build_footer()

    for page in PAGES:
        body = "\n\n".join(
            rewrite_links(clean(read(os.path.join(RAW, b + ".html"))))
            for b in page["blocks"])

        html = (head_tpl
                .replace("{{TITLE}}", page["title"])
                .replace("{{DESC}}", page["desc"])
                .replace("{{BASE}}", BASE)
                .replace("{{PATH}}", "" if page["path"] == "/" else page["path"]))

        html += build_nav(page["path"]) + "\n" + body + "\n\n" + footer
        html += '\n\n</div>\n<script src="/main.js" defer></script>\n</body>\n</html>\n'

        out = page["out"]
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        with open(out, "w") as fh:
            fh.write(html)
        print("  %-28s %6d bytes" % (out, len(html)))


if __name__ == "__main__":
    print("Membangun situs...")
    main()
    print("Selesai.")
