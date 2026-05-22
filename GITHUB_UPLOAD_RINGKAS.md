# 🚀 PANDUAN CEPAT: UPLOAD KE GITHUB

**Panduan praktis untuk upload aplikasi ke GitHub agar bisa langsung jalan**

---

## 🎯 Ringkasan: File Apa Yang Harus Upload?

### ✅ UPLOAD INI (Source Code & Config)
```
✅ package.json + package-lock.json
✅ src/ (React components)
✅ electron/ (Electron main)
✅ embedding_extractor/ (Python ML)
✅ face_recognition_test/ (Python testing)
✅ raspy-biometric-backend/ (Backend)
✅ tsconfig.json, vite.config.ts
✅ Semua file .md dokumentasi
✅ .gitignore
✅ .env.example (template only!)
```

### ❌ JANGAN UPLOAD INI (Artifacts & Data)
```
❌ node_modules/
❌ dist/, dist-electron/
❌ bundle/
❌ venv/, env/
❌ *.db (database files)
❌ *.pkl (embeddings files)
❌ .env (production config)
❌ logs/, __pycache__/
❌ .vscode/, .idea/ (personal settings)
```

---

## ⚡ 4 Langkah Upload ke GitHub

### Langkah 1: Cleanup Local
```bash
# Windows PowerShell
Remove-Item -Recurse -Force node_modules, dist, dist-electron, bundle, venv, __pycache__, .idea
Remove-Item -Path .env, *.db, *.pkl -ErrorAction SilentlyContinue
```

### Langkah 2: Install & Lock
```bash
npm install
# Ini generate package-lock.json yang SANGAT PENTING
```

### Langkah 3: Git Prepare
```bash
git init
git add .
git status  # Verifikasi file yang akan di-upload
git commit -m "Initial commit: Biometric Desktop App"
```

### Langkah 4: Push ke GitHub
```bash
git branch -M main
git remote add origin https://github.com/yourname/biometric-desktop.git
git push -u origin main
```

---

## 📋 Setup Setelah Clone dari GitHub

Ketika orang lain clone repository, mereka harus:

### 1️⃣ Clone Repository
```bash
git clone https://github.com/yourname/biometric-desktop.git
cd biometric-desktop
```

### 2️⃣ Install Node Dependencies
```bash
npm install
```

### 3️⃣ Setup Python Environment
```bash
# Buat virtual environment
python -m venv venv

# Aktivasi (Windows)
venv\Scripts\activate

# Aktivasi (Linux/Mac)
source venv/bin/activate

# Install Python packages
pip install -r embedding_extractor/requirements.txt
pip install -r raspy-biometric-backend/requirements.txt
pip install -r face_recognition_test/requirements.txt
```

### 4️⃣ Setup Configuration
```bash
# Copy template environment file
copy .env.example .env

# Edit .env dengan konfigurasi lokal:
# - RASPY_API_URL
# - RASPY_API_KEY
# - API_PORT
# - dll
```

### 5️⃣ Jalankan Aplikasi
```bash
npm run dev
```

---

## 🔒 Critical: File Yang Harus Ada Di GitHub

| File | Alasan | Status |
|------|--------|--------|
| `package.json` | Defines npm dependencies | ✅ MUST |
| `package-lock.json` | Lock versions untuk konsistensi | ✅ MUST |
| `tsconfig.json` | TypeScript configuration | ✅ MUST |
| `vite.config.ts` | Build configuration | ✅ MUST |
| `requirements.txt` (all) | Python dependencies | ✅ MUST |
| `.gitignore` | Tell git apa yang di-ignore | ✅ MUST |
| `.env.example` | Template for .env (NO CREDENTIALS!) | ✅ MUST |
| `src/`, `electron/` | Semua source code | ✅ MUST |
| `*.md` docs | Dokumentasi & instructions | ✅ MUST |

---

## 🔥 Verifikasi Sebelum Push

### 1. Cek .gitignore
```bash
# File ini HARUS exist dan benar
cat .gitignore
# Harus ada:
# node_modules/
# dist/
# .env
# *.db
# *.pkl
# venv/
```

### 2. Cek git status
```bash
git status
# JANGAN ADA:
# - node_modules/
# - dist/
# - .env
# - *.db
# - venv/

# HARUS ADA:
# - package.json, package-lock.json
# - tsconfig.json, vite.config.ts
# - src/, electron/
# - *.md files
# - .gitignore
```

### 3. Cek package-lock.json
```bash
# File ini WAJIB ada!
ls package-lock.json
# Jika tidak ada, jalankan:
npm install
```

---

## 🛠️ Troubleshooting: Masalah Umum

### ❌ Error: "node_modules tidak ada setelah clone"
```bash
npm install
# Ini akan download dari package-lock.json
```

### ❌ Error: "Python modules tidak found"
```bash
python -m venv venv
venv\Scripts\activate
pip install -r embedding_extractor/requirements.txt
```

### ❌ Error: ".env not found"
```bash
copy .env.example .env
# Edit dengan konfigurasi lokal
```

### ❌ Error: "Package-lock.json missing"
```bash
npm install
# Ini generate package-lock.json
git add package-lock.json
git commit -m "Add package-lock.json"
```

### ❌ Error: "Port 3001 sudah dipakai"
```bash
# Windows
netstat -ano | findstr :3001
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :3001
kill -9 <PID>
```

---

## 📚 Dokumentasi Yang Harus Ada

