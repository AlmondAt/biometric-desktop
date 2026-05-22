# 📚 TUTORIAL TEKNISI - Sistem Biometrik Desktop

## Daftar Isi
1. [Persyaratan Sistem](#persyaratan-sistem)
2. [Setup Awal](#setup-awal)
3. [Instalasi & Konfigurasi](#instalasi--konfigurasi)
4. [Menjalankan Sistem](#menjalankan-sistem)
5. [Arsitektur Sistem](#arsitektur-sistem)
6. [Troubleshooting](#troubleshooting)
7. [Maintenance](#maintenance)

---

## ✅ Persyaratan Sistem

### Hardware
- **Processor**: Intel/AMD Core i5 atau lebih baik (untuk face recognition processing)
- **RAM**: Minimal 8GB (recommended 16GB)
- **Storage**: 20GB free space
- **Webcam**: USB webcam atau built-in dengan kualitas HD
- **Network**: Koneksi ke Raspberry Pi (LAN/WiFi)

### Software
- **Windows 10/11** atau **Linux/macOS**
- **Python 3.10+**
- **Node.js 18+** dengan npm
- **Git** (untuk cloning repository)

### Koneksi
- Raspberry Pi 5 dengan backend biometrik aktif
- IP Raspy dapat diakses dari desktop (sama network atau via VPN)

---

## 🔧 Setup Awal

### 1. Clone Repository
```powershell
# Windows PowerShell
git clone <repo-url> "d:\New folder"
cd "d:\New folder"
```

### 2. Install Python Dependencies
```powershell
# Setup Python virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install embedding extractor requirements
cd embedding_extractor
python -m pip install -r requirements.txt
cd ..
```

### 3. Install Node.js Dependencies
```powershell
npm install
```

---

## 🛠️ Instalasi & Konfigurasi

### Tahap 1: Konfigurasi Backend Python

**File**: `embedding_extractor/config.py`

```python
# Wajib konfigurasi:
SIMILARITY_THRESHOLD = 0.60      # Threshold pengenalan wajah
MODEL_PATH = "./models"           # Path model FaceNet
AUGMENTATION_ENABLED = True       # Enable data augmentation
DATABASE_PATH = "./data"          # Path database lokal
```

### Tahap 2: Konfigurasi Raspy Connection

**File**: `electron/database.ts`

Atur IP dan port Raspy:
```typescript
const RASPY_API_URL = "http://192.168.1.100:5000";  // Sesuaikan IP Raspy
const API_TIMEOUT = 30000;                           // 30 detik timeout
```

### Tahap 3: Konfigurasi Vite & Electron

**File**: `vite.config.ts`

```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,  // Dev server port
    strictPort: false,
  }
})
```

### Tahap 4: Konfigurasi Database Lokal

Database lokal (SQLite) akan dibuat otomatis di:
- Windows: `%APPDATA%/electron-app/database.db`
- Linux: `~/.config/electron-app/database.db`
- macOS: `~/Library/Application Support/electron-app/database.db`

---

## 🚀 Menjalankan Sistem

### Mode Development

```powershell
# Di folder root project
npm run dev
```

**Proses yang berjalan:**
1. Vite dev server (`http://localhost:5173`)
2. Electron main process
3. Express API server (`http://localhost:3001`)

Tunggu sampai:
```
✓ Vite dev server ready
✓ Electron window open
✓ Internal Express API running on port 3001
```

### Mode Production (Build)

```powershell
# Build Frontend & Backend
npm run build

# Package sebagai installer
npm run dist

# Hasil installer ada di ./dist/ folder
```

---

## 🏗️ Arsitektur Sistem

### Komponen Utama

```
┌─────────────────────────────────────────────────────────┐
│           APLIKASI DESKTOP (Windows/Linux/macOS)         │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────┐         ┌──────────────────┐      │
│  │  Frontend React  │◄────────┤  Electron Main   │      │
│  │   (src/*.tsx)    │         │  (electron/*.ts) │      │
│  └──────────────────┘         └──────────────────┘      │
│           │                            │                 │
│           └────────────┬───────────────┘                 │
│                        ▼                                  │
│              ┌──────────────────┐                        │
│              │   Express API    │                        │
│              │  (port 3001)     │                        │
│              └──────────────────┘                        │
│                        │                                  │
│         ┌──────────────┼──────────────┐                  │
│         ▼              ▼              ▼                  │
│    ┌────────┐   ┌──────────┐   ┌──────────┐             │
│    │SQLite  │   │ Python   │   │ Raspy    │             │
│    │Database│   │ Training │   │  API     │             │
│    └────────┘   └──────────┘   └──────────┘             │
│                                       │                  │
└───────────────────────────────────────┼──────────────────┘
                                        │
                        ┌───────────────▼───────────────┐
                        │   RASPBERRY PI BACKEND        │
                        │  (main_integrated.py)         │
                        │                               │
                        │  ├─ Face Recognition DB       │
                        │  ├─ Embeddings Storage        │
                        │  ├─ Access Logs               │
                        │  └─ Device State Machine      │
                        └───────────────────────────────┘
```

### Flow Data Enrollment

```
1. User Submit Foto via UI
   ↓
2. Electron → Express API (/api/training/start)
   ↓
3. Express → Spawn Python Process (training_api.py)
   ↓
4. Python:
   ├─ Load MTCNN & FaceNet models
   ├─ Deteksi wajah di setiap foto
   ├─ Generate 50 augmentasi per foto
   ├─ Extract embedding dari 512-D space
   └─ Simpan embeddings.pkl
   ↓
5. Python → Express (return hasil)
   ↓
6. Express → Electron UI (show success)
   ↓
7. Upload embeddings.pkl ke Raspy via API
```

---

## 🔍 Troubleshooting

### ❌ Problem: "Express API not running"

**Diagnosis:**
```powershell
# Check apakah port 3001 sudah digunakan
netstat -ano | findstr :3001
```

**Solusi:**
```powershell
# Buat process baru menggunakan port berbeda
# Edit di electron/main.ts, ubah PORT = 3002
# Kemudian restart npm run dev
```

### ❌ Problem: "Connection refused ke Raspy"

**Check koneksi:**
```powershell
# Test ping ke Raspy
ping 192.168.1.100

# Test akses API Raspy
curl http://192.168.1.100:5000/api/status
```

**Jika tidak respond:**
1. Pastikan Raspy sudah boot
2. Cek IP address Raspy (gunakan `hostname -I` di Raspy)
3. Cek firewall settings
4. Update IP di `electron/database.ts`

### ❌ Problem: "Python module not found"

**Solusi:**
```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Install/upgrade requirements
cd embedding_extractor
python -m pip install --upgrade -r requirements.txt

# Specific packages
python -m pip install torch facenet-pytorch mtcnn pillow opencv-python
```

### ❌ Problem: Training sangat lambat (>5 menit)

**Penyebab:**
- CPU bottleneck (processing 50 augmentasi per foto)
- Model belum di-cache (first run: load dari disk)
- Banyak foto yang di-process

**Solusi:**
```python
# Edit embedding_extractor/config.py
AUGMENTATION_COUNT = 30  # Kurangi dari 50 ke 30
BATCH_SIZE = 8          # Increase batch processing
```

### ❌ Problem: "embeddings.pkl not found" saat recognition

**Penyebab:** Training gagal atau belum dijalankan

**Debug:**
```powershell
# Cek file embeddings.pkl
ls "d:\New folder\embeddings.pkl"

# Lihat console/logs saat training
# Cari error messages di training process
```

### ❌ Problem: "NOT IDENTIFIED" saat test recognition

**Penyebab:** 
- Threshold terlalu tinggi
- Foto training terlalu sedikit
- Kondisi lighting berbeda saat capture vs recognition

**Solusi:**
```python
# Edit config.py - turunkan threshold
SIMILARITY_THRESHOLD = 0.55  # Dari 0.60 ke 0.55

# Atau tambah foto training (15-20 foto lebih baik)
```

### ❌ Problem: Webcam tidak terdeteksi

**Check:**
```powershell
# List available cameras di Windows
wmic logicaldisk get name

# Test dengan Python
python -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"
```

---

## 🔧 Maintenance

### Backup Data

```powershell
# Backup database lokal
Copy-Item "$env:APPDATA\electron-app\database.db" `
          "D:\Backup\database_$(Get-Date -Format 'yyyyMMdd').db"

# Backup embeddings dari Raspy
# SSH ke Raspy:
ssh pi@192.168.1.100
scp pi@192.168.1.100:~/embeddings.pkl D:\Backup\
```

### Update System

```powershell
# Update dependencies
npm update
cd embedding_extractor && pip install --upgrade -r requirements.txt

# Test sebelum production
npm run dev
# Test enrollment & recognition flow
```

### Monitoring

**Check Log Files:**
- Electron: Developer Tools (Ctrl+Shift+I)
- Express API: Console saat `npm run dev`
- Python: stdout/stderr dari training process

**Health Check Raspy:**
```powershell
curl http://192.168.1.100:5000/api/status
```

Expected response:
```json
{
  "status": "ok",
  "users_count": 5,
  "db_path": "/home/pi/biometrics.db"
}
```

---

## 📋 Checklist Deployment

- [ ] Python dependencies terinstall & test
- [ ] Node.js dependencies terinstall
- [ ] Koneksi ke Raspy verified
- [ ] IP Raspy benar di config
- [ ] Database lokal dapat diakses
- [ ] Webcam terdeteksi & berfungsi
- [ ] Development mode berjalan tanpa error
- [ ] Test enrollment dengan minimal 3 user
- [ ] Test recognition & verify threshold
- [ ] Backup database & config

---

## 📞 Support

**Untuk bantuan lebih lanjut:**
1. Check `ts_errors.txt` untuk TypeScript compilation errors
2. Baca log di Electron DevTools (Ctrl+Shift+I)
3. Test minimal flow: capture foto → training → recognition
