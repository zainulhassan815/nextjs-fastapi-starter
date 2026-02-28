from fastapi import APIRouter

from app.deps import CurrentUserDep, DbDep
from app.detection.schemas import DetectionMethodResponse, ResetMethodsResponse
from app.detection.service import list_methods, reset_all_methods
from app.schemas.base import ErrorResponse

router = APIRouter()


@router.get(
    "/methods",
    response_model=list[DetectionMethodResponse],
    summary="List detection methods",
    description="Get all detection methods with their current decay factors and usage counts",
    responses={401: {"model": ErrorResponse, "description": "Not authenticated"}},
)
async def get_detection_methods(db: DbDep, current_user: CurrentUserDep):
    return await list_methods(db)


@router.post(
    "/methods/reset",
    response_model=ResetMethodsResponse,
    summary="Reset detection methods",
    description="Reset all detection methods to full strength (decay_factor=1.0, usage_count=0)",
    responses={401: {"model": ErrorResponse, "description": "Not authenticated"}},
)
async def reset_detection_methods(db: DbDep, current_user: CurrentUserDep):
    count = await reset_all_methods(db)
    return ResetMethodsResponse(
        reset_count=count,
        message="All detection methods reset to full strength",
    )
