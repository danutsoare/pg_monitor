from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class MonitoredDatabase(BaseModel):
    __tablename__ = "monitored_databases"

    name = Column(String, index=True, nullable=False)
    host = Column(String, nullable=False)
    port = Column(Integer, default=5432, nullable=False)
    dbname = Column(String, nullable=False)
    username = Column(String, nullable=False)
    password_encrypted = Column(String, nullable=False)  # Placeholder for encrypted password
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    snapshots = relationship("Snapshot", back_populates="database", cascade="all, delete-orphan") 