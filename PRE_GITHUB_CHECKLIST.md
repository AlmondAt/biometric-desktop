# ✅ Pre-GitHub Upload Checklist

**Use this checklist before pushing to GitHub**

## 🔍 Files Check

### Must Upload ✅
- [ ] `package.json` - npm configuration
- [ ] `package-lock.json` - npm lock file (run `npm install` if missing)
- [ ] `tsconfig.json` - TypeScript config
- [ ] `vite.config.ts` - Vite config
- [ ] `electron-builder.bundled.json` - Electron builder config
- [ ] `index.html` - HTML entry point
- [ ] `.gitignore` - Git ignore rules
- [ ] All `.tsx`, `.ts` files in `src/` and `electron/`
- [ ] All Python files in `embedding_extractor/`, `face_recognition_test/`, `raspy-biometric-backend/`
- [ ] All `requirements.txt` files
- [ ] All `*.md` documentation files
- [ ] `scripts/` folder with build scripts
- [ ] `build/pyinstaller/` with `.spec` files

### Must NOT Upload ❌
- [ ] `node_modules/` folder (delete it)
- [ ] `dist/` folder (delete it)
- [ ] `dist-electron/` folder (delete it)
- [ ] `bundle/` folder (delete it)
- [ ] `venv/`, `ENV/`, `env/` folders (delete them)
- [ ] `.env` file (upload `.env.example` instead)
- [ ] `*.db` files (SQLite databases)
- [ ] `*.pkl` files (embeddings, models)
- [ ] `.vscode/` personal settings (optional to keep)
- [ ] `.idea/` IntelliJ settings (delete it)
- [ ] `__pycache__/` Python cache (delete it)
- [ ] `*.pyc` files (Python compiled)
- [ ] `.DS_Store`, `Thumbs.db` (OS files)

---

## 🧹 Cleanup Commands

### Windows PowerShell (Run as Admin)
```powershell
# Navigate to project root
cd "d:\New folder"

# Remove build artifacts
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force dist-electron -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force bundle -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force __pycache__ -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .idea -ErrorAction SilentlyContinue

# Remove credentials
Remove-Item -Path .env -ErrorAction SilentlyContinue
Remove-Item -Path *.db -ErrorAction SilentlyContinue
Remove-Item -Path *.pkl -ErrorAction SilentlyContinue

# Remove virtual environments
Remove-Item -Recurse -Force venv -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force ENV -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force env -ErrorAction SilentlyContinue

Write-Host "✅ Cleanup selesai!"
```

### Linux/macOS (Bash)
```bash
#!/bin/bash
cd "$(dirname "$0")"

# Remove build artifacts
rm -rf node_modules dist dist-electron bundle __pycache__ .idea

# Remove credentials
rm -f .env *.db *.pkl

# Remove virtual environments
rm -rf venv ENV env .venv

echo "✅ Cleanup selesai!"
```

---

## 📦 Pre-Upload Setup

### 1. Install npm dependencies (if package-lock.json missing)
```bash
npm install
```
This will generate `package-lock.json` - **JANGAN HAPUS FILE INI!**

### 2. Verify .gitignore exists and is correct
- [ ] File `.gitignore` ada di root folder
- [ ] Berisi rules untuk node_modules, dist, .env, *.db, *.pkl, venv

### 3. Create .env.example (template only - no real credentials!)
```bash
# .env.example - TEMPLATE ONLY, NO REAL CREDENTIALS
API_PORT=3001
NODE_ENV=development
RASPY_API_URL=http://localhost:5000
RASPY_API_KEY=replace_with_your_key
PYTHON_PORT=5001
```

### 4. Verify folder structure
```
✅ src/               - React components
✅ electron/          - Electron main process
✅ embedding_extractor/  - Python ML backend
✅ face_recognition_test/ - Test module
✅ raspy-biometric-backend/ - Backend integration
✅ scripts/           - Build scripts
✅ build/             - Build configs
✅ docs/              - Documentation (optional)
```

---

## 🔐 Security Checks

### Before Upload:
- [ ] No hardcoded API keys in source code
- [ ] No hardcoded passwords in configs
- [ ] No `.env` file (only `.env.example`)
- [ ] No database files (`.db`, `.sqlite`)
- [ ] No private keys (`*.pem`, `*.key`)
- [ ] No credentials in config files
- [ ] No sensitive data in comments
- [ ] Check git status untuk file yang sensitif

### Check Command:
```bash
git status
# Should NOT show any .env, *.db, *.pkl, node_modules, etc.
```

---

## 📝 Git Commands Sequence

### Step 1: Cleanup
```bash
# See what files will be deleted
git clean -fdn

# If OK, delete them
git clean -fd
```

