"""
Training API - Digunakan oleh Electron app via subprocess
Menerima list base64 images → augmentasi → extract → save

Usage dari Node.js:
  python training_api.py <user_id> <images_json_file>
  
  oder old method (deprecated):
  python training_api.py <user_id> <images_json>
"""

import sys
import json
import base64
import pickle
import os
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
from tqdm import tqdm

from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
from config import FACENET_MODEL, USE_GPU


class TrainingPipeline:
    def __init__(self, embedding_key, embeddings_path='./embeddings.pkl', augmentations_per_photo=15, replace_existing=False):
        self.embedding_key = embedding_key
        self.embeddings_path = embeddings_path
        self.augmentations_per_photo = augmentations_per_photo
        self.replace_existing = replace_existing
        
        print(f"[INIT] Loading models...", flush=True)
        use_cuda = USE_GPU and torch.cuda.is_available()
        self.device = torch.device('cuda' if use_cuda else 'cpu')
        self.mtcnn = MTCNN(device=self.device, keep_all=False)
        self.model = InceptionResnetV1(pretrained=FACENET_MODEL, device=self.device)
        self.model.eval()
        
        # Load existing embeddings
        if os.path.exists(embeddings_path):
            with open(embeddings_path, 'rb') as f:
                self.embeddings_db = pickle.load(f)
        else:
            self.embeddings_db = {}
        
        if self.replace_existing or self.embedding_key not in self.embeddings_db:
            self.embeddings_db[self.embedding_key] = []
        
        print(
            f"[INIT] Ready on {self.device}. User {self.embedding_key} has {len(self.embeddings_db[self.embedding_key])} embeddings. "
            f"Using {self.augmentations_per_photo} augmentations/photo",
            flush=True,
        )
    
    def base64_to_cv2(self, base64_str):
        """Convert base64 to OpenCV image"""
        try:
            img_data = base64.b64decode(base64_str.split(',')[1] if ',' in base64_str else base64_str)
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return img
        except Exception as e:
            print(f"[ERROR] Failed to decode image: {e}", flush=True)
            return None
    
    def rotate_image(self, img, angle):
        h, w = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(img, M, (w, h))
    
    def zoom_image(self, img, zoom_factor):
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
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 2] = hsv[:, :, 2] * factor
        hsv[:, :, 2] = np.clip(hsv[:, :, 2], 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    
    def adjust_contrast(self, img, factor):
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
        l = lab[:, :, 0]
        l = (l - 50) * factor + 50
        l = np.clip(l, 0, 255)
        lab[:, :, 0] = l
        return cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)
    
    def translate_image(self, img, tx, ty):
        h, w = img.shape[:2]
        M = np.float32([[1, 0, tx], [0, 1, ty]])
        return cv2.warpAffine(img, M, (w, h))
    
    def flip_image(self, img, direction='horizontal'):
        if direction == 'horizontal':
            return cv2.flip(img, 1)
        return cv2.flip(img, -1)
    
    def gaussian_blur(self, img, kernel_size=(3, 3)):
        return cv2.GaussianBlur(img, kernel_size, 0)
    
    def generate_augmentations(self, img):
        """Generate augmentasi untuk memperkaya embedding."""
        augmentations = [img]
        
        for angle in [10, 20, 30, -10, -20, -30, 15]:
            augmentations.append(self.rotate_image(img, angle))
        
        for zoom in [0.8, 0.9, 1.1, 1.2, 0.75, 1.15, 0.85]:
            augmentations.append(self.zoom_image(img, zoom))
        
        for factor in [0.6, 0.7, 0.8, 1.2, 1.3, 1.4, 0.9]:
            augmentations.append(self.adjust_brightness(img, factor))
        
        for factor in [0.8, 0.9, 1.1, 1.2, 0.7, 1.3, 0.95]:
            augmentations.append(self.adjust_contrast(img, factor))
        
        h, w = img.shape[:2]
        for tx, ty in [(w//10, 0), (-w//10, 0), (0, h//10), (0, -h//10),
                       (w//8, h//8), (-w//8, -h//8), (w//6, -h//6)]:
            augmentations.append(self.translate_image(img, tx, ty))
        
        flipped_h = self.flip_image(img, 'horizontal')
        flipped_both = self.flip_image(img, 'both')
        for aug in [flipped_h, self.flip_image(img, 'vertical'), flipped_both, flipped_h]:
            augmentations.append(aug)
        
        for kernel in [(3, 3), (5, 5), (3, 3), (5, 5), (3, 3), (7, 7), (5, 5)]:
            augmentations.append(self.gaussian_blur(img, kernel))
        
        for angle, bright_factor in [(15, 1.2), (-15, 0.8), (20, 1.1)]:
            rotated = self.rotate_image(img, angle)
            bright = self.adjust_brightness(rotated, bright_factor)
            augmentations.append(bright)
        
        return augmentations[:self.augmentations_per_photo]
    
    def extract_embeddings(self, images):
        """Extract embeddings dari list images"""
        embeddings = []
        
        for idx, img in enumerate(images):
            try:
                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(rgb_img)
                
                face_tensor = self.mtcnn(pil_img)
                if face_tensor is None:
                    continue
                
                with torch.no_grad():
                    embedding = self.model(face_tensor.unsqueeze(0).to(self.device))
                
                embeddings.append(embedding.cpu().numpy()[0])
            except:
                pass
        
        return embeddings
    
    def process_images(self, base64_images):
        """Process list of base64 images"""
        total_photos = len(base64_images)
        total_embeddings_before = len(self.embeddings_db[self.embedding_key])
        
        print(f"[PROCESS] Processing {total_photos} photos", flush=True)
        
        for photo_idx, base64_str in enumerate(base64_images):
            photo_num = photo_idx + 1
            
            # Decode
            print(f"[PHOTO {photo_num}/{total_photos}] Decoding...", flush=True)
            img = self.base64_to_cv2(base64_str)
            if img is None:
                print(f"[PHOTO {photo_num}/{total_photos}] Failed to decode", flush=True)
                continue
            
            # Generate augmentations
            print(f"[PHOTO {photo_num}/{total_photos}] Generating {self.augmentations_per_photo} augmentations...", flush=True)
            augmented_images = self.generate_augmentations(img)
            
            # Extract embeddings
            print(f"[PHOTO {photo_num}/{total_photos}] Extracting embeddings...", flush=True)
            embeddings = self.extract_embeddings(augmented_images)
            
            if embeddings:
                self.embeddings_db[self.embedding_key].extend(embeddings)
                print(f"[PHOTO {photo_num}/{total_photos}] SUCCESS - {len(embeddings)} embeddings extracted", flush=True)
            else:
                print(f"[PHOTO {photo_num}/{total_photos}] FAILED - No embeddings extracted", flush=True)
        
        # Save
        print(f"[SAVE] Saving embeddings...", flush=True)
        with open(self.embeddings_path, 'wb') as f:
            pickle.dump(self.embeddings_db, f)
        
        total_embeddings_after = len(self.embeddings_db[self.embedding_key])
        added = total_embeddings_after - total_embeddings_before
        
        print(f"[COMPLETE] Added {added} embeddings for user {self.embedding_key}", flush=True)
        print(f"[COMPLETE] Total embeddings: {total_embeddings_after}", flush=True)
        print(json.dumps({
            'embeddingKey': self.embedding_key,
            'added': added,
            'total': total_embeddings_after
        }), flush=True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[ERROR] Usage: python training_api.py <payload_json_file_or_json>", flush=True)
        sys.exit(1)
    
    payload_input = sys.argv[1]
    
    try:
        if os.path.isfile(payload_input):
            print(f"[INPUT] Reading from file: {payload_input}", flush=True)
            with open(payload_input, 'r') as f:
                payload = json.load(f)
        else:
            print(f"[INPUT] Parsing JSON directly", flush=True)
            payload = json.loads(payload_input)

        if isinstance(payload, list):
            embedding_key = 'unknown-user'
            base64_images = payload
            embeddings_path = './embeddings.pkl'
            replace_existing = False
        else:
            embedding_key = payload.get('embeddingKey') or payload.get('userId') or payload.get('fullName')
            base64_images = payload.get('photos', [])
            embeddings_path = payload.get('embeddingsPath', './embeddings.pkl')
            replace_existing = bool(payload.get('replaceExisting', False))

        if not embedding_key:
            print('[ERROR] embeddingKey/fullName wajib diisi', flush=True)
            sys.exit(1)
        
        if not isinstance(base64_images, list) or len(base64_images) == 0:
            print("[ERROR] No valid images provided", flush=True)
            sys.exit(1)
        
        print(f"[INPUT] Got {len(base64_images)} images", flush=True)
        
        pipeline = TrainingPipeline(embedding_key, embeddings_path=embeddings_path, replace_existing=replace_existing)
        pipeline.process_images(base64_images)
        
        print("[SUCCESS] Training completed successfully", flush=True)
        sys.exit(0)
    
    except Exception as e:
        print(f"[ERROR] {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
