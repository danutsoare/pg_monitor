import uvicorn
from app.core.config import settings
from app.api.api import app # Keep importing the app with routers
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.scheduler import init_scheduler, shutdown_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    init_scheduler()
    yield
    # Shutdown
    print("Shutting down...")
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
    uvicorn.run(
        "main:app", # This will now run the imported app object
        host="0.0.0.0",
        port=8000,
        reload=True,
    )