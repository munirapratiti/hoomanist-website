# Petunjuk untuk Claude

Situs company profile Hoomanist. HTML/CSS/JS statis tanpa framework, dirakit
`build.py` (Python 3, **tanpa Node**), deploy otomatis ke Vercel via GitHub.
Live di <https://hoomanist.id>. Lihat `README.md` untuk penjelasan lengkap.

## Aturan yang kalau dilanggar merusak diam-diam

**Berkas HTML di root adalah keluaran, bukan sumber.** `index.html`,
`services/index.html`, dan seterusnya dibangkitkan `build.py`. Menyuntingnya
langsung terasa berhasil, lalu hilang tanpa pesan error di build berikutnya.
Sumbernya: `src/raw/*.html` (tata letak) + `content/*.json` (teks).

**Jalankan `python3 build.py` setelah menyunting `src/` atau `content/`.**
Tanpa itu perubahan tidak muncul di halaman.

**`extract.py` hanya sekali jalan, jangan pernah dijalankan lagi.** Dulu ia
mengangkat teks dari HTML ke `content/`. Sekarang `src/raw/*.html` berisi
`{{placeholder}}`, bukan teks — menjalankannya lagi akan mengekstrak
placeholder itu sendiri dan merusak seluruh template.

**`git pull` sebelum mulai menyunting.** Pemilik situs menyunting sendiri
lewat CMS di `/admin`, dan simpanannya jadi commit langsung ke `main`.
Tanpa pull dulu, editannya tertimpa.

**Teks baru harus ditambahkan ke dua tempat**: `content/<bagian>.json` (isi)
dan `content/_meta/<bagian>.json` (jenis tag + label untuk form admin).
Kalau meta-nya lupa, ruas itu tidak muncul di `/admin`.

**Alamat situs hanya ditulis di `site_config.py`.** `build.py`, `gen_admin.py`,
`robots.txt`, dan `sitemap.xml` semua mengikutinya. Jangan tulis ulang URL
di tempat lain.

**Alamat email sengaja tidak ada di HTML.** Disusun saat runtime di `main.js`
(konstanta `EMAIL`) sebagai penghambat scraper. Jangan "dirapikan" dengan
menuliskannya langsung ke markup.

## Hal yang butuh keputusan pemilik, bukan diputuskan sendiri

**Jangan mengarang klaim tentang bisnisnya.** Testimoni, nama klien, angka
hasil kerja, skema harga, dan janji layanan hanya boleh ditulis kalau pemilik
situs mengonfirmasinya. Situs ini dibaca calon klien; klaim yang meleset
merugikan mereka secara nyata.

**Foto hanya dari sumber berlisensi jelas** — Unsplash atau Pexels — dan
tautan asalnya dicatat di bagian "Asal gambar" di `README.md`. Pernah ada
foto dari magnific.com yang status lisensinya tidak bisa dipastikan lalu
diganti; jangan pakai sumber itu lagi.

**Testimoni harus memakai foto orang aslinya**, bukan stock. Foto stock yang
mewakili orang sungguhan adalah kebohongan ke pengunjung.

## Cara kerja sehari-hari

```bash
git pull                       # selalu, sebelum menyunting apa pun
python3 build.py               # setelah mengubah src/ atau content/
python3 -m http.server 8000    # pratinjau di http://localhost:8000
```

Commit lalu `git push` ke `main` — Vercel menjalankan `build.py` sendiri saat
deploy, jadi situs terbarui sekitar satu menit kemudian.

Kalau domain berubah, **Redirect URI di OAuth App GitHub wajib ikut diubah**
(github.com/settings/developers → Hoomanist Admin), kalau tidak login `/admin`
akan ditolak. Ini di luar repo dan paling mudah terlupakan.
