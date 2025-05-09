from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator
from app.core.utils import format_bytes_to_pretty_str


# Schema for a single time series data point
class ActivityDataPoint(BaseModel):
    timestamp: datetime
    count: int


# Schema for the activity timeseries response
class ActivityTimeSeries(BaseModel):
    db_id: int
    data: List[ActivityDataPoint]

    class Config:
        from_attributes = True # Allow mapping from ORM objects


# Schema for detailed session activity information
class SessionDetail(BaseModel):
    # Inherit or define fields based on SessionActivity model
    id: int
    snapshot_id: int
    datid: Optional[int] = None
    datname: Optional[str] = None
    pid: Optional[int] = None
    usesysid: Optional[int] = None
    usename: Optional[str] = None
    application_name: Optional[str] = None
    client_addr: Optional[str] = None
    client_hostname: Optional[str] = None
    client_port: Optional[int] = None
    backend_start: Optional[datetime] = None
    xact_start: Optional[datetime] = None
    query_start: Optional[datetime] = None
    state_change: Optional[datetime] = None
    wait_event_type: Optional[str] = None
    wait_event: Optional[str] = None
    state: Optional[str] = None
    backend_xid: Optional[str] = None # Representing xid as string
    backend_xmin: Optional[str] = None # Representing xid as string
    query_id: Optional[int] = None
    query: Optional[str] = None
    backend_type: Optional[str] = None

    class Config:
        from_attributes = True


# Schema for the list of session details response
class SessionDetailList(BaseModel):
    db_id: int
    snapshot_id: int
    snapshot_time: datetime
    sessions: List[SessionDetail]


# Schema for individual statement statistics
class StatementStatDetail(BaseModel):
    # Match fields from StatementStats model
    id: int
    snapshot_id: int
    userid: Optional[int] = None
    dbid: Optional[int] = None
    queryid: Optional[int] = None
    query: Optional[str] = None
    calls: Optional[int] = None
    total_time: Optional[float] = None
    min_time: Optional[float] = None
    max_time: Optional[float] = None
    mean_time: Optional[float] = None
    stddev_time: Optional[float] = None
    rows: Optional[int] = None
    shared_blks_hit: Optional[int] = None
    shared_blks_read: Optional[int] = None
    shared_blks_dirtied: Optional[int] = None
    shared_blks_written: Optional[int] = None
    local_blks_hit: Optional[int] = None
    local_blks_read: Optional[int] = None
    local_blks_dirtied: Optional[int] = None
    local_blks_written: Optional[int] = None
    temp_blks_read: Optional[int] = None
    temp_blks_written: Optional[int] = None
    blk_read_time: Optional[float] = None
    blk_write_time: Optional[float] = None

    class Config:
        from_attributes = True


# Schema for the list of statement stats response
class StatementStatList(BaseModel):
    db_id: int
    snapshot_id: int
    snapshot_time: datetime
    statements: List[StatementStatDetail]


# Schema for individual database object metadata and size
class DbObjectDetail(BaseModel):
    # Match fields from DbObject model
    id: int
    snapshot_id: int
    object_type: str
    schema_name: str
    object_name: str
    total_size_bytes: Optional[int] = None
    table_size_bytes: Optional[int] = None
    index_size_bytes: Optional[int] = None
    toast_size_bytes: Optional[int] = None
    owner: Optional[str] = None
    size_pretty: Optional[str] = Field(None, description="Human-readable size (e.g., '1.2 MiB')")

    @model_validator(mode='before')
    @classmethod
    def calculate_size_pretty(cls, values):
        if isinstance(values, dict):
            total_size_bytes = values.get('total_size_bytes')
            values['size_pretty'] = format_bytes_to_pretty_str(total_size_bytes)
        elif hasattr(values, 'total_size_bytes'):
            setattr(values, 'size_pretty', format_bytes_to_pretty_str(values.total_size_bytes))
        return values

    class Config:
        from_attributes = True


# Schema for the list of database objects response
class DbObjectList(BaseModel):
    db_id: int
    snapshot_id: int
    snapshot_time: datetime
    objects: List[DbObjectDetail]


