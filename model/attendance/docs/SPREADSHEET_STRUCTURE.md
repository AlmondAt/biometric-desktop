# Google Sheets Structure & Data Mapping

## Overview
Dokumen ini menjelaskan struktur Google Sheets yang digunakan untuk menyimpan attendance records dari Raspberry Pi.

---

## Sheet: Attendance (Main)

### Purpose
Menyimpan semua attendance/absensi records yang disubmit dari Raspberry Pi.

### Columns

| # | Kolom | Format | Source | Notes |
|---|-------|--------|--------|-------|
| A | ID | Integer | Raspberry Pi (Database) | User ID dari fingerprint/face database |
| B | Nama | Text | Raspberry Pi (Database) | Nama user dari database |
| C | Job | Text | Raspberry Pi (User Input) | Pilihan job dari menu (PS Muro, Dasar Menengah, Lanjut) |
| D | Domain | Text | Raspberry Pi (User Input) | Lokasi lab (Lab Depok, Lab Kalimalang, Lab Karawaci) |
| E | Domisili | Text | Raspberry Pi (User Input) | Domisili/asal pengguna |
| F | Shift_A | Number (0/1) | Raspberry Pi (User Input) | 1 = hadir, 0 = tidak |
| G | Shift_B | Number (0/1) | Raspberry Pi (User Input) | 1 = hadir, 0 = tidak |
| H | Shift_C | Number (0/1) | Raspberry Pi (User Input) | 1 = hadir, 0 = tidak |
| I | Shift_D | Number (0/1) | Raspberry Pi (User Input) | 1 = hadir, 0 = tidak |
| J | Shift_E | Number (0/1) | Raspberry Pi (User Input) | 1 = hadir, 0 = tidak |
| K | Tanggal | Date | Raspberry Pi (System) | Format: YYYY-MM-DD |
| L | Waktu | Time | Raspberry Pi (System) | Format: HH:MM:SS |
| M | Status | Text | Raspberry Pi (System) | "Registered" atau "Unregistered" |
| N | Akses | Integer | Raspberry Pi (System) | Sequential number per user |
| O | Metode | Text | Raspberry Pi (System) | "biometrik" (future: "manual") |
| P | Foto | Text | Raspberry Pi (System) | File path ke foto yang diambil |

### Example Data

```
ID | Nama | Job | Domain | Domisili | Shift_A | Shift_B | Shift_C | Shift_D | Shift_E | Tanggal | Waktu | Status | Akses | Metode | Foto
101 | John Doe | PS Muro | Lab Depok | Jakarta | 1 | 1 | 0 | 0 | 0 | 2026-06-09 | 14:30:15 | Registered | 1 | biometrik | /photos/101_001.jpg
102 | Jane Smith | Dasar Menengah | Lab Kalimalang | Bekasi | 1 | 0 | 1 | 0 | 0 | 2026-06-09 | 15:45:22 | Registered | 1 | biometrik | /photos/102_001.jpg
999 | Unknown User | | | | | | | | | 2026-06-09 | 16:00:00 | Unregistered | 0 | biometrik | /photos/unknown_001.jpg
```

---

## Sheet: Configuration (Optional)

### Purpose
Menyimpan konfigurasi sistem untuk referensi.

### Layout

```
A | B
──┼────────────────────────────────────
1 | Setting | Value
2 | Web App URL | https://script.google.com/macros/.../usercontent
3 | Last Sync | 2026-06-09 16:00:00
4 | Pending Records | 0
5 | Total Users | 152
6 | Today Attendance | 87
```

---

## Data Flow: Raspberry Pi → Google Sheets

### Step 1: User Authentication
```
Raspberry Pi System
├─ Touch Sensor activated
├─ Fingerprint verification
├─ Face recognition
└─ User identified
```

### Step 2: User Selects Options
```
Menu Input
├─ Job selection (user picks)
├─ Domain selection (user picks)
├─ Shift input (user picks)
└─ Confirmation
```

### Step 3: Record Building
```
absensi_utils.py
├─ Gather user data from database
├─ Combine with user inputs
├─ Build payload dictionary
└─ Format for Google Sheets
```

### Step 4: Upload to Google Sheets
```
Payload sent via HTTP POST to Google Apps Script
{
  "id": "101",
  "name": "John Doe",
  "job": "PS Muro",
  "domain": "Lab Depok",
  "domisili": "Jakarta",
  "shift_A": "1",
  "shift_B": "1",
  "shift_C": "0",
  "shift_D": "0",
  "shift_E": "0",
  "tanggal": "2026-06-09",
  "waktu": "14:30:15",
  "status": "Registered",
  "akses": "1",
  "metode": "biometrik"
}
```

### Step 5: Google Apps Script Processing
```
Google Apps Script (code.gs)
├─ Receive HTTP POST
├─ Extract payload
├─ Append to Google Sheets
├─ Return success status
└─ (Optional: Send email notification)
```

### Step 6: Success/Failure
```
Upload Success
├─ Record stored in Google Sheets
└─ Confirmation shown on Raspberry Pi LCD

Upload Failure
├─ Record saved to logs/absensi_pending.csv
├─ Retry mechanism triggered
└─ Fallback to local storage
```

---

## CSV Fallback Mechanism

### When CSV is Used
- Google Sheets server unreachable
- Network timeout
- Apps Script error (4xx, 5xx)

### File: `logs/absensi_pending.csv`

