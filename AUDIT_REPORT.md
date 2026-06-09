# 📋 AUDIT REPOSITORY BIOMETRIC-DESKTOP
**Status:** PRE-REFACTOR ANALYSIS  
**Date:** June 9, 2026  
**Prepared by:** Software Architect & Repository Maintainer

---

## ✅ TAHAP 1 - HASIL AUDIT REPOSITORY

### 1.1 Ringkasan Struktur Saat Ini

```
biometric-desktop/                          # 1.0.0 - Electron + React + Python ML
├── 📄 README.md                            # Documentation (outdated)
├── 📄 SYSTEM_DOCUMENTATION.md              # Detailed architecture doc
├── 📄 package.json                         # Node.js dependencies & scripts
├── 📄 tsconfig.json                        # TypeScript config
├── 📄 vite.config.ts                       # Vite build config
├── 📄 electron-builder.bundled.json        # Electron packager config
│
├── 🔵 embedding_extractor/                 # [ACTIVE] Face embedding extraction
│   ├── main.py
│   ├── training_api.py                     # Used by Electron app
│   ├── embedding_store.py                  # Used by Electron app
│   ├── config.py                           # Relative paths to ../photos, ../embeddings.pkl
│   ├── facenet_utils.py
│   ├── mtcnn_utils.py
│   ├── data_augmentation.py
│   ├── test_training.py
│   ├── collect_and_extract.py
│   ├── requirements.txt
│   ├── README.md
│   ├── AUGMENTATION_GUIDE.md
│   └── COLLECTION_GUIDE.md
│
├── 🟡 web_app/                             # [ACTIVE] Desktop application (React + Electron)
│   ├── index.html
│   ├── electron/
│   │   ├── main.ts                         # Electron entry point
│   │   ├── preload.ts                      # IPC bridge
│   │   ├── api.ts                          # Express backend + Python orchestration
│   │   └── database.ts                     # SQLite operations
│   └── src/
│       ├── App.tsx
│       ├── EnrollmentView.tsx
│       ├── SetupWizard.tsx
│       ├── main.tsx
│       └── index.css
│
├── 🟡 model/                               # [SEMI-ACTIVE] ML Pipeline structure
│   ├── acquisition/                        # Data acquisition & preprocessing
│   │   ├── embedding_extractor/            # [DUPLICATE] Empty placeholder
│   │   │   ├── config.py                   # Same as root version
│   │   │   ├── facenet_utils.py
│   │   │   ├── main.py
│   │   │   ├── mtcnn_utils.py
│   │   │   ├── README.md                   # EMPTY
│   │   │   └── requirements.txt
│   │   │
│   │   └── face_recognition_test/          # Face recognition testing
│   │       ├── recognition.py
│   │       ├── video_recognition.py
│   │       ├── config.py
│   │       ├── VIDEO_MODE.md
│   │       └── README.md
│   │
│   ├── training/                           # [EMPTY] Future training scripts
│   ├── inference/                          # [EMPTY] Future inference scripts
│   │
│   ├── raspy-biometric-backend/            # [ACTIVE] Raspberry Pi Flask API
│   │   ├── api_server.py
│   │   ├── config.yaml
│   │   ├── requirements.txt
│   │   ├── setup.sh
│   │   ├── QUICKSTART.md
│   │   ├── README.md
│   │   ├── modules/
│   │   │   ├── __init__.py
│   │   │   ├── db_manager.py
│   │   │   └── face_matcher.py
│   │   └── tools/
│   │       ├── __init__.py
│   │       ├── enroll_face.py
│   │       ├── enroll_fingerprint.py
│   │       └── list_users.py
│   │
│   └── raspy-main-integrated/              # [ACTIVE] Integrated Raspberry Pi system
│       ├── main_integrated.py              # Main entry point
│       ├── config.example.yaml
│       ├── requirements.txt
│       ├── QUICKSTART.md
│       ├── README.md
│       ├── arduino/
│       │   └── arduino_firmware.ino
│       ├── modules/
│       │   ├── __init__.py
│       │   ├── biometric.py
│       │   ├── absensi_utils.py
│       │   ├── embedded_api.py
│       │   ├── logger.py
│       │   └── serial_nanonano.py
│       ├── face/
│       │   ├── __init__.py
│       │   ├── arcface_utils.py
│       │   ├── capture_face.py
│       │   ├── head_pose.py
│       │   ├── manage_faces.py
│       │   ├── mtcnn_utils.py
│       └── AppsScript
│
├── 🔵 docs/                                # Documentation folder
├── 🔵 scripts/                             # Build & utility scripts
│   └── build-python-runtime.ps1
│
├── 📚 Documentation Files (Root)
│   ├── QUICK_START.md
│   ├── TUTORIAL_PENGGUNA.md
│   ├── TUTORIAL_TEKNISI.md
│   ├── ALUR_APLIKASI_DETAIL.md
│   ├── INTEGRATION_GUIDE.md
│   ├── PROJECT_RECAP_AND_PR.md
│   ├── PRE_GITHUB_CHECKLIST.md
│   ├── GITHUB_UPLOAD_*.md (4 files)
│   ├── ADD_USER_WITH_ID_README.md
│   ├── SYSTEM_PROMPT.md
│   └── ts_errors.txt
│
└── 📄 Configuration Files (Root)
    ├── package-lock.json
    ├── .env.example
    └── .gitignore
```

