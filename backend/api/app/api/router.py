from fastapi import APIRouter

from app.api.routes import (
    admin,
    alerts,
    assistant,
    aqi,
    auth,
    forecasts,
    locations,
    notifications,
    planner,
    profiles,
    recommendations,
    users,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(profiles.router)
api_router.include_router(locations.router)
api_router.include_router(alerts.router)
api_router.include_router(notifications.router)
api_router.include_router(aqi.router)
api_router.include_router(forecasts.router)
api_router.include_router(planner.router)
api_router.include_router(recommendations.router)
api_router.include_router(assistant.router)
api_router.include_router(admin.router)
