#!/usr/bin/env python3
"""
Lab Robotika 2025 - Integrated Attendance System
Raspberry Pi 5 + Arduino Nano + Biometric Sensors

Main Entry Point with State Machine
"""

import sys
import os
import time
import yaml
import signal
import json
import base64
import pickle
import sqlite3
import threading
from datetime import datetime
from enum import Enum, auto
from http.server import ThreadingHTTPServer

import numpy as np

# Add modules directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from modules.logger import SystemLogger
from modules.serial_nanonano import NanoSerial, find_arduino_port
from modules.biometric import BiometricAuth
from modules.absensi_utils import AbsensiManager
from modules.embedded_api import make_api_handler


class SystemState(Enum):
    """System states"""
    BOOT = auto()
    SPLASH = auto()
    IDLE = auto()
    TOUCH_ACTIVATED = auto()
    FINGERPRINT = auto()
    FACE = auto()
    # Enrollment / admin states
    ADMIN_PIN = auto()
    ENROLL_MENU = auto()
    ENROLL_INPUT_ID = auto()
    ENROLL_FINGERPRINT = auto()
    ENROLL_FACE = auto()
    ENROLL_CONFIRM = auto()
    MENU = auto()
    ATTENDANCE_JOB = auto()
    ATTENDANCE_DOMAIN = auto()
    ATTENDANCE_SHIFT_INPUT = auto()
    ATTENDANCE_CONFIRM = auto()
    ACCESS = auto()
    EMERGENCY = auto()
    ERROR = auto()


