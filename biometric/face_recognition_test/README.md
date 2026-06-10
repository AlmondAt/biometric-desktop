# Face Recognition Test

Script untuk test apakah embedding yang sudah di-extract berhasil dan bisa mendeteksi siapa orang di foto.

## Struktur Folder

```
face_recognition_test/
├── recognition.py       # Script utama untuk test
├── config.py           # Konfigurasi (threshold, path, dll)
├── test_photos/        # Folder untuk test images
└── README.md
```

## Cara Menggunakan

### 1. Siapkan Test Photos

1. Masukkan foto test ke folder `test_photos/`
2. Foto harus dalam format: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.gif`
3. **Important:** Foto harus berisi WAJAH yang jelas (sesuai dengan wajah yang ada di database embeddings)

Contoh struktur:
```
test_photos/
├── test_1.jpg
├── test_2.jpg
├── test_3.jpg
└── ...
```

### 2. Jalankan Recognition Test

```powershell
# Pastikan sudah di folder ini
cd biometric/face_recognition_test

# Jalankan dengan Python
python recognition.py
```

### 3. Interpretasi Results

Output akan menampilkan:

```
🔍 Menganalisis: test_1.jpg
============================================================
[Detection] ✓ Wajah terdeteksi (confidence: 0.98)

[Comparison Results]
User       Similarity      Match?
----------------------------------------
1          0.8234 (max: 0.8456)  ✓

============================================================
✓ IDENTIFIED: User 1
  - Average Similarity: 0.8234
  - Max Similarity: 0.8456
```

**Arti:**
- ✓ = Match (teridentifikasi sebagai user tsb)
- ✗ = No match (tidak cocok)
- **Similarity** = Nilai 0-1. Semakin tinggi = semakin mirip
  - > 0.6 = Threshold untuk consider sebagai match (bisa diubah di config.py)

## Konfigurasi (config.py)

Bisa menyesuaikan beberapa parameter:

```python
# Similarity threshold (cosine similarity)
# Semakin tinggi = semakin strict (butuh lebih mirip)
SIMILARITY_THRESHOLD = 0.6  # Change this value

# Distance metric: 'cosine' atau 'euclidean'
DISTANCE_METRIC = 'cosine'

# Gunakan GPU jika tersedia
MTCNN_DEVICE = 'cuda'  # atau 'cpu'
FACENET_DEVICE = 'cuda'  # atau 'cpu'
```

## Troubleshooting

### ❌ "Embeddings file not found"
- **Cause:** `embeddings.pkl` belum dibuat
- **Fix:** Jalankan `embedding_extractor/main.py` terlebih dahulu

### ❌ "Tidak ada wajah terdeteksi"
- **Cause:** Foto tidak jelas atau tidak ada wajah
- **Fix:** Ganti dengan foto yang lebih jelas

### ⚠ "Wajah terdeteksi tapi confidence rendah"
- **Cause:** Foto blur atau wajah kecil
- **Fix:** Gunakan foto berkualitas lebih baik

### ❌ "NOT IDENTIFIED"
- **Cause:** Similarity score terlalu rendah
- **Fix:** 
  1. Turunkan `SIMILARITY_THRESHOLD` di config.py
  2. Atau pastikan foto training dan test dari kondisi/angle yang mirip

## Notes

- Script ini assume bahwa `embeddings.pkl` sudah ada di project root directory
- MTCNN digunakan untuk detect face
- FaceNet digunakan untuk extract embedding
- Comparison menggunakan cosine similarity
- Bisa support multiple users dalam database

## Performance Tips

- Gunakan GPU kalau ada (CUDA) untuk lebih cepat:
  ```python
  MTCNN_DEVICE = 'cuda'
  FACENET_DEVICE = 'cuda'
  ```
- First run akan lebih lambat karena model loading
- Subsequent runs lebih cepat

## Next Steps

Setelah berhasil test, bisa:
1. Increase data training dengan lebih banyak foto
2. Setup production system dengan real-time camera
3. Fine-tune threshold sesuai use case
