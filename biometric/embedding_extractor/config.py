"""
Konfigurasi untuk Embedding Extractor
"""
import os

# Path konfigurasi
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHOTOS_ROOT = os.path.join(BASE_DIR, '../photos')  # Folder utama foto
EMBEDDINGS_PATH = os.path.join(BASE_DIR, '../embeddings.pkl')  # Output embeddings

# Model konfigurasi
FACENET_MODEL = 'vggface2'  # Model pretrained untuk FaceNet
TARGET_FACE_SIZE = (160, 160)  # Ukuran target untuk preprocessing

# MTCNN konfigurasi
MTCNN_MIN_FACE_SIZE = 20
MTCNN_THRESHOLDS = [0.6, 0.7, 0.7]
MTCNN_FACTOR = 0.709

# Processing
USE_GPU = True  # Gunakan GPU jika tersedia
VERBOSE = True  # Print progress detail
