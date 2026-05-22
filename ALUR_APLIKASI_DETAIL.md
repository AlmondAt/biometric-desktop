# 🔍 ALUR APLIKASI BIOMETRIC DESKTOP - PENJELASAN DETAIL

**Last Updated**: May 22, 2026  
**Level**: Ultra Detail (Dari User Action sampai Database)

---

## 📊 Ringkasan Arsitektur Keseluruhan

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER (Admin / CoAdmin)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  BROWSER VIEW   │
                    │  (React + Vite) │
                    └────────┬────────┘
                             │ HTTP (localhost:3001)
                    ┌────────▼────────────────┐
                    │   ELECTRON MAIN         │
                    │  (IPC Bridge)           │
                    └────────┬────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼────┐      ┌────────▼────────┐    ┌─────▼──────┐
   │ Express │      │   SQLite        │    │   Python   │
   │  API    │      │   Database      │    │  Subprocess│
   │ :3001   │      │ (biometrics.db) │    │  Training  │
   └────┬────┘      └─────────────────┘    │  Face      │
        │                                   │ Recognition│
        │                    ┌──────────────┴────────────┘
        │                    │
        │           ┌────────▼────────┐
        │           │  Raspy Backend  │
        │           │  (API Server)   │
        └───────────►│  :5000          │
                    └─────────────────┘
```

---

## 1️⃣ TAHAP STARTUP (Saat Aplikasi Dibuka)

### 1.1 Electron Main Process Start
```javascript
// electron/main.ts
1. BrowserWindow dibuat
2. Electron load index.html (React app)
3. express/api.ts di-spawn sebagai child process
```

**Langkah-langkah:**
```
START → Electron main process
   ├─ createWindow()
   │  └─ Buka jendela dengan React UI
   ├─ startServer() di api.ts
   │  ├─ initializeDatabase() 
   │  │  └─ Load atau create SQLite DB di localStorage
   │  ├─ Seed default data (admin/coadmin login)
   │  └─ Express listen di port 3001
   └─ Ready ✅
```

### 1.2 React App Initialize
```javascript
// src/main.tsx
1. React render App.tsx
2. App.tsx cek apakah user sudah login
3. Tampilkan login screen atau dashboard
```

---

## 2️⃣ LOGIN FLOW (Masuk Aplikasi)

### 2.1 User Masukkan Credentials

```
UI: Login Screen
├─ Input: username = "admin"
├─ Input: password = "admin123"
└─ Click: LOGIN button
   │
   ▼
Frontend (React)
   │
   └─ fetch('http://localhost:3001/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({
          username: 'admin',
          password: 'admin123'
        })
      })
   │
   ▼
Backend Express API (api.ts)
   │
   └─ POST /api/auth/login → verifyLogin()
      │
      ├─ Query SQLite: SELECT * FROM auth_accounts 
      │  WHERE username = 'admin'
      │
      ├─ Hash password yang dikirim:
      │  password_hash = scryptSync('admin123', salt, 64)
      │
      ├─ Bandingkan dengan password_hash di database
      │
      ├─ Jika cocok → return AuthUser object:
      │  {
      │    accountId: 1,
      │    userId: null,
      │    username: 'admin',
      │    fullName: 'System Administrator',
      │    role: 'admin'
      │  }
      │
      └─ Response 200 OK ✅
   │
   ▼
Frontend (React)
   │
   ├─ setState({ authUser, isLoggedIn: true })
   ├─ localStorage.setItem('authUser', JSON.stringify(authUser))
   └─ Redirect to Dashboard
```

### 2.2 Database Query Detail

```sql
-- Database: biometrics.db
-- Table: auth_accounts

SELECT id, user_id, username, password_hash, password_salt, role, full_name_snapshot
FROM auth_accounts
WHERE username = 'admin' AND is_active = 1

-- Result:
┌────┬─────────┬──────────┬──────────────────────┬────────────┬──────┬──────────────────────┐
│ id │ user_id │ username │ password_hash        │ salt       │ role │ full_name_snapshot   │
├────┼─────────┼──────────┼──────────────────────┼────────────┼──────┼──────────────────────┤
│ 1  │ NULL    │ admin    │ a3f9e8c7... (64 hex) │ 8f2c1b9... │ admin│ System Administrator │
└────┴─────────┴──────────┴──────────────────────┴────────────┴──────┴──────────────────────┘
```

---

## 3️⃣ DASHBOARD FLOW (Halaman Utama)

### 3.1 Dashboard Load Data

```
User klik Dashboard → App.tsx component mount
   │
   └─ useEffect → fetch('/api/dashboard')
      │
      ▼
