"""
Data Augmentation - Generate multiple pose variations dari foto
Dari 10 foto normal → 500 foto dengan berbagai angle, posisi, brightness, dll
"""
import os
import cv2
import numpy as np
from pathlib import Path
import random

class DataAugmentor:
    def __init__(self, input_dir, output_dir, augmentations_per_image=50):
        """
        Initialize augmentor
        
        Args:
            input_dir: Folder dengan original photos
            output_dir: Folder output untuk augmented photos
            augmentations_per_image: Jumlah augmentation per foto (default 50)
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.augmentations_per_image = augmentations_per_image
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"[Augmentor initialized]")
        print(f"Input: {input_dir}")
        print(f"Output: {output_dir}")
        print(f"Augmentations per image: {augmentations_per_image}")
    
    def rotate_image(self, img, angle):
        """Rotate image dengan angle (degrees)"""
        h, w = img.shape[:2]
        center = (w // 2, h // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(img, rotation_matrix, (w, h))
        return rotated
    
    def zoom_image(self, img, zoom_factor):
        """Zoom in/out"""
        h, w = img.shape[:2]
        new_h, new_w = int(h * zoom_factor), int(w * zoom_factor)
        
        if zoom_factor > 1:  # Zoom in - crop
            start_h = (new_h - h) // 2
            start_w = (new_w - w) // 2
            zoomed = cv2.resize(img, (new_w, new_h))
            return zoomed[start_h:start_h+h, start_w:start_w+w]
        else:  # Zoom out - pad
            zoomed = cv2.resize(img, (new_w, new_h))
            padded = np.full((h, w, 3), 128, dtype=np.uint8)
            pad_h = (h - new_h) // 2
            pad_w = (w - new_w) // 2
            padded[pad_h:pad_h+new_h, pad_w:pad_w+new_w] = zoomed
            return padded
    
    def adjust_brightness(self, img, factor):
        """Adjust brightness (0.5 = darker, 1.5 = brighter)"""
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
        matrix = np.float32([
            [1, 0, tx],
            [0, 1, ty]
        ])
        translated = cv2.warpAffine(img, matrix, (w, h))
        return translated
    
    def flip_image(self, img, direction='horizontal'):
        """Flip image"""
        if direction == 'horizontal':
            return cv2.flip(img, 1)
        elif direction == 'vertical':
            return cv2.flip(img, 0)
        else:
            return cv2.flip(img, -1)
    
    def gaussian_blur(self, img, kernel_size=(3, 3)):
        """Add slight blur (simulate different focus)"""
        return cv2.GaussianBlur(img, kernel_size, 0)
    
    def add_noise(self, img, noise_level=0.02):
        """Add Gaussian noise"""
        noise = np.random.normal(0, noise_level * 255, img.shape)
        noisy = np.clip(img.astype(np.float32) + noise, 0, 255)
        return noisy.astype(np.uint8)
    
    def augment_image(self, img_path, output_prefix):
        """
        Generate augmentations untuk 1 image
        Total: augmentations_per_image variations
        """
        img = cv2.imread(img_path)
        if img is None:
            print(f"❌ Failed to load: {img_path}")
            return 0
        
        augmented_count = 0
        
        # 1. Original (no augmentation)
        output_path = os.path.join(self.output_dir, f"{output_prefix}_{augmented_count:03d}.jpg")
        cv2.imwrite(output_path, img)
        augmented_count += 1
        
        # 2-8: Rotations (berbagai angle)
        angles = [10, 20, 30, -10, -20, -30, 15]
        for angle in angles:
            rotated = self.rotate_image(img, angle)
            output_path = os.path.join(self.output_dir, f"{output_prefix}_{augmented_count:03d}.jpg")
            cv2.imwrite(output_path, rotated)
            augmented_count += 1
        
        # 9-15: Zoom variations
        zoom_factors = [0.8, 0.9, 1.1, 1.2, 0.75, 1.15, 0.85]
        for zoom in zoom_factors:
            zoomed = self.zoom_image(img, zoom)
            output_path = os.path.join(self.output_dir, f"{output_prefix}_{augmented_count:03d}.jpg")
            cv2.imwrite(output_path, zoomed)
            augmented_count += 1
        
        # 16-22: Brightness
        brightness_factors = [0.6, 0.7, 0.8, 1.2, 1.3, 1.4, 0.9]
        for factor in brightness_factors:
            bright = self.adjust_brightness(img, factor)
            output_path = os.path.join(self.output_dir, f"{output_prefix}_{augmented_count:03d}.jpg")
            cv2.imwrite(output_path, bright)
            augmented_count += 1
        
        # 23-29: Contrast
        contrast_factors = [0.8, 0.9, 1.1, 1.2, 0.7, 1.3, 0.95]
        for factor in contrast_factors:
            contrast = self.adjust_contrast(img, factor)
            output_path = os.path.join(self.output_dir, f"{output_prefix}_{augmented_count:03d}.jpg")
            cv2.imwrite(output_path, contrast)
            augmented_count += 1
        
        # 30-36: Translations (geser posisi)
        h, w = img.shape[:2]
        translations = [
            (w//10, 0), (-w//10, 0), (0, h//10), (0, -h//10),
            (w//8, h//8), (-w//8, -h//8), (w//6, -h//6)
        ]
        for tx, ty in translations:
            translated = self.translate_image(img, tx, ty)
            output_path = os.path.join(self.output_dir, f"{output_prefix}_{augmented_count:03d}.jpg")
            cv2.imwrite(output_path, translated)
            augmented_count += 1
        
        # 37-40: Flip variations
        flipped_h = self.flip_image(img, 'horizontal')
        flipped_v = self.flip_image(img, 'vertical')
        flipped_both = self.flip_image(img, 'both')
        
        for aug_img in [flipped_h, flipped_v, flipped_both, flipped_h]:
            output_path = os.path.join(self.output_dir, f"{output_prefix}_{augmented_count:03d}.jpg")
            cv2.imwrite(output_path, aug_img)
            augmented_count += 1
        
        # 41-47: Blur (simulate different focus)
        blur_sizes = [(3, 3), (5, 5), (3, 3), (5, 5), (3, 3), (7, 7), (5, 5)]
        for kernel in blur_sizes:
            blurred = self.gaussian_blur(img, kernel)
            output_path = os.path.join(self.output_dir, f"{output_prefix}_{augmented_count:03d}.jpg")
            cv2.imwrite(output_path, blurred)
            augmented_count += 1
        
        # 48-50: Kombinasi transformasi (rotate + brightness)
        combinations = [
            (15, 1.2),   # Rotate + brighter
            (-15, 0.8),  # Rotate + darker
            (20, 1.1)    # Rotate + slight brightness
        ]
        for angle, bright_factor in combinations:
            rotated = self.rotate_image(img, angle)
            bright = self.adjust_brightness(rotated, bright_factor)
            output_path = os.path.join(self.output_dir, f"{output_prefix}_{augmented_count:03d}.jpg")
            cv2.imwrite(output_path, bright)
            augmented_count += 1
        
        return augmented_count
    
    def augment_all(self):
        """Augment semua foto di input directory"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}
        image_files = [
            f for f in os.listdir(self.input_dir)
            if os.path.splitext(f)[1].lower() in image_extensions
        ]
        
        if not image_files:
            print(f"❌ Tidak ada foto di {self.input_dir}")
            return
        
        print(f"\n{'=' * 60}")
        print(f"DATA AUGMENTATION")
        print(f"{'=' * 60}")
        print(f"📁 Found {len(image_files)} images")
        print(f"🎯 Target: {len(image_files) * self.augmentations_per_image} augmented images")
        print()
        
        total_augmented = 0
        
        for idx, img_file in enumerate(image_files, 1):
            img_path = os.path.join(self.input_dir, img_file)
            output_prefix = os.path.splitext(img_file)[0]
            
            count = self.augment_image(img_path, output_prefix)
            total_augmented += count
            
            print(f"[{idx}/{len(image_files)}] {img_file}: ✓ {count} variations generated")
        
        print(f"\n{'=' * 60}")
        print(f"✓ AUGMENTATION COMPLETE!")
        print(f"📊 Total augmented images: {total_augmented}")
        print(f"📁 Saved to: {self.output_dir}")
        print(f"{'=' * 60}\n")


if __name__ == "__main__":
    import sys
    
    # Default paths
    INPUT_DIR = "./augment_input"
    OUTPUT_DIR = "./augmented_photos"
    AUGMENTATIONS_PER_IMAGE = 50
    
    # Parse arguments
    if len(sys.argv) > 1:
        INPUT_DIR = sys.argv[1]
    if len(sys.argv) > 2:
        OUTPUT_DIR = sys.argv[2]
    if len(sys.argv) > 3:
        AUGMENTATIONS_PER_IMAGE = int(sys.argv[3])
    
    try:
        augmentor = DataAugmentor(INPUT_DIR, OUTPUT_DIR, AUGMENTATIONS_PER_IMAGE)
        augmentor.augment_all()
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
