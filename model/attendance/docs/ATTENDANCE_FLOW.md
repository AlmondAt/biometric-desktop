# Complete Attendance Flow Documentation

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    BIOMETRIC LAB ATTENDANCE SYSTEM               │
│                  (Raspberry Pi 5 + Arduino Nano)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  1. HARDWARE LAYER                                      │   │
│  │  ├─ Touch Sensor (LCD activation)                       │   │
│  │  ├─ Fingerprint Sensor (AS608/R307)                     │   │
│  │  ├─ Camera Module (Face capture)                        │   │
│  │  ├─ Arduino Nano (Serial comm)                          │   │
│  │  └─ LCD 16x2 (Status display)                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│           ↓                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  2. CONTROL LAYER (main_integrated.py)                 │   │
│  │  ├─ State Machine                                       │   │
│  │  ├─ Biometric Authentication                            │   │
│  │  ├─ Menu Navigation                                     │   │
│  │  └─ Error Handling                                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│           ↓                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  3. ATTENDANCE LAYER (absensi_utils.py)                │   │
│  │  ├─ Data Collection                                     │   │
│  │  ├─ Google Sheets Upload                                │   │
│  │  └─ CSV Fallback                                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│           ↓                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  4. PERSISTENCE LAYER                                  │   │
│  │  ├─ Google Sheets (primary)                             │   │
│  │  ├─ CSV Logs (fallback)                                 │   │
│  │  └─ SQLite Database (user profiles)                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Complete Attendance Flow

### PHASE 1: System Initialization

```
[System Start]
    │
    ├─ Load config.yaml
    ├─ Initialize sensors:
    │  ├─ Fingerprint sensor (AS608)
    │  ├─ Camera module
    │  ├─ Touch sensor
    │  └─ LCD display
    ├─ Load database:
    │  ├─ SQLite: biometrics.db
    │  ├─ Embeddings: embeddings.pkl (face recognition)
    │  └─ User database
    │
    ├─ Display splash screen on LCD
    │  ┌──────────────────┐
    │  │ Robotika Lab     │
    │  │ 2026            │
    │  └──────────────────┘
    │
    └─→ IDLE STATE
         (Waiting for user touch)
```

---

### PHASE 2: User Activation (Touch Sensor)

```
[IDLE STATE]
    │
    ├─ Touch Sensor Detected
    │
    └─→ TOUCH_ACTIVATED STATE
         │
         ├─ Display options on LCD:
         │  ┌──────────────────────────┐
         │  │ 1. Attendance            │
         │  │ 2. Admin                 │
         │  │ 3. Enrollment            │
         │  │ 4. Info                  │
         │  └──────────────────────────┘
         │
         └─→ Menu selection via keypad
              (User presses: 1 for Attendance)
              
              If 1 (Attendance):
              └─→ FINGERPRINT STATE
```

---

### PHASE 3: Fingerprint Verification

```
[FINGERPRINT STATE]
    │
    ├─ Display on LCD:
    │  ┌──────────────────────────┐
    │  │ Letakkan jari di sensor  │
    │  │ (15 detik timeout)       │
    │  └──────────────────────────┘
    │
    ├─ Sensor waits for fingerprint
    │  ├─ Timeout? (15s) → CAPTURE_FACE → UNREGISTERED
    │  ├─ Detected? → Query database
    │  └─ Match found?
    │
    ├─ IF MATCH → Get user_id from database
    │  │
    │  ├─ Load user profile:
    │  │  ├─ user_id
    │  │  ├─ user_name
    │  │  └─ user_embeddings (for face verify)
    │  │
    │  └─→ FACE STATE
    │
    └─ IF NO MATCH → CAPTURE_FACE
         │
         ├─ Capture photo from camera
         ├─ Save to logs/unknown_faces/
         │
         └─→ UNREGISTERED FLOW (see below)
```

---

### PHASE 4: Face Recognition Verification

```
[FACE STATE]
    │
    ├─ Display on LCD:
    │  ┌──────────────────────────┐
    │  │ Posisikan wajah ke kamera│
    │  │ (45 detik timeout)       │
    │  └──────────────────────────┘
    │
    ├─ Capture face images:
    │  ├─ Use rpicam-jpeg (Raspberry Pi camera)
    │  ├─ Capture up to 4 frames
    │  ├─ Timeout? → UNREGISTERED FLOW
    │  └─ Frames ready? → Extract embeddings
    │
    ├─ Extract FaceNet embeddings:
    │  ├─ MTCNN: Detect face in each frame
    │  ├─ FaceNet: Extract 512-dim embedding
    │  ├─ Calculate: Average embedding across frames
    │  └─ Result: Single verification vector
    │
    ├─ Verify against stored embeddings:
    │  ├─ Load user_embeddings from embeddings.pkl
    │  ├─ Calculate cosine similarity
    │  ├─ Threshold: 0.8 (80% confidence)
    │  │
    │  ├─ IF similarity >= 0.8:
    │  │  ├─ User VERIFIED ✓
    │  │  ├─ Status: "Registered"
    │  │  └─→ ATTENDANCE_JOB STATE
    │  │
    │  └─ IF similarity < 0.8:
    │     ├─ User NOT MATCHED
    │     └─→ UNREGISTERED FLOW
    │
    └─ (Next phase depends on verification result)
```

