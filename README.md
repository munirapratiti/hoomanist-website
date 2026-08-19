# Hoomanist Website

Situs statis satu halaman untuk Hoomanist. Tanpa framework, tanpa build step —
HTML, CSS, dan JavaScript biasa. Di-deploy ke Vercel.

## Struktur

| File | Isi |
|---|---|
| `index.html` | Seluruh halaman. Styling utama pakai inline style (bawaan desain). |
| `styles.css` | Style global: reset, tipografi, animasi, breakpoint responsif. |
| `main.js` | Scroll reveal, angka count-up, link email, dan form kontak. |
| `assets/` | Gambar: logo, logo partner, foto tim. |
| `favicon.svg` | Brand mark. |
| `vercel.json` | Cache header dan security header. |

## Menjalankan secara lokal

```bash
python3 -m http.server 8000
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
  scraper. Kalau alamatnya berubah, ubah konstanta `EMAIL` di `main.js` —
  satu tempat, berlaku untuk seluruh halaman.
- **Sumber desain** ada di Claude Design, project "Hoomanist Website".
  File ini hasil konversi dari `Hoomanist Website.dc.html`. Kalau desain di
  sana diubah, perubahannya tidak otomatis masuk ke sini.

## Belum selesai

- **Gambar `og:image`.** Preview link di WhatsApp/LinkedIn/X butuh gambar
  1200×630 px. Simpan sebagai `assets/og-image.png`, lalu tambahkan kembali
  di `<head>`:
  ```html
  <meta property="og:image" content="https://hoomanist-website.vercel.app/assets/og-image.png">
  ```
  dan ubah `twitter:card` menjadi `summary_large_image`.
- **URL di `<link rel="canonical">` dan `og:url`** masih menunjuk ke
  `hoomanist-website.vercel.app`. Ganti kalau nanti pakai domain sendiri.
