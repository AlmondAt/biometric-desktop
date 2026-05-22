"""
Configuration untuk Face Recognition Test
"""
import os

# Path configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMBEDDINGS_PATH = os.path.join(BASE_DIR, '..', 'embeddings.pkl')
TEST_PHOTOS_DIR = os.path.join(BASE_DIR, 'test_photos')

# Model configuration
MTCNN_DEVICE = 'cpu'  # Gunakan 'cuda' jika punya GPU
FACENET_DEVICE = 'cpu'  # Gunakan 'cuda' jika punya GPU

# Recognition threshold (cosine similarity)
# Semakin tinggi = semakin strict (butuh lebih mirip)
SIMILARITY_THRESHOLD = 0.6

# Distance metric: 'cosine' atau 'euclidean'
DISTANCE_METRIC = 'cosine'

# Confidence threshold untuk mendeteksi wajah
FACE_DETECTION_THRESHOLD = 0.9
