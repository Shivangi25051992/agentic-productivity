"""API routers live here."""

from .users import router as users_router
from .tasks import router as tasks_router
from .fitness_logs import router as fitness_logs_router
from .auth import router as auth_router
from .fitness import router as fitness_router
from .admin_auth import router as admin_auth_router
from .admin_config import router as admin_config_router
from .profile import router as profile_router

__all__ = [
    "users_router",
    "tasks_router",
    "fitness_logs_router",
    "auth_router",
    "fitness_router",
    "admin_auth_router",
    "admin_config_router",
    "profile_router",
]


