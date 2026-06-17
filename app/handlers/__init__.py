from aiogram import Router

from app.handlers.admin import admin_router
from app.handlers.offers import router as offers_router
from app.handlers.onboarding import router as onboarding_router
from app.handlers.start import router as start_router


def setup_routers() -> Router:
    root = Router()
    root.include_router(start_router)
    root.include_router(onboarding_router)
    root.include_router(offers_router)
    root.include_router(admin_router)
    return root
