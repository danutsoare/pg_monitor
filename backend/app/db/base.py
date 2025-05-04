# backend/app/db/base.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

Base = declarative_base()

# Models should inherit from this Base in their respective files.
# Do not import models here; they will be discovered via standard imports
# when the application loads or Alembic runs.

# Import all the models, so that Base knows about them before Alembic runs.
# from app.models.database import MonitoredDatabase # This seems incorrect, models should import Base

# TODO: Uncomment these once the corresponding model files are created in app/models/
# from app.models.snapshot import Snapshot
# from app.models.session_activity import SessionActivity
# from app.models.statement_stats import StatementStats
# from app.models.db_object import DbObject
# from app.models.lock import Lock

# If models are not yet created, comment out the relevant imports above 