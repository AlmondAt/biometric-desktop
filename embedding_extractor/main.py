"""
Script Ekstrak Embedding Wajah
Membaca foto dari folder photos/<nama_user>/ dan menghasilkan embeddings.pkl

Usage:
    python main.py
"""

import cv2
import os
import numpy as np
import glob
import argparse
from mtcnn_utils import detect_face_mtcnn
from facenet_utils import preprocess_face, extract_embedding, save_embeddings
from config import PHOTOS_ROOT, EMBEDDINGS_PATH, VERBOSE


def extract_embeddings(photos_root=PHOTOS_ROOT, output_path=EMBEDDINGS_PATH, verbose=VERBOSE):
    """
    Ekstrak embedding dari semua foto pengguna
    
    Args:
        photos_root (str): Root folder yang berisi subfolder <nama_user>
        output_path (str): Path file output embeddings.pkl
        verbose (bool): Tampilkan progress detail
        
    Returns:
        dict: Dictionary nama_user -> list embeddings
    """
    
    # Pastikan folder photos ada
    if not os.path.exists(photos_root):
        print(f"[ERROR] Folder {photos_root} tidak ditemukan!")
        print(f"[INFO] Membuat folder baru di {photos_root}")
        os.makedirs(photos_root, exist_ok=True)
        print(f"[INFO] Silakan letakkan foto di subfolder: {photos_root}/<nama_user>/")
        return {}
    
    embeddings_dict = {}
    user_folders = sorted([f for f in os.listdir(photos_root) 
                          if os.path.isdir(os.path.join(photos_root, f))])
    
    if not user_folders:
        print(f"[ERROR] Tidak ada subfolder user di {photos_root}")
        print(f"[INFO] Format folder: {photos_root}/<nama_user>/")
        return {}
    
    print(f"[INFO] Ditemukan {len(user_folders)} user: {user_folders}\n")
    
    for user_idx, user_name in enumerate(user_folders, 1):
        photo_dir = os.path.join(photos_root, user_name)
        photo_paths = sorted(glob.glob(os.path.join(photo_dir, '*.jpg')))
        
        if not photo_paths:
            photo_paths += sorted(glob.glob(os.path.join(photo_dir, '*.png')))
        
        if not photo_paths:
            print(f"[{user_idx}/{len(user_folders)}] User '{user_name}' - Tidak ada foto")
            continue
        
        print(f"[{user_idx}/{len(user_folders)}] User: {user_name} | {len(photo_paths)} foto")
        
        embeddings = []
        failed_count = 0
        
        for i, photo_path in enumerate(photo_paths, 1):
            try:
                image = cv2.imread(photo_path)
                if image is None:
                    if verbose:
                        print(f"  [{i}/{len(photo_paths)}] ⚠️  Gagal membaca file: {os.path.basename(photo_path)}")
                    failed_count += 1
                    continue
                
                # Deteksi wajah
                face_img, bbox = detect_face_mtcnn(image)
                if face_img is None:
                    if verbose:
                        print(f"  [{i}/{len(photo_paths)}] ⚠️  Tidak ada wajah di: {os.path.basename(photo_path)}")
                    failed_count += 1
                    continue
                
                # Preprocess
                face_tensor = preprocess_face(face_img)
                if face_tensor is None:
                    if verbose:
                        print(f"  [{i}/{len(photo_paths)}] ⚠️  Gagal preprocess: {os.path.basename(photo_path)}")
                    failed_count += 1
                    continue
                
                # Ekstrak embedding
                embedding = extract_embedding(face_tensor)
                if embedding is None:
                    if verbose:
                        print(f"  [{i}/{len(photo_paths)}] ⚠️  Gagal ekstrak embedding: {os.path.basename(photo_path)}")
                    failed_count += 1
                    continue
                
                embeddings.append(embedding)
                if verbose:
                    print(f"  [{i}/{len(photo_paths)}] ✓ {os.path.basename(photo_path)}")
                    
            except Exception as e:
                if verbose:
                    print(f"  [{i}/{len(photo_paths)}] ❌ Error: {str(e)}")
                failed_count += 1
                continue
        
        if len(embeddings) > 0:
            embeddings_dict[user_name] = embeddings
            success_rate = len(embeddings) / len(photo_paths) * 100
            print(f"  ✓ Sukses: {user_name} ({len(embeddings)}/{len(photo_paths)} foto, {success_rate:.0f}%)\n")
        else:
            print(f"  ❌ Gagal: {user_name} (0 embedding valid)\n")
    
    if len(embeddings_dict) == 0:
        print("[ERROR] Tidak ada embedding yang berhasil diekstrak!")
        return {}
    
    # Simpan ke file
    save_embeddings(embeddings_dict, output_path)
    print(f"\n[SUCCESS] Berhasil menyimpan embedding ke {output_path}")
    print(f"[INFO] Total: {len(embeddings_dict)} user disimpan")
    
    # Print statistik
    total_embeddings = sum(len(emb) for emb in embeddings_dict.values())
    print(f"[INFO] Total: {total_embeddings} embedding")
    
    return embeddings_dict


def main():
    parser = argparse.ArgumentParser(description='Ekstrak embedding wajah dari folder foto')
    parser.add_argument('--photos', type=str, default=PHOTOS_ROOT,
                       help=f'Path folder foto (default: {PHOTOS_ROOT})')
    parser.add_argument('--output', type=str, default=EMBEDDINGS_PATH,
                       help=f'Path output embeddings.pkl (default: {EMBEDDINGS_PATH})')
    parser.add_argument('--verbose', action='store_true', default=VERBOSE,
                       help='Tampilkan detail progress')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("  EKSTRAK EMBEDDING WAJAH (FaceNet + MTCNN)")
    print("=" * 60)
    print(f"Input folder:  {args.photos}")
    print(f"Output file:   {args.output}")
    print("=" * 60 + "\n")
    
    extract_embeddings(args.photos, args.output, args.verbose)


if __name__ == "__main__":
    main()