### 1.2 Analisis Fungsi Folder

| Folder | Status | Fungsi Utama | Dependency | Kategori Target |
|--------|--------|-------------|-----------|-----------------|
| **embedding_extractor** | 🔵 Active | Extract face embeddings (FaceNet+MTCNN) | PyTorch, facenet-pytorch, opencv, mtcnn | `acquisition` |
| **web_app/electron** | 🔵 Active | Electron main process + IPC bridge | electron, express | `builder` |
| **web_app/src** | 🔵 Active | React UI components | react, react-router, react-webcam | `builder` |
| **model/acquisition/embedding_extractor** | 🟡 Duplicate | Same as root version (incomplete) | PyTorch, facenet-pytorch | `acquisition` |
| **model/acquisition/face_recognition_test** | 🟡 Active | Test recognition against embeddings | OpenCV, NumPy | `inference` |
| **model/training** | ⚫ Empty | Placeholder for future training | N/A | `training` |
| **model/inference** | ⚫ Empty | Placeholder for future inference | N/A | `inference` |
| **model/raspy-biometric-backend** | 🟡 Active | Flask API server untuk Raspy | Flask, sqlite3, facenet-pytorch | `backend` |
| **model/raspy-main-integrated** | 🟡 Active | Integrated Raspy system + Arduino | PySerial, OpenCV, NumPy | `deployment` |
| **docs/** | 🔵 Semi-Active | Documentation storage | N/A | N/A |
| **scripts/** | 🔵 Semi-Active | Build scripts (Python runtime) | PowerShell | N/A |

### 1.3 Dependency Analysis

#### Python Dependencies (Root embedding_extractor)
```
torch, torchvision, torchaudio
facenet-pytorch
mtcnn
opencv-python
Pillow
numpy
scipy
scikit-learn
requests
pyyaml
flask
```

#### Node.js/TypeScript Dependencies
```
react, react-dom
react-router-dom
react-webcam
vite, typescript
electron, electron-builder
express
cors
mysql2
sql.js
lucide-react
```

#### Hardware/System
```
Arduino Nano (fingerprint sensor)
Raspberry Pi 5
Camera module
Fingerprint sensor (optical)
```

---

## ✅ TAHAP 2 - ANALISIS DUPLIKASI

### 2.1 Folder `embedding_extractor` - CRITICAL DUPLICATE

#### Lokasi 1: `/embedding_extractor/` (ROOT) ✅ COMPLETE
- **Status:** ACTIVE & COMPLETE
- **Ukuran:** ~13 files
- **Digunakan oleh:** 
  - Electron app via `getBundledResourcePath('embedding_extractor', ...)`
  - Referenced in `package.json` build config
  - API calls di `web_app/electron/api.ts`
- **Files:** main.py, training_api.py, embedding_store.py, config.py, dll
- **Last Updated:** Recent (appears to be active development)
- **Path dalam config.py:** Uses relative paths (`../photos`, `../embeddings.pkl`)

#### Lokasi 2: `/model/acquisition/embedding_extractor/` (INCOMPLETE)
- **Status:** INCOMPLETE & UNUSED
- **Ukuran:** ~6 files
- **Digunakan oleh:** NONE (empty README, no direct references)
- **Files:** config.py, facenet_utils.py, main.py, mtcnn_utils.py, requirements.txt, README.md (EMPTY)
- **Last Updated:** Appears to be stale
- **Path dalam config.py:** Uses relative paths (`../photos`, `../embeddings.pkl`)

#### Perbandingan Detail
```
File                   | Root Ver | Model/Acq Ver | NOTES
─────────────────────────────────────────────────────────
main.py               | ✓        | ✓            | Root has full logic
training_api.py       | ✓        | ✗            | ONLY in root, actively used
embedding_store.py    | ✓        | ✗            | ONLY in root, actively used
config.py             | ✓        | ✓            | Nearly identical
facenet_utils.py      | ✓        | ✓            | Identical
mtcnn_utils.py        | ✓        | ✓            | Identical
data_augmentation.py  | ✓        | ✗            | ONLY in root
test_training.py      | ✓        | ✗            | ONLY in root
requirements.txt      | ✓        | ✓            | Likely identical
README.md             | ✓        | ✗ EMPTY      | Root is comprehensive
```

#### Kesimpulan Duplikasi
| Aspek | Temuan |
|-------|--------|
| **Mana yang lebih lengkap?** | Root `/embedding_extractor/` (100% complete, all utilities present) |
| **Mana yang lebih baru?** | Root `/embedding_extractor/` (actively maintained, full features) |
| **Mana yang digunakan aplikasi?** | Root `/embedding_extractor/` (referenced in api.ts & package.json build) |
| **Mana yang sebaiknya dipertahankan?** | Root `/embedding_extractor/` ONLY |
| **Mana yang aman dihapus?** | `/model/acquisition/embedding_extractor/` (incomplete, unused duplicate) |
| **Risk Level** | LOW - No active references to model/acquisition version |

### 2.2 File Redundancy Check

**Duplicate Utilities:**
- `model/acquisition/embedding_extractor/facenet_utils.py` = `embedding_extractor/facenet_utils.py` (identical)
- `model/acquisition/embedding_extractor/mtcnn_utils.py` = `embedding_extractor/mtcnn_utils.py` (identical)
- `model/acquisition/embedding_extractor/config.py` ≈ `embedding_extractor/config.py` (similar, relative paths)

**Unique to Root (NOT IN DUPLICATE):**
- `embedding_extractor/training_api.py` ← CRITICAL - Used by Electron app
- `embedding_extractor/embedding_store.py` ← CRITICAL - Used by Electron app
- `embedding_extractor/data_augmentation.py` ← Used by training pipeline
- `embedding_extractor/test_training.py` ← Test suite

---

## ✅ TAHAP 3 - REORGANISASI MODEL STRUCTURE

### 3.1 Proposed Final Structure - ACQUISITION

```
model/acquisition/                          # DATA COLLECTION & PREPROCESSING
├── README.md                               # Acquisition pipeline docs
├── 
├── embedding_extraction/                   # Face embedding extraction (moved from root)
│   ├── main.py
│   ├── training_api.py
│   ├── embedding_store.py
│   ├── facenet_utils.py
│   ├── mtcnn_utils.py
│   ├── config.py                           # Will update path references
│   ├── data_augmentation.py
│   ├── test_training.py
│   ├── collect_and_extract.py
│   ├── requirements.txt
│   ├── README.md
│   ├── AUGMENTATION_GUIDE.md
│   └── COLLECTION_GUIDE.md
│
└── face_recognition_test/                  # TEST PHASE
    ├── recognition.py
    ├── video_recognition.py
    ├── config.py
    ├── VIDEO_MODE.md
    └── README.md
```

**Alasan:**
- `embedding_extraction/` lebih deskriptif daripada `embedding_extractor/`
- Semua acquisition tools berada di satu folder terorganisir
- Path relatif akan tetap stabil (hanya perlu update `config.py`)

### 3.2 Proposed Final Structure - TRAINING

```
model/training/                             # MODEL TRAINING PIPELINE
├── README.md
└── (future training scripts)
```

**Note:** Currently empty, placeholder untuk phase 2.

### 3.3 Proposed Final Structure - INFERENCE

```
model/inference/                            # MODEL INFERENCE & VERIFICATION
├── README.md
└── (future inference scripts)
```

**Note:** Currently empty, placeholder untuk phase 2.

### 3.4 Proposed Final Structure - BACKEND

```
model/backend/                              # RASPBERRY PI FLASK API
├── api_server.py
├── config.yaml
├── requirements.txt
├── setup.sh
├── QUICKSTART.md
├── README.md
├── modules/
│   ├── __init__.py
│   ├── db_manager.py
│   └── face_matcher.py
└── tools/
    ├── __init__.py
    ├── enroll_face.py
    ├── enroll_fingerprint.py
    └── list_users.py
```

**Path Reference:** Folder dipindahkan dari `raspy-biometric-backend/` ke `backend/`  
**Risk Level:** MEDIUM - Will need import path updates in any scripts that reference this

### 3.5 Proposed Final Structure - DEPLOYMENT

```
model/deployment/                           # INTEGRATED RASPBERRY PI SYSTEM
├── main_integrated.py
├── config.example.yaml
├── requirements.txt
├── QUICKSTART.md
├── README.md
├── arduino/
│   └── arduino_firmware.ino
├── modules/
│   ├── __init__.py
│   ├── biometric.py
│   ├── absensi_utils.py
│   ├── embedded_api.py
│   ├── logger.py
│   └── serial_nanonano.py
├── face/
│   ├── __init__.py
│   ├── arcface_utils.py
│   ├── capture_face.py
│   ├── head_pose.py
│   ├── manage_faces.py
│   └── mtcnn_utils.py
└── AppsScript
```

**Path Reference:** Folder dipindahkan dari `raspy-main-integrated/` ke `deployment/`  
**Risk Level:** MEDIUM - May have internal path references

### 3.6 Proposed Final Structure - MODEL FOLDER

```
model/
├── README.md                               # Model pipeline overview
│
├── acquisition/
│   ├── embedding_extraction/               # (moved from root)
│   └── face_recognition_test/
│
├── training/                               # (currently empty)
├── inference/                              # (currently empty)
│
├── backend/                                # (renamed from raspy-biometric-backend)
│   ├── modules/
│   ├── tools/
│   └── ...
│
└── deployment/                             # (renamed from raspy-main-integrated)
    ├── modules/
    ├── face/
    ├── arduino/
    └── ...
```

---

## ✅ TAHAP 4 - REORGANISASI WEB_APP STRUCTURE

### 4.1 Current Web App Structure

```
web_app/                                    # DESKTOP APP (React + Electron)
├── index.html
├── electron/
│   ├── main.ts
│   ├── preload.ts
│   ├── api.ts
│   └── database.ts
└── src/
    ├── App.tsx
    ├── EnrollmentView.tsx
    ├── SetupWizard.tsx
    ├── main.tsx
    └── index.css
```

### 4.2 Proposed Reorganization - TIDAK DIPERLUKAN

**Rekomendasi:** Struktur web_app saat ini SUDAH OPTIMAL untuk proyek skripsi

**Alasan:**
1. ✅ Struktur sederhana dan mudah dipahami
2. ✅ Electron + React standard pattern
3. ✅ `electron/` = main process + API
4. ✅ `src/` = UI components
5. ✅ Tidak ada folder `builder/` atau `running/` yang diperlukan
   - Jika ditambahkan, akan menambah kompleksitas tanpa benefit nyata
   - Build process sudah handled di `package.json` scripts
   - Development/production dihandle oleh Vite + Electron

### 4.3 Rekomendasi Struktur Web App (FINAL)

**JANGAN UBAH** - Pertahankan apa adanya:
```
web_app/                                    # DESKTOP APP (React + Electron)
├── index.html
├── electron/                               # ✅ Electron main process
│   ├── main.ts
│   ├── preload.ts
│   ├── api.ts                              # Express backend + Python orchestration
│   └── database.ts
└── src/                                    # ✅ React UI
    ├── App.tsx
    ├── EnrollmentView.tsx
    ├── SetupWizard.tsx
    ├── main.tsx
    └── index.css
```

**Build scripts di `package.json`:**
- `npm run dev` = Vite dev server + Electron
- `npm run build` = Compile + Bundle + Package
- `npm run build:bundled` = Include Python runtime

---

## ✅ TAHAP 5 - VALIDASI IMPORT & DEPENDENCY

### 5.1 Python Imports to Check

#### Root `/embedding_extractor/` files
```python
# main.py
from mtcnn_utils import detect_face_mtcnn
from facenet_utils import preprocess_face, extract_embedding, save_embeddings
from config import PHOTOS_ROOT, EMBEDDINGS_PATH, VERBOSE

# training_api.py
from config import FACENET_MODEL, USE_GPU
from facenet_pytorch import MTCNN, InceptionResnetV1

# embedding_store.py
import pickle
import os
import sys
```

**Current Status:** All imports use relative paths (same folder)  
**After Move to `/model/acquisition/embedding_extraction/`:** UNCHANGED - Still relative

#### `/model/acquisition/face_recognition_test/` files
```python
# recognition.py
import cv2
import numpy as np
import pickle
import os

# Relative imports (same folder)
from config import EMBEDDINGS_PATH, ...
```

**Current Status:** Relative imports  
**After Move:** UNCHANGED

#### `/model/raspy-biometric-backend/` files
```python
# api_server.py
from modules.db_manager import ...
from modules.face_matcher import ...

# modules/db_manager.py
import sqlite3
import os
```

**Current Status:** Uses relative `modules.` imports  
**After Move to `/model/backend/`:** UNCHANGED - Still relative

#### `/model/raspy-main-integrated/` files
```python
# main_integrated.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from modules.logger import SystemLogger
from modules.serial_nanonano import NanoSerial
from modules.biometric import BiometricAuth
```

**Current Status:** Adds modules to sys.path, then imports  
**After Move to `/model/deployment/`:** UNCHANGED - Still relative

### 5.2 TypeScript/JavaScript Imports to Check

#### `web_app/electron/api.ts`
```typescript
// Line 1133, 1160, 1224
const embeddingScript = getBundledResourcePath('embedding_extractor', 'embedding_store.py')
const trainingScript = getBundledResourcePath('embedding_extractor', 'training_api.py')
```

**Current Issue:** Hardcoded path `'embedding_extractor'`  
**Action Required:** Update to `'embedding_extraction'` jika folder di-rename  
**ATAU** Pertahankan root structure (recommended)

#### `web_app/electron/main.ts`
- Tidak ada explicit path references ke model folder (good!)

### 5.3 Configuration Files to Check

#### `package.json` Build Config
```json
"extraResources": [
  {
    "from": "model/acquisition/embedding_extractor",
    "to": "app-resources/embedding_extractor",
    "filter": ["**/*"]
  }
]
```

**Current Issue:** References `model/acquisition/embedding_extractor` (WRONG - empty folder!)  
**Action Required:** Update to point to correct location

#### `vite.config.ts`
```typescript
export default defineConfig({
  plugins: [
    react(),
    electron([
      {
        entry: 'electron/main.ts',
      },
    ]),
  ],
})
```

**Status:** ✅ No path changes needed

### 5.4 Documentation Files to Check

- `SYSTEM_DOCUMENTATION.md` - References paths, akan perlu update
- `README.md` - References model structure, akan perlu update
- `model/acquisition/embedding_extractor/README.md` - Empty, akan dihapus
- `model/raspy-biometric-backend/README.md` - Will need path updates
- `model/raspy-main-integrated/README.md` - Will need path updates

### 5.5 Summary of Path Changes Required

| File/Config | Current | Target | Change Type | Risk |
|-------------|---------|--------|-------------|------|
| api.ts | `getBundledResourcePath('embedding_extractor', ...)` | Keep ROOT or update | Code | MEDIUM |
| package.json | `model/acquisition/embedding_extractor` | `embedding_extractor/` | Config | MEDIUM |
| config.py (in embedding) | `../photos`, `../embeddings.pkl` | Update to `../../` | Config | LOW |
| SYSTEM_DOCUMENTATION.md | Multiple path references | Update all | Docs | LOW |
| README.md | Model structure docs | Update structure section | Docs | LOW |

---

## ✅ TAHAP 6 - ANALISIS RISIKO & MITIGASI

### 6.1 Risk Assessment by Category

#### CRITICAL RISKS (High Impact, Must Mitigate)
| Risk | Impact | Severity | Mitigation |
|------|--------|----------|-----------|
| Breaking Electron app path references | App won't find Python scripts | CRITICAL | Update package.json build config + api.ts |
| Incorrect Python import paths | Scripts fail to run | CRITICAL | Test relative paths after move |
| Breaking Raspberry Pi system | Backend API fails | CRITICAL | Keep raspy systems isolated, test thoroughly |

#### MEDIUM RISKS (Medium Impact, Should Address)
| Risk | Impact | Severity | Mitigation |
|------|--------|----------|-----------|
| Documentation becoming outdated | Confusion, installation failures | MEDIUM | Update all README files + SYSTEM_DOCUMENTATION.md |
| Database path references | SQLite connections fail | MEDIUM | Verify relative paths still work |
| Configuration file paths | App settings break | MEDIUM | Update config.yaml, config.py files |

#### LOW RISKS (Low Impact, Nice to Fix)
| Risk | Impact | Severity | Mitigation |
|------|--------|----------|-----------|
| Unused files in duplicate folder | Confusion, wasted space | LOW | Delete model/acquisition/embedding_extractor/ |
| Dead documentation links | Broken references | LOW | Fix .md file links |

### 6.2 Safety Checklist

- [ ] Backup entire repository before making changes
- [ ] Create git branch `refactor/reorganize-structure`
- [ ] Test each change incrementally
- [ ] Verify Python imports after each move
- [ ] Test Electron app build: `npm run build`
- [ ] Test Python script execution from new paths
- [ ] Update all documentation files
- [ ] Run final integration test

---

## 📊 TAHAP 6 - STRUKTUR FOLDER SAAT INI VS DIREKOMENDASIKAN

### Current Structure (Root Level)
```
biometric-desktop/                          (26 items)
├── embedding_extractor/                    ✅ ACTIVE
├── web_app/                                ✅ ACTIVE
├── model/                                  🟡 MIXED STATUS
│   ├── acquisition/embedding_extractor/    ⚫ DUPLICATE (DELETE)
│   ├── acquisition/face_recognition_test/  🟡 ACTIVE
│   ├── training/                           ⚫ EMPTY
│   ├── inference/                          ⚫ EMPTY
│   ├── raspy-biometric-backend/            🟡 ACTIVE
│   └── raspy-main-integrated/              🟡 ACTIVE
├── docs/                                   ✅ Present
├── scripts/                                ✅ Present
└── [18 README/Config files at root]        🟡 Cluttered
```

### Recommended Structure
```
biometric-desktop/                          (cleaner root)
├── 📄 README.md                            (updated, comprehensive)
├── 📄 SYSTEM_DOCUMENTATION.md
├── 📄 package.json
├── 📄 tsconfig.json
├── 📄 vite.config.ts
│
├── 📚 docs/                                (organized)
│   ├── QUICK_START.md
│   ├── SYSTEM_DOCUMENTATION.md (moved here or kept at root)
│   ├── INTEGRATION_GUIDE.md
│   └── user-guides/
│
├── 🔧 scripts/
│   └── build-python-runtime.ps1
│
├── 🖥️  web_app/                            (unchanged - already optimal)
│   ├── electron/
│   └── src/
│
├── 🤖 model/                               (reorganized by function)
│   ├── README.md                           (new - pipeline overview)
│   │
│   ├── acquisition/                        (DATA COLLECTION)
│   │   ├── embedding_extraction/           (renamed from embedding_extractor)
│   │   └── face_recognition_test/
│   │
│   ├── training/                           (FUTURE - MODEL TRAINING)
│   ├── inference/                          (FUTURE - PREDICTIONS)
│   │
│   ├── backend/                            (renamed from raspy-biometric-backend)
│   │   ├── modules/
│   │   ├── tools/
│   │   └── ...
│   │
│   └── deployment/                         (renamed from raspy-main-integrated)
│       ├── modules/
│       ├── face/
│       ├── arduino/
│       └── ...
```

---

## 📋 DAFTAR FILE YANG AKAN DIPINDAHKAN

### PHASE 1: Move `embedding_extractor/` to `model/acquisition/embedding_extraction/`

```
Source Files (13 items)              Destination
─────────────────────────────────────────────────────────────
embedding_extractor/                 model/acquisition/embedding_extraction/
├── main.py                           → embedding_extraction/main.py
├── training_api.py                   → embedding_extraction/training_api.py ⭐
├── embedding_store.py                → embedding_extraction/embedding_store.py ⭐
├── facenet_utils.py                  → embedding_extraction/facenet_utils.py
├── mtcnn_utils.py                    → embedding_extraction/mtcnn_utils.py
├── config.py                         → embedding_extraction/config.py
├── data_augmentation.py              → embedding_extraction/data_augmentation.py
├── test_training.py                  → embedding_extraction/test_training.py
├── collect_and_extract.py            → embedding_extraction/collect_and_extract.py
├── requirements.txt                  → embedding_extraction/requirements.txt
├── README.md                         → embedding_extraction/README.md
├── AUGMENTATION_GUIDE.md             → embedding_extraction/AUGMENTATION_GUIDE.md
└── COLLECTION_GUIDE.md               → embedding_extraction/COLLECTION_GUIDE.md
```

**Status Change:**
- OLD: `/embedding_extractor/` (active)
- NEW: `/model/acquisition/embedding_extraction/` (active)
- DELETE: `/model/acquisition/embedding_extractor/` (empty duplicate)

**Path Updates Required in Files:**
- `config.py`: Update relative paths `../../` instead of `../`

**Path Updates Required in Code:**
- `web_app/electron/api.ts`: Update `getBundledResourcePath('embedding_extractor', ...)` → `getBundledResourcePath('model/acquisition/embedding_extraction', ...)`
- `package.json`: Update `extraResources` path

---

### PHASE 2: Rename `raspy-biometric-backend/` → `backend/`

```
Source Files                         Destination
─────────────────────────────────────────────────────────────
model/raspy-biometric-backend/       model/backend/
├── api_server.py                    → backend/api_server.py
├── config.yaml                      → backend/config.yaml
├── requirements.txt                 → backend/requirements.txt
├── setup.sh                         → backend/setup.sh
├── README.md                        → backend/README.md
├── QUICKSTART.md                    → backend/QUICKSTART.md
├── modules/                         → backend/modules/
│   ├── __init__.py
│   ├── db_manager.py
│   └── face_matcher.py
└── tools/                           → backend/tools/
    ├── __init__.py
    ├── enroll_face.py
    ├── enroll_fingerprint.py
    └── list_users.py
