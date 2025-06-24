import argparse
import os
import sys

# Adjust sys.path to allow imports from the parent directory (project root)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.append(PROJECT_ROOT)

from app.db.database import SessionLocal
from app.db.models import User

def toggle_user_admin_status(user_id: int):
    """Toggles the admin status of the user with the given email."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"Error: User with id '{user_id}' not found.")
            return

        current_status = user.is_admin
        user.is_admin = not current_status
        db.commit()

        if user.is_admin:
            print(f"Successfully promoted user '{user_id}' to admin.")
        else:
            print(f"Successfully demoted user '{user_id}' to normal user.")

    except Exception as e:
        db.rollback()
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Toggle a user's admin status (promote to admin or demote to normal user).")
    parser.add_argument("user_id", type=int, help="The ID of the user whose admin status to toggle.")
    args = parser.parse_args()

    toggle_user_admin_status(args.user_id)
