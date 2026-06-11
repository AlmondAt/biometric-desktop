# 🎭 Biometric Lab Access Control System

Sistem biometric terintegrasi untuk kontrol akses lab dan manajemen attendance menggunakan fingerprint dan face recognition. Terdiri dari aplikasi desktop (Electron + React), ML pipeline (Python FaceNet/MTCNN), dan sistem Raspberry Pi dengan integrasi Google Sheets.

**Status:** Production Ready v1.0
**Last Updated:** June 2026
**Built dengan:** Electron + React + Express + Python ML + Arduino + Raspberry Pi 5

---

# 🚀 Instalasi & Build Aplikasi Desktop

## Prasyarat

Pastikan sudah terinstall:

* Node.js 18+ (disarankan Node.js 20 LTS)
* NPM
* Python 3.9+
* Git

Verifikasi instalasi:

```bash
node -v
npm -v
python --version
git --version
```

---

## Clone Repository

```bash
git clone https://github.com/AlmondAt/biometric-desktop.git
cd biometric-desktop
```

---

## Konfigurasi Setelah Refactor Struktur Repository

### 1. Update vite.config.ts

Cari:

```ts
export default defineConfig({
  plugins: [
    react(),
    electron([
```

Ubah menjadi:

```ts
export default defineConfig({
  root: 'web_app',

  plugins: [
    react(),
    electron([
```

---

### 2. Update tsconfig.json

Cari:

```json
"include": ["src"]
```

Ubah menjadi:

```json
"include": ["web_app/src"]
```

---

### 3. Update package.json

Cari:

```json
"extraResources": [
  {
    "from": "embedding_extractor",
    "to": "app-resources/embedding_extractor",
    "filter": ["**/*"]
  }
]
```

Ubah menjadi:

```json
"extraResources": [
  {
    "from": "biometric/embedding_extractor",
    "to": "app-resources/embedding_extractor",
    "filter": ["**/*"]
  }
]
```

---

### 4. Update web_app/index.html

Cari:

```html
<script type="module" src="/src/main.tsx"></script>
```

Ubah menjadi:

```html
<script type="module" src="./src/main.tsx"></script>
```

---
## Hapus .gitignore

hapus semua isi yang ada di .gitignore

## Install Dependencies

```bash
npm install
```

---

## Build Application

```bash
npm run build
```

Pastikan proses build selesai tanpa error.

---

## Menjalankan Aplikasi

```bash
npm run dev
```

Untuk saat ini aplikasi masih dijalankan melalui CMD / PowerShell dan belum menggunakan file `.exe` ataupun shortcut desktop.

### Status Saat Ini

* ✅ Electron berjalan melalui command line
* ✅ Development mode menggunakan `npm run dev`
* ✅ Production build menggunakan `npm run build`
* ❌ Belum tersedia installer `.exe`
* ❌ Belum tersedia desktop launcher
* ❌ Belum berjalan sebagai aplikasi desktop standalone

---

## 🎯 Quick Access (Pilih Berdasarkan Kebutuhan)

### 👤 Pengguna Aplikasi Desktop

* 📖 User Tutorial: `docs/pengguna/TUTORIAL_PENGGUNA.md`

### 🔧 Setup & Teknis

* ⚡ Quick Start: `docs/teknisi/QUICK_START.md`
* 📘 Technical Tutorial: `docs/teknisi/TUTORIAL_TEKNISI.md`
* 🏗️ System Documentation: `docs/teknisi/SYSTEM_DOCUMENTATION.md`
* 🔗 Integration Guide: `docs/teknisi/INTEGRATION_GUIDE.md`

### 🎯 Modul Spesifik

* Face Recognition Testing: `biometric/face_recognition_test/README.md`
* ML Pipeline: `biometric/embedding_extractor/README.md`
* Raspberry Pi Main System: `raspberry_pi/raspy-main-integrated/README.md`
* Attendance & Google Sheets: `attendance/docs/APPS_SCRIPT_SETUP.md`

---

## 📂 Struktur Repository

```text
biometric-desktop/
│
├── web_app/
├── biometric/
├── raspberry_pi/
├── attendance/
├── docs/
├── scripts/
│
├── package.json
├── package-lock.json
├── tsconfig.json
├── vite.config.ts
├── electron-builder.bundled.json
├── .env.example
└── .gitignore
```

---

## 🏗️ System Architecture Overview

```text
Desktop App (Electron + React)
            ↓
Backend API (Express)
            ↓
ML Pipeline (FaceNet + MTCNN)
            ↓
Raspberry Pi 5
            ↓
Arduino Nano + Sensors
            ↓
Google Sheets + Apps Script
```

---

## 🔐 Authentication Flow

```text
Touch Sensor
     ↓
Fingerprint Verification
     ↓
Face Recognition
     ↓
Attendance Form
     ↓
Google Sheets Upload
     ↓
Door Unlock
```

---

## 📊 Attendance & Google Sheets

### Data Storage

| Storage       | Purpose             |
| ------------- | ------------------- |
| Google Sheets | Primary Database    |
| CSV Pending   | Offline Queue       |
| SQLite        | Local User Database |

---

## 🌐 Raspberry Pi Configuration

### Start System

```bash
source /home/pi/Skripsi/.venv39/bin/activate
cd ~/Skripsi/lab
python model/raspy-main-integrated/main_integrated.py
```

---

## 🔧 Tech Stack

| Layer    | Technology                   |
| -------- | ---------------------------- |
| Frontend | React 18, TypeScript, Vite   |
| Desktop  | Electron                     |
| Backend  | Express.js                   |
| Database | SQLite                       |
| ML       | FaceNet, MTCNN, OpenCV       |
| Hardware | Raspberry Pi 5, Arduino Nano |
| Cloud    | Google Sheets, Apps Script   |

---

## 🚀 Quick Start

### Desktop Development

```bash
npm install
npm run build
npm run dev
```

### Raspberry Pi

```bash
ssh pi@raspberrypi.local

cd ~/Skripsi/lab

pip install -r requirements.txt

cp config.example.yaml config.yaml

python main_integrated.py
```

---

## 🧪 Development

### Desktop

```bash
npm run dev
npm run build
npm run test
```

### Raspberry Pi

```bash
python -u model/raspy-main-integrated/main_integrated.py 2>&1 | tee logs/debug.log

tail -f logs/access.log

tail -f logs/events.log
```

---

## 🐛 Troubleshooting

### Backend Tidak Jalan

```bash
netstat -an | findstr 3001
```

### Fingerprint Tidak Terdeteksi

```bash
ls -la /dev/ttyUSB*
```

### Google Sheets Gagal Upload

```bash
ping google.com
```

### Kamera Tidak Berjalan

```bash
libcamera-hello --duration 2000
```

---

## 🚀 Next Steps

1. Ikuti `docs/teknisi/QUICK_START.md`
2. Setup Google Apps Script
3. Setup Raspberry Pi
4. Test seluruh hardware
5. Deploy ke lingkungan produksi

---

## 📝 License

MIT License

---

**Ready to enroll faces and manage attendance? Let's go! 🎭**

**Last Updated:** June 2026
**System Version:** v1.0
**Status:** Production Ready
