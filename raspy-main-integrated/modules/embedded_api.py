"""Embedded HTTP API handler factory for the desktop bridge."""

import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse


def make_api_handler(system):
    """Return a BaseHTTPRequestHandler subclass that delegates to *system*."""

    class EmbeddedApiHandler(BaseHTTPRequestHandler):
        def _send_json(self, status_code, payload):
            response = json.dumps(payload).encode('utf-8')
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(response)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            self.end_headers()
            self.wfile.write(response)

        def _read_json(self):
            content_length = int(self.headers.get('Content-Length', '0'))
            if content_length <= 0:
                return {}
            raw_body = self.rfile.read(content_length)
            if not raw_body:
                return {}
            return json.loads(raw_body.decode('utf-8'))

        def _extract_user_id(self, path):
            parts = [p for p in path.split('/') if p]
            if len(parts) >= 3 and parts[0] == 'api' and parts[1] == 'users':
                try:
                    return int(parts[2])
                except ValueError:
                    return None
            return None

        def _require_user_id(self, payload):
            """Return (user_id, None) on success or (None, (status, body)) on failure."""
            uid = payload.get('user_id', payload.get('id'))
            if uid is None:
                return None, (400, {'message': 'user_id is required'})
            return int(uid), None

        def do_OPTIONS(self):
            self._send_json(200, {'status': 'ok'})

        def do_GET(self):
            path = urlparse(self.path).path.rstrip('/') or '/'
            try:
                if path == '/api/health':
                    self._send_json(200, {
                        'status': 'ok',
                        'service': 'main_integrated_api',
                        'device_mode': system.device_mode,
                        'db_path': system.db_path,
                        'embeddings_path': system.embeddings_path
                    })
                    return

                if path == '/api/users':
                    self._send_json(200, system._list_users())
                    return

                if path == '/api/logs':
                    self._send_json(200, system._list_logs())
                    return

                if path == '/api/device/mode':
                    self._send_json(200, {
                        'mode': system.device_mode,
                        'updated_at': system.device_mode_updated_at.isoformat()
                    })
                    return

                user_id = self._extract_user_id(path)
                if user_id is not None:
                    users = [u for u in system._list_users() if int(u['id']) == user_id]
                    if users:
                        self._send_json(200, users[0])
                    else:
                        self._send_json(404, {'message': 'user not found'})
                    return

                self._send_json(404, {'message': 'endpoint not found'})
            except Exception as e:
                system.logger.error(f'API GET error on {path}: {e}')
                self._send_json(500, {'message': str(e)})

        def do_POST(self):
            path = urlparse(self.path).path.rstrip('/') or '/'
            try:
                payload = self._read_json()

                if path == '/api/add-user':
                    _, resp, code = system._create_user(payload)
                    self._send_json(code, resp)
                    return

                if path == '/api/update-user':
                    uid, err = self._require_user_id(payload)
                    if err:
                        self._send_json(*err)
                        return
                    _, resp, code = system._update_user(uid, payload)
                    self._send_json(code, resp)
                    return

                if path == '/api/enroll-face':
                    _, resp, code = system._upsert_face_embedding(payload)
                    self._send_json(code, resp)
                    return

                if path in ('/api/enroll-fingerprint', '/api/fingerprint/enroll'):
                    _, resp, code = system._enroll_fingerprint(payload)
                    self._send_json(code, resp)
                    return

                user_id = self._extract_user_id(path)
                if user_id is not None:
                    parts = [p for p in path.split('/') if p]
                    if len(parts) == 4 and parts[3] == 'fingerprint':
                        merged_payload = dict(payload)
                        merged_payload.setdefault('user_id', user_id)
                        _, resp, code = system._enroll_fingerprint(merged_payload)
                        self._send_json(code, resp)
                        return

                if path == '/api/delete-face':
                    uid, err = self._require_user_id(payload)
                    if err:
                        self._send_json(*err)
                        return
                    _, resp, code = system._clear_face_data(uid)
                    self._send_json(code, resp)
                    return

                if path == '/api/delete-fingerprint':
                    uid, err = self._require_user_id(payload)
                    if err:
                        self._send_json(*err)
                        return
                    _, resp, code = system._clear_fingerprint_data(uid)
                    self._send_json(code, resp)
                    return

                if path == '/api/cancel-enrollment':
                    uid, err = self._require_user_id(payload)
                    if err:
                        self._send_json(*err)
                        return
                    # Clear incomplete enrollment data (both face and fingerprint)
                    _, face_resp, face_code = system._clear_face_data(uid)
                    _, fp_resp, fp_code = system._clear_fingerprint_data(uid)
                    self._send_json(200, {
                        'status': 'ok',
                        'message': 'enrollment cancelled - all biometric data cleared',
                        'face_cleared': face_resp.get('removed_embedding', False),
                        'fingerprint_cleared': fp_resp.get('sensor_deleted', False)
                    })
                    return

                if path == '/api/device/mode':
                    _, resp, code = system._set_external_device_mode(payload)
                    self._send_json(code, resp)
                    return

                self._send_json(404, {'message': 'endpoint not found'})
            except json.JSONDecodeError:
                self._send_json(400, {'message': 'invalid JSON payload'})
            except Exception as e:
                system.logger.error(f'API POST error on {path}: {e}')
                self._send_json(500, {'message': str(e)})

        def do_PUT(self):
            path = urlparse(self.path).path.rstrip('/') or '/'
            try:
                user_id = self._extract_user_id(path)
                if user_id is None:
                    self._send_json(404, {'message': 'endpoint not found'})
                    return
                _, resp, code = system._update_user(user_id, self._read_json())
                self._send_json(code, resp)
            except json.JSONDecodeError:
                self._send_json(400, {'message': 'invalid JSON payload'})
            except Exception as e:
                system.logger.error(f'API PUT error on {path}: {e}')
                self._send_json(500, {'message': str(e)})

        def do_DELETE(self):
            path = urlparse(self.path).path.rstrip('/') or '/'
            try:
                user_id = self._extract_user_id(path)
                if user_id is not None:
                    parts = [p for p in path.split('/') if p]
                    if len(parts) == 3:
                        _, resp, code = system._delete_user(user_id)
                        self._send_json(code, resp)
                        return
                    if len(parts) == 4 and parts[3] == 'face':
                        _, resp, code = system._clear_face_data(user_id)
                        self._send_json(code, resp)
                        return
                    if len(parts) == 4 and parts[3] == 'fingerprint':
                        _, resp, code = system._clear_fingerprint_data(user_id)
                        self._send_json(code, resp)
                        return
                self._send_json(404, {'message': 'endpoint not found'})
            except Exception as e:
                system.logger.error(f'API DELETE error on {path}: {e}')
                self._send_json(500, {'message': str(e)})

        def log_message(self, format_string, *args):
            system.logger.debug('API: ' + (format_string % args))

    return EmbeddedApiHandler
