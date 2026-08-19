# Hoomanist Website

Situs statis satu halaman untuk Hoomanist. Tanpa framework, tanpa build step —
HTML, CSS, dan JavaScript biasa. Di-deploy ke Vercel.

## Struktur

Situs multi-halaman. **File HTML di root adalah hasil bangunan — jangan diedit
langsung**, karena akan tertimpa. Edit sumbernya di `src/`, lalu jalankan
`python3 build.py`.

| Path | Isi |
|---|---|
| `build.py` | Perakit situs. Berisi daftar halaman, menu, dan judul/deskripsi SEO. |
| `src/head.html` | Template `<head>` untuk semua halaman. |
| `src/raw/*.html` | Potongan konten tiap section, hasil ekstraksi dari desain. |
| `styles.css` | Style global: reset, tipografi, animasi, breakpoint responsif. |
| `main.js` | Scroll reveal, angka count-up, link email, form kontak. |
| `assets/` | Gambar: logo, logo partner, foto tim. |
| `vercel.json` | Cache header dan security header. |

Halaman yang dihasilkan: `/`, `/services`, `/why-us`, `/proof`,
`/for-creatives`, `/faq`, `/contact`.

Nav dan footer dibangkitkan satu kali di `build.py`, jadi menambah atau
mengubah menu cukup satu baris — tidak perlu menyunting tujuh berkas.

## Menjalankan secara lokal

```bash
python3 build.py && python3 -m http.server 8000
```

Lalu buka <http://localhost:8000>. Tidak perlu Node.

## Deploy

Setiap `git push` ke branch `main` memicu deploy otomatis di Vercel.
Push ke branch lain menghasilkan preview URL terpisah.

## Catatan

- **Form kontak tidak punya backend.** Form menyusun link `mailto:` dan
  menyerahkannya ke aplikasi email pengunjung. Tidak ada data yang dikirim ke
  server mana pun. Kalau nanti butuh form yang benar-benar mengirim ke inbox,
  perlu tambahan layanan seperti Formspree atau Vercel Functions.
- **Alamat email disusun di `main.js`, bukan ditulis di HTML.** Ini menghambat
  scraper. Kalau alamatnya berubah, ubah konstanta `EMAIL` di `main.js`.
- **Sumber desain** ada di Claude Design, project "Hoomanist Website".
  Konversinya satu arah — perubahan di sana tidak mengalir ke sini.

## Belum selesai

- **Dua gambar belum ada** dan harus diunduh manual dari Claude Design ke
  `assets/`: `logo-experia-sm.png` dan `team-munira-sm.jpg` (simpan sebagai
  `team-munira-sm.png`). Keduanya melebihi batas 256 KB alat pengambil berkas.

  Logo ikon diambil dari berkas brand asli di
  `PT Kinarya Nara Kolektif/Hoomanist/Brand Identity/Hoomanist Logo/Icon PNG 1.png`,
  dipotong dari kanvas 2000x2000 (isinya hanya 39%) dan diskalakan ke 128 px.
- **Gambar `og:image`** untuk preview link di WhatsApp/LinkedIn/X. Perlu 1200×630
  px, simpan sebagai `assets/og-image.png`, lalu tambahkan di `src/head.html`
  dan ubah `twitter:card` menjadi `summary_large_image`.
- **URL di `canonical` dan `og:url`** memakai konstanta `BASE` di `build.py`.
  Ganti satu baris itu kalau pindah ke domain sendiri.
