# backend/app/api/v1/endpoints/connections.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import schemas # Assuming schemas package is in app
# from app import crud    # Old import
from app.crud import crud_connection # Import the specific CRUD module
from app.api import deps # Assuming a dependency file for DB session

# Assume crud functions are organized like crud.connection.create_connection
# If crud functions are directly in crud module, adjust imports/calls
# e.g., from app.crud import create_connection, get_connection ...

router = APIRouter()

@router.post("/", response_model=schemas.Connection, status_code=status.HTTP_201_CREATED)
def create_connection_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    connection_in: schemas.ConnectionCreate
):
    """
    Add a new monitored database connection.
    """
    # existing_connection = crud.connection.get_connection_by_alias(db, alias=connection_in.alias)
    existing_connection = crud_connection.get_connection_by_alias(db, alias=connection_in.alias)
    if existing_connection:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Connection with alias '{connection_in.alias}' already exists.",
        )
    # TODO: Add logic to test connection before saving?
    connection = crud_connection.create_connection(db=db, connection=connection_in)
    # Return data conforming to Connection schema (without password)
    return connection

@router.get("/", response_model=List[schemas.Connection])
def read_connections_endpoint(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve a list of all monitored database connections.
    """
    # connections = crud.connection.get_connections(db=db, skip=skip, limit=limit)
    connections = crud_connection.get_connections(db=db, skip=skip, limit=limit)
    # Ensure returned data conforms to Connection schema (without password)
    return connections

@router.get("/{connection_id}", response_model=schemas.Connection)
def read_connection_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    connection_id: int,
):
    """
    Get details of a specific monitored database connection by ID.
    """
    # connection = crud.connection.get_connection(db=db, connection_id=connection_id)
    connection = crud_connection.get_connection(db=db, connection_id=connection_id)
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found.",
        )
    # Ensure returned data conforms to Connection schema (without password)
    return connection

@router.put("/{connection_id}", response_model=schemas.Connection)
def update_connection_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    connection_id: int,
    connection_in: schemas.ConnectionUpdate,
):
    """
    Update an existing monitored database connection.
    """
    # connection = crud.connection.get_connection(db=db, connection_id=connection_id)
    connection = crud_connection.get_connection(db=db, connection_id=connection_id)
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found.",
        )
    # Check if the new alias conflicts with another existing connection
    if connection_in.alias and connection_in.alias != connection.alias:
        # existing_connection = crud.connection.get_connection_by_alias(db, alias=connection_in.alias)
        existing_connection = crud_connection.get_connection_by_alias(db, alias=connection_in.alias)
        if existing_connection and existing_connection.id != connection_id:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Connection with alias '{connection_in.alias}' already exists.",
            )

    # updated_connection = crud.connection.update_connection(
    #     db=db, connection_id=connection_id, connection_update=connection_in
    # )
    updated_connection = crud_connection.update_connection(
        db=db, connection_id=connection_id, connection_update=connection_in
    )
    # Ensure returned data conforms to Connection schema (without password)
    return updated_connection


@router.delete("/{connection_id}", response_model=schemas.Connection)
def delete_connection_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    connection_id: int,
):
    """
    Delete a monitored database connection.
    """
    # connection = crud.connection.get_connection(db=db, connection_id=connection_id)
    connection = crud_connection.get_connection(db=db, connection_id=connection_id)
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found.",
        )
    # deleted_connection = crud.connection.delete_connection(db=db, connection_id=connection_id)
    deleted_connection = crud_connection.delete_connection(db=db, connection_id=connection_id)
    # Return the details of the deleted connection (without password)
    return deleted_connection 