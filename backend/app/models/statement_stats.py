from sqlalchemy import Column, Integer, ForeignKey, String, Float, BigInteger, Text, Boolean
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class StatementStats(BaseModel):
    __tablename__ = "statement_stats"

    snapshot_id = Column(Integer, ForeignKey("snapshots.id"), nullable=False, index=True)

    # Columns from pg_stat_statements
    userid = Column(BigInteger)  # OID of user who executed the statement
    dbid = Column(BigInteger)  # OID of database in which the statement was executed
    # toplevel = Column(Boolean) # Available in newer PG versions (PG14+)
    queryid = Column(BigInteger, index=True)  # Internal hash code, computed from the statement's parse tree
    query = Column(Text)  # Text of a representative statement

    # Statistics
    calls = Column(BigInteger)  # Number of times executed
    total_time = Column(Float)  # Total time spent in the statement, in milliseconds
    min_time = Column(Float)  # Minimum time spent in the statement, in milliseconds
    max_time = Column(Float)  # Maximum time spent in the statement, in milliseconds
    mean_time = Column(Float)  # Mean time spent in the statement, in milliseconds
    stddev_time = Column(Float)  # Population standard deviation of time spent in the statement, in milliseconds
    rows = Column(BigInteger)  # Total number of rows retrieved or affected by the statement
    shared_blks_hit = Column(BigInteger)  # Total number of shared block cache hits by the statement
    shared_blks_read = Column(BigInteger)  # Total number of shared blocks read by the statement
    shared_blks_dirtied = Column(BigInteger)  # Total number of shared blocks dirtied by the statement
    shared_blks_written = Column(BigInteger)  # Total number of shared blocks written by the statement
    local_blks_hit = Column(BigInteger)  # Total number of local block cache hits by the statement
    local_blks_read = Column(BigInteger)  # Total number of local blocks read by the statement
    local_blks_dirtied = Column(BigInteger)  # Total number of local blocks dirtied by the statement
    local_blks_written = Column(BigInteger)  # Total number of local blocks written by the statement
    temp_blks_read = Column(BigInteger)  # Total number of temp blocks read by the statement
    temp_blks_written = Column(BigInteger)  # Total number of temp blocks written by the statement
    blk_read_time = Column(Float)  # Total time the statement spent reading blocks, in milliseconds
    blk_write_time = Column(Float)  # Total time the statement spent writing blocks, in milliseconds
    # Note: Newer PG versions might have additional fields like plan times, JIT stats, etc.

    # Relationships
    snapshot = relationship("Snapshot", back_populates="statement_stats") 