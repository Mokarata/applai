# pylint: disable=wrong-import-position
import argparse
import os
import sys

# Adjust sys.path to allow imports from the parent directory (project root)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.append(PROJECT_ROOT)

from app.core.logging import get_logger
from app.db.database import SessionLocal
from app.db.models import User

logger = get_logger(__name__)


def toggle_user_admin_status(user_id: int):
    """Toggles the admin status of the user with the given email."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error("User with id '%s' not found.", user_id)
            return

        current_status = user.is_admin
        user.is_admin = not current_status
        db.commit()

        if user.is_admin:
            logger.info("Successfully promoted user '%s' to admin.", user_id)
        else:
            logger.info("Successfully demoted user '%s' to normal user.", user_id)

    except Exception:
        db.rollback()
        logger.exception(
            "An error occurred while toggling admin status for user '%s'", user_id
        )
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Toggle a user's admin status (promote to admin or demote to normal user)."
    )
    parser.add_argument(
        "user_id", type=int, help="The ID of the user whose admin status to toggle."
    )
    args = parser.parse_args()

    toggle_user_admin_status(args.user_id)
