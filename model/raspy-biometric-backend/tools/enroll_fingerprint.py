#!/usr/bin/env python3
"""
CLI Tool - Enroll Fingerprint ID ke database
Untuk Arduino fingerprint sensor
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.db_manager import BiometricDatabase


def main():
    print("""
╔════════════════════════════════════════════╗
║      FINGERPRINT ENROLLMENT TOOL           ║
║      Register Fingerprint ID               ║
╚════════════════════════════════════════════╝
    """)
    
    db = BiometricDatabase('biometrics.db')
    
    # Show list of users
    print("\n📋 Enrolled Users (without fingerprint):")
    all_users = db.get_all_users(status='active')
    
    users_without_fp = []
    for idx, (user_id, name, enrollment_date, status) in enumerate(all_users, 1):
        user_data = db.get_user(user_id)
        if user_data and not user_data[4]:  # fingerprint_id
            print(f"   {idx}. {user_id} - {name}")
            users_without_fp.append(user_id)
    
    if not users_without_fp:
        print("   All users already have fingerprint IDs")
        return
    
    print()
    user_id = input("📝 Masukkan User ID: ").strip()
    
    if user_id not in users_without_fp:
        print(f"❌ User ID {user_id} tidak ditemukan atau sudah punya fingerprint")
        return
    
    # Get fingerprint ID
    fp_id = input("👆 Masukkan Fingerprint ID (dari Arduino): ").strip()
    
    if not fp_id:
        print("❌ Fingerprint ID tidak boleh kosong")
        return
    
    # Update user with fingerprint
    try:
        from modules.db_manager import sqlite3, pickle
        
        conn = sqlite3.connect('biometrics.db')
        cursor = conn.cursor()
        
        cursor.execute('UPDATE users SET fingerprint_id = ? WHERE id = ?', (fp_id, user_id))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Fingerprint ID {fp_id} registered untuk user {user_id}")
    
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