Backend GET /api/dashboard
   │
   ├─ await syncUsersFromRaspy()
   │  ├─ Fetch Raspy API: GET http://localhost:5000/api/users
   │  ├─ Loop setiap user dari Raspy
   │  └─ upsertRemoteUser() → insert/update ke local DB
   │     └─ Query SQLite:
   │        INSERT INTO users (id, full_name, role, source, ...)
   │        VALUES (1, 'John Doe', 'member', 'raspy-sync', ...)
   │
   ├─ await loadUnifiedLogs(20)
   │  ├─ Load dari Raspy: GET http://localhost:5000/api/logs
   │  ├─ Load dari spreadsheet (jika enabled)
   │  ├─ Load dari local DB: SELECT * FROM access_logs
   │  └─ Merge + deduplicate + sort by timestamp DESC
   │
   ├─ await getRaspyStatus()
   │  ├─ Fetch: GET http://localhost:5000/api/health
   │  └─ Return online/offline status
   │
   └─ Response JSON:
      {
        success: true,
        metrics: {
          totalUsers: 45,
          attendanceToday: 23,
          systemStatus: 'online'
        },
        recentActivity: [
          {
            id: 1,
            fullName: 'John Doe',
            method: 'face',
            accessStatus: 'success',
            eventTime: '2026-05-22T14:30:45Z'
          },
          ...
        ],
        systemStatusMessage: 'Online',
        integration: {
          spreadsheetEnabled: false
        }
      }
      │
      ▼
Frontend (React)
   │
   └─ setState({ dashboard: response })
      └─ Display:
         ├─ 📊 Total Users: 45
         ├─ 🔓 Attendance Today: 23
         ├─ 🟢 System Status: ONLINE
         └─ 📋 Recent Activity (8 items)
            ├─ [2026-05-22 14:30] John Doe - Face ✅
            ├─ [2026-05-22 14:25] Jane Smith - Face ✅
            └─ ...
```

---

## 4️⃣ USER MANAGEMENT FLOW

### 4.1 List Users

```
User klik "Data User" → App.tsx route to users tab
   │
   └─ useEffect → fetch('/api/users')
      │
      ▼
Backend GET /api/users
   │
   ├─ await syncUsersFromRaspy()
   │  └─ [sama seperti dashboard]
   │
   └─ Response: { success: true, users: [...] }
      │
      ▼
Frontend
   │
   └─ setState({ users: response.users })
      └─ Display table dengan:
         ├─ ID | Nama | Role | Face | Fingerprint | Source
         ├─ 1  | John Doe | member | ✅ | ❌ | raspy-sync
         ├─ 2  | Jane Smith | admin | ✅ | ✅ | local
         └─ 3  | Bob Johnson | coadmin | ❌ | ❌ | local
```

### 4.2 Tambah User Baru

```
User klik "Tambah User" button → membuka form modal
   │
   ├─ Input: fullName = "Michael Scott"
   ├─ Input: role = "member"
   ├─ Input: username = (kosong - member tidak perlu)
   └─ Click: SUBMIT
      │
      ▼
Frontend
   │
   └─ fetch('/api/users', {
        method: 'POST',
        body: {
          fullName: 'Michael Scott',
          role: 'member'
        }
      })
      │
      ▼
Backend POST /api/users
   │
   ├─ Validasi:
   │  ├─ fullName tidak kosong ✓
   │  ├─ role valid ('member') ✓
   │  └─ Nama tidak ada di DB ✓
   │
   ├─ Query SQLite:
   │  INSERT INTO users (full_name, role, registration_date, updated_at, source)
   │  VALUES ('Michael Scott', 'member', '2026-05-22T14:35:00Z', '2026-05-22T14:35:00Z', 'local')
   │  
   │  Result: id = 4 (auto increment)
   │
   ├─ Create user di Raspy (optional):
   │  POST http://localhost:5000/api/add-user
   │  body: { name: 'Michael Scott', full_name: 'Michael Scott' }
   │
   └─ Response 201 Created:
      {
        success: true,
        user: {
          id: 4,
          displayNo: 4,
          fullName: 'Michael Scott',
          role: 'member',
          username: null,
          faceEnrolled: false,
          fingerprintEnrolled: false,
          source: 'local'
        }
      }
      │
      ▼
