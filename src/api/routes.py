from fastapi import APIRouter

from .routers import v1

# Create a main API router and include the versioned router
api_router = APIRouter()

# Manually include the versioned router
api_router.include_router(v1.router, prefix="/api/v1", tags=["v1"])  # Include v1 routes
