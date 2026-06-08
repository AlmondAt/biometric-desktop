# Quick Start - After Fix

## ✅ What Changed
- **Added:** Stub enrollment methods (prevent crashes)
- **Removed:** Broken enrollment logic from main_integrated.py
- **Fixed:** Nothing - verification logic was already correct!
- **Result:** System now works for verification & attendance

---

## 🚀 To Use the System

### 1️⃣ Setup Users in Database
```bash
cd ~/Skripsi/lab
sqlite3 database/biometrics.db

# Add user
INSERT INTO users (id, name, access_level) VALUES (101, 'John Doe', 0);
INSERT INTO users (id, name, access_level) VALUES (102, 'Jane Smith', 0);
.exit
```

### 2️⃣ Enroll Face (Before first use)
```bash
cd ~/Skripsi/lab/face

# For John
python capture_face.py --name "John Doe"
# Press SPACE to capture 5 poses (frontal, left, right, smile, other)

# For Jane  
python capture_face.py --name "Jane Smith"

# Verify enrollment
python manage_faces.py --action list
```

### 3️⃣ Enroll Fingerprint (Optional but recommended)
```bash
cd ~/Skripsi/lab/fingerprint

# For John (ID 101)
python fingerprint_wrapper.py --action enroll --user_id 101
# Place finger 3 times on sensor

# For Jane (ID 102)
python fingerprint_wrapper.py --action enroll --user_id 102

# Verify
python fingerprint_wrapper.py --action list
```

### 4️⃣ Run Main System
```bash
cd ~/Skripsi/lab
python main_integrated.py
```

**System will:**
1. Boot → Splash screen → Idle
2. Wait for touch sensor
3. Scan fingerprint → Verify against DB
4. Verify face → Compare with enrollments
5. Show menu → Select job & domain
6. Submit attendance → Google Sheets ✅

---

## 📊 Verification Flow

```
Touch activated
    ↓
Fingerprint scan
    ├─ Found? → Get user_id & name from DB ✅
    └─ Not found? → Fail, return to idle ❌
    ↓
Face verification
    ├─ Load embeddings.pkl
    ├─ Resolve user_id → name (via DB)
    ├─ Get reference embedding for name
    ├─ Capture frame → Extract embedding
    ├─ Compare similarity (cosine)
    ├─ Similarity > 0.7? → Match ✅
    └─ Otherwise → Fail, return to idle ❌
    ↓
Menu (if both verified)
    ├─ A: Select job (1:PS Muro, 2:DM, 3:Lanjut)
    ├─ B: Select domain (A:Depok, B:Kmal, C:Karawaci)  
    ├─ #: Submit → Google Sheets ✅
    └─ *: Reset

Emergency unlock
    └─ Button push → Open door 5s
```

---

## 🔧 If Something Fails

### "Fingerprint not found"
```bash
# Check DB has the user
sqlite3 database/biometrics.db
> SELECT id, name, fingerprint_id FROM users WHERE id=101;

# If fingerprint_id is NULL, re-enroll
cd fingerprint
python fingerprint_wrapper.py --action enroll --user_id 101
```

### "Face not found in database"
```bash
# Check embeddings
cd face
python manage_faces.py --action list

# If missing, enroll
python capture_face.py --name "John Doe"

# Verify
python manage_faces.py --action info
```

### "Camera not working"
```bash
# Check device
v4l2-ctl --list-devices

# Try specific device in config
face_timeout: 15  # Increase if needed
use_rpicam: true  # Use rpicam-jpeg fallback
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `database/biometrics.db` | User records (id, name, fingerprint_id) |
| `database/embeddings.pkl` | Face embeddings {"name": array} |
| `face/capture_face.py` | Enroll faces |
| `fingerprint/fingerprint_wrapper.py` | Enroll fingerprints |
| `config.yaml` | System configuration |
| `main_integrated.py` | Main attendance system |

---

## 🎯 Admin PIN (Optional)

If you want to access admin menu in system:
1. Press `#` in IDLE state
2. Enter PIN (default: **1234**)
3. Shows "Use CLI tools" message
4. Press `*` to go back

**Note:** Actual enrollment must be done via CLI tools (capture_face.py, fingerprint_wrapper.py)

---

## ✅ Checklist Before Running

- [ ] Database created: `sqlite3 database/biometrics.db`
- [ ] Users added to DB with id, name
- [ ] Faces enrolled: `python face/capture_face.py --name "..."`
- [ ] Verify face list: `python face/manage_faces.py --action list`
- [ ] Fingerprints enrolled (optional): `python fingerprint/fingerprint_wrapper.py --action enroll --user_id [ID]`
- [ ] Camera connected: `v4l2-ctl --list-devices`
- [ ] Arduino connected: Check config.yaml serial ports
- [ ] Google Sheets URL in config.yaml is correct
- [ ] GPIO pins correct for relay

---

**Last Updated:** 2026-03-06  
**Status:** ✅ Ready to use
