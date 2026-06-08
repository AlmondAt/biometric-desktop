# SETUP INSTRUCTIONS

## ⚡ Quick Setup (5 menit)

### 1. Prerequisites
- Python 3.10+
- pip
- Webcam/USB Camera (untuk enrollment)
- ~2GB RAM

### 2. Install

```bash
cd raspy-biometric-backend
chmod +x setup.sh
./setup.sh
```

Atau manual:
```bash
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. First Run

**Enroll first user:**
```bash
python3 tools/enroll_face.py
```

**Start API server:**
```bash
python3 api_server.py
```

**Test in another terminal:**
```bash
curl http://localhost:5000/api/status
```

---

## 📋 Command Reference

### Enrollment
```bash
# Capture 10 face photos dan extract embeddings
python3 tools/enroll_face.py

# Register fingerprint ID untuk user
python3 tools/enroll_fingerprint.py

# List all enrolled users
python3 tools/list_users.py
```

### Server
```bash
# Development mode
python3 api_server.py

# Production with Gunicorn
gunicorn -w 2 -b 0.0.0.0:5000 api_server:app
```

### Database
```bash
# Initialize fresh database
python3 << 'EOF'
from modules.db_manager import BiometricDatabase
db = BiometricDatabase('biometrics.db')
EOF

# Check database content with SQLite CLI
sqlite3 biometrics.db
sqlite> SELECT COUNT(*) FROM users;
sqlite> SELECT id, name, status FROM users;
sqlite> .quit
```

---

## 🔌 API Endpoints

All endpoints return JSON responses.

### 1. Status
```
GET /api/status
Response: {"status": "online", "stats": {...}}
```

### 2. Enroll User
```
POST /api/enroll
Body: {
  "user_id": "user_001",
  "name": "Budi Santoso",
  "embeddings": [[0.1, -0.2, ...], [...]],
  "fingerprint_id": "FP001" (optional)
}
Response: {"success": true, "user_id": "user_001"}
```

### 3. Recognize Face
```
POST /api/recognize
Body: {"embedding": [0.1, -0.2, ...]}
Response: {
  "success": true,
  "matched": true,
  "user_id": "user_001",
  "name": "Budi Santoso",
  "confidence": 0.95
}
```

### 4. Get Users
```
GET /api/users?status=active
Response: {
  "success": true,
  "count": 5,
  "users": [...]
}
```

### 5. Get User Details
```
GET /api/users/user_001
Response: {
  "success": true,
  "user": {...}
}
```

### 6. Delete User
```
DELETE /api/users/user_001?action=deactivate
```

### 7. Stats
```
GET /api/stats
Response: {
  "success": true,
  "stats": {
    "active_users": 5,
    "total_embeddings": 50
  }
}
```

---

## 🐛 Troubleshooting

### Camera Not Found
```bash
# Check connected cameras
v4l2-ctl --list-devices

# Or use libcamera (Raspy OS)
libcamera-hello --list-cameras
```

### Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000

# Kill it
kill -9 <PID>
```

### Database Locked
```bash
# Check if another process uses it
lsof biometrics.db

# Reset database
rm biometrics.db
python3 tools/enroll_face.py
```

### Import Errors
```bash
# Reinstall requirements
pip install --force-reinstall -r requirements.txt

# For torch CPU version
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

---

## 📊 Database Structure

### users table
```sql
id              TEXT PRIMARY KEY
name            TEXT
enrollment_date TIMESTAMP
status          TEXT (active/inactive)
fingerprint_id  TEXT
notes           TEXT
```

### embeddings table
```sql
id          INTEGER PRIMARY KEY
user_id     TEXT (FK)
embedding   BLOB (numpy array)
created_at  TIMESTAMP
source      TEXT
```

### recognition_logs table
```sql
id              INTEGER PRIMARY KEY
user_id         TEXT
recognized_name TEXT
confidence      REAL (0-1)
timestamp       TIMESTAMP
method          TEXT (face/fingerprint)
device          TEXT
```

---

## 🔒 Security Notes

⚠️ **This backend is NOT production-ready without:**

1. **Authentication** - Add API key/token validation
2. **HTTPS** - Use SSL/TLS certificates
3. **Rate Limiting** - Prevent brute force attacks
4. **Input Validation** - Sanitize all inputs
5. **Database Backup** - Regular backups
6. **Firewall** - Restrict access to local network only

For production deployment:
- Use Gunicorn + Nginx
- Add reverse proxy authentication
- Implement request signing
- Monitor logs and alerts

---

## 💡 Tips

1. **Similarity Threshold:** Edit `config.yaml` to adjust strictness
   - 0.5 = permissive (more false positives)
   - 0.7 = balanced (recommended)
   - 0.9 = strict (more false negatives)

2. **Multiple Embeddings:** Store 10+ embeddings per user for better accuracy

3. **Lighting:** Enroll in different lighting conditions for robustness

4. **Distance:** Keep face 30-60cm from camera during enrollment

---

**Questions? Check README.md for full documentation!**
