# backend/app/crud/crud_connection.py

from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app import schemas
from app.models import Connection # Correct import path and model name
from app.core.security import get_password_hash # Use hashing, not encryption
from app.schemas.connection import ConnectionCreate, ConnectionUpdate
from pydantic import SecretStr
from typing import List, Optional

# TODO: Add password hashing/decryption logic here

def get_connection(db: Session, connection_id: int) -> Connection | None:
    """Retrieves a single connection by its ID."""
    return db.query(Connection).filter(Connection.id == connection_id).first()

def get_connections(db: Session, skip: int = 0, limit: int = 100) -> List[Connection]:
    """Retrieves a list of connections with pagination."""
    return db.query(Connection).offset(skip).limit(limit).all()

def get_connection_by_alias(db: Session, alias: str) -> Optional[Connection]:
    """Retrieves a connection by its alias."""
    return db.query(Connection).filter(Connection.alias == alias).first()

def create_connection(db: Session, connection: ConnectionCreate) -> Connection:
    """Creates a new connection entry in the database with a hashed password."""
    hashed_password = get_password_hash(connection.password.get_secret_value())
    db_connection = Connection(
        alias=connection.alias,
        hostname=connection.hostname,
        port=connection.port,
        username=connection.username,
        db_name=connection.db_name,
        # Store the hashed password
        db_password_encrypted=hashed_password
    )
    db.add(db_connection)
    db.commit()
    db.refresh(db_connection)
    # The object returned will be mapped by SQLAlchemy. Pydantic's orm_mode handles conversion.
    return db_connection

def update_connection(db: Session, connection_id: int, connection_update: ConnectionUpdate) -> Optional[Connection]:
    """Updates an existing connection, hashing the password if provided."""
    db_connection = get_connection(db, connection_id)
    if not db_connection:
        return None

    update_data = connection_update.dict(exclude_unset=True)

    # Handle password update specifically
    if "password" in update_data and update_data["password"] is not None:
        hashed_password = get_password_hash(update_data["password"].get_secret_value())
        # Update the password hash field in the model
        db_connection.db_password_encrypted = hashed_password
        # Remove password from update_data dict to avoid errors during iteration below
        del update_data["password"]
    elif "password" in update_data:
        # If password is None in the update schema, remove it from dict
        # so it doesn't try to set the DB field to None accidentally.
         del update_data["password"]


    for key, value in update_data.items():
        setattr(db_connection, key, value)

    db.commit()
    db.refresh(db_connection)
    return db_connection

def delete_connection(db: Session, connection_id: int) -> Optional[Connection]:
    """Deletes a connection from the database."""
    db_connection = get_connection(db, connection_id)
    if db_connection:
        db.delete(db_connection)
        db.commit()
    # Return the deleted object (or None if not found) to allow the API to respond
    return db_connection 