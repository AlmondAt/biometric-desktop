# 📋 Biometric Desktop App - System Documentation

**Project**: Biometric Enrollment & Recognition System  
**Stack**: Electron + React (Frontend) + Node.js/Express (Backend) + Python (ML/AI)  
**Last Updated**: May 2026

---

## 📐 System Architecture

### Overview Diagram
```
┌─────────────────────────────────────────────────────────┐
│                  DESKTOP APPLICATION                    │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Electron Main Process (IPC Bridge)              │  │
│  │  - Window Management                             │  │
│  │  - Inter-Process Communication                   │  │
│  │  - Resource Management                           │  │
│  └──────────────────────────────────────────────────┘  │
│                         │                                │
│        ┌────────────────┼────────────────┐              │
│        ▼                ▼                ▼              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐         │
│  │  React   │    │ Express  │    │  Python  │         │
│  │Frontend  │◄──►│  API :3001│◄─►│ Services │         │
│  │ Vite Dev │    │          │    │          │         │
│  └──────────┘    └──────────┘    └──────────┘         │
│                         │                                │
│  ┌────────────────────────────────────────────────────┐ │
│  │       SQLite Database                              │ │
│  │  - User profiles                                   │ │
│  │  - Biometric embeddings                            │ │
│  │  - Recognition logs                                │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Layer Breakdown

#### 1. **Frontend Layer** (React + TypeScript)
- **Framework**: Vite + React
- **Components**: 
  - `App.tsx` - Main application container
  - `EnrollmentView.tsx` - User enrollment interface
  - `SetupWizard.tsx` - System configuration
- **Responsibilities**:
  - User interface for enrollment & recognition
  - Webcam integration
  - Photo capture & preview
  - HTTP requests to Express backend

#### 2. **Electron Layer** (IPC & Main Process)
- **Files**:
  - `electron/main.ts` - Window creation & app lifecycle
  - `electron/preload.ts` - Secure IPC bridge
  - `electron/api.ts` - Express server instantiation
- **Responsibilities**:
  - Manages Electron window
  - Starts Express API server
  - Handles system paths & resources
  - Resource bundling

#### 3. **Backend API Layer** (Express.js on :3001)
- **File**: `electron/api.ts`
- **Endpoints**:
  - POST `/api/enroll` - Start enrollment
  - POST `/api/train` - Process training
  - GET `/api/embeddings` - Retrieve embeddings
  - POST `/api/recognize` - Perform face recognition
- **Responsibilities**:
  - HTTP API for frontend
  - Python subprocess management
  - File I/O operations
  - Error handling & logging

#### 4. **Python Services Layer**
Core ML/AI processing:

**a) Embedding Extractor** (`embedding_extractor/`)
- **Models**: FaceNet + MTCNN
- **Input**: Webcam photos (`.jpg`)
- **Process**:
  1. MTCNN face detection
  2. Face alignment & crop (160×160)
  3. FaceNet embedding extraction
  4. Data augmentation (rotate, flip, etc)
  5. Save to `embeddings.pkl`
- **Output**: Pickled embeddings dictionary

**b) Face Recognition** (`face_recognition_test/`)
- **Process**:
  1. Load embeddings from `embeddings.pkl`
  2. Capture webcam frame
  3. MTCNN face detection
  4. Extract FaceNet embedding
  5. Calculate cosine similarity with stored embeddings
  6. Return matches with confidence scores
- **Threshold**: 0.6+ similarity = identified

#### 5. **Database Layer** (SQLite)
- **Location**: `embeddings.pkl` (pickle format)
- **Fallback**: SQLite for future user metadata
- **Stores**:
  - User ID → Embeddings mapping
  - Training history
  - Recognition events

---

## 🔌 Wiring & Data Flow

### Enrollment Flow
```
[UI: Enrollment Form]
    │
    ├─ User enters ID: "john_doe"
    ├─ Clicks webcam area → camera stream captured
    ├─ Clicks "Ambil Foto" 10+ times
    │  (Photos saved to temp memory)
    │
    ▼