### Step 2: Stage files
```bash
git add .
```

### Step 3: Verify staging
```bash
git status
# Review hasilnya sebelum commit
```

### Step 4: Commit
```bash
git commit -m "Initial commit: Biometric Desktop App with all source files"
```

### Step 5: Push ke GitHub
```bash
git branch -M main
git remote add origin https://github.com/yourname/biometric-desktop.git
git push -u origin main
```

---

## 🧪 Post-Upload Verification

After pushing to GitHub:

### 1. Test Fresh Clone
```bash
# Clone ke folder baru
cd /tmp  # atau C:\temp untuk Windows
git clone https://github.com/yourname/biometric-desktop.git test-clone
cd test-clone
```

### 2. Verify files exist
```bash
# Should exist:
ls package.json package-lock.json tsconfig.json vite.config.ts
ls src/App.tsx electron/main.ts embedding_extractor/requirements.txt
ls -la | grep "^-" | grep -v node_modules | grep -v dist | wc -l
# Should show all your source files
```

### 3. Verify sensitive files NOT present
```bash
# Should NOT exist:
ls .env 2>/dev/null || echo "✅ .env tidak ada"
ls *.db 2>/dev/null || echo "✅ Database files tidak ada"
ls *.pkl 2>/dev/null || echo "✅ Pickle files tidak ada"
ls -d node_modules 2>/dev/null || echo "✅ node_modules tidak ada"
```

### 4. Setup dan run
```bash
npm install
# ... setup Python ...
npm run dev
# Should work without errors
```

---

## 🚀 Final Checklist

### Documentation
- [ ] `README.md` updated dengan instructions
- [ ] `QUICK_START.md` updated
- [ ] `GITHUB_UPLOAD_GUIDE.md` created
- [ ] All `*.md` files are in repository
- [ ] Create `.github/workflows/` if CI/CD needed

### Repository Settings (pada GitHub)
- [ ] Repository name sesuai (`biometric-desktop`)
- [ ] Description updated
- [ ] Readme ditampilkan
- [ ] Branch protection rules (jika perlu)
- [ ] GitHub Actions enabled (jika perlu CI/CD)

### Code Quality
- [ ] No TODO/FIXME comments dengan credentials
- [ ] No console.log dengan sensitive data
- [ ] TypeScript lint clean
- [ ] Python imports OK
- [ ] No unused imports

### Ready to Share
- [ ] Repository dapat di-clone
- [ ] Setup instructions jelas
- [ ] No missing dependencies
- [ ] Can run `npm run dev` successfully
- [ ] Python backend can start

---

## 📋 Troubleshooting Checklist

### Problem: "node_modules missing after clone"
```bash
npm install
# Regenerates node_modules dari package-lock.json
```

### Problem: "Python dependencies missing"
```bash
python -m venv venv
venv\Scripts\activate
pip install -r embedding_extractor/requirements.txt
pip install -r raspy-biometric-backend/requirements.txt
```

### Problem: ".env file tidak ada"
```bash
cp .env.example .env
# Edit dengan konfigurasi lokal
```

### Problem: "Port 3001 already in use"
```bash
# Kill existing process
netstat -ano | findstr :3001
taskkill /PID <PID> /F
```

### Problem: "Git still tracking deleted files"
```bash
git rm --cached node_modules -r
git rm --cached .env
git commit -m "Remove tracking of ignored files"
```

---

## ✨ Optional: GitHub README Template

Tambahkan ke `README.md` untuk GitHub:

```markdown
# 🎭 Biometric Desktop Application

Aplikasi desktop untuk enrollment dan recognition biometrik dengan Electron + React + Python.

## 🚀 Quick Start

1. Clone repository
   \`\`\`bash
   git clone https://github.com/yourname/biometric-desktop.git
   cd biometric-desktop
   \`\`\`

2. Follow setup instructions di [QUICK_START.md](./QUICK_START.md)

3. Run development
   \`\`\`bash
   npm install
   npm run dev
   \`\`\`

## 📚 Documentation

- [Quick Start](./QUICK_START.md)
- [System Documentation](./SYSTEM_DOCUMENTATION.md)
- [GitHub Upload Guide](./GITHUB_UPLOAD_GUIDE.md)
- [Integration Guide](./INTEGRATION_GUIDE.md)

## 🔧 Tech Stack

- Electron, React, TypeScript, Vite
- Node.js + Express
- Python + FaceNet
- SQLite

## 📄 License

MIT

## 👤 Author

Muhammad Al Farizi
```

---

**Last Updated**: May 22, 2026  
**Status**: ✅ Ready to use before uploading to GitHub
