# Video Face Recognition Mode

Script untuk deteksi wajah dari video (webcam atau video file). Lebih praktis dan real-time!

## Cara Jalankan

### Option 1: Dari Webcam (Recommended - paling gampang)

```powershell
cd biometric/face_recognition_test
python video_recognition.py
```

Beres! Webcam akan langsung ke-detect dan recognition jalan real-time.

### Option 2: Dari Video File

```powershell
python video_recognition.py "path/to/video.mp4"
```

Contoh:
```powershell
python video_recognition.py "C:\video_test.mp4"
```

## Keyboard Controls

Saat video berjalan:

| Key | Fungsi |
|-----|--------|
| `q` | Quit (keluar) |
| `p` | Pause/Resume video |
| `s` | Save current frame dengan annotation |

## Output Format

### Visual:
- **Wajah terdeteksi & dikenal** → Box HIJAU + nama user + similarity score
  ```
  User 1 (0.82)
  ```

- **Wajah terdeteksi tapi TIDAK dikenal** → Box MERAH + "Unknown"
  ```
  Unknown
  ```

### Info di layar:
- Frame counter (frame ke berapa)
- Jumlah wajah terdeteksi
- Status (paused/running)

## Contoh Flow

```
[Webcam started]
Frame 1: Detect 1 face → Extract embedding → Compare dengan DB
         → Match dengan User 1 (similarity: 0.85) → Draw GREEN box
         
Frame 2: Detect 1 face → Extract embedding → No match (similarity: 0.42 < threshold 0.6)
         → Draw RED box dengan "Unknown"

Frame 3: No face detected → Blank frame

Frame 4: Detect 2 faces → Extract embeddings → Match User 1 & User 2
         → Draw 2 GREEN boxes
```

## Performa

### Processing Speed:
- **Webcam**: Real-time (~5-15 FPS tergantung GPU)
- **Video file**: Depends on file size & codec

### GPU vs CPU:
Kalau punya GPU (NVIDIA CUDA):
```python
# Edit config.py
MTCNN_DEVICE = 'cuda'
FACENET_DEVICE = 'cuda'
```

Hasilnya: 5-10x lebih cepat!

## Output Files

Saat press `s`, frame di-save dengan format:
```
recognition_frame_1.jpg
recognition_frame_42.jpg
```

## Troubleshooting

### ❌ "ModuleNotFoundError: No module named 'cv2'"
OpenCV belum install. Jalankan di embedding_extractor folder:
```powershell
cd biometric/embedding_extractor
python -m pip install -r requirements.txt
```

### ❌ Webcam tidak detected
- Pastikan webcam aktif dan tidak dipakai aplikasi lain
- Coba ganti dengan: `python video_recognition.py 1` (device 1)
- Restart computer kalau perlu

### ❌ "No face detected" tapi ada wajah
- Pahami pencahayaan kurang baik
- Wajah terlalu kecil atau sudut aneh
- Coba: bergerak lebih dekat ke camera

### ❌ "Unknown" semua padahal seharusnya recognize
- Threshold terlalu tinggi. Edit config.py:
  ```python
  SIMILARITY_THRESHOLD = 0.5  # dari 0.6 jadi 0.5 (lebih loose)
  ```
- Atau training data kurang (tambah foto saat training)

### ⚠ Proses lambat / lag
- Gunakan GPU kalau ada di config.py
- Reduce video resolution
- Close apps lain

## Bonus Tips

### Save video dengan annotation:
Bisa modifikasi script untuk save video output (next update!)

### Multiple video sources:
Kalau ada multiple cameras, coba:
```powershell
python video_recognition.py 0  # Camera 0
python video_recognition.py 1  # Camera 1
```

### Real-time stats:
Script udah show:
- Frame count
- Face count
- Similarity scores
- User IDs

Sempurna untuk demo atau testing! 🎥✨
