from fastapi import APIRouter

from app.deps import CurrentUserDep, DbDep
from app.schemas.base import ErrorResponse
from app.users.schemas import UpdateUserRequest, UserResponse
from app.users.service import update_user

router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get user profile",
    description="Get the profile of the currently authenticated user",
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
async def get_profile(current_user: CurrentUserDep):
    return current_user


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update user profile",
    description="Update the profile of the currently authenticated user",
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
async def update_profile(update_data: UpdateUserRequest, current_user: CurrentUserDep, db: DbDep):
    user = await update_user(db, current_user, **update_data.model_dump(exclude_unset=True))
    return user
