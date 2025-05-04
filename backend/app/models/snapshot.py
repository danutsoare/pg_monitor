from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import BaseModel


class Snapshot(BaseModel):
    __tablename__ = "snapshots"

    database_id = Column(Integer, ForeignKey("monitored_databases.id"), nullable=False, index=True)
    snapshot_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    database = relationship("MonitoredDatabase", back_populates="snapshots")
    session_activities = relationship("SessionActivity", back_populates="snapshot", cascade="all, delete-orphan")
    statement_stats = relationship("StatementStats", back_populates="snapshot", cascade="all, delete-orphan")
    db_objects = relationship("DbObject", back_populates="snapshot", cascade="all, delete-orphan")
    locks = relationship("Lock", back_populates="snapshot", cascade="all, delete-orphan") 