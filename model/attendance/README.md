# Attendance Module - Biometric Lab System

## Overview

Modul attendance bertanggung jawab untuk mengelola integrasi Google Sheets dan menyimpan attendance records dari Raspberry Pi.

---

## Folder Structure

```
model/attendance/
├── README.md                          # This file
├── AppsScript/                        # Google Apps Script code
│   └── code.gs                        # (if exists from deployment)
├── spreadsheet-template/              # Google Sheets template
│   ├── Attendance_Template.csv        # Sample data structure
│   └── Template_Instructions.md       # How to use template
└── docs/                              # Documentation
    ├── SPREADSHEET_STRUCTURE.md       # Sheet layout & data mapping
    ├── APPS_SCRIPT_SETUP.md           # Google Apps Script deployment guide
    └── ATTENDANCE_FLOW.md             # Complete system flow diagram
```

---

## Quick Start

### 1. Setup Google Sheets
```bash
1. Create Google Sheet: https://sheets.google.com
2. Create sheet named "Attendance"
3. Add header row with columns (A-P):
   ID, Nama, Job, Domain, Domisili, Shift_A, Shift_B, Shift_C, Shift_D, Shift_E, 
   Tanggal, Waktu, Status, Akses, Metode, Foto
```

### 2. Deploy Google Apps Script
```bash
1. In Google Sheet, click: Tools → Script editor
2. Copy code from docs/APPS_SCRIPT_SETUP.md
3. Click Deploy → New Deployment
4. Select: Web app
5. Click Deploy
6. Copy the Web App URL
```

### 3. Configure Raspberry Pi
```yaml
# config.yaml
google_sheets:
  web_app_url: "https://script.google.com/macros/d/[ID]/usercontent"
  retry_interval: 300      # 5 minutes
  max_retries: 3
```

### 4. Test System
```bash
# Verify connection
curl -X POST https://script.google.com/macros/d/[ID]/usercontent \
  -H "Content-Type: application/json" \
  -d '{"id":"101","name":"Test","tanggal":"2026-06-09","waktu":"14:30:00","status":"Registered"}'

# Response: OK
```

---

## Key Components

### 1. **absensi_utils.py** (in raspy-main-integrated/)

Responsible for:
- Building attendance payloads
- Uploading to Google Sheets
- Handling CSV fallback
- Retry mechanism

Key Classes:
- `AbsensiManager` - Main attendance handler
  - `upload_to_spreadsheet()` - Send data to Google Sheets
  - `_build_payload()` - Format data for upload
  - `_save_to_pending_csv()` - Save failed uploads

### 2. **Google Apps Script** (code.gs)

Responsible for:
- Receiving HTTP POST from Raspberry Pi
- Validating payload
- Appending to Google Sheet
- Returning success/failure status

Key Function:
- `doPost(e)` - Receives & processes attendance data

### 3. **Google Sheets**

Stores:
- Attendance records (primary)
- Configuration (optional)
- Usage statistics & reports (optional)

Columns:
- ID, Nama, Job, Domain, Domisili
- Shift_A through Shift_E
- Tanggal, Waktu, Status, Akses, Metode, Foto

---

## Data Flow

```
Raspberry Pi System
    ↓
Biometric Verification (fingerprint + face)
    ↓
User Selects: Job, Domain, Shift
    ↓
absensi_utils.upload_to_spreadsheet()
    ├─ Build JSON payload
    ├─ POST to Google Apps Script
    │
    ├─ Success (HTTP 200)
    │   └─ Data stored in Google Sheets
    │
    └─ Failure (timeout/error)
        └─ Save to CSV (logs/absensi_pending.csv)
            └─ Retry on next user or scheduled timer
```

---

## File Descriptions

### Spreadsheet Template Files

#### `Attendance_Template.csv`
Sample CSV with example data showing correct column structure:
```
101,John Doe,PS Muro,Lab Depok,Jakarta,1,1,0,0,0,2026-06-09,14:30:15,Registered,1,biometrik,...
```

**Use:** Import into Google Sheets to validate structure

#### `Template_Instructions.md`
Step-by-step instructions for:
- Importing template into Google Sheets
- Setting up formulas
- Configuring Raspberry Pi
- Field descriptions
- Troubleshooting

### Documentation Files

#### `SPREADSHEET_STRUCTURE.md`
Detailed documentation of:
- Sheet names & purposes
- Column definitions & data types
- Data examples
- Mapping from Raspberry Pi
- CSV fallback mechanism
- Data validation rules

**Read this for:** Understanding the data structure

#### `APPS_SCRIPT_SETUP.md`
Complete guide for:
- Creating Google Sheet
- Writing Apps Script code
- Deploying as Web App
- Getting Web App URL
- Configuring Raspberry Pi
- Testing the system
- Error handling
- Advanced features

**Read this for:** Setting up Google Sheets integration

#### `ATTENDANCE_FLOW.md`
Complete system flow documentation:
- System architecture diagram
- Phase-by-phase flow with diagrams
- State machine visualization
- Error scenarios
- Network failure handling
- Photo capture & storage
- Database structure
- Monitoring & metrics
- Troubleshooting flowchart

**Read this for:** Understanding the complete system flow

---

