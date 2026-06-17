from aiogram import Router

from app.handlers.admin.panel import router as panel_router

admin_router = Router(name="admin")
admin_router.include_router(panel_router)

__all__ = ["admin_router"]
