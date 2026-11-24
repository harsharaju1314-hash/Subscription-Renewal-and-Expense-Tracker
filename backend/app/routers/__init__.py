from backend.app.routers.auth import router as auth_router, get_current_user, require_role
from backend.app.routers.subscriptions import router as subscriptions_router
from backend.app.routers.categories import router as categories_router
from backend.app.routers.analytics import router as analytics_router
from backend.app.routers.optimization import router as optimization_router
from backend.app.routers.ai import router as ai_router
from backend.app.routers.expenses import router as expenses_router
from backend.app.routers.renewals import router as renewals_router
from backend.app.routers.admin import router as admin_router

__all__ = [
    "auth_router",
    "get_current_user",
    "require_role",
    "subscriptions_router",
    "categories_router",
    "analytics_router",
    "optimization_router",
    "ai_router",
    "expenses_router",
    "renewals_router",
    "admin_router",
]
