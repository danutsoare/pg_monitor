# backend/app/db/base.py
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all the models, so that Base knows about them before Alembic runs.
from app.models.database import MonitoredDatabase

# TODO: Uncomment these once the corresponding model files are created in app/models/
# from app.models.snapshot import Snapshot
# from app.models.session_activity import SessionActivity
# from app.models.statement_stats import StatementStats
# from app.models.db_object import DbObject
# from app.models.lock import Lock

# If models are not yet created, comment out the relevant imports above 