Frontend
   │
   ├─ Toast: "✅ User berhasil ditambahkan"
   ├─ Tambah ke state: users.push(newUser)
   └─ Close modal
      └─ Tampilkan user baru di table
```

### 4.3 Edit User

```
User klik "Edit" pada user row → form pre-filled
   │
   ├─ Current: fullName = "Jane Smith", role = "admin"
   ├─ Change: role = "coadmin" (dari admin → coadmin)
   └─ Click: SAVE
      │
      ▼
Frontend
   │
   └─ fetch('/api/users/2', {
        method: 'PUT',
        body: {
          fullName: 'Jane Smith',
          role: 'coadmin',
          username: 'jane_smith',
          password: 'newpass123'
        }
      })
      │
      ▼
Backend PUT /api/users/:id (id=2)
   │
   ├─ Get current user dari DB
   ├─ Validasi full_name unik
   ├─ Update Raspy dulu:
   │  PUT http://localhost:5000/api/users/2
   │  body: { user_id: 2, full_name: 'Jane Smith' }
   │
   ├─ Jika Raspy sukses, update local DB:
   │  UPDATE users SET full_name='Jane Smith', role='coadmin', updated_at=NOW()
   │  WHERE id=2
   │
   ├─ Update auth_accounts (untuk login credentials):
   │  UPDATE auth_accounts SET 
   │    username='jane_smith',
   │    password_hash=HASH('newpass123'),
   │    role='coadmin'
   │  WHERE user_id=2
   │
   └─ Response 200 OK:
      {
        success: true,
        user: { id: 2, fullName: 'Jane Smith', role: 'coadmin', ... },
        remote: { updated: true, message: 'User berhasil diperbarui di Raspy' }
      }
      │
      ▼
Frontend
   │
   ├─ Toast: "✅ User berhasil diperbarui"
   └─ Update state: users[index] = updatedUser
```

### 4.4 Delete User

```
User klik "Delete" dengan konfirmasi → confirm dialog
   │
   ├─ Confirm: "Apakah Anda yakin ingin menghapus Jane Smith?"
   └─ Click: YES
      │
      ▼
Frontend
   │
   └─ fetch('/api/users/2', { method: 'DELETE' })
      │
      ▼
Backend DELETE /api/users/:id (id=2)
   │
   ├─ Get user dari DB dulu
   ├─ Delete dari Raspy dulu:
   │  DELETE http://localhost:5000/api/users/2
   │
   ├─ Jika Raspy sukses & user ada embeddings:
   │  ├─ Run Python script: embedding_store.py delete
   │  │  └─ Remove entry dari embeddings.pkl
   │  └─ Hapus dari access_logs (jika ada)
   │
   ├─ Delete dari local DB:
   │  DELETE FROM users WHERE id=2
   │  DELETE FROM auth_accounts WHERE user_id=2
   │
   └─ Response 200 OK:
      { success: true, remote: { deleted: true, message: '...' } }
      │
      ▼
Frontend
   │
   ├─ Toast: "✅ User berhasil dihapus"
   └─ Remove dari state: users = users.filter(u => u.id !== 2)
```

---

## 5️⃣ ENROLLMENT FLOW (Pendaftaran Wajah + Fingerprint)

### 5.1 Preparation Phase

```
User klik "Pendaftaran User Baru" → Form enrollment
   │
   ├─ Input: fullName = "Robert Langdon"
   ├─ Input: role = "member"
   └─ Click: "Mulai Enrollment"
      │
      ▼
Frontend
   │
   └─ fetch('/api/enrollment/prepare', {
        method: 'POST',
        body: {
          fullName: 'Robert Langdon',
          role: 'member'
        }
      })
      │
      ▼
Backend POST /api/enrollment/prepare
   │
   ├─ Create user di Raspy dulu:
   │  POST http://localhost:5000/api/add-user
   │  body: { name: 'Robert Langdon', full_name: 'Robert Langdon' }
   │  
   │  Response: { id: 100, user_id: 100, ... }
   │
   ├─ Simpan ke pendingEnrollments map (in-memory):
   │  {
   │    userId: 100,
   │    fullName: 'Robert Langdon',
   │    role: 'member',
   │    faceEmbeddingCount: 0
   │  }
   │
   ├─ Send signal ke Raspy (untuk set device mode):
   │  POST http://localhost:5000/api/device/mode
   │  body: {
   │    mode: 'enrollment',
   │    stage: 'start',
   │    userId: 100,
   │    fullName: 'Robert Langdon'
   │  }
   │
   └─ Response 201 Created:
      {
        success: true,
        user: { id: 100, fullName: 'Robert Langdon', ... },
        device: { delivered: true, message: '...' }
      }
      │
      ▼
