from fastapi import APIRouter

from src.models.common import StatusResponse
from src.services.auth_service.router.router import router as auth_router
from src.services.role_service.router.router import router as role_router
from src.services.user_service.router.router import router as user_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(user_router, prefix="/users", tags=["User"])
router.include_router(role_router, prefix="/roles", tags=["Role"])


@router.get("/health", response_model=StatusResponse)
async def health_test():
    return StatusResponse
