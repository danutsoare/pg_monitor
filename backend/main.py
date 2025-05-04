import uvicorn
from app.core.config import settings
from app.api.api import app # Keep importing the app with routers
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware # Add CORS import
import logging # Add logging import
import sys # Add sys import

from app.scheduler import init_scheduler, shutdown_scheduler

# --- Logging Configuration ---
log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO) # Set root logger level

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)

# You might want to add a FileHandler here for production
# file_handler = logging.FileHandler("app.log")
# file_handler.setFormatter(log_formatter)
# logger.addHandler(file_handler)
# ---------------------------

# TODO: Restrict origins in production
origins = [
    "*", # Allow all origins for development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods
    allow_headers=["*"], # Allow all headers
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up application...") # Use logger
    init_scheduler()
    yield
    # Shutdown
    logger.info("Shutting down application...") # Use logger
    shutdown_scheduler()

# app = FastAPI(lifespan=lifespan) # REMOVE THIS LINE - it overwrites the imported app

# Assign the lifespan context manager to the imported app's router
app.router.lifespan_context = lifespan

# Remove the root endpoint defined here, as it's likely handled within api.py or redundant
# @app.get("/")
# async def read_root():
#     return {"Hello": "World"}

# Comments below are now potentially inaccurate but harmless
# Include routers later
# from app.api.v1.api import api_router
# app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    logger.info("Starting Uvicorn server...") # Use logger
    uvicorn.run(
        "main:app", # This will now run the imported app object
        host="0.0.0.0",
        port=8000,
        reload=True,
    )