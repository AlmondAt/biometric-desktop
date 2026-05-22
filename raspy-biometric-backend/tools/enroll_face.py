#!/usr/bin/env python3
"""
CLI Tool - Enroll Face via Webcam
Capture 10 photos per user untuk face recognition database
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import cv2
    import numpy as np
    from modules.db_manager import BiometricDatabase
except ImportError as e:
    print(f"❌ Error: {e}")
    print("Make sure dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)


def extract_face_embedding(frame, use_dummy=False):
    """
    Extract face embedding menggunakan FaceNet
    Untuk production: gunakan facenet-pytorch
    Untuk demo: return random 512-dim vector
    """
    if use_dummy:
        # Dummy mode: return random embedding (untuk testing tanpa GPU)
        return np.random.randn(512)
    
    try:
        # Production: use facenet-pytorch
        from facenet_pytorch import InceptionResnetV1, MTCNN
        import torch
        
        # Load models
        mtcnn = MTCNN(image_size=160, keep_all=False)
        model = InceptionResnetV1(pretrained='vggface2').eval()
        
        # Convert to tensor
        img_tensor = torch.from_numpy(frame).permute(2, 0, 1).unsqueeze(0).float()
        
        # MTCNN face detection
        face = mtcnn(img_tensor)
        if face is None:
            return None
        
        # Extract embedding
        with torch.no_grad():
            embedding = model(face)
        
        return embedding.numpy().flatten()
    
    except Exception as e:
        print(f"⚠️  Warning: {e}")
        print("Using dummy mode for testing")
        return None


def main():
    print("""
╔════════════════════════════════════════════╗
║      FACE ENROLLMENT TOOL                  ║
║      Capture 10 Photos for Database        ║
╚════════════════════════════════════════════╝
    """)
    
    # Input user info
    user_id = input("📝 Masukkan User ID (contoh: user_001): ").strip()
    if not user_id:
        print("❌ User ID tidak boleh kosong")
        return
    
    user_name = input("📝 Masukkan Nama Lengkap: ").strip()
    if not user_name:
        print("❌ Nama tidak boleh kosong")
        return
    
    # Initialize database
    db = BiometricDatabase('biometrics.db')
    
    # Check if user exists
    if db.get_user(user_id):
        print(f"❌ User ID {user_id} sudah ada di database")
        return
    
    # Add user ke database
    success, msg = db.add_user(user_id, user_name)
    if not success:
        print(f"❌ Error: {msg}")
        return
    
    print(f"✅ User {user_name} ditambahkan ke database")
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Kamera tidak ditemukan!")
        return
    
    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("""
╔════════════════════════════════════════════╗
║      CAPTURE PHOTOS                       ║
║  SPACE = Capture, ESC = Exit              ║
╚════════════════════════════════════════════╝
    """)
    
    captured_photos = 0
    embeddings = []
    target_photos = 10
    use_dummy = False
    
    while captured_photos < target_photos:
        ret, frame = cap.read()
        if not ret:
            print("❌ Error reading frame from camera")
            break
        
        # Flip frame
        frame = cv2.flip(frame, 1)
        
        # Display info
        cv2.putText(frame, f"Photos: {captured_photos}/{target_photos}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "SPACE=Capture, ESC=Exit", (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
        
        cv2.imshow('Face Enrollment', frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord(' '):
            # Capture photo
            try:
                # Extract embedding
                embedding = extract_face_embedding(frame, use_dummy=use_dummy)
                
                if embedding is not None:
                    embeddings.append(embedding)
                    captured_photos += 1
                    print(f"✅ Photo {captured_photos}/{target_photos} captured")
                else:
                    print("⚠️  Wajah tidak terdeteksi, coba lagi")
            
            except Exception as e:
                print(f"⚠️  Error capturing: {e}")
                use_dummy = True  # Fall back to dummy mode
                embedding = extract_face_embedding(frame, use_dummy=True)
                embeddings.append(embedding)
                captured_photos += 1
                print(f"✅ Photo {captured_photos}/{target_photos} captured (dummy mode)")
        
        elif key == 27:  # ESC
            print("❌ Enrollment dibatalkan")
            cap.release()
            cv2.destroyAllWindows()
            return
    
    cap.release()
    cv2.destroyAllWindows()
    
    # Store embeddings
    if len(embeddings) > 0:
        success, msg = db.store_embeddings(user_id, embeddings, source='direct')
        
        if success:
            print(f"\n✅ Enrollment berhasil!")
            print(f"   User ID: {user_id}")
            print(f"   Name: {user_name}")
            print(f"   Embeddings: {len(embeddings)}")
            
            # Show stats
            stats = db.get_stats()
            print(f"\n📊 Database Status:")
            print(f"   Total Users: {stats['total_users']}")
            print(f"   Active Users: {stats['active_users']}")
            print(f"   Total Embeddings: {stats['total_embeddings']}")
        else:
            print(f"❌ Error storing embeddings: {msg}")
    else:
        print("❌ No embeddings captured")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
