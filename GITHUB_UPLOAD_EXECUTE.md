# 🚀 STEP-BY-STEP GITHUB UPLOAD GUIDE

**Status**: Ready to Execute  
**Date**: May 22, 2026  
**Level**: Copy-Paste Commands

---

## ✅ Pre-Upload Checklist (Baca Dulu!)

Sebelum mulai, pastikan:
- [ ] Git sudah terinstall (`git --version`)
- [ ] GitHub account sudah siap
- [ ] Repository di GitHub sudah dibuat kosong dengan nama `biometric-desktop`
- [ ] Tidak ada yang perlu disimpan di folder (data sementara bersihkan)

---

## 📋 TAHAP 1: CLEANUP LOCAL (Bersihkan Folder)

### 1.1 Buka PowerShell sebagai Admin

Tekan: **Windows Key + R** → ketik `powershell` → Ctrl+Shift+Enter

### 1.2 Navigate ke Project Folder

```powershell
cd "d:\New folder"
```

Verifikasi lokasi:
```powershell
pwd
# Should show: d:\New folder (atau D:\New folder)

ls
# Should show: package.json, src/, electron/, etc
```

### 1.3 Delete Build Artifacts & Cache

**⚠️ HATI-HATI! Delete file yang tidak perlu:**

```powershell
# 1. Delete node_modules (terbesar!)
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
Write-Host "✅ node_modules deleted"

# 2. Delete build outputs
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force dist-electron -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force bundle -ErrorAction SilentlyContinue
Write-Host "✅ dist folders deleted"

# 3. Delete Python cache
Remove-Item -Recurse -Force __pycache__ -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .idea -ErrorAction SilentlyContinue
Write-Host "✅ Cache deleted"

# 4. Delete databases & embeddings
Remove-Item -Path *.db -ErrorAction SilentlyContinue
Remove-Item -Path *.pkl -ErrorAction SilentlyContinue
Remove-Item -Path .env -ErrorAction SilentlyContinue
Write-Host "✅ Databases & credentials deleted"

# 5. Delete virtual environments
Remove-Item -Recurse -Force venv -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force ENV -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force env -ErrorAction SilentlyContinue
Write-Host "✅ Python venv deleted"

Write-Host "`n✅ CLEANUP COMPLETE!"
```

### 1.4 Verify Cleanup

```powershell
# Check remaining size
Get-ChildItem -Recurse | Measure-Object -Property Length -Sum | ForEach-Object {
  [math]::Round($_.Sum / 1MB, 2)
}
# Should be < 100 MB

# Should NOT see these folders:
ls | findstr /i "node_modules dist venv"
# If nothing shows = GOOD ✅
```

---

## 📦 TAHAP 2: SETUP NPM DEPENDENCIES

### 2.1 Install Node Modules

```powershell
npm install
```

**Expected output:**
```
added XXX packages in X.XXs

up to date, audited XXX packages
```

⏱️ **Tunggu sampai selesai** (5-10 menit tergantung internet)

### 2.2 Verify package-lock.json Created

```powershell
ls package-lock.json

# Should show file exists:
# Mode                 LastWriteTime         Length Name
# ----                 -------               ------ ----
# -a---           5/22/2026 10:30:00 AM     150000 package-lock.json
```

✅ **PENTING**: File `package-lock.json` sekarang harus exist!

### 2.3 Delete node_modules Lagi

```powershell
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
Write-Host "✅ node_modules deleted (keep package-lock.json!)"

# Verify package-lock.json still exists
ls package-lock.json
# Should show: ✅ exists
```

---

## 🔧 TAHAP 3: SETUP .gitignore

### 3.1 Check .gitignore Exists

```powershell
ls .gitignore

# If exists → skip to 3.2
# If NOT exist → error, sudah dibuat otomatis jadi harus ada
```

### 3.2 Verify Content

```powershell
# Show first 20 lines
Get-Content .gitignore -Head 20

# Should show:
# node_modules/
# dist/
# dist-electron/
# .env
# *.db
# *.pkl
# venv/
```

---

## 📝 TAHAP 4: SETUP .env.example

### 4.1 Check .env.example Exists

```powershell
ls .env.example

# Should exist (already created)
```

### 4.2 Verify NO Real .env File

```powershell
ls .env -ErrorAction SilentlyContinue

# Should show: File NOT found ✅
# If file exists → delete it:
# Remove-Item -Path .env -ErrorAction SilentlyContinue
```

---

## 🔐 TAHAP 5: GIT INITIALIZATION

### 5.1 Check Git Status

```powershell
git --version
# Should show: git version 2.xx.x

