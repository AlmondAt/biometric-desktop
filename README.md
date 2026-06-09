# 🎭 Biometric Lab Access Control System

Sistem biometric terintegrasi untuk kontrol akses lab dan manajemen attendance menggunakan fingerprint dan face recognition. Terdiri dari aplikasi desktop (Electron + React), ML pipeline (Python FaceNet/MTCNN), dan sistem Raspberry Pi dengan integrasi Google Sheets.

**Status:** Production Ready v1.0  
**Last Updated:** June 2026  
**Built dengan:** Electron + React + Express + Python ML + Arduino + Raspberry Pi 5

---

## 🎯 Quick Access

- **Desktop App Users:** [TUTORIAL_PENGGUNA.md](TUTORIAL_PENGGUNA.md)
- **Technical Setup:** [TUTORIAL_TEKNISI.md](TUTORIAL_TEKNISI.md) | [QUICK_START.md](QUICK_START.md)
- **Google Sheets Setup:** [model/attendance/docs/APPS_SCRIPT_SETUP.md](model/attendance/docs/APPS_SCRIPT_SETUP.md)
- **System Flow Diagrams:** [model/attendance/docs/ATTENDANCE_FLOW.md](model/attendance/docs/ATTENDANCE_FLOW.md)
- **Raspberry Pi:** [model/raspy-main-integrated/README.md](model/raspy-main-integrated/README.md)

---

## 📋 Complete Repository Structure

