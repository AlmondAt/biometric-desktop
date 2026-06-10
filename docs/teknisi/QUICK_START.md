# Quick Start - Testing Integrated System

## Prerequisites
- ✅ Python 3.10 installed
- ✅ All dependencies in requirements.txt
- ✅ Webcam working
- ✅ Node.js + npm

## Test Flow (5 minutes)

### 1. Start Backend & Frontend
```powershell
cd "d:\New folder"
npm run dev
```

Wait untuk:
- Vite dev server ready
- Electron window open
- Express API on :3001

### 2. Test Enrollment (New User)
1. Click "Enrollment" menu
2. Enter User ID: `test_user_1`
3. Click webcam area untuk position wajah
4. Click "Ambil Foto" button (do this 10+ times)
   - Move face around untuk different angles
   - Capture sampai ada 10 foto di grid preview
5. Click "Mulai Training Wajah"
6. **WAIT** (UI akan show progress):
   ```
   Memproses augmentasi dan ekstrak embedding...
   [Roughly 50-80 seconds]
   ✅ Training berhasil! 10 × 50 = 500 embeddings
   ```

### 3. Verify embeddings.pkl Created
```powershell
# Check file exists
ls "d:\New folder\embeddings.pkl"

# Should show file size (roughly 100KB+)
```

### 4. Test Recognition with Video
```powershell
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

Point at webcam:
- Should see: **✓ IDENTIFIED: test_user_1 (similarity: 0.82+)**
- Box: **GREEN** with user ID

## Troubleshooting

### ❌ "Express API not running"
- Check terminal: `[Internal Express API running on port 3001]`
- If not, restart: `npm run dev`

### ❌ "Connection refused :3001"
- Check if port 3001 in use: `netstat -ano | findstr :3001`
- Kill process if needed

### ❌ "Python module not found" during training
```powershell
cd embedding_extractor
python -m pip install -r requirements.txt
```

### ❌ Training takes too long (>3 minutes)
- CPU bottleneck, normal on slower systems
- First run: models loading from disk
- Subsequent trainings: faster (cached)

### ❌ "embeddings.pkl not found" during recognition
- Training hasilnya failed, check console for errors
- Retry enrollment process

### ❌ "NOT IDENTIFIED" saat recognition
- Similarity score too low (< 0.6)
- Try: Lower threshold di `config.py` SIMILARITY_THRESHOLD
- Or: Train dengan lebih banyak photos (15-20)

## Success Criteria

✅ Enrollment selesai
- ✓ UI shows "✅ Training berhasil!"
- ✓ `embeddings.pkl` created

✅ Recognition works  
- ✓ Webcam shows GREEN box
- ✓ Shows: "✓ IDENTIFIED: user_X"
- ✓ Similarity > 0.6

## Next Steps

1. **Add more users**
   - Repeat enrollment dengan different User ID
   - Setiap user dapat embeddings tersendiri

2. **Fine-tune threshold**
   - Edit: `face_recognition_test/config.py`
   - Lower untuk lebih lenient
   - Higher untuk lebih strict

3. **Optimize performance**
   - GPU setup (CUDA) untuk 10x faster
   - Edit: `training_api.py` dan `video_recognition.py`

4. **Deploy to production**
   - Package sebagai standalone exe
   - Setup database (instead of pickle file)
   - Add security (encrypt embeddings)

## Debug Commands

### Check embeddings
```python
import pickle
with open('embeddings.pkl', 'rb') as f:
    db = pickle.load(f)
    for user_id, embeddings in db.items():
        print(f"{user_id}: {len(embeddings)} embeddings")
```

### Check API logs
- Check browser console (F12)
- Check terminal output (Express logs)
- Check embeddings.pkl timestamp

### Reset system (if needed)
```powershell
# Delete embeddings to start fresh
rm "d:\New folder\embeddings.pkl"

# Or delete specific user data (Python):
# (Edit embeddings dengan pickle, remove user)
```

---

**Ready to test! Have fun! 🚀**