Struktur:
```
timestamp,name,id,job,domain,domisili,shift_A,shift_B,shift_C,shift_D,shift_E,status,akses,metode,foto
2026-06-09 14:30:15,John Doe,101,PS Muro,Lab Depok,Jakarta,1,1,0,0,0,Registered,1,biometrik,/photos/101_001.jpg
```

### Retry Logic
1. Simpan ke CSV jika upload gagal
2. System mencoba retry setiap 5 menit (configurable)
3. Max 3 retry attempts
4. Jika semua gagal, manual upload later

---

## Data Fields Reference

### Auto-Generated Fields

#### ID
- Source: Database fingerprint/face
- Type: Integer
- Example: 101, 102, 999 (unknown)
- Mapped dari: `users.id`

#### Nama (Name)
- Source: Database user profile
- Type: Text
- Example: "John Doe", "Unknown User"
- Mapped dari: `users.name`

#### Tanggal (Date)
- Source: System timestamp
- Format: YYYY-MM-DD
- Example: "2026-06-09"
- Set by: `datetime.now().strftime('%Y-%m-%d')`

#### Waktu (Time)
- Source: System timestamp
- Format: HH:MM:SS
- Example: "14:30:15"
- Set by: `datetime.now().strftime('%H:%M:%S')`

#### Status
- Source: Biometric verification result
- Type: Text
- Values:
  - "Registered" = user found in database
  - "Unregistered" = user not recognized
- Set by: `absensi_utils._compute_status()`

#### Akses (Access/Sequence)
- Source: CSV history + counter
- Type: Integer
- Represents: nth submission for this user
- Computed by: `_get_next_akses_count(user_id)`

#### Metode (Method)
- Source: System
- Type: Text
- Current: Always "biometrik"
- Future: Could be "manual" for admin override

#### Foto (Photo)
- Source: File path
- Type: Text
- Example: "/photos/101_001.jpg"
- Location: Relative path from Raspberry Pi logs

### User-Selected Fields

#### Job
- User picks from menu
- Values: "PS Muro", "Dasar Menengah", "Lanjut"
- From config: `job_codes` in `config.yaml`

#### Domain
- User picks from menu
- Values: "Lab Depok", "Lab Kalimalang", "Lab Karawaci"
- From config: `domain_codes` in `config.yaml`

#### Domisili
- User input text
- Free text, no predefined values
- Example: "Jakarta", "Bekasi", "Tangerang"

#### Shift_A through Shift_E
- User selects which shifts they worked
- Type: Boolean (0 or 1)
- 1 = present, 0 = absent
- Can select multiple shifts

---

## Data Validation

### Required Fields (Must not be empty)
- ID (except for unregistered)
- Nama (except for unregistered)
- Tanggal
- Waktu
- Status

### Optional Fields (Can be empty for unregistered)
- Job
- Domain
- Domisili
- Shift_A-E

### Field Formats

| Field | Format | Validation |
|-------|--------|-----------|
| ID | Integer | > 0 or = 999 (unknown) |
| Nama | Text | Non-empty |
| Tanggal | YYYY-MM-DD | Valid date |
| Waktu | HH:MM:SS | Valid time |
| Status | Enum | "Registered" or "Unregistered" |
| Shift_* | 0 or 1 | No other values |

---

## Integration with Apps Script

### Incoming Data
Google Apps Script receives JSON:
```javascript
{
  id: "101",
  name: "John Doe",
  job: "PS Muro",
  domain: "Lab Depok",
  // ... all other fields
}
```

### Processing
```javascript
function doPost(e) {
  var payload = JSON.parse(e.postData.contents);
  var sheet = SpreadsheetApp.getActive().getSheetByName("Attendance");
  
  // Append as new row
  sheet.appendRow([
    payload.id,
    payload.name,
    payload.job,
    // ... etc
  ]);
  
  return ContentService.createTextOutput("OK");
}
```

### Response
```
HTTP 200 OK
```

---

## Troubleshooting Data Issues

### Missing Columns
**Problem:** Some columns appear empty or missing

**Solution:**
1. Verify Apps Script code is sending all fields
2. Check config.yaml for correct field names
3. Manually add column headers to sheet

### Wrong Data Types
**Problem:** Numbers showing as text, dates as strings

**Solution:**
1. Format columns in Google Sheets (Format → Number)
2. Verify Python code is sending correct types
3. Check CSV for quote escaping issues

### Duplicate Entries
**Problem:** Same record appears twice

**Possible Causes:**
- Retry logic triggered twice
- Manual re-upload

**Solution:**
1. Check timestamp to identify duplicates
2. Delete manually or via Apps Script
3. Verify network stability

### Unregistered Bulk Upload
**Problem:** Many "Unregistered" entries

**Solution:**
1. Check if fingerprint database is corrupted
2. Verify face recognition model accuracy
3. Review face_embeddings.pkl integrity

---

## Reporting & Analytics

### Suggested Queries

#### Daily Attendance
```javascript
=COUNTIF(Attendance!M:M, "Registered")
```

#### By Job
```javascript
=COUNTIF(Attendance!C:C, "PS Muro")
```

#### By Shift
```javascript
=SUM(Attendance!F:F)  // Count Shift A attendees
```

#### Unregistered Count
```javascript
=COUNTIF(Attendance!M:M, "Unregistered")
```

---

## Next Steps

1. Review [APPS_SCRIPT_SETUP.md](./APPS_SCRIPT_SETUP.md) untuk deployment
2. Review [ATTENDANCE_FLOW.md](./ATTENDANCE_FLOW.md) untuk alur lengkap
3. Lihat [Template Instructions](../spreadsheet-template/Template_Instructions.md)