```
biometric-desktop/
│
├── 📱 web_app/                         # Desktop Application (Electron + React)
│   ├── src/                            # React UI Components
│   │   ├── App.tsx                     # Main app container
│   │   ├── EnrollmentView.tsx          # Face/fingerprint enrollment UI
│   │   ├── SetupWizard.tsx             # Initial system setup
│   │   ├── index.css                   # Styling
│   │   └── main.tsx                    # Entry point
│   │
│   ├── electron/                       # Electron Main Process & IPC
│   │   ├── main.ts                     # Window & menu management
│   │   ├── preload.ts                  # IPC bridge to renderer
│   │   ├── api.ts                      # Express backend (:3001)
│   │   └── database.ts                 # SQLite database layer
│   │
│   ├── package.json                    # Node dependencies & build scripts
│   ├── tsconfig.json                   # TypeScript configuration
│   └── vite.config.ts                  # Vite bundler config
│
├── 🤖 embedding_extractor/             # ⭐ Core Face Embedding ML Pipeline (ROOT)
│   ├── main.py                         # Extract embeddings from photos directory
│   ├── training_api.py                 # HTTP API called by desktop app
│   ├── embedding_store.py              # Manage embedding keys
│   ├── facenet_utils.py                # FaceNet model wrapper
│   ├── mtcnn_utils.py                  # MTCNN face detection
│   ├── data_augmentation.py            # Image augmentation for training
│   ├── config.py                       # ML config (paths, thresholds)
│   ├── requirements.txt                # Python dependencies
│   ├── README.md                       # ML pipeline documentation
│   └── tests/                          # Unit tests for ML pipeline
│
├── 🏗️ model/                           # Raspberry Pi & Backend Systems
│   │
│   ├── attendance/                     # 📊 ATTENDANCE & GOOGLE SHEETS INTEGRATION
│   │   ├── README.md                   # Module overview
│   │   ├── AppsScript/                 # Google Apps Script deployment
│   │   ├── spreadsheet-template/       # Google Sheets templates
│   │   │   ├── Attendance_Template.csv # Sample data
│   │   │   └── Template_Instructions.md
│   │   │
│   │   └── docs/                       # Complete documentation
│   │       ├── SPREADSHEET_STRUCTURE.md    # Data schema & mapping
│   │       ├── APPS_SCRIPT_SETUP.md       # Google Sheets setup guide
│   │       └── ATTENDANCE_FLOW.md         # Complete system flow with diagrams
│   │
│   ├── raspy-main-integrated/          # 🎯 MAIN SYSTEM (Raspberry Pi)
│   │   ├── main_integrated.py          # System state machine & main loop
│   │   ├── config.example.yaml         # Configuration template
│   │   ├── modules/
│   │   │   ├── absensi_utils.py        # Google Sheets upload + CSV fallback
│   │   │   ├── biometric.py            # Biometric verification wrapper
│   │   │   ├── embedded_api.py         # Internal HTTP server
│   │   │   ├── logger.py               # Event logging
│   │   │   └── serial_nanonano.py      # Arduino serial communication
│   │   │
│   │   ├── face/                       # Face recognition module
│   │   │   ├── capture_face.py         # Capture from camera
│   │   │   ├── arcface_utils.py        # ArcFace embeddings (alternative)
│   │   │   ├── head_pose.py            # Head pose detection
│   │   │   ├── manage_faces.py         # Face management
│   │   │   └── mtcnn_utils.py          # MTCNN detection
│   │   │
│   │   ├── arduino/                    # Arduino Nano firmware
│   │   │   └── arduino_firmware.ino    # Fingerprint & door control
│   │   │
│   │   ├── config.example.yaml         # System configuration
│   │   ├── requirements.txt            # Python dependencies
│   │   ├── QUICKSTART.md               # Setup guide
│   │   └── README.md                   # System documentation
│   │
│   ├── acquisition/                    # Face Data Acquisition (for training)
│   │   ├── embedding_extractor/        # Deprecated - use root version
│   │   └── face_recognition_test/      # Face recognition testing
│   │       ├── recognition.py          # Test recognition against embeddings
│   │       ├── video_recognition.py    # Real-time camera test
│   │       └── config.py               # Test configuration
│   │
│   ├── raspy-biometric-backend/        # Raspberry Pi API Server (Flask)
│   ├── training/                       # Model Training (Future)
│   └── inference/                      # Inference Scripts (Future)
│
├── 📚 docs/                            # Project Documentation
│   ├── SYSTEM_DOCUMENTATION.md         # System architecture
│   ├── INTEGRATION_GUIDE.md            # Integration instructions
│   ├── ALUR_APLIKASI_DETAIL.md         # Detailed application flow
│   └── [other documentation files]
│
├── 📦 scripts/                         # Build & Utility Scripts
│   └── build-python-runtime.ps1        # Build bundled Python for distribution
│
├── Root Documentation
│   ├── README.md                       # This file (Overview & Setup)
│   ├── QUICK_START.md                  # Quick start guide
│   ├── PRE_GITHUB_CHECKLIST.md         # Before pushing to GitHub
│   ├── TUTORIAL_PENGGUNA.md            # User tutorial (Indonesian)
│   ├── TUTORIAL_TEKNISI.md             # Technical tutorial (Indonesian)
│   ├── SYSTEM_DOCUMENTATION.md         # System architecture details
│   └── [other documentation files]
│
└── Configuration Files
    ├── package.json                    # Node.js main project config
    ├── tsconfig.json                   # TypeScript configuration
    ├── vite.config.ts                  # Vite bundler config
    └── electron-builder.bundled.json   # Electron build config
```

---

## 🎯 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│          BIOMETRIC LAB ACCESS CONTROL SYSTEM                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  TIER 1: Desktop Application (Windows/Mac/Linux)           │
│  ├─ React UI for enrollment & monitoring                   │
│  └─ Electron main process spawning Express backend         │
│           ↓                                                │
│  TIER 2: Backend Services (Express :3001)                 │
│  ├─ REST API endpoints                                     │
│  ├─ Python ML subprocess (training_api.py)               │
│  └─ SQLite database (user profiles)                        │
│           ↓                                                │
│  TIER 3: ML Pipeline (FaceNet + MTCNN)                    │
│  ├─ Face embedding extraction (512-dim vectors)           │
│  ├─ Data augmentation                                      │
│  └─ embeddings.pkl storage                                │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  TIER 4: Raspberry Pi System (Lab Access Station)         │
│  ├─ Touch Sensor → LCD Menu Display                       │
│  ├─ Fingerprint Verification (AS608 sensor)               │
│  ├─ Face Recognition (RPi camera + embeddings)            │
│  ├─ Attendance Form (Job/Domain/Shift selection)          │
│  ├─ Arduino Nano (relay control, serial comm)             │
│  └─ Magnetic Lock Door Control                            │
│           ↓                                                │
│  TIER 5: Cloud Services                                   │
│  ├─ Google Sheets (primary attendance database)            │
│  ├─ Google Apps Script (serverless webhook)               │
│  └─ CSV Fallback (logs/absensi_pending.csv)              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔐 Authentication Flows