Frontend
   │
   ├─ setState({ enrollmentMode: 'capture-face', userId: 100 })
   └─ Switch to webcam view untuk capture foto wajah
```

### 5.2 Face Capture Phase

```
Frontend: Tampilkan webcam live view
   │
   ├─ User click "Ambil Foto" → webcamRef.current.getScreenshot()
   ├─ Screenshot → base64 string
   ├─ Add ke photos array (state)
   ├─ Tampilkan preview foto di grid
   └─ Repeat 10+ times sampai "Mulai Training Wajah"
      │
      ▼
Frontend grid display:
   ├─ [Foto 1] [Foto 2] [Foto 3]
   ├─ [Foto 4] [Foto 5] [Foto 6]
   ├─ [Foto 7] [Foto 8] [Foto 9]
   └─ [Foto 10]
```

### 5.3 Face Training Phase

```
User click "Mulai Training Wajah" dengan 10 foto
   │
   └─ fetch('/api/enrollment/face', {
        method: 'POST',
        body: {
          userId: 100,
          photos: [base64_1, base64_2, ..., base64_10],
          skipFingerprint: false  // akan ada fase fingerprint
        }
      })
      │
      ▼
Backend POST /api/enrollment/face
   │
   ├─ Step 1: Prepare payload
   │  ├─ ensureTempDir() → create .temp folder
   │  ├─ Write payload ke file JSON:
   │  │  {
   │  │    "embeddingKey": "Robert Langdon",
   │  │    "userId": 100,
   │  │    "photos": [base64_1, base64_2, ...],
   │  │    "embeddingsPath": "/storage/embeddings.pkl",
   │  │    "replaceExisting": false
   │  │  }
   │  └─ Save ke: .temp/training-<timestamp>-100.json
   │
   ├─ Step 2: Notify Raspy (capture-face mode)
   │  POST http://localhost:5000/api/device/mode
   │  body: {
   │    mode: 'capture-face',
   │    userId: 100,
   │    fullName: 'Robert Langdon'
   │  }
   │
   ├─ Step 3: Spawn Python subprocess
   │  │
   │  └─ spawn('python3', ['embedding_extractor/training_api.py', payloadPath])
   │     │
   │     ▼
   │     Python Script (training_api.py):
   │     │
   │     ├─ Load payload JSON
   │     ├─ Create photos temp folder
   │     ├─ Decode base64 → save ke folder (photo_1.jpg, photo_2.jpg, ...)
   │     │
   │     ├─ Step 3a: MTCNN Detection
   │     │  ├─ For each photo:
   │     │  │  ├─ Load image (photo_1.jpg)
   │     │  │  ├─ mtcnn.detect_faces(image)
   │     │  │  └─ Get bounding boxes (x, y, w, h)
   │     │  │
   │     │  └─ If no face detected:
   │     │     └─ Skip atau error
   │     │
   │     ├─ Step 3b: Face Alignment & Crop
   │     │  ├─ For each detected face:
   │     │  │  ├─ Get landmarks (5 points: eyes, nose, mouth)
   │     │  │  ├─ Align face using landmarks
   │     │  │  └─ Crop to 160×160 pixels
   │     │  │
   │     │  └─ Result: aligned_face_1.jpg, aligned_face_2.jpg, ...
   │     │
   │     ├─ Step 3c: FaceNet Embedding Extraction
   │     │  ├─ Load FaceNet model (pre-trained)
   │     │  ├─ For each aligned face:
   │     │  │  ├─ forward(aligned_face_1.jpg) → 512-dim vector
   │     │  │  └─ embedding_1 = [0.12, -0.34, 0.56, ..., 0.89]
   │     │  │
   │     │  └─ Result: 10 embeddings (512-dim each)
   │     │
   │     ├─ Step 3d: Data Augmentation
   │     │  ├─ For each original photo:
   │     │  │  ├─ Rotate -15°, -10°, 0°, +10°, +15°
   │     │  │  ├─ Brightness adjust ±20%
   │     │  │  ├─ Extract embedding untuk setiap augmented
   │     │  │  └─ Add to total
   │     │  │
   │     │  └─ Total: ~500 embeddings (10 photos × 50 augmentations)
   │     │
   │     ├─ Step 3e: Save to embeddings.pkl
   │     │  ├─ Load existing embeddings.pkl
   │     │  ├─ Add/update entry:
   │     │  │  {
   │     │  │    "Robert Langdon": [
   │     │  │      [0.12, -0.34, 0.56, ...],  // embedding 1
   │     │  │      [0.15, -0.30, 0.52, ...],  // embedding 2
   │     │  │      ...
   │     │  │      [0.18, -0.35, 0.58, ...]   // embedding 500
   │     │  │    ]
   │     │  │  }
   │     │  └─ Save to embeddings.pkl (binary pickle format)
   │     │
   │     └─ Output JSON to stdout:
   │        {
   │          "status": "success",
   │          "total": 500,
   │          "embeddingKey": "Robert Langdon",
   │          "added": 500
   │        }
   │
   ├─ Step 4: Backend read Python output
   │  ├─ Parse stdout
   │  ├─ Extract: total = 500 embeddings
   │  │
   │  └─ Notify Raspy (training-face mode):
   │     POST http://localhost:5000/api/device/mode
   │     body: {
   │       mode: 'training-face',
   │       userId: 100,
   │       fullName: 'Robert Langdon'
   │     }
   │
   ├─ Step 5: Sync embeddings ke Raspy
   │  ├─ Read embeddings.pkl file (binary)
   │  ├─ Encode ke base64
   │  └─ POST http://localhost:5000/api/enroll-face
   │     body: {
   │       user_id: 100,
   │       full_name: 'Robert Langdon',
   │       embeddings_file_base64: '<very long base64 string>'
   │     }
   │
   ├─ Step 6: Update pendingEnrollments
   │  └─ pendingEnrollments[100].faceEmbeddingCount = 500
   │
   └─ Response 200 OK:
      {
        success: true,
        user: { id: 100, fullName: 'Robert Langdon', faceEnrolled: true, ... },
        training: {
          totalEmbeddings: 500,
          output: '[JSON output from Python]'
        },
        nextStep: 'fingerprint'  // atau 'done' jika skipFingerprint=true
      }
      │
      ▼
