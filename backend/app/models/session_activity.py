from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Text, BigInteger
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class SessionActivity(BaseModel):
    __tablename__ = "session_activity"

    snapshot_id = Column(Integer, ForeignKey("snapshots.id"), nullable=False, index=True)

    # Columns from pg_stat_activity
    datid = Column(BigInteger)
    datname = Column(String)
    pid = Column(Integer, index=True)
    usesysid = Column(BigInteger)
    usename = Column(String)
    application_name = Column(String)
    client_addr = Column(String)  # Could be INET type if DB supports it
    client_hostname = Column(String)
    client_port = Column(Integer)
    backend_start = Column(DateTime(timezone=True))
    xact_start = Column(DateTime(timezone=True))
    query_start = Column(DateTime(timezone=True))
    state_change = Column(DateTime(timezone=True))
    wait_event_type = Column(String)
    wait_event = Column(String)
    state = Column(String)
    backend_xid = Column(String) # Type 'xid' might require custom handling or cast
    backend_xmin = Column(String) # Type 'xid' might require custom handling or cast
    query_id = Column(BigInteger) # pg_stat_activity in newer PG versions
    query = Column(Text)
    backend_type = Column(String)

    # Relationships
    snapshot = relationship("Snapshot", back_populates="session_activities") 