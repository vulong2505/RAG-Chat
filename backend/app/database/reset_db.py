from sqlalchemy import create_engine
from app.config.settings import settings
from app.models.database import Base

def reset_db():
    # Connect to the database
    engine = create_engine(settings.DATABASE_URL)
    
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    
    # Recreate all tables
    Base.metadata.create_all(bind=engine)
    
    print("Database has been reset.")

if __name__ == "__main__":
    reset_db()