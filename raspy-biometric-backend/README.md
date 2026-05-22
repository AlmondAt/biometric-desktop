# 🔐 Biometric Backend - Raspberry Pi 5

Sistem backend untuk enrollment face recognition dan database biometrik di Raspberry Pi 5.

## 📋 Struktur Folder

```
raspy-biometric-backend/
├── api_server.py           # Main Flask API server
├── config.yaml             # Konfigurasi sistem
├── requirements.txt        # Python dependencies
├── biometrics.db           # Database (auto-created)
├── modules/
│   ├── __init__.py
│   ├── db_manager.py       # Database operations (SQLite)
│   ├── api_routes.py       # Flask routes/endpoints
│   └── face_matcher.py     # Face matching logic
└── tools/
    ├── enroll_face.py      # CLI tool - enroll wajah
    ├── enroll_fingerprint.py # CLI tool - enroll fingerprint
    └── list_users.py       # CLI tool - list users
```

---

## 🚀 Setup Tahapan

### **Tahap 1: Setup Environment di Raspberry Pi**

#### 1.1 Install Python 3.10
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip
```

#### 1.2 Clone/Copy Project
```bash
cd ~/
git clone <repo-url>  # atau copy folder manual via SCP
cd raspy-biometric-backend
```

#### 1.3 Create Virtual Environment
```bash
python3.10 -m venv venv
source venv/bin/activate
```

#### 1.4 Install Dependencies
```bash
pip install --upgrade pip setuptools
pip install -r requirements.txt
```

**Catatan:** Jika ada error dengan `torch`, install versi CPU:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

---

### **Tahap 2: Setup Database**

#### 2.1 Initialize Database
```bash
python3 << EOF
from modules.db_manager import BiometricDatabase
db = BiometricDatabase('biometrics.db')
print("✅ Database initialized!")
EOF
```

#### 2.2 Verify Database Created
```bash
ls -la biometrics.db
sqlite3 biometrics.db ".tables"  # Should show: embeddings, recognition_logs, users
```

---

### **Tahap 3: Configuration**

#### 3.1 Update `config.yaml`
Edit file sesuai kebutuhan:
- `database.path` - Path ke biometrics.db
- `api.host` - Default: 0.0.0.0 (accessible dari network)
- `api.port` - Default: 5000
- `recognition.similarity_threshold` - Default: 0.5 (0-1, semakin tinggi semakin strict)

---

### **Tahap 4: Enrollment Users**

#### 4.1 Capture & Enroll Wajah
```bash
# Pastikan camera sudah built-in atau USB camera terhubung
python3 tools/enroll_face.py

# Ikuti prompt:
# - Masukkan User ID (cth: "user_001")
# - Masukkan Nama (cth: "Budi Santoso")
# - Tekan SPACE untuk capture 10 photos
# - ESC untuk stop
```

#### 4.2 (Optional) Enroll Fingerprint
```bash
python3 tools/enroll_fingerprint.py

# Ikuti prompt untuk register ID fingerprint
```

#### 4.3 List Enrolled Users
```bash
python3 tools/list_users.py

# Output:
# ID: user_001 | Name: Budi Santoso | Status: active | Embeddings: 10
# ID: user_002 | Name: Rina P | Status: active | Embeddings: 10
```

---

### **Tahap 5: Jalankan API Server**

#### 5.1 Start Server
```bash
# Development mode
python3 api_server.py

# Atau dengan Gunicorn (production)
pip install gunicorn
gunicorn -w 2 -b 0.0.0.0:5000 api_server:app
```

#### 5.2 Verify Server Running
```bash
# Di terminal lain, test API
curl http://localhost:5000/api/status