[Frontend → Express API]
    │
    POST /api/enroll
    {
      userId: "john_doe",
      photos: [<base64 images>]
    }
    │
    ▼
[Express Backend]
    │
    ├─ Save photos to `photos/john_doe/`
    ├─ Spawn Python subprocess: training_api.py
    │
    ▼
[Python: Embedding Extraction]
    │
    ├─ MTCNN detects faces in photos
    ├─ Extract FaceNet embeddings (512-dim vectors)
    ├─ Data augmentation: rotate, flip, blur
    ├─ Create 500+ embeddings from 10 photos
    └─ Save to `embeddings.pkl`
    │
    ▼
[Express API Response]
    │
    Return: { status: "success", embeddings_count: 500 }
    │
    ▼
[Frontend: Display "✅ Training berhasil!"]
```

### Recognition Flow
```
[UI: Recognition View]
    │
    ├─ Webcam stream running
    ├─ User presses SPACE
    │
    ▼
[Frontend → Express API]
    │
    POST /api/recognize
    {
      frame: <base64 image>
    }
    │
    ▼
[Express Backend]
    │
    ├─ Load embeddings.pkl
    ├─ Spawn Python subprocess: recognition process
    │
    ▼
[Python: Face Recognition]
    │
    ├─ MTCNN detects face in frame
    ├─ Extract FaceNet embedding (512-dim)
    ├─ Calculate cosine similarity with all stored embeddings
    ├─ Find best match
    ├─ Compare with threshold (0.6)
    │
    ├─ If similarity > 0.6:
    │  └─ Return: { identified: true, userId: "john_doe", confidence: 0.82 }
    │
    └─ If similarity < 0.6:
       └─ Return: { identified: false }
    │
    ▼
[Frontend: Display Box]
    │
    GREEN BOX: ✓ IDENTIFIED: john_doe
    RED BOX:   ✗ NOT IDENTIFIED
```

### Component Communication Map
```
┌─────────────────────┐
│   React Frontend    │
│  (Vite Dev Server)  │
└──────────┬──────────┘
           │ HTTP
           ▼
┌─────────────────────┐
│   Express API       │
│    :3001            │
└────────┬────────────┘
         │ Subprocess
         │ (Python calls)
         ▼
┌─────────────────────────────────┐
│  Python ML Services             │
│  - training_api.py              │
│  - face_recognition.py          │
│  (Uses: PyTorch, OpenCV, MTCNN) │
└─────────────────────────────────┘
         │
         ▼
    ┌─────────────┐
    │ embeddings  │
    │ .pkl        │
    └─────────────┘
