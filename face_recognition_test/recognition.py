"""
Face Recognition Test - Deteksi siapa orang di foto berdasarkan embedding
"""
import pickle
import os
from pathlib import Path
import numpy as np
from PIL import Image
import cv2
from scipy.spatial.distance import cosine, euclidean

from facenet_pytorch import MTCNN, InceptionResnetV1
import torch

from config import (
    EMBEDDINGS_PATH, TEST_PHOTOS_DIR, SIMILARITY_THRESHOLD,
    DISTANCE_METRIC, MTCNN_DEVICE, FACENET_DEVICE
)


class FaceRecognizer:
    def __init__(self):
        """Initialize MTCNN dan FaceNet model"""
        print("[INFO] Loading MTCNN model...")
        self.device = torch.device(FACENET_DEVICE)
        self.mtcnn = MTCNN(device=MTCNN_DEVICE)
        
        print("[INFO] Loading FaceNet model...")
        self.model = InceptionResnetV1(pretrained='vggface2', device=FACENET_DEVICE)
        self.model.eval()
        
        # Load embeddings database
        print(f"[INFO] Loading embeddings from {EMBEDDINGS_PATH}...")
        if not os.path.exists(EMBEDDINGS_PATH):
            raise FileNotFoundError(f"Embeddings file not found: {EMBEDDINGS_PATH}")
        
        with open(EMBEDDINGS_PATH, 'rb') as f:
            self.embeddings_db = pickle.load(f)
        
        print(f"[✓] Loaded {len(self.embeddings_db)} users dari database")
    
    def extract_embedding(self, image_path):
        """Extract embedding dari foto"""
        try:
            # Load image
            img = Image.open(image_path).convert('RGB')
            
            # Detect face dengan MTCNN
            face_tensor, prob = self.mtcnn(img, return_prob=True)
            
            if face_tensor is None:
                return None, "❌ Tidak ada wajah terdeteksi"
            
            if prob < 0.9:
                return None, f"⚠ Wajah terdeteksi tapi confidence rendah: {prob:.2f}"
            
            # Extract embedding
            with torch.no_grad():
                embedding = self.model(face_tensor.unsqueeze(0).to(self.device))
            
            return embedding.cpu().numpy()[0], f"✓ Wajah terdeteksi (confidence: {prob:.2f})"
        
        except Exception as e:
            return None, f"❌ Error: {str(e)}"
    
    def calculate_similarity(self, emb1, emb2):
        """Hitung similarity antara 2 embedding"""
        if DISTANCE_METRIC == 'cosine':
            distance = cosine(emb1, emb2)
            similarity = 1 - distance
        else:  # euclidean
            distance = euclidean(emb1, emb2)
            similarity = 1 / (1 + distance)
        
        return similarity
    
    def recognize_face(self, image_path):
        """Recognize wajah di foto"""
        print(f"\n🔍 Menganalisis: {os.path.basename(image_path)}")
        print("=" * 60)
        
        # Extract embedding
        embedding, msg = self.extract_embedding(image_path)
        print(f"[Detection] {msg}")
        
        if embedding is None:
            return None
        
        # Compare dengan database
        best_match = None
        best_similarity = 0
        
        print("\n[Comparison Results]")
        print(f"{'User':<10} {'Similarity':<15} {'Match?'}")
        print("-" * 40)
        
        for user_id, user_embeddings in self.embeddings_db.items():
            # Average similarity dari semua foto user
            similarities = []
            for user_emb in user_embeddings:
                sim = self.calculate_similarity(embedding, user_emb)
                similarities.append(sim)
            
            avg_similarity = np.mean(similarities)
            max_similarity = np.max(similarities)
            
            is_match = "✓" if avg_similarity >= SIMILARITY_THRESHOLD else "✗"
            print(f"{user_id:<10} {avg_similarity:.4f} (max: {max_similarity:.4f})  {is_match}")
            
            if avg_similarity > best_similarity:
                best_similarity = avg_similarity
                best_match = (user_id, avg_similarity, max_similarity)
        
        # Result
        print("\n" + "=" * 60)
        if best_match and best_match[1] >= SIMILARITY_THRESHOLD:
            user_id, avg_sim, max_sim = best_match
            print(f"✓ IDENTIFIED: User {user_id}")
            print(f"  - Average Similarity: {avg_sim:.4f}")
            print(f"  - Max Similarity: {max_sim:.4f}")
            return best_match
        else:
            print(f"❌ NOT IDENTIFIED")
            if best_match:
                user_id, avg_sim, max_sim = best_match
                print(f"  - Closest match: User {user_id} ({avg_sim:.4f})")
                print(f"  - Threshold: {SIMILARITY_THRESHOLD}")
            return None
    
    def recognize_all(self):
        """Recognize semua foto di test_photos folder"""
        if not os.path.exists(TEST_PHOTOS_DIR):
            print(f"❌ Test photos directory not found: {TEST_PHOTOS_DIR}")
            return
        
        # Get all image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}
        image_files = [
            f for f in os.listdir(TEST_PHOTOS_DIR)
            if os.path.splitext(f)[1].lower() in image_extensions
        ]
        
        if not image_files:
            print(f"❌ Tidak ada foto di folder: {TEST_PHOTOS_DIR}")
            return
        
        print(f"\n{'=' * 60}")
        print(f"FACE RECOGNITION TEST")
        print(f"{'=' * 60}")
        print(f"📁 Test photos directory: {TEST_PHOTOS_DIR}")
        print(f"📊 Found {len(image_files)} image(s)\n")
        
        results = []
        for img_file in image_files:
            img_path = os.path.join(TEST_PHOTOS_DIR, img_file)
            result = self.recognize_face(img_path)
            results.append({
                'filename': img_file,
                'result': result
            })
        
        # Summary
        print(f"\n\n{'=' * 60}")
        print("SUMMARY")
        print(f"{'=' * 60}")
        identified = sum(1 for r in results if r['result'] is not None)
        print(f"Total photos: {len(results)}")
        print(f"Identified: {identified}")
        print(f"Not identified: {len(results) - identified}")
        
        return results


if __name__ == "__main__":
    try:
        recognizer = FaceRecognizer()
        recognizer.recognize_all()
    
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print(f"\n📝 Pastikan sudah jalankan embedding_extractor/main.py terlebih dahulu!")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
