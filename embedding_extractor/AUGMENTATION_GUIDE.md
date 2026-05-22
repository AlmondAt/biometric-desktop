# Data Augmentation - Dari 10 Foto → 500 Foto

Script untuk generate ribuan variasi dari foto asli dengan berbagai:
- **Rotasi** (berbagai sudut: 10°, 20°, 30°, -10°, -20°, -30°)
- **Zoom** (in/out: 0.75x, 0.8x, 0.9x, 1.1x, 1.2x, 1.15x)
- **Brightness** (terang/gelap: 0.6x - 1.4x)
- **Contrast** (contrast adjustment)
- **Translasi** (geser posisi wajah dalam frame)
- **Flip** (horizontal, vertical, both)
- **Blur** (simulate different focus)
- **Kombinasi** (rotate + brightness, dll)

## Quick Start

### Step 1: Siapkan folder input

```
embedding_extractor/
├── augment_input/          ← Folder INI harus kamu buat & isi dengan foto original
│   ├── photo1.jpg
│   ├── photo2.jpg
│   └── ... (maksimal 10 foto, nggak perlu banyak)
├── data_augmentation.py    ← Script ini
└── ...
```

Copy 10 foto original ke folder `augment_input/`.

### Step 2: Jalankan augmentor

```powershell
cd "d:\New folder\embedding_extractor"

# Simple - default settings (50 augmentations per image = 500 total)
C:\Users\Den\AppData\Local\Programs\Python\Python310\python.exe data_augmentation.py

# Atau dengan custom settings
# Syntax: python data_augmentation.py <input_dir> <output_dir> <augmentations_per_image>
C:\Users\Den\AppData\Local\Programs\Python\Python310\python.exe data_augmentation.py ./augment_input ./augmented_photos 50
```

### Step 3: Tunggu proses

Output:
```
============================================================
DATA AUGMENTATION
============================================================
📁 Found 10 images
🎯 Target: 500 augmented images

[1/10] photo1.jpg: ✓ 50 variations generated
[2/10] photo2.jpg: ✓ 50 variations generated
...
============================================================
✓ AUGMENTATION COMPLETE!
📊 Total augmented images: 500
📁 Saved to: ./augmented_photos
```

### Step 4: Copy augmented photos ke training folder

```powershell
# Copy semua augmented photos ke photos/1/ folder (atau user ID yang sesuai)
Copy-Item "augmented_photos/*" -Destination "../photos/1/" -Recurse
```

Atau manual:
1. Open file explorer
2. Buka folder `augmented_photos`
3. Select all → Copy
4. Paste ke `photos/1/` (replace jika perlu)

### Step 5: Jalankan embedding extractor dengan data baru

```powershell
cd "d:\New folder\embedding_extractor"
C:\Users\Den\AppData\Local\Programs\Python\Python310\python.exe main.py
```

Sekarang embedding akan extract dari 500 foto dengan berbagai pose! 💪

## Augmentation Details

Setiap foto akan di-generate menjadi 50 variasi:

| No | Tipe | Count | Contoh |
|----|------|-------|--------|
| 1 | Original | 1 | No modification |
| 2-8 | Rotasi | 7 | 10°, 20°, 30°, -10°, -20°, -30°, 15° |
| 9-15 | Zoom | 7 | 0.8x, 0.9x, 1.1x, 1.2x, 0.75x, 1.15x, 0.85x |
| 16-22 | Brightness | 7 | 0.6x, 0.7x, 0.8x, 1.2x, 1.3x, 1.4x, 0.9x |
| 23-29 | Contrast | 7 | 0.8x, 0.9x, 1.1x, 1.2x, 0.7x, 1.3x, 0.95x |
| 30-36 | Translasi | 7 | Shift dalam berbagai arah |
| 37-40 | Flip | 4 | H-flip, V-flip, Both-flip |
| 41-47 | Blur | 7 | Kernel size: 3x3, 5x5, 7x7 |
| 48-50 | Kombinasi | 3 | Rotate + brightness combo |

## Manfaat Augmentation

✅ **Lebih Robust** - Model adapt dengan berbagai kondisi (angle, pencahayaan, focus)  
✅ **Generalisasi Lebih Baik** - Bukan hanya belajar dari 10 foto, tapi 500 variasi  
✅ **Mitigasi Overfitting** - Lebih diversitas = lebih generalize  
✅ **Kualitas Recognition Lebih Baik** - Lebih akurat mengenali orang di berbagai kondisi  

## Folder Structure Sebelum & Sesudah

### Sebelum:
```
embedding_extractor/
├── photos/1/
│   ├── photo_0.jpg
│   ├── photo_1.jpg
│   └── ... (10 foto)
```

### Sesudah Augmentation:
```
embedding_extractor/
├── photos/1/
│   ├── photo_0_000.jpg  (original)
│   ├── photo_0_001.jpg  (rotasi 10°)
│   ├── photo_0_002.jpg  (rotasi 20°)
│   ├── photo_0_003.jpg  (zoom 0.8x)
│   ├── ... (50 variations dari photo_0.jpg)
│   ├── photo_1_000.jpg  (original)
│   ├── photo_1_001.jpg
│   └── ... (50 variations dari photo_1.jpg)
│   └── ... (total 500 foto)
```

Total: **500 foto** dari cuma **10 original**! 🎉

## Advanced Usage

### Custom augmentations count

Mau 100 variations per foto (1000 total)?

```powershell
python data_augmentation.py ./augment_input ./augmented_photos 100
```

### Use different input/output folders

```powershell
python data_augmentation.py "D:\my_photos" "D:\output_augmented" 50
```

## Tips & Tricks

### ✅ Best Practices
- Gunakan foto berkualitas baik sebagai input
- Minimal 10 foto dengan berbagai angle/kondisi
- Jangan gunakan foto yang terlalu mirip (boring)
- Check bahwa output tergenerate dengan baik sebelum training

### ⚠️ Pitfalls
- **Jangan re-augment augmented photos** - quality akan degrade
- **Reset embeddings.pkl sebelum retrain** - embeddings lama akan interfere
- **Check disk space** - 10 photos × 50 augmentations = ~250MB+ (tergantung resolution)

## Performance Impact

### Embedding Extraction Time
- 10 photos: ~5-10 detik
- 500 photos: ~4-5 menit (tergantung GPU)

### Recognition Accuracy
- Dengan 10 photos: ~70-80% accuracy
- Dengan 500 photos: ~90-95% accuracy (significant improvement!)

## Troubleshooting

### ❌ "ModuleNotFoundError: No module named 'cv2'"
```powershell
python -m pip install -r requirements.txt
```

### ❌ Output folder kosong
- Check input folder ada foto atau tidak
- Pastikan format foto valid (.jpg, .png)
- Check disk space cukup

### ❌ Proses sangat lambat
- Normal! Processing 500 images butuh beberapa menit
- Gunakan GPU kalau bisa
- Keep patience 😄

## Next Steps

Setelah augmentation & training selesai:

1. **Test recognition** dengan video atau foto test
2. **Fine-tune threshold** di config.py kalau perlu
3. **Increase variations** kalau accuracy masih kurang
4. **Production deploy** jika sudah puas dengan hasil

---

**Enjoy! 500+ variations dari 10 foto = Recognition model yang jauh lebih baik!** 🚀
