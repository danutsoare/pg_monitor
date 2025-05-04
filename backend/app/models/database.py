from sqlalchemy import Column, Integer, String
# from app.db.base_class import Base # Old import
from app.db.base import Base # Import from the new base.py
from sqlalchemy.orm import relationship

class MonitoredDatabase(Base):
    __tablename__ = "monitored_databases"

    id = Column(Integer, primary_key=True, index=True)
    alias = Column(String, index=True, unique=True, nullable=False)
    hostname = Column(String, nullable=False)
    port = Column(Integer, nullable=False, default=5432)
    username = Column(String, nullable=False)
    db_name = Column(String, nullable=False)
    # TODO: Store a HASHED password, not the raw password.
    # The length should accommodate common hash outputs (e.g., 60 for bcrypt)
    # For now, using String without length constraints for simplicity during dev.
    hashed_password = Column(String, nullable=False)

    # Columns from initial migration not in current model: is_active, created_at, updated_at

    # Relationships (if needed later, e.g., to snapshots)
    snapshots = relationship("Snapshot", back_populates="database", cascade="all, delete-orphan") 