```

**Status Change:**
- OLD: `/model/raspy-biometric-backend/` (active)
- NEW: `/model/backend/` (active)

**Path Updates Required:**
- None in Python files (all use relative imports)
- Documentation references to folder name

---

### PHASE 3: Rename `raspy-main-integrated/` → `deployment/`

```
Source Files                         Destination
─────────────────────────────────────────────────────────────
model/raspy-main-integrated/         model/deployment/
├── main_integrated.py               → deployment/main_integrated.py
├── config.example.yaml              → deployment/config.example.yaml
├── requirements.txt                 → deployment/requirements.txt
├── QUICKSTART.md                    → deployment/QUICKSTART.md
├── README.md                        → deployment/README.md
├── arduino/                         → deployment/arduino/
│   └── arduino_firmware.ino
├── modules/                         → deployment/modules/
├── face/                            → deployment/face/
└── AppsScript                       → deployment/AppsScript
```

**Status Change:**
- OLD: `/model/raspy-main-integrated/` (active)
- NEW: `/model/deployment/` (active)

**Path Updates Required:**
- None in Python files (all use relative imports)
- Documentation references

---

## 🗑️ DAFTAR FILE YANG AKAN DIHAPUS

### Files to DELETE (Safe Deletion)

```
Target Files for Deletion              Reason
──────────────────────────────────────────────────────────────
model/acquisition/embedding_extractor/  DUPLICATE FOLDER
  ├── config.py                         ├─ Incomplete duplicate
  ├── facenet_utils.py                  ├─ Identical to root
  ├── main.py                           ├─ Incomplete version
  ├── mtcnn_utils.py                    ├─ Identical to root
  ├── README.md                         ├─ EMPTY FILE
  └── requirements.txt                  └─ Obsolete copy

