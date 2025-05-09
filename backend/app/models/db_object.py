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

    owner = Column(String, nullable=True) # Owner of the object (role name)

    # Size information
    total_size_bytes = Column(BigInteger, nullable=True)  # pg_total_relation_size(), nullable
    table_size_bytes = Column(BigInteger, nullable=True)  # pg_table_size(), nullable
    index_size_bytes = Column(BigInteger, nullable=True)  # pg_indexes_size(), nullable
    toast_size_bytes = Column(BigInteger, nullable=True)  # Size of the TOAST table, if any, nullable

    # Relationships
    snapshot = relationship("Snapshot", back_populates="db_objects") 