```

---

## 📁 Folder Structure

```
d:\New folder\
│
├── 📄 Core Configuration Files
│   ├── package.json              ← npm scripts & dependencies
│   ├── tsconfig.json             ← TypeScript config
│   ├── vite.config.ts            ← Vite bundler config
│   ├── electron-builder.bundled.json  ← App packaging config
│   └── index.html                ← Entry HTML file
│
├── 📂 src/                        ← React Frontend
│   ├── main.tsx                  ← React entry point
│   ├── App.tsx                   ← Main app component
│   ├── EnrollmentView.tsx        ← Enrollment UI
│   ├── SetupWizard.tsx           ← Setup wizard UI
│   └── index.css                 ← Global styles
│
├── 📂 electron/                   ← Electron Main Process
│   ├── main.ts                   ← App entry (window creation)
│   ├── preload.ts                ← Secure IPC bridge
│   ├── api.ts                    ← Express server setup
│   └── database.ts               ← DB operations
│
├── 📂 embedding_extractor/        ← Face Embedding ML
│   ├── main.py                   ← Entry point
│   ├── training_api.py           ← Training subprocess
│   ├── facenet_utils.py          ← FaceNet model
│   ├── mtcnn_utils.py            ← MTCNN detection
│   ├── config.py                 ← ML configuration
│   ├── requirements.txt          ← Python dependencies
│   └── data_augmentation.py      ← Image augmentation
│
├── 📂 face_recognition_test/      ← Recognition Testing
│   ├── video_recognition.py      ← Webcam recognition demo
│   ├── recognition.py            ← Recognition logic
│   ├── config.py                 ← Config (thresholds)
│   └── test_photos/              ← Sample test images
│
├── 📂 raspy-biometric-backend/    ← Raspberry Pi Backend (Future)
│   ├── api_server.py             ← Flask API server
│   ├── config.yaml               ← Server config
│   ├── requirements.txt          ← Dependencies
│   ├── modules/
│   │   ├── db_manager.py         ← Database ops
│   │   ├── face_matcher.py       ← Face matching
│   │   └── api_routes.py         ← Flask routes
│   └── tools/
│       ├── enroll_face.py        ← CLI enrollment
│       ├── enroll_fingerprint.py ← Fingerprint enroll
│       └── list_users.py         ← List users CLI
│
├── 📂 bundle/                     ← Python Runtime Bundle
│   └── python-runtime/           ← Bundled Python 3.10
│       ├── python/
│       ├── DLLs/
│       ├── Lib/
│       ├── Scripts/
│       └── insightface/           ← Face models
│
├── 📂 build/                      ← Build Artifacts
│   └── pyinstaller/
│       └── training_api.spec     ← PyInstaller config
│
├── 📂 dist/                       ← Built Frontend (Output)
│   └── [generated on build]
│
├── 📂 dist-electron/              ← Built Electron (Output)
│   ├── main.js
│   └── preload.js
│
├── 📂 scripts/                    ← Build Scripts
│   └── build-python-runtime.ps1  ← Runtime packaging
│
└── 📄 Documentation Files
    ├── QUICK_START.md            ← Quick start guide
    ├── PROJECT_RECAP_AND_PR.md   ← Project summary
    ├── TUTORIAL_TEKNISI.md       ← Technical guide
    ├── TUTORIAL_PENGGUNA.md      ← User guide
    ├── INTEGRATION_GUIDE.md      ← Integration docs
    └── ADD_USER_WITH_ID_README.md ← User enrollment guide
```

---

## 🚀 Startup Guide

### Prerequisites
```
✅ Node.js 16+ (with npm)
✅ Python 3.10
✅ Webcam
✅ ~2GB RAM minimum
✅ ~1GB disk space (for models)
```

### Development Setup

#### 1. Install Dependencies
```bash
cd "d:\New folder"
npm install

cd embedding_extractor
pip install -r requirements.txt
cd ..
```

#### 2. Start Development Environment
```bash
npm run dev
```

**Expected output:**
```
[Vite dev server ready] on http://localhost:5173
[Electron window opened] 1200x800
[Internal Express API running on port 3001]
```

#### 3. Verify System is Ready
- Electron window appears with UI
- Vite dev server shows in terminal
- No red errors in console

### First Time Enrollment (Testing)

#### Step 1: Enrollment Form
1. Click **"Enrollment"** menu
2. Enter User ID: `test_user_1`
3. Click webcam area to position face

#### Step 2: Photo Capture
1. Click **"Ambil Foto"** button 10+ times
2. Move face around for different angles
3. Grid preview shows captured photos
4. Total: 10 photos minimum

#### Step 3: Training
1. Click **"Mulai Training Wajah"** button
2. **Wait 50-80 seconds** for processing:
   - Data augmentation (rotation, flip, etc)
   - FaceNet embedding extraction
   - Storing to `embeddings.pkl`
3. Success message: `✅ Training berhasil! 10 × 50 = 500 embeddings`

#### Step 4: Verify Embeddings
```bash
# Check file exists
ls "d:\New folder\embeddings.pkl"
# Should show ~100KB+ file
```

### Test Recognition

#### Method 1: In-App Recognition
1. Click **"Recognition"** menu
2. Position face in webcam
3. Press **SPACE** to test
4. Result: Green box with user ID (if > 0.6 similarity)

#### Method 2: Standalone Test
```bash
cd "d:\New folder\face_recognition_test"
python video_recognition.py
```

**Expected output:**
```
============================================================
FACE RECOGNITION TEST
============================================================
📁 Test photos directory: ...
📊 Loading embeddings for users: ['test_user_1']
[Webcam ready]
Press SPACE to test
```

---

## 🔧 Troubleshooting

### Category A: Startup Issues

#### ❌ "npm: command not found"
**Solution:**
- Install Node.js from https://nodejs.org/
- Restart terminal/system
- Verify: `node --version` & `npm --version`

#### ❌ "Electron window doesn't open"
**Solution:**
```bash
# Check for errors
npm run dev 2>&1 | tee debug.log

