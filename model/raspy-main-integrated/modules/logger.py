#!/usr/bin/env python3
"""
Logger Module - Centralized logging and image saving
"""

import os
import cv2
import logging
from datetime import datetime
from pathlib import Path


class SystemLogger:
    def __init__(self, config):
        self.log_folder = config.get('logging', {}).get('log_folder', 'logs')
        self.events_log = config.get('logging', {}).get('events_log', 'logs/events.log')
        self.access_log = config.get('logging', {}).get('access_log', 'logs/access.log')
        self.unknown_folder = config.get('logging', {}).get('unknown_faces', 'logs/unknown_faces')
        
        # Create directories
        os.makedirs(self.log_folder, exist_ok=True)
        os.makedirs(self.unknown_folder, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(self.events_log),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def info(self, message):
        """Log info message"""
        self.logger.info(message)
    
    def error(self, message):
        """Log error message"""
        self.logger.error(message)
    
    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)
    
    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)
    
    def save_image(self, img, tag="capture"):
        """
        Save image to logs folder
        
        Args:
            img: OpenCV image (numpy array)
            tag: Tag for filename (e.g., 'verified', 'failed', 'unknown')
            
        Returns:
            str: Path to saved image
        """
        if img is None:
            self.warning(f"save_image: Image is None, cannot save with tag '{tag}'")
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Determine folder based on tag
        if 'unknown' in tag or 'failed' in tag:
            folder = self.unknown_folder
        else:
            folder = self.log_folder
        
        filename = f"{tag}_{timestamp}.jpg"
        filepath = os.path.join(folder, filename)
        
        try:
            cv2.imwrite(filepath, img)
            self.info(f"Image saved: {filepath}")
            return filepath
        except Exception as e:
            self.error(f"Failed to save image: {e}")
            return None
    
    def log_access(self, user_id, user_name, status, method="biometric"):
        """
        Log door access attempt
        
        Args:
            user_id: User identifier
            user_name: User's name
            status: Access status (granted/denied)
            method: Authentication method
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(self.access_log, 'a') as f:
            f.write(f"[{timestamp}] User: {user_name} (ID: {user_id}), Status: {status}, Method: {method}\n")
        
        self.info(f"Access logged: {user_name} - {status}")
    
    def log_event(self, event_type, details):
        """
        Log system event
        
        Args:
            event_type: Type of event (e.g., 'emergency', 'error', 'attendance')
            details: Event details (dict or string)
        """
        if isinstance(details, dict):
            details_str = ", ".join([f"{k}={v}" for k, v in details.items()])
        else:
            details_str = str(details)
        
        self.info(f"[{event_type.upper()}] {details_str}")
    
    def log_failed_biometric(self, user_name, fingerprint_match, face_match, image_path=None):
        """
        Log failed biometric verification
        
        Args:
            user_name: User name (or None if unknown)
            fingerprint_match: Boolean, fingerprint match result
            face_match: Boolean, face match result
            image_path: Path to captured image
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        reason = []
        
        if not fingerprint_match:
            reason.append("fingerprint_failed")
        if not face_match:
            reason.append("face_failed")
        
        reason_str = ", ".join(reason) if reason else "unknown"
        
        self.warning(
            f"Failed verification: User={user_name or 'Unknown'}, "
            f"Reason={reason_str}, Image={image_path or 'N/A'}"
        )
