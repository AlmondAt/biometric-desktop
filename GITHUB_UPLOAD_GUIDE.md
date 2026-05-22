# 📤 Panduan Upload ke GitHub - Biometric Desktop App

**Last Updated**: May 22, 2026  
**Tujuan**: Memastikan aplikasi dapat berjalan dengan lancar setelah di-clone dari GitHub

---

## 📋 Daftar Isi
1. [File & Folder WAJIB Upload](#file--folder-wajib-upload)
2. [File & Folder JANGAN Upload](#file--folder-jangan-upload)
3. [Setup .gitignore](#setup-gitignore)
4. [Struktur Repository](#struktur-repository)
5. [Instruksi Setup Setelah Clone](#instruksi-setup-setelah-clone)
6. [Troubleshooting](#troubleshooting)

---

## ✅ File & Folder WAJIB Upload

### A. Konfigurasi & Build Files
```
├── package.json              # ⭐ Dependencies npm
├── package-lock.json         # ⭐ Lock file (SANGAT PENTING)
├── tsconfig.json             # TypeScript configuration
├── vite.config.ts            # Vite configuration
├── electron-builder.bundled.json  # Electron builder config
├── electron-builder.json     # Electron builder config
```

### B. Source Code
```
├── src/
│   ├── App.tsx              # React main component
│   ├── EnrollmentView.tsx
│   ├── SetupWizard.tsx
│   ├── main.tsx             # React entry point
│   └── index.css
│
├── electron/
│   ├── main.ts              # Electron main process
│   ├── preload.ts           # Preload script
│   ├── api.ts               # Internal Express API
│   └── database.ts          # SQLite database layer
```

### C. Python Backend
```
├── embedding_extractor/     # ⭐ SELURUH FOLDER
│   ├── main.py
│   ├── training_api.py
│   ├── config.py
│   ├── requirements.txt     # ⭐ SANGAT PENTING
│   ├── data_augmentation.py
│   ├── embedding_store.py
│   ├── facenet_utils.py
│   ├── mtcnn_utils.py
│   └── *.md
│
├── face_recognition_test/   # ⭐ Testing & documentation
│   ├── requirements.txt
│   └── *.py
│
├── raspy-biometric-backend/
│   ├── requirements.txt     # ⭐ SANGAT PENTING
│   ├── config.yaml          # ⭐ Configuration template
│   ├── api_server.py
│   ├── modules/
│   ├── tools/
│   └── *.md
```

### D. Documentation
```
├── README.md                # ⭐ Harus ada
├── QUICK_START.md          # ⭐ Instruksi cepat
├── SYSTEM_DOCUMENTATION.md
├── INTEGRATION_GUIDE.md
├── TUTORIAL_PENGGUNA.md
├── TUTORIAL_TEKNISI.md
├── PROJECT_RECAP_AND_PR.md
├── ADD_USER_WITH_ID_README.md
├── SYSTEM_PROMPT.md
└── *.md (semua dokumentasi)
```

### E. Build & Configuration
```
├── build/
│   └── pyinstaller/
│       └── training_api.spec   # PyInstaller spec file
│
├── scripts/
│   └── build-python-runtime.ps1  # Build script
```

### F. Assets & Resources
```
├── index.html               # HTML entry point
└── add-user-with-id.js      # Utility scripts
```

---

## ❌ File & Folder JANGAN Upload

### A. Generated / Build Output
```
❌ dist/                      # Build output
❌ dist-electron/            # Electron build output
❌ bundle/                    # Python bundled runtime
❌ build/                     # Build artifacts (kecuali config)
❌ node_modules/             # npm dependencies
❌ __pycache__/              # Python cache
❌ *.egg-info/               # Python package info
❌ .egg                      # Python eggs
```

### B. Environment & Credentials
```
❌ .env                       # Environment variables
❌ .env.local                 # Local env
❌ *.pem                      # Private keys
❌ *.key                      # Secret keys
❌ config.yaml (production)   # Production config (upload template saja)
❌ credentials.json           # API credentials
```

### C. Database & Data Files
```
❌ *.db                       # SQLite databases
❌ *.pkl                      # Pickle files (embeddings, models)
❌ embeddings.pkl            # Trained embeddings
❌ *.sqlite                   # SQLite files
❌ logs/                      # Application logs
❌ data/                      # Generated data (jika ada)
```

### D. IDE & System Files
```
❌ .vscode/                   # VS Code settings (personal)
❌ .idea/                     # IntelliJ settings
❌ .DS_Store                  # macOS
❌ Thumbs.db                  # Windows
❌ *.swp / *.swo             # Vim
❌ dist/                      # Distribution files
```

### E. Dependencies & Virtual Environments
```
❌ venv/                      # Python virtual env
❌ ENV/                       # Virtual environment
❌ env/                       # Virtual environment
❌ node_modules/             # Node modules
```

---

## 🔒 Setup .gitignore

**Buat file `.gitignore` di root project:**

```gitignore
# Build output
dist/
dist-electron/
build/
*.egg-info/
*.egg
*.pyc
__pycache__/

# Dependencies
node_modules/
venv/
ENV/
env/

# Environment files
.env
.env.local
.env.*.local
*.pem
*.key
credentials.json

# Database & Data
*.db
*.sqlite
embeddings.pkl
*.pkl
logs/
data/

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store
Thumbs.db

# Python
*.py[cod]
*$py.class
*.so
build/
develop-eggs/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/

# OS
*.log
.DS_Store
Thumbs.db

# Bundle
bundle/python-runtime/

# IDE settings
.vscode/settings.json
.vscode/extensions.json
```

---

## 📁 Struktur Repository yang Direkomendasikan

```
biometric-desktop/
│
├── 📄 README.md                    # Entry point dokumentasi
├── 📄 QUICK_START.md              # Setup cepat
├── 📄 GITHUB_UPLOAD_GUIDE.md       # Dokumen ini
├── 📄 SYSTEM_DOCUMENTATION.md     # Dokumentasi sistem
├── 📄 INTEGRATION_GUIDE.md        # Integrasi guide
│
├── 📄 package.json                # ⭐ Node dependencies
├── 📄 package-lock.json           # ⭐ Lock file
├── 📄 tsconfig.json               # TypeScript config
├── 📄 vite.config.ts              # Vite config
├── 📄 electron-builder.bundled.json
│
├── 📄 index.html
├── 📄 .gitignore                  # ⭐ PENTING: Setup ini
│
├── 📁 src/                        # React components
│   ├── App.tsx
│   ├── main.tsx
│   ├── index.css
│   ├── EnrollmentView.tsx
│   └── SetupWizard.tsx
│
├── 📁 electron/                   # Electron main process
│   ├── main.ts
│   ├── preload.ts
│   ├── api.ts
│   └── database.ts
│
├── 📁 embedding_extractor/        # Python ML backend
│   ├── requirements.txt           # ⭐ Python deps
│   ├── main.py
│   ├── training_api.py
│   ├── config.py
│   ├── data_augmentation.py
│   ├── facenet_utils.py
│   ├── mtcnn_utils.py
│   └── embedding_store.py
│
├── 📁 face_recognition_test/      # Testing module
│   ├── requirements.txt
│   ├── recognition.py
│   ├── video_recognition.py
│   ├── config.py
│   └── README.md
│
├── 📁 raspy-biometric-backend/    # Backend integration
│   ├── requirements.txt           # ⭐ Python deps
│   ├── config.yaml.example        # Template (bukan production)
│   ├── README.md
│   ├── api_server.py
│   ├── modules/
│   └── tools/
│
├── 📁 scripts/                    # Build scripts
│   └── build-python-runtime.ps1
│
├── 📁 build/
│   └── pyinstaller/
│       └── training_api.spec      # PyInstaller spec
│
└── 📁 docs/                       # Opsional: Dokumentasi tambahan
    ├── INSTALLATION.md
    ├── CONFIGURATION.md
    └── TROUBLESHOOTING.md
```

---

## 🚀 Instruksi Setup Setelah Clone dari GitHub

Ketika developer lain mengclone repository, mereka harus menjalankan langkah-langkah ini:

### Step 1: Clone Repository
```bash
git clone https://github.com/yourname/biometric-desktop.git
cd biometric-desktop
```

### Step 2: Install Node Dependencies
```bash
npm install
```
> 📌 `package-lock.json` memastikan semua dependencies terinstall dengan versi yang tepat

### Step 3: Setup Python Backend

#### Option A: Menggunakan Virtual Environment (Recommended)
```bash
# Buat virtual environment
python -m venv venv

# Aktivasi virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install Python dependencies untuk embedding_extractor
cd embedding_extractor
pip install -r requirements.txt
cd ..

# Install Python dependencies untuk raspy-biometric-backend
cd raspy-biometric-backend
pip install -r requirements.txt
cd ..

# Install dependencies untuk face_recognition_test
cd face_recognition_test
pip install -r requirements.txt
cd ..
```

#### Option B: Menggunakan Conda (Alternative)
```bash
conda create -n biometric-desktop python=3.10
conda activate biometric-desktop
pip install -r embedding_extractor/requirements.txt
pip install -r raspy-biometric-backend/requirements.txt
pip install -r face_recognition_test/requirements.txt
```

### Step 4: Setup Environment Files
```bash
# Buat .env file untuk konfigurasi lokal
# Copy template jika ada
cp .env.example .env

# Edit .env dengan konfigurasi lokal:
# RASPY_API_URL=http://localhost:5000
# RASPY_API_KEY=your_key
# API_PORT=3001
```

### Step 5: Setup Python Runtime Bundle (Optional - hanya untuk build)
```bash
# Jika ingin membuild instalasi standalone dengan Python bundled
pwsh -ExecutionPolicy Bypass -File .\scripts\build-python-runtime.ps1
```

### Step 6: Development Mode - Run Application
```bash
# Start development server (semua component: Electron, React, Express, Python)
npm run dev
```

**Expected Output:**
```
✓ Vite dev server ready on http://localhost:5173
✓ Electron window opened
✓ Express API running on http://localhost:3001
✓ Python services ready
```

### Step 7: Build untuk Production
```bash
# Build dengan Python runtime bundled
npm run build:bundled

# Atau build tanpa Python bundled (anggap Python sudah di-system)
npm run build
```

---

## ⚙️ Konfigurasi yang Perlu Disetup Setelah Clone

Setelah menjalankan langkah-langkah di atas, developer perlu mengkonfigurasi:

### 1. Environment Variables (`.env`)
```env
# API Configuration
API_PORT=3001
NODE_ENV=development

# Raspy Integration
RASPY_API_URL=http://localhost:5000
RASPY_API_KEY=your_api_key_here
RASPY_API_TIMEOUT=5000

# Python Services
PYTHON_PORT=5001
EMBEDDING_MODEL=facenet

# Logging
LOG_LEVEL=info
LOG_DIR=./logs

# Database
DB_PATH=./app.db
EMBEDDINGS_PATH=./embeddings.pkl
```

### 2. Python Configuration (`raspy-biometric-backend/config.yaml`)
```yaml
database:
  type: sqlite
  path: ./biometric.db

api:
  host: 0.0.0.0
  port: 5000
  debug: false

face_recognition:
  model: facenet
  threshold: 0.5
  min_faces: 1

logging:
  level: INFO
  file: ./logs/raspy.log
```

### 3. Database Setup
```bash
# Database akan otomatis dibuat saat aplikasi pertama kali berjalan
# Atau manual:
npm run dev
# Aplikasi akan create database.db dan embeddings.pkl
```

---

## 📋 Checklist Sebelum Upload ke GitHub

### Pre-Upload Checklist:
- [ ] Jalankan `npm install` untuk generate `package-lock.json`
- [ ] Hapus `node_modules/` folder
- [ ] Hapus `dist/`, `dist-electron/`, `bundle/` folder
- [ ] Hapus semua `*.db`, `*.pkl` files
- [ ] Hapus `.env` file (upload `.env.example` saja)
- [ ] Hapus `venv/`, `ENV/`, `env/` folders
- [ ] Setup `.gitignore` dengan benar
- [ ] Jalankan `git status` untuk verifikasi
- [ ] Test: `git clone` di folder lain dan jalankan setup

### Commands untuk Cleanup:
```bash
# Windows PowerShell
Remove-Item -Recurse -Force node_modules
Remove-Item -Recurse -Force dist
Remove-Item -Recurse -Force dist-electron
Remove-Item -Recurse -Force bundle
Remove-Item -Recurse -Force venv
Remove-Item -Path *.db
Remove-Item -Path *.pkl
Remove-Item -Path .env

# Linux/Mac
rm -rf node_modules dist dist-electron bundle venv
rm -f *.db *.pkl .env
```

### Verifikasi Sebelum Push:
```bash
git status
# Hanya file WAJIB UPLOAD yang harus muncul di sini

git add .
git commit -m "Initial commit: Biometric Desktop App"
git push origin main
```

---

## 🔄 Continuous Integration / Deployment

### Recommended GitHub Actions Workflow

Buat file `.github/workflows/build.yml`:

```yaml
name: Build & Test

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '18'
    
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install Node dependencies
      run: npm install
    
    - name: Install Python dependencies
      run: |
        pip install -r embedding_extractor/requirements.txt
        pip install -r raspy-biometric-backend/requirements.txt
    
    - name: Build
      run: npm run build
```

---

## 🆘 Troubleshooting

### ❌ Error: "node_modules not found"
**Solution:**
```bash
npm install
```

### ❌ Error: "Python module not found"
**Solution:**
```bash
python -m venv venv
venv\Scripts\activate  # or: source venv/bin/activate
pip install -r embedding_extractor/requirements.txt
pip install -r raspy-biometric-backend/requirements.txt
```

### ❌ Error: "package-lock.json is missing"
**Solution:**
```bash
# Hapus node_modules dan package-lock.json
rm -rf node_modules package-lock.json
npm install  # Ini akan generate package-lock.json baru
```

### ❌ Error: "Port 3001 already in use"
**Solution:**
```bash
# Windows:
netstat -ano | findstr :3001
taskkill /PID <PID> /F

# Linux/Mac:
lsof -i :3001
kill -9 <PID>
```

### ❌ Error: ".env file not found"
**Solution:**
```bash
# Create .env from template
cp .env.example .env
# Edit .env dengan konfigurasi lokal
```

---

## 📝 Template: README untuk GitHub

Buat atau update `README.md`:

```markdown
# 🎭 Biometric Desktop Application

Aplikasi desktop untuk enrollment dan monitoring biometrik (face & fingerprint) 
dengan integrasi ke sistem Raspy.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.10+
- Git

### Installation

\`\`\`bash
# 1. Clone repository
git clone https://github.com/yourname/biometric-desktop.git
cd biometric-desktop

# 2. Install dependencies
npm install

# 3. Setup Python
python -m venv venv
venv\Scripts\activate
pip install -r embedding_extractor/requirements.txt
pip install -r raspy-biometric-backend/requirements.txt

# 4. Configure environment
copy .env.example .env
# Edit .env dengan konfigurasi Anda

# 5. Run development
npm run dev
\`\`\`

### Build

\`\`\`bash
# Build dengan Python bundled
npm run build:bundled

# Atau build standar
npm run build
npm run dist:win
\`\`\`

## 📚 Documentation

- [Quick Start](./QUICK_START.md) - Setup cepat
- [System Documentation](./SYSTEM_DOCUMENTATION.md) - Dokumentasi sistem
- [GitHub Upload Guide](./GITHUB_UPLOAD_GUIDE.md) - File upload guide
- [Integration Guide](./INTEGRATION_GUIDE.md) - Integrasi dengan Raspy

## 📋 Tech Stack

- **Frontend**: React + TypeScript + Vite
- **Desktop**: Electron
- **Backend**: Node.js + Express
- **ML/AI**: Python + FaceNet + MTCNN
- **Database**: SQLite
- **Biometric**: Face Recognition

## 📄 License

MIT License

## 👥 Contributors

- Muhammad Al Farizi
- GitHub Copilot
```

---

## ✅ Final Verification

Sebelum merge ke `main` branch:

```bash
# 1. Test fresh clone
cd /tmp
git clone https://github.com/yourname/biometric-desktop.git test-clone
cd test-clone

# 2. Follow setup instructions
npm install
python -m venv venv
venv\Scripts\activate
pip install -r embedding_extractor/requirements.txt

# 3. Verify dapat berjalan
npm run dev
# Harus berjalan tanpa error

# 4. Jika sukses, repository siap untuk dipublikasikan
```

---

## 📞 Support & Questions

Jika ada pertanyaan tentang file upload atau setup, silakan:
1. Buka GitHub Issue
2. Check documentation di folder `docs/`
3. Lihat Troubleshooting section di atas

---

**Last Updated**: May 22, 2026  
**Status**: ✅ Ready for GitHub Upload
