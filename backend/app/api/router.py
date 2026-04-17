from fastapi import APIRouter
from fastapi import Depends

from app.api.v1.auth import router as auth_router
from app.api.v1.chat import router as chat_router
from app.api.v1.files import router as files_router
from app.api.v1.health import router as health_router
from app.api.v1.timestamps import router as timestamps_router
from app.services.auth import get_current_user

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(files_router, dependencies=[Depends(get_current_user)])
api_router.include_router(chat_router, dependencies=[Depends(get_current_user)])
api_router.include_router(timestamps_router, dependencies=[Depends(get_current_user)])
