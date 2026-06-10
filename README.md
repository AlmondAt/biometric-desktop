# 🎭 Biometric Lab Access Control System

Sistem biometric terintegrasi untuk kontrol akses lab dan manajemen attendance menggunakan fingerprint dan face recognition. Terdiri dari aplikasi desktop (Electron + React), ML pipeline (Python FaceNet/MTCNN), dan sistem Raspberry Pi dengan integrasi Google Sheets.

**Status:** Production Ready v1.0  
**Last Updated:** June 2026  
**Built dengan:** Electron + React + Express + Python ML + Arduino + Raspberry Pi 5

---

## 🎯 Quick Access (Pilih Berdasarkan Kebutuhan)

### 👤 Pengguna Aplikasi Desktop
- **📖 User Tutorial:** [docs/pengguna/TUTORIAL_PENGGUNA.md](docs/pengguna/TUTORIAL_PENGGUNA.md) - Panduan lengkap untuk menggunakan aplikasi

### 🔧 Setup & Teknis
- **⚡ Quick Start:** [docs/teknisi/QUICK_START.md](docs/teknisi/QUICK_START.md) - Setup cepat untuk developer
- **📘 Technical Tutorial:** [docs/teknisi/TUTORIAL_TEKNISI.md](docs/teknisi/TUTORIAL_TEKNISI.md) - Setup lengkap semua komponen
- **🏗️ System Documentation:** [docs/teknisi/SYSTEM_DOCUMENTATION.md](docs/teknisi/SYSTEM_DOCUMENTATION.md) - Arsitektur sistem detail
- **🔗 Integration Guide:** [docs/teknisi/INTEGRATION_GUIDE.md](docs/teknisi/INTEGRATION_GUIDE.md) - Panduan integrasi

### 🎯 Modul Spesifik
- **Face Recognition Testing:** [biometric/face_recognition_test/README.md](biometric/face_recognition_test/README.md)
- **ML Pipeline:** [biometric/embedding_extractor/README.md](biometric/embedding_extractor/README.md)
- **Raspberry Pi Main System:** [raspberry_pi/raspy-main-integrated/README.md](raspberry_pi/raspy-main-integrated/README.md)
- **Attendance & Google Sheets:** [attendance/docs/APPS_SCRIPT_SETUP.md](attendance/docs/APPS_SCRIPT_SETUP.md)

---

## � Struktur Repository