Frontend
   │
   ├─ setState({ enrollmentStatus: 'face-done' })
   ├─ Toast: "✅ Training berhasil! 500 embeddings"
   └─ Display: "Silahkan lanjut ke fase fingerprint" (jika ada)
```

### 5.4 Fingerprint Enrollment Phase (Optional)

```
User siap untuk scan fingerprint
   │
   └─ fetch('/api/enrollment/fingerprint', {
        method: 'POST',
        body: { userId: 100 }
      })
      │
      ▼
Backend POST /api/enrollment/fingerprint
   │
   ├─ Notify Raspy (scan-fingerprint mode):
   │  POST http://localhost:5000/api/device/mode
   │  body: {
   │    mode: 'scan-fingerprint',
   │    userId: 100,
   │    fullName: 'Robert Langdon'
   │  }
   │
   ├─ [User scan fingerprint di alat Raspy]
   │  └─ Fingerprint device process scan
   │     └─ Raspy mendapat fingerprint ID (misal: 101)
   │
   ├─ Backend enroll fingerprint di Raspy:
   │  POST http://localhost:5000/api/enroll-fingerprint
   │  body: {
   │    user_id: 100,
   │    full_name: 'Robert Langdon'
   │  }
   │
   ├─ Raspy return:
   │  {
   │    fingerprint_id: 101,
   │    message: 'Fingerprint enrolled'
   │  }
   │
   ├─ Backend finalize enrollment:
   │  ├─ Get pending enrollment dari memory
   │  ├─ Create user di local DB:
   │  │  INSERT INTO users (id, full_name, role, registration_date, ...)
   │  │  VALUES (100, 'Robert Langdon', 'member', NOW(), ...)
   │  │
   │  ├─ Mark face enrollment:
   │  │  UPDATE users
   │  │  SET face_embedding_key='Robert Langdon',
   │  │      face_embedding_count=500,
   │  │      face_enrolled=1
   │  │  WHERE id=100
   │  │
   │  ├─ Mark fingerprint enrollment:
   │  │  UPDATE users
   │  │  SET fingerprint_id=101,
   │  │      fingerprint_enrolled=1
   │  │  WHERE id=100
   │  │
   │  └─ Remove dari pendingEnrollments
   │
   ├─ Notify Raspy (idle mode):
   │  POST http://localhost:5000/api/device/mode
   │  body: { mode: 'idle', userId: 100, fullName: 'Robert Langdon' }
   │
   └─ Response 200 OK:
      {
        success: true,
        fingerprintId: 101,
        user: {
          id: 100,
          fullName: 'Robert Langdon',
          faceEnrolled: true,
          fingerprintEnrolled: true,
          faceEmbeddingCount: 500,
          fingerprintId: 101
        }
      }
      │
      ▼
