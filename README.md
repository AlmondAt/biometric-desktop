# 🎭 Biometric Desktop - Enrollment & Monitoring App

Desktop application untuk enrollment wajah dan fingerprint dengan monitoring real-time.
Built dengan: **Electron + React + Express + Python ML + Arduino**

## 📋 Struktur Project

\`\`\`
biometric-desktop/
├── web_app/                    # Desktop Application (React + Electron)
│   ├── src/                   # React components
│   ├── electron/              # Electron main process
│   ├── package.json
│   └── tsconfig.json
├── model/                      # ML Pipeline
│   ├── acquisition/
│   │   ├── embedding_extractor/    # Face embedding extraction
│   │   └── face_recognition_test/  # Recognition testing
│   ├── training/              # Model training (future)
│   ├── inference/             # Inference scripts (future)
│   ├── raspy-biometric-backend/    # Raspberry Pi API server
│   └── raspy-main-integrated/      # Integrated Raspberry Pi system
├── docs/                       # Documentation
├── scripts/                    # Build & utility scripts
├── package.json               # Node dependencies
├── tsconfig.json              # TypeScript config
└── README.md                  # This file
\`\`\`

## 🚀 Quick Start

### 1. Desktop App (React + Electron)
\`\`\`bash
# Install dependencies
npm install

# Development
npm run dev

# Build
npm run build

# Build with Python runtime
npm run build:bundled
\`\`\`

### 2. ML Model Setup
\`\`\`bash
# Embedding Extractor
cd model/acquisition/embedding_extractor
pip install -r requirements.txt
python main.py

# Face Recognition Test
cd model/acquisition/face_recognition_test
python recognition.py
\`\`\`

### 3. Raspberry Pi Backend
\`\`\`bash
cd model/raspy-biometric-backend
pip install -r requirements.txt
python api_server.py
\`\`\`

## 📁 Folder Details

### \`web_app/\`
- **src/** - React components (App.tsx, EnrollmentView, SetupWizard, dll)
- **electron/** - Electron main process & IPC handlers
- Main entry: npm run dev

### \`model/acquisition/\`
- **embedding_extractor/** - Extract face embeddings menggunakan FaceNet + MTCNN
- **face_recognition_test/** - Test recognition dengan embeddings yang sudah di-extract

### \`model/raspy-*\`
- **raspy-biometric-backend/** - Flask API server untuk Raspy
- **raspy-main-integrated/** - Integrated system dengan Arduino, fingerprint, dll

## 🔧 Tech Stack

- **Frontend:** React 18, TypeScript, Vite
- **Desktop:** Electron 30
- **Backend:** Express, Flask (Python)
- **ML:** PyTorch, FaceNet, MTCNN
- **Database:** SQLite (Raspy), SQL.js (Desktop)
- **Hardware:** Arduino, Fingerprint sensor, Raspberry Pi 5

## 📚 Documentation

- Lihat \`docs/\` untuk dokumentasi lengkap
- \`model/acquisition/embedding_extractor/README.md\` - Embedding extraction guide
- \`model/raspy-biometric-backend/README.md\` - Raspy setup guide

## 🤝 Contributing

1. Create branch dari \`main\`
2. Make changes
3. Test locally
4. Create PR

## 📝 License

MIT License

---

**Ready to enroll faces? Let's go! 🎭**
