# SYSTEM UNDERSTANDING PROMPT

You are analyzing a **Biometric Desktop Application** - a face recognition enrollment and matching system built with Electron, React, and Python.

## SYSTEM OVERVIEW
- **Name**: Biometric Desktop
- **Purpose**: Enroll user faces and perform real-time face recognition
- **Architecture**: Multi-layer (Electron Desktop App + Express API + Python ML Services)
- **Target Platform**: Windows (with bundled Python runtime)

---

## SYSTEM ARCHITECTURE

The application consists of 5 layers:

### Layer 1: Frontend (React + TypeScript + Vite)
- **Port**: 5173 (dev), served from dist/ (production)
- **Components**: 
  - `App.tsx` - Main container
  - `EnrollmentView.tsx` - Enrollment UI
  - `SetupWizard.tsx` - System configuration
- **Purpose**: User interface for enrollment and recognition workflows
- **Tech**: React, TypeScript, Vite bundler

### Layer 2: Electron Main Process
- **Entry**: `electron/main.ts`
- **Responsibilities**: 
  - Window management (1200x800)
  - Starts Express API server on :3001
  - Handles app lifecycle
  - Manages system resources
- **IPC Bridge**: `preload.ts` for secure communication

### Layer 3: Backend API (Express.js on :3001)
- **Entry**: `electron/api.ts`
- **Key Endpoints**:
  - POST `/api/enroll` - Start enrollment with photos
  - POST `/api/train` - Trigger Python training subprocess
  - POST `/api/recognize` - Perform face recognition on frame
  - GET `/api/embeddings` - Retrieve stored embeddings count
- **Responsibility**: HTTP API bridge between React frontend and Python backend

### Layer 4: Python ML Services
Located in `embedding_extractor/` - handles all ML/AI processing:

**Process A: Training (Enrollment)**
1. Input: 10+ webcam photos of a user (saved as JPG)
2. MTCNN: Detect faces in photos (face detection)
3. FaceNet: Extract 512-dimensional embeddings (face representation)
4. Augmentation: Create variations (rotate, flip, blur) to get 500+ embeddings
5. Output: Save all embeddings to `embeddings.pkl` (Python pickle format)
6. Time: ~50-80 seconds per user

**Process B: Recognition**
1. Input: Webcam frame (JPG)
2. MTCNN: Detect face in frame
3. FaceNet: Extract embedding
4. Comparison: Calculate cosine similarity with all stored embeddings
5. Threshold: If similarity >= 0.6 → IDENTIFIED, else NOT IDENTIFIED
6. Output: { userId, similarity_score }
7. Time: ~1-2 seconds

**Key ML Models:**
- FaceNet (vggface2) - Extract facial embeddings (512-dim vectors)
- MTCNN - Multi-task Cascaded Convolutional Networks (face detection)
- Configuration: `embedding_extractor/config.py`

### Layer 5: Data Storage (SQLite + Pickle)
- **Primary**: `embeddings.pkl` - Pickled Python dictionary
  - Format: `{ "user_id_1": [embedding1, embedding2, ...], "user_id_2": [...], ... }`
  - Size: ~100KB per user (500 embeddings)
- **Fallback**: SQLite database for future metadata storage

---

## DATA FLOW

### Enrollment Flow
```
User UI
  ↓ [clicks "Ambil Foto" 10+ times]
  ↓ Photos uploaded as base64
Express API (:3001)
  ↓ [spawns Python subprocess: training_api.py]
  ↓ [saves photos to photos/john_doe/]
Python ML Engine
  ↓ MTCNN face detection
  ↓ FaceNet embedding extraction
  ↓ Data augmentation (500+ embeddings)
  ↓ Save to embeddings.pkl
  ↓ [subprocess exits]
Express API
  ↓ [returns success status]
UI Display
  ↓ "✅ Training berhasil! 500 embeddings"
```

### Recognition Flow
```
User UI
  ↓ [presses SPACE]
  ↓ Webcam frame captured
Express API (:3001)
  ↓ [spawns Python subprocess]
Python ML Engine
  ↓ Load embeddings.pkl
  ↓ MTCNN face detection on frame
  ↓ FaceNet embedding extraction
  ↓ Calculate cosine similarity with all stored embeddings
  ↓ Find best match
  ↓ Return { userId, similarity }
  ↓ [subprocess exits]
Express API
  ↓ [returns match result]
UI Display
  ↓ GREEN BOX: ✓ IDENTIFIED john_doe (0.82)
  ↓ OR RED BOX: ✗ NOT IDENTIFIED
```

---

## FOLDER STRUCTURE