### Complete Attendance Flow (Registered User)

```
[USER TOUCHES SENSOR]
         ↓
[LCD: Menu Options]  ← User selects "Attendance"
         ↓
[FINGERPRINT VERIFICATION] (15 sec timeout)
├─ Sensor captures fingerprint
├─ Match in database?
│  ├─ YES → Continue
│  └─ NO → UNREGISTERED FLOW
         ↓
[FACE RECOGNITION] (45 sec timeout)
├─ Capture 4 frames from camera
├─ MTCNN detection + FaceNet embedding (512-dim)
├─ Cosine similarity vs stored embedding
├─ Match found (≥0.8 threshold)?
│  ├─ YES → VERIFIED ✓
│  └─ NO → UNREGISTERED FLOW
         ↓
[JOB SELECTION] (from config)
├─ Display: "1. PS Muro  2. Dasar Menengah  3. Lanjut"
└─ User input via keypad
         ↓
[DOMAIN SELECTION] (from config)
├─ Display: "A. Lab Depok  B. Kalimalang  C. Karawaci"
└─ User input via keypad
         ↓
[SHIFT INPUT] (5 shifts A-E, binary 1/0)
├─ Display each shift name
├─ User input: 1 (working) or 0 (not working)
└─ Store selections
         ↓
[CONFIRMATION]
├─ Display: Name, Job, Domain, Selected Shifts
├─ Ask: "1. Confirm  2. Cancel"
└─ IF Cancel → Return to IDLE
         ↓ (IF Confirm)
[UPLOAD TO GOOGLE SHEETS]
├─ Build JSON payload
├─ HTTP POST to Apps Script
├─ Success? → Store in Google Sheets
└─ Failure? → Save to CSV, retry later
         ↓
[SUCCESS DISPLAY]
├─ LCD: "✓ Terima kasih!"
├─ Activate door lock (3 seconds)
└─ Return to IDLE
```

### Unregistered User Flow

```
[FINGERPRINT/FACE NOT FOUND]
         ↓
[CAPTURE PHOTO]
├─ Save to: logs/unknown_faces/[timestamp].jpg
└─ Store photo path in record
         ↓
[RECORD AS UNREGISTERED]
├─ User ID: 999
├─ Name: "Unknown User"
├─ Status: "Unregistered"
├─ Method: "biometrik"
└─ Photo: [path from capture]
         ↓
[UPLOAD TO GOOGLE SHEETS]
├─ Mark status as "Unregistered"
├─ Admin notified (optional email)
└─ Data available for manual review
         ↓
[ACCESS DENIED]
├─ LCD: "⚠ User tidak dikenali"
├─ No door unlock
└─ Log for security review
```

---

## 📊 Attendance & Google Sheets Integration

**Module Location:** `model/attendance/`

### Quick Setup

```bash
# 1. Create Google Sheet
#    → https://sheets.google.com
#    → Name: "Biometric Lab Attendance"
#    → Create sheet named "Attendance"

# 2. Deploy Google Apps Script
#    → Tools → Script editor
#    → Copy code from: model/attendance/docs/APPS_SCRIPT_SETUP.md
#    → Deploy → New Deployment → Web app

# 3. Copy Web App URL and update Raspberry Pi config.yaml
#    google_sheets:
#      web_app_url: "https://script.google.com/macros/d/[ID]/usercontent"
#      retry_interval: 300
#      max_retries: 3

# 4. System automatically uploads attendance
```

