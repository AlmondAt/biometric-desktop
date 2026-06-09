# Attendance Spreadsheet Template Instructions

## Overview
Template ini menunjukkan struktur kolom yang digunakan oleh sistem Biometric Desktop untuk mencatat absensi ke Google Sheets.

## Struktur Kolom

| No | Kolom | Tipe | Sumber | Keterangan |
|----|-------|------|--------|-----------|
| 1 | **ID** | Integer | Database | User ID dari sistem biometric |
| 2 | **Nama** | Text | Database | Nama lengkap pengguna |
| 3 | **Job** | Text | User Input | Pilihan Job (PS Muro, Dasar Menengah, Lanjut) |
| 4 | **Domain** | Text | User Input | Lokasi Lab (Lab Depok, Lab Kalimalang, Lab Karawaci) |
| 5 | **Domisili** | Text | User Input | Asal/Lokasi tempat tinggal |
| 6 | **Shift_A** | Boolean (0/1) | User Input | Apakah hadir di Shift A |
| 7 | **Shift_B** | Boolean (0/1) | User Input | Apakah hadir di Shift B |
| 8 | **Shift_C** | Boolean (0/1) | User Input | Apakah hadir di Shift C |
| 9 | **Shift_D** | Boolean (0/1) | User Input | Apakah hadir di Shift D |
| 10 | **Shift_E** | Boolean (0/1) | User Input | Apakah hadir di Shift E |
| 11 | **Tanggal** | Date | System | Tanggal absensi (YYYY-MM-DD) |
| 12 | **Waktu** | Time | System | Waktu absensi (HH:MM:SS) |
| 13 | **Status** | Text | System | Registered / Unregistered |
| 14 | **Akses** | Integer | System | Nomor akses (sequence number) |
| 15 | **Metode** | Text | System | biometrik / manual |
| 16 | **Foto** | File Path | System | Path ke foto yang diambil |

## Cara Menggunakan

### 1. Import ke Google Sheets
```
1. Buka Google Sheets baru
2. File → Import → Upload tab
3. Pilih file Attendance_Template.csv
4. Pilih opsi "Insert new sheet"
5. Click "Import data"
```

### 2. Setup Formulas
Anda bisa menambahkan formula di Google Sheets:
- Autosum untuk total kehadiran per shift
- Format conditional untuk status unregistered
- Chart untuk visualisasi attendance

### 3. Configuration di Raspberry Pi
```yaml
# config.yaml
google_sheets:
  web_app_url: "https://script.google.com/macros/.../usercontent"
```

## Field Descriptions

### Auto-Generated Fields (dari Raspberry Pi)
- **ID**: Diambil dari database fingerprint/face
- **Nama**: Nama yang terdaftar di sistem
- **Tanggal**: Timestamp saat absensi diproses
- **Waktu**: Waktu proses (HH:MM:SS)
- **Status**: Berdasarkan kecocokan biometric
- **Akses**: Nomor urut submission untuk user
- **Metode**: Selalu "biometrik"
- **Foto**: Path ke foto yang diambil saat verifikasi

### User Input Fields
- **Job**: Pengguna memilih dari menu sebelum absensi
- **Domain**: Pengguna memilih lokasi lab
- **Domisili**: Pengguna input domisili/asal
- **Shift_A-E**: Pengguna memilih shift yang dihadiri

### Data Type Notes
- **Boolean fields (Shift_A-E)**: 1 = Ya/Hadir, 0 = Tidak
- **Status**: "Registered" jika user terdaftar, "Unregistered" jika tidak dikenali
- **Akses**: Increment otomatis per submission per user

## Example Data

### Registered User (Success)
```
101,John Doe,PS Muro,Lab Depok,Jakarta,1,1,0,0,0,2026-06-09,14:30:15,Registered,1,biometrik,/photos/101_001.jpg
```
- User dikenali ✅
- Memilih Job: PS Muro
- Memilih Domain: Lab Depok
- Hadir untuk Shift A & B
- Nomor akses: 1 (first submission)

### Unregistered User (Failed)
```
999,Unknown User,,,2026-06-09,16:00:00,Unregistered,-,biometrik,/photos/unknown_001.jpg
```
- User tidak dikenali ❌
- Job & Domain kosong (tidak bisa input)
- Status: Unregistered
- Foto tetap tersimpan untuk review admin

## Best Practices

1. **Backup Regular**
   - Download CSV backup setiap hari
   - Gunakan version control untuk config

2. **Permission Management**
   - Share sheet hanya ke authorized users
   - Use email groups untuk access control

3. **Data Cleaning**
   - Remove duplicate entries
   - Archive old data ke separate sheet
   - Maintain data integrity

4. **Monitoring**
   - Check "Unregistered" entries setiap hari
   - Verify foto untuk entries yang suspicious
   - Monitor network connectivity untuk sync

## Troubleshooting

### Data tidak terkirim ke Google Sheets
- ✅ Verify Web App URL correct di config.yaml
- ✅ Check Google Apps Script deployment active
- ✅ Verify network connectivity
- ✅ Check logs: `logs/absensi_pending.csv` untuk pending entries

### Duplikat entries
- Cek `logs/attendance_history.csv` untuk verification
- Remove manual dari Google Sheets

### Missing fields
- Pastikan Apps Script code lengkap
- Verify sheet columns sesuai template

## Next Steps

Setelah setup template:
1. Lanjut ke [SPREADSHEET_STRUCTURE.md](../docs/SPREADSHEET_STRUCTURE.md) untuk detail sheet
2. Lanjut ke [APPS_SCRIPT_SETUP.md](../docs/APPS_SCRIPT_SETUP.md) untuk deployment
3. Lanjut ke [ATTENDANCE_FLOW.md](../docs/ATTENDANCE_FLOW.md) untuk alur lengkap
