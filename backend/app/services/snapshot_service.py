# backend/app/services/snapshot_service.py
import logging
import asyncpg
from datetime import datetime, timezone # Import datetime
import asyncio # Import asyncio

from app.db.session import SessionLocal # Import SessionLocal
from app.models.snapshot import Snapshot # Import Snapshot model
from app.models.session_activity import SessionActivity # Import SessionActivity model
from app.models.statement_stats import StatementStats # Import StatementStats model
from app.models.lock import Lock # Import Lock model
from app.models.db_object import DbObject # Import DbObject model

logger = logging.getLogger(__name__)

async def take_snapshot(db_conn_details: dict):
    """
    Connects to a monitored PostgreSQL database, gathers monitoring data,
    and stores it in the application's database.
    """
    monitored_db_id = db_conn_details.get('id')
    db_name = db_conn_details.get('db_name', 'unknown')
    host = db_conn_details.get('host')
    port = db_conn_details.get('port')
    user = db_conn_details.get('username')
    password = db_conn_details.get('password') # Assume decrypted password

    if not monitored_db_id:
        logger.error("Missing monitored_database_id in connection details. Skipping snapshot.")
        return

    logger.info(f"Starting snapshot for database ID: {monitored_db_id} ({db_name} at {host}:{port})")

    conn = None
    activity_records = []
    statements_records = []
    lock_records = []
    object_records = []

    try:
        # 1. Establish connection to target database
        logger.info(f"Connecting to target database: {db_name} at {host}:{port} as {user}")
        conn = await asyncpg.connect(
            user=user,
            password=password,
            database=db_name,
            host=host,
            port=port,
            timeout=10 # Add a connection timeout
        )
        logger.info(f"Successfully connected to target database: {db_name}")

        # --- Execute monitoring queries --- 
        # (Error handling added around each query section)

        # Query pg_stat_activity
        try:
            logger.info(f"Fetching pg_stat_activity for {db_name}...")
            activity_query = '''
                SELECT
                    datid, datname, pid, usesysid, usename, application_name,
                    client_addr, client_hostname, client_port, backend_start,
                    xact_start, state, wait_event_type, wait_event, query_start,
                    state_change, backend_xid, backend_xmin,
                    query_id, query, backend_type
                FROM pg_stat_activity
                WHERE datname = $1 AND backend_type = 'client backend'
            '''
            activity_records = await conn.fetch(activity_query, db_name)
            logger.info(f"Fetched {len(activity_records)} activity records from {db_name}.")
        except asyncpg.PostgresError as e:
            logger.error(f"Database error fetching pg_stat_activity for {db_name}: {e}")
        except Exception as e:
            logger.error(f"Error fetching pg_stat_activity for {db_name}: {e}", exc_info=True)


        # Query pg_stat_statements (check if enabled first)
        statements_enabled = False
        try:
            check_ext_query = "SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'"
            statements_enabled = await conn.fetchval(check_ext_query) is not None
            if statements_enabled:
                logger.info(f"Fetching pg_stat_statements for {db_name}...")
                statements_query = '''
                    SELECT
                        userid, dbid, queryid, query, calls, total_exec_time,
                        min_exec_time, max_exec_time, mean_exec_time, stddev_exec_time,
                        rows, shared_blks_hit, shared_blks_read, shared_blks_dirtied,
                        shared_blks_written, local_blks_hit, local_blks_read,
                        local_blks_dirtied, local_blks_written, temp_blks_read,
                        temp_blks_written, blk_read_time, blk_write_time,
                        toplevel, plans, total_plan_time, min_plan_time, max_plan_time,
                        mean_plan_time, stddev_plan_time, wal_records, wal_fpi,
                        wal_bytes, jit_functions, jit_generation_time, jit_inlining_count,
                        jit_inlining_time, jit_optimization_count, jit_optimization_time,
                        jit_emission_count, jit_emission_time
                    FROM pg_stat_statements
                    WHERE dbid = (SELECT oid FROM pg_database WHERE datname = $1)
                '''
                # Note: total_time and total_plan_time might be named differently in older PG
                # Adjust query based on target PG version if needed
                statements_records = await conn.fetch(statements_query, db_name)
                logger.info(f"Fetched {len(statements_records)} statement records from {db_name}.")
            else:
                logger.warning(f"pg_stat_statements extension not found or enabled in database {db_name}. Skipping statement stats.")
        except asyncpg.UndefinedTableError:
             logger.warning(f"pg_stat_statements table not found in database {db_name}. Skipping statement stats.")
        except asyncpg.PostgresError as e:
            logger.error(f"Database error checking/fetching pg_stat_statements for {db_name}: {e}")
        except Exception as e:
            logger.error(f"Error checking/fetching pg_stat_statements for {db_name}: {e}", exc_info=True)

        # Query pg_locks
        try:
            logger.info(f"Fetching pg_locks for {db_name}...")
            locks_query = '''
                SELECT
                    locktype, database, relation, page, tuple, virtualxid,
                    transactionid, classid, objid, objsubid, virtualtransaction,
                    pid, mode, granted, fastpath, waitstart
                FROM pg_locks
                WHERE database = (SELECT oid FROM pg_database WHERE datname = $1)
            '''
            lock_records = await conn.fetch(locks_query, db_name)
            logger.info(f"Fetched {len(lock_records)} lock records from {db_name}.")
        except asyncpg.PostgresError as e:
            logger.error(f"Database error fetching pg_locks for {db_name}: {e}")
        except Exception as e:
            logger.error(f"Error fetching pg_locks for {db_name}: {e}", exc_info=True)

        # Query object sizes
        try:
            logger.info(f"Fetching object sizes for {db_name}...")
            # Simplified query for broad compatibility
            objects_query = '''
                SELECT
                    n.nspname AS schema_name,
                    c.relname AS object_name,
                    CASE c.relkind
                        WHEN 'r' THEN 'table'
                        WHEN 'i' THEN 'index'
                        WHEN 'S' THEN 'sequence'
                        WHEN 'v' THEN 'view'
                        WHEN 'm' THEN 'materialized view'
                        WHEN 'f' THEN 'foreign table'
                        WHEN 'p' THEN 'partitioned table'
                        ELSE 'other'
                    END AS object_type,
                    pg_total_relation_size(c.oid) AS total_size_bytes,
                    pg_relation_size(c.oid) AS table_size_bytes,
                    pg_indexes_size(c.oid) AS index_size_bytes
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
                  AND n.nspname !~ '^pg_toast'
                  AND c.relkind IN ('r', 'p', 'm', 'i') -- Tables, Part. Tables, MViews, Indexes
                ORDER BY total_size_bytes DESC
                LIMIT 5000; -- Limit results to avoid overwhelming data
            '''
            object_records = await conn.fetch(objects_query)
            logger.info(f"Fetched {len(object_records)} object size records from {db_name}.")
        except asyncpg.PostgresError as e:
            logger.error(f"Database error fetching object sizes for {db_name}: {e}")
        except Exception as e:
            logger.error(f"Error fetching object sizes for {db_name}: {e}", exc_info=True)

        # --- Store results in application database --- 
        logger.info("Attempting to store snapshot data in application database...")
        
        snapshot_id = None
        activities_added = 0
        statements_added = 0
        locks_added = 0
        objects_added = 0
        
        # Use synchronous session for app DB access
        with SessionLocal() as app_db:
            try:
                # 3. Create Snapshot record
                new_snapshot = Snapshot(
                    database_id=monitored_db_id,
                    snapshot_time=datetime.now(timezone.utc) # Use timezone-aware datetime
                )
                app_db.add(new_snapshot)
                app_db.flush() # Flush to get the snapshot ID
                snapshot_id = new_snapshot.id
                logger.info(f"Created Snapshot record with ID: {snapshot_id}")

                # 4. Process and store SessionActivity records
                for record in activity_records:
                    # Ensure correct type casting, handle potential None values
                    session_activity = SessionActivity(
                        snapshot_id=snapshot_id,
                        datid=record.get('datid'),
                        datname=record.get('datname'),
                        pid=record.get('pid'),
                        usesysid=record.get('usesysid'),
                        usename=record.get('usename'),
                        application_name=record.get('application_name'),
                        client_addr=str(record.get('client_addr')) if record.get('client_addr') else None,
                        client_hostname=record.get('client_hostname'),
                        client_port=record.get('client_port'),
                        backend_start=record.get('backend_start'),
                        xact_start=record.get('xact_start'),
                        query_start=record.get('query_start'),
                        state_change=record.get('state_change'),
                        wait_event_type=record.get('wait_event_type'),
                        wait_event=record.get('wait_event'),
                        state=record.get('state'),
                        backend_xid=str(record.get('backend_xid')) if record.get('backend_xid') else None,
                        backend_xmin=str(record.get('backend_xmin')) if record.get('backend_xmin') else None,
                        query_id=record.get('query_id'), # May be None
                        query=record.get('query'),
                        backend_type=record.get('backend_type')
                    )
                    app_db.add(session_activity)
                activities_added = len(activity_records)

                # 5. Process and store StatementStats records
                for record in statements_records:
                    statement_stats = StatementStats(
                        snapshot_id=snapshot_id,
                        userid=record.get('userid'),
                        dbid=record.get('dbid'),
                        queryid=record.get('queryid'),
                        query=record.get('query'),
                        calls=record.get('calls'),
                        total_exec_time=record.get('total_exec_time'),
                        min_exec_time=record.get('min_exec_time'),
                        max_exec_time=record.get('max_exec_time'),
                        mean_exec_time=record.get('mean_exec_time'),
                        stddev_exec_time=record.get('stddev_exec_time'),
                        rows=record.get('rows'),
                        shared_blks_hit=record.get('shared_blks_hit'),
                        shared_blks_read=record.get('shared_blks_read'),
                        shared_blks_dirtied=record.get('shared_blks_dirtied'),
                        shared_blks_written=record.get('shared_blks_written'),
                        local_blks_hit=record.get('local_blks_hit'),
                        local_blks_read=record.get('local_blks_read'),
                        local_blks_dirtied=record.get('local_blks_dirtied'),
                        local_blks_written=record.get('local_blks_written'),
                        temp_blks_read=record.get('temp_blks_read'),
                        temp_blks_written=record.get('temp_blks_written'),
                        blk_read_time=record.get('blk_read_time'),
                        blk_write_time=record.get('blk_write_time'),
                        toplevel=record.get('toplevel'),
                        plans=record.get('plans'),
                        total_plan_time=record.get('total_plan_time'),
                        min_plan_time=record.get('min_plan_time'),
                        max_plan_time=record.get('max_plan_time'),
                        mean_plan_time=record.get('mean_plan_time'),
                        stddev_plan_time=record.get('stddev_plan_time'),
                        wal_records=record.get('wal_records'),
                        wal_fpi=record.get('wal_fpi'),
                        wal_bytes=record.get('wal_bytes'),
                        jit_functions=record.get('jit_functions'),
                        jit_generation_time=record.get('jit_generation_time'),
                        jit_inlining_count=record.get('jit_inlining_count'),
                        jit_inlining_time=record.get('jit_inlining_time'),
                        jit_optimization_count=record.get('jit_optimization_count'),
                        jit_optimization_time=record.get('jit_optimization_time'),
                        jit_emission_count=record.get('jit_emission_count'),
                        jit_emission_time=record.get('jit_emission_time'),
                    )
                    app_db.add(statement_stats)
                statements_added = len(statements_records)

                # 6. Process and store Lock records
                for record in lock_records:
                    db_lock = Lock(
                        snapshot_id=snapshot_id,
                        locktype=record.get('locktype'),
                        database=record.get('database'), 
                        relation=record.get('relation'), 
                        page=record.get('page'),
                        tuple=record.get('tuple'),
                        virtualxid=record.get('virtualxid'),
                        transactionid=str(record.get('transactionid')) if record.get('transactionid') else None,
                        classid=record.get('classid'),
                        objid=record.get('objid'),
                        objsubid=record.get('objsubid'),
                        virtualtransaction=record.get('virtualtransaction'),
                        pid=record.get('pid'),
                        mode=record.get('mode'),
                        granted=record.get('granted'),
                        fastpath=record.get('fastpath'),
                        waitstart=record.get('waitstart')
                    )
                    app_db.add(db_lock)
                locks_added = len(lock_records)

                # 7. Process and store DbObject records
                for record in object_records:
                    total_size = record.get('total_size_bytes', 0)
                    table_size = record.get('table_size_bytes', 0)
                    index_size = record.get('index_size_bytes', 0)
                    # Calculate toast size
                    toast_size = total_size - table_size - index_size

                    db_object = DbObject(
                        snapshot_id=snapshot_id,
                        object_type=record.get('object_type'),
                        schema_name=record.get('schema_name'),
                        object_name=record.get('object_name'),
                        total_size_bytes=total_size,
                        table_size_bytes=table_size,
                        index_size_bytes=index_size,
                        toast_size_bytes=max(0, toast_size) # Ensure non-negative
                    )
                    app_db.add(db_object)
                objects_added = len(object_records)

                # Commit the transaction using asyncio.to_thread
                await asyncio.to_thread(app_db.commit)
                logger.info(f"Successfully committed snapshot data for snapshot ID: {snapshot_id}")

            except Exception as db_e:
                logger.error(f"Error interacting with application database for snapshot {snapshot_id}: {db_e}", exc_info=True)
                try:
                    await asyncio.to_thread(app_db.rollback)
                    logger.info(f"Rolled back transaction for snapshot ID: {snapshot_id}")
                except Exception as rb_e:
                    logger.error(f"Failed to rollback transaction for snapshot ID: {snapshot_id}: {rb_e}")
                # We don't re-raise here, log the error and continue to finally block

            # Logging outside the try/except block, only if snapshot_id was obtained
            if snapshot_id:
                 logger.info(f"Stored {activities_added} SessionActivity records for snapshot ID: {snapshot_id}")
                 if statements_added > 0:
                     logger.info(f"Stored {statements_added} StatementStats records for snapshot ID: {snapshot_id}")
                 if locks_added > 0:
                     logger.info(f"Stored {locks_added} Lock records for snapshot ID: {snapshot_id}")
                 if objects_added > 0:
                     logger.info(f"Stored {objects_added} DbObject records for snapshot ID: {snapshot_id}")

            logger.info(f"Successfully finished snapshot processing for database ID: {monitored_db_id}")

    except asyncpg.InterfaceError as conn_e:
        logger.error(f"Connection error during snapshot for DB ID {monitored_db_id} ({db_name}): {conn_e}. Connection might be closed.")
    except asyncpg.PostgresError as e:
        logger.error(f"Database error during snapshot for DB ID {monitored_db_id} ({db_name}): {e}")
    except Exception as e:
        logger.error(f"Unexpected error during snapshot for DB ID {monitored_db_id} ({db_name}): {e}", exc_info=True) # Add traceback
    finally:
        if conn and not conn.is_closed():
            await conn.close()
            logger.info(f"Connection closed for target database: {db_name}") 