Frontend
   │
   ├─ Toast: "✅ Enrollment berhasil! User siap digunakan."
   └─ Close enrollment modal → back to users list
      └─ User baru tampil di table:
         100 | Robert Langdon | member | ✅ | ✅ | local
```

---

## 6️⃣ RETRAIN FACE FLOW

```
Admin klik tombol "Retrain" pada user row → Confirm dialog
   │
   ├─ Confirm: "Retrain embedding Robert Langdon?"
   └─ Click: YES
      │
      ▼
Frontend → Redirect to enrollment view dengan mode='retrain'
   │
   └─ [sama seperti enrollment, tapi dengan replaceExisting=true]
      │
      ├─ Capture 10+ foto baru
      ├─ POST /api/enrollment/face dengan replaceExisting=true
      │
      └─ Backend Python script:
         ├─ Load existing embeddings.pkl
         ├─ Delete old entry: embeddings["Robert Langdon"] = []
         ├─ Generate 500 new embeddings dari foto baru
         ├─ Update embeddings.pkl
         └─ Response dengan embedding count baru
```

---

## 7️⃣ ACCESS LOGS / ATTENDANCE FLOW

### 7.1 Record Attendance (Dari Raspy)

```
Raspy device detect face/fingerprint
   │
   ├─ Raspy recognize → get userId
   ├─ Raspy create log entry
   └─ POST http://localhost:3001/api/attendance
      {
        userId: 100,
        fullName: 'Robert Langdon',
        method: 'face',
        accessStatus: 'success',
        similarity: 0.89,
        eventTime: '2026-05-22T15:45:30Z',
        source: 'raspy'
      }
      │
      ▼
Backend POST /api/attendance
   │
   ├─ Record ke access_logs table:
   │  INSERT INTO access_logs (
   │    user_id, full_name, method, access_status, similarity,
   │    source, event_time
   │  )
   │  VALUES (100, 'Robert Langdon', 'face', 'success', 0.89, 'raspy', ...)
   │
   └─ Response: { success: true }
```

### 7.2 View Attendance Logs

```
Admin klik "Access Logs" → Load logs
   │
   └─ fetch('/api/logs?limit=200')
      │
      ▼
Backend GET /api/logs
   │
   ├─ Load dari berbagai source:
   │  ├─ loadRemoteLogs() → Fetch dari Raspy /api/logs
   │  ├─ listLocalAccessLogs() → Query local access_logs
   │  └─ loadSpreadsheetLogs() (if enabled) → Fetch spreadsheet CSV
   │
   ├─ Merge semua logs
   ├─ Deduplicate (remove duplikat)
   ├─ Sort by eventTime DESC
   ├─ Limit ke 200 items
   │
   └─ Response:
      {
        success: true,
        logs: [
          {
            id: 1,
            userId: 100,
            fullName: 'Robert Langdon',
            method: 'face',
            accessStatus: 'success',
            similarity: 0.89,
            eventTime: '2026-05-22T15:45:30Z',
            source: 'raspy'
          },
          {
            id: 2,
            userId: 101,
            fullName: 'Jane Doe',
            method: 'fingerprint',
            accessStatus: 'success',
            similarity: null,
            eventTime: '2026-05-22T15:40:00Z',
            source: 'raspy'
          },
          ...
        ]
      }
      │
      ▼
Frontend
   │
   ├─ setState({ logs: response.logs })
   └─ Display table dengan sorting & filtering:
      ├─ Time | User | Method | Status | Similarity
      ├─ 15:45 | Robert Langdon | Face | ✅ | 0.89
      ├─ 15:40 | Jane Doe | Fingerprint | ✅ | -
      └─ ...
```

---

## 8️⃣ SETTINGS & RASPY INTEGRATION FLOW

### 8.1 Settings View

```
Admin klik "Pengaturan" → Settings tab
   │
   └─ fetch('/api/settings')
      │
      ▼
Backend GET /api/settings
   │
   ├─ Query: SELECT * FROM app_settings
   └─ Response:
      {
        success: true,
        settings: {
          raspy_api_base_url: 'http://127.0.0.1:5000',
          spreadsheet_csv_url: '',
          spreadsheet_enabled: '0',
          raspy_mode_endpoint: '/api/device/mode'
        }
      }
      │
      ▼
Frontend
   │
   ├─ setState({ settings: response.settings })
   └─ Display form dengan field:
      ├─ Input: Raspy API Base URL = "http://127.0.0.1:5000"
      ├─ Input: Spreadsheet CSV URL = (empty)
      ├─ Checkbox: Enable Spreadsheet = unchecked
      ├─ Button: "Test Connection"
      └─ Button: "Diagnostics"
```

### 8.2 Test Connection

```
Admin click "Test Connection" button
   │
   └─ fetch('/api/settings/test-connection', { method: 'POST' })
      │
      ▼
Backend POST /api/settings/test-connection
   │
   ├─ Call getRaspyStatus()
   │  └─ fetch('http://127.0.0.1:5000/api/health')
   │
   ├─ If response 200 OK:
   │  └─ { online: true, message: '✅ Raspy Online', payload: {...} }
   │
   └─ If timeout/error:
      └─ { online: false, message: '❌ Cannot connect to Raspy' }
      │
      ▼
Frontend
   │
   ├─ Toast: "✅ Raspy Online" atau "❌ Raspy Offline"
   └─ Update UI dengan status
```

### 8.3 Diagnostics

```
Admin click "Diagnostics" button
   │
   └─ fetch('/api/integration/diagnostics')
      │
      ▼
Backend GET /api/integration/diagnostics
   │
   ├─ Call runRaspyDiagnostics()
   │  ├─ getRaspyStatus() → Health check
   │  ├─ Fetch /api/users → User count
   │  ├─ Fetch /api/logs → Log count
   │  ├─ Fetch /api/device/mode → Read device mode
   │  └─ POST /api/device/mode → Write device mode (test)
   │
   └─ Response:
      {
        success: true,
        diagnostics: {
          baseUrl: 'http://127.0.0.1:5000',
          checks: {
            health: {
              ok: true,
              message: '✅ Raspy Health OK'
            },
            users: {
              ok: true,
              count: 45,
              message: undefined
            },
            logs: {
              ok: true,
              count: 523,
              message: undefined
            },
            deviceModeRead: {
              ok: true,
              payload: { mode: 'idle' }
            },
            deviceModeWrite: {
              ok: true,
              message: 'Signal terkirim'
            }
          }
        }
      }
      │
      ▼
Frontend
   │
   ├─ setState({ diagnostics: response.diagnostics })
   └─ Display checklist:
      ├─ ✅ Health: Online
      ├─ ✅ Users: 45 records
      ├─ ✅ Logs: 523 records
      ├─ ✅ Device Mode: Read OK
      └─ ✅ Device Mode: Write OK
```

---

## 9️⃣ SETUP WIZARD FLOW (First Time Setup)

```
User buka app pertama kali → SetupWizard modal
   │
   └─ Display system checks:
      ├─ Check Python executable
      ├─ Check PyTorch installed
      ├─ Check FaceNet-PyTorch
      ├─ Check OpenCV
      ├─ Check Webcam access
      └─ Check Storage access
      │
      ▼
Frontend loop untuk setiap check:
   │
   ├─ fetch('/api/setup/check', { checkId: 'python' })
   │
   ▼
Backend POST /api/setup/check
   │
   ├─ checkPythonExecutable()
   │  ├─ Create temp script: print(sys.version)
   │  ├─ spawn('python3', [scriptPath])
   │  ├─ Parse output → "Python 3.10.5"
   │  └─ Return { success: true, message: '✅ Python 3.10.5 detected' }
   │
   ├─ checkTorch()
   │  ├─ Create temp script: importlib.util.find_spec('torch')
   │  ├─ spawn('python3', [scriptPath])
   │  └─ Return success atau error message
   │
   └─ [similar untuk semua checks]
      │
      ▼
Frontend
   │
   └─ Display status:
      ├─ ✅ Python 3.10.5 detected
      ├─ ✅ PyTorch terinstall
      ├─ ✅ FaceNet-PyTorch terinstall
      ├─ ✅ OpenCV terinstall
      ├─ ✅ Webcam detected
      └─ ✅ Storage writable
         │
         └─ Button: "Lanjut ke Konfigurasi"
            │
            ▼
         Configure Raspy URL:
         ├─ Input: http://127.0.0.1:5000
         └─ Button: "Selesai & Masuk Dashboard"
            │
            ▼
         Backend POST /api/setup/configure
         │
         ├─ setSetting('raspy_api_base_url', 'http://127.0.0.1:5000')
         └─ Save ke app_settings table
            │
            ▼
         Frontend
         │
         ├─ localStorage.setItem('setupComplete', 'true')
         ├─ Close wizard modal
         └─ Redirect to Dashboard (dengan login dulu)
```

---

## 🔟 DATABASE STRUCTURE (SQLite - biometrics.db)

```
┌──────────────────────────────────────────────────────────┐
│                     SQLite Database                       │
└──────────────────────────────────────────────────────────┘

TABLE: auth_accounts
┌─────┬─────────┬───────────┬──────────────┬──────────────┐
│ id  │ user_id │ username  │ password_hash│ role         │
├─────┼─────────┼───────────┼──────────────┼──────────────┤
│ 1   │ NULL    │ admin     │ a3f9e8c7...  │ admin        │
│ 2   │ NULL    │ coadmin   │ b4f8d7c6...  │ coadmin      │
└─────┴─────────┴───────────┴──────────────┴──────────────┘

TABLE: users
┌────┬──────────────────┬──────┬──────────────────┬────────────────┐
│ id │ full_name        │ role │ face_enrolled    │ fingerprint_id │
├────┼──────────────────┼──────┼──────────────────┼────────────────┤
│ 1  │ John Doe         │ mem  │ 1 (true)         │ 101            │
│ 2  │ Jane Smith       │ coa  │ 1 (true)         │ 102            │
│ 100│ Robert Langdon   │ mem  │ 1 (true)         │ 103            │
└────┴──────────────────┴──────┴──────────────────┴────────────────┘

TABLE: access_logs
┌────┬─────────┬──────────────────┬──────────┬────────┐
│ id │ user_id │ fullname         │ method   │ status │
├────┼─────────┼──────────────────┼──────────┼────────┤
│ 1  │ 1       │ John Doe         │ face     │ success│
│ 2  │ 2       │ Jane Smith       │ finger   │ success│
└────┴─────────┴──────────────────┴──────────┴────────┘

TABLE: app_settings
┌──────────────────────┬─────────────────────────┐
│ key                  │ value                   │
├──────────────────────┼─────────────────────────┤
│ raspy_api_base_url   │ http://127.0.0.1:5000   │
│ spreadsheet_enabled  │ 0                       │
└──────────────────────┴─────────────────────────┘

FILE: embeddings.pkl (Pickle format - binary)
{
  "John Doe": [
    [0.12, -0.34, 0.56, ...],     // embedding 1
    [0.15, -0.30, 0.52, ...],     // embedding 2
    ...
    [0.18, -0.35, 0.58, ...]      // embedding 500
  ],
  "Jane Smith": [
    [...],
    [...],
    ...
  ]
}
```

---

## 1️⃣1️⃣ REQUEST/RESPONSE FLOW SUMMARY

```
┌────────────────────┐
│  React Frontend    │
│  (Vite + Vite)     │
└─────────┬──────────┘
          │ HTTP (localhost:3001)
          ▼
┌────────────────────────────┐
│ Express API                │
│ (electron/api.ts)          │
│ ├─ GET /api/dashboard      │
│ ├─ GET /api/users          │
│ ├─ POST /api/users         │
│ ├─ PUT /api/users/:id      │
│ ├─ DELETE /api/users/:id   │
│ ├─ POST /api/enrollment/*  │
│ ├─ POST /api/attendance    │
│ ├─ GET /api/logs           │
│ └─ ... (40+ endpoints)     │
└────────┬───────────────────┘
         │
    ┌────┼────┐
    │    │    │
    ▼    ▼    ▼
  SQLite  Python  Raspy
  DB      ML/AI   API
```

---

**Semoga penjelasan ini jelas! Ada yang ingin diperdalam lagi? 🚀**