# Navigate ke project root
cd "d:\New folder"
```

### 5.2 Initialize Git Repository

```powershell
# Check jika sudah git repo
git status
```

**Jika sudah ada repo (sudah .git folder):**
```
On branch main
...
```
→ Lanjut ke 5.3

**Jika belum ada repo (error: not a git repo):**
```powershell
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"
Write-Host "✅ Git initialized"
```

### 5.3 Check Git Status Again

```powershell
git status

# Expected output:
# On branch main (atau master)
# Changes not staged for commit:
#   (use "git add <file>..." to update what will be committed)
#
#   modified: <some files>
#
# Untracked files:
#   (use "git add <file>..." to include in what will be committed)
#
#   <many files>
```

---

## ✅ TAHAP 6: VERIFY FILES TO UPLOAD

### 6.1 Check What Will Be Staged

```powershell
# See which files git will upload
git status --porcelain | head -20

# Expected: Should show many files
# ✅ SHOULD include: package.json, src/, electron/, etc
# ❌ Should NOT include: node_modules/, dist/, .env, *.db, *.pkl
```

### 6.2 Quick Audit

```powershell
# Verify NO sensitive files in staging
git status | findstr /i "node_modules dist .env .db .pkl venv"

# If output empty → GOOD ✅
# If show files → PROBLEM ❌ (run cleanup again)
```

---

## 📤 TAHAP 7: GIT ADD & COMMIT

### 7.1 Add All Files to Staging

```powershell
git add .

# Verify what will be committed
git status

# Should show:
# Changes to be committed:
#   new file: .env.example
#   new file: .gitignore
#   new file: package.json
#   new file: package-lock.json
#   new file: src/...
#   new file: electron/...
#   ... (40+ files)
```

### 7.2 Verify NO BAD Files

```powershell
git status | findstr "node_modules dist .env .db .pkl"

# If NOTHING shows → ✅ GOOD
# If show files → run this to remove:
# git reset HEAD node_modules
# git reset HEAD dist
# etc
```

### 7.3 Commit

```powershell
git commit -m "Initial commit: Biometric Desktop App - Complete source code with Electron, React, Express, Python ML backend"

# Expected output:
# [main (root-commit) a1b2c3d] Initial commit: ...
#  XX files changed, XXXXX insertions(+)
#  create mode 100644 .env.example
#  create mode 100644 .gitignore
#  ... (40+ files)
```

---

## 🌐 TAHAP 8: CONNECT TO GITHUB

### 8.1 Create GitHub Repository

1. **Buka**: https://github.com/new
2. **Repository name**: `biometric-desktop`
3. **Description**: `Desktop biometric enrollment and monitoring app with Electron, React, Express, and Python ML`
4. **Public** atau **Private** (pilih sesuai preferensi)
5. **Jangan** check "Initialize this repository with" (biar kosong)
6. **Click**: Create repository

**Result**: Anda akan dapat perintah seperti:
```
…or push an existing repository from the command line

git remote add origin https://github.com/YOUR_USERNAME/biometric-desktop.git
git branch -M main
git push -u origin main
```

### 8.2 Copy GitHub URL

Di halaman repository yang baru dibuat, ada button **Code** (hijau).
Klik → copy HTTPS link:
```
https://github.com/YOUR_USERNAME/biometric-desktop.git
```

(Ganti `YOUR_USERNAME` dengan username GitHub Anda)

---

## 🚀 TAHAP 9: PUSH KE GITHUB

### 9.1 Add Remote Repository

```powershell
# Ganti dengan URL dari step 8.2
git remote add origin https://github.com/YOUR_USERNAME/biometric-desktop.git

# Verify
git remote -v
# Should show:
# origin  https://github.com/YOUR_USERNAME/biometric-desktop.git (fetch)
# origin  https://github.com/YOUR_USERNAME/biometric-desktop.git (push)
```

### 9.2 Ensure Main Branch

```powershell
git branch -M main

# Verify
git branch
# Should show: * main
```

### 9.3 Push to GitHub

```powershell
git push -u origin main
```

**First time, might ask for authentication:**
- GitHub akan open browser untuk login
- Atau accept personal access token jika sudah setup

⏱️ **Tunggu sampai selesai** (1-5 menit tergantung file size)

**Expected output:**
```
Enumerating objects: XXX, done.
Counting objects: 100% (XXX/XXX), done.
Delta compression using up to 8 threads
Compressing objects: 100% (XXX/XXX), done.
Writing objects: 100% (XXX/XXX), X.XX MiB | X.XX MiB/s, done.
...
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

