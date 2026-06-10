"""
Integrated Face Data Collection Pipeline
Foto → Augmentasi → Embedding Extraction (semua otomatis!)

Flow:
1. Capture foto dari webcam (press SPACE untuk capture)
2. Auto augmentasi → 50 variasi per foto
3. Auto extract embedding semua variasi
4. Auto save ke embeddings.pkl
5. Done! Ready untuk recognition
"""
import pickle
import os
import cv2
import numpy as np
from pathlib import Path
import time
from tqdm import tqdm
from PIL import Image

from facenet_pytorch import MTCNN, InceptionResnetV1
import torch


class IntegratedDataCollector:
    def __init__(self, user_id, embeddings_path='../embeddings.pkl', augmentations_per_photo=50):
        """
        Initialize collector
        
        Args:
            user_id: ID user (e.g., '1', '2', 'user_john', etc)
            embeddings_path: Path ke embeddings.pkl (akan create jika belum ada)
            augmentations_per_photo: Jumlah augmentation per foto (default 50)
        """
        self.user_id = user_id
        self.embeddings_path = embeddings_path
        self.augmentations_per_photo = augmentations_per_photo
        
        print("[INFO] Loading models...")
        self.device = torch.device('cpu')
        self.mtcnn = MTCNN(device='cpu', keep_all=False)
        self.model = InceptionResnetV1(pretrained='vggface2', device='cpu')
        self.model.eval()
        
        # Load existing embeddings atau create baru
        if os.path.exists(embeddings_path):
            print(f"[INFO] Loading existing embeddings from {embeddings_path}")
            with open(embeddings_path, 'rb') as f:
                self.embeddings_db = pickle.load(f)
            print(f"[✓] Loaded embeddings for users: {list(self.embeddings_db.keys())}")
        else:
            print(f"[INFO] Creating new embeddings database")
            self.embeddings_db = {}
        
        # Initialize user embeddings jika belum ada
        if user_id not in self.embeddings_db:
            self.embeddings_db[user_id] = []
            print(f"[✓] Created new user: {user_id}")
        else:
            print(f"[✓] User {user_id} already exist dengan {len(self.embeddings_db[user_id])} embeddings")
    
    def rotate_image(self, img, angle):
        """Rotate dengan angle"""
        h, w = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(img, M, (w, h))
    
    def zoom_image(self, img, zoom_factor):
        """Zoom in/out"""
        h, w = img.shape[:2]
        new_h, new_w = int(h * zoom_factor), int(w * zoom_factor)
        
        if zoom_factor > 1:
            start_h = (new_h - h) // 2
            start_w = (new_w - w) // 2
            zoomed = cv2.resize(img, (new_w, new_h))
            return zoomed[start_h:start_h+h, start_w:start_w+w]
        else:
            zoomed = cv2.resize(img, (new_w, new_h))
            padded = np.full((h, w, 3), 128, dtype=np.uint8)
            pad_h = (h - new_h) // 2
            pad_w = (w - new_w) // 2
            padded[pad_h:pad_h+new_h, pad_w:pad_w+new_w] = zoomed
            return padded
    
    def adjust_brightness(self, img, factor):
        """Adjust brightness"""
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 2] = hsv[:, :, 2] * factor
        hsv[:, :, 2] = np.clip(hsv[:, :, 2], 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    
    def adjust_contrast(self, img, factor):
        """Adjust contrast"""
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
        l = lab[:, :, 0]
        l = (l - 50) * factor + 50
        l = np.clip(l, 0, 255)
        lab[:, :, 0] = l
        return cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)
    
    def translate_image(self, img, tx, ty):
        """Translate/shift image"""
        h, w = img.shape[:2]
        M = np.float32([[1, 0, tx], [0, 1, ty]])
        return cv2.warpAffine(img, M, (w, h))
    
    def flip_image(self, img, direction='horizontal'):
        """Flip image"""
        if direction == 'horizontal':
            return cv2.flip(img, 1)
        return cv2.flip(img, -1)
    
    def gaussian_blur(self, img, kernel_size=(3, 3)):
        """Gaussian blur"""
        return cv2.GaussianBlur(img, kernel_size, 0)
    
    def generate_augmentations(self, img):
        """
        Generate 50 augmentasi dari 1 foto
        Return: list of augmented images
        """
        augmentations = [img]  # Original
        
        # Rotations
        for angle in [10, 20, 30, -10, -20, -30, 15]:
            augmentations.append(self.rotate_image(img, angle))
        
        # Zooms
        for zoom in [0.8, 0.9, 1.1, 1.2, 0.75, 1.15, 0.85]:
            augmentations.append(self.zoom_image(img, zoom))
        
        # Brightness
        for factor in [0.6, 0.7, 0.8, 1.2, 1.3, 1.4, 0.9]:
            augmentations.append(self.adjust_brightness(img, factor))
        
        # Contrast
        for factor in [0.8, 0.9, 1.1, 1.2, 0.7, 1.3, 0.95]:
            augmentations.append(self.adjust_contrast(img, factor))
        
        # Translations
        h, w = img.shape[:2]
        for tx, ty in [(w//10, 0), (-w//10, 0), (0, h//10), (0, -h//10),
                       (w//8, h//8), (-w//8, -h//8), (w//6, -h//6)]:
            augmentations.append(self.translate_image(img, tx, ty))
        
        # Flips
        flipped_h = self.flip_image(img, 'horizontal')
        flipped_both = self.flip_image(img, 'both')
        for aug in [flipped_h, self.flip_image(img, 'vertical'), flipped_both, flipped_h]:
            augmentations.append(aug)
        
        # Blur
        for kernel in [(3, 3), (5, 5), (3, 3), (5, 5), (3, 3), (7, 7), (5, 5)]:
            augmentations.append(self.gaussian_blur(img, kernel))
        
        # Combinations
        for angle, bright_factor in [(15, 1.2), (-15, 0.8), (20, 1.1)]:
            rotated = self.rotate_image(img, angle)
            bright = self.adjust_brightness(rotated, bright_factor)
            augmentations.append(bright)
        
        return augmentations[:self.augmentations_per_photo]
    
    def extract_embeddings(self, images):
        """
        Extract embeddings dari list images
        Return: list of embeddings
        """
        embeddings = []
        
        for img in tqdm(images, desc="Extracting embeddings", leave=False):
            try:
                # Convert BGR to RGB for MTCNN
                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(rgb_img)
                
                # Detect face
                face_tensor = self.mtcnn(pil_img)
                
                if face_tensor is None:
                    continue
                
                # Extract embedding
                with torch.no_grad():
                    embedding = self.model(face_tensor.unsqueeze(0).to(self.device))
                
                embeddings.append(embedding.cpu().numpy()[0])
            
            except Exception as e:
                print(f"  ⚠ Error processing image: {e}")
                continue
        
        return embeddings
    
    def capture_and_process(self):
        """
        Main loop: Capture dari webcam, augmentasi, extract
        """
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Cannot open webcam")
            return
        
        print("\n" + "=" * 60)
        print("INTEGRATED DATA COLLECTION")
        print("=" * 60)
        print(f"👤 User ID: {self.user_id}")
        print(f"📊 Current embeddings: {len(self.embeddings_db[self.user_id])}")
        print("\n[CONTROLS]")
        print("  SPACE     = Capture & process photo")
        print("  q         = Quit & save")
        print("\n" + "=" * 60 + "\n")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Resize untuk display
            display = cv2.resize(frame, (640, 480))
            
            # Show info
            cv2.putText(display, "Press SPACE to capture", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(display, f"Total embeddings: {len(self.embeddings_db[self.user_id])}", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow("Data Collection - Press SPACE to capture, 'q' to quit", display)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord(' '):  # SPACE
                print(f"\n✓ Photo captured! Processing...")
                self.process_photo(frame)
        
        cap.release()
        cv2.destroyAllWindows()
        
        # Save embeddings
        self.save_embeddings()
    
    def process_photo(self, img):
        """
        Process 1 foto:
        1. Augmentasi → 50 variasi
        2. Extract embedding semua variasi
        3. Save ke database
        """
        print(f"  [1/3] Generating {self.augmentations_per_photo} augmentations...")
        augmented_images = self.generate_augmentations(img)
        print(f"      ✓ Generated {len(augmented_images)} augmented images")
        
        print(f"  [2/3] Extracting embeddings...")
        embeddings = self.extract_embeddings(augmented_images)
        print(f"      ✓ Extracted {len(embeddings)} embeddings")
        
        if embeddings:
            print(f"  [3/3] Saving to database...")
            self.embeddings_db[self.user_id].extend(embeddings)
            print(f"      ✓ Total embeddings for {self.user_id}: {len(self.embeddings_db[self.user_id])}")
            print(f"\n✅ Photo processed successfully!\n")
        else:
            print(f"      ❌ No embeddings extracted!")
    
    def save_embeddings(self):
        """Save embeddings ke file"""
        with open(self.embeddings_path, 'wb') as f:
            pickle.dump(self.embeddings_db, f)
        print(f"\n✅ SAVED: {len(self.embeddings_db[self.user_id])} embeddings untuk user {self.user_id}")
        print(f"📁 Path: {self.embeddings_path}")


if __name__ == "__main__":
    import sys
    
    # Parse user ID
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
    else:
        user_id = input("Enter User ID (e.g., '1', 'john', 'user_2'): ").strip()
        if not user_id:
            user_id = "1"
    
    try:
        collector = IntegratedDataCollector(user_id)
        collector.capture_and_process()
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
