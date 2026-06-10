# GOOGLE SHEETS STRUCTURE & DATA MAPPING

## Overview

Dokumen ini menjelaskan struktur Google Sheets yang digunakan untuk menyimpan data absensi dari sistem biometrik berbasis Raspberry Pi dan Google Apps Script.

Google Apps Script bertugas untuk:

* Membuat timestamp otomatis
* Menghitung mutu shift
* Menghitung total shift
* Menghitung jumlah akses
* Menentukan status Registered / Unregistered
* Menyimpan data ke Google Sheets

---

# Sheet: Attendance

## Purpose

Menyimpan seluruh data absensi yang dikirim dari Raspberry Pi.

---

# Spreadsheet Structure

## Header Layout

### Row 1

```text
Tanggal | ID | Nama | Shift 1 | | Shift 2 | | Shift 3 | | Shift 4 | | Shift 5 | | Domisili | Status | Akses | Total Shift
```

### Row 2

```text
         |    |      | Ket | Mutu | Ket | Mutu | Ket | Mutu | Ket | Mutu | Ket | Mutu
```

### Row 3+

Data absensi.

---

# Columns

| Kolom | Nama         | Source       |
| ----- | ------------ | ------------ |
| A     | Tanggal      | Apps Script  |
| B     | ID           | Raspberry Pi |
| C     | Nama         | Raspberry Pi |
| D     | Shift 1 Ket  | Raspberry Pi |
| E     | Shift 1 Mutu | Apps Script  |
| F     | Shift 2 Ket  | Raspberry Pi |
| G     | Shift 2 Mutu | Apps Script  |
| H     | Shift 3 Ket  | Raspberry Pi |
| I     | Shift 3 Mutu | Apps Script  |
| J     | Shift 4 Ket  | Raspberry Pi |
| K     | Shift 4 Mutu | Apps Script  |
| L     | Shift 5 Ket  | Raspberry Pi |
| M     | Shift 5 Mutu | Apps Script  |
| N     | Domisili     | Raspberry Pi |
| O     | Status       | Apps Script  |
| P     | Akses        | Apps Script  |
| Q     | Total Shift  | Apps Script  |

---

# Example Data

| Tanggal             | ID | Nama   | S1 | M1  | S2 | M2  | S3 | M3 | S4 | M4 | S5 | M5 | Domisili  | Status       | Akses | Total |
| ------------------- | -- | ------ | -- | --- | -- | --- | -- | -- | -- | -- | -- | -- | --------- | ------------ | ----- | ----- |
| 2026-05-30 13:26:11 | 5  | Fariz  | 2  | 1.5 | 3  | 2.5 | 5  | 3  | 6  | 5  | 4  | 2  | Lab Depok | Registered   | 1     | 14    |
| 2026-05-30 14:06:47 | 16 | Mahmud | 2  | 1.5 | 4  | 2   | 5  | 3  | 6  | 5  | 8  | 4  | Lab Depok | Registered   | 1     | 15.5  |
| 2026-05-30 14:20:00 |    |        |    |     |    |     |    |    |    |    |    |    | -         | Unregistered | 1     | 0     |

---

# Data Flow

## Step 1 - Authentication

```text
Touch Sensor
      ↓
Fingerprint Verification
      ↓
Face Recognition
```

Jika berhasil:

```text
Registered User
```

Jika gagal:

```text
Unregistered User
```

---

## Step 2 - Attendance Form

User mengisi:

```text
Domisili
Shift 1
Shift 2
Shift 3
Shift 4
Shift 5
```

Contoh:

```text
Domisili : Lab Depok

Shift 1 : 2
Shift 2 : 3
Shift 3 : 5
Shift 4 : 6
Shift 5 : 4
```

---

## Step 3 - Payload Creation

Raspberry Pi membuat payload.

Contoh:

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

## Step 4 - Upload

```text
Raspberry Pi
      ↓
HTTP POST
      ↓
Google Apps Script
      ↓
Google Sheets
```

---

# Shift Mapping

Apps Script melakukan konversi kode shift menjadi mutu.

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

# Status Calculation

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

# Access Calculation

Apps Script menghitung jumlah kemunculan ID pada spreadsheet.

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

# Total Shift Calculation

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

# Unregistered Flow

Jika fingerprint atau wajah gagal diverifikasi:

Payload:

```json
{}
```

atau

```json
{
  "id":"",
  "name":""
}
```

Apps Script menghasilkan:

```text
Status = Unregistered
Akses = 1
Total Shift = 0
Domisili = -
```

---

# CSV Fallback

Jika upload gagal:

```text
Google Sheets Unreachable
      ↓
Save Local CSV
      ↓
logs/absensi_pending.csv
```

---

# CSV Structure

```csv
timestamp,id,name,domisili,shift_A,shift_B,shift_C,shift_D,shift_E
2026-06-10 14:30:00,5,Fariz,Lab Depok,2,3,5,6,4
```

---

# Retry Logic

1. Upload gagal
2. Simpan ke absensi_pending.csv
3. Retry otomatis
4. Maksimal 3 percobaan
5. Jika masih gagal tetap tersimpan lokal

---

# Reporting Formula

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

# Final Architecture

```text
Touch Sensor
      ↓
Fingerprint
      ↓
Face Recognition
      ↓
Attendance Form
      ↓
Raspberry Pi
      ↓
Apps Script
      ↓
Google Sheets

Stored Data:
- Timestamp
- ID
- Nama
- Shift 1 Ket
- Shift 1 Mutu
- Shift 2 Ket
- Shift 2 Mutu
- Shift 3 Ket
- Shift 3 Mutu
- Shift 4 Ket
- Shift 4 Mutu
- Shift 5 Ket
- Shift 5 Mutu
- Domisili
- Status
- Akses
- Total Shift
```
