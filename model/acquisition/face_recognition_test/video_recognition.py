"""
Face Recognition from Video - Real-time wajah detection dan recognition
Bisa dari webcam atau video file
"""
import pickle
import os
import numpy as np
import cv2
from scipy.spatial.distance import cosine, euclidean

from facenet_pytorch import MTCNN, InceptionResnetV1
import torch

from config import (
    EMBEDDINGS_PATH, SIMILARITY_THRESHOLD,
    DISTANCE_METRIC, MTCNN_DEVICE, FACENET_DEVICE
)


class VideoFaceRecognizer:
    def __init__(self):
        """Initialize MTCNN dan FaceNet model"""
        print("[INFO] Loading MTCNN model...")
        self.device = torch.device(FACENET_DEVICE)
        self.mtcnn = MTCNN(device=MTCNN_DEVICE, keep_all=True)
        
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
    
    def extract_embedding_from_face(self, face_tensor):
        """Extract embedding dari face tensor"""
        with torch.no_grad():
            embedding = self.model(face_tensor.to(self.device))
        return embedding.cpu().numpy()
    
    def calculate_similarity(self, emb1, emb2):
        """Hitung similarity antara 2 embedding"""
        if DISTANCE_METRIC == 'cosine':
            distance = cosine(emb1, emb2)
            similarity = 1 - distance
        else:  # euclidean
            distance = euclidean(emb1, emb2)
            similarity = 1 / (1 + distance)
        return similarity
    
    def recognize_embedding(self, embedding):
        """Recognize embedding dan return best match"""
        best_match = None
        best_similarity = 0
        
        for user_id, user_embeddings in self.embeddings_db.items():
            similarities = []
            for user_emb in user_embeddings:
                sim = self.calculate_similarity(embedding, user_emb)
                similarities.append(sim)
            
            avg_similarity = np.mean(similarities)
            
            if avg_similarity > best_similarity:
                best_similarity = avg_similarity
                best_match = (user_id, avg_similarity)
        
        if best_match and best_match[1] >= SIMILARITY_THRESHOLD:
            return best_match
        return None
    
    def process_video(self, video_source=0):
        """
        Process video dari webcam atau file
        
        Args:
            video_source: 0 untuk webcam, atau path ke video file
        """
        # Open video source
        cap = cv2.VideoCapture(video_source)
        
        if video_source == 0:
            print("[INFO] Membuka webcam...")
        else:
            print(f"[INFO] Membuka video: {video_source}")
        
        if not cap.isOpened():
            print("❌ Error: Tidak bisa buka webcam/video")
            return
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"✓ Video properties - FPS: {fps}, Resolution: {width}x{height}")
        print("\n[CONTROLS]")
        print("  'q' = Quit")
        print("  's' = Save current frame with annotations")
        print("  'p' = Pause/Resume")
        print("\n" + "=" * 60)
        
        frame_count = 0
        paused = False
        
        while True:
            if not paused:
                ret, frame = cap.read()
                
                if not ret:
                    print("❌ Video ended atau error membaca frame")
                    break
                
                frame_count += 1
                
                # Resize frame untuk faster processing (optional)
                display_frame = frame.copy()
                process_frame = cv2.resize(frame, (384, 384))
                
                # Convert BGR to RGB for MTCNN
                rgb_frame = cv2.cvtColor(process_frame, cv2.COLOR_BGR2RGB)
                
                # Detect faces
                boxes, probs = self.mtcnn.detect(rgb_frame, landmarks=False)
                
                # Extract faces dan embeddings
                if boxes is not None:
                    # Convert to tensor untuk embedding extraction
                    faces = self.mtcnn.extract(rgb_frame, boxes, save_path=None)
                    
                    if faces is not None:
                        embeddings = self.extract_embedding_from_face(faces)
                        
                        # Draw boxes dan recognize
                        for idx, (box, prob) in enumerate(zip(boxes, probs)):
                            if idx < len(embeddings):
                                embedding = embeddings[idx]
                                result = self.recognize_embedding(embedding)
                                
                                # Scale coordinates to original frame
                                scale_x = width / 384
                                scale_y = height / 384
                                x1, y1, x2, y2 = box
                                x1, y1, x2, y2 = int(x1 * scale_x), int(y1 * scale_y), int(x2 * scale_x), int(y2 * scale_y)
                                
                                # Draw box dan label
                                if result:
                                    user_id, similarity = result
                                    label = f"User {user_id} ({similarity:.2f})"
                                    color = (0, 255, 0)  # Green = recognized
                                else:
                                    label = "Unknown"
                                    color = (0, 0, 255)  # Red = not recognized
                                
                                cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, 2)
                                cv2.putText(display_frame, label, (x1, y1 - 10),
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                else:
                    label = "No face detected"
                
                # Add info ke frame
                cv2.putText(display_frame, f"Frame: {frame_count}", (10, 30),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(display_frame, f"Faces: {len(boxes) if boxes is not None else 0}", (10, 70),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                if paused:
                    cv2.putText(display_frame, "PAUSED", (width - 150, 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Show frame
            cv2.imshow("Face Recognition - Press 'q' to quit", display_frame)
            
            # Handle keyboard
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\n✓ Closing...")
                break
            elif key == ord('p'):
                paused = not paused
                if paused:
                    print("[INFO] Paused")
                else:
                    print("[INFO] Resumed")
            elif key == ord('s'):
                filename = f"recognition_frame_{frame_count}.jpg"
                cv2.imwrite(filename, display_frame)
                print(f"✓ Frame saved: {filename}")
        
        cap.release()
        cv2.destroyAllWindows()
        print("\n[✓] Done!")


if __name__ == "__main__":
    import sys
    
    try:
        recognizer = VideoFaceRecognizer()
        
        # Check command line args
        if len(sys.argv) > 1:
            video_path = sys.argv[1]
            print(f"Processing video file: {video_path}")
            recognizer.process_video(video_path)
        else:
            print("Starting webcam...")
            recognizer.process_video(0)  # 0 untuk webcam
    
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print(f"\n📝 Pastikan sudah jalankan embedding_extractor/main.py terlebih dahulu!")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
