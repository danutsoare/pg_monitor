from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

# Import the common BaseClass
from app.db.base_class import BaseClass


class Connection(BaseClass):
    __tablename__ = "monitored_databases" # Explicitly set table name
    # id = Column(Integer, primary_key=True, index=True) # Now defined in BaseClass

    # Columns must match the actual database schema revealed by information_schema
    alias = Column(String, index=True, nullable=False) # Renamed from name
    hostname = Column(String, nullable=False) # Renamed from host
    port = Column(Integer, nullable=False, default=5432)
    db_name = Column(String, nullable=False) # Renamed from dbname
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)  # Renamed from password_encrypted
    # is_active = Column(Boolean, default=True) # Removed, does not exist in DB
    # is_monitored = Column(Boolean, default=True)  # Removed, does not exist in DB

    # Relationships
    snapshots = relationship("Snapshot", back_populates="database", cascade="all, delete-orphan") 