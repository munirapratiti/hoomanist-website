#!/usr/bin/env python3
"""Regenerates admin/config.yml from the extracted content.

The CMS needs every editable field declared up front. Rather than maintain
that list by hand next to content/, it is derived from content/_meta/, so
adding text to a section and re-running extract keeps the admin form in step.

Run after extract.py, or whenever a section gains or loses text.
"""

import json
import os
import re

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


# Peran tiap elemen, dipakai sebagai label. Label harus menggambarkan
# *fungsi* ruasnya, bukan mengutip isinya — kutipan akan basi begitu teksnya
# disunting, dan justru menyesatkan.
ROLE = {
    "h1": "Judul utama",
    "h2": "Judul",
    "h3": "Sub-judul",
    "h4": "Sub-judul",
    "p": "Paragraf",
    "summary": "Pertanyaan",
    "button": "Tombol",
    "a": "Tautan",
    "li": "Butir",
    "label": "Label isian",
    "span": "Teks pendek",
    "div": "Teks pendek",
    "td": "Sel tabel",
    "th": "Kepala tabel",
}


# Nama khusus untuk ruas yang sering dicari dan sulit dikenali dari perannya
# saja — misalnya tiga angka statistik di beranda yang semuanya "teks pendek".
OVERRIDE = {
    ("top", "3"): "Statistik 1 — angka",
    ("top", "years_active"): "Statistik 1 — keterangan",
    ("top", "10_20"): "Statistik 2 — angka",
    ("top", "roles_placed"): "Statistik 2 — keterangan",
    ("top", "90"): "Statistik 3 — angka",
    ("top", "day_guarantee"): "Statistik 3 — keterangan",
    ("top", "where_creative_people_belong"): "Label kecil di atas judul",
    ("top", "good_people_great_work"): "Tulisan tangan (good people. great work.)",
    ("top", "people_presence_purpose"): "Kartu ungu — judul",
    ("top", "the_three_things_we_build_every_engageme"): "Kartu ungu — keterangan",
    ("_section2", "clients_amp_partners_small_but_real_and_"): "Judul bagian klien",
    ("_section2", "every_hire_since_2022_plus_culture_and_r"): "Kartu Sosplan — keterangan",
    ("_section2", "partner_brand_and_creative_team_support"): "Kartu 360 Padel — keterangan",
    ("_section2", "partner_creative_people_partnership"): "Kartu Experia — keterangan",
    ("_section2", "creative_recruitment_and_team_developmen"): "Kartu by.U — keterangan",
}


def strip_tags(v):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", v)).strip()


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
        seen = {}
        for key, m in meta.items():
            value = vals.get(key, "")
            # Long copy gets a textarea; headings and labels stay single-line.
            widget = "text" if len(value) > 70 or "<br" in value else "string"

            # Label menggambarkan peran ruas, bukan mengutip isinya. Kutipan
            # akan basi begitu teksnya disunting dan justru menyesatkan.
            role = ROLE.get(m.get("tag", ""), "Teks")
            seen[role] = seen.get(role, 0) + 1
            label = OVERRIDE.get((stem, key)) or (
                role if seen[role] == 1 else "%s %d" % (role, seen[role]))

            # Isi saat ini jadi keterangan. Berkas ini dibangkitkan ulang tiap
            # build, jadi keterangannya selalu ikut isi terbaru.
            preview = strip_tags(value)
            hint = (preview[:70] + "…") if len(preview) > 70 else preview
            if "<" in value:
                hint = (hint + "  ⚠️ berisi tag HTML — biarkan utuh").strip()

            # Nama ruas selalu dikutip: slug dari angka seperti "90" atau "68"
            # akan dibaca YAML sebagai bilangan, dan Decap menolaknya.
            out += [
                f"          - name: {esc(key)}",
                f"            label: {esc(label)}",
                f"            widget: {widget}",
                "            required: false",
            ]
            if hint:
                out.append(f"            hint: {esc(hint)}")

    with open("admin/config.yml", "w") as fh:
        fh.write("\n".join(out) + "\n")

    fields = sum(len(json.load(open(f"content/_meta/{s}.json")))
                 for s, _ in SECTIONS if os.path.exists(f"content/_meta/{s}.json"))
    print(f"admin/config.yml: {len(SECTIONS)} bagian, {fields} ruas")


if __name__ == "__main__":
    main()
