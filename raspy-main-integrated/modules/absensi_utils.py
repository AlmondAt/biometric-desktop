#!/usr/bin/env python3
"""
Attendance Utilities - Google Sheets integration and CSV fallback
"""

import requests
import csv
import os
from datetime import datetime


class AbsensiManager:
    def __init__(self, config, logger=None):
        self.config = config
        self.logger = logger
        
        self.web_app_url = config.get('google_sheets', {}).get('web_app_url', '')
        self.retry_interval = config.get('google_sheets', {}).get('retry_interval', 300)
        self.max_retries = config.get('google_sheets', {}).get('max_retries', 3)
        
        self.pending_csv = config.get('logging', {}).get('pending_csv', 'logs/absensi_pending.csv')
        self.attendance_history_csv = config.get(
            'logging', {}
        ).get('attendance_history_csv', 'logs/attendance_history.csv')
        
        # Ensure logs directory exists
        os.makedirs(os.path.dirname(self.pending_csv), exist_ok=True)
        os.makedirs(os.path.dirname(self.attendance_history_csv), exist_ok=True)

    def _compute_status(self, record):
        """Build the attendance registration status expected by the sheet."""
        if record.get('status') not in [None, '']:
            return record.get('status')
        return 'Registered' if record.get('name') and record.get('id') else 'Unregistered'

    def _compute_domisili(self, record):
        """Prefer an explicit domisili field and fall back to the selected domain."""
        domisili = record.get('domisili')
        if domisili not in [None, '']:
            return domisili
        domain = record.get('domain')
        return domain if domain not in [None, ''] else '-'

    def _get_next_akses_count(self, user_id):
        """Count prior attendance submissions for a user from the local history log."""
        if user_id in [None, '']:
            return 1

        normalized_user_id = str(user_id)
        if not os.path.isfile(self.attendance_history_csv):
            return 1

        try:
            with open(self.attendance_history_csv, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                previous_count = sum(
                    1 for row in reader if str(row.get('id', '')) == normalized_user_id
                )
            return previous_count + 1
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to read attendance history CSV: {e}")
            return 1

    def _append_to_attendance_history(self, record):
        """Persist a local record of attendance submissions for akses numbering."""
        try:
            file_exists = os.path.isfile(self.attendance_history_csv)
            fieldnames = ['timestamp', 'id', 'name', 'status', 'akses']

            with open(self.attendance_history_csv, 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()

                writer.writerow({
                    'timestamp': f"{record.get('tanggal', '')} {record.get('waktu', '')}".strip(),
                    'id': record.get('id', ''),
                    'name': record.get('name', ''),
                    'status': record.get('status', ''),
                    'akses': record.get('akses', ''),
                })
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to append attendance history CSV: {e}")

    def _build_payload(self, record):
        """Normalize the outgoing attendance payload for Google Sheets."""
        akses_value = record.get('akses')
        if akses_value in [None, '']:
            akses_value = self._get_next_akses_count(record.get('id'))

        payload = {
            'id': record.get('id', ''),
            'name': record.get('name', ''),
            'job': record.get('job', ''),
            'domain': record.get('domain', ''),
            'domisili': self._compute_domisili(record),
            'shift_A': record.get('shift_A', ''),
            'shift_B': record.get('shift_B', ''),
            'shift_C': record.get('shift_C', ''),
            'shift_D': record.get('shift_D', ''),
            'shift_E': record.get('shift_E', ''),
            'status': self._compute_status(record),
            'akses': akses_value,
            'metode': record.get('metode', 'biometrik')
        }

        normalized_record = dict(record)
        normalized_record.update({
            'domisili': payload['domisili'],
            'status': payload['status'],
            'akses': payload['akses']
        })
        return payload, normalized_record
    
    def upload_to_spreadsheet(self, record):
        """
        Upload attendance record to Google Sheets
        
        Args:
            record: Dictionary containing attendance data
                Required keys: id, name, job, domain, tanggal, waktu, metode
                Optional: foto (file path)
        
        Returns:
            bool: True if upload successful, False otherwise
        """
        if not self.web_app_url:
            if self.logger:
                self.logger.error("Google Sheets URL not configured")
            return False
        
        payload, normalized_record = self._build_payload(record)
        is_retry_upload = bool(record.get('_retry_upload'))
        
        try:
            response = requests.post(
              self.web_app_url,
              json=payload,
              timeout=10
            )
            
            if response.status_code == 200:
                if not is_retry_upload:
                    self._append_to_attendance_history(normalized_record)
                if self.logger:
                    self.logger.info(f"Attendance uploaded successfully: {normalized_record.get('name')}")
                return True
            else:
                if self.logger:
                    self.logger.error(f"Upload failed: HTTP {response.status_code}, {response.text}")
                if not is_retry_upload:
                    self._append_to_attendance_history(normalized_record)
                
                # Save to pending CSV
                if not is_retry_upload:
                    self._save_to_pending_csv(normalized_record)
                return False
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Upload exception: {e}")
            if not is_retry_upload:
                self._append_to_attendance_history(normalized_record)
            
            # Save to pending CSV
            if not is_retry_upload:
                self._save_to_pending_csv(normalized_record)
            return False
    
    def _save_to_pending_csv(self, record):
        """Save failed upload to CSV for later retry"""
        try:
            file_exists = os.path.isfile(self.pending_csv)
            fieldnames = [
                'timestamp', 'name', 'id', 'job', 'domain', 'domisili',
                'shift_A', 'shift_B', 'shift_C', 'shift_D', 'shift_E',
                'status', 'akses', 'metode', 'foto'
            ]
            
            with open(self.pending_csv, 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                writer.writerow({
                    'timestamp': f"{record.get('tanggal')} {record.get('waktu')}",
                    'name': record.get('name', 'Unknown'),
                    'id': record.get('id', ''),
                    'job': record.get('job', ''),
                    'domain': record.get('domain', ''),
                    'domisili': record.get('domisili', ''),
                    'shift_A': record.get('shift_A', ''),
                    'shift_B': record.get('shift_B', ''),
                    'shift_C': record.get('shift_C', ''),
                    'shift_D': record.get('shift_D', ''),
                    'shift_E': record.get('shift_E', ''),
                    'status': record.get('status', ''),
                    'akses': record.get('akses', ''),
                    'metode': record.get('metode', 'biometric'),
                    'foto': record.get('foto', ''),
                })
            
            if self.logger:
                self.logger.info(f"Record saved to pending CSV: {record.get('name')}")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to save to pending CSV: {e}")
    
    def retry_pending_uploads(self):
        """
        Retry uploading records from pending CSV
        
        Returns:
            int: Number of successful uploads
        """
        if not os.path.isfile(self.pending_csv):
            return 0
        
        successful = 0
        remaining = []
        
        try:
            with open(self.pending_csv, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                records = list(reader)
            
            for record in records:
                # Convert CSV record back to format for upload
                upload_record = {
                    'tanggal': record['timestamp'].split()[0],
                    'waktu': record['timestamp'].split()[1] if len(record['timestamp'].split()) > 1 else '00:00:00',
                    'name': record.get('name', ''),
                    'id': record.get('id', ''),
                    'job': record.get('job', ''),
                    'domain': record.get('domain', ''),
                    'domisili': record.get('domisili', record.get('domain', '')),
                    'shift_A': record.get('shift_A', ''),
                    'shift_B': record.get('shift_B', ''),
                    'shift_C': record.get('shift_C', ''),
                    'shift_D': record.get('shift_D', ''),
                    'shift_E': record.get('shift_E', ''),
                    'status': record.get('status', ''),
                    'akses': record.get('akses', ''),
                    'metode': record.get('metode', 'biometric'),
                    'foto': record.get('foto', ''),
                    '_retry_upload': True,
                }
                
                if self.upload_to_spreadsheet(upload_record):
                    successful += 1
                else:
                    remaining.append(record)
            
            # Rewrite pending CSV with only failed records
            if remaining:
                with open(self.pending_csv, 'w', newline='') as csvfile:
                    fieldnames = [
                        'timestamp', 'name', 'id', 'job', 'domain', 'domisili',
                        'shift_A', 'shift_B', 'shift_C', 'shift_D', 'shift_E',
                        'status', 'akses', 'metode', 'foto'
                    ]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(remaining)
            else:
                # All uploaded, delete CSV
                os.remove(self.pending_csv)
            
            if self.logger:
                self.logger.info(f"Retry complete: {successful} uploaded, {len(remaining)} remaining")
            
            return successful
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to retry pending uploads: {e}")
            return 0