---

### PHASE 5A: Registered User - Attendance Input

```
[ATTENDANCE_JOB STATE]
    │
    ├─ Display on LCD:
    │  ┌──────────────────────────┐
    │  │ Pilih Job:               │
    │  │ 1. PS Muro               │
    │  │ 2. Dasar Menengah        │
    │  │ 3. Lanjut                │
    │  │ [User presses keypad]    │
    │  └──────────────────────────┘
    │
    ├─ Store user input:
    │  └─ job_selection = "PS Muro"  (or similar)
    │
    └─→ ATTENDANCE_DOMAIN STATE

[ATTENDANCE_DOMAIN STATE]
    │
    ├─ Display on LCD:
    │  ┌──────────────────────────┐
    │  │ Pilih Domain/Lab:        │
    │  │ A. Lab Depok             │
    │  │ B. Lab Kalimalang        │
    │  │ C. Lab Karawaci          │
    │  │ [User presses keypad]    │
    │  └──────────────────────────┘
    │
    ├─ Store user input:
    │  └─ domain_selection = "Lab Depok"  (or similar)
    │
    └─→ ATTENDANCE_SHIFT_INPUT STATE

[ATTENDANCE_SHIFT_INPUT STATE]
    │
    ├─ Display on LCD:
    │  ┌──────────────────────────────────┐
    │  │ Input Shift (0/1):               │
    │  │ Shift A: 1                       │
    │  │ Shift B: 1                       │
    │  │ Shift C: 0                       │
    │  │ Shift D: 0                       │
    │  │ Shift E: 0                       │
    │  │ [User inputs via keypad]         │
    │  └──────────────────────────────────┘
    │
    ├─ Store shift selections:
    │  └─ shift_A=1, shift_B=1, shift_C=0, etc.
    │
    └─→ ATTENDANCE_CONFIRM STATE

[ATTENDANCE_CONFIRM STATE]
    │
    ├─ Display on LCD:
    │  ┌──────────────────────────────┐
    │  │ Konfirmasi:                  │
    │  │ Nama: John Doe               │
    │  │ Job: PS Muro                 │
    │  │ Domain: Lab Depok            │
    │  │                              │
    │  │ 1. Confirm  2. Cancel        │
    │  └──────────────────────────────┘
    │
    ├─ IF user presses "1" (Confirm):
    │  │
    │  ├─ Gather data:
    │  │  ├─ User ID (from fingerprint/face)
    │  │  ├─ User Name (from database)
    │  │  ├─ Job (user input)
    │  │  ├─ Domain (user input)
    │  │  ├─ Shifts (user input)
    │  │  ├─ Timestamp (system)
    │  │  ├─ Status: "Registered"
    │  │  ├─ Method: "biometrik"
    │  │  └─ Photo path (if available)
    │  │
    │  ├─ Build payload for Google Sheets:
    │  │  {
    │  │    "id": "101",
    │  │    "name": "John Doe",
    │  │    "job": "PS Muro",
    │  │    "domain": "Lab Depok",
    │  │    "domisili": "Jakarta",
    │  │    "shift_A": "1",
    │  │    "shift_B": "1",
    │  │    "shift_C": "0",
    │  │    "shift_D": "0",
    │  │    "shift_E": "0",
    │  │    "tanggal": "2026-06-09",
    │  │    "waktu": "14:30:15",
    │  │    "status": "Registered",
    │  │    "akses": "1",
    │  │    "metode": "biometrik"
    │  │  }
    │  │
    │  └─→ UPLOAD PHASE
    │
    └─ IF user presses "2" (Cancel):
         │
         ├─ Display: "Dibatalkan"
         └─→ IDLE STATE
```

---

### PHASE 5B: Unregistered User - Handling

