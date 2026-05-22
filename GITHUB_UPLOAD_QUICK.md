# ⚡ QUICK REFERENCE - GITHUB UPLOAD CHECKLIST

**Print atau screenshot ini untuk reference cepat saat execute!**

---

## 🎯 TAHAP & CHECKPOINT

```
TAHAP 1: CLEANUP
├─ [ ] cd "d:\New folder"
├─ [ ] Delete: node_modules, dist, dist-electron, bundle
├─ [ ] Delete: __pycache__, .idea
├─ [ ] Delete: *.db, *.pkl, .env
├─ [ ] Delete: venv, ENV, env
└─ [ ] VERIFY: Folder size < 100MB

TAHAP 2: NPM
├─ [ ] npm install
├─ [ ] VERIFY: package-lock.json created
└─ [ ] Delete node_modules lagi

TAHAP 3: GIT
├─ [ ] git init (jika belum)
├─ [ ] git status (cek status)
├─ [ ] git add .
├─ [ ] AUDIT: Tidak ada node_modules, dist, .env
└─ [ ] git commit -m "Initial commit..."

TAHAP 4: GITHUB
├─ [ ] Create empty repository di GitHub
├─ [ ] Copy HTTPS URL
├─ [ ] git remote add origin <URL>
├─ [ ] git branch -M main
└─ [ ] git push -u origin main

TAHAP 5: VERIFY
├─ [ ] Check GitHub - files muncul
├─ [ ] Test fresh clone
├─ [ ] npm install di clone
└─ [ ] ALL GOOD ✅
```

---

## 🔄 COMMAND REFERENCE (Copy-Paste)

### Cleanup All

```powershell
cd "d:\New folder"
Remove-Item -Recurse -Force node_modules, dist, dist-electron, bundle, venv, __pycache__, .idea -ErrorAction SilentlyContinue
Remove-Item -Path *.db, *.pkl, .env -ErrorAction SilentlyContinue
Write-Host "✅ Cleanup done"
```

### NPM Setup

```powershell
npm install
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
ls package-lock.json
```

### Git & Push

```powershell
git init
git config user.name "Your Name"
git config user.email "your@email.com"
git add .
git status
git commit -m "Initial commit: Biometric Desktop App"
git remote add origin https://github.com/YOUR_USERNAME/biometric-desktop.git
git branch -M main
git push -u origin main
```

### Test Clone

```powershell
cd $env:TEMP
git clone https://github.com/YOUR_USERNAME/biometric-desktop.git
cd biometric-desktop
npm install
```

---

## ✅ CRITICAL POINTS

| Item | Status | Action |
|------|--------|--------|
| `package.json` | ✅ Must exist | Do NOT delete |
| `package-lock.json` | ✅ Must exist | Auto-created by npm install |
| `node_modules/` | ❌ Must NOT exist | Delete after npm install |
| `.env` | ❌ Must NOT exist | Delete before git add |
| `.env.example` | ✅ Must exist | Template for users |
| `src/`, `electron/` | ✅ Must exist | Source code folders |
| `.gitignore` | ✅ Must exist | Already created |
| `.git/` | ✅ Must exist | Created by git init |
| Folder size | < 100MB | Check with du -hs . |

---

## ⚠️ ERROR SOLUTIONS

| Error | Solution |
|-------|----------|
| "node_modules not found after clone" | `npm install` |
| ".env file in repo" | `git rm --cached .env && git commit` |
| "Authentication failed" | Use Personal Access Token (not password) |
| "Repository not found" | Check HTTPS URL, check GitHub repo exists |
| "fatal: not a git repository" | Run `git init` first |
| "branch main doesn't exist" | Run `git branch -M main` |

---

## 📱 Commands by Step

```
STEP 1: Navigate
  cd "d:\New folder"

STEP 2: Cleanup  
  Remove-Item -Recurse -Force node_modules, dist, dist-electron, bundle, venv, __pycache__, .idea -EA SC
  Remove-Item -Path *.db, *.pkl, .env -EA SC

STEP 3: NPM
  npm install
  Remove-Item -Recurse -Force node_modules -EA SC

STEP 4: Git Init
  git init
  git config user.name "Your Name"
  git config user.email "your.email@example.com"

STEP 5: Add & Commit
  git add .
  git status  [VERIFY - no node_modules, dist, .env]
  git commit -m "Initial commit: Biometric Desktop App"

STEP 6: GitHub Remote
  git remote add origin https://github.com/YOUR_USERNAME/biometric-desktop.git
  git branch -M main

STEP 7: Push
  git push -u origin main

STEP 8: Test
  cd $env:TEMP
  git clone https://github.com/YOUR_USERNAME/biometric-desktop.git
  cd biometric-desktop
  npm install
  [VERIFY - everything works]
```

---

## 🎬 START HERE

**Jangan lupa:**
1. **Create empty repository di GitHub dulu** (https://github.com/new)
2. **Copy HTTPS URL** dari repository
3. **Replace YOUR_USERNAME** di semua command
4. **Run commands satu-satu** (jangan sekaligus)
5. **Verify setiap step** sebelum lanjut

---

**Time Estimate:** 15-20 menit (including npm install)

**Ready? Go to GITHUB_UPLOAD_EXECUTE.md for full details!** ✨
