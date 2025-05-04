from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, BigInteger
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Lock(BaseModel):
    __tablename__ = "locks"

    snapshot_id = Column(Integer, ForeignKey("snapshots.id"), nullable=False, index=True)

    # Columns from pg_locks
    locktype = Column(String)  # Type of the lockable object
    database = Column(BigInteger)  # OID of the database containing the object
    relation = Column(BigInteger)  # OID of the relation target of the lock
    page = Column(Integer)  # Page number target of the lock within the relation
    tuple = Column(Integer)  # Tuple number target of the lock within the page
    virtualxid = Column(String)  # Virtual transaction ID holding or awaiting the lock
    transactionid = Column(String)  # Transaction ID holding or awaiting the lock (type xid)
    classid = Column(BigInteger)  # OID of the system catalog containing the object
    objid = Column(BigInteger)  # OID of the object within its system catalog
    objsubid = Column(Integer)  # Column number target of the lock
    virtualtransaction = Column(String)  # Virtual ID of the transaction holding or awaiting the lock
    pid = Column(Integer, index=True)  # Process ID of the server process holding or awaiting the lock
    mode = Column(String)  # Name of the lock mode held or desired
    granted = Column(Boolean)  # True if lock is held, false if awaited
    fastpath = Column(Boolean)  # True if lock was taken via fast path
    waitstart = Column(String) # Start time of wait (available in newer PG versions)

    # Relationships
    snapshot = relationship("Snapshot", back_populates="locks") 