### Data Storage

| Storage | Purpose | Failover |
|---------|---------|----------|
| **Google Sheets** | Primary attendance database (real-time, centralized) | - |
| **CSV (pending)** | Failed submissions queue | Retries when online |
| **SQLite** | User profiles & biometrics | Local fallback |

### Key Documentation

- [model/attendance/README.md](model/attendance/README.md) - Module overview
- [model/attendance/docs/APPS_SCRIPT_SETUP.md](model/attendance/docs/APPS_SCRIPT_SETUP.md) - Complete Google Sheets setup
- [model/attendance/docs/SPREADSHEET_STRUCTURE.md](model/attendance/docs/SPREADSHEET_STRUCTURE.md) - Data schema & columns
- [model/attendance/docs/ATTENDANCE_FLOW.md](model/attendance/docs/ATTENDANCE_FLOW.md) - State machine diagrams & flow

---

## 🌐 Raspberry Pi Configuration

### Network Settings

```yaml
WiFi SSID: almond
WiFi Password: 123456789

SSH Access: ssh pi@raspberrypi.local
SSH Password: raspberry
```

### Running the System

**Main command to start:**

```bash
cd ~/Skripsi/lab
python model/raspy-main-integrated/main_integrated.py
```

**System startup:**
1. Loads config.yaml
2. Initializes sensors (fingerprint, camera, LCD)
3. Displays splash screen
4. Waits for user touch
5. Processes attendance flow

### System Configuration (`config.yaml`)

```yaml
serial:
  port: /dev/ttyUSB0          # Arduino serial port
  baudrate: 9600

camera:
  width: 640
  height: 480
  framerate: 30

fingerprint:
  timeout: 15                 # seconds
  threshold: 50               # match threshold

face:
  timeout: 45                 # seconds
  threshold: 0.8              # cosine similarity

google_sheets:
  web_app_url: ""            # Fill with deployed Apps Script URL
  retry_interval: 300        # 5 minutes
  max_retries: 3

job_codes:
  "1": "PS Muro"
  "2": "Dasar Menengah"
  "3": "Lanjut"

domain_codes:
  "A": "Lab Depok"
  "B": "Lab Kalimalang"
  "C": "Lab Karawaci"
```

### Hardware Connections

```
Raspberry Pi GPIO:
├─ GPIO17 → Relay (Magnetic Lock Control)
├─ GPIO22 → Door Sensor (feedback input)
├─ GPIO27 → Emergency Unlock Button
└─ UART (GPIO14/15) → Arduino Nano (serial)

Arduino Nano:
├─ D2 → Fingerprint Sensor TX
├─ D3 → Fingerprint Sensor RX
├─ D4 → Relay Control Output
└─ GND → Common Ground
```

---

## 🚀 Quick Start

### For Desktop Application Users

```bash
# 1. Install dependencies
npm install

# 2. Start development mode (hot reload)
npm run dev

# 3. Open application (http://localhost:5173)

# 4. Build for production
npm run build
```

**Available scripts:**
- `npm run dev` - Development with hot reload
- `npm run build` - Production build
- `npm run build:bundled` - Build with bundled Python runtime
- `npm run package` - Package as native installer

### For Raspberry Pi Deployment

```bash
# 1. SSH into Raspberry Pi
ssh pi@raspberrypi.local
# Password: raspberry

# 2. Navigate to project
cd ~/Skripsi/lab

# 3. Install dependencies
cd model/raspy-main-integrated
pip install -r requirements.txt

# 4. Configure system
cp config.example.yaml config.yaml
# Edit config.yaml with your Google Sheets URL
# and system-specific settings

# 5. Create log directories
mkdir -p logs/unknown_faces
mkdir -p logs/attendance_photos

# 6. Run the system
python main_integrated.py
```

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, TypeScript, Vite, CSS3 |
| **Desktop** | Electron 30, Node.js |
| **Backend** | Express.js, SQLite, Python |
| **ML** | PyTorch, FaceNet, MTCNN, OpenCV |
| **Hardware** | Raspberry Pi 5, Arduino Nano, AS608 Fingerprint Sensor, RPi Camera |
| **Cloud** | Google Sheets, Google Apps Script |