# Verify Vite server started
# Look for: "VITE v..." message

# Try rebuild
npm run build
npm run serve
```

#### ❌ "Vite dev server not starting"
**Solution:**
```bash
# Kill existing processes on port 5173
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Clear Vite cache
rmdir /s vite_cache .vite 2>$null
npm run dev
```

#### ❌ "Express API error on port 3001"
**Solution:**
```bash
# Check if port is in use
netstat -ano | findstr :3001

# Kill process if occupied
taskkill /PID <PID> /F

# Restart app
npm run dev
```

---

### Category B: Enrollment Issues

#### ❌ "Webcam not detected"
**Solution:**
- Windows Settings → Privacy → Camera → Check app is enabled
- Test: Windows built-in Camera app
- Verify permissions in DevTools Console
- Try: Reload Electron window (Ctrl+R)

#### ❌ "Photos not being saved"
**Solution:**
```bash
# Check photos folder exists
ls "d:\New folder\photos"
# Create if missing:
mkdir "d:\New folder\photos"

# Verify permissions
# File → Properties → Security → Modify (check box)
```

#### ❌ "Python module not found: torch, mtcnn, etc"
**Solution:**
```bash
cd embedding_extractor

# Reinstall all dependencies
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall

# Verify installation
python -c "import torch; print(torch.__version__)"
python -c "import mtcnn; print('MTCNN OK')"
```

#### ❌ "Training takes longer than 3 minutes"
**Possible Causes:**
- CPU bottleneck (normal on slower systems)
- First run: Models loading from disk (~1 min)
- Large number of photos (>20)

**Solutions:**
```bash
# Check CPU/Memory usage
# Windows Task Manager → Performance tab

# Reduce photos to 10-15
# Training will be faster

# Enable GPU (if available)
# embedding_extractor/config.py
# Set: USE_GPU = True
```

#### ❌ "Training starts but no progress"
**Solution:**
```bash
# Check if Python subprocess is running
# Task Manager → Processes → search "python"

# If stuck, kill and retry
# Task Manager → End Process

# Check logs
echo "Check Electron console for error details"
# DevTools → Console tab
```

#### ❌ "'embeddings.pkl not found' during recognition"
**Cause:** Training failed or file not created

**Solution:**
```bash
# Verify training completed
ls "d:\New folder\embeddings.pkl"

# If missing, retry enrollment
# Follow "First Time Enrollment" steps again

# Check for errors in console
```

---

### Category C: Recognition Issues

#### ❌ "NOT IDENTIFIED" when face should be recognized
**Causes:**
- Similarity score < 0.6 (threshold)
- Different lighting/angle than training
- Poor quality photos during training

**Solutions:**

**Option 1: Lower threshold**
```python
# embedding_extractor/config.py
SIMILARITY_THRESHOLD = 0.55  # Lower from 0.6
```
⚠️ *Warning: May increase false positives*

**Option 2: Re-train with more photos**
```bash
# Enroll with 15-20 photos instead of 10
# Vary angles, lighting, and distance
# Include different expressions
```

**Option 3: Check embedding quality**
```bash
python
>>> import pickle
>>> with open('embeddings.pkl', 'rb') as f:
...     data = pickle.load(f)
>>> print(f"Users: {list(data.keys())}")
>>> print(f"Embeddings per user: {len(data['test_user_1'])}")
```

#### ❌ "All faces recognized as same person"
**Cause:** Threshold too low or insufficient training

**Solution:**
```python
# embedding_extractor/config.py
SIMILARITY_THRESHOLD = 0.65  # Increase threshold
```

#### ❌ "Webcam lag or freezing during recognition"
**Solution:**
```bash
# Check USB connection (if external webcam)
# Close other apps using webcam
# Device Manager → Camera → Update drivers

