#!/usr/bin/env python3
"""Regenerates admin/config.yml from the extracted content.

The CMS needs every editable field declared up front. Rather than maintain
that list by hand next to content/, it is derived from content/_meta/, so
adding text to a section and re-running extract keeps the admin form in step.

Run after extract.py, or whenever a section gains or loses text.
"""

import json
import os

REPO = "munirapratiti/hoomanist-website"
SITE = "https://hoomanist-website.vercel.app"

# Section file -> the label the editor sees. Ordered as they appear on the site.
SECTIONS = [
    ("top",        "Beranda — Bagian atas"),
    ("_section2",  "Beranda — Klien & partner"),
    ("_section3",  "Beranda — Kenapa ini penting"),
    ("home-cta",   "Beranda — Ajakan hubungi"),
    ("services",   "Services"),
    ("pricing",    "Services — Harga"),
    ("why",        "Why Us"),
    ("team",       "Why Us — Profil tim"),
    ("proof",      "Proof"),
    ("creatives",  "For Creatives"),
    ("faq",        "FAQ"),
    ("contact",    "Contact"),
    ("_footer12",  "Footer"),
]


def esc(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main():
    out = [
        "# Dibangkitkan oleh gen_admin.py — jangan disunting langsung.",
        "backend:",
        "  name: github",
        f"  repo: {REPO}",
        "  branch: main",
        f"  base_url: {SITE}",
        "  auth_endpoint: api/auth",
        "",
        "media_folder: assets",
        "public_folder: /assets",
        "",
        "collections:",
        "  - name: isi",
        "    label: Isi Website",
        "    files:",
    ]

    for stem, label in SECTIONS:
        meta_path = f"content/_meta/{stem}.json"
        val_path = f"content/{stem}.json"
        if not os.path.exists(meta_path):
            continue
        meta = json.load(open(meta_path))
        vals = json.load(open(val_path))

        out += [
            f"      - name: {stem.strip('_')}",
            f"        label: {esc(label)}",
            f"        file: {val_path}",
            "        format: json",
            "        fields:",
        ]
        for key, m in meta.items():
            value = vals.get(key, "")
            # Long copy gets a textarea; headings and labels stay single-line.
            widget = "text" if len(value) > 70 or "<br" in value else "string"
            # Nama ruas selalu dikutip: slug dari angka seperti "90" atau "68"
            # akan dibaca YAML sebagai bilangan, dan Decap menolaknya.
            out += [
                f"          - name: {esc(key)}",
                f"            label: {esc(m['label'])}",
                f"            widget: {widget}",
                "            required: false",
            ]

    with open("admin/config.yml", "w") as fh:
        fh.write("\n".join(out) + "\n")

    fields = sum(len(json.load(open(f"content/_meta/{s}.json")))
                 for s, _ in SECTIONS if os.path.exists(f"content/_meta/{s}.json"))
    print(f"admin/config.yml: {len(SECTIONS)} bagian, {fields} ruas")


if __name__ == "__main__":
    main()
