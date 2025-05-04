import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Ensure the app directory is in the Python path
# APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# sys.path.insert(0, APP_DIR)
# Instead, add the parent directory of 'app' to the path if needed,
# assuming the script is run with /app as the working directory.
# Or rely on PYTHONPATH if set correctly in the environment.
sys.path.insert(0, '.') # Add current working directory explicitly

# Import Base and models
from app.db.session import Base  # Assuming Base is defined here
# Try importing the package first to ensure it's found
import app.models
from app.models.monitored_database import MonitoredDatabase
from app.models.snapshot import Snapshot
from app.models.session_activity import SessionActivity
from app.models.statement_stats import StatementStats
from app.models.db_object import DbObject
from app.models.lock import Lock
from app.core.config import settings # Assuming settings object with SQLALCHEMY_DATABASE_URI property

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata # Use our Base metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

SQLALCHEMY_DATABASE_URI = str(settings.SQLALCHEMY_DATABASE_URI) # Use the property
if not SQLALCHEMY_DATABASE_URI:
    raise ValueError("Could not construct SQLALCHEMY_DATABASE_URI from settings")

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # url = config.get_main_option("sqlalchemy.url")
    url = SQLALCHEMY_DATABASE_URI # Use URL from settings
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Use SQLALCHEMY_DATABASE_URI from settings for the connection
    configuration = config.get_section(config.config_ini_section, {})
    # configuration['sqlalchemy.url'] = DATABASE_URL
    configuration['sqlalchemy.url'] = SQLALCHEMY_DATABASE_URI

    connectable = engine_from_config(
        # config.get_section(config.config_ini_section, {}),
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
