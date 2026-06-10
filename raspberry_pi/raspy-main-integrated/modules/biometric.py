#!/usr/bin/env python3
"""
Biometric Module - Fingerprint and Face Recognition
Refactored from main_no_gui.py
"""

import cv2
import time
import sqlite3
import pickle
import numpy as np
import subprocess
import tempfile
import os
import shutil


class BiometricAuth:
    def __init__(self, config, logger=None):
        self.config = config
        self.logger = logger
        
        # Paths from config
        self.db_path = config.get('database', {}).get('sqlite_path', 'biometrics.db')
        self.embeddings_path = config.get('database', {}).get('embeddings_path', 'database/embeddings.pkl')
        
        # Fingerprint settings
        self.fp_port = config.get('serial', {}).get('fingerprint_port', '/dev/ttyUSB0')
        self.fp_baudrate = config.get('serial', {}).get('fingerprint_baudrate', 57600)
        self.fp_timeout = config.get('biometric', {}).get('fingerprint_timeout', 12)
        
        # Face recognition settings
        self.face_threshold = config.get('biometric', {}).get('face_threshold', 0.7)
        self.face_timeout = config.get('biometric', {}).get('face_timeout', 15)
        self.stable_frames = config.get('biometric', {}).get('stable_frames', 3)
        
        # Camera settings
        self.camera_devices = config.get('camera', {}).get('devices', ['/dev/video0', 0])
        # Option to use rpicam CLI tool instead of OpenCV capture (fallback)
        self.use_rpicam = config.get('camera', {}).get('use_rpicam', False)
        self.rpicam_timeout = config.get('camera', {}).get('rpicam_timeout', 12)
        
        # Initialize components
        self.fingerprint_sensor = None
        self.cap = None
        self.face_embeddings = None
        # Last face verification error code (string) for callers to inspect
        self.last_face_error = None
        
        # Load face recognition modules
        self._load_face_modules()
        
    def _load_face_modules(self):
        """Load MTCNN and ArcFace modules"""
        try:
            from face.mtcnn_utils import detect_face_mtcnn
            from face.arcface_utils import (
                preprocess_face, 
                extract_embedding, 
                compute_similarity, 
                load_embeddings
            )
            
            self.detect_face = detect_face_mtcnn
            self.preprocess_face = preprocess_face
            self.extract_embedding = extract_embedding
            self.compute_similarity = compute_similarity
            self.load_embeddings = load_embeddings
            
            # Load embeddings
            self.face_embeddings = self.load_embeddings(self.embeddings_path)
            
            if self.logger:
                self.logger.info("Face recognition modules loaded successfully")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to load face recognition modules: {e}")
            return False
    
    def initialize_fingerprint_sensor(self):
        """Initialize fingerprint sensor"""
        if self.logger:
            self.logger.info("Initializing fingerprint sensor...")
        
        try:
            from pyfingerprint.pyfingerprint import PyFingerprint
            
            sensor = PyFingerprint(
                self.fp_port, 
                self.fp_baudrate, 
                0xFFFFFFFF, 
                0x00000000
            )
            
            if not sensor.verifyPassword():
                raise ValueError("Fingerprint sensor password incorrect")
            
            self.fingerprint_sensor = sensor
            
            if self.logger:
                self.logger.info("Fingerprint sensor initialized")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Fingerprint sensor initialization failed: {e}")
            self.fingerprint_sensor = None
            return False
    
    def initialize_camera(self):
        """Initialize camera"""
        if self.cap and self.cap.isOpened():
            return True

        # If configured to use rpicam only, verify the CLI binary can produce one frame
        if self.use_rpicam:
            try:
                test = self._capture_with_rpicam(timeout_s=self.rpicam_timeout)
                if test is not None:
                    if self.logger:
                        self.logger.info("Camera available via rpicam")
                    # We don't hold a cv2.VideoCapture when using rpicam
                    self.cap = None
                    return True
                else:
                    if self.logger:
                        self.logger.error("rpicam found but could not capture a frame")
                    return False
            except Exception as e:
                if self.logger:
                    self.logger.error(f"rpicam test capture failed: {e}")
                return False
        # Try multiple backends and warm-up reads. Some camera drivers
        # on Raspberry Pi need a specific backend (V4L2 or GStreamer) or
        # a few warm-up frames before read() returns data.
        backends = []
        try:
            backends = [cv2.CAP_V4L2, cv2.CAP_GSTREAMER, cv2.CAP_ANY]
        except Exception:
            backends = [cv2.CAP_ANY]

        width = self.config.get('camera', {}).get('width', 640)
        height = self.config.get('camera', {}).get('height', 480)

        for device in self.camera_devices:
            for backend in backends:
                try:
                    cap = cv2.VideoCapture(device, backend)
                    if not cap.isOpened():
                        # try next backend
                        if self.logger:
                            self.logger.debug(f"Camera open failed for {device} backend={backend}")
                        continue

                    # set desired resolution
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

                    # warm-up: read a few frames
                    ok = False
                    for i in range(6):
                        ret, frame = cap.read()
                        if ret and frame is not None:
                            ok = True
                            break
                        time.sleep(0.05)

                    if not ok:
                        # streaming not producing frames with this backend
                        cap.release()
                        if self.logger:
                            self.logger.warning(f"No frames from camera {device} using backend {backend}")
                        continue

                    # keep this capture
                    self.cap = cap
                    if self.logger:
                        self.logger.info(f"Camera initialized: {device} (backend={backend})")
                    return True

                except Exception as e:
                    if self.logger:
                        self.logger.warning(f"Failed to open camera {device} with backend {backend}: {e}")
                    try:
                        cap.release()
                    except Exception:
                        pass
                    continue

        if self.logger:
            self.logger.error("No camera device available or no frames could be captured")
        return False

    def _capture_with_rpicam(self, width=None, height=None, timeout_s=None):
        """Capture a single JPEG using the rpicam-jpeg CLI and return an OpenCV BGR image.

        Returns None on failure.
        """
        if timeout_s is None:
            timeout_s = self.rpicam_timeout

        # Find rpicam binary
        rpicam_bin = shutil.which('rpicam-jpeg')
        if not rpicam_bin:
            # try plain command name
            rpicam_bin = 'rpicam-jpeg'

        tmpf = None
        try:
            tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            tmpf = tmp.name
            tmp.close()

            # rpicam-jpeg supports a simple CLI; avoid passing unknown flags
            # Convert timeout_s to milliseconds for rpicam-jpeg --timeout parameter
            rpicam_timeout_ms = int(timeout_s * 1000) if timeout_s else 10000
            cmd = [rpicam_bin, '--timeout', str(rpicam_timeout_ms), '-o', tmpf]

            # Run the command with a timeout (add buffer to process timeout)
            try:
                proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout_s+5)
            except subprocess.TimeoutExpired as e:
                if self.logger:
                    stderr_msg = e.stderr.decode(errors='ignore') if e.stderr else '(no stderr)'
                    self.logger.warning(f"rpicam-jpeg timed out after {timeout_s}s: {stderr_msg}")
                return None

            if proc.returncode != 0:
                if self.logger:
                    stdout_msg = proc.stdout.decode(errors='ignore')
                    stderr_msg = proc.stderr.decode(errors='ignore')
                    self.logger.warning(f"rpicam-jpeg failed code {proc.returncode}: stdout={stdout_msg} stderr={stderr_msg}")
                return None

            # load with OpenCV
            img = cv2.imread(tmpf)
            return img

        except Exception as e:
            if self.logger:
                self.logger.error(f"rpicam capture error: {e}")
            return None
        finally:
            try:
                if tmpf and os.path.exists(tmpf):
                    os.remove(tmpf)
            except Exception:
                pass
    
    def scan_fingerprint(self, timeout_seconds=None):
        """
        Scan fingerprint and return user info
        
        Args:
            timeout_seconds: Override default timeout
            
        Returns:
            tuple: (success: bool, user_id: str, user_name: str)
        """
        if timeout_seconds is None:
            timeout_seconds = self.fp_timeout
        
        # Initialize sensor if needed
        if not self.fingerprint_sensor:
            if not self.initialize_fingerprint_sensor():
                return False, None, None
        
        if self.logger:
            self.logger.info("Waiting for fingerprint...")
        
        start_time = time.time()
        
        try:
            # Wait for finger placement (no timeout)
            while True:
                if time.time() - start_time > timeout_seconds:
                    if self.logger:
                        self.logger.warning("Fingerprint scan timeout")
                    return False, None, None
                
                if self.fingerprint_sensor.readImage():
                    # Finger detected, start processing
                    if self.logger:
                        self.logger.debug("Finger detected, processing...")
                    
                    self.fingerprint_sensor.convertImage(0x01)
                    result = self.fingerprint_sensor.searchTemplate()
                    
                    position = result[0]
                    
                    if position >= 0:
                        # Match found, get user from database
                        conn = sqlite3.connect(self.db_path)
                        c = conn.cursor()
                        # Select primary user id and name for the matched fingerprint position
                        c.execute("SELECT id, name, fingerprint_id FROM users WHERE fingerprint_id=?", (position,))
                        data = c.fetchone()
                        conn.close()

                        if data:
                            user_id = data[0]
                            user_name = data[1]

                            if self.logger:
                                self.logger.info(f"Fingerprint matched: {user_name} (fingerprint pos: {position}, user id: {user_id})")

                            # Return canonical user id (string) and name
                            return True, str(user_id), user_name
                        else:
                            if self.logger:
                                self.logger.warning(f"Fingerprint matched (pos: {position}) but user not in database")
                            return False, None, None
                    else:
                        if self.logger:
                            self.logger.warning("Fingerprint not matched")
                        return False, None, None
                
                time.sleep(0.1)
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Fingerprint scan error: {e}")
            self.fingerprint_sensor = None
            return False, None, None
    
    def verify_face(self, user_name, timeout_seconds=None):
        """
        Verify face against registered user (by username)
        """
        if timeout_seconds is None:
            timeout_seconds = self.face_timeout
        
        # Reset error
        self.last_face_error = None
        
        # Check if face modules are loaded
        if not hasattr(self, 'detect_face') or self.detect_face is None:
            if self.logger:
                self.logger.error("Face recognition modules not loaded")
            self.last_face_error = 'modules_not_loaded'
            return False
        
        # Reload embeddings setiap verifikasi
        self.face_embeddings = self.load_embeddings(self.embeddings_path)
        
        if not self.face_embeddings:
            if self.logger:
                self.logger.error("Face embeddings not loaded")
            self.last_face_error = 'no_embedding'
            return False
        
        # Gunakan username sebagai key
        user_key = str(user_name)
        
        if user_key not in self.face_embeddings:
            if self.logger:
                self.logger.error(f"User '{user_key}' not found in embeddings")
            self.last_face_error = 'no_embedding'
            return False
        
        # Initialize camera
        if not self.initialize_camera():
            if self.logger:
                self.logger.error("Camera not available")
            self.last_face_error = 'camera_unavailable'
            return False
        
        if self.logger:
            self.logger.info(f"Verifying face for user: {user_key}")
        
        start_time = time.time()
        stable_count = 0
        failed_count = 0
        max_failed = 10
        
        while time.time() - start_time < timeout_seconds:
            frame = None
            ret = False
            
            # Try to read frame
            if self.cap is not None:
                ret, frame = self.cap.read()
            elif self.use_rpicam:
                # RPiCam capture (synchronous, blocking ~10s per capture)
                frame = self._capture_with_rpicam()
                ret = frame is not None
                if self.logger and ret:
                    self.logger.debug(f"[RPiCam] Frame captured: {frame.shape}")
            
            # If frame read failed, just continue retrying
            if not ret or frame is None:
                failed_count += 1
                if self.logger:
                    self.logger.debug(f"[FRAME] Capture failed (failed_count={failed_count})")
                
                # If too many consecutive failures, stop trying
                if failed_count >= max_failed:
                    if self.logger:
                        self.logger.warning(
                            f"Too many frame capture failures for {user_key}"
                        )
                    self.last_face_error = 'frame_capture_failed'
                    return False
                
                time.sleep(0.2)
                continue
            
            # Detect face in frame
            face_img, bbox = self.detect_face(frame)
            
            if face_img is not None:
                face_tensor = self.preprocess_face(face_img)
                
                if face_tensor is not None:
                    emb = self.extract_embedding(face_tensor)
                    
                    # Check if embedding extraction was successful
                    if emb is None:
                        if self.logger:
                            self.logger.debug("Embedding extraction failed")
                        failed_count += 1
                    else:
                        # Reset failed count on successful embedding
                        failed_count = 0
                        
                        ref_embeddings = self.face_embeddings[user_key]
                        
                        if isinstance(ref_embeddings, list):
                            similarities = [
                                self.compute_similarity(emb, ref)
                                for ref in ref_embeddings
                            ]
                            max_similarity = max(similarities)
                        else:
                            max_similarity = self.compute_similarity(emb, ref_embeddings)
                        
                        if self.logger:
                            self.logger.debug(
                                f"[FACE] Similarity: {max_similarity:.4f}, "
                                f"stable: {stable_count}/{self.stable_frames}"
                            )
                        
                        if max_similarity > self.face_threshold:
                            stable_count += 1
                            
                            if stable_count >= self.stable_frames:
                                if self.logger:
                                    self.logger.info(
                                        f"✓ Face verified for {user_key} "
                                        f"(similarity: {max_similarity:.4f})"
                                    )
                                return True
                        else:
                            # Similarity too low, reset stable count
                            stable_count = 0
                            if self.logger:
                                self.logger.debug(
                                    f"Similarity {max_similarity:.4f} < threshold {self.face_threshold}"
                                )
                else:
                    if self.logger:
                        self.logger.debug("Face preprocessing failed")
                    failed_count += 1
            else:
                # No face detected
                if self.logger:
                    self.logger.debug("No face detected in frame")
                failed_count += 1
                
                # If too many consecutive failures with no faces, stop trying
                if failed_count >= max_failed:
                    if self.logger:
                        self.logger.warning(
                            f"Too many failed attempts for {user_key}"
                        )
                    self.last_face_error = 'no_faces_detected'
                    return False
            
            time.sleep(0.3)
        
        if self.logger:
            self.logger.warning(f"Face verification timeout for {user_key}")
        
        self.last_face_error = 'timeout'
        return False
    
    def capture_frame(self):
        """
        Capture a single frame from camera
        
        Returns:
            numpy.ndarray: Captured frame or None
        """
        if not self.initialize_camera():
            return None
        # If using OpenCV VideoCapture, do a small retry loop
        if self.cap is not None:
            for i in range(4):
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    return frame
                time.sleep(0.05)

            if self.logger:
                self.logger.error("Failed to capture frame after retries")
            return None

        # If configured to use rpicam, try CLI capture
        if self.use_rpicam:
            for i in range(3):
                frame = self._capture_with_rpicam()
                if frame is not None:
                    return frame
                time.sleep(0.1)

            if self.logger:
                self.logger.error("Failed to capture frame with rpicam after retries")
            return None

        # No camera available
        if self.logger:
            self.logger.error("No camera available to capture frame")
        return None
    
    def enroll_fingerprint(self, user_id):
        """
        Stub for fingerprint enrollment
        Enrollment is performed separately using fingerprint_wrapper.py
        
        Args:
            user_id: User ID (string)
            
        Returns:
            tuple: (False, "Enrollment via CLI tool")
        """
        if self.logger:
            self.logger.warning(f"Fingerprint enrollment not available in main system for user {user_id}")
            self.logger.info("Use: python fingerprint/fingerprint_wrapper.py --user_id {user_id}")
        return False, "Use fingerprint_wrapper.py tool"
    
    def enroll_face(self, user_id):
        """
        Stub for face enrollment
        Enrollment is performed separately using capture_face.py
        
        Args:
            user_id: User ID (string)
            
        Returns:
            tuple: (False, "Enrollment via CLI tool")
        """
        if self.logger:
            self.logger.warning(f"Face enrollment not available in main system for user {user_id}")
            self.logger.info("Use: python face/capture_face.py --name <user_name>")
        return False, "Use capture_face.py tool"
    
    def cleanup(self):
        """Release resources"""
        if self.cap:
            self.cap.release()
            self.cap = None
        
        if self.logger:
            self.logger.info("Biometric resources released")
