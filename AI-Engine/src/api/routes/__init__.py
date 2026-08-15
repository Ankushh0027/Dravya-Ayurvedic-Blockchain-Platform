from src.api.routes.health import router as health_router
from src.api.routes.prediction import router as prediction_router
from src.api.routes.batch import router as batch_router, inventory_router
from src.api.routes.chat import router as chat_router

__all__ = [
    "health_router",
    "prediction_router",
    "batch_router",
    "inventory_router",
    "chat_router",
]
