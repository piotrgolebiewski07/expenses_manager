from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.categories import router as categories_router
from app.api.expenses import router as expenses_router

api_router = APIRouter()

api_router.include_router(expenses_router)
api_router.include_router(auth_router)
api_router.include_router(categories_router)

