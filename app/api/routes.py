from fastapi import APIRouter

from .endpoints import *

api_router = APIRouter(prefix="/api/v1")

# Include all endpoint routers
