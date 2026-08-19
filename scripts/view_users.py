import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.db.session import SessionLocal
from app.models.user import User
from app.models.user_preference import UserPreference

def view_all_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print("\n" + "="*70)
        print(" REGISTERED USERS IN DATABASE")
        print("="*70)
        if not users:
            print("No registered users found in database.")
            return

        for u in users:
            pref = db.query(UserPreference).filter(UserPreference.user_id == u.id).first()
            print(f"\nUser ID        : {u.id}")
            print(f"Username       : {u.username}")
            print(f"Email          : {u.email}")
            print(f"Full Name      : {u.full_name or 'N/A'}")
            print(f"Created At     : {u.created_at}")
            if pref:
                print(f"Onboarding     : COMPLETED")
                print(f"Preferred Genres   : {pref.genres}")
                print(f"Preferred Duration : {pref.duration}")
                print(f"Preferred Years    : {pref.release_year}")
            else:
                print(f"Onboarding     : PENDING / NOT STARTED")
            print("-" * 50)
    finally:
        db.close()

if __name__ == "__main__":
    view_all_users()
