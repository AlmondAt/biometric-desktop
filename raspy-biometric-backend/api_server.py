#!/usr/bin/env python3
"""
Flask API Server - Biometric Backend untuk Raspberry Pi
Endpoints untuk enrollment dan face recognition
"""
import sys
import os
import yaml
import numpy as np
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import modules
from modules.db_manager import BiometricDatabase
from modules.face_matcher import FaceMatcher


# ==================== Flask App Setup ====================

app = Flask(__name__)
CORS(app)

# Load configuration
config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
with open(config_path, 'r') as f:
    CONFIG = yaml.safe_load(f)


def resolve_database_path(config_file_path, configured_path):
    if os.path.isabs(configured_path):
        return configured_path

    config_dir = os.path.dirname(config_file_path)
    return os.path.abspath(os.path.join(config_dir, configured_path))

# Initialize components
DB = BiometricDatabase(resolve_database_path(config_path, CONFIG['database']['path']))
MATCHER = FaceMatcher(CONFIG['recognition']['similarity_threshold'])


# ==================== API Endpoints ====================

@app.route('/api/status', methods=['GET'])
def api_status():
    """Health check endpoint"""
    try:
        stats = DB.get_stats()
        
        return jsonify({
            'success': True,
            'status': 'online',
            'timestamp': datetime.now().isoformat(),
            'stats': stats
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/enroll', methods=['POST'])
def api_enroll():
    """
    Enroll new user dengan face embeddings
    
    Expected JSON:
    {
        "user_id": "user_001",
        "name": "Budi Santoso",
        "embeddings": [[0.124, -0.456, ...], [...], ...],
        "fingerprint_id": "FP001" (optional),
        "notes": "..." (optional)
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        user_id = data.get('user_id', '').strip()
        name = data.get('name', '').strip()
        embeddings_list = data.get('embeddings', [])
        fingerprint_id = data.get('fingerprint_id')
        notes = data.get('notes')
        
        if not user_id or not name:
            return jsonify({
                'success': False,
                'error': 'user_id dan name wajib diisi'
            }), 400
        
        if not embeddings_list:
            return jsonify({
                'success': False,
                'error': 'embeddings tidak boleh kosong'
            }), 400
        
        # Add user
        success, msg = DB.add_user(user_id, name, fingerprint_id, notes)
        if not success:
            return jsonify({
                'success': False,
                'error': msg
            }), 400
        
        # Store embeddings
        success, msg = DB.store_embeddings(user_id, embeddings_list, source='desktop')
        if not success:
            return jsonify({
                'success': False,
                'error': msg
            }), 400
        
        return jsonify({
            'success': True,
            'message': f'User {name} enrolled dengan {len(embeddings_list)} embeddings',
            'user_id': user_id
        }), 201
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/recognize', methods=['POST'])
def api_recognize():
    """
    Real-time face recognition
    
    Expected JSON:
    {
        "embedding": [0.124, -0.456, ...]
    }
    """
    try:
        data = request.get_json()
        
        test_embedding = data.get('embedding')
        if not test_embedding:
            return jsonify({
                'success': False,
                'error': 'embedding required'
            }), 400
        
        # Validate embedding size
        test_embedding = np.array(test_embedding)
        if len(test_embedding) != 512:
            return jsonify({
                'success': False,
                'error': f'Embedding size harus 512, got {len(test_embedding)}'
            }), 400
        
        # Get all embeddings dari database
        embeddings_dict = DB.get_all_embeddings(active_only=True)
        
        if not embeddings_dict:
            return jsonify({
                'success': True,
                'matched': False,
                'message': 'Database kosong, tidak ada user terdata'
            }), 200
        
        # Perform matching
        result = MATCHER.match_face(test_embedding, embeddings_dict)
        
        # Log recognition jika ada match
        if result['matched']:
            DB.log_recognition(
                result['user_id'],
                result['name'],
                result['confidence'],
                method='face',
                device='raspy'
            )
        
        return jsonify({
            'success': True,
            'matched': result['matched'],
            'user_id': result['user_id'],
            'name': result['name'],
            'confidence': result['confidence'],
            'top_matches': result['all_matches'][:5]  # Top 5 matches
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/users', methods=['GET'])
def api_get_users():
    """Get list semua enrolled users"""
    try:
        status_filter = request.args.get('status', 'active')  # active, inactive, all
        
        users = DB.get_all_users(status=status_filter)
        
        # Format response dengan embedding count
        users_list = []
        for index, (user_id, name, enrollment_date, status) in enumerate(users, 1):
            user = DB.get_user(user_id)
            embeddings = DB.get_user_embeddings(user_id)
            fingerprint_id = user[4] if user else None
            users_list.append({
                'user_id': user_id,
                'name': name,
                'enrollment_date': enrollment_date,
                'status': status,
                'display_no': index,
                'has_fingerprint': fingerprint_id is not None,
                'has_face': len(embeddings) > 0,
                'embedding_count': len(embeddings)
            })
        
        return jsonify({
            'success': True,
            'count': len(users_list),
            'users': users_list
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/users/<user_id>', methods=['GET'])
def api_get_user(user_id):
    """Get detail user tertentu"""
    try:
        user = DB.get_user(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': f'User {user_id} tidak ditemukan'
            }), 404
        
        embeddings = DB.get_user_embeddings(user_id)
        logs = DB.get_recognition_log(user_id, limit=10)
        
        return jsonify({
            'success': True,
            'user': {
                'user_id': user[0],
                'name': user[1],
                'enrollment_date': user[2],
                'status': user[3],
                'fingerprint_id': user[4],
                'embedding_count': len(embeddings),
                'last_recognition': logs[0] if logs else None,
                'recent_logs': logs
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/users/<user_id>', methods=['DELETE'])
def api_delete_user(user_id):
    """Delete/deactivate user"""
    try:
        action = request.args.get('action', 'deactivate')  # deactivate or delete
        
        if action == 'delete':
            # Permanent delete
            success, msg = DB.delete_user(user_id)
            if not success:
                return jsonify({
                    'success': False,
                    'error': msg
                }), 400
            
            return jsonify({
                'success': True,
                'message': f'User {user_id} deleted permanently'
            }), 200
        
        else:
            # Deactivate (soft delete)
            success, msg = DB.update_user_status(user_id, 'inactive')
            if not success:
                return jsonify({
                    'success': False,
                    'error': msg
                }), 400
            
            return jsonify({
                'success': True,
                'message': f'User {user_id} deactivated'
            }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/users/<user_id>/status', methods=['PUT'])
def api_update_user_status(user_id):
    """Update user status"""
    try:
        data = request.get_json()
        new_status = data.get('status', 'active')
        
        if new_status not in ['active', 'inactive']:
            return jsonify({
                'success': False,
                'error': f'Invalid status: {new_status}'
            }), 400
        
        success, msg = DB.update_user_status(user_id, new_status)
        
        if not success:
            return jsonify({
                'success': False,
                'error': msg
            }), 400
        
        return jsonify({
            'success': True,
            'message': msg
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/recognition-logs', methods=['GET'])
def api_get_logs():
    """Get recognition logs"""
    try:
        user_id = request.args.get('user_id')
        limit = int(request.args.get('limit', 50))
        
        logs = DB.get_recognition_log(user_id=user_id, limit=limit)
        
        logs_list = [
            {
                'user_id': log[0],
                'name': log[1],
                'confidence': log[2],
                'timestamp': log[3],
                'method': log[4]
            }
            for log in logs
        ]
        
        return jsonify({
            'success': True,
            'count': len(logs_list),
            'logs': logs_list
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stats', methods=['GET'])
def api_get_stats():
    """Get database statistics"""
    try:
        stats = DB.get_stats()
        
        return jsonify({
            'success': True,
            'stats': stats,
            'config': {
                'similarity_threshold': CONFIG['recognition']['similarity_threshold'],
                'embedding_size': CONFIG['recognition']['embedding_size']
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/config', methods=['GET'])
def api_get_config():
    """Get system configuration"""
    try:
        safe_config = {
            'recognition': CONFIG.get('recognition', {}),
            'mtcnn': CONFIG.get('mtcnn', {}),
            'processing': CONFIG.get('processing', {})
        }
        
        return jsonify({
            'success': True,
            'config': safe_config
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint tidak ditemukan'
    }), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        'success': False,
        'error': 'Server error'
    }), 500


# ==================== Main ====================

if __name__ == '__main__':
    # Get config
    api_host = CONFIG['api']['host']
    api_port = CONFIG['api']['port']
    debug_mode = CONFIG['api'].get('debug', False)
    
    print(f"""
╔════════════════════════════════════════════╗
║   Biometric Backend - Raspberry Pi 5       ║
║   Flask API Server                         ║
╚════════════════════════════════════════════╝

🚀 Starting server...
📌 Host: {api_host}
📌 Port: {api_port}
📌 Debug: {debug_mode}
📊 Database: {CONFIG['database']['path']}

Endpoints:
  GET  /api/status
  POST /api/enroll
  POST /api/recognize
  GET  /api/users
  GET  /api/stats

Press CTRL+C to stop.
    """)
    
    app.run(host=api_host, port=api_port, debug=debug_mode)
