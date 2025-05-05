from sqlalchemy.orm import Session
from sqlalchemy import func, select, desc
from datetime import datetime, timedelta
from typing import Optional, List
from enum import Enum

from app import models, schemas

def get_activity_timeseries_data(
    db: Session,
    db_id: int,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    # TODO: Add interval/bucketing logic if needed
) -> List[schemas.ActivityDataPoint]:
    """Fetches activity count grouped by snapshot time for a given database.

    Args:
        db: Database session.
        db_id: ID of the monitored database.
        start_time: Optional start time filter.
        end_time: Optional end time filter.

    Returns:
        List of ActivityDataPoint schemas.
    """
    if end_time is None:
        end_time = datetime.utcnow()
    if start_time is None:
        # Default to the last 1 hour if no start_time provided
        start_time = end_time - timedelta(hours=1)

    # Query to count session activities per snapshot within the time range
    stmt = (
        select(
            models.Snapshot.snapshot_time,
            func.count(models.SessionActivity.id).label("count"),
        )
        .join(models.SessionActivity, models.Snapshot.id == models.SessionActivity.snapshot_id)
        .where(models.Snapshot.database_id == db_id)
        .where(models.Snapshot.snapshot_time >= start_time)
        .where(models.Snapshot.snapshot_time <= end_time)
        .group_by(models.Snapshot.snapshot_time)
        .order_by(models.Snapshot.snapshot_time)
    )

    results = db.execute(stmt).all()

    # Convert results to Pydantic schema
    data_points = [
        schemas.ActivityDataPoint(timestamp=row.snapshot_time, count=row.count)
        for row in results
    ]

    return data_points


def get_latest_snapshot(db: Session, db_id: int) -> Optional[models.Snapshot]:
    """Fetches the most recent snapshot for a given database ID."""
    return (
        db.query(models.Snapshot)
        .filter(models.Snapshot.database_id == db_id)
        .order_by(models.Snapshot.snapshot_time.desc())
        .first()
    )

def get_session_details_by_snapshot(
    db: Session,
    snapshot_id: int
) -> List[models.SessionActivity]:
    """Fetches all session activity records for a specific snapshot ID."""
    return (
        db.query(models.SessionActivity)
        .filter(models.SessionActivity.snapshot_id == snapshot_id)
        .all()
    )

# Enum for sorting statement statistics
class StatementSortBy(str, Enum):
    calls = "calls"
    total_time = "total_time"
    mean_time = "mean_time"
    rows = "rows"
    shared_blks_read = "shared_blks_read"
    shared_blks_hit = "shared_blks_hit"

def get_statement_stats_by_snapshot(
    db: Session,
    snapshot_id: int,
    sort_by: StatementSortBy = StatementSortBy.total_time,
    limit: Optional[int] = 20 # Default limit
) -> List[models.StatementStats]:
    """Fetches statement statistics for a specific snapshot ID, with sorting and limit.

    Args:
        db: Database session.
        snapshot_id: ID of the snapshot.
        sort_by: Field to sort the results by.
        limit: Maximum number of results to return.

    Returns:
        List of StatementStats models.
    """
    sort_column = getattr(models.StatementStats, sort_by.value, models.StatementStats.total_time)

    query = (
        db.query(models.StatementStats)
        .filter(models.StatementStats.snapshot_id == snapshot_id)
        .order_by(desc(sort_column))
    )

    if limit is not None:
        query = query.limit(limit)

    return query.all()

def get_db_objects_by_snapshot(
    db: Session,
    snapshot_id: int,
    sort_by_size: bool = True, # Default to sorting by size descending
    limit: Optional[int] = 100 # Default limit
) -> List[models.DbObject]:
    """Fetches database objects for a specific snapshot ID, optionally sorted by size.

    Args:
        db: Database session.
        snapshot_id: ID of the snapshot.
        sort_by_size: If True, sort by total_size_bytes descending.
        limit: Maximum number of results to return.

    Returns:
        List of DbObject models.
    """
    query = (
        db.query(models.DbObject)
        .filter(models.DbObject.snapshot_id == snapshot_id)
    )

    if sort_by_size:
        # Ensure nulls are treated consistently if size can be null
        # Apply desc() first, then nullslast()
        query = query.order_by(desc(models.DbObject.total_size_bytes).nullslast())
    else:
        # Default sort order if not sorting by size
        query = query.order_by(models.DbObject.schema_name, models.DbObject.object_name)

    if limit is not None:
        query = query.limit(limit)

    return query.all()

def get_locks_by_snapshot(db: Session, snapshot_id: int) -> List[models.Lock]:
    """Fetches all lock records for a specific snapshot ID."""
    return (
        db.query(models.Lock)
        .filter(models.Lock.snapshot_id == snapshot_id)
        .order_by(models.Lock.pid, models.Lock.granted.desc()) # Example sort order
        .all()
    )

# You might combine the above or use them separately in the endpoint 