```
[UNREGISTERED FLOW]
    │
    ├─ Capture face photo:
    │  ├─ Take full-resolution photo
    │  ├─ Save to: logs/unknown_faces/[timestamp].jpg
    │  └─ Store photo path in record
    │
    ├─ Display on LCD:
    │  ┌──────────────────────────────┐
    │  │ ⚠ User tidak dikenali       │
    │  │ Foto telah disimpan          │
    │  │ Admin akan review            │
    │  │                              │
    │  │ Tekan tombol untuk lanjut... │
    │  └──────────────────────────────┘
    │
    ├─ Gather minimal data:
    │  ├─ User ID: 999 (unknown)
    │  ├─ User Name: "Unknown User"
    │  ├─ Job: (empty)
    │  ├─ Domain: (empty)
    │  ├─ Domisili: (empty)
    │  ├─ Shifts: All 0
    │  ├─ Timestamp (system)
    │  ├─ Status: "Unregistered"
    │  ├─ Method: "biometrik"
    │  └─ Photo path: logs/unknown_faces/[timestamp].jpg
    │
    ├─ Build payload:
    │  {
    │    "id": "999",
    │    "name": "Unknown User",
    │    "job": "",
    │    "domain": "",
    │    "domisili": "",
    │    "shift_A": "0",
    │    "shift_B": "0",
    │    "shift_C": "0",
    │    "shift_D": "0",
    │    "shift_E": "0",
    │    "tanggal": "2026-06-09",
    │    "waktu": "15:45:22",
    │    "status": "Unregistered",
    │    "akses": "-",
    │    "metode": "biometrik",
    │    "foto": "logs/unknown_faces/[timestamp].jpg"
    │  }
    │
    └─→ UPLOAD PHASE
```

---

### PHASE 6: Upload to Google Sheets

```
[UPLOAD PHASE]
    │
    ├─ absensi_utils.upload_to_spreadsheet(record)
    │
    ├─ Network check:
    │  ├─ Verify Google Sheets URL configured
    │  ├─ If not configured:
    │  │  └─ Save to CSV immediately
    │  │
    │  └─ If configured, attempt upload
    │
    ├─ HTTP POST request:
    │  POST https://script.google.com/macros/d/[ID]/usercontent
    │  Content-Type: application/json
    │  Body: {payload}
    │
    ├─ Response handling:
    │  │
    │  ├─ IF HTTP 200 OK:
    │  │  │
    │  │  ├─ Append to local history CSV:
    │  │  │  └─ logs/attendance_history.csv
    │  │  │
    │  │  ├─ Display on LCD:
    │  │  │  ┌──────────────────────────┐
    │  │  │  │ ✓ Absensi Tersimpan     │
    │  │  │  │ Data terkirim ke server │
    │  │  │  └──────────────────────────┘
    │  │  │
    │  │  └─→ SUCCESS
    │  │
    │  └─ IF HTTP ERROR (4xx, 5xx, timeout):
    │     │
    │     ├─ Append to local history CSV
    │     │
    │     ├─ Save to pending CSV:
    │     │  └─ logs/absensi_pending.csv
    │     │
    │     ├─ Display on LCD:
    │     │  ┌──────────────────────────┐
    │     │  │ ⚠ Koneksi gagal         │
    │     │  │ Data disimpan di lokal  │
    │     │  └──────────────────────────┘
    │     │
    │     ├─ Implement retry logic:
    │     │  ├─ Wait retry_interval (300s default)
    │     │  ├─ Retry upload (max_retries: 3)
    │     │  ├─ If all retries fail → keep in pending
    │     │  └─ Next sync attempt: next user attendance
    │     │
    │     └─→ PARTIAL SUCCESS (saved locally, will retry)
    │
    └─→ COMPLETION PHASE
```

---

### PHASE 7: System Completion

```
[COMPLETION PHASE]
    │
    ├─ Display confirmation:
    │  ┌──────────────────────────┐
    │  │ ✓ Terima kasih!          │
    │  │ Silakan ambil kartu...   │
    │  │                          │
    │  │ (Splash: 5 detik)        │
    │  └──────────────────────────┘
    │
    ├─ Wait for user to leave
    │  └─ Optional: Door unlock signal
    │     (If mag lock + relay configured)
    │
    ├─ Reset state:
    │  ├─ Clear user data from memory
    │  ├─ Release sensors
    │  └─ Prepare for next user
    │
    └─→ IDLE STATE
         (Back to waiting for touch)
```

---

## Monitoring & Error Handling

### Timeout Scenarios

```
[TIMEOUT: Fingerprint (15s)]
└─→ User didn't place finger or sensor malfunction
    ├─ Display: "Sensor timeout, silahkan coba wajah"
    └─→ Go to FACE STATE

[TIMEOUT: Face Capture (45s)]
└─→ Camera module issue or user not facing camera
    ├─ Display: "Kamera timeout"
    └─→ Go to UNREGISTERED FLOW

[TIMEOUT: Menu Input (20s per field)]
└─→ User didn't input selection
    ├─ Display: "Input timeout, coba lagi"
    └─→ Go to previous menu state
```

### Network Failure Scenarios

```
[Network Down]
    ├─ User attendance recorded: YES
    ├─ Google Sheets update: FAILED
    ├─ CSV fallback: YES (logs/absensi_pending.csv)
    │
    ├─ System will retry when:
    │  ├─ Next user attendance (background sync)
    │  ├─ Scheduled retry timer (5-10 min)
    │  └─ Manual retry (if implemented)
    │
    └─ User will see: "Data disimpan di lokal"
```

### Photo Capture & Storage

```
[Registered User Photos]
├─ Optional: Captured during face verification
├─ Format: JPG
├─ Location: logs/attendance_photos/[user_id]_[timestamp].jpg
└─ Purpose: Visual confirmation of attendance

[Unregistered User Photos]
├─ Always captured for review
├─ Format: JPG
├─ Location: logs/unknown_faces/[timestamp].jpg
├─ Purpose: Admin manual verification & enrollment
└─ Auto-cleanup: Keep last 30 days (configurable)
```

---

## Database & Storage

### SQLite Database (biometrics.db)

```
Schema:
├─ users
│  ├─ id (INTEGER, PK)
│  ├─ name (TEXT)
│  ├─ fingerprint_id (INTEGER, unique)
│  └─ access_level (INTEGER)
│
└─ fingerprints
   ├─ id (INTEGER, PK)
   ├─ user_id (FK)
   ├─ template (BLOB)
   └─ enrolled_at (DATETIME)
```

### Face Embeddings (embeddings.pkl)

```
Format: Python pickle (dict)
Structure:
{
  "101": [
    [array(512)],  # embedding 1
    [array(512)],  # embedding 2
    ...
  ],
  "102": [
    [array(512)],
    ...
  ]
}
```

### CSV Fallback (logs/)

```
├─ attendance_history.csv
│  ├─ Local record of all submissions
│  ├─ Columns: timestamp, id, name, status, akses
│  └─ Purpose: Track access numbers
│
└─ absensi_pending.csv
   ├─ Failed submissions awaiting retry
   ├─ Columns: All attendance fields
   └─ Purpose: Retry queue for offline periods
```

---

## Performance & Monitoring

### System Metrics to Track

```
Fingerprint Verification
├─ Detection rate: % of successful detections
├─ Matching accuracy: % of correct user matches
├─ Response time: Average time from touch to result
└─ Failure reasons: Sensor issues, dry finger, etc.

Face Recognition
├─ Detection rate: % of faces detected in frame
├─ Matching accuracy: % of correct user identification
├─ Response time: Average capture + processing time
└─ False positive rate: Incorrect matches

Network/Sync
├─ Upload success rate: % of successful submissions
├─ Average upload time: Upload latency to Google Sheets
├─ Retry rate: % of records requiring retry
└─ Offline periods: Total downtime per day

User Metrics
├─ Unique users per day: Count of unique attendees
├─ Unregistered attempts: Failed biometric matches
├─ Average time per attendance: User interaction time
└─ Peak hours: Times with highest usage
```

---

## Troubleshooting Flowchart

```
[System Not Responding]
├─ Check LCD display
├─ Check sensor lights (LED indicators)
├─ Restart Raspberry Pi if needed
└─ Review logs:
   ├─ logs/events.log (system events)
   ├─ logs/access.log (attendance records)
   └─ logs/absensi_pending.csv (sync queue)

[Face Recognition Issues]
├─ Check camera angle (face centered)
├─ Clean camera lens
├─ Verify lighting (avoid backlighting)
├─ Retrain face embeddings if accuracy poor
└─ Check embeddings.pkl integrity

[Fingerprint Issues]
├─ Clean fingerprint sensor
├─ Enroll user again (poor template)
├─ Check sensor cable connection
└─ Verify sensor port in config.yaml

[Network Issues]
├─ Ping google.com from Raspberry Pi
├─ Check WiFi SSID & password
├─ Verify Google Apps Script deployment
├─ Check CSV fallback in logs/
└─ Manual upload pending CSV when online
```

---

## Data Privacy & Compliance

### Data Stored
- User ID & Name (biometric identifier)
- Biometric templates (fingerprint, face)
- Attendance records (job, location, time)
- Photos (captured during verification)

### Retention Policy
```
Keep: 90 days
Archive: > 90 days → backup to Drive
Delete: > 1 year → permanent delete
```

### Access Control
```
Admin: Full access to system & data
Users: Can view own attendance records
Guests: No access
```

---

## Next Steps

1. Review [SPREADSHEET_STRUCTURE.md](./SPREADSHEET_STRUCTURE.md) for data details
2. Review [APPS_SCRIPT_SETUP.md](./APPS_SCRIPT_SETUP.md) for Google Sheets setup
3. Follow the complete system setup guide
4. Test each phase before going live
5. Monitor system performance during first week

---

**Last Updated:** June 2026  
**System Version:** Biometric Desktop v1.0