class LabAttendanceSystem:
    def __init__(self, config_path='config.yaml'):
        """Initialize the system"""
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize logger
        self.logger = SystemLogger(self.config)
        self.logger.info("=== Lab Robotika Attendance System Starting ===")
        
        # Initialize components
        self.serial = None
        self.biometric = None
        self.absensi = None
        
        # State machine
        self.state = SystemState.BOOT
        self.previous_state = None
        
        # Session data
        self.current_user_id = None
        self.current_user_name = None
        self.job_selection = None
        self.domain_selection = None
        self.input_buffer = ""
        self.state_before_emergency = None
        self.emergency_active = False
        self.emergency_release_at = None
        self.emergency_timer = None
        self.emergency_ignore_until = 0
        
        # Shift input data
        self.shift_input_buffer = ""
        self.shift_A = self.shift_B = self.shift_C = self.shift_D = self.shift_E = None
        
        # Job and domain codes from config
        self.job_codes = self.config.get('job_codes', {})
        self.domain_codes = self.config.get('domain_codes', {})

        # Runtime paths
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        database_cfg = self.config.get('database', {})
        self.db_path = self._resolve_runtime_path(
            database_cfg.get('sqlite_path', 'biometrics.db')
        )
        self.embeddings_path = self._resolve_runtime_path(
            database_cfg.get('embeddings_path', 'database/embeddings.pkl')
        )

        # Embedded API server configuration
        api_cfg = self.config.get('api', {})
        self.api_host = os.getenv('RASPY_API_HOST', str(api_cfg.get('host', '0.0.0.0')))
        self.api_port = int(os.getenv('RASPY_API_PORT', api_cfg.get('port', 5000)))
        self.api_server = None
        self.api_thread = None
        self.data_lock = threading.RLock()
        self.action_lock = threading.Lock()
        self.action_thread = None

        # Device status shared with desktop
        self.device_mode = 'boot'
        self.device_mode_updated_at = datetime.now()
        
        # Flags
        self.running = True
        self.system_active = False
        # Enrollment/admin helpers
        # Admin PIN for entering registration menu (set in config or default '1234')
        self.admin_pin = str(self.config.get('admin_pin', '1234'))
        # enroll_mode: 'both' | 'fingerprint' | 'face'
        self.enroll_mode = None
        # temporary storage during enrollment (e.g., user id/name)
        self.enroll_user_id = None
        self.enroll_user_name = None

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _resolve_runtime_path(self, path_value):
        """Resolve project-relative paths used by the runtime."""
        if not path_value:
            return self.base_dir
        if os.path.isabs(path_value):
            return path_value
        return os.path.join(self.base_dir, path_value)

    def _truncate_display_line(self, value, max_length=20):
        """Keep LCD text within a predictable width."""
        text = '' if value is None else str(value)
        return text[:max_length]

    def _set_device_mode(self, mode, detail=None, push_to_display=True):
        """Store and optionally display the externally visible device mode."""
        self.device_mode = str(mode or 'idle')
        self.device_mode_updated_at = datetime.now()

        if not push_to_display or not self.serial:
            return

        display_map = {
            'idle': [
                'Touch sensor',
                'untuk mulai',
                '',
                ''
            ],
            'enrollment': [
                'Mode Enrollment',
                'Panel desktop',
                'sinkron aktif',
                ''
            ],
            'capture-face': [
                'Capture wajah',
                'Posisikan wajah',
                'di depan kamera',
                ''
            ],
            'training-face': [
                'Training wajah',
                'Proses desktop',
                'kirim embed...',
                ''
            ],
            'waiting-fingerprint': [
                'Siapkan jari',
                'tempel ke sensor',
                '',
                ''
            ],
            'scan-fingerprint': [
                'Scanning...',
                'Sidik jari',
                'sedang dicek',
                ''
            ]
        }

        lines = list(display_map.get(self.device_mode, [
            'Mode perangkat',
            self.device_mode,
            '',
            ''
        ]))

        if detail:
            lines[3] = str(detail)

        try:
            self.serial.send_display([
                self._truncate_display_line(line) for line in lines[:4]
            ])
        except Exception as e:
            self.logger.warning(f"Failed to update LCD for mode '{self.device_mode}': {e}")

    def _get_db_connection(self):
        """Create a SQLite connection safe for the API thread."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _get_user_columns(self, conn):
        """Read the available users table columns for compatibility."""
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(users)")
        return {row[1] for row in cursor.fetchall()}

    def _build_user_select_clause(self, columns):
        """Build a compatible SELECT clause even if some columns are missing."""
        fields = []
        for column_name in ['id', 'name', 'fingerprint_id', 'face_embedding_path', 'registration_date']:
            if column_name in columns:
                fields.append(column_name)
            else:
                fields.append(f"NULL AS {column_name}")
        return ', '.join(fields)

    def _normalize_embedding_entry(self, entry):
        """Convert incoming JSON-friendly embedding data to the runtime format."""
        if entry is None:
            return None
        if isinstance(entry, np.ndarray):
            return entry.astype(np.float32)
        if isinstance(entry, list):
            if not entry:
                return []
            first = entry[0]
            if isinstance(first, (int, float)):
                return np.array(entry, dtype=np.float32)
            return [np.array(item, dtype=np.float32) for item in entry]
        return entry

    def _load_embeddings_map(self):
        """Load the embeddings dictionary from disk."""
        if not os.path.exists(self.embeddings_path):
            return {}

        with open(self.embeddings_path, 'rb') as embeddings_file:
            data = pickle.load(embeddings_file)

        if isinstance(data, dict):
            return data

        raise ValueError('embeddings.pkl must contain a dictionary')

    def _save_embeddings_map(self, embeddings):
        """Persist the embeddings dictionary and refresh the biometric cache."""
        os.makedirs(os.path.dirname(self.embeddings_path), exist_ok=True)
        with open(self.embeddings_path, 'wb') as embeddings_file:
            pickle.dump(embeddings, embeddings_file)

        if self.biometric and hasattr(self.biometric, 'load_embeddings'):
            try:
                self.biometric.face_embeddings = self.biometric.load_embeddings(self.embeddings_path)
            except Exception as e:
                self.logger.warning(f"Failed to refresh in-memory embeddings cache: {e}")

    def _find_embedding_key(self, embeddings, name):
        """Resolve a case-insensitive embedding key."""
        if not name:
            return None
        if name in embeddings:
            return name

        lookup = str(name).strip().lower()
        for existing_key in embeddings.keys():
            if str(existing_key).strip().lower() == lookup:
                return existing_key
        return None

    def _embedding_count(self, embedding_entry):
        """Expose a stable count for desktop monitoring."""
        if embedding_entry is None:
            return 0
        if isinstance(embedding_entry, np.ndarray):
            return 1
        if isinstance(embedding_entry, list):
            if not embedding_entry:
                return 0
            first = embedding_entry[0]
            if isinstance(first, (int, float)):
                return 1
            return len(embedding_entry)
        return 1

    def _serialize_user_row(self, row, embeddings=None, display_no=None):
        """Convert a SQLite row to JSON-safe user data."""
        user_name = row['name'] if 'name' in row.keys() else None
        embedding_entry = None
        if embeddings is not None and user_name:
            embedding_key = self._find_embedding_key(embeddings, user_name)
            if embedding_key is not None:
                embedding_entry = embeddings.get(embedding_key)

        return {
            'id': row['id'],
            'display_no': display_no,
            'name': user_name,
            'full_name': user_name,
            'fingerprint_id': row['fingerprint_id'],
            'face_embedding_path': row['face_embedding_path'],
            'registration_date': row['registration_date'],
            'embedding_count': self._embedding_count(embedding_entry)
        }

    def _fetch_user_row(self, conn, user_id):
        """Fetch a single user row by id."""
        columns = self._get_user_columns(conn)
        select_clause = self._build_user_select_clause(columns)
        cursor = conn.cursor()
        cursor.execute(f"SELECT {select_clause} FROM users WHERE id = ?", (user_id,))
        return cursor.fetchone()

    def _list_users(self):
        """Return all users from the Raspy source-of-truth database."""
        with self.data_lock:
            embeddings = self._load_embeddings_map()
            conn = self._get_db_connection()
            try:
                columns = self._get_user_columns(conn)
                select_clause = self._build_user_select_clause(columns)
                cursor = conn.cursor()
                cursor.execute(f"SELECT {select_clause} FROM users ORDER BY id ASC")
                rows = cursor.fetchall()
                return [
                    self._serialize_user_row(row, embeddings, display_no=index)
                    for index, row in enumerate(rows, start=1)
                ]
            finally:
                conn.close()

    def _create_user(self, payload):
        """Create a user directly in the Raspy database."""
        user_name = str(payload.get('full_name') or payload.get('name') or '').strip()
        if not user_name:
            return False, {'message': 'name is required'}, 400

        with self.data_lock:
            conn = self._get_db_connection()
            try:
                columns = self._get_user_columns(conn)
                insert_columns = ['name']
                insert_values = [user_name]

                if 'face_embedding_path' in columns:
                    insert_columns.append('face_embedding_path')
                    insert_values.append(None)
                if 'registration_date' in columns:
                    insert_columns.append('registration_date')
                    insert_values.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

                placeholders = ', '.join(['?'] * len(insert_columns))
                cursor = conn.cursor()
                cursor.execute(
                    f"INSERT INTO users ({', '.join(insert_columns)}) VALUES ({placeholders})",
                    insert_values
                )
                conn.commit()

                row = self._fetch_user_row(conn, cursor.lastrowid)
                return True, {
                    'status': 'ok',
                    'message': 'user created',
                    'user': self._serialize_user_row(row, self._load_embeddings_map())
                }, 201
            except sqlite3.IntegrityError as e:
                return False, {'message': f'failed to create user: {e}'}, 409
            finally:
                conn.close()

    def _update_user(self, user_id, payload):
        """Update a user and keep embeddings keyed by the current full name."""
        ignored_fields = [
            key for key in ['role', 'username', 'password', 'password_hash']
            if key in payload
        ]

        with self.data_lock:
            conn = self._get_db_connection()
            try:
                row = self._fetch_user_row(conn, user_id)
                if row is None:
                    return False, {'message': 'user not found'}, 404

                columns = self._get_user_columns(conn)
                updates = []
                values = []

                new_name = payload.get('full_name') or payload.get('name')
                if new_name is not None and 'name' in columns:
                    new_name = str(new_name).strip()
                    if not new_name:
                        return False, {'message': 'name cannot be empty'}, 400
                    if new_name != row['name']:
                        updates.append('name = ?')
                        values.append(new_name)
                else:
                    new_name = row['name']

                if 'fingerprint_id' in payload and 'fingerprint_id' in columns:
                    updates.append('fingerprint_id = ?')
                    values.append(payload.get('fingerprint_id'))

                if 'face_embedding_path' in payload and 'face_embedding_path' in columns:
                    updates.append('face_embedding_path = ?')
                    values.append(payload.get('face_embedding_path'))

                if updates:
                    values.append(user_id)
                    conn.cursor().execute(
                        f"UPDATE users SET {', '.join(updates)} WHERE id = ?",
                        values
                    )
                    conn.commit()

                if new_name != row['name']:
                    embeddings = self._load_embeddings_map()
                    old_key = self._find_embedding_key(embeddings, row['name'])
                    if old_key is not None:
                        embeddings[new_name] = embeddings.pop(old_key)
                        self._save_embeddings_map(embeddings)
                    if str(self.current_user_id) == str(user_id):
                        self.current_user_name = new_name

                updated_row = self._fetch_user_row(conn, user_id)
                response = {
                    'status': 'ok',
                    'message': 'user updated',
                    'user': self._serialize_user_row(updated_row, self._load_embeddings_map())
                }
                if ignored_fields:
                    response['note'] = (
                        'desktop auth fields remain local and were ignored: ' +
                        ', '.join(ignored_fields)
                    )
                return True, response, 200
            except sqlite3.IntegrityError as e:
                return False, {'message': f'failed to update user: {e}'}, 409
            finally:
                conn.close()

    def _delete_fingerprint_template(self, fingerprint_id):
        """Delete a fingerprint template from the sensor when possible."""
        if fingerprint_id is None:
            return False, 'no fingerprint template assigned'
        if not self.biometric:
            return False, 'biometric subsystem not initialized'

        try:
            if not self.biometric.fingerprint_sensor:
                initialized = self.biometric.initialize_fingerprint_sensor()
                if not initialized:
                    return False, 'fingerprint sensor unavailable'

            sensor = self.biometric.fingerprint_sensor
            deleted = sensor.deleteTemplate(int(fingerprint_id))
            if deleted:
                return True, 'template deleted from sensor'
            return False, 'sensor refused to delete template'
        except Exception as e:
            return False, str(e)

    def _get_next_available_fingerprint_id(self, conn):
        """Return the next positive fingerprint slot not used in the database."""
        cursor = conn.cursor()
        cursor.execute('SELECT fingerprint_id FROM users WHERE fingerprint_id IS NOT NULL')
        used_ids = set()
        for row in cursor.fetchall():
            try:
                fingerprint_id = int(row['fingerprint_id'])
            except (TypeError, ValueError, KeyError):
                continue
            if fingerprint_id > 0:
                used_ids.add(fingerprint_id)

        candidate = 1
        while candidate in used_ids:
            candidate += 1
        return candidate

    def _run_fingerprint_enrollment_on_sensor(self, timeout_seconds=10):
        """Try to enroll a fingerprint on the physical sensor."""
        if not self.biometric:
            return False, None, 'biometric subsystem not initialized', 'fallback'

        try:
            if not self.biometric.fingerprint_sensor:
                initialized = self.biometric.initialize_fingerprint_sensor()
                if not initialized:
                    return False, None, 'fingerprint sensor unavailable', 'fallback'

            sensor = self.biometric.fingerprint_sensor
            
            # HARD RESET: Reinitialize sensor to clear any state from verification
            try:
                # Force sensor re-initialization
                self.biometric.fingerprint_sensor = None
                time.sleep(0.5)
                if not self.biometric.initialize_fingerprint_sensor():
                    return False, None, 'fingerprint sensor reinit failed', 'fallback'
                sensor = self.biometric.fingerprint_sensor
                time.sleep(0.5)
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Sensor reinit error: {e}")
                # Continue anyway
                pass
            
            # Clear any remaining buffer data
            try:
                for _ in range(10):  # More aggressive buffer clear
                    if sensor.readImage():
                        time.sleep(0.05)
                    else:
                        break
                time.sleep(0.3)
            except Exception:
                pass  # Ignore errors during buffer clear
            
            self._set_device_mode('waiting-fingerprint', detail='tempel jari', push_to_display=True)

            started_at = time.time()
            while time.time() - started_at < timeout_seconds:
                if sensor.readImage():
                    break
                time.sleep(0.1)
            else:
                return False, None, 'Fingerprint scan dibatalkan', 'scan'

            sensor.convertImage(0x01)
            self._set_device_mode('waiting-fingerprint', detail='angkat-tempel ulang', push_to_display=True)

            lifted_at = time.time()
            while time.time() - lifted_at < timeout_seconds:
                if not sensor.readImage():
                    break
                time.sleep(0.1)
            else:
                return False, None, 'Fingerprint scan dibatalkan', 'scan'

            second_scan_at = time.time()
            while time.time() - second_scan_at < timeout_seconds:
                if sensor.readImage():
                    break
                time.sleep(0.1)
            else:
                return False, None, 'Fingerprint scan dibatalkan', 'scan'

            sensor.convertImage(0x02)
            if sensor.compareCharacteristics() == 0:
                return False, None, 'Fingerprint scan dibatalkan', 'scan'

            sensor.createTemplate()
            fingerprint_id = int(sensor.storeTemplate())
            return True, fingerprint_id, 'Fingerprint berhasil diregistrasi', 'sensor'
        except Exception as e:
            return False, None, str(e), 'fallback'
        finally:
            self._set_device_mode('idle', push_to_display=False)

    def _enroll_fingerprint(self, payload):
        """Enroll a fingerprint for an existing user from the desktop integration."""
        user_id = payload.get('user_id', payload.get('id'))
        if user_id is None:
            return False, {'success': False, 'message': 'user_id is required'}, 400

        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            return False, {'success': False, 'message': 'user_id must be an integer'}, 400

        allow_fallback = bool(payload.get('allow_fallback', True))

        with self.action_lock:
            with self.data_lock:
                conn = self._get_db_connection()
                try:
                    row = self._fetch_user_row(conn, user_id)
                    if row is None:
                        return False, {'success': False, 'message': 'User tidak ditemukan'}, 200

                    if row['fingerprint_id'] is not None:
                        return True, {
                            'success': True,
                            'message': 'Fingerprint sudah terdaftar',
                            'fingerprint_id': row['fingerprint_id'],
                            'user_id': user_id,
                            'user': self._serialize_user_row(row, self._load_embeddings_map())
                        }, 200
                finally:
                    conn.close()

            success, fingerprint_id, message, source = self._run_fingerprint_enrollment_on_sensor()
            fallback_used = False

            if not success:
                if source == 'scan' or not allow_fallback:
                    return False, {'success': False, 'message': message}, 200
                fallback_used = True

            with self.data_lock:
                conn = self._get_db_connection()
                try:
                    row = self._fetch_user_row(conn, user_id)
                    if row is None:
                        return False, {'success': False, 'message': 'User tidak ditemukan'}, 200

                    assigned_fingerprint_id = fingerprint_id
                    if fallback_used:
                        assigned_fingerprint_id = self._get_next_available_fingerprint_id(conn)

                    columns = self._get_user_columns(conn)
                    if 'fingerprint_id' not in columns:
                        return False, {'success': False, 'message': 'users.fingerprint_id column not found'}, 500

                    conn.cursor().execute(
                        'UPDATE users SET fingerprint_id = ? WHERE id = ?',
                        (assigned_fingerprint_id, user_id)
                    )
                    conn.commit()

                    updated_row = self._fetch_user_row(conn, user_id)
                    response = {
                        'success': True,
                        'message': 'Fingerprint berhasil diregistrasi',
                        'fingerprint_id': assigned_fingerprint_id,
                        'user_id': user_id,
                        'user': self._serialize_user_row(updated_row, self._load_embeddings_map())
                    }
                    if fallback_used:
                        response['fallback_used'] = True
                        response['message_detail'] = message
                    return True, response, 200
                finally:
                    conn.close()

    def _clear_face_data(self, user_id):
        """Remove face embeddings for a user while preserving the user record."""
        with self.data_lock:
            conn = self._get_db_connection()
            try:
                row = self._fetch_user_row(conn, user_id)
                if row is None:
                    return False, {'message': 'user not found'}, 404

                embeddings = self._load_embeddings_map()
                embedding_key = self._find_embedding_key(embeddings, row['name'])
                removed_embedding = False
                if embedding_key is not None:
                    embeddings.pop(embedding_key, None)
                    self._save_embeddings_map(embeddings)
                    removed_embedding = True

                columns = self._get_user_columns(conn)
                if 'face_embedding_path' in columns:
                    conn.cursor().execute(
                        'UPDATE users SET face_embedding_path = NULL WHERE id = ?',
                        (user_id,)
                    )
                    conn.commit()

                updated_row = self._fetch_user_row(conn, user_id)
                return True, {
                    'status': 'ok',
                    'message': 'face data cleared',
                    'removed_embedding': removed_embedding,
                    'user': self._serialize_user_row(updated_row, self._load_embeddings_map())
                }, 200
            finally:
                conn.close()

    def _clear_fingerprint_data(self, user_id):
        """Remove fingerprint data for a user while preserving the user record."""
        with self.data_lock:
            conn = self._get_db_connection()
            try:
                row = self._fetch_user_row(conn, user_id)
                if row is None:
                    return False, {'message': 'user not found'}, 404

                sensor_deleted, sensor_message = self._delete_fingerprint_template(row['fingerprint_id'])

                columns = self._get_user_columns(conn)
                if 'fingerprint_id' in columns:
                    conn.cursor().execute(
                        'UPDATE users SET fingerprint_id = NULL WHERE id = ?',
                        (user_id,)
                    )
                    conn.commit()

                updated_row = self._fetch_user_row(conn, user_id)
                return True, {
                    'status': 'ok',
                    'message': 'fingerprint cleared',
                    'sensor_deleted': sensor_deleted,
                    'sensor_message': sensor_message,
                    'user': self._serialize_user_row(updated_row, self._load_embeddings_map())
                }, 200
            finally:
                conn.close()

    def _delete_user(self, user_id):
        """Delete a user and remove linked biometric artifacts when possible."""
        with self.data_lock:
            conn = self._get_db_connection()
            try:
                row = self._fetch_user_row(conn, user_id)
                if row is None:
                    return False, {'message': 'user not found'}, 404

                embeddings = self._load_embeddings_map()
                embedding_key = self._find_embedding_key(embeddings, row['name'])
                if embedding_key is not None:
                    embeddings.pop(embedding_key, None)
                    self._save_embeddings_map(embeddings)

                sensor_deleted, sensor_message = self._delete_fingerprint_template(row['fingerprint_id'])

                conn.cursor().execute('DELETE FROM users WHERE id = ?', (user_id,))
                conn.commit()

                return True, {
                    'status': 'ok',
                    'message': 'user deleted',
                    'sensor_deleted': sensor_deleted,
                    'sensor_message': sensor_message
                }, 200
            finally:
                conn.close()

    def _decode_embeddings_file_payload(self, encoded_payload):
        """Decode a base64 payload containing embeddings data."""
        raw_bytes = base64.b64decode(encoded_payload)

        try:
            decoded = pickle.loads(raw_bytes)
        except Exception:
            decoded = json.loads(raw_bytes.decode('utf-8'))

        if not isinstance(decoded, dict):
            raise ValueError('decoded embeddings payload must be a dictionary')

        normalized = {}
        for key, value in decoded.items():
            normalized[str(key)] = self._normalize_embedding_entry(value)
        return normalized

    def _upsert_face_embedding(self, payload):
        """Store face embeddings sent by the desktop and bind them to a user."""
        user_id = payload.get('user_id', payload.get('id'))
        if user_id is None:
            return False, {'message': 'user_id is required'}, 400

        desktop_name = payload.get('full_name') or payload.get('name')
        photo_paths = payload.get('photo_paths') or []
        photos_base64 = payload.get('photos_base64') or []
        merge_file = bool(payload.get('merge_file'))

        embedding_payload = None
        embeddings_from_file = None

        if 'embedding' in payload:
            embedding_payload = self._normalize_embedding_entry(payload.get('embedding'))
        elif 'embeddings' in payload:
            embedding_payload = self._normalize_embedding_entry(payload.get('embeddings'))
        elif 'embeddings_file_base64' in payload:
            try:
                embeddings_from_file = self._decode_embeddings_file_payload(payload.get('embeddings_file_base64'))
            except Exception as e:
                return False, {'message': f'failed to decode embeddings file: {e}'}, 400

        with self.data_lock:
            conn = self._get_db_connection()
            try:
                row = self._fetch_user_row(conn, user_id)
                if row is None:
                    return False, {'message': 'user not found'}, 404

                full_name = str(desktop_name or row['name'] or '').strip()
                if not full_name:
                    return False, {'message': 'full_name is required'}, 400

                embeddings = self._load_embeddings_map()

                if embeddings_from_file is not None:
                    if merge_file:
                        embeddings.update(embeddings_from_file)
                    else:
                        selected_key = self._find_embedding_key(embeddings_from_file, full_name)
                        if selected_key is None and len(embeddings_from_file) == 1:
                            selected_key = next(iter(embeddings_from_file.keys()))
                        if selected_key is None:
                            return False, {
                                'message': 'full_name not found inside uploaded embeddings file'
                            }, 400
                        embedding_payload = embeddings_from_file[selected_key]

                if embedding_payload is None:
                    return False, {
                        'message': (
                            'desktop training must send embedding, embeddings, or '
                            'embeddings_file_base64; raw photos alone are not enough'
                        ),
                        'received_photo_paths': len(photo_paths),
                        'received_photos_base64': len(photos_base64)
                    }, 400

                if merge_file and embeddings_from_file is not None:
                    final_key = self._find_embedding_key(embeddings, full_name)
                    if final_key is None and len(embeddings_from_file) == 1:
                        uploaded_key = next(iter(embeddings_from_file.keys()))
                        embeddings[full_name] = embeddings.pop(uploaded_key)
                        final_key = full_name
                    elif final_key is not None and final_key != full_name:
                        embeddings[full_name] = embeddings.pop(final_key)
                        final_key = full_name
                    elif final_key is None:
                        return False, {
                            'message': 'uploaded embeddings file does not contain an entry for full_name'
                        }, 400
                else:
                    final_key = full_name
                    embeddings[final_key] = embedding_payload

                if merge_file and embeddings_from_file is not None:
                    self._save_embeddings_map(embeddings)
                else:
                    self._save_embeddings_map(embeddings)

                columns = self._get_user_columns(conn)
                updates = []
                values = []

                if 'name' in columns and row['name'] != full_name:
                    updates.append('name = ?')
                    values.append(full_name)

                if 'face_embedding_path' in columns:
                    updates.append('face_embedding_path = ?')
                    values.append(self.embeddings_path)

                if updates:
                    values.append(user_id)
                    conn.cursor().execute(
                        f"UPDATE users SET {', '.join(updates)} WHERE id = ?",
                        values
                    )
                    conn.commit()

                updated_row = self._fetch_user_row(conn, user_id)
                return True, {
                    'status': 'face_enrolled',
                    'user_id': user_id,
                    'full_name': final_key,
                    'face_embedding_path': self.embeddings_path,
                    'received_photo_paths': len(photo_paths),
                    'received_photos_base64': len(photos_base64),
                    'user': self._serialize_user_row(updated_row, self._load_embeddings_map())
                }, 200
            finally:
                conn.close()

    def _set_external_device_mode(self, payload):
        """Apply a device mode requested by the desktop."""
        mode = payload.get('mode')
        if not mode:
            return False, {'message': 'mode is required'}, 400

        detail = payload.get('message') or payload.get('detail')
        self._set_device_mode(mode, detail=detail, push_to_display=True)
        return True, {
            'status': 'ok',
            'mode': self.device_mode,
            'message': 'device mode updated',
            'updated_at': self.device_mode_updated_at.isoformat()
        }, 200

    def _list_logs(self, limit=100):
        """Return recent access logs if the optional access_log DB exists."""
        access_log_db = os.path.abspath(os.path.join(self.base_dir, '..', 'database', 'access_log.db'))
        if not os.path.exists(access_log_db):
            return []

        conn = sqlite3.connect(access_log_db, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT timestamp, name, similarity, image_path FROM access_log ORDER BY timestamp DESC LIMIT ?',
                (limit,)
            )
            rows = cursor.fetchall()
            return [
                {
                    'timestamp': row['timestamp'],
                    'name': row['name'],
                    'method': 'face',
                    'status': 'logged',
                    'similarity': row['similarity'],
                    'image_path': row['image_path']
                }
                for row in rows
            ]
        finally:
            conn.close()

    def start_api_server(self):
        """Start the embedded HTTP API used by the desktop app."""
        if self.api_thread and self.api_thread.is_alive():
            return True

        try:
            handler = make_api_handler(self)
            self.api_server = ThreadingHTTPServer((self.api_host, self.api_port), handler)
            self.api_thread = threading.Thread(
                target=self.api_server.serve_forever,
                name='embedded-api-server',
                daemon=True
            )
            self.api_thread.start()
            self.logger.info(f'Embedded API server listening on {self.api_host}:{self.api_port}')
            return True
        except Exception as e:
            self.logger.error(f'Failed to start embedded API server: {e}')
            self.api_server = None
            self.api_thread = None
            return False

    def stop_api_server(self):
        """Stop the embedded API server."""
        if self.api_server:
            try:
                self.api_server.shutdown()
                self.api_server.server_close()
            except Exception as e:
                self.logger.warning(f'Failed to stop embedded API server cleanly: {e}')
            finally:
                self.api_server = None
                self.api_thread = None
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info("Shutdown signal received")
        self.running = False
    
    def initialize_components(self):
        """Initialize all hardware components"""
        self.logger.info("Initializing components...")
        
        # Initialize Arduino serial connection
        arduino_port = self.config.get('serial', {}).get('arduino_port')
        
        if not arduino_port:
            arduino_port = find_arduino_port(self.logger)
        
        if not arduino_port:
            self.logger.error("Cannot find Arduino Nano")
            return False
        
        arduino_baud = self.config.get('serial', {}).get('arduino_baudrate', 115200)
        self.serial = NanoSerial(arduino_port, arduino_baud, self.logger)
        
        if not self.serial.connect():
            self.logger.error("Failed to connect to Arduino")
            return False
        
        # Start serial read loop with message callback
        self.serial.start_read_loop(callback=self._handle_arduino_message)
        
        # Initialize biometric system
        self.biometric = BiometricAuth(self.config, self.logger)
        
        # Initialize attendance manager
        self.absensi = AbsensiManager(self.config, self.logger)

        # Device is now ready to be observed by the desktop panel
        self._set_device_mode('idle', push_to_display=False)
        
        self.logger.info("All components initialized")
        return True
    
    def _handle_arduino_message(self, message):
        """
        Callback for messages from Arduino
        
        Expected message format (JSON):
        - {"type": "system", "event": "boot"}
        - {"type": "input", "source": "touch", "state": "on"}
        - {"type": "input", "source": "keypad", "key": "A"}
        - {"type": "event", "name": "emergency", "state": "pressed"}
        """
        msg_type = message.get('type')
        
        if msg_type == 'system':
            event = message.get('event')
            if event == 'boot':
                self.logger.info("Arduino boot signal received")
            else:
                self.logger.debug(f"Arduino system event: {event}")
        
        elif msg_type == 'input':
            source = message.get('source')
            
            if source == 'touch':
                state = message.get('state')
                if state == 'on' and not self.system_active:
                    self.logger.info("Touch sensor activated")
                    self.system_active = True
                    self.state = SystemState.TOUCH_ACTIVATED
            
            elif source == 'keypad':
                key = message.get('key')
                self._handle_keypad_input(key)
        
        elif msg_type == 'event':
            name = message.get('name')
            if name == 'emergency':
                self.logger.warning("EMERGENCY BUTTON PRESSED")
                self._handle_emergency()

    def _start_background_action(self, target, action_name):
        """Run slow keypad actions without blocking the serial read loop."""
        with self.action_lock:
            if self.action_thread and self.action_thread.is_alive():
                self.logger.warning(f"Action still running, ignoring {action_name}")
                return False

            def runner():
                try:
                    target()
                except Exception as e:
                    self.logger.error(f"Background action '{action_name}' failed: {e}")
                    self.state = SystemState.ERROR
                finally:
                    with self.action_lock:
                        self.action_thread = None

            self.action_thread = threading.Thread(
                target=runner,
                name=f'action-{action_name}',
                daemon=True
            )
            self.action_thread.start()
            return True
    
    def _handle_keypad_input(self, key):
        """Handle keypad input based on current state"""
        self.logger.debug(f"Keypad: {key} (State: {self.state.name})")
        
        # Global: if we're in idle and admin starts with '#', go to admin pin entry
        if self.state == SystemState.IDLE and key == '#':
            # Enter admin PIN entry state
            self.input_buffer = ""
            self.state = SystemState.ADMIN_PIN
            self.serial.send_display([
                "Admin PIN:",
                "_ _ _ _",
                "#=OK * =CLR",
                ""
            ])
            return

        if self.state == SystemState.MENU:
            if key == 'A':
                # Attendance mode
                self.state = SystemState.ATTENDANCE_JOB
                self._show_job_selection()
            
            elif key == 'B':
                # Door access mode
                self._start_background_action(self._handle_door_access, 'door-access')
            
            elif key == 'C':
                # Return to idle
                self._reset_session()
        
        elif self.state == SystemState.ATTENDANCE_JOB:
            if key in ['1', '2', '3']:
                self.job_selection = key
                self.logger.info(f"Job selected: {self.job_codes.get(key)}")
                self.state = SystemState.ATTENDANCE_DOMAIN
                self._show_domain_selection()
            
            elif key == '*':
                # Reset
                self.job_selection = None
                self._show_job_selection()
        
        elif self.state == SystemState.ATTENDANCE_DOMAIN:
            if key in ['A', 'B', 'C']:
                self.domain_selection = key
                self.logger.info(f"Domain selected: {self.domain_codes.get(key)}")
                self.shift_input_buffer = ""
                self.state = SystemState.ATTENDANCE_SHIFT_INPUT
                self._show_shift_input_prompt()
            
            elif key == '*':
                # Reset to job selection
                self.domain_selection = None
                self.state = SystemState.ATTENDANCE_JOB
                self._show_job_selection()
        
        elif self.state == SystemState.ATTENDANCE_SHIFT_INPUT:
            # Valid characters for shift input: 0-9, A, B, C
            if key in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C']:
                if len(self.shift_input_buffer) < 5:
                    self.shift_input_buffer += key
                    self.logger.debug(f"Shift input: {self.shift_input_buffer}")
                    
                    # Show current input on display
                    disp_input = self.shift_input_buffer + ('_' * (5 - len(self.shift_input_buffer)))
                    self.serial.send_display([
                        "Isi Shift",
                        f"[{disp_input}]",
                        "0-9 A B C",
                        "# OK, * Reset"
                    ])
                    
                    # If buffer reaches 5, auto-proceed to confirm
                    if len(self.shift_input_buffer) == 5:
                        self._parse_shift_input()
                        self.state = SystemState.ATTENDANCE_CONFIRM
                        self._show_attendance_confirm()
            
            elif key == '*':
                # Reset to domain selection
                self._reset_shifts()
                self.state = SystemState.ATTENDANCE_DOMAIN
                self._show_domain_selection()
        
        elif self.state == SystemState.ATTENDANCE_CONFIRM:
            if key == '#':
                # Send attendance
                self._start_background_action(self._submit_attendance, 'submit-attendance')
            
            elif key == '*':
                # Reset to domain selection
                self.domain_selection = None
                self._reset_shifts()
                self.state = SystemState.ATTENDANCE_DOMAIN
                self._show_domain_selection()
        
        # Admin PIN entry
        elif self.state == SystemState.ADMIN_PIN:
            if key.isdigit():
                # append digit (max 8 for safety)
                if len(self.input_buffer) < 8:
                    self.input_buffer += key
                # show masked
                disp = '*' * len(self.input_buffer)
                self.serial.send_display(["Admin PIN:", disp, "#=OK * =CLR", ""])

            elif key == '*':
                # clear/reset
                self.input_buffer = self.input_buffer[:-1]
                disp = '*' * len(self.input_buffer)
                self.serial.send_display(["Admin PIN:", disp, "#=OK * =CLR", ""])

            elif key == '#':
                # submit
                if self.input_buffer == self.admin_pin:
                    self.logger.info("Admin PIN accepted")
                    self.input_buffer = ""
                    self.state = SystemState.ENROLL_MENU
                    self._state_enroll_menu()
                else:
                    self.logger.warning("Admin PIN rejected")
                    self.serial.send_display(["PIN salah", "Coba lagi", "#=Retry", "*"])
                    self.input_buffer = ""

        # Enrollment/menu handling
        elif self.state == SystemState.ENROLL_MENU:
            # Enrollment via CLI tools only - just allow exit
            if key == '*':
                # cancel and return to idle
                self._reset_session()

        elif self.state == SystemState.ENROLL_INPUT_ID:
            # Enrollment via CLI tools only - no input handling needed
            pass

        elif self.state == SystemState.ENROLL_FINGERPRINT:
            # Enrollment via CLI tools only - allow return to menu
            if key == '#':
                self.state = SystemState.ENROLL_MENU
                self.previous_state = None

        elif self.state == SystemState.ENROLL_FACE:
            # Enrollment via CLI tools only - allow return to menu
            if key == '#':
                self.state = SystemState.ENROLL_MENU
                self.previous_state = None
    
    def _handle_emergency(self):
        """Handle emergency unlock"""
        now = time.time()
        if self.emergency_active or now < self.emergency_ignore_until:
            return

        self.logger.warning("Emergency unlock activated")
        self.emergency_active = True
        self.emergency_release_at = now + 5
        self.emergency_ignore_until = now + 6
        self.state_before_emergency = self.state
        self.state = SystemState.EMERGENCY
        self.previous_state = None
        self.system_active = False

        if self.serial:
            self.serial.send_display([
                "EMERGENCY UNLOCK",
                "Pintu terbuka",
                "Darurat aktif",
                ""
            ])
            relay_sent = self.serial.send_relay('open', duration=5)
            self.logger.info(f"Emergency relay OPEN command sent: {relay_sent}")

        if self.emergency_timer:
            self.emergency_timer.cancel()

        self.emergency_timer = threading.Timer(5, self._release_emergency)
        self.emergency_timer.daemon = True
        self.emergency_timer.start()

        self.logger.log_event('emergency', {'timestamp': datetime.now()})

    def _release_emergency(self):
        """Release emergency mode even if the main loop is blocked."""
        if not self.emergency_active:
            return

        if self.serial:
            relay_sent = self.serial.send_relay('close')
            self.logger.info(f"Emergency relay CLOSE command sent: {relay_sent}")

        self.logger.info("Emergency relay CLOSE sent")
        self.emergency_active = False
        self.emergency_release_at = None
        self.state_before_emergency = None
        self.emergency_timer = None
        self._reset_session()

    def _state_emergency(self):
        """Emergency state"""
        if self.previous_state != SystemState.EMERGENCY:
            self.logger.info("State: EMERGENCY")
            self.serial.send_display([
                "EMERGENCY UNLOCK",
                "Pintu terbuka",
                "Darurat aktif",
                ""
            ])
            self.previous_state = SystemState.EMERGENCY

        if self.emergency_release_at and time.time() >= self.emergency_release_at:
            self._release_emergency()
            return

        time.sleep(0.5)
    
    def run(self):
        """Main state machine loop"""
        api_started = self.start_api_server()
        if not api_started:
            self.logger.warning('Desktop API is unavailable because the embedded server failed to start')

        if not self.initialize_components():
            self.logger.error("Initialization failed; keeping API alive for desktop monitoring")
            while self.running:
                time.sleep(1)
            self.cleanup()
            return
        
        # State machine
        while self.running:
            try:
                if self.state == SystemState.BOOT:
                    self._state_boot()
                
                elif self.state == SystemState.SPLASH:
                    self._state_splash()
                
                elif self.state == SystemState.IDLE:
                    self._state_idle()
                
                elif self.state == SystemState.TOUCH_ACTIVATED:
                    self._state_touch_activated()
                
                elif self.state == SystemState.FINGERPRINT:
                    self._state_fingerprint()
                
                elif self.state == SystemState.FACE:
                    self._state_face()

                elif self.state == SystemState.ADMIN_PIN:
                    self._state_enroll_admin_pin()

                elif self.state == SystemState.ENROLL_MENU:
                    self._state_enroll_menu()
                
                elif self.state == SystemState.MENU:
                    self._state_menu()
                
                elif self.state == SystemState.ATTENDANCE_SHIFT_INPUT:
                    self._state_attendance_shift_input()
                
                elif self.state == SystemState.ACCESS:
                    pass

                elif self.state == SystemState.EMERGENCY:
                    self._state_emergency()
                
                elif self.state == SystemState.ERROR:
                    self._state_error()
                
                time.sleep(0.1)  # Small delay to prevent CPU hogging
                
            except Exception as e:
                self.logger.error(f"State machine error: {e}")
                self.state = SystemState.ERROR
        
        # Cleanup
        self.cleanup()
    
    def _state_boot(self):
        """Boot state"""
        self.logger.info("State: BOOT")
        
        # Send boot acknowledgment to Arduino
        time.sleep(1)
        
        self.state = SystemState.SPLASH
    
    def _state_splash(self):
        """Splash screen state"""
        self.logger.info("State: SPLASH")
        
        # Display splash screen on LCD
        self.serial.send_display([
            "Selamat Datang",
            "Di",
            "Lab Robotika",
            "2026"
        ])
        
        # Wait for splash duration
        splash_duration = self.config.get('timeouts', {}).get('splash_duration', 5)
        time.sleep(splash_duration)
        
        self.state = SystemState.IDLE
    
    def _state_idle(self):
        """Idle/standby state"""
        if self.previous_state != SystemState.IDLE:
            self.logger.info("State: IDLE")
            self._set_device_mode('idle', push_to_display=False)
            
            # Display standby message
            self.serial.send_display([
                "Touch sensor",
                "untuk mulai",
                "",
                ""
            ])
            
            self.previous_state = SystemState.IDLE
            self.system_active = False
        
        # Wait for touch activation (handled by Arduino message callback)
        time.sleep(0.5)
    
    def _state_touch_activated(self):
        """Touch activated state"""
        self.logger.info("State: TOUCH_ACTIVATED")
        self._set_device_mode('waiting-fingerprint', push_to_display=False)
        
        # Display fingerprint prompt
        self.serial.send_display([
            "Silakan tempelkan",
            "sidik jari",
            "",
            ""
        ])
        
        time.sleep(1)
        
        self.state = SystemState.FINGERPRINT
    
    def _state_fingerprint(self):
        """Fingerprint verification state"""
        self.logger.info("State: FINGERPRINT")
        self._set_device_mode('scan-fingerprint', push_to_display=False)
        
        self.serial.send_display([
            "Scanning...",
            "Sidik jari",
            "",
            ""
        ])
        
        # Scan fingerprint
        success, user_id, user_name = self.biometric.scan_fingerprint()

        if self.emergency_active:
            return
        
        if success and user_id and user_name:
            self.logger.info(f"Fingerprint matched: {user_name}")
            
            self.current_user_id = user_id
            self.current_user_name = user_name
            
            self.serial.send_display([
                "Sidik jari cocok",
                user_name,
                "",
                ""
            ])
            
            time.sleep(1)
            
            self.state = SystemState.FACE
        
        else:
            self.logger.warning("Fingerprint verification failed")
            
            # Capture image
            img_path = ''
            frame = self.biometric.capture_frame()
            if frame is not None:
                img_path = self.logger.save_image(frame, "failed_fingerprint")
                self.logger.log_failed_biometric(None, False, False, img_path)

            self._submit_monitoring_record('fingerprint', img_path)
            
            self.serial.send_display([
                "Sidik jari",
                "tidak cocok",
                "",
                ""
            ])
            
            time.sleep(2)
            
            self._reset_session()
    
    def _state_face(self):
        """Face verification state"""
        self.logger.info("State: FACE")
        self._set_device_mode('capture-face', detail=self.current_user_name, push_to_display=False)
        
        self.serial.send_display([
            f"Verify wajah:",
            self.current_user_name,
            "Verifikasi...",
            ""
        ])
        
        # Verify face
        # Use canonical user id for verification (do not use name)
        success = self.biometric.verify_face(self.current_user_name)

        if self.emergency_active:
            return
        
        if success:
            self.logger.info(f"Face verified: {self.current_user_name}")
            
            self.serial.send_display([
                f"Verify wajah:",
                self.current_user_name,
                "Verifikasi OK",
                ""
            ])
            
            # Capture verified image
            frame = self.biometric.capture_frame()
            if frame is not None:
                self.logger.save_image(frame, f"verified_{self.current_user_name}")
            
            time.sleep(1)
            
            self.state = SystemState.MENU
        
        else:
            self.logger.warning(f"Face verification failed for {self.current_user_name}")
            
            # If camera is unavailable (error message indicates), skip face and go to menu
            # This allows fingerprint-only attendance to work even if camera fails
            # Decide based on biometric.last_face_error
            last_err = getattr(self.biometric, 'last_face_error', None)

            if last_err == 'camera_unavailable':
                # Camera missing - allow fingerprint-only flow to proceed
                self.logger.info(f"Face verification skipped for {self.current_user_name} - camera unavailable. Proceeding to menu.")
                self.serial.send_display([
                    "Face verif skip",
                    "Proses lanjut...",
                    "",
                    ""
                ])
                time.sleep(1)
                self.state = SystemState.MENU
            else:
                # Capture failed image
                img_path = ''
                frame = self.biometric.capture_frame()
                if frame is not None:
                    img_path = self.logger.save_image(frame, f"failed_face_{self.current_user_name}")
                    # Log details: user id known, face failed
                    self.logger.log_failed_biometric(self.current_user_name, True, False, img_path)

                self._submit_monitoring_record('face', img_path)

                self.serial.send_display([
                    "Wajah tidak cocok",
                    "Verifikasi gagal",
                    "",
                    ""
                ])

                time.sleep(2)

                self._reset_session()
    
    def _state_menu(self):
        """Menu selection state"""
        if self.previous_state != SystemState.MENU:
            self.logger.info("State: MENU")
            
            # Display menu
            self.serial.send_display([
                "Menu",
                "A. Absensi",
                "B. Akses Pintu",
                "C. Kembali"
            ])
            
            self.previous_state = SystemState.MENU
        
        # Wait for keypad input (handled by callback)
        time.sleep(0.5)
    
    def _show_job_selection(self):
        """Show job selection screen"""
        self.serial.send_display([
            "JOB :",
            "1:PS Muro 2:DM",
            "3:Lanjut",
            "# Kirim, * Reset"
        ])
    
    def _show_domain_selection(self):
        """Show domain selection screen"""
        self.serial.send_display([
            "DOMAIN :",
            "A:Depok B:Kmal",
            "C:Karawaci",
            "# Kirim, * Reset"
        ])
    
    def _show_shift_input_prompt(self):
        """Show shift input prompt screen"""
        self.serial.send_display([
            "Isi Shift",
            "A B C D E",
            "0-9 A B C",
            "# OK, * Reset"
        ])
    
    def _parse_shift_input(self):
        """Parse 5-character shift input into individual shift values"""
        if len(self.shift_input_buffer) == 5:
            self.shift_A, self.shift_B, self.shift_C, self.shift_D, self.shift_E = self.shift_input_buffer
            self.logger.info(f"Shift input parsed: A={self.shift_A}, B={self.shift_B}, C={self.shift_C}, D={self.shift_D}, E={self.shift_E}")
    
    def _state_attendance_shift_input(self):
        """Attendance shift input state - wait for keypad input"""
        if self.previous_state != SystemState.ATTENDANCE_SHIFT_INPUT:
            self.logger.info("State: ATTENDANCE_SHIFT_INPUT")
            self._show_shift_input_prompt()
            self.previous_state = SystemState.ATTENDANCE_SHIFT_INPUT
        
        # Keypad input handled by callback
        time.sleep(0.5)
    
    def _show_attendance_confirm(self):
        """Show attendance confirmation with shift details"""
        job_name = self.job_codes.get(self.job_selection, '?')
        domain_name = self.domain_codes.get(self.domain_selection, '?')
        shift_display = f"[{self.shift_input_buffer}]" if self.shift_input_buffer else "?"
        
        self.serial.send_display([
            f"Job: {job_name[:15]}",
            f"Dom: {domain_name[:15]}",
            f"Shift: {shift_display}",
            "# Kirim, * Reset"
        ])

    # -------------------- Enrollment / Admin states --------------------
    def _state_enroll_admin_pin(self):
        """Admin PIN state - keypad handles input; keep display alive"""
        if self.previous_state != SystemState.ADMIN_PIN:
            self.logger.info("State: ADMIN_PIN")
            # initial prompt already sent by keypad handler, but ensure display
            self.serial.send_display([
                "Admin PIN:",
                "_ _ _ _",
                "#=OK * =CLR",
                ""
            ])
            self.previous_state = SystemState.ADMIN_PIN
        time.sleep(0.2)

    def _state_enroll_menu(self):
        """Show admin menu - enrollment via CLI tools"""
        if self.previous_state != SystemState.ENROLL_MENU:
            self.logger.info("State: ENROLL_MENU")
            self._set_device_mode('enrollment', push_to_display=False)
            self.serial.send_display([
                "CLI Tools Hanya",
                "Gunakan capture_face",
                "fingerprint_wrapper",
                "*:Back"
            ])
            self.previous_state = SystemState.ENROLL_MENU
        time.sleep(0.2)

    def _state_enroll_unavailable(self, state_enum, extra_line='Gunakan tools CLI'):
        """Shared display for enrollment states unavailable in main system."""
        if self.previous_state != state_enum:
            self.logger.info(f"State: {state_enum.name} (unavailable in main system)")
            self.serial.send_display([
                "Enrollment tidak",
                "tersedia di sistem.",
                extra_line,
                ""
            ])
            self.previous_state = state_enum
        time.sleep(0.5)

    def _state_enroll_fingerprint(self):
        """Fingerprint enrollment - not available in main system"""
        self._state_enroll_unavailable(SystemState.ENROLL_FINGERPRINT)

    def _state_enroll_face(self):
        """Face enrollment - not available in main system"""
        self._state_enroll_unavailable(SystemState.ENROLL_FACE, "Gunakan: capture_face")

    def _build_attendance_record(self, now=None, status=None, overrides=None):
        """Build a spreadsheet record for normal attendance or monitoring events."""
        now = now or datetime.now()
        record = {
            'id': self.current_user_id,
            'name': self.current_user_name,
            'job': self.job_codes.get(self.job_selection, ''),
            'domain': self.domain_codes.get(self.domain_selection, ''),
            'domisili': self.domain_codes.get(self.domain_selection, ''),
            'shift_A': self.shift_A,
            'shift_B': self.shift_B,
            'shift_C': self.shift_C,
            'shift_D': self.shift_D,
            'shift_E': self.shift_E,
            'tanggal': now.strftime('%Y-%m-%d'),
            'waktu': now.strftime('%H:%M:%S'),
            'metode': 'biometrik',
            'foto': ''
        }

        if status is not None:
            record['status'] = status

        if overrides:
            record.update(overrides)

        return record

    def _submit_monitoring_record(self, failure_stage, image_path=''):
        """Upload failed biometric attempts so unknown or mismatched users are monitored."""
        stage_label = str(failure_stage or 'biometric').strip().lower()
        record = self._build_attendance_record(
            status='Unregistered',
            overrides={
                'job': '',
                'domain': '',
                'domisili': '-',
                'shift_A': '',
                'shift_B': '',
                'shift_C': '',
                'shift_D': '',
                'shift_E': '',
                'metode': f'{stage_label}_failed',
                'foto': image_path or ''
            }
        )

        success = self.absensi.upload_to_spreadsheet(record)
        if success:
            self.logger.info(f"Monitoring attendance uploaded for {stage_label} failure")
        else:
            self.logger.warning(f"Monitoring attendance queued locally for {stage_label} failure")
    
    def _submit_attendance(self):
        """Submit attendance to Google Sheets"""
        self.logger.info("Submitting attendance...")
        
        self.serial.send_display([
            "Mengirim data...",
            "",
            "",
            ""
        ])
        
        # Prepare record
        record = self._build_attendance_record(status='Registered')
        
        # Upload to spreadsheet
        success = self.absensi.upload_to_spreadsheet(record)
        
        if success:
            self.serial.send_display([
                "Absensi",
                "Tersimpan",
                "",
                ""
            ])
        else:
            self.serial.send_display([
                "Gagal kirim",
                "Tersimpan lokal",
                "",
                ""
            ])
        
        time.sleep(2)
        
        self._reset_session()
    
    def _handle_door_access(self):
        """Handle door access"""
        self.logger.info("Door access requested")
        
        # Open door
        duration = self.config.get('relay', {}).get('open_duration', 5)
        relay_open_sent = self.serial.send_relay('open', duration=duration)
        self.logger.info(f"Door relay OPEN command sent: {relay_open_sent}")
        
        # Log access
        self.logger.log_access(
            self.current_user_id,
            self.current_user_name,
            'granted',
            'biometric'
        )

        self.serial.send_display([
            "== PINTU TERBUKA ==",
            f"Halo, {self.current_user_name}",
            "Silakan masuk",
            ""
        ])

        time.sleep(duration)

        relay_close_sent = self.serial.send_relay('close')
        self.logger.info(f"Door relay CLOSE command sent: {relay_close_sent}")

        self._reset_session()
    
    def _state_error(self):
        """Error state"""
        self.logger.error("State: ERROR")
        
        self.serial.send_display([
            "Error sistem",
            "Mohon tunggu",
            "",
            ""
        ])
        
        time.sleep(3)
        
        self._reset_session()
    
    def _reset_shifts(self):
        """Clear shift input state."""
        self.shift_input_buffer = ""
        self.shift_A = self.shift_B = self.shift_C = self.shift_D = self.shift_E = None

    def _reset_session(self):
        """Reset session and return to idle"""
        self.logger.info("Resetting session")
        self.current_user_id = None
        self.current_user_name = None
        self.job_selection = None
        self.domain_selection = None
        self.input_buffer = ""
        self._reset_shifts()
        self.system_active = False
        self.emergency_active = False
        self.emergency_release_at = None
        self.state_before_emergency = None
        if self.emergency_timer:
            self.emergency_timer.cancel()
            self.emergency_timer = None
        self._set_device_mode('idle', push_to_display=False)
        # Immediately push idle screen so LCD doesn't stay stuck on the last menu
        if self.serial:
            try:
                self.serial.send_display([
                    "Touch sensor",
                    "untuk mulai",
                    "",
                    ""
                ])
            except Exception:
                pass
        self.state = SystemState.IDLE
        # Force the main loop to enter the IDLE branch normally on the next tick
        self.previous_state = None
    
    def cleanup(self):
        """Cleanup resources"""
        self.logger.info("Cleaning up resources...")
        self.stop_api_server()
        
        if self.biometric:
            self.biometric.cleanup()
        
        if self.serial:
            self.serial.disconnect()
        
        self.logger.info("=== System shutdown complete ===")


def main():
    """Entry point"""
    print("=" * 60)
    print("  LAB ROBOTIKA 2025 - INTEGRATED ATTENDANCE NGAWI SISTEM")
    print("  Raspberry Pi 5 + Arduino Nano + Biometric Sensors")
    print("=" * 60)
    print()
    
    try:
        system = LabAttendanceSystem()
        system.run()
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
