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

- **Lisensi foto stock.** `assets/photo-team.jpg` berasal dari berkas unduhan
  di folder Downloads dan tampak seperti foto stock. Sebelum situs dipakai
  untuk keperluan komersial, pastikan lisensinya memadai — sebagian penyedia
  mewajibkan atribusi pada paket gratisnya. Ini perlu dicek oleh pemilik situs.


- **Gambar `og:image`** untuk preview link di WhatsApp/LinkedIn/X. Perlu 1200×630
  px, simpan sebagai `assets/og-image.png`, lalu tambahkan di `src/head.html`
  dan ubah `twitter:card` menjadi `summary_large_image`.
- **URL di `canonical` dan `og:url`** memakai konstanta `BASE` di `build.py`.
  Ganti satu baris itu kalau pindah ke domain sendiri.

## Menyiapkan gambar

Gambar mentah biasanya jauh lebih besar dari kebutuhan tampil. Berkas asli
disimpan di `source/` (tidak ikut Git). Pemrosesan memakai `sips`, bawaan
macOS — tidak perlu memasang apa pun:

```bash
# potong kotak: -c tinggi lebar, --cropOffset dari atas dan dari kiri
sips -c 2100 2100 --cropOffset 1400 724 source/IMG_5647.JPG --out /tmp/crop.jpg
sips -Z 256 /tmp/crop.jpg --out assets/team-munira.jpg
```

Ukuran tampil avatar 108 px, jadi 256 px sudah cukup untuk layar retina.
Foto Munira turun dari 7,2 MB menjadi 13 KB dengan cara ini.

Pada foto Tito ada logo Sosplan di kaosnya. Logo itu tidak dihapus dengan
menyunting piksel — batas bawah potongan cukup disetel di atas garis logo
(y=2250 dari tinggi 4000), sehingga logo tidak pernah masuk frame. Kalau
suatu saat perlu potongan yang lebih lebar, logonya akan muncul lagi.