## Integration with Raspberry Pi

The attendance module is called by `raspy-main-integrated/main_integrated.py`:

```python
from modules.absensi_utils import AbsensiManager

# Initialize
self.absensi = AbsensiManager(self.config, self.logger)

# During attendance confirmation
record = {
    "id": user_id,
    "name": user_name,
    "job": user_job_selection,
    "domain": user_domain_selection,
    "domisili": user_domisili_input,
    "shift_A": shift_a_status,
    # ... other fields
}

# Upload
success = self.absensi.upload_to_spreadsheet(record)
```

---

## Configuration

Edit `model/raspy-main-integrated/config.yaml`:

```yaml
google_sheets:
  web_app_url: ""                    # Fill with deployed URL
  retry_interval: 300                # Seconds (5 min default)
  max_retries: 3                     # Number of retry attempts

logging:
  pending_csv: "logs/absensi_pending.csv"              # Failed submissions
  attendance_history_csv: "logs/attendance_history.csv" # Local tracking
```

---

## Common Use Cases

### Use Case 1: Normal Attendance (Registered User)
```
1. User places finger on sensor → Fingerprint match
2. User faces camera → Face recognition match
3. User selects Job (e.g., "PS Muro")
4. User selects Domain (e.g., "Lab Depok")
5. User selects Shift (e.g., Shift A, B)
6. System uploads to Google Sheets
7. Record appears in Google Sheet immediately
```

### Use Case 2: Unregistered User
```
1. User places finger → No match found
2. User faces camera → No face match
3. System captures photo
4. System records as "Unregistered"
5. Admin notified (optional email)
6. Photo saved for manual review
7. Record in Google Sheet with Status="Unregistered"
```

### Use Case 3: Network Offline
```
1. User attendance recorded locally
2. Upload to Google Sheets fails
3. System saves to CSV (logs/absensi_pending.csv)
4. Network comes back online
5. System automatically retries
6. Record syncs to Google Sheets
```

---

## Monitoring

### Check Pending Records
```bash
cd ~/Skripsi/lab
cat logs/absensi_pending.csv  # Failed submissions
cat logs/attendance_history.csv  # Local history
```

### Check System Logs
```bash
tail -f logs/events.log        # System events
tail -f logs/access.log        # Attendance events
```

### Monitor Google Sheets
```
1. Check "Attendance" sheet for new records
2. Check "Configuration" sheet for sync status
3. Review any "Unregistered" entries for manual action
```

---

## Troubleshooting

### Records not appearing in Google Sheets
**Check:**
1. Google Apps Script deployed? (Tools → Script editor)
2. Web App URL correct in config.yaml?
3. Network connectivity? (ping google.com)
4. Check logs: `tail -f logs/events.log`

**If offline:**
- Records saved in `logs/absensi_pending.csv`
- Will sync when online

### Google Apps Script errors
**Check:**
1. Apps Script → Execution log
2. Verify code is correct (see APPS_SCRIPT_SETUP.md)
3. Check permissions are set to "Anyone"

### Photos not saving
**Check:**
1. Camera module connected?
2. Disk space available? (df -h)
3. Log directory permissions? (ls -la logs/)

---

## Best Practices

1. **Regular Backups**
   - Download Google Sheet backup weekly
   - Archive old data to separate sheet

2. **Monitor Unregistered**
   - Review daily for security issues
   - Enroll legitimate new users
   - Report suspicious activity

3. **Network Reliability**
   - Ensure stable WiFi connection
   - Set realistic retry intervals
   - Monitor offline periods

4. **Data Privacy**
   - Limit Google Sheet sharing
   - Regular photo cleanup (> 30 days)
   - Compliance with data protection rules

5. **System Health**
   - Monitor attendance logs
   - Check sensor calibration
   - Verify photo quality

---

## Support & Documentation

For more details, see:
- [SPREADSHEET_STRUCTURE.md](./docs/SPREADSHEET_STRUCTURE.md) - Data schema
- [APPS_SCRIPT_SETUP.md](./docs/APPS_SCRIPT_SETUP.md) - Google Sheets setup
- [ATTENDANCE_FLOW.md](./docs/ATTENDANCE_FLOW.md) - Complete system flow
- [Template Instructions](./spreadsheet-template/Template_Instructions.md) - Template usage

---

## Version Information

- **Module Version:** 1.0
- **Created:** June 2026
- **Compatible with:** Biometric Desktop v1.0
- **Python Version:** 3.8+
- **Google Sheets API:** Google Apps Script v8

---

## License & Credits

Part of: **Biometric Lab Access Control System**  
Developed for: **Robotika Laboratory**  
Created by: Lab Robotika Team, 2026

---

## Next Steps

1. Follow [APPS_SCRIPT_SETUP.md](./docs/APPS_SCRIPT_SETUP.md) to set up Google Sheets
2. Test with [SPREADSHEET_STRUCTURE.md](./docs/SPREADSHEET_STRUCTURE.md) reference
3. Monitor with [ATTENDANCE_FLOW.md](./docs/ATTENDANCE_FLOW.md) guidelines
4. Review logs regularly for system health

---

**Questions or issues?** Check the troubleshooting sections in the documentation files or review system logs at `logs/events.log`.