# Schema for individual lock information
class LockDetail(BaseModel):
    # Based on frontend LockInfo and pg_locks structure
    # Ensure fields match the data returned by the corresponding CRUD function
    id: int # Assuming there's a primary key in the Lock model
    snapshot_id: int

    # Fields corresponding to pg_locks or similar view
    pid: Optional[int] = None
    relation: Optional[int] = None # Changed from relation_name: str to match model's relation: BigInteger (stores OID)
    locktype: Optional[str] = None
    mode: Optional[str] = None
    granted: Optional[bool] = None
    waitstart: Optional[str] = None # Changed from datetime to str to match model
    query: Optional[str] = None         # The blocked or blocking query (NOTE: Field missing in current models.Lock)

    # Add other relevant fields if available, e.g.:
    # relation_oid: Optional[int] = None
    # transactionid: Optional[str] = None # Representing xid as string
    # virtualtransaction: Optional[str] = None
    # virtualxid: Optional[str] = None
    # tuple: Optional[str] = None # Representing tuple identifier
    # page: Optional[int] = None
    # classid: Optional[int] = None
    # objid: Optional[int] = None
    # objsubid: Optional[int] = None
    # database_name: Optional[str] = None # If locks from multiple DBs are stored

    class Config:
        # Enable ORM mode for automatic conversion from SQLAlchemy models (Pydantic v2 uses 'from_attributes')
        from_attributes = True


# Schema for the list of locks response
class LockList(BaseModel):
    db_id: int
    snapshot_id: int
    snapshot_time: datetime
    locks: List[LockDetail]


# --- Detailed Object Information Schemas ---

class ColumnDetail(BaseModel):
    column_name: str
    data_type: str
    collation: Optional[str] = None
    is_nullable: bool # Changed from YES/NO to bool
    column_default: Optional[str] = None
    storage: Optional[str] = None
    compression: Optional[str] = None # For toast-eligible types
    stats_target: Optional[int] = None
    description: Optional[str] = None
    # Raw pg_attribute fields, might be useful for advanced display
    # attrelid: int # OID of the table this column belongs to
    # attnum: int # Number of the column (1-based)
    # atttypid: int # OID of the column's data type
    # attlen: int # Length of the data type
    # atttypmod: int # Type-specific data supplied at table creation time (e.g., max length for varchar)
    # attnotnull: bool
    # atthasdef: bool # Has a default value
    # attoptions: Optional[List[str]] = None # Column-specific options
    # attfdwoptions: Optional[List[str]] = None # Column-specific FDW options


class IndexDetail(BaseModel):
    index_name: str
    index_definition: str # e.g., CREATE INDEX ... or "PRIMARY KEY, btree (col)"
    is_primary_key: bool = False
    is_unique: bool = False
    index_type: str # e.g., btree, hash, gist, gin
    # Might add columns covered by the index if easily obtainable


class ConstraintDetail(BaseModel):
    constraint_name: str
    constraint_type: str # e.g., PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK
    definition: str # For CHECK constraints, the expression; for FK, the referenced table/cols
    # For FKs, might include referenced_table, referenced_columns, on_update, on_delete actions


class ObjectFullDetails(BaseModel):
    schema_name: str
    object_name: str
    object_type: str # table, view, materialized view, index, sequence etc.
    owner: Optional[str] = None
    
    # For Tables/Views/Materialized Views
    columns: Optional[List[ColumnDetail]] = None
    row_count: Optional[int] = None # For tables, materialized views
    
    # For Tables
    indexes: Optional[List[IndexDetail]] = None
    constraints: Optional[List[ConstraintDetail]] = None
    access_method: Optional[str] = None # e.g., heap, heap with OID_column, etc.
    options: Optional[List[str]] = None # e.g., fillfactor=100, autovacuum_enabled=true

    # For Indexes (some info might be redundant if object_type is 'index')
    # index_specific_detail: Optional[IndexDetail] = None # If we want to embed directly for type 'index'
    
    # For Views
    view_definition: Optional[str] = None
    
    # For Sequences
    # sequence_details: Optional[SequenceDetail] = None # TODO: Add if needed

    # General metadata, if available
    description: Optional[str] = None
    # Could add more specific fields as identified by psql \d+ for different object types

    class Config:
        from_attributes = True

# End of new schemas

# Add other monitoring-related schemas here... 