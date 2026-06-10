# Attendance Module - Biometric Lab System

## Overview

Modul Attendance bertanggung jawab untuk mengelola proses absensi dan integrasi Google Sheets pada sistem Biometric Lab berbasis Raspberry Pi.

Attendance module digunakan untuk:

* Menyimpan data absensi
* Mengirim data ke Google Sheets
* Menyimpan fallback data ke CSV saat offline
* Mengelola retry upload otomatis
* Menghitung histori akses pengguna

Google Apps Script bertugas sebagai backend yang menerima data dari Raspberry Pi dan melakukan proses tambahan seperti:

* Generate timestamp
* Generate status
* Generate access count
* Generate mutu shift
* Generate total shift

---

# Folder Structure

```text
model/attendance/
├── README.md
├── AppsScript/
│   └── code.gs
├── spreadsheet-template/
│   ├── Attendance_Template.csv
│   └── Template_Instructions.md
└── docs/
    ├── SPREADSHEET_STRUCTURE.md
    ├── APPS_SCRIPT_SETUP.md
    └── ATTENDANCE_FLOW.md
```

---

# Quick Start

## 1. Setup Google Sheets

Buat spreadsheet baru.

Nama sheet:

```text
Attendance
```

Struktur:

| A       | B  | C    | D      | E       | F      | G       | H      | I       | J      | K       | L      | M       | N        | O      | P     | Q           |
| ------- | -- | ---- | ------ | ------- | ------ | ------- | ------ | ------- | ------ | ------- | ------ | ------- | -------- | ------ | ----- | ----------- |
| Tanggal | ID | Nama | S1 Ket | S1 Mutu | S2 Ket | S2 Mutu | S3 Ket | S3 Mutu | S4 Ket | S4 Mutu | S5 Ket | S5 Mutu | Domisili | Status | Akses | Total Shift |

---

## 2. Deploy Google Apps Script

```text
Extensions
      ↓
Apps Script
      ↓
Paste code.gs
      ↓
Deploy
      ↓
Web App
      ↓
Copy URL
```

---

## 3. Configure Raspberry Pi

```yaml
google_sheets:
  web_app_url: "https://script.google.com/macros/s/xxxxxxxxxxxxxxxxxxxx/exec"

  retry_interval: 300
  max_retries: 3
```

---

## 4. Test Connection

```bash
curl -X POST \
"https://script.google.com/macros/s/xxxxxxxxxxxxxxxxxxxx/exec" \
-H "Content-Type: application/json" \
-d '{
"id":"5",
"name":"Fariz",
"domisili":"Lab Depok",
"shift_A":"2",
"shift_B":"3",
"shift_C":"5",
"shift_D":"6",
"shift_E":"4"
}'
```

Response:

```json
{
  "status":"success",
  "total_shift":14
}
```

---

# Key Components

## 1. absensi_utils.py

Bertanggung jawab untuk:

* Build attendance payload
* Upload ke Google Sheets
* Menyimpan pending upload
* Retry upload otomatis

Fungsi utama:

```python
upload_to_spreadsheet()
_build_payload()
_save_to_pending_csv()
_retry_pending_uploads()
```

---

## 2. Google Apps Script

Bertanggung jawab untuk:

* Menerima HTTP POST
* Memvalidasi data
* Menghitung mutu shift
* Menghitung total shift
* Menghitung jumlah akses
* Menentukan status
* Menyimpan ke Google Sheets

Fungsi utama:

```javascript
doPost(e)
```

---

## 3. Google Sheets

Menyimpan:

* Timestamp
* User ID
* Nama
* Shift
* Mutu
* Domisili
* Status
* Akses
* Total Shift

---

# Spreadsheet Structure

| Col | Field        |
| --- | ------------ |
| A   | Tanggal      |
| B   | ID           |
| C   | Nama         |
| D   | Shift 1 Ket  |
| E   | Shift 1 Mutu |
| F   | Shift 2 Ket  |
| G   | Shift 2 Mutu |
| H   | Shift 3 Ket  |
| I   | Shift 3 Mutu |
| J   | Shift 4 Ket  |
| K   | Shift 4 Mutu |
| L   | Shift 5 Ket  |
| M   | Shift 5 Mutu |
| N   | Domisili     |
| O   | Status       |
| P   | Akses        |
| Q   | Total Shift  |

---

# Data Flow

```text
Touch Sensor
      ↓
Fingerprint Verification
      ↓
Face Recognition
      ↓
Attendance Form
      ↓
Build Payload
      ↓
Google Apps Script
      ↓
Google Sheets
```

---

# Payload Structure

Raspberry Pi mengirim:

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

Field berikut tidak dikirim:

```text
Tanggal
Status
Akses
Mutu
Total Shift
```

karena dibuat oleh Apps Script.

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

# Registered User Example

Payload:

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

Stored Data:

```text
2026-05-30 13:26:11 | 5 | Fariz | 2 | 1.5 | 3 | 2.5 | 5 | 3 | 6 | 5 | 4 | 2 | Lab Depok | Registered | 1 | 14
```

---

# Unregistered User Example

Payload:

```json
{}
```

Stored Data:

```text
2026-05-30 13:27:20 | | | | | | | | | | | | | - | Unregistered | 1 | 0
```

---

# CSV Fallback

Jika upload gagal:

```text
Google Sheets Offline
      ↓
Save CSV
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

```text
Upload Failed
      ↓
Save Pending CSV
      ↓
Retry
      ↓
Upload Success
```

Konfigurasi:

```yaml
retry_interval: 300
max_retries: 3
```

---

# Integration Example

```python
record = {
    "id": user_id,
    "name": user_name,
    "domisili": domisili,
    "shift_A": shift_a,
    "shift_B": shift_b,
    "shift_C": shift_c,
    "shift_D": shift_d,
    "shift_E": shift_e
}

success = self.absensi.upload_to_spreadsheet(record)
```

---

# Monitoring

## Pending Upload

```bash
cat logs/absensi_pending.csv
```

## Attendance History

```bash
cat logs/attendance_history.csv
```

## Event Logs

```bash
tail -f logs/events.log
```

---

# Troubleshooting

## Data Tidak Masuk Google Sheets

Periksa:

```text
Apps Script Deployment
Internet Connection
Spreadsheet Permission
Web App URL
```

---

## Status Salah

Periksa payload:

```json
{
  "id":"5",
  "name":"Fariz"
}
```

harus memiliki ID dan Nama.

---

## Total Shift Salah

Periksa:

```text
Shift Mapping
Apps Script
Spreadsheet Header
```

---

# Documentation

* SPREADSHEET_STRUCTURE.md
* APPS_SCRIPT_SETUP.md
* ATTENDANCE_FLOW.md
* Template_Instructions.md

---

# Version Information

Module Version : 2.0

Compatible With:

```text
Biometric Desktop
Google Apps Script
Google Sheets Attendance System
```

---

# Architecture Summary

```text
Fingerprint
      +
Face Recognition
      ↓
Attendance Form
      ↓
Raspberry Pi
      ↓
Google Apps Script
      ↓
Google Sheets

Stored:
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
