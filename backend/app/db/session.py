from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create SQLAlchemy engine
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)

# Create sessionmaker with the engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for declarative models
# Base = declarative_base() # This seems redundant if base_class.py is used

# Dependency to get DB session (MOVED to app.api.deps)
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()