from sqlalchemy import Column, Integer, ForeignKey, String, BigInteger
from sqlalchemy.orm import relationship

# Import the common BaseClass
from app.db.base_class import BaseClass


class DbObject(BaseClass):
    __tablename__ = "db_objects"
    # id = Column(Integer, primary_key=True, index=True)

    snapshot_id = Column(Integer, ForeignKey("snapshots.id"), nullable=False, index=True)

    # Object metadata
    object_type = Column(String, nullable=False)  # e.g., 'table', 'index', 'view'
    schema_name = Column(String, nullable=False)
    object_name = Column(String, nullable=False)
    # OID might be useful depending on queries used
    # oid = Column(BigInteger)

    # Size information
    total_size_bytes = Column(BigInteger)  # pg_total_relation_size()
    table_size_bytes = Column(BigInteger)  # pg_table_size()
    index_size_bytes = Column(BigInteger)  # pg_indexes_size()
    toast_size_bytes = Column(BigInteger)  # Size of the TOAST table, if any

    # Relationships
    snapshot = relationship("Snapshot", back_populates="db_objects") 