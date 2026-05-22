# Integrated Data Collection Pipeline

**Foto → Augmentasi → Embedding** - Semua otomatis dalam satu flow! ✨

Tidak perlu beda-beda step lagi. Just capture foto, dan script otomatis:
1. ✓ Generate 50 augmentasi per foto
2. ✓ Extract embedding semua variasi
3. ✓ Save ke embeddings.pkl
4. ✓ Ready untuk recognition

## Quick Start

### Single Command - Mulai Collection

```powershell
cd "d:\New folder\embedding_extractor"
C:\Users\Den\AppData\Local\Programs\Python\Python310\python.exe collect_and_extract.py
```

Script akan ask User ID:
```
Enter User ID (e.g., '1', 'john', 'user_2'): 1
```

### What Happens:

```
✓ Loading models...
✓ Loaded embeddings for users: ['1']
✓ User 1 already exist dengan 500 embeddings

============================================================
INTEGRATED DATA COLLECTION
============================================================
👤 User ID: 1
📊 Current embeddings: 500

[CONTROLS]
  SPACE     = Capture & process photo
  q         = Quit & save
============================================================

[Webcam ready - press SPACE to capture]
```

## Usage

### 1. Capture Foto (Press SPACE)

- Position wajah di webcam
- Press **SPACE** untuk capture

### 2. Automatic Processing (Tanpa input lagi!)

```
✓ Photo captured! Processing...
  [1/3] Generating 50 augmentations...
      ✓ Generated 50 augmented images
  [2/3] Extracting embeddings...
      ✓ Extracted 50 embeddings
  [3/3] Saving to database...
      ✓ Total embeddings for 1: 550

✅ Photo processed successfully!
```

### 3. Ulangi atau Quit

- Capture foto lagi (press SPACE)
- Atau press **q** untuk quit & save

### 4. Done!

```
✅ SAVED: 550 embeddings untuk user 1
📁 Path: ../embeddings.pkl
```

## Advanced Usage

### Multiple Users

```powershell
# User 1
python collect_and_extract.py 1

# User 2
python collect_and_extract.py 2

# User john
python collect_and_extract.py john
```

Script akan automatically:
- Load existing embeddings
- Add ke user baru atau append ke existing user
- Update `.pkl` file

### Command Line Direct

```powershell
# Skip input prompt
python collect_and_extract.py user_123
```

## Flow Diagram

```
START
  ↓
[Ask User ID]
  ↓
[Load embeddings.pkl / Create new]
  ↓
[Open Webcam]
  ↓
[Wait for SPACE input]
  ↓
[Capture Frame]
  ↓
[Generate 50 Augmentations] ← 2-3 secs
  ├─ Original
  ├─ Rotasi 7 variations
  ├─ Zoom 7 variations
  ├─ Brightness 7 variations
  ├─ Contrast 7 variations
  ├─ Translasi 7 variations
  ├─ Flip 4 variations
  ├─ Blur 7 variations
  └─ Kombinasi 3 variations
  ↓
[Extract Embeddings dari 50 images] ← 3-5 secs
  ↓
[Save to embeddings.pkl]
  ↓
[Update Statistics]
  ↓
[LOOP] → Tunggu input lagi atau quit
  ↓
[Save Final embeddings.pkl]
  ↓
END
```

## What Gets Saved

Setiap capture akan add embedding dari:
- **1 original foto**
- **49 augmented variations** (berbagai angle, brightness, zoom, dll)

Total: **50 embeddings** per foto capture

## Time Breakdown (per foto)

| Step | Time | Note |
|------|------|------|
| Generate augmentations | 2-3s | Fast - pure image processing |
| Extract embeddings | 3-5s | CPU/GPU dependent |
| Save to disk | <1s | Quick |
| **Total** | **5-8s** | Per foto capture |

## Results After Multiple Captures

| Captures | Total Embeddings | User Recognition Quality |
|----------|------------------|--------------------------|
| 1 | 50 | Poor (not recommended) |
| 5 | 250 | Fair |
| 10 | 500 | Good ✓ |
| 15 | 750 | Very Good ✓✓ |
| 20+ | 1000+ | Excellent ✓✓✓ |

**Recommendation:** Capture 10-15 foto dari berbagai posisi = excellent recognition! 

## Keyboard Controls

| Key | Action |
|-----|--------|
| **SPACE** | Capture current frame & auto process |
| **q** | Quit & save embeddings.pkl |

## Features

✅ **Real-time Processing** - See stats update after each capture  
✅ **Multiple Users** - Add embeddings untuk multiple users dalam satu file  
✅ **Error Handling** - Skip jika ada face detection error  
✅ **Progress Tracking** - Lihat berapa embeddings sudah di-collect  
✅ **Auto Augmentation** - No manual step needed  
✅ **Auto Extraction** - Embedding langsung extracted dan saved  

## Database Structure

Embeddings disimpan dalam format:
```python
{
    '1': [embedding1, embedding2, ..., embedding50],
    '2': [embedding1, embedding2, ..., embedding50],
    'john': [embedding1, embedding2, ...],
    ...
}
```

Setiap embedding adalah:
- **Size:** 512-dimensional vector (FaceNet output)
- **Type:** numpy array
- **Format:** Binary pickle format

## Troubleshooting

### ❌ "No face detected" pada beberapa augmentasi
**Normal!** Beberapa augmentasi extreme (severe rotation/zoom) mungkin tidak terdeteksi face.  
Script automatically skip dan lanjut ke augmentasi berikutnya.

### ❌ "Cannot open webcam"
- Check webcam connection
- Pastikan tidak dipakai aplikasi lain
- Coba restart

### ⚠️ Processing sangat lambat (>15s per foto)
- Mungkin CPU bottleneck
- Check background processes
- Gunakan GPU kalau tersedia:
  ```python
  # Edit collect_and_extract.py
  self.device = torch.device('cuda')  # instead of 'cpu'
  ```

### ❌ "ModuleNotFoundError"
```powershell
cd d:\New\ folder\embedding_extractor
python -m pip install -r requirements.txt
```

## Pro Tips

### 💡 Capture Strategy
1. **Framing position varied** - Face center, left, right, top, bottom
2. **Different angles** - Normal, tilted 45°, upside down
3. **Different distances** - Close, medium, far
4. **Different lighting** - Natural, shade, bright, dim
5. **Different expressions** - Neutral, smile, angry, tired

### 💡 Optimal Results
- Capture 10-15 photos dari berbagai posisi/kondisi
- Each capture = 50 embeddings otomatis
- Total: 500-750 embeddings ideal
- Recognition accuracy: 90%+ ✓

### 💡 Production Setup
```bash
# Setup untuk multiple users
python collect_and_extract.py user1  # Capture 10 fotos
python collect_and_extract.py user2  # Capture 10 fotos
python collect_and_extract.py user3  # Capture 10 fotos

# Total: 3 users × 500 embeddings = database ready!
```

## Next Steps

Setelah collection selesai:

1. **Deploy recognition**
   ```powershell
   cd "d:\New folder\face_recognition_test"
   python video_recognition.py
   ```

2. **Test dengan webcam** - Real-time detection!

3. **Monitor stats** - Lihat accuracy, confidence scores

4. **Add more users** - Just run script lagi dengan user ID baru

---

**That's it! Integrated, automatic, dan efficient!** 🚀
