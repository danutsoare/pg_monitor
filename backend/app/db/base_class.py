# backend/app/db/base_class.py
import re
from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declared_attr

# Import the actual Base from db.base
from app.db.base import Base

class BaseClass(Base):
    """
    Common base class for SQLAlchemy models.
    Includes an auto-generated table name and a primary key column.
    """
    __abstract__ = True

    # Automatically generate __tablename__
    @declared_attr
    def __tablename__(cls):
        # Converts CamelCase class name to snake_case_plural table name
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()
        # Ensure pluralization (simple 's' suffix, might need refinement for irregular plurals)
        if not name.endswith('s'):
            name += 's'
        elif name.endswith('ss'): # Avoid things like address -> addressses
             pass # Keep as is if ends in 'ss'
        elif name.endswith('ys') and len(name) > 2 and name[-3] not in 'aeiou': # e.g. activity -> activities
            name = name[:-2] + 'ies'
        # Add more specific pluralization rules if needed

        return name

    id = Column(Integer, primary_key=True, index=True)

    # Add other common columns if needed, e.g.:
    # from sqlalchemy import DateTime
    # from sqlalchemy.sql import func
    # created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    # updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False) 