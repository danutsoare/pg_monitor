from pydantic import BaseModel, Field, SecretStr, validator
from typing import Optional

class ConnectionBase(BaseModel):
    """Base schema for connection details."""
    alias: str = Field(..., example="My Production DB", min_length=1, max_length=100)
    hostname: str = Field(..., example="localhost", max_length=255)
    port: int = Field(default=5432, example=5432, ge=1, le=65535)
    username: str = Field(..., example="postgres", max_length=100)
    db_name: str = Field(..., example="mydatabase", max_length=100)

    @validator('alias', 'hostname', 'username', 'db_name')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v

class ConnectionCreate(ConnectionBase):
    """Schema for creating a new connection. Includes the password."""
    # TODO: Implement proper password hashing/encryption before storing
    password: SecretStr = Field(..., example="supersecret")

class ConnectionUpdate(BaseModel):
    """Schema for updating a connection. All fields are optional."""
    alias: Optional[str] = Field(None, example="My Prod DB Renamed", min_length=1, max_length=100)
    hostname: Optional[str] = Field(None, example="prod.db.example.com", max_length=255)
    port: Optional[int] = Field(None, example=5433, ge=1, le=65535)
    username: Optional[str] = Field(None, example="admin_user", max_length=100)
    db_name: Optional[str] = Field(None, example="production_db", max_length=100)
    # Allow updating the password
    password: Optional[SecretStr] = Field(None, example="newsecretpassword")

    @validator('alias', 'hostname', 'username', 'db_name', pre=True, always=True)
    def not_empty_optional(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Field cannot be empty if provided')
        return v

class ConnectionInDBBase(ConnectionBase):
    """Base schema for connections stored in the database."""
    id: int

    class Config:
        orm_mode = True # Compatibility with SQLAlchemy models

class Connection(ConnectionInDBBase):
    """Schema for returning connection details via the API. Excludes password."""
    pass # Inherits all fields from ConnectionInDBBase, no password

# This schema might not be strictly necessary if the DB model includes password
# and orm_mode handles it, but explicitly defining it can be clearer.
# class ConnectionInDB(ConnectionInDBBase):
#     """Schema representing a full connection object potentially including sensitive info (like hashed password)
#        if needed for internal use, but generally avoid exposing this.
#     """
#     # Example: if storing hashed password in DB model
#     # hashed_password: str
#     # Or if storing the raw password (temporarily, for development)
#     password: SecretStr # Matches the temporary storage in crud 