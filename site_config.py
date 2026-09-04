"""Satu-satunya tempat alamat situs dituliskan.

build.py dan gen_admin.py sama-sama membacanya, dan robots.txt serta
sitemap.xml dibangkitkan darinya — jadi pindah domain cukup mengubah
satu baris di berkas ini.
"""

BASE = "https://hoomanist-website.vercel.app"

PATHS = ["", "/services", "/why-us", "/proof", "/for-creatives", "/faq", "/contact"]
