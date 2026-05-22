# 👥 TUTORIAL PENGGUNA - Sistem Biometrik Desktop

**Versi 1.0** | Tanggal: April 2026

## Daftar Isi
1. [Perkenalan Sistem](#perkenalan-sistem)
2. [Memulai Aplikasi](#memulai-aplikasi)
3. [Login](#login)
4. [Menu Utama](#menu-utama)
5. [Pendaftaran Pengguna Baru](#pendaftaran-pengguna-baru)
6. [Worst Case Scenarios](#️-worst-case-scenarios)
7. [Panduan Solusi](#🔧-panduan-solusi)
8. [Tips & Trik](#tips--trik)
9. [FAQ](#faq)

---

## 🎯 Perkenalan Sistem

Aplikasi ini adalah sistem **keamanan biometrik berbasis pengenalan wajah** yang memungkinkan:

✅ **Pendaftaran wajah** - Simpan data wajah pengguna  
✅ **Verifikasi identitas** - Cek siapa yang hadir melalui kamera  
✅ **Manajemen data pengguna** - Tambah, ubah, hapus data pengguna  
✅ **Riwayat akses** - Lihat log siapa saja yang masuk  

---

## 🚀 Memulai Aplikasi

### Langkah 1: Nyalakan Aplikasi

1. Klik icon aplikasi desktop atau double-click file executable
2. Tunggu 3-5 detik sampai jendela aplikasi terbuka
3. Anda akan melihat layar **Login**

### Langkah 2: Siapkan Perangkat

Sebelum mulai:
- ✅ Pastikan **webcam sudah terpasang** (USB atau built-in)
- ✅ Periksa **pencahayaan bagus** (cukup terang di area wajah)
- ✅ Pastikan **koneksi internet stabil** (jika terhubung ke server)

---

## 🔐 Login

### Cara Login

1. **Masukkan Username Admin**
   - Field: "Username"
   - Contoh: `admin` atau `operator`

2. **Masukkan Password**
   - Field: "Password"
   - Karakter password disembunyikan untuk keamanan

3. **Klik Tombol Login**
   - Jika credentials benar → Masuk ke Dashboard
   - Jika salah → Muncul pesan error, silakan coba lagi

### Lupa Password?

Hubungi Administrator atau Teknisi sistem untuk reset password.

---

## 📊 Menu Utama

Setelah login, Anda akan melihat Dashboard dengan menu di sebelah kiri:

```
┌─────────────────────────────────┐
│      SISTEM BIOMETRIK WAJAH     │
├─────────────────────────────────┤
│                                 │
│ 📊 Dashboard                    │
│ 👤 Data Pengguna                │
│ ✏️  Pendaftaran / Perbarui       │
│ 📋 Riwayat Akses                │
│ ⚙️  Pengaturan                   │
│ 🚪 Logout                       │
│                                 │
└─────────────────────────────────┘
```

### 1️⃣ Dashboard

**Fungsi:** Menampilkan ringkasan sistem secara real-time

Anda akan melihat:
- 📈 **Total Users** - Jumlah pengguna terdaftar dalam sistem
- 📊 **Attendance Today** - Jumlah akses/absensi hari ini dari semua sumber (lokal, Raspy, spreadsheet)
- 🟢 **System Status** - Status koneksi sistem (Online/Offline) dengan pesan status
- 📋 **Recent Activity** - Tabel log aktivitas akses terbaru dengan waktu, nama, ringkasan, status, dan sumber data

**Aksi:** Dashboard otomatis refresh setiap 10 detik. Anda juga bisa manual refresh dengan klik tombol "Refresh"

### 2️⃣ Data Pengguna

**Fungsi:** Mengelola daftar pengguna terdaftar

**Fitur:**
- 🔍 **Cari pengguna** - Ketik nama, role, username, atau ID di search box
- ✏️ **Edit data** - Ubah nama lengkap, role, atau username pengguna (admin only)
- 📷 **Retrain wajah** - Ambil ulang foto wajah untuk pengguna (icon kamera, admin only)
- 🗑️ **Hapus pengguna** - Hapus pengguna dari sistem (admin only)

**Informasi yang ditampilkan:**
- ID Pengguna
- Nama Lengkap
- Role (admin, coadmin, member)
- Username Login
- Status Face (jumlah embeddings atau "Belum")
- Status Fingerprint (ID atau "Belum")
- Sumber (local / raspy-sync)
- Tanggal Registrasi

### 3️⃣ Pendaftaran / Perbarui

**Fungsi:** Mendaftarkan pengguna baru atau memperbarui data wajah pengguna yang sudah ada

**Opsi yang tersedia:**
- ➕ **Pengguna Baru** - Daftar pengguna baru dengan ambil foto wajah
- 🔄 **Perbarui Pengguna Lama** - Ambil ulang foto wajah untuk pengguna yang sudah terdaftar

Lihat [Pendaftaran Pengguna Baru](#pendaftaran-pengguna-baru) di bawah untuk panduan detail step-by-step.

### 4️⃣ Riwayat Akses

**Fungsi:** Melihat log detail semua aktivitas akses dari semua sumber (lokal, Raspy, spreadsheet)

**Informasi yang ditampilkan:**
- Waktu akses (tanggal & jam)
- Employee ID (jika ada)
- Nama pengguna
- Domisili (lokasi dari data spreadsheet, jika ada)
- Status akses (Success / Failed / No Match)
- Akses type (masuk/keluar atau custom dari sumber)

**Filter yang tersedia:**
- 🔍 **Search** - Cari berdasarkan nama, event, metode, atau sumber
- 📊 **Filter Sumber** - Pilih sumber data:
  - **Semua** - Tampilkan dari semua sumber
  - **Local** - Hanya dari database lokal aplikasi
  - **Raspy** - Hanya dari server Raspy
  - **Spreadsheet** - Hanya dari spreadsheet yang tersinkronisasi

### 5️⃣ Pengaturan

**Fungsi:** Mengatur konfigurasi integrasi sistem dengan Raspy dan Spreadsheet

**Opsi yang tersedia:**
- 🔗 **Raspy API Base URL** - Alamat server Raspy (contoh: `http://192.168.1.10:5000`)
- 🔗 **Device Mode Endpoint** - Endpoint untuk mengubah mode alat di Raspy
- 📊 **Spreadsheet CSV URL** - URL Google Sheets atau sumber data eksternal (format CSV)
- 📊 **Spreadsheet Mode** - Aktifkan/nonaktifkan sinkronisasi data dari spreadsheet
- ✅ **Test Koneksi Raspy** - Periksa apakah Raspy terkoneksi
- ✅ **Jalankan Diagnostics** - Jalankan diagnostik lengkap sistem Raspy
- ✅ **Test Spreadsheet** - Validasi format dan akses spreadsheet

**Catatan:** Setting untuk threshold pengenalan, resolusi webcam, dan brightness/contrast masih dikembangkan dan akan tersedia di update selanjutnya.

---

## 📝 Pendaftaran Pengguna Baru

### Proses Pendaftaran (Step-by-Step)

#### Step 1: Isi Data Dasar Pengguna

1. Klik menu **"Pendaftaran / Perbarui"**
2. Pilih tombol **"Pengguna Baru"**
3. Isi form dengan data:
   - **ID Pengguna*** (required): `12345` atau `john_doe`
   - **Nama Lengkap** (optional): `Budi Santoso`
   - **Departemen**: `IT` / `HR` / `Production`
   - **Email**: `budi@company.com`

   *Field dengan * adalah wajib diisi

4. Klik **"Lanjut"**

#### Step 2: Siapkan Webcam

1. Layar akan menampilkan preview webcam
2. Posisikan **wajah Anda di tengah-tengah frame** (dalam kotak merah/hijau)
3. Pastikan pencahayaan cukup:
   - ✅ Cahaya dari depan (tidak backlight)
   - ✅ Tidak ada bayangan di wajah
   - ✅ Wajah terlihat jelas (tidak blur)

#### Step 3: Ambil Foto Wajah

1. Klik tombol **"Ambil Foto"** untuk setiap sudut wajah

   **Rekomendasi 10-15 foto dengan variasi:**
   - Pandangan lurus ke depan (3-4 foto)
   - Kepala sedikit miringke kiri (2-3 foto)
   - Kepala sedikit miring ke kanan (2-3 foto)
   - Kepala menengadah sedikit (2-3 foto)
   - Kepala menunduk sedikit (2-3 foto)

2. Setiap foto yang berhasil akan muncul di grid preview bawah

3. **Tips saat ambil foto:**
   - Gerakkan kepala perlahan-lahan
   - Jangan mengedipkan mata
   - Ekspresi wajah normal (tidak tersenyum terlalu lebar)
   - Minimal jarak: 30cm dari kamera

4. Ketika sudah cukup (minimal 10 foto), klik **"Lanjut"**

#### Step 4: Proses Training Wajah (Otomatis)

1. Klik tombol **"Mulai Training Wajah"**

2. Sistem akan:
   - 🔄 Memproses augmentasi foto (membuat variasi)
   - 🧠 Menganalisis fitur wajah
   - 💾 Menyimpan data wajah (embeddings)

3. **Tunggu proses selesai** (biasanya 1-2 menit)
   
   Anda akan melihat:
   ```
   ⏳ Memproses augmentasi dan ekstrak embedding...
   ⏳ Fase 1: Deteksi wajah (10 foto)
   ⏳ Fase 2: Generate augmentasi (500 variasi)
   ⏳ Fase 3: Extract embedding (ekstrak fitur)
   ✅ Training berhasil! 10 × 50 = 500 embeddings
   ```

4. Jika berhasil → Klik **"Selesai"**

   Jika ada error → Lihat [Troubleshooting](#faq) di bawah

#### Step 5: Verifikasi Pendaftaran

1. Sistem akan menampilkan ringkasan:
   - ✓ Pengguna: [nama]
   - ✓ Wajah terdaftar: [status]
   - ✓ Embeddings: [jumlah]

2. Klik **"Kembali ke Dashboard"** untuk selesai

### Perbarui Wajah Pengguna Lama

1. Klik menu **"Pendaftaran / Perbarui"**
2. Pilih tombol **"Perbarui Pengguna Lama"**
3. **Cari pengguna** yang akan diperbarui dari dropdown list
4. Ikuti langkah yang sama seperti Step 2-5 di atas
5. Wajah lama akan diganti dengan yang baru

---

## ⚠️ Worst Case Scenarios

Berikut adalah daftar masalah/error yang mungkin terjadi saat menggunakan aplikasi:

1. ❌ **Login Gagal** - Muncul pesan error "Invalid credentials" atau "User not found"
2. ❌ **Dashboard Error / Tidak Muncul** - Dashboard blank, loading terus-menerus, atau error message
3. ❌ **Search Pengguna Tidak Bekerja** - Ketik nama/ID di search box tapi data tidak filter
4. ❌ **Enrollment / Training Wajah Error** - Proses training gagal, muncul error, atau stuck di loading
5. ❌ **Raspy Connection Error** - System Status menunjukkan "Offline", Test Connection gagal
6. ❌ **Edit / Delete Pengguna Gagal** - Tombol edit/delete tidak bekerja atau data tidak berubah
7. ❌ **Spreadsheet Sync Error** - Spreadsheet data tidak muncul di Recent Activity atau Access Logs
8. ❌ **Access Logs Tidak Tampil** - Riwayat Akses page blank atau kosong
9. ❌ **Aplikasi Crash / Freeze** - Aplikasi suddenly close atau UI hang/tidak responsif
10. ❌ **Settings Tidak Bisa Disimpan** - Klik "Simpan Settings" tapi tidak ada konfirmasi

---

## 🔧 Panduan Solusi

### ✅ 1. Login Gagal

**Penyebab & Solusi:**
| Penyebab | Solusi |
|---------|--------|
| Username/Password salah | Pastikan username dan password benar. Default: `admin` / `admin123` |
| Capslock aktif | Tekan Capslock untuk menonaktifkan |
| Database lokal corrupt | Hubungi administrator untuk reset database atau clear cache aplikasi |
| Akun belum terdaftar | Minta admin untuk buat akun baru di sistem |

---

### ✅ 2. Dashboard Error / Tidak Muncul

**Penyebab & Solusi:**
| Penyebab | Solusi |
|---------|--------|
| Koneksi ke backend terputus | Periksa internet connection, restart aplikasi |
| API server sedang down | Tunggu beberapa saat, atau hubungi admin untuk restart backend |
| Database lokal corrupt | Clear aplikasi cache: `Ctrl+Shift+Delete` → Clear Cache & Cookies |
| Port backend sudah digunakan | Pastikan tidak ada aplikasi lain yang pakai port yang sama (default: 5000) |

**Percobaan lanjutan:**
1. Buka DevTools: `F12` → Console tab
2. Lihat error message detail
3. Screenshot dan kirim ke administrator

---

### ✅ 3. Search Pengguna Tidak Bekerja

**Penyebab & Solusi:**
| Penyebab | Solusi |
|---------|--------|
| Belum ada data pengguna | Daftar pengguna baru terlebih dahulu di "Pendaftaran / Perbarui" |
| Search case-sensitive | Coba gunakan huruf kecil atau besar sesuai database |
| UI belum refresh | Klik tombol "Refresh" di atas tabel |
| Koneksi database unstable | Coba logout, login kembali |

---

### ✅ 4. Enrollment / Training Wajah Error

**Penyebab & Solusi:**

**4a. Webcam tidak terdeteksi**
| Gejala | Solusi |
|--------|--------|
| Preview webcam hitam/blank | Cek apakah webcam USB terpasang atau built-in sudah on |
| Error "Camera not accessible" | Tutup aplikasi lain yang pakai webcam (Zoom, Teams, dll) |
| Driver webcam tidak installed | Install/update driver webcam di Device Manager |
| Permission denied | Izinkan aplikasi akses kamera di Windows Settings → Privacy → Camera |

**4b. Foto tidak tersimpan**
| Gejala | Solusi |
|--------|--------|
| Tombol "Ambil Foto" tidak respons | Tunggu beberapa detik, mungkin sedang process |
| Foto blur / tidak terdeteksi wajah | Pastikan pencahayaan cukup, wajah jelas di tengah frame |
| Grid preview kosong setelah klik | Bersihkan lensa webcam, jauhkan dari backlight |

**4c. Training gagal / timeout**
| Gejala | Solusi |
|--------|--------|
| Loading "Memproses augmentasi..." tidak selesai (> 5 menit) | Proses Python backend sedang heavy, tunggu atau restart |
| Error "Training failed" | Coba enroll dengan 10-12 foto terlebih dahulu (tidak perlu 15+) |
| "Insufficient embeddings" error | Pastikan minimal 10 foto sudah tersimpan sebelum start training |

**Solusi umum:**
1. Reload aplikasi: `Ctrl+Shift+R` (clear cache reload)
2. Restart backend server
3. Hubungi admin dengan screenshot error message

---

### ✅ 5. Raspy Connection Error

**Penyebab & Solusi:**
| Penyebab | Solusi |
|---------|--------|
| Raspy IP Address salah | Cek di Settings → Raspy API Base URL (pastikan formatnya `http://192.168.x.x:5000`) |
| Raspy server sedang offline | Hubungi teknisi untuk restart Raspy |
| Network unreachable | Ping Raspy dari CMD: `ping 192.168.x.x` |
| Firewall blocked connection | Whitelist IP Raspy di Windows Firewall atau router |
| Wrong endpoint | Cek di Settings → Device Mode Endpoint (default: `/api/device/mode`) |

**Test di Settings:**
1. Klik menu "Pengaturan"
2. Isi Raspy API URL dengan benar
3. Klik "Test Koneksi Raspy" → tunggu hasil
4. Jika gagal, lihat error message di dialog

---

### ✅ 6. Edit / Delete Pengguna Gagal

**Penyebab & Solusi:**
| Penyebab | Solusi |
|---------|--------|
| Bukan role Admin | Hanya Admin yang bisa edit/delete. CoAdmin hanya bisa view & add |
| User tidak bisa dihapus (sedang dipakai) | Periksa apakah user masih ada di access logs recent |
| Koneksi terputus saat save | Cek internet, coba lagi |
| Data validation error | Pastikan field Name tidak kosong, Username unik |

**Langkah troubleshoot:**
1. Refresh table: klik "Refresh" button
2. Logout-login kembali
3. Hubungi admin jika masih gagal

---

### ✅ 7. Spreadsheet Sync Error

**Penyebab & Solusi:**
| Penyebab | Solusi |
|---------|--------|
| Spreadsheet Mode tidak aktif | Klik Settings → toggle "Spreadsheet Mode" ke "Aktif" |
| URL spreadsheet salah/tidak accessible | Pastikan format CSV URL benar dan sheet bisa diakses publik |
| Format CSV tidak sesuai | Cek tutorial di Settings → klik "Test Spreadsheet" untuk debug |
| Sharing permission error | Buat link share spreadsheet dengan akses "View anyone" |
| Rate limit Google Sheets | Tunggu beberapa menit sebelum test ulang |

**Test di Settings:**
1. Isi Spreadsheet CSV URL dengan benar
2. Klik "Test Spreadsheet" button
3. Lihat hasil: jika OK, baris data akan terlihat preview-nya

---

### ✅ 8. Access Logs Tidak Tampil

**Penyebab & Solusi:**
| Penyebab | Solusi |
|---------|--------|
| Belum ada aktivitas akses sama sekali | Lakukan enrollment/training wajah untuk generate log |
| Filter Sumber terlalu ketat | Ubah filter dari "Local" ke "Semua" untuk lihat dari semua sumber |
| Search keyword terlalu spesifik | Kosongkan search box atau pakai keyword yang lebih umum |
| Database lokal belum sync | Klik "Refresh" button untuk manual sync |

---

### ✅ 9. Aplikasi Crash / Freeze

**Penyebab & Solusi:**
| Penyebab | Solusi |
|---------|--------|
| Memory leak dari webcam (setelah long session) | Restart aplikasi setiap 2-3 jam penggunaan heavy |
| Process Python backend crash | Restart backend service dari admin panel |
| Terlalu banyak data di Recent Activity | Clear old logs atau filter data |
| Windows resource issue | Close aplikasi lain yang heavy (Chrome, Photoshop, dll) |

**Saat Freeze:**
1. Tunggu 10 detik
2. Jika tetap freeze, force close: `Alt+F4` atau Task Manager `Ctrl+Shift+Esc` → kill process
3. Restart aplikasi

---

### ✅ 10. Settings Tidak Bisa Disimpan

**Penyebab & Solusi:**
| Penyebab | Solusi |
|---------|--------|
| Field URL invalid | Pastikan format URL benar, contoh: `http://192.168.1.10:5000` (jangan lupa `http://`) |
| Backend validation error | Periksa console error (F12) untuk detail |
| API timeout | Tunggu beberapa saat, coba lagi |
| Permission denied | Pastikan Anda login sebagai Admin |

**Tips:**
- Jangan ganti banyak field sekaligus, test satu per satu
- Setelah simpan, tunggu "✅ Settings integrasi berhasil disimpan" toast notification

---
##  Tips & Trik

### Mendapatkan Hasil Terbaik

| Situasi | Tips |
|---------|------|
| **Pencahayaan buruk** | Pastikan cahaya dari depan, gunakan lampu tambahan jika perlu |
| **Glasses/Kacamata** | Usahakan minimal 10-15 foto, termasuk dengan kacamata |
| **Rambut panjang** | Pastikan wajah tidak tertutup rambut |
| **Jenggot/Cambang** | Letakkan dengan rapi, hindari pencahayaan aneh |
| **Masker/Scarf** | Gunakan untuk training jika akan sering pakai masker |

### Konsistensi Adalah Kunci

✅ Pencahayaan yang sama saat enrollment & verifikasi = Hasil lebih baik  
✅ Semakin banyak foto training = Semakin akurat pengenalan  
✅ Beragam sudut wajah = Sistem lebih robust terhadap variasi  

### Ketika Perlu Re-training

- Jika Anda potong rambut drastis
- Jika Anda tambah/lepas kacamata permanen
- Jika Anda ubah status jenggot/cambang
- Jika hasil verifikasi drop signifikan (< 70%)

---

## ❓ FAQ

### Q: Berapa lama proses training?
**A:** Biasanya 1-3 menit tergantung jumlah foto dan spesifikasi komputer. Proses pertama lebih lambat karena loading model.

### Q: Apa itu "Similarity Score"?
**A:** Angka 0-100% yang menunjukkan tingkat kesamaan wajah dengan data database. Semakin tinggi = semakin mirip. Minimum threshold biasanya 60%.

### Q: Bagaimana jika lupa login?
**A:** Hubungi Administrator untuk reset password. Tidak ada mekanisme self-service saat ini.

### Q: Apakah data wajah aman?
**A:** Ya! Data wajah (embeddings) disimpan dalam database terenkripsi dan hanya bisa diakses di sistem tertutup. Data asli foto tidak disimpan.

### Q: Bisa di-share ke device lain?
**A:** Tidak. Setiap desktop app memiliki database lokal sendiri. Untuk multi-device, hubungi teknisi untuk setup dengan Raspy central server.

### Q: Apa yang terjadi jika webcam error?
**A:** Aplikasi akan menampilkan error message. Cek:
1. Kabel USB webcam terpasang
2. Tidak ada aplikasi lain yang pakai webcam
3. Driver webcam ter-install dengan benar
4. Restart aplikasi

### Q: Berapa user maksimal yang bisa terdaftar?
**A:** Sistem support ribuan user. Performa tergantung spesifikasi komputer dan Raspy.

### Q: Bagaimana kalau threshold terlalu tinggi/rendah?
**A:** 
- **Terlalu tinggi** → Banyak false negative (orang tidak dikenali)
- **Terlalu rendah** → Banyak false positive (orang salah dikenali)

Untuk sekarang, setting threshold masih di level backend/Raspy. Hubungi administrator teknis untuk adjust konfigurasi threshold sistem.

### Q: Bisa export data riwayat akses?
**A:** Belum tersedia di versi ini. Fitur export akan ditambahkan di update selanjutnya.

### Q: Apakah sistem bisa offline?
**A:** Ya! Sistem bisa bekerja hanya dengan database lokal. Tapi jika ada Raspy, disarankan tetap online untuk sinkronisasi.

---

## 📞 Hubungi Support

**Untuk pertanyaan atau masalah:**
- 📧 Email: `support@company.com`
- 📞 Telepon: `+62-XXX-XXXX-XXXX`
- 🕐 Jam kerja: Senin-Jumat, 08:00-17:00 WIB

---

## 📝 Catatan Penting

⚠️ **PRIVASI WAJAH:** Data wajah Anda disimpan aman dan hanya digunakan untuk keperluan keamanan sistem.

⚠️ **JANGAN:** 
- ❌ Bagikan password login
- ❌ Ubah setting tanpa izin Admin
- ❌ Lepas/pindahkan webcam tanpa izin

✅ **LAKUKAN:**
- ✅ Logout setelah selesai
- ✅ Report error ke Admin
- ✅ Update wajah jika ada perubahan penampilan drastis

---

**Selamat menggunakan Sistem Biometrik Wajah!** 🎉