✅ **SUCCESS!** Repository uploaded to GitHub!

---

## ✔️ TAHAP 10: VERIFY DI GITHUB

### 10.1 Buka GitHub Repository

Buka: https://github.com/YOUR_USERNAME/biometric-desktop

### 10.2 Verify Files Ada

Check apakah files sudah muncul:

**✅ HARUS ADA:**
- [ ] `package.json`
- [ ] `package-lock.json`
- [ ] `tsconfig.json`
- [ ] `vite.config.ts`
- [ ] `.gitignore`
- [ ] `.env.example`
- [ ] `src/` folder
- [ ] `electron/` folder
- [ ] `embedding_extractor/` folder
- [ ] `README.md` dan dokumentasi lain
- [ ] Folders: `raspy-biometric-backend/`, `face_recognition_test/`, `scripts/`, `build/`

**❌ JANGAN ADA:**
- [ ] `node_modules/`
- [ ] `dist/`, `dist-electron/`
- [ ] `.env` (hanya `.env.example`)
- [ ] `*.db`, `*.pkl`
- [ ] `venv/`, `ENV/`, `env/`
- [ ] `.idea/` atau `.vscode/` personal settings

### 10.3 Check Commit Message

Klik **Commits** → Should show commit Anda dengan message:
```
Initial commit: Biometric Desktop App - Complete source code...
```

---

## 🧪 TAHAP 11: TEST FRESH CLONE

### 11.1 Create Test Folder

```powershell
# Go to temp location
cd $env:TEMP

# atau di D:\ buat folder test
cd D:\
mkdir test-clone
cd test-clone
```

### 11.2 Clone Repository

```powershell
git clone https://github.com/YOUR_USERNAME/biometric-desktop.git

# Tunggu sampai selesai
# Should show:
# Cloning into 'biometric-desktop'...
# remote: Counting objects: XXX, done.
# remote: Compressing objects: 100% (XXX/XXX), done.
# Receiving objects: 100% (XXX/XXX), X.XX MiB | X.XX MiB/s, done.
# Unpacking objects: 100% (XXX/XXX), done.
```

### 11.3 Navigate to Cloned Repo

```powershell
cd biometric-desktop

# Verify files exist
ls package.json
ls src/
ls electron/
ls embedding_extractor/

# All should exist ✅
```

### 11.4 Test npm install

```powershell
npm install

# Should complete successfully
# Will download dari package-lock.json
```

### 11.5 Verify Setup

```powershell
# Check if files correct
Get-ChildItem | Measure-Object

# Should show ~50 items (folders + files)
```

✅ **SUCCESS!** Repository dapat di-clone dan setup berhasil!

---

## 📋 TROUBLESHOOTING

### Problem: "node_modules" masih ke-upload

**Solution:**
```powershell
git rm -r --cached node_modules
git commit -m "Remove node_modules from tracking"
git push
```

### Problem: ".env file" ke-upload

**Solution:**
```powershell
git rm --cached .env
git commit -m "Remove .env from tracking"
git push
```

### Problem: Authentication failed

**Solution:**
- GitHub meminta personal access token (bukan password)
- Generate di: https://github.com/settings/tokens
- Gunakan token untuk authentication

### Problem: Repository sudah exist di GitHub

**Solution:**
```powershell
# Delete local git
Remove-Item -Recurse -Force .git

# Start fresh
git init
git add .
git commit -m "Initial commit..."
git remote add origin https://github.com/YOUR_USERNAME/biometric-desktop.git
git branch -M main
git push -u origin main --force
```

---

## 🎯 FINAL CHECKLIST

Setelah push ke GitHub:

- [ ] Repository exist di https://github.com/YOUR_USERNAME/biometric-desktop
- [ ] `package.json` dan `package-lock.json` ada
- [ ] `src/`, `electron/`, folder Python ada
- [ ] `.gitignore` ada dan bekerja
- [ ] `.env.example` ada (BUKAN `.env`)
- [ ] Tidak ada `node_modules/`, `dist/`, `*.db`, `*.pkl`
- [ ] Fresh clone test berhasil
- [ ] `npm install` berhasil di fresh clone

✅ **Semuanya OK? Repository siap untuk dikerjakan developer lain!**

---

## 📚 Next Steps (After Upload)

1. **Update README.md** dengan setup instructions (lihat GITHUB_UPLOAD_RINGKAS.md)
2. **Setup GitHub Actions** untuk CI/CD (optional)
3. **Create Releases** untuk binaries (electron-builder output)
4. **Invite collaborators** jika perlu team

---

**Siap? Jalankan step 1 dulu!** 🚀

