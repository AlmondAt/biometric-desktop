# Google Apps Script Setup Guide

## Overview
Panduan lengkap untuk setup Google Apps Script dan menghubungkannya dengan Raspberry Pi.

---

## Prerequisites

- Google Account
- Google Sheets access
- Raspberry Pi yang sudah berjalan
- config.yaml siap dikonfigurasi

---

## Step 1: Create Google Sheet

### 1.1 Open Google Sheets
```
1. Buka https://sheets.google.com
2. Klik "Blank" untuk membuat sheet baru
3. Beri nama: "Biometric Lab Attendance"
4. Klik "Create"
```

### 1.2 Setup Attendance Sheet
```
1. Klik sheet tab (default: Sheet1)
2. Rename menjadi "Attendance"
3. Buat header row dengan kolom:
   A: ID
   B: Nama
   C: Job
   D: Domain
   E: Domisili
   F: Shift_A
   G: Shift_B
   H: Shift_C
   I: Shift_D
   J: Shift_E
   K: Tanggal
   L: Waktu
   M: Status
   N: Akses
   O: Metode
   P: Foto
```

### 1.3 Setup Configuration Sheet (Optional)
```
1. Klik "+" untuk add sheet
2. Rename menjadi "Configuration"
3. Buat setup dengan:
   A1: "Setting"    B1: "Value"
   A2: "Web App URL" B2: [Will fill later]
   A3: "Last Sync"   B3: [Will auto-update]
```

---

## Step 2: Create Google Apps Script

### 2.1 Open Script Editor
```
1. Di Google Sheet, klik menu: Tools → Script editor
2. Ini akan membuka Apps Script page di tab baru
```

### 2.2 Replace Default Code
```
1. Di Script Editor, hapus semua code default
2. Paste code berikut:
```

### Sample Apps Script Code

```javascript
/**
 * Biometric Lab Attendance System
 * Google Apps Script Backend
 * 
 * Receives attendance data from Raspberry Pi and stores in Google Sheets
 */

// Configuration
const SHEET_NAME = "Attendance";
const CONFIG_SHEET = "Configuration";

/**
 * Main endpoint: Receives POST requests from Raspberry Pi
 * Expected payload:
 * {
 *   id: "101",
 *   name: "John Doe",
 *   job: "PS Muro",
 *   domain: "Lab Depok",
 *   domisili: "Jakarta",
 *   shift_A: "1",
 *   shift_B: "1",
 *   shift_C: "0",
 *   shift_D: "0",
 *   shift_E: "0",
 *   status: "Registered",
 *   akses: "1",
 *   metode: "biometrik",
 *   tanggal: "2026-06-09",
 *   waktu: "14:30:15"
 * }
 */
function doPost(e) {
  try {
    const payload = JSON.parse(e.postData.contents);
    
    // Validate required fields
    if (!payload.tanggal || !payload.waktu) {
      return ContentService.createTextOutput("ERROR: Missing date/time")
        .setMimeType(ContentService.MimeType.JSON);
    }
    
    // Get or create sheet
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
    
    if (!sheet) {
      return ContentService.createTextOutput("ERROR: Attendance sheet not found")
        .setMimeType(ContentService.MimeType.JSON);
    }
    
    // Append data to sheet
    const newRow = [
      payload.id || "",
      payload.name || "",
      payload.job || "",
      payload.domain || "",
      payload.domisili || "",
      payload.shift_A || "0",
      payload.shift_B || "0",
      payload.shift_C || "0",
      payload.shift_D || "0",
      payload.shift_E || "0",
      payload.tanggal || "",
      payload.waktu || "",
      payload.status || "Unregistered",
      payload.akses || "",
      payload.metode || "biometrik",
      payload.foto || ""
    ];
    
    sheet.appendRow(newRow);
    
    // Update last sync time
    updateLastSync();
    
    // Log successful submission
    Logger.log("Attendance recorded: " + payload.name + " at " + payload.tanggal + " " + payload.waktu);
    
    return ContentService.createTextOutput("OK")
      .setMimeType(ContentService.MimeType.JSON);
    
  } catch (error) {
    Logger.log("ERROR: " + error.toString());
    return ContentService.createTextOutput("ERROR: " + error.toString())
      .setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * Update last sync timestamp
 */
function updateLastSync() {
  try {
    const configSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG_SHEET);
    if (!configSheet) return;
    
    const now = new Date();
    const formattedTime = Utilities.formatDate(now, Session.getScriptTimeZone(), "yyyy-MM-dd HH:mm:ss");
    
    configSheet.getRange("B3").setValue(formattedTime);
  } catch (e) {
    Logger.log("Could not update sync time: " + e.toString());
  }
}

/**
 * (Optional) Process GET request for health check
 */
function doGet(e) {
  return ContentService.createTextOutput("Biometric Lab Attendance - Apps Script Active")
    .setMimeType(ContentService.MimeType.TEXT);
}

/**
 * (Optional) Send email notification on attendance
 * Uncomment and modify email address as needed
 */
function sendNotification(name, status) {
  // const email = "admin@example.com";
  // const subject = "Attendance: " + name;
  // const message = name + " - " + status;
  // GmailApp.sendEmail(email, subject, message);
}

/**
 * (Optional) Create daily summary report
 */
function createDailySummary() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  const data = sheet.getDataRange().getValues();
  
  // Count registrations by status
  const registered = data.filter(row => row[12] === "Registered").length;
  const unregistered = data.filter(row => row[12] === "Unregistered").length;
  
  Logger.log("Daily Summary: " + registered + " Registered, " + unregistered + " Unregistered");
}
```

### 2.3 Save the Script
```
1. Klik "Save" (atau Ctrl+S)
2. Beri nama: "Biometric Attendance Handler"
3. Klik "Save"
```

---

## Step 3: Deploy as Web App

### 3.1 Create Deployment
```
1. Di Apps Script editor, klik "Deploy" → "New Deployment"
2. Klik icon gear (⚙️) untuk pilih tipe
3. Pilih "Web app"
```

### 3.2 Configure Deployment
```
Execute as: [Your email address]
Who has access: Anyone
```

**Important:** "Anyone" diperlukan agar Raspberry Pi bisa akses tanpa auth.

### 3.3 Authorize
```
1. Klik "Authorize access"
2. Pilih Google Account
3. Klik "Allow" untuk authorize access ke Sheets
```

### 3.4 Get Web App URL
```
1. Deployment akan selesai
2. Copy URL yang ditampilkan
3. Format: https://script.google.com/macros/d/[ID]/usercontent
4. SIMPAN URL INI - akan digunakan di Raspberry Pi
```

**Example URL:**
```
https://script.google.com/macros/d/1a2b3c4d5e6f7g8h9i0j/usercontent
```

---

## Step 4: Configure Raspberry Pi

### 4.1 Update config.yaml
```yaml
google_sheets:
  web_app_url: "https://script.google.com/macros/d/[ID]/usercontent"
  retry_interval: 300      # 5 minutes
  max_retries: 3
```

### 4.2 Test Connection
```bash
# SSH ke Raspberry Pi
ssh pi@raspberrypi.local

# Test curl
curl -X POST https://script.google.com/macros/d/[ID]/usercontent \
  -H "Content-Type: application/json" \
  -d '{"id":"101","name":"Test User","tanggal":"2026-06-09","waktu":"14:30:00","status":"Registered","metode":"biometrik"}'

# Response: OK
```

---

## Step 5: Test the System

### 5.1 Manual Test via Postman
```
1. Buka Postman (atau gunakan curl)
2. Method: POST
3. URL: https://script.google.com/macros/d/[ID]/usercontent
4. Headers: Content-Type: application/json
5. Body (JSON):
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
6. Klik "Send"
7. Response: OK
8. Check Google Sheet - data harus ada di Attendance sheet
```

### 5.2 Test via Raspberry Pi System
```bash
# Run the system
cd ~/Skripsi/lab
python main_integrated.py

# Perform attendance:
# 1. Touch sensor
# 2. Fingerprint verification
# 3. Face recognition
# 4. Select job/domain/shift
# 5. Confirm

# Check if data appears in Google Sheet
```

---

## Step 6: Handle Errors

### Error: "Script not deployed"
```
✅ Solution:
1. Make sure you clicked "Deploy" → "New Deployment"
2. Verify deployment status is "Active"
3. Check that Web App URL is correct
```

### Error: "Permission denied"
```
✅ Solution:
1. Re-authorize the script
2. Make sure "Who has access" is set to "Anyone"
3. Check Google Account permissions
```

### Error: "Sheet not found"
```
✅ Solution:
1. Verify sheet name is exactly "Attendance"
2. Check if sheet exists (not deleted)
3. Rename sheet if needed
```

### Error: 404 Not Found
```
✅ Solution:
1. Verify Web App URL is correct
2. Check if deployment is active
3. Redeploy if necessary
```

### Error: Data not appearing in Sheet
```
✅ Debugging:
1. Check Google Sheets Execution Logs:
   - Apps Script → Execution log
   - Look for error messages
2. Verify column headers match script
3. Check if Raspberry Pi is sending correct JSON
4. Verify network connectivity
```

---

## Advanced Features

### 1. Email Notifications
Uncomment di Apps Script:
```javascript
function sendNotification(name, status) {
  const email = "your-email@gmail.com";
  const subject = "Attendance: " + name;
  const message = name + " marked as " + status;
  GmailApp.sendEmail(email, subject, message);
}

// Call in doPost:
sendNotification(payload.name, payload.status);
```

### 2. Daily Summary Report
```javascript
function createDailySummary() {
  // Buat summary setiap hari
  // Bisa di-schedule via Triggers
}

// Setup trigger:
// Apps Script → Triggers → Add trigger
// Function: createDailySummary
// Event: Time-driven → Day timer → Midnight to 1am
```

### 3. Data Backup
```javascript
function backupData() {
  // Backup sheet data ke Drive
  // Or export to CSV
}
```

### 4. Photo Storage
Untuk menyimpan foto ke Google Drive:
```javascript
// Modify doPost to accept foto as base64
// Decode dan simpan ke Drive folder
```

---

## Troubleshooting Network Issues

### Raspberry Pi Cannot Connect to Internet
```
1. Check WiFi connection: iwconfig
2. Ping Google: ping google.com
3. Check firewall: sudo ufw status
4. Verify DNS: cat /etc/resolv.conf
```

### Timeout Errors
```
1. Increase timeout di config.yaml:
   retry_interval: 600  # 10 minutes
   
2. Check network latency: ping script.google.com

3. Verify Apps Script is running fast
   - Check execution logs
   - Optimize code if slow
```

### SSL/Certificate Errors
```
1. Update certificates:
   sudo apt update && sudo apt install ca-certificates

2. Verify date/time on Raspberry Pi:
   date
   timedatectl
```

---

## Best Practices

### 1. Security
- ❌ Don't hardcode sensitive data in script
- ✅ Use environment variables in config.yaml
- ✅ Share Google Sheet only with authorized users
- ✅ Regularly review access logs

### 2. Performance
- ✅ Keep script code minimal
- ✅ Use batch operations if possible
- ✅ Monitor Apps Script quotas

### 3. Reliability
- ✅ Implement retry logic (already in absensi_utils.py)
- ✅ Monitor pending CSV for failed submissions
- ✅ Regularly backup Google Sheet
- ✅ Test connectivity before going live

### 4. Monitoring
- ✅ Check execution logs regularly
- ✅ Monitor "Unregistered" entries
- ✅ Verify data accuracy
- ✅ Set up alerts for failures

---

## Deployment Checklist

Before going live:
- [ ] Google Sheet created and named correctly
- [ ] Apps Script code deployed
- [ ] Web App URL copied
- [ ] Raspberry Pi config.yaml updated with URL
- [ ] Manual test via Postman passed
- [ ] System test via Raspberry Pi passed
- [ ] Error handling tested
- [ ] Network connectivity verified
- [ ] Access permissions configured
- [ ] Backup strategy in place

---

## Next Steps

1. Review [SPREADSHEET_STRUCTURE.md](./SPREADSHEET_STRUCTURE.md) untuk data mapping
2. Review [ATTENDANCE_FLOW.md](./ATTENDANCE_FLOW.md) untuk alur lengkap
3. Monitor system during first week of deployment
4. Collect feedback dari users

---

## Support & Troubleshooting

For detailed logs:
```bash
# Raspberry Pi logs
cat logs/events.log
cat logs/access.log
cat logs/absensi_pending.csv

# Google Apps Script logs
# Tools → Execution log di Apps Script editor
```

---

**Last Updated:** June 2026  
**Compatible with:** Biometric Desktop v1.0
