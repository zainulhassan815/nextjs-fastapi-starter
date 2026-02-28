from fastapi import APIRouter

from app.routes.auth import router as auth_router
from app.routes.budget import router as budget_router
from app.routes.detection import router as detection_router
from app.routes.moderation import router as moderation_router
from app.routes.posts import router as posts_router
from app.routes.reviews import router as reviews_router
from app.routes.users import router as users_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(posts_router, prefix="/posts", tags=["posts"])
api_router.include_router(moderation_router, prefix="/moderation", tags=["moderation"])
api_router.include_router(reviews_router, prefix="/reviews", tags=["reviews"])
api_router.include_router(detection_router, prefix="/detection", tags=["detection"])
api_router.include_router(budget_router, prefix="/budget", tags=["budget"])