```
biometric-desktop/
│
├── 📱 web_app/                         # Desktop Application (Electron + React)
│   ├── src/                            # React UI Components
│   │   ├── App.tsx                     # Main app container
│   │   ├── EnrollmentView.tsx          # Face/fingerprint enrollment UI
│   │   ├── SetupWizard.tsx             # Initial system setup
│   │   └── main.tsx                    # Entry point
│   │
│   ├── electron/                       # Electron Main Process & IPC
│   │   ├── main.ts                     # Window & menu management
│   │   ├── preload.ts                  # IPC bridge to renderer
│   │   ├── api.ts                      # Express backend (:3001)
│   │   └── database.ts                 # SQLite database layer
│   │
│   ├── index.html                      # HTML template
│   ├── package.json                    # Node dependencies
│   ├── tsconfig.json                   # TypeScript config
│   └── vite.config.ts                  # Vite bundler config
│
├── 🤖 biometric/                       # ⭐ ML PIPELINE & FACE RECOGNITION
│   │
│   ├── embedding_extractor/            # Face Embedding ML Pipeline
│   │   ├── main.py                     # Extract embeddings from photos
│   │   ├── training_api.py             # HTTP API (called by desktop app)
│   │   ├── embedding_store.py          # Manage embedding storage
│   │   ├── facenet_utils.py            # FaceNet model wrapper
│   │   ├── mtcnn_utils.py              # MTCNN face detection
│   │   ├── data_augmentation.py        # Image augmentation
│   │   ├── config.py                   # ML configuration
│   │   ├── requirements.txt            # Python dependencies
│   │   └── README.md                   # Pipeline documentation
│   │
│   └── face_recognition_test/          # Face Recognition Testing Module
│       ├── recognition.py              # Test recognition against embeddings
│       ├── video_recognition.py        # Real-time camera testing
│       ├── config.py                   # Test configuration
│       └── README.md                   # Testing guide
│
├── 🍓 raspberry_pi/                    # RASPBERRY PI & EMBEDDED SYSTEMS
│   │
│   ├── raspy-main-integrated/          # Main System (State Machine)
│   │   ├── main_integrated.py          # System state machine & main loop
│   │   ├── config.example.yaml         # Configuration template
│   │   │
│   │   ├── modules/                    # Core modules
│   │   │   ├── absensi_utils.py        # Google Sheets + CSV upload
│   │   │   ├── biometric.py            # Fingerprint + face verification
│   │   │   ├── embedded_api.py         # HTTP server
│   │   │   ├── logger.py               # Event logging
│   │   │   └── serial_nanonano.py      # Arduino serial communication
│   │   │
│   │   ├── face/                       # Face recognition module
│   │   │   ├── capture_face.py         # Camera capture
│   │   │   ├── arcface_utils.py        # ArcFace embeddings
│   │   │   ├── head_pose.py            # Head pose detection
│   │   │   ├── manage_faces.py         # Face management
│   │   │   └── mtcnn_utils.py          # MTCNN detection
│   │   │
│   │   ├── arduino/                    # Arduino firmware
│   │   │   └── arduino_firmware.ino    # Fingerprint & door control
│   │   │
│   │   ├── requirements.txt            # Python dependencies
│   │   ├── QUICKSTART.md               # Raspberry Pi setup
│   │   └── README.md                   # System documentation
│   │
│   └── raspy-biometric-backend/        # Biometric Backend API Server
│       ├── api_server.py               # REST API server
│       ├── config.yaml                 # Configuration
│       ├── modules/
│       │   ├── db_manager.py           # Database management
│       │   └── face_matcher.py         # Face matching logic
│       ├── tools/
│       │   ├── enroll_face.py          # Face enrollment tool
│       │   ├── enroll_fingerprint.py   # Fingerprint enrollment
│       │   └── list_users.py           # List users utility
│       ├── requirements.txt            # Dependencies
│       ├── QUICKSTART.md               # Setup guide
│       └── README.md                   # API documentation
│
├── 📊 attendance/                      # ATTENDANCE & GOOGLE SHEETS
│   ├── AppsScript/                     # Google Apps Script code
│   │   └── [Google Apps Script files]
│   │
│   ├── spreadsheet-template/           # Google Sheets templates
│   │   ├── Attendance_Template.csv     # Sample CSV
│   │   └── Template_Instructions.md
│   │
│   └── docs/                           # Complete documentation
│       ├── SPREADSHEET_STRUCTURE.md    # Data schema & mapping
│       ├── APPS_SCRIPT_SETUP.md        # Google Sheets setup
│       └── ATTENDANCE_FLOW.md          # System flow with diagrams
│
├── 📚 docs/                            # PROJECT DOCUMENTATION
│   ├── teknisi/                        # Technical documentation
│   │   ├── SYSTEM_DOCUMENTATION.md     # Architecture & systems
│   │   ├── QUICK_START.md              # Quick start guide
│   │   ├── TUTORIAL_TEKNISI.md         # Full technical tutorial
│   │   ├── INTEGRATION_GUIDE.md        # Integration instructions
│   │   ├── ALUR_APLIKASI_DETAIL.md    # Detailed application flow
│   │   └── ADD_USER_WITH_ID_README.md  # User ID fixing utility
│   │
│   └── pengguna/                       # User documentation
│       └── TUTORIAL_PENGGUNA.md        # End-user tutorial
│
├── 📦 scripts/                         # BUILD & UTILITIES
│   ├── build-python-runtime.ps1        # Build Python bundled runtime
│   └── add-user-with-id.js             # User ID management utility
│
├── Configuration & Build Files
│   ├── package.json                    # Node.js dependencies & scripts
│   ├── package-lock.json               # Dependency lock file
│   ├── tsconfig.json                   # TypeScript configuration
│   ├── vite.config.ts                  # Vite bundler config
│   ├── electron-builder.bundled.json   # Electron build config
│   └── .env.example                    # Environment template
│
└── Version Control
    └── .gitignore                      # Git ignore rules
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
source /home/pi/Skripsi/.venv39/bin/activate
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
# Serial Communication
serial:
  arduino_port: "/dev/ttyUSB0"  # Arduino Nano serial port
  arduino_baudrate: 115200
  fingerprint_port: "/dev/ttyUSB1"  # AS608/R307 sensor
  fingerprint_baudrate: 57600
  timeout: 1.0

# Camera Configuration
camera:
  devices: ['/dev/video0', 0]  # OpenCV devices to try
  width: 640
  height: 480
  use_rpicam: true  # use rpicam-jpeg CLI fallback when OpenCV fails
  rpicam_timeout: 1  # seconds for rpicam-jpeg to capture (each capture ~10s)

# Biometric Settings
biometric:
  fingerprint_timeout: 15  # seconds (increased from 12 to handle sensor initialization delay)
  face_timeout: 20  # seconds (increased from 8 to accommodate rpicam delays)
  face_threshold: 0.7  # similarity threshold (0.0 - 1.0)
  stable_frames: 1  # number of consistent frames for face verification

# Touch Sensor
touch:
  debounce_ms: 200

# Keypad Input
keypad:
  input_timeout: 20  # seconds per field

# Relay/Door Control
relay:
  open_duration: 10  # seconds
  
# Database Paths
database:
  sqlite_path: "biometrics.db"
  embeddings_path: "database/embeddings.pkl"
  
# Logging
logging:
  log_folder: "logs"
  events_log: "logs/events.log"
  access_log: "logs/access.log"
  pending_csv: "logs/absensi_pending.csv"
  unknown_faces: "logs/unknown_faces"

# Google Sheets Integration
google_sheets:
  web_app_url: "https://script.google.com/macros/s/AKfycbwp_OIwmPKKbUotz-53NPL7f8gt1YJ9Z8n1HpmmtouENlFpzUbDO6lFSjwAuEDF0NTl6w/exec"
  retry_interval: 300  # seconds (5 minutes)
  max_retries: 3

# LCD Display
lcd:
  update_delay: 0.15  # minimum delay between updates (seconds)

# System Timeouts
timeouts:
  splash_duration: 5  # seconds
  message_display: 3  # seconds
  
# Job Codes (for attendance menu)
job_codes:
  "1": "PS Muro"
  "2": "Dasar Menengah"
  "3": "Lanjut"

# Domain Codes (for attendance menu)
domain_codes:
  "A": "Lab Depok"
  "B": "Lab Kalimalang"
  "C": "Lab Karawaci"

```

### Hardware Connections

```text
Arduino Nano
├─ D3    → Relay Module (Magnetic Door Lock)
├─ D4    → Emergency Button (INPUT_PULLUP)
├─ D7    → Touch Sensor (TTP223)
├─ A4    → I2C SDA
├─ A5    → I2C SCL
├─ TX/RX → Raspberry Pi (USB Serial)
└─ GND   → Common Ground

I2C Bus
├─ LCD 20x4 I2C (0x27)
│  ├─ SDA → A4
│  ├─ SCL → A5
│  ├─ VCC → 5V
│  └─ GND → GND
│
└─ Keypad 4x4 + PCF8574 (0x20)
   ├─ SDA → A4
   ├─ SCL → A5
   ├─ VCC → 5V
   └─ GND → GND

Touch Sensor (TTP223)
├─ VCC → 5V
├─ GND → GND
└─ OUT → D7

Emergency Button
├─ One Side  → D4
└─ Other Side → GND

Relay Module
├─ IN  → D3
├─ VCC → 5V
└─ GND → GND

Magnetic Door Lock
├─ Controlled by Relay Module
└─ External Power Supply (12V)

Communication
└─ Raspberry Pi 5 ↔ Arduino Nano
   ├─ USB Serial
   ├─ Baudrate : 115200
   └─ JSON-based Communication Protocol
```
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
