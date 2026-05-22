"""
Database Manager - Handle SQLite operations untuk biometrics.db
"""
import sqlite3
import pickle
import numpy as np
from datetime import datetime
import os


class BiometricDatabase:
    """SQLite database manager untuk face embeddings dan user data"""
    
    def __init__(self, db_path='biometrics.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Create tables jika belum ada"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table - simpan info user dan fingerprint ID
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active',
            fingerprint_id TEXT,
            notes TEXT
        )
        ''')
        
        # Embeddings table - simpan face embeddings (512-dim vectors)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            embedding BLOB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source TEXT DEFAULT 'desktop',
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        ''')
        
        # Recognition logs table - audit trail
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS recognition_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            recognized_name TEXT,
            confidence REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            method TEXT,
            device TEXT DEFAULT 'raspy'
        )
        ''')
        
        # Fingerprint ID mapping (untuk fingerprint scanner)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS fingerprint_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            fingerprint_id TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        ''')
        
        # Create index untuk faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON embeddings(user_id)')
        user_columns = self._get_table_columns(cursor, 'users')
        if 'status' in user_columns:
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_status ON users(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_recognition_user ON recognition_logs(user_id)')
        
        conn.commit()
        conn.close()

    def _get_table_columns(self, cursor, table_name):
        cursor.execute(f"PRAGMA table_info({table_name})")
        return {row[1] for row in cursor.fetchall()}

    def _has_table(self, cursor, table_name):
        cursor.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
            (table_name,)
        )
        return cursor.fetchone() is not None
    
    def add_user(self, user_id, name, fingerprint_id=None, notes=None):
        """Tambah user baru ke database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO users (id, name, fingerprint_id, status, notes)
            VALUES (?, ?, ?, 'active', ?)
            ''', (user_id, name, fingerprint_id, notes))
            
            conn.commit()
            conn.close()
            return True, f"User {name} added successfully"
        
        except sqlite3.IntegrityError:
            return False, f"User ID {user_id} already exists"
        except Exception as e:
            return False, str(e)
    
    def store_embeddings(self, user_id, embeddings_array, source='desktop'):
        """Store face embeddings untuk user (bisa multiple)"""
        try:
            if isinstance(embeddings_array, list):
                embeddings_array = np.array(embeddings_array)
            
            # Validate embedding size (should be 512-dim for FaceNet)
            if embeddings_array.ndim == 1:
                if len(embeddings_array) != 512:
                    return False, f"Embedding size should be 512, got {len(embeddings_array)}"
                embeddings_list = [embeddings_array]
            else:
                # Multiple embeddings
                embeddings_list = embeddings_array
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Store each embedding
            for emb in embeddings_list:
                embedding_blob = pickle.dumps(np.array(emb))
                cursor.execute('''
                INSERT INTO embeddings (user_id, embedding, source)
                VALUES (?, ?, ?)
                ''', (user_id, embedding_blob, source))
            
            conn.commit()
            conn.close()
            return True, f"Stored {len(embeddings_list)} embeddings for user {user_id}"
        
        except Exception as e:
            return False, str(e)
    
    def get_all_embeddings(self, active_only=True):
        """Get semua embeddings untuk matching (return dict by user_id)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            user_columns = self._get_table_columns(cursor, 'users')
            has_embeddings_table = self._has_table(cursor, 'embeddings')

            if not has_embeddings_table:
                if 'face_embedding_path' in user_columns:
                    cursor.execute('SELECT id, name, face_embedding_path FROM users ORDER BY id')
                    results = cursor.fetchall()
                    conn.close()

                    embeddings_dict = {}
                    for user_id, name, face_embedding_path in results:
                        if face_embedding_path:
                            embeddings_dict[user_id] = {
                                'name': name,
                                'embeddings': [face_embedding_path]
                            }

                    return embeddings_dict

                conn.close()
                return {}
            
            if active_only and 'status' in user_columns:
                cursor.execute('''
                SELECT u.id, u.name, e.embedding
                FROM users u
                LEFT JOIN embeddings e ON u.id = e.user_id
                WHERE u.status = 'active'
                ORDER BY u.id
                ''')
            else:
                cursor.execute('''
                SELECT u.id, u.name, e.embedding
                FROM users u
                LEFT JOIN embeddings e ON u.id = e.user_id
                ORDER BY u.id
                ''')
            
            results = cursor.fetchall()
            conn.close()
            
            embeddings_dict = {}
            for user_id, name, embedding_blob in results:
                if embedding_blob:
                    embedding = pickle.loads(embedding_blob)
                    if user_id not in embeddings_dict:
                        embeddings_dict[user_id] = {
                            'name': name,
                            'embeddings': []
                        }
                    embeddings_dict[user_id]['embeddings'].append(embedding)
            
            return embeddings_dict
        
        except Exception as e:
            print(f"Error getting embeddings: {e}")
            return {}
    
    def get_user_embeddings(self, user_id):
        """Get semua embeddings untuk specific user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            user_columns = self._get_table_columns(cursor, 'users')
            has_embeddings_table = self._has_table(cursor, 'embeddings')

            if not has_embeddings_table:
                if 'face_embedding_path' in user_columns:
                    cursor.execute('SELECT face_embedding_path FROM users WHERE id = ?', (user_id,))
                    row = cursor.fetchone()
                    conn.close()
                    return [row[0]] if row and row[0] else []

                conn.close()
                return []
            
            cursor.execute('''
            SELECT embedding FROM embeddings WHERE user_id = ? ORDER BY created_at
            ''', (user_id,))
            
            embedding_rows = cursor.fetchall()
            conn.close()
            
            embeddings = []
            for emb_blob in embedding_rows:
                embedding = pickle.loads(emb_blob[0])
                embeddings.append(embedding)
            
            return embeddings
        
        except Exception as e:
            print(f"Error getting user embeddings: {e}")
            return []
    
    def log_recognition(self, user_id, recognized_name, confidence, method='face', device='raspy'):
        """Log recognition event untuk audit"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO recognition_logs (user_id, recognized_name, confidence, method, device)
            VALUES (?, ?, ?, ?, ?)
            ''', (user_id, recognized_name, confidence, method, device))
            
            conn.commit()
            conn.close()
            return True
        
        except Exception as e:
            print(f"Error logging recognition: {e}")
            return False
    
    def get_user(self, user_id):
        """Get user info by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            user_columns = self._get_table_columns(cursor, 'users')

            date_column = 'enrollment_date' if 'enrollment_date' in user_columns else 'registration_date'
            status_expr = 'status' if 'status' in user_columns else "'active'"
            
            cursor.execute(
                f'''
                SELECT id, name, {date_column}, {status_expr}, fingerprint_id
                FROM users WHERE id = ?
                ''',
                (user_id,)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            return result
        
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def get_all_users(self, status='all'):
        """Get all users"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            user_columns = self._get_table_columns(cursor, 'users')
            date_column = 'enrollment_date' if 'enrollment_date' in user_columns else 'registration_date'
            has_status = 'status' in user_columns
            
            if status == 'all' or not has_status:
                status_expr = 'status' if has_status else "'active'"
                cursor.execute(
                    f'SELECT id, name, {date_column}, {status_expr} FROM users ORDER BY name'
                )
            else:
                cursor.execute(
                    f'''
                    SELECT id, name, {date_column}, status
                    FROM users WHERE status = ? ORDER BY name
                    ''',
                    (status,)
                )
            
            results = cursor.fetchall()
            conn.close()
            
            return results
        
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    def update_user_status(self, user_id, status):
        """Update user status (active/inactive)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('UPDATE users SET status = ? WHERE id = ?', (status, user_id))
            
            conn.commit()
            conn.close()
            
            return True, f"User {user_id} status updated to {status}"
        
        except Exception as e:
            return False, str(e)
    
    def delete_user(self, user_id):
        """Delete user dan semua associated data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete embeddings
            cursor.execute('DELETE FROM embeddings WHERE user_id = ?', (user_id,))
            
            # Delete fingerprint templates
            cursor.execute('DELETE FROM fingerprint_templates WHERE user_id = ?', (user_id,))
            
            # Delete user
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            
            conn.commit()
            conn.close()
            
            return True, f"User {user_id} deleted successfully"
        
        except Exception as e:
            return False, str(e)
    
    def get_stats(self):
        """Get database statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            user_columns = self._get_table_columns(cursor, 'users')
            has_embeddings_table = self._has_table(cursor, 'embeddings')
            has_logs_table = self._has_table(cursor, 'recognition_logs')
            
            if 'status' in user_columns:
                cursor.execute('SELECT COUNT(*) FROM users WHERE status = "active"')
                active_users = cursor.fetchone()[0]
            else:
                cursor.execute('SELECT COUNT(*) FROM users')
                active_users = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM users')
            total_users = cursor.fetchone()[0]
            
            if has_embeddings_table:
                cursor.execute('SELECT COUNT(*) FROM embeddings')
                total_embeddings = cursor.fetchone()[0]
            elif 'face_embedding_path' in user_columns:
                cursor.execute('SELECT COUNT(*) FROM users WHERE face_embedding_path IS NOT NULL')
                total_embeddings = cursor.fetchone()[0]
            else:
                total_embeddings = 0
            
            if has_logs_table:
                cursor.execute('SELECT COUNT(*) FROM recognition_logs')
                total_logs = cursor.fetchone()[0]
            else:
                total_logs = 0
            
            conn.close()
            
            return {
                'active_users': active_users,
                'total_users': total_users,
                'total_embeddings': total_embeddings,
                'recognition_logs': total_logs
            }
        
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}
    
    def get_recognition_log(self, user_id=None, limit=50):
        """Get recognition logs"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute('''
                SELECT user_id, recognized_name, confidence, timestamp, method
                FROM recognition_logs WHERE user_id = ?
                ORDER BY timestamp DESC LIMIT ?
                ''', (user_id, limit))
            else:
                cursor.execute('''
                SELECT user_id, recognized_name, confidence, timestamp, method
                FROM recognition_logs
                ORDER BY timestamp DESC LIMIT ?
                ''', (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            return results
        
        except Exception as e:
            print(f"Error getting recognition logs: {e}")
            return []
