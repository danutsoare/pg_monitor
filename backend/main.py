import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
import asyncpg # Added for version logging

from app.core.config import settings # Keep settings import if needed
from app.scheduler import init_scheduler, shutdown_scheduler
from app.api.api import api_router # Import the main API router

# Early logging setup or basic config if needed before full app setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"asyncpg version: {asyncpg.__version__}") # Added logging for asyncpg version

# --- Logging Configuration ---
log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO) # Set root logger level

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)
# ---------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up application...")
    init_scheduler()
    yield
    # Shutdown
    logger.info("Shutting down application...")
    shutdown_scheduler()

# Create the FastAPI app instance here with the lifespan manager
app = FastAPI(
    title=settings.PROJECT_NAME, # Add title from settings if available
    openapi_url=f"{settings.API_V1_STR}/openapi.json", # Add openapi url from settings
    lifespan=lifespan
)

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

# Include the main API router
app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    logger.info("Starting Uvicorn server...")
    uvicorn.run(
        "main:app", # Uvicorn targets the 'app' instance defined in this file
        host="0.0.0.0",
        port=8000,
        reload=settings.RELOAD_MODE # Use setting for reload if available
        # reload=True, # Or keep True if setting doesn't exist
    )