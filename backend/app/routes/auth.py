from fastapi import APIRouter, HTTPException, status

from app.auth.schemas import CreateUserRequest, LoginRequest, TokenResponse
from app.auth.service import authenticate_user, create_user
from app.auth.utils import create_access_token
from app.deps import CurrentUserDep, DbDep
from app.schemas.base import ErrorResponse
from app.users.schemas import UserResponse
from app.users.service import get_user_by_email

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password",
    responses={
        409: {"model": ErrorResponse, "description": "Email already registered"},
    },
)
async def register(user_data: CreateUserRequest, db: DbDep):
    existing = await get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "ALREADY_EXISTS", "message": "Email already registered"},
        )
    user = await create_user(db, email=user_data.email, password=user_data.password, full_name=user_data.full_name)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate user",
    description="Login with email and password to receive a JWT token",
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
    },
)
async def login(user_data: LoginRequest, db: DbDep):
    user = await authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "Invalid email or password"},
        )
    token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return TokenResponse(access_token=token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get the profile of the currently authenticated user",
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
async def get_me(current_user: CurrentUserDep):
    return current_user
