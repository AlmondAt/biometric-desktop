# Embedding Extractor 🎭

Script untuk ekstrak embedding wajah dari foto dan menyimpannya ke `embeddings.pkl`.

## Struktur Folder

```
embedding_extractor/
├── main.py              # Script utama
├── facenet_utils.py     # Utilities FaceNet (InceptionResnetV1)
├── mtcnn_utils.py       # Utilities MTCNN (deteksi wajah)
├── config.py            # Konfigurasi path dan settings
├── requirements.txt     # Dependencies
└── README.md           # File ini
```

## Requirements

- Python 3.7+
- PyTorch (GPU opsional, CPU juga jalan)
- FaceNet PyTorch
- OpenCV

## Instalasi

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Setup folder struktur:**
```
../photos/
├── nama_user_1/
│   ├── photo_1.jpg
│   ├── photo_2.jpg
│   └── ...
├── nama_user_2/
│   ├── photo_1.jpg
│   ├── photo_2.jpg
│   └── ...
└── ...
```

## Cara Menggunakan

### Default (gunakan konfigurasi di config.py)
```bash
python main.py
```

### Custom path
```bash
python main.py --photos ../photos --output ../embeddings.pkl --verbose
```

### Opsi:
- `--photos PHOTOS_DIR` - Path folder foto (default: ../photos)
- `--output OUTPUT_FILE` - Path embeddings.pkl (default: ../embeddings.pkl)
- `--verbose` - Tampilkan detail progress

## Output

File `embeddings.pkl` akan berisi dictionary:
```python
{
    'nama_user_1': [embedding1, embedding2, ...],  # List of numpy arrays (512 dim)
    'nama_user_2': [embedding1, embedding2, ...],
    ...
}
```

## Tips

- **Kualitas foto**: Gunakan foto yang jelas, pencahayaan baik, dan wajah terlihat
- **Jumlah foto**: Min 5-10 foto per orang untuk hasil bagus
- **Format**: Dukung `.jpg` dan `.png`
- **GPU**: Ekstrak lebih cepat dengan GPU. Pastikan PyTorch punya CUDA support
- **Progress**: Gunakan `--verbose` untuk lihat detail processing

## Troubleshooting

### Error: "Folder photos tidak ditemukan"
→ Buat folder `photos` dan tambahkan subfolder dengan nama user

### Error: "Tidak ada subfolder user"
→ Struktur folder salah. Format: `photos/<nama_user>/`

### Error: "Tidak ada embedding yang berhasil diekstrak"
→ Foto tidak jelas atau tidak ada wajah. Cek kualitas foto

### Proses lambat
→ Normal untuk CPU. Gunakan GPU untuk lebih cepat

## Model Details

- **Face Detection**: MTCNN (Multi-task Cascaded Convolutional Networks)
- **Face Recognition**: FaceNet - InceptionResnetV1 (VGGFace2 pretrained)
- **Embedding Size**: 512 dimensi
- **Distance Metric**: Cosine Similarity
