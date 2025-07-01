from .database import engine
from .models import Base


# Create database tables
def create_tables():
    """Create database tables."""
    Base.metadata.create_all(engine)