---

## 📚 Complete Documentation

| Document | Purpose |
|----------|---------|
| [TUTORIAL_PENGGUNA.md](TUTORIAL_PENGGUNA.md) | User operation guide (Indonesian) |
| [TUTORIAL_TEKNISI.md](TUTORIAL_TEKNISI.md) | Technical setup guide (Indonesian) |
| [QUICK_START.md](QUICK_START.md) | Quick setup instructions |
| [SYSTEM_DOCUMENTATION.md](docs/SYSTEM_DOCUMENTATION.md) | Detailed system architecture |
| [INTEGRATION_GUIDE.md](docs/INTEGRATION_GUIDE.md) | Integration instructions |
| [model/attendance/README.md](model/attendance/README.md) | Attendance module overview |
| [model/attendance/docs/APPS_SCRIPT_SETUP.md](model/attendance/docs/APPS_SCRIPT_SETUP.md) | Google Apps Script deployment |
| [model/attendance/docs/SPREADSHEET_STRUCTURE.md](model/attendance/docs/SPREADSHEET_STRUCTURE.md) | Data schema & mapping |
| [model/attendance/docs/ATTENDANCE_FLOW.md](model/attendance/docs/ATTENDANCE_FLOW.md) | Complete flow diagrams |
| [model/raspy-main-integrated/README.md](model/raspy-main-integrated/README.md) | Raspberry Pi system guide |
| [embedding_extractor/README.md](embedding_extractor/README.md) | ML pipeline documentation |

---

## 🧪 Development

### Desktop App
```bash
npm run dev              # Hot reload development
npm run build            # Production build
npm run test             # Run tests (if configured)
```

### Raspberry Pi
```bash
# SSH to Pi
ssh pi@raspberrypi.local

# Run with verbose logging
cd ~/Skripsi/lab
python -u model/raspy-main-integrated/main_integrated.py 2>&1 | tee logs/debug.log

# Monitor attendance logs
tail -f logs/access.log

# Check system events
tail -f logs/events.log
```

---

## 🐛 Troubleshooting

### Desktop App

**Backend not starting:**
```bash
netstat -an | grep 3001          # Check port availability
lsof -ti:3001 | xargs kill -9    # Kill existing process
```

**Face embedding fails:**
```bash
python --version                 # Verify Python installed
pip list | grep facenet          # Check ML dependencies
```

### Raspberry Pi

**Fingerprint sensor issue:**
```bash
ls -la /dev/ttyUSB*              # Check serial connection
cat config.yaml | grep serial    # Verify configuration
```

**Google Sheets upload fails:**
```bash
ping google.com                  # Check network
cat logs/absensi_pending.csv     # Check pending records
curl [YOUR_APPS_SCRIPT_URL]      # Test manually
```

**Camera not working:**
```bash
vcgencmd get_camera              # Check camera status
raspi-config                     # Enable camera
libcamera-hello --duration 2000  # Test camera
```

---

## 🚀 Next Steps

1. **Setup**: Follow [QUICK_START.md](QUICK_START.md) or [TUTORIAL_TEKNISI.md](TUTORIAL_TEKNISI.md)
2. **Attendance**: Follow [model/attendance/docs/APPS_SCRIPT_SETUP.md](model/attendance/docs/APPS_SCRIPT_SETUP.md)
3. **Raspberry Pi**: Follow [model/raspy-main-integrated/README.md](model/raspy-main-integrated/README.md)
4. **Testing**: Test on actual hardware before production deployment

---

## 📝 License

MIT License

---

**Ready to enroll faces and manage attendance? Let's go! 🎭**

**Last Updated:** June 2026  
**System Version:** v1.0  
**Status:** Production Ready