# Reduce resolution in config.py
TARGET_FACE_SIZE = (128, 128)  # Lower from 160
```

---

### Category D: Build & Deployment

#### ❌ "npm run build fails with TypeScript error"
**Solution:**
```bash
# Check errors
npm run build 2>&1 | head -20

# Fix TypeScript
npx tsc --noEmit

# Try rebuild from clean state
rm -r dist dist-electron node_modules
npm install
npm run build
```

#### ❌ "Bundled Python runtime not found"
**Solution:**
```bash
# Rebuild Python runtime
npm run build:python-runtime

# This requires PowerShell and ~5 minutes
# Check: bundle/python-runtime/python.exe
```

#### ❌ "Electron installer (.exe) generation failed"
**Solution:**
```bash
# Build development version first
npm run build

# Then create installer
npm run dist:win

# Installer will be in: dist/Biometric Desktop-Setup-1.0.0.nsis
```

---

### Category E: Performance Issues

#### ❌ "High CPU usage while idle"
**Solution:**
- Check for stray Python processes: `tasklist | findstr python`
- Close other apps
- Disable background services

#### ❌ "Memory leak (RAM keeps growing)"
**Solution:**
```bash
# Restart Electron app
# Close and reopen npm run dev

# Check for circular references in code
# Enable DevTools memory profiler
```

---

## 📊 System Health Check

### Quick Diagnostic Script
```powershell
# Run this to verify system setup:

Write-Host "🔍 Biometric System Diagnostic" -ForegroundColor Cyan

# 1. Check Node.js
Write-Host "`n1. Node.js/npm:" -ForegroundColor Yellow
node --version
npm --version

# 2. Check Python
Write-Host "`n2. Python:" -ForegroundColor Yellow
python --version

# 3. Check required Python packages
Write-Host "`n3. Python Packages:" -ForegroundColor Yellow
python -c "import torch, mtcnn, facenet_pytorch, cv2; print('✓ All packages OK')"

# 4. Check ports availability
Write-Host "`n4. Port Availability:" -ForegroundColor Yellow
netstat -ano | findstr ":3001 :5173" | findstr "LISTENING" && echo "✓ Ports free" || echo "✗ Ports occupied"

# 5. Check key files
Write-Host "`n5. Key Files:" -ForegroundColor Yellow
Test-Path "embedding_extractor\requirements.txt" && echo "✓ embedding_extractor OK"
Test-Path "electron\main.ts" && echo "✓ electron OK"
Test-Path "src\App.tsx" && echo "✓ src OK"

Write-Host "`n✅ Diagnostic complete" -ForegroundColor Green
```

---

## 📞 Quick Reference

| Component | Port | Process | Status |
|-----------|------|---------|--------|
| Vite Dev Server | 5173 | npm run dev | Frontend |
| Express API | 3001 | Electron subprocess | Backend |
| Electron App | - | npm run dev | Main App |
| Python ML | - | On-demand subprocess | ML Processing |

| File/Folder | Purpose |
|------------|---------|
| `embeddings.pkl` | Stored face embeddings database |
| `photos/` | Temporary training photos |
| `dist/` | Compiled React app |
| `dist-electron/` | Compiled Electron code |

---

## 🎓 Next Steps

1. **Test Enrollment** → Complete first enrollment flow
2. **Test Recognition** → Verify face matching works
3. **Explore Code** → Read comments in `App.tsx`, `training_api.py`
4. **Customize** → Adjust thresholds in `config.py`
5. **Deploy** → Run `npm run dist:win` for .exe installer

---

**Need more help?** Check the detailed guides:
- 🚀 [QUICK_START.md](QUICK_START.md)
- 📖 [TUTORIAL_TEKNISI.md](TUTORIAL_TEKNISI.md)
- 👤 [TUTORIAL_PENGGUNA.md](TUTORIAL_PENGGUNA.md)
- 🔗 [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