Create atau update files ini di GitHub:

### 1. README.md
```markdown
# Biometric Desktop App

Quick start untuk clone dan run aplikasi.

## Installation
1. npm install
2. Setup Python venv
3. Copy .env.example ke .env
4. npm run dev
```

### 2. QUICK_START.md
Step-by-step instructions untuk testing.

### 3. GITHUB_UPLOAD_GUIDE.md
Detail tentang file upload (sudah dibuat).

### 4. .env.example
Template environment variables (sudah dibuat).

### 5. PRE_GITHUB_CHECKLIST.md
Checklist sebelum upload (sudah dibuat).

---

## ✅ Final Verification Checklist

Sebelum `git push`:

- [ ] Run `npm install` (generate package-lock.json)
- [ ] Delete `node_modules/` folder
- [ ] Delete `dist/`, `dist-electron/`, `bundle/` folders
- [ ] Delete database `*.db` files
- [ ] Delete embeddings `*.pkl` files
- [ ] Delete `.env` file (keep `.env.example`)
- [ ] Delete virtual environments (`venv/`)
- [ ] Run `git status` dan verify file list
- [ ] `.gitignore` file ada
- [ ] Dokumentasi .md file semuanya ada
- [ ] `package.json` dan `package-lock.json` ada

---

## 🎯 Simple Command Sequence

Copy-paste ini untuk cleanup & upload:

### Windows PowerShell:
```powershell
# Cleanup
Remove-Item -Recurse -Force node_modules, dist, dist-electron, bundle, venv, __pycache__, .idea -ErrorAction SilentlyContinue
Remove-Item -Path .env, *.db, *.pkl -ErrorAction SilentlyContinue

# Setup npm
npm install

# Git prepare
git init
git add .
git status  # Verify!
git commit -m "Initial commit: Biometric Desktop App"

# Push ke GitHub (sesuaikan URL)
git remote add origin https://github.com/yourname/biometric-desktop.git
git branch -M main
git push -u origin main
```

### Linux/Mac:
```bash
# Cleanup
rm -rf node_modules dist dist-electron bundle venv __pycache__ .idea
rm -f .env *.db *.pkl

# Setup npm
npm install

# Git prepare
git init
git add .
git status  # Verify!
git commit -m "Initial commit: Biometric Desktop App"

# Push ke GitHub
git remote add origin https://github.com/yourname/biometric-desktop.git
git branch -M main
git push -u origin main
```

---

## 🚀 Setelah Upload: Verifikasi

### 1. Test fresh clone di folder lain:
```bash
cd /tmp
git clone https://github.com/yourname/biometric-desktop.git test
cd test
npm install
# Semua harus berjalan tanpa error
```

### 2. Cek file di GitHub:
- Lihat di https://github.com/yourname/biometric-desktop
- Harus ada: package.json, src/, electron/, .gitignore, README.md, .env.example
- JANGAN ada: node_modules/, dist/, .env (tanpa example), *.db, *.pkl

### 3. Update README dengan:
```markdown
## Quick Start

1. git clone ...
2. npm install
3. Setup Python venv dan pip install dari requirements.txt
4. copy .env.example ke .env dan edit
5. npm run dev
```

---

## 💡 Pro Tips

1. **Untuk Windows PowerShell**: 
   - Gunakan `Remove-Item` bukan `rm`
   - Selalu gunakan `-Force` flag

2. **Untuk Linux/Mac**:
   - Gunakan `rm -rf` untuk folder
   - Selalu double-check sebelum delete

3. **For package-lock.json**:
   - JANGAN pernah delete ini
   - Ini ensure semua orang dapat dependency versi yang sama

4. **For .env file**:
   - JANGAN pernah commit .env yang sebenarnya
   - Upload `.env.example` tanpa credentials
   - Setiap developer buat `.env` mereka sendiri

5. **For sensitive data**:
   - Jangan hardcode API keys di source code
   - Gunakan environment variables
   - Gunakan GitHub Secrets untuk CI/CD

---

## 📞 Pertanyaan Yang Sering Diajukan

**Q: Apakah package-lock.json harus di-upload?**
A: ✅ YA! SANGAT PENTING. Ini memastikan semua orang dapat dependency versi yang sama.

**Q: Apakah node_modules harus di-upload?**
A: ❌ TIDAK! Terlalu besar. Setiap orang run `npm install` untuk generate-nya.

**Q: Apakah .env harus di-upload?**
A: ❌ TIDAK! Upload `.env.example` saja (tanpa credentials).

**Q: Bagaimana kalau lupa delete .env sebelum push?**
A: Lihat section "Troubleshooting: Git still tracking deleted files"

**Q: Database file .db harus di-upload?**
A: ❌ TIDAK! Ini generated saat aplikasi jalan pertama kali.

**Q: Python virtual environment harus di-upload?**
A: ❌ TIDAK! Terlalu besar. Setiap orang buat `venv` mereka sendiri.

---

## 📋 Recommended .gitignore (untuk copy-paste)

```
# Build
node_modules/
dist/
dist-electron/
bundle/
build/

# Python
venv/
env/
ENV/
__pycache__/
*.pyc
*.egg-info/

# Environment
.env
.env.local

# Data
*.db
*.pkl
*.sqlite

# IDE
.vscode/
.idea/
.DS_Store
Thumbs.db
```

---

**Created**: May 22, 2026  
**Version**: 1.0  
**Status**: ✅ Ready untuk reference
