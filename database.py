import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. We look for a 'DATABASE_URL' environment variable (sent by Docker).
# 2. If it's not found, we use your local localhost connection.
# Change this line in your code
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:312004@host.docker.internal:5432/curriculum_db"

# Create the SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a SessionLocal class for database transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our database models
Base = declarative_base()

# Dependency to get a database session in our FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()