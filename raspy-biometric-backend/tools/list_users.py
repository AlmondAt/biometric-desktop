#!/usr/bin/env python3
"""
CLI Tool - List all enrolled users dan statistics
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.db_manager import BiometricDatabase
from datetime import datetime


def main():
    db = BiometricDatabase('biometrics.db')
    
    print("""
╔════════════════════════════════════════════╗
║      ENROLLED USERS LIST                   ║
╚════════════════════════════════════════════╝
    """)
    
    # Get stats
    stats = db.get_stats()
    print(f"📊 Database Statistics:")
    print(f"   Active Users: {stats['active_users']}")
    print(f"   Total Users: {stats['total_users']}")
    print(f"   Total Embeddings: {stats['total_embeddings']}")
    print(f"   Recognition Logs: {stats['recognition_logs']}\n")
    
    # Get all users
    all_users = db.get_all_users(status='all')
    
    if not all_users:
        print("No users enrolled yet.\n")
        return
    
    print("╔═══════════════════════════════════════════════════════════════════════════════╗")
    print("║ ID           │ Name                 │ Status      │ Enrolled       │ Embeddings ║")
    print("╠═══════════════════════════════════════════════════════════════════════════════╣")
    
    for user_id, name, enrollment_date, status in all_users:
        embeddings = db.get_user_embeddings(user_id)
        
        # Format fields
        id_str = user_id[:12].ljust(12)
        name_str = name[:20].ljust(20)
        status_str = status[:11].ljust(11)
        
        # Parse enrollment date
        try:
            enroll_date = datetime.fromisoformat(enrollment_date).strftime('%Y-%m-%d')
        except:
            enroll_date = enrollment_date[:10] if enrollment_date else "---"
        
        emb_count = str(len(embeddings)).ljust(10)
        
        print(f"║ {id_str} │ {name_str} │ {status_str} │ {enroll_date} │ {emb_count} ║")
    
    print("╚═══════════════════════════════════════════════════════════════════════════════╝\n")
    
    # Show recent recognitions
    recent_logs = db.get_recognition_log(limit=5)
    
    if recent_logs:
        print("📝 Recent Recognitions:")
        print("╔═══════════════════════════════════════════════════════════════════════════════╗")
        print("║ User ID         │ Name                 │ Confidence │ Timestamp          ║")
        print("╠═══════════════════════════════════════════════════════════════════════════════╣")
        
        for user_id, name, confidence, timestamp, method in recent_logs:
            user_str = (user_id or "---")[:15].ljust(15)
            name_str = (name or "?")[:20].ljust(20)
            conf_str = f"{confidence:.2f}".ljust(10)
            
            # Parse timestamp
            try:
                ts = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M')
            except:
                ts = str(timestamp)[:16]
            
            print(f"║ {user_str} │ {name_str} │ {conf_str} │ {ts} ║")
        
        print("╚═══════════════════════════════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
