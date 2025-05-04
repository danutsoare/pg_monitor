from fastapi import APIRouter

# Remove FastAPI and middleware imports, as app creation is now in main.py
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# Keep endpoint imports
from app.api.v1.endpoints import connections, monitoring
# Health check might be separate or included here depending on desired structure
from app.api.endpoints import health

# Remove settings import if not directly needed for router config
# from app.core.config import settings

# Remove the FastAPI app instance creation
# app = FastAPI(...)

# Remove CORS middleware addition
# app.add_middleware(...)

# Create the main API router for version 1
api_router = APIRouter()

# Include endpoint routers into the main v1 router
# The prefix here defines the path relative to where api_router is included in main.py
api_router.include_router(connections.router, prefix="/connections", tags=["connections"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])

# Optionally include the health router here too, or keep it separate in main.py
# If included here, adjust prefix in main.py accordingly
# api_router.include_router(health.router, prefix="/health", tags=["health"]) # Example if moved here

# The api_router object is now defined and will be imported by main.py