# Expected response:
# {"status":"online","timestamp":"2026-04-11 10:30:45"}
```

---

### **Tahap 6: Integration dengan Desktop App**

#### 6.1 Update Desktop App Config
Di desktop app (`src/ElectronConfig.ts` atau env):
```javascript
const RASPY_API_URL = "http://<IP-RASPY>:5000";
// Contoh: "http://192.168.1.100:5000"
```

#### 6.2 Test Enrollment dari Desktop
- Desktop capture 10 photos
- Click "Start Training Face"
- Desktop extract embeddings & POST ke `/api/enroll`
- Verify di Raspy: `python3 tools/list_users.py`

#### 6.3 Test Recognition
```bash
# Di desktop app: capture test photo
# Extract embedding & POST ke `/api/recognize`

# Atau test manual di Raspy:
curl -X POST http://localhost:5000/api/recognize \
  -H "Content-Type: application/json" \
  -d '{"embedding": [0.124, -0.456, ...]}'
```

---

## 📡 API Endpoints

### **1. Health Check**
```
GET /api/status
Response: {"status": "online", "timestamp": "2026-04-11 10:30:45"}
```

### **2. Enrollment**
```
POST /api/enroll
Body: {
  "user_id": "user_001",
  "name": "Budi Santoso",
  "embeddings": [[0.124, -0.456, ...], [...], ...],
  "fingerprint_id": "FP001" (optional)
}
Response: {"success": true, "user_id": "user_001"}
```

### **3. Face Recognition**
```
POST /api/recognize
Body: {"embedding": [0.124, -0.456, ...]}
Response: {
  "success": true,
  "matched": true,
  "user_id": "user_001",
  "name": "Budi Santoso",
  "confidence": 0.92
}
```

### **4. List Users**
```
GET /api/users
Response: {
  "success": true,
  "users": [
    {"id": "user_001", "name": "Budi Santoso", "status": "active", "enrollment_date": "2026-04-11"},
    ...
  ]
}
```

### **5. Delete User**
```
DELETE /api/users/<user_id>
Response: {"success": true, "message": "User user_001 deactivated"}
```

---

## 🔧 Troubleshooting

### Camera Not Found
```bash
# List USB devices
lsusb

# Check camera
libcamera-hello --list-cameras

# Or use v4l2
v4l2-ctl --list-devices
```

### Database Locked
```bash
# Check if another process is using it
lsof biometrics.db

# Reset database (hati-hati!)
rm biometrics.db
python3 tools/init_db.py
```

### API Not Accessible from Other Devices
- Check Raspy IP: `hostname -I`
- Check firewall: `sudo ufw status`
- Allow port 5000: `sudo ufw allow 5000`

---

## 📊 Database Schema

### Users Table
```sql
id TEXT PRIMARY KEY
name TEXT NOT NULL
enrollment_date TIMESTAMP
status TEXT (active/inactive)
fingerprint_id TEXT
```

### Embeddings Table
```sql
id INTEGER PRIMARY KEY
user_id TEXT (FK)
embedding BLOB (numpy array as pickle)
created_at TIMESTAMP
```

### Recognition Logs Table
```sql
id INTEGER PRIMARY KEY
user_id TEXT
recognized_name TEXT
confidence REAL
timestamp TIMESTAMP
method TEXT (face/fingerprint)
```

---

## ⚡ Quick Start

```bash
# 1. Setup
source venv/bin/activate
pip install -r requirements.txt

# 2. Init database
python3 << 'EOF'
from modules.db_manager import BiometricDatabase
BiometricDatabase('biometrics.db')
EOF

# 3. Enroll first user
python3 tools/enroll_face.py

# 4. Start server
python3 api_server.py

# 5. Test from desktop app
# POST http://<RASPY-IP>:5000/api/recognize
```

---

## 📝 Notes

- **Python Version:** 3.10+ required
- **Memory:** Min 2GB RAM, rekomendasi 4GB untuk Raspy 5
- **Storage:** Min 2GB untuk models + database
- **Internet:** Opsional (local network only)
- **Security:** API tidak ada authentication - gunakan firewall/VPN untuk production

---

**Ready to go! 🚀**
