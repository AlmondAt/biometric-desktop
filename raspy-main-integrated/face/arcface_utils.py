import cv2
import numpy as np
import pickle
import os

# Try to import heavy ML deps (facenet_pytorch, torch). If unavailable,
# disable ArcFace functionality but keep helper functions so the rest of
# application can still run.
ARCFACE_AVAILABLE = False
try:
    import torch
    from facenet_pytorch import InceptionResnetV1

    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    try:
        arcface_model = InceptionResnetV1(pretrained='vggface2').eval().to(device)
        ARCFACE_AVAILABLE = True
    except Exception as e:
        print(f"[!] Gagal inisialisasi ArcFace model: {e}")
        arcface_model = None
except ModuleNotFoundError as e:
    print(f"[!] ArcFace non-aktif: modul tidak ditemukan: {e}")
    arcface_model = None
except Exception as e:
    print(f"[!] ArcFace import error: {e}")
    arcface_model = None

def preprocess_face(face_img, target_size=(160, 160)):
    """
    Pra-pemrosesan wajah untuk model ArcFace
    
    Args:
        face_img (numpy.ndarray): Gambar wajah
        target_size (tuple): Ukuran target untuk model
        
    Returns:
        torch.Tensor: Tensor wajah yang telah diproses
    """
    # If ArcFace deps are not available we still allow callers to attempt
    # preprocessing, but signal by returning None if torch is missing.
    if not ARCFACE_AVAILABLE:
        print("[!] preprocess_face: ArcFace/torch tidak tersedia; mengembalikan None")
        return None

    try:
        if face_img is None or not isinstance(face_img, np.ndarray):
            print("[!] Input face_img tidak valid (None atau bukan numpy array)")
            return None

        # Cek dimensi gambar
        if len(face_img.shape) != 3:
            print(f"[!] Dimensi gambar tidak valid: {face_img.shape}")
            return None

        # Cek ukuran gambar
        if face_img.shape[0] <= 0 or face_img.shape[1] <= 0:
            print(f"[!] Ukuran gambar tidak valid: {face_img.shape}")
            return None

        # Resize gambar dengan error handling
        try:
            face_img = cv2.resize(face_img, target_size)
        except cv2.error as e:
            print(f"[!] Error resize gambar: {e}")
            return None

        # Konversi BGR ke RGB
        face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)

        # Normalisasi (0-255 -> 0-1)
        face_img = face_img / 255.0

        # Konversi ke tensor
        import torch
        face_tensor = torch.from_numpy(face_img.transpose((2, 0, 1))).float()

        # Tambahkan dimensi batch
        face_tensor = face_tensor.unsqueeze(0)

        return face_tensor

    except Exception as e:
        print(f"[!] Error dalam preprocess_face: {e}")
        return None

def extract_embedding(face_tensor):
    """
    Ekstrak embedding dari wajah menggunakan ArcFace
    
    Args:
        face_tensor (torch.Tensor): Tensor wajah yang telah diproses
        
    Returns:
        numpy.ndarray: Vektor embedding
    """
    if not ARCFACE_AVAILABLE or arcface_model is None:
        print("[!] extract_embedding: ArcFace tidak tersedia; mengembalikan None")
        return None

    if face_tensor is None:
        return None

    import torch
    with torch.no_grad():
        face_tensor = face_tensor.to(device)
        embedding = arcface_model(face_tensor).cpu().numpy()

    return embedding[0]  # Hilangkan dimensi batch

def compute_similarity(embedding1, embedding2):
    """
    Menghitung cosine similarity antara dua embedding
    
    Args:
        embedding1 (numpy.ndarray): Embedding pertama
        embedding2 (numpy.ndarray/list): Embedding kedua atau list embedding
        
    Returns:
        float: Cosine similarity tertinggi (0-1)
    """
    # Jika ArcFace tidak tersedia, selalu return 0 similarity
    if not ARCFACE_AVAILABLE:
        print("[!] compute_similarity: ArcFace tidak tersedia; mengembalikan 0")
        return 0

    # Jika embedding2 adalah list embeddings, ambil similarity tertinggi
    if isinstance(embedding2, list):
        max_similarity = 0
        for emb in embedding2:
            similarity = compute_similarity(embedding1, emb)
            max_similarity = max(max_similarity, similarity)
        return max_similarity
    
    # Jika embedding2 adalah array tunggal
    dot_product = np.dot(embedding1, embedding2)
    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)
    
    if norm1 == 0 or norm2 == 0:
        return 0
        
    return dot_product / (norm1 * norm2)

def save_embeddings(embeddings_dict, file_path):
    """
    Menyimpan embeddings ke file
    
    Args:
        embeddings_dict (dict): Dictionary nama -> embedding
        file_path (str): Path file tujuan
    """
    # Buat direktori jika belum ada
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'wb') as f:
        pickle.dump(embeddings_dict, f)
        
def load_embeddings(file_path):
    """
    Memuat embeddings dari file
    
    Args:
        file_path (str): Path file sumber
        
    Returns:
        dict: Dictionary nama -> embedding
    """
    try:
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    except ModuleNotFoundError as e:
        print(f"[!] Gagal memuat embeddings karena modul tidak ditemukan: {e}. Embeddings akan dikosongkan.")
        return {}
    except (FileNotFoundError, EOFError):
        print(f"File embedding tidak ditemukan di {file_path}")
        return {}
    except Exception as e:
        print(f"[!] Error lain saat load_embeddings: {e}")
        return {}