```
Root Directory: d:\New folder\

Core Configuration:
  - package.json (npm scripts: dev, build, serve, dist:win)
  - tsconfig.json (TypeScript compilation)
  - vite.config.ts (Frontend bundler config)
  - electron-builder.bundled.json (App packaging for .exe)
  - index.html (Entry HTML)

Frontend Code (React):
  src/
    - main.tsx (React entry point)
    - App.tsx (Main app component)
    - EnrollmentView.tsx (Enrollment UI)
    - SetupWizard.tsx (Setup UI)
    - index.css (Styles)

Electron/Desktop Code:
  electron/
    - main.ts (Electron window creation)
    - preload.ts (IPC secure bridge)
    - api.ts (Express server setup)
    - database.ts (DB operations)

Python ML Code:
  embedding_extractor/
    - main.py (Entry point)
    - training_api.py (Training subprocess - called by Express)
    - facenet_utils.py (FaceNet model loading)
    - mtcnn_utils.py (MTCNN face detection)
    - config.py (Model configs: GPU, face size, thresholds)
    - data_augmentation.py (Image transformations)
    - requirements.txt (Python deps: torch, mtcnn, facenet-pytorch, opencv)

Recognition Testing:
  face_recognition_test/
    - video_recognition.py (Standalone recognition demo)
    - recognition.py (Recognition logic)
    - config.py (Similarity threshold, etc)
    - test_photos/ (Sample test images)

Raspberry Pi Backend (Future):
  raspy-biometric-backend/
    - api_server.py (Flask API for RPi)
    - config.yaml (Server config)
    - modules/ (DB, face matching logic)
    - tools/ (CLI enrollment tools)

Build Artifacts:
  bundle/python-runtime/ (Bundled Python 3.10 executable)
  build/pyinstaller/ (PyInstaller configs)
  dist/ (Built React app - generated)
  dist-electron/ (Built Electron code - generated)

Build Scripts:
  scripts/build-python-runtime.ps1 (PowerShell script to package Python)

Documentation:
  QUICK_START.md, TUTORIAL_TEKNISI.md, etc.
```

---

## KEY CONNECTIONS

1. **Frontend ↔ Backend**: HTTP requests to Express API on :3001
   - POST `/api/enroll` with base64 photos
   - POST `/api/train` to trigger training
   - POST `/api/recognize` with webcam frame

2. **Express ↔ Python**: Subprocess spawning
   - Express calls `python training_api.py` (training)
   - Express calls `python recognize.py` (recognition)
   - Python writes results to stdout/stderr
   - Express reads and returns via HTTP

3. **Python ↔ Storage**: File I/O
   - Reads photos from `photos/user_id/`
   - Writes embeddings to `embeddings.pkl`
   - Reads `embeddings.pkl` for recognition

4. **Electron Window**: Hosts React app
   - Uses preload.ts for secure IPC
   - Passes system paths to Express startup
   - Manages window state

---

## TECHNOLOGY STACK

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + TypeScript + Vite + CSS |
| Desktop | Electron 25+ |
| Backend API | Express.js (embedded in Electron) |
| ML/AI | PyTorch + FaceNet + MTCNN + OpenCV |
| Database | embeddings.pkl (pickle) + SQLite |
| Bundler | Vite (frontend) + Electron Builder (app) |
| Python Runtime | Python 3.10 (bundled or system) |

---

## STARTUP FLOW

1. **npm run dev** starts Vite dev server (frontend)
2. Electron launches and loads Vite dev server
3. Electron spawns Express API server on :3001
4. Frontend connects to Express API via HTTP
5. User interacts with React UI
6. Express handles requests by spawning Python subprocesses
7. Python performs ML operations
8. Results returned to frontend

---

## CONFIGURATION POINTS

- **ML Thresholds**: `embedding_extractor/config.py`
  - `SIMILARITY_THRESHOLD = 0.6` (recognition confidence)
  - `USE_GPU = True` (GPU acceleration)
  - `TARGET_FACE_SIZE = (160, 160)` (face alignment size)

- **API Server**: `electron/api.ts`
  - Port: 3001
  - Routes for enroll, train, recognize

- **App Config**: `package.json`
  - `npm run dev` - Development
  - `npm run build` - Production build
  - `npm run dist:win` - Windows installer

---

## COMMON OPERATIONS

- **Enroll New User**: UI form → Express API → Python training → embeddings.pkl
- **Recognize Face**: Webcam frame → Express API → Python recognition → result
- **Deploy App**: `npm run build` then `npm run dist:win` for .exe
- **Rebuild Python Runtime**: `npm run build:python-runtime` (requires PowerShell)

---

## ERROR HANDLING & TROUBLESHOOTING

**If Express API not responding:**
- Check port 3001 in use: `netstat -ano | findstr :3001`
- Check terminal for [Internal Express API running] message

**If Python subprocess fails:**
- Check console for error traceback
- Verify Python packages installed: `pip install -r requirements.txt`
- Check if Python process spawned: Task Manager → Processes

**If face recognition not working:**
- Verify embeddings.pkl exists and has content
- Lower threshold in config.py if needed
- Re-train with more photos (15-20)

---

## USE THIS PROMPT FOR

1. Explaining system architecture to stakeholders
2. Onboarding new developers to codebase
3. Debugging issues across layers
4. Planning new features or modifications
5. Understanding data flows
6. Discussing performance optimization
7. Planning deployment strategy

---

**End of System Understanding Prompt**

---

## USAGE INSTRUCTION

Use this prompt when:
- Starting work on the codebase
- Explaining system to team members
- Debugging cross-layer issues
- Planning architecture changes
- Writing tests or documentation

Share the full prompt text with AI assistants to provide instant system context.
