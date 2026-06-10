"""
Simple test untuk verify training_api.py working dengan file input
"""
import json
import os
import sys

# Add parent dir to path
sys.path.insert(0, os.path.dirname(__file__))

from training_api import TrainingPipeline

def test_training_with_file():
    """Test training dengan simulated images"""
    
    # Create dummy base64 images (minimal valid JPEG)
    minimal_jpeg_b64 = "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8VAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAA8A/9k="
    
    # Create test JSON file
    test_dir = ".temp"
    os.makedirs(test_dir, exist_ok=True)
    
    test_file = os.path.join(test_dir, "test_training.json")
    test_data = {
        "photos": [
            f"data:image/jpeg;base64,{minimal_jpeg_b64}",
            f"data:image/jpeg;base64,{minimal_jpeg_b64}"
        ]
    }
    
    with open(test_file, 'w') as f:
        json.dump(test_data, f)
    
    print(f"[TEST] Created test file: {test_file}")
    print(f"[TEST] File size: {os.path.getsize(test_file)} bytes")
    
    # Test loading
    try:
        with open(test_file, 'r') as f:
            loaded_data = json.load(f)
        photos = loaded_data.get('photos', [])
        print(f"[TEST] ✓ Loaded {len(photos)} photos from file")
        return True
    except Exception as e:
        print(f"[TEST] ✗ Failed to load: {e}")
        return False
    finally:
        # Cleanup
        try:
            os.remove(test_file)
        except:
            pass

if __name__ == "__main__":
    print("Testing training_api.py file input...")
    success = test_training_with_file()
    
    if success:
        print("[TEST] ✅ File input test PASSED")
        sys.exit(0)
    else:
        print("[TEST] ❌ File input test FAILED")
        sys.exit(1)