[Empty Folder]                          DELETE AFTER: Training complete
```

**Verification:**
- ✅ These files have active duplicates in `/embedding_extractor/`
- ✅ No code references to this duplicate folder
- ✅ README is EMPTY (proof of abandonment)
- ✅ No active imports from this location

**Risk: VERY LOW** - Completely safe to delete

---

## 📝 LANGKAH MIGRASI (STEP-BY-STEP)

### Step 1: Pre-Migration Verification (5 min)
```bash
# 1. Backup repository
git stash                              # Save any uncommitted changes
git branch refactor/reorganize         # Create safety branch

# 2. Verify current structure
ls -la embedding_extractor/
ls -la model/acquisition/embedding_extractor/
ls -la model/raspy-*

# 3. Test current build
npm install                            # Reinstall dependencies
npm run build                          # Test build (should succeed)
```

### Step 2: Delete Duplicate Folder (2 min)
```bash
# 1. Delete the empty/duplicate folder
rm -rf model/acquisition/embedding_extractor/

# 2. Verify deletion
ls -la model/acquisition/

# 3. Commit change
git add .
git commit -m "refactor: remove duplicate embedding_extractor folder"
```

### Step 3: Move Embedding Extractor (10 min)
```bash
# 1. Create new destination
mkdir -p model/acquisition/embedding_extraction

