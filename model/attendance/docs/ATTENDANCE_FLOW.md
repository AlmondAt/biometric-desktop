# COMPLETE ATTENDANCE FLOW DOCUMENTATION

## System Overview

```text
User
  ↓
Touch Sensor
  ↓
Fingerprint Verification
  ↓
Face Recognition
  ↓
Attendance Form
  ↓
Google Apps Script
  ↓
Google Sheets
```

---

# PHASE 1 - System Initialization

```text
System Start
    │
    ├─ Load config.yaml
    ├─ Load SQLite Database
    ├─ Load Face Embeddings
    ├─ Initialize Arduino
    ├─ Initialize Fingerprint Sensor
    ├─ Initialize Camera
    ├─ Initialize LCD
    │
    └─ IDLE STATE
```

LCD:

```text
Robotika Lab
Ready
```

System menunggu touch sensor.

---

# PHASE 2 - Touch Sensor

```text
IDLE
 │
 └─ Touch Sensor Triggered
      │
      └─ Activate Attendance System
```

LCD:

```text
Silakan Tempel
Sidik Jari
```

---

# PHASE 3 - Fingerprint Verification

```text
Fingerprint Scan
       │
       ├─ Match Found
       │      │
       │      └─ Get User ID
       │
       └─ No Match
              │
              └─ UNREGISTERED FLOW
```

Jika fingerprint cocok:

```text
User ID ditemukan
Nama ditemukan
```

lanjut ke Face Recognition.

---

# PHASE 4 - Face Recognition

```text
Face Recognition
        │
        ├─ Match
        │      │
        │      └─ Attendance Form
        │
        └─ No Match
               │
               └─ UNREGISTERED FLOW
```

Proses:

```text
Camera Capture
      ↓
MTCNN Face Detection
      ↓
FaceNet Embedding
      ↓
Cosine Similarity
      ↓
Verification
```

Threshold:

```text
0.8
```

atau sesuai konfigurasi sistem.

---

# PHASE 5 - Attendance Form

Jika fingerprint dan wajah berhasil diverifikasi.

User masuk ke form absensi.

---

## Step 1 - Domisili

Contoh:

```text
Lab Depok
Lab Kalimalang
Lab Karawaci
```

Pilihan disimpan ke:

```text
domisili
```

---

## Step 2 - Shift Input

User mengisi:

```text
Shift 1
Shift 2
Shift 3
Shift 4
Shift 5
```

Contoh:

```text
Shift 1 : 2
Shift 2 : 3
Shift 3 : 5
Shift 4 : 6
Shift 5 : 4
```

Disimpan menjadi:

```json
{
  "shift_A":"2",
  "shift_B":"3",
  "shift_C":"5",
  "shift_D":"6",
  "shift_E":"4"
}
```

---

## Step 3 - Confirmation

Tampilkan ringkasan:

```text
Nama : Fariz
Domisili : Lab Depok

S1 : 2
S2 : 3
S3 : 5
S4 : 6
S5 : 4

Confirm ?
```

Jika:

```text
YES
```

lanjut upload.

Jika:

```text
NO
```

kembali ke form.

---

# PHASE 6 - Build Payload

Raspberry Pi hanya mengirim:

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

Tidak perlu mengirim:

```text
Tanggal
Waktu
Status
Akses
Total Shift
```

karena dihitung oleh Apps Script.

---

# PHASE 7 - Upload to Google Sheets

```text
Attendance Form
      ↓
POST Request
      ↓
Google Apps Script
      ↓
Google Sheets
```

Request:

```http
POST
Content-Type: application/json
```

Body:

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

# PHASE 8 - Apps Script Processing

Apps Script akan:

```text
1. Generate Timestamp
2. Generate Status
3. Generate Access Count
4. Convert Shift → Mutu
5. Calculate Total Shift
6. Save to Spreadsheet
```

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

Apps Script menghitung jumlah absensi berdasarkan ID.

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

# Unregistered Flow

Jika:

```text
Fingerprint Gagal
atau
Face Recognition Gagal
```

Maka:

```text
Capture Photo
      ↓
Save Unknown Face
      ↓
Upload Minimal Data
```

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

Apps Script otomatis menghasilkan:

```text
Status = Unregistered
Akses = 1
Total Shift = 0
```

Spreadsheet:

```text
Tanggal      : Auto
ID           :
Nama         :
Shift        :
Domisili     : -
Status       : Unregistered
Akses        : 1
Total Shift  : 0
```

---

# Network Failure Handling

Jika Google Sheets gagal:

```text
Upload Failed
      ↓
Save Local CSV
      ↓
logs/absensi_pending.csv
```

Kemudian:

```text
Retry Upload
```

saat koneksi kembali normal.

---

# Success Flow

```text
Touch Sensor
      ↓
Fingerprint
      ↓
Face Recognition
      ↓
Attendance Form
      ↓
Upload
      ↓
Google Apps Script
      ↓
Google Sheets
      ↓
Success
      ↓
Idle State
```

---

# Final Data Flow

```text
Fingerprint
      +
Face Recognition
      ↓
Attendance Form
      ↓
Raspberry Pi
      ↓
Apps Script
      ↓
Google Sheets

Google Sheets:
- Tanggal
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
