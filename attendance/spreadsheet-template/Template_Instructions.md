# Attendance Spreadsheet Template Instructions

## Overview

Template ini digunakan oleh sistem Biometric Desktop untuk menyimpan data absensi ke Google Sheets melalui Google Apps Script.

Google Apps Script akan secara otomatis:

* Membuat timestamp absensi
* Menghitung mutu shift
* Menghitung total shift
* Menghitung jumlah akses
* Menentukan status Registered / Unregistered

Raspberry Pi hanya mengirim data identitas, domisili, dan kode shift.

---

# Spreadsheet Layout

## Row 1

```text
Tanggal | ID | Nama | Shift 1 | | Shift 2 | | Shift 3 | | Shift 4 | | Shift 5 | | Domisili | Status | Akses | Total Shift
```

## Row 2

```text
         |    |      | Ket | Mutu | Ket | Mutu | Ket | Mutu | Ket | Mutu | Ket | Mutu
```

## Row 3+

Data absensi.

---

# Struktur Kolom

| No | Kolom        | Source       | Keterangan                |
| -- | ------------ | ------------ | ------------------------- |
| 1  | Tanggal      | Apps Script  | Timestamp otomatis        |
| 2  | ID           | Raspberry Pi | User ID                   |
| 3  | Nama         | Raspberry Pi | Nama pengguna             |
| 4  | Shift 1 Ket  | Raspberry Pi | Kode Shift 1              |
| 5  | Shift 1 Mutu | Apps Script  | Nilai mutu Shift 1        |
| 6  | Shift 2 Ket  | Raspberry Pi | Kode Shift 2              |
| 7  | Shift 2 Mutu | Apps Script  | Nilai mutu Shift 2        |
| 8  | Shift 3 Ket  | Raspberry Pi | Kode Shift 3              |
| 9  | Shift 3 Mutu | Apps Script  | Nilai mutu Shift 3        |
| 10 | Shift 4 Ket  | Raspberry Pi | Kode Shift 4              |
| 11 | Shift 4 Mutu | Apps Script  | Nilai mutu Shift 4        |
| 12 | Shift 5 Ket  | Raspberry Pi | Kode Shift 5              |
| 13 | Shift 5 Mutu | Apps Script  | Nilai mutu Shift 5        |
| 14 | Domisili     | Raspberry Pi | Lokasi/domisili pengguna  |
| 15 | Status       | Apps Script  | Registered / Unregistered |
| 16 | Akses        | Apps Script  | Jumlah akses user         |
| 17 | Total Shift  | Apps Script  | Total mutu seluruh shift  |

---

# Cara Menggunakan

## 1. Buat Spreadsheet Baru

```text
Google Sheets
      ↓
Create Blank Spreadsheet
      ↓
Rename Sheet:
Attendance
```

---

## 2. Setup Header

Masukkan header sesuai struktur di atas.

Data harus dimulai dari:

```text
Row 3
```

karena:

```text
Row 1 = Header Utama
Row 2 = Ket / Mutu
Row 3 = Data
```

---

## 3. Deploy Apps Script

Deploy Apps Script sebagai:

```text
Web App
```

dan copy URL hasil deployment.

---

## 4. Configure Raspberry Pi

```yaml
google_sheets:
  web_app_url: "https://script.google.com/macros/s/xxxxxxxxxxxxxxxxxxxx/exec"
```

---

# Data Yang Dikirim Raspberry Pi

Contoh payload:

```json
{
  "id":"5",
  "name":"Fariz",
  "domisili":"Lab Depok",
  "shift_A":"2",
  "shift_B":"3",
  "shift_C":"5",
  "shift_D":"6",
  "shift_E":"4"
}
```

---

# Data Yang Dibuat Apps Script

Apps Script otomatis membuat:

```text
Tanggal
Status
Akses
Mutu Shift
Total Shift
```

Raspberry Pi tidak perlu mengirim field tersebut.

---

# Shift Mapping

| Kode | Mutu |
| ---- | ---- |
| 0    | 0    |
| 1    | 1    |
| 2    | 1.5  |
| 3    | 2.5  |
| 4    | 2    |
| 5    | 3    |
| 6    | 5    |
| 7    | 6    |
| 8    | 4    |
| 9    | -    |
| A    | 3    |
| B    | 2    |
| C    | -    |

---

# Example Data

## Registered User

Input dari Raspberry Pi:

```json
{
  "id":"5",
  "name":"Fariz",
  "domisili":"Lab Depok",
  "shift_A":"2",
  "shift_B":"3",
  "shift_C":"5",
  "shift_D":"6",
  "shift_E":"4"
}
```

Data yang tersimpan:

```text
2026-05-30 13:26:11 | 5 | Fariz | 2 | 1.5 | 3 | 2.5 | 5 | 3 | 6 | 5 | 4 | 2 | Lab Depok | Registered | 1 | 14
```

---

## Unregistered User

Input:

```json
{}
```

Data yang tersimpan:

```text
2026-05-30 13:27:20 | | | | | | | | | | | | | - | Unregistered | 1 | 0
```

---

# Status Logic

Apps Script:

```javascript
(data.id && data.name)
```

Jika true:

```text
Registered
```

Jika false:

```text
Unregistered
```

---

# Access Logic

Apps Script menghitung jumlah kemunculan ID.

Contoh:

```text
ID 5 pertama
Akses = 1

ID 5 kedua
Akses = 2

ID 5 ketiga
Akses = 3
```

---

# Total Shift Logic

Contoh:

```text
Shift 1 = 2
Shift 2 = 3
Shift 3 = 5
Shift 4 = 6
Shift 5 = 4
```

Mutu:

```text
1.5
2.5
3
5
2
```

Total:

```text
14
```

---

# Recommended Formulas

## Registered Count

```excel
=COUNTIF(O:O,"Registered")
```

## Unregistered Count

```excel
=COUNTIF(O:O,"Unregistered")
```

## Total Shift Value

```excel
=SUM(Q:Q)
```

## Total Access

```excel
=SUM(P:P)
```

---

# Troubleshooting

## Data Tidak Masuk

Periksa:

```text
Apps Script Deployment
Google Sheets Permission
Internet Connection
```

---

## Status Salah

Pastikan payload mengirim:

```json
{
  "id":"5",
  "name":"Fariz"
}
```

untuk user yang valid.

---

## Total Shift Tidak Sesuai

Periksa:

```text
Shift Mapping
Apps Script Code
Spreadsheet Formula
```

---

# Documentation References

1. APPS_SCRIPT_SETUP.md
2. ATTENDANCE_FLOW.md
3. SPREADSHEET_STRUCTURE.md

Seluruh dokumen di atas harus menggunakan struktur spreadsheet yang sama agar sinkron dengan implementasi sistem.