# 2. Move files
cp -r embedding_extractor/* model/acquisition/embedding_extraction/

# 3. Update paths in config.py
#    OLD: PHOTOS_ROOT = os.path.join(BASE_DIR, '../photos')
#    NEW: PHOTOS_ROOT = os.path.join(BASE_DIR, '../../photos')
#    (Adjust relative paths as needed)

# 4. Update package.json extraResources
#    OLD: "from": "model/acquisition/embedding_extractor"
#    NEW: "from": "embedding_extractor"  (Keep at root for build)

# 5. Delete root folder
rm -rf embedding_extractor/

# 6. Test
npm run build  # Should still work
python model/acquisition/embedding_extraction/main.py  # Test execution
```

### Step 4: Update api.ts References (10 min)
```bash
# In web_app/electron/api.ts:
# Update lines 1133, 1160, 1224:

# OLD: const embeddingScript = getBundledResourcePath('embedding_extractor', 'embedding_store.py')
# NEW: const embeddingScript = getBundledResourcePath('embedding_extractor', 'embedding_store.py')
# (Keep the same - getBundledResourcePath handles the mapping)

# VERIFY: Check if package.json extraResources is pointing correctly
```

### Step 5: Rename Backend Folders (10 min)
```bash
# 1. Rename raspy-biometric-backend → backend
mv model/raspy-biometric-backend model/backend

# 2. Rename raspy-main-integrated → deployment  
mv model/raspy-main-integrated model/deployment

# 3. Verify
ls -la model/  # Should show: acquisition/, backend/, deployment/, etc.

# 4. Test imports (if any external scripts reference these)
python model/backend/api_server.py  # Test import
python model/deployment/main_integrated.py  # Test import
```

### Step 6: Update Documentation (15 min)
```bash
# 1. Update README.md - Fix model structure references
# 2. Update SYSTEM_DOCUMENTATION.md - Fix path references
# 3. Create model/README.md - New pipeline overview
# 4. Update model/acquisition/README.md - Add overview
# 5. Fix any broken links in documentation
```

### Step 7: Test Complete Build (10 min)
```bash
# 1. Clean and reinstall
rm -rf node_modules dist dist-electron
npm install

# 2. Test development
npm run dev  # Run dev server (Ctrl+C to stop)

# 3. Test build
npm run build  # Full build with Python bundling
npm run build:bundled  # Bundled with Python runtime (if applicable)

# 4. Test Electron
npm run serve  # Launch desktop app

# 5. Verify embedded resources
# Check that embedding extraction works from bundled path
```

### Step 8: Final Verification (10 min)
```bash
# 1. Verify all Python scripts
python model/acquisition/embedding_extraction/main.py  # Test extraction
python model/acquisition/face_recognition_test/recognition.py  # Test recognition
python model/backend/api_server.py  # Test backend startup
python model/deployment/main_integrated.py  # Test deployment startup

# 2. Verify git status
git status  # Should show moved/renamed files
git log --oneline  # Should show refactor commits

# 3. Create comprehensive README
# Document new structure, installation, deployment
```

### Step 9: Commit Final Changes
```bash
# 1. Add all changes
git add .

# 2. Create descriptive commit
git commit -m "refactor: reorganize model folder structure
- Move embedding_extractor to model/acquisition/embedding_extraction
- Rename raspy-biometric-backend to model/backend
- Rename raspy-main-integrated to model/deployment
- Update all path references in package.json and api.ts
- Update documentation to reflect new structure"

# 3. Push to feature branch
git push origin refactor/reorganize
```

---

## ⚠️ PRE-EXECUTION CHECKLIST

Before running ANY changes, verify:

- [ ] Repository backed up (create new branch)
- [ ] Current build works: `npm run build` ✅
- [ ] All Python scripts run: `python model/.../main.py` ✅
- [ ] Documentation read and understood
- [ ] Have tested the steps on a copy (optional but recommended)
- [ ] Ready to invest ~1 hour on refactoring
- [ ] Team members notified of upcoming refactor

---

## 📊 SUMMARY TABLE

| Aspect | Finding | Action | Risk |
|--------|---------|--------|------|
| Duplicate embedding_extractor | 2 versions, 1 incomplete | Delete model/acq version | LOW |
| Path references in api.ts | Hardcoded 'embedding_extractor' | Update if moving to model/ | MEDIUM |
| Package.json build config | Wrong path reference | Fix path | MEDIUM |
| Python relative imports | All local (good) | Minimal changes | LOW |
| Raspberry Pi systems | raspy-* naming confusing | Rename to backend/deployment | LOW |
| Web app structure | Already optimal | No changes | NONE |
| Documentation | Outdated, scattered | Consolidate & update | MEDIUM |
| Empty folders | training/, inference/ | Keep as placeholders | NONE |

---

## 🎯 KESIMPULAN AUDIT

### ✅ Findings

1. **Duplikasi Kritis:** Folder `model/acquisition/embedding_extractor/` adalah incomplete duplicate dari root `embedding_extractor/`
   - Root version: 100% complete, actively used
   - Model version: 50% complete, unused
   - **Rekomendasi:** Delete model version

2. **Path References:** 
   - `api.ts` hardcodes `'embedding_extractor'` path
   - `package.json` references wrong location
   - **Rekomendasi:** Update both files

3. **Struktur Model:**
   - Disorganized naming (raspy-*, ambiguous names)
   - **Rekomendasi:** Rename to acquisition, training, inference, backend, deployment

4. **Web App:**
   - Already well-structured
   - **Rekomendasi:** Do NOT change

5. **Documentation:**
   - Scattered across root
   - **Rekomendasi:** Consolidate in docs/ folder

### 📊 Estimated Effort

| Phase | Task | Duration | Difficulty |
|-------|------|----------|-----------|
| 1 | Delete duplicate folder | 5 min | Very Easy |
| 2 | Move/rename folders | 15 min | Easy |
| 3 | Update code references | 15 min | Easy |
| 4 | Update documentation | 30 min | Medium |
| 5 | Testing & verification | 30 min | Medium |
| **TOTAL** | | **~1.5 hours** | **Easy-Medium** |

---

## 📋 NEXT STEPS

**WAIT FOR APPROVAL** before proceeding.

Once approved, review and execute:
1. [Refactor Plan Document](./REFACTOR_PLAN.md) (to be created)
2. Step-by-step migration guide
3. Testing checklist
4. Rollback procedures (if needed)

**Questions or concerns?** Review relevant sections in this audit report.

---

**End of Audit Report**  
**Status:** Ready for Review & Approval  
**Action Required:** User approval before execution
