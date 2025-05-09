from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Any, Optional
from datetime import datetime

from app.api import deps
from app import schemas
from app import crud
from app.services import object_details_service
import asyncpg
from app.core.security import decrypt

router = APIRouter()


@router.get("/")
async def read_monitoring_root():
    """
    Placeholder endpoint for monitoring root.
    """
    return {"message": "Monitoring endpoints root"}


@router.get("/activity/timeseries/{db_id}", response_model=schemas.ActivityTimeSeries)
async def get_activity_timeseries(
    *,
    db: Session = Depends(deps.get_db),
    db_id: int,
    start_time: Optional[datetime] = Query(None, description="Start time for the data range (ISO 8601 format)"),
    end_time: Optional[datetime] = Query(None, description="End time for the data range (ISO 8601 format)")
) -> Any:
    """
    Get time series activity data for a specific database within a specified time range.
    If start_time or end_time are omitted, backend defaults might apply (e.g., last hour).
    """
    # Validate or default time range if necessary
    # Fetch data using CRUD function
    activity_data = crud.monitoring.get_activity_timeseries_data(
        db=db, db_id=db_id, start_time=start_time, end_time=end_time
    )

    if not activity_data:
         # Return empty list if no data, maybe log this?
         return schemas.ActivityTimeSeries(db_id=db_id, data=[]) # Return structure with empty data

    # Assuming crud function returns data in the correct format for the schema
    return schemas.ActivityTimeSeries(db_id=db_id, data=activity_data)


@router.get("/sessions/{db_id}/latest", response_model=schemas.SessionDetailList)
async def get_latest_session_details(
    *,
    db: Session = Depends(deps.get_db),
    db_id: int,
) -> Any:
    """
    Get detailed session information from the latest snapshot for a specific database.
    """
    latest_snapshot = crud.monitoring.get_latest_snapshot(db=db, db_id=db_id)

    if not latest_snapshot:
        raise HTTPException(
            status_code=404,
            detail=f"No snapshot found for database ID {db_id}"
        )

    session_details = crud.monitoring.get_session_details_by_snapshot(
        db=db,
        snapshot_id=latest_snapshot.id
    )

    return schemas.SessionDetailList(
        db_id=db_id,
        snapshot_id=latest_snapshot.id,
        snapshot_time=latest_snapshot.snapshot_time,
        sessions=session_details
    )


@router.get("/statements/{db_id}/latest", response_model=schemas.StatementStatList)
async def get_latest_statement_stats(
    *,
    db: Session = Depends(deps.get_db),
    db_id: int,
    sort_by: crud.monitoring.StatementSortBy = Query(
        crud.monitoring.StatementSortBy.total_time,
        description="Field to sort statements by"
    ),
    limit: Optional[int] = Query(20, description="Maximum number of statements to return", ge=1, le=100)
) -> Any:
    """
    Get statement statistics from the latest snapshot for a specific database,
    with options for sorting and limiting results.
    """
    latest_snapshot = crud.monitoring.get_latest_snapshot(db=db, db_id=db_id)

    if not latest_snapshot:
        raise HTTPException(
            status_code=404,
            detail=f"No snapshot found for database ID {db_id}"
        )

    statement_stats = crud.monitoring.get_statement_stats_by_snapshot(
        db=db,
        snapshot_id=latest_snapshot.id,
        sort_by=sort_by,
        limit=limit
    )

    return schemas.StatementStatList(
        db_id=db_id,
        snapshot_id=latest_snapshot.id,
        snapshot_time=latest_snapshot.snapshot_time,
        statements=statement_stats
    )


@router.get("/objects/{db_id}/latest", response_model=schemas.DbObjectList)
async def get_latest_db_objects(
    *,
    db: Session = Depends(deps.get_db),
    db_id: int,
    sort_by_size: bool = Query(True, description="Sort results by total size descending"),
    limit: Optional[int] = Query(100, description="Maximum number of objects to return", ge=1, le=1000)
) -> Any:
    """
    Get database object metadata and size from the latest snapshot for a specific database.
    Allows sorting by size and limiting results.
    """
    latest_snapshot = crud.monitoring.get_latest_snapshot(db=db, db_id=db_id)

    if not latest_snapshot:
        raise HTTPException(
            status_code=404,
            detail=f"No snapshot found for database ID {db_id}"
        )

    db_objects = crud.monitoring.get_db_objects_by_snapshot(
        db=db,
        snapshot_id=latest_snapshot.id,
        sort_by_size=sort_by_size,
        limit=limit
    )

    return schemas.DbObjectList(
        db_id=db_id,
        snapshot_id=latest_snapshot.id,
        snapshot_time=latest_snapshot.snapshot_time,
        objects=db_objects
    )


@router.get("/locks/{db_id}/latest", response_model=schemas.LockList)
async def get_latest_locks(
    *,
    db: Session = Depends(deps.get_db),
    db_id: int,
    # Add Query parameters for filtering/sorting if needed later
    # e.g., granted_only: bool = Query(False, description="Only show granted locks"),
    # e.g., sort_by: Optional[str] = Query(None, description="Field to sort locks by")
) -> Any:
    """
    Get lock information from the latest snapshot for a specific database.
    """
    latest_snapshot = crud.monitoring.get_latest_snapshot(db=db, db_id=db_id)

    if not latest_snapshot:
        raise HTTPException(
            status_code=404,
            detail=f"No snapshot found for database ID {db_id}"
        )

    # Placeholder for the actual CRUD function call
    # This function needs to be implemented in crud/crud_monitoring.py
    lock_details = crud.monitoring.get_locks_by_snapshot(
        db=db,
        snapshot_id=latest_snapshot.id,
        # Pass any filter/sort parameters here
    )

    # This schema (LockList and LockDetail) needs to be defined in schemas/monitoring.py
    return schemas.LockList(
        db_id=db_id,
        snapshot_id=latest_snapshot.id,
        snapshot_time=latest_snapshot.snapshot_time,
        locks=lock_details # Assuming crud function returns a list compatible with LockDetail
    )

@router.get("/objects/{db_id}/{schema_name}/{object_name}/details", response_model=Optional[schemas.monitoring.ObjectFullDetails])
async def get_object_full_details_endpoint(
    *,
    app_db: Session = Depends(deps.get_db),
    db_id: int,
    schema_name: str,
    object_name: str,
    object_type: str, # Type of the object (table, view, index, etc.)
    owner: Optional[str] = None # Owner might be passed from the client if already known
) -> Any:
    """
    Get comprehensive details for a specific database object (table, view, index, etc.).
    """
    db_conn_details_model = crud.connection.get_connection(db=app_db, connection_id=db_id)
    if not db_conn_details_model:
        raise HTTPException(status_code=404, detail=f"Monitored database with ID {db_id} not found.")

    # Convert SQLAlchemy model to dict for asyncpg
    db_conn_params = {
        "host": db_conn_details_model.hostname,
        "port": db_conn_details_model.port,
        "user": db_conn_details_model.username,
        "password": decrypt(db_conn_details_model.encrypted_password),
        "database": db_conn_details_model.db_name,
        "timeout": 10 # Connection timeout
    }

    conn = None
    try:
        conn = await asyncpg.connect(**db_conn_params)
        details = await object_details_service.get_object_full_details(
            conn=conn, 
            schema_name=schema_name, 
            object_name=object_name, 
            object_type=object_type,
            owner=owner # Pass owner if provided by client (e.g. from the existing table row)
        )
        if not details:
            # This case might mean the object wasn't found by the service function, 
            # or an error occurred during detail fetching that was logged but returned None.
            raise HTTPException(status_code=404, detail=f"{object_type.capitalize()} '{schema_name}.{object_name}' not found or details could not be fetched.")
        return details
    except asyncpg.PostgresError as e:
        # Handle specific database connection or query errors
        raise HTTPException(status_code=503, detail=f"Database error when connecting to or querying monitored DB: {e}")
    except Exception as e:
        # Handle other unexpected errors
        # Log the error for debugging: logger.error(f"Error fetching object details: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    finally:
        if conn:
            await conn.close()

# New endpoint for fetching row count specifically
@router.get("/objects/{db_id}/{schema_name}/{object_name}/rowcount", response_model=Optional[schemas.monitoring.ObjectRowCount]) # Define ObjectRowCount in schemas
async def get_object_row_count_endpoint(
    *,
    app_db: Session = Depends(deps.get_db),
    db_id: int,
    schema_name: str,
    object_name: str,
    # No object_type needed as this is specifically for tables/views that support row counts
) -> Any:
    """
    Get the row count for a specific database object (table, materialized view).
    """
    db_conn_details_model = crud.connection.get_connection(db=app_db, connection_id=db_id)
    if not db_conn_details_model:
        raise HTTPException(status_code=404, detail=f"Monitored database with ID {db_id} not found.")

    db_conn_params = {
        "host": db_conn_details_model.hostname,
        "port": db_conn_details_model.port,
        "user": db_conn_details_model.username,
        "password": decrypt(db_conn_details_model.encrypted_password),
        "database": db_conn_details_model.db_name,
        "timeout": 10
    }

    conn = None
    try:
        conn = await asyncpg.connect(**db_conn_params)
        # Assuming object_details_service.get_row_count handles tables/views correctly
        row_count = await object_details_service.get_row_count(
            conn=conn, 
            schema_name=schema_name, 
            table_name=object_name # Parameter name in get_row_count is table_name
        )
        # The schema ObjectRowCount will simply be { "row_count": Optional[int] }
        return schemas.monitoring.ObjectRowCount(row_count=row_count)
    except asyncpg.PostgresError as e:
        # Log specific pg error: logger.error(f"DB error fetching row count for {schema_name}.{object_name}: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail=f"Database error when fetching row count: {e}")
    except Exception as e:
        # Log general error: logger.error(f"Error fetching row count for {schema_name}.{object_name}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while fetching row count: {e}")
    finally:
        if conn:
            await conn.close()

# Add other monitoring-related endpoints here as needed... 