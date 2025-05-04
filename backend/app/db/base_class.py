# backend/app/db/base_class.py
import re
from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declared_attr

# Import the actual Base from db.base
from app.db.base import Base

class BaseClass(Base):
    """
    Common base class for SQLAlchemy models.
    Includes a primary key column.
    Table name should be defined explicitly in subclasses.
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)

    # Add other common columns if needed, e.g.:
    # from sqlalchemy import DateTime
    # from sqlalchemy.sql import func
    # created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    # updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False) 