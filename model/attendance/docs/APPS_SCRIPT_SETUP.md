# GOOGLE_APPS_SCRIPT_SETUP.md

## Overview

Panduan setup Google Sheets dan Google Apps Script untuk sistem absensi biometrik.

Sistem ini menerima data absensi dari Raspberry Pi kemudian:

* Menyimpan data ke Google Sheets
* Membuat timestamp otomatis
* Menghitung mutu shift otomatis
* Menghitung total mutu otomatis
* Menghitung jumlah akses otomatis
* Menentukan status Registered / Unregistered otomatis

---

# Step 1 - Create Google Spreadsheet

Buat spreadsheet baru dengan nama:

```text
Biometric Attendance System
```

Rename sheet pertama menjadi:

```text
Attendance
```

---

# Step 2 - Setup Spreadsheet Header

Mulai dari row 2.

| A         | B  | C    | D       | E      | F       | G      | H       | I      | J       | K      | L       | M      | N        | O      | P     | Q           |
| --------- | -- | ---- | ------- | ------ | ------- | ------ | ------- | ------ | ------- | ------ | ------- | ------ | -------- | ------ | ----- | ----------- |
| Timestamp | ID | Name | Shift A | Mutu A | Shift B | Mutu B | Shift C | Mutu C | Shift D | Mutu D | Shift E | Mutu E | Domisili | Status | Akses | Total Shift |

Row 1 boleh digunakan untuk title.

Contoh:

```text
A1: Biometric Attendance System
```

Data akan mulai ditulis dari row 3.

---

# Step 3 - Create Google Apps Script

Buka:

Extensions → Apps Script

Hapus semua kode default.

Paste kode berikut:

```javascript
function doPost(e){

  try{

    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Attendance");
    var data = JSON.parse(e.postData.contents);

    var mutuMap = {
      "0":0,
      "1":1,
      "2":1.5,
      "3":2.5,
      "4":2,
      "5":3,
      "6":5,
      "7":6,
      "8":4,
      "9":"",
      "A":3,
      "B":2,
      "C":""
    };

    var row = Math.max(sheet.getLastRow()+1,3);

    var now = new Date();

    sheet.getRange(row,1).setValue(now);
    sheet.getRange(row,1).setNumberFormat("yyyy-mm-dd hh:mm:ss");

    sheet.getRange(row,2).setValue(data.id || "");
    sheet.getRange(row,3).setValue(data.name || "");

    var totalMutu = 0;

    function isiShift(n,kode){

      if(!kode) return;

      kode = String(kode).toUpperCase();

      var mutu = mutuMap[kode] ?? "";

      var ketCol = 3 + (n*2 -1);
      var mutuCol = 3 + (n*2);

      sheet.getRange(row,ketCol).setValue(kode);
      sheet.getRange(row,mutuCol).setValue(mutu);

      if(typeof mutu === "number"){
        totalMutu += mutu;
      }
    }

    isiShift(1,data.shift_A);
    isiShift(2,data.shift_B);
    isiShift(3,data.shift_C);
    isiShift(4,data.shift_D);
    isiShift(5,data.shift_E);

    sheet.getRange(row,14).setValue(data.domisili || "-");

    var status =
      (data.name && data.id)
      ? "Registered"
      : "Unregistered";

    sheet.getRange(row,15).setValue(status);

    var id = data.id;
    var aksesCount = 1;

    if(id){

      var lastRow = sheet.getLastRow();

      if(lastRow >= 3){

        var idColumn = sheet
          .getRange(3,2,lastRow-2,1)
          .getValues();

        aksesCount = idColumn.filter(function(r){
          return r[0] == id;
        }).length;
      }
    }

    sheet.getRange(row,16).setValue(aksesCount);

    sheet.getRange(row,17).setValue(totalMutu);

    return ContentService
      .createTextOutput(JSON.stringify({
        status:"success",
        total_shift:totalMutu
      }))
      .setMimeType(ContentService.MimeType.JSON);

  }
  catch(err){

    return ContentService
      .createTextOutput(JSON.stringify({
        status:"error",
        message:err.toString()
      }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
```

Simpan project.

---

# Step 4 - Deploy Apps Script

Klik:

```text
Deploy
→ New Deployment
→ Web App
```

Konfigurasi:

```text
Execute As:
Me

Who Has Access:
Anyone
```

Klik:

```text
Deploy
```

Lalu copy URL yang diberikan.

Contoh:

```text
https://script.google.com/macros/s/xxxxxxxxxxxxxxxxxxxxxxxxxxxxx/exec
```

---

# Step 5 - Configure Raspberry Pi

Masukkan URL tersebut ke config aplikasi.

Contoh:

```yaml
google_sheets:
  web_app_url: "https://script.google.com/macros/s/xxxxxxxxxxxxxxxxxxxxxxxxxxxxx/exec"
```

---

# JSON Payload

Raspberry Pi hanya perlu mengirim:

```json
{
  "id":"101",
  "name":"Muhammad Al Farizi",
  "domisili":"Bekasi",
  "shift_A":"1",
  "shift_B":"5",
  "shift_C":"A",
  "shift_D":"",
  "shift_E":""
}
```

Tidak perlu mengirim:

* status
* timestamp
* akses
* total_shift

Karena semuanya dihitung otomatis oleh Apps Script.

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

Jika:

```text
ID ada
dan
Name ada
```

Maka:

```text
Registered
```

Selain itu:

```text
Unregistered
```

---

# Access Counter Logic

Setiap ID akan dihitung otomatis.

Contoh:

```text
ID 101 Login Pertama
Akses = 1

ID 101 Login Kedua
Akses = 2

ID 101 Login Ketiga
Akses = 3
```

---

# Total Shift Logic

Contoh:

```text
Shift_A = 1
Shift_B = 5
Shift_C = A
```

Mutu:

```text
1 + 3 + 3
```

Total Shift:

```text
7
```

---

# Test Using CURL

```bash
curl -X POST \
"https://script.google.com/macros/s/xxxxxxxxxxxxxxxxxxxxxxxxxxxxx/exec" \
-H "Content-Type: application/json" \
-d '{
"id":"101",
"name":"Muhammad Al Farizi",
"domisili":"Bekasi",
"shift_A":"1",
"shift_B":"5",
"shift_C":"A"
}'
```

Response:

```json
{
  "status":"success",
  "total_shift":7
}
```

---

# Attendance Flow

```text
Touch Sensor
      ↓
Fingerprint Verification
      ↓
Face Recognition
      ↓
Attendance Form
      ↓
Submit Attendance
      ↓
Raspberry Pi
      ↓
Google Apps Script
      ↓
Google Sheets

Apps Script:
- Generate Timestamp
- Generate Status
- Count Access
- Convert Shift To Mutu
- Calculate Total Shift
```

---

# Troubleshooting

## Sheet Not Found

Pastikan nama sheet:

```text
Attendance
```

harus sama persis.

## Permission Error

Pastikan deployment menggunakan:

```text
Who Has Access:
Anyone
```

## Data Not Appearing

Periksa:

```text
Apps Script Logs
Executions
```

untuk melihat error terbaru.

## Invalid JSON

Pastikan Raspberry Pi mengirim:

```text
Content-Type: application/json
```

dan format JSON valid.

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
- Timestamp
- ID
- Name
- Shift
- Mutu
- Domisili
- Status
- Akses
- Total Shift
```
