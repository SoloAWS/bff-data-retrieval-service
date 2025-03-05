from fastapi import APIRouter

# Import routes from the v1 module
from .routes import router as data_retrieval_router

# Create the v1 router
router = APIRouter()

# Include v1 specific routers
router.include_router(data_retrieval_router)