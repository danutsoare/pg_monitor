from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Import the common BaseClass
from app.db.base_class import BaseClass

class Snapshot(BaseClass):
    __tablename__ = "snapshots"
    # id = Column(Integer, primary_key=True, index=True)

    database_id = Column(Integer, ForeignKey("monitored_databases.id"), nullable=False) # Use correct table name
    snapshot_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    database = relationship("Connection", back_populates="snapshots")
    session_activities = relationship("SessionActivity", back_populates="snapshot", cascade="all, delete-orphan")
    statement_stats = relationship("StatementStats", back_populates="snapshot", cascade="all, delete-orphan")
    db_objects = relationship("DbObject", back_populates="snapshot", cascade="all, delete-orphan")
    locks = relationship("Lock", back_populates="snapshot", cascade="all, delete-orphan") 