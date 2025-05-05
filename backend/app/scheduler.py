# backend/app/scheduler.py
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
import asyncio # Import asyncio
import os # Import os module

from app.core.config import settings
# Import necessary functions/models
from app.db.session import SessionLocal # For accessing app DB
from app.services.snapshot_service import take_snapshot # The job to run
from app.crud.crud_connection import get_connections # To get monitored DBs
# from app.core.security import get_password_hash # Original comment, can be removed
from app.core.security import decrypt # Import decrypt function
# TODO: Implement secure password retrieval instead of passing hashed password
# from app.core.security import decrypt_password # Placeholder

logger = logging.getLogger(__name__)

scheduler = None

def get_scheduler():
    global scheduler
    if scheduler is None:
        raise RuntimeError("Scheduler not initialized")
    return scheduler

def init_scheduler():
    """Initializes and starts the APScheduler."""
    global scheduler
    logger.info("Initializing scheduler...")

    jobstores = {
        'default': SQLAlchemyJobStore(url=settings.SQLALCHEMY_DATABASE_URI)
        # Consider using a separate DB or schema for job store in production
    }
    executors = {
        'default': AsyncIOExecutor()
    }
    job_defaults = {
        'coalesce': True,  # Run missed jobs only once
        'max_instances': 3 # Limit concurrent runs
    }

    scheduler = AsyncIOScheduler(
        jobstores=jobstores,
        executors=executors,
        job_defaults=job_defaults,
        timezone='UTC' # Or configure based on requirements
    )

    # Add the main snapshot job (runs on interval)
    scheduler.add_job(
        trigger_snapshot_runs, # Function to execute
        'interval',
        minutes=settings.SNAPSHOT_INTERVAL_MINUTES, # Use configured interval
        id='trigger_all_snapshots_interval', # Unique ID for the interval job
        replace_existing=True # Replace if job with same ID exists
    )

    scheduler.start()
    logger.info("Scheduler started.")

    # Trigger the first run immediately after startup - REMOVED
    # logger.info("Creating task for initial snapshot trigger.")
    # asyncio.create_task(trigger_snapshot_runs())

def shutdown_scheduler():
    """Shuts down the scheduler gracefully."""
    global scheduler
    if scheduler and scheduler.running:
        logger.info("Shutting down scheduler...")
        scheduler.shutdown()
        logger.info("Scheduler shut down.")
    scheduler = None

async def trigger_snapshot_runs():
    """Fetches all active monitored databases and schedules individual snapshot jobs."""
    logger.info("Triggering snapshot runs...")
    monitored_dbs = []
    try:
        # Use a synchronous session within the async function
        with SessionLocal() as db: # Use synchronous 'with'
            # Run the synchronous get_connections in a separate thread
            monitored_dbs = await asyncio.to_thread(get_connections, db, limit=1000)

        logger.info(f"Found {len(monitored_dbs)} databases to potentially snapshot.")

        active_dbs = [db_conn for db_conn in monitored_dbs if getattr(db_conn, 'is_active', True)]
        logger.info(f"Scheduling snapshots for {len(active_dbs)} active databases.")

        for db_conn in active_dbs:
            # Retrieve encrypted password and decrypt it
            if not hasattr(db_conn, 'encrypted_password') or not db_conn.encrypted_password:
                logger.warning(f"No encrypted password found for database ID {db_conn.id} ({db_conn.alias}). Skipping snapshot.")
                continue

            plain_password = decrypt(db_conn.encrypted_password)

            if not plain_password:
                logger.error(f"Failed to decrypt password for database ID {db_conn.id} ({db_conn.alias}). Check ENCRYPTION_KEY and stored password data. Skipping snapshot.")
                continue # Skip scheduling for this DB if decryption fails
            else:
                logger.debug(f"Successfully decrypted password for database ID {db_conn.id}")

            conn_details = {
                "id": db_conn.id,
                "host": db_conn.hostname, # Model uses hostname
                "port": db_conn.port,
                "db_name": db_conn.db_name,
                "username": db_conn.username,
                "password": plain_password
            }
            # Schedule immediate run for each DB
            job_id = f"snapshot_db_{db_conn.id}"
            logger.debug(f"Adding job {job_id} for db: {db_conn.alias} (ID: {db_conn.id})")
            try:
                # Ensure get_scheduler() returns a running scheduler
                sched = get_scheduler()
                if sched and sched.running: # Check if scheduler exists and is running
                    sched.add_job(
                        take_snapshot, # This should be an async function
                        args=[conn_details],
                        id=job_id,
                        jobstore="default", # Consider memory store if jobs are transient
                        executor="default",
                        replace_existing=True, # Replace if previous run for this DB is stuck
                        misfire_grace_time=60 # Allow 60 seconds grace period
                    )
                else:
                    logger.warning(f"Scheduler not running or not initialized, cannot add job {job_id}")
            except Exception as job_e:
                logger.error(f"Failed to add snapshot job {job_id} for db {db_conn.id}: {job_e}")

    except Exception as e:
        logger.error(f"Error in trigger_snapshot_runs: {e}", exc_info=True)

    logger.info("Finished triggering snapshot runs.") 