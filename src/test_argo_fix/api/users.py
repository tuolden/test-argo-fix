"""User management endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from ..core.logging import get_logger
from ..models.user import User as UserModel
from ..services.user_service import UserService
from .deps import get_current_active_user, get_current_superuser, get_user_service
from .schemas import Message, User, UserCreate, UserUpdate

router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_create: UserCreate,
    user_service: UserService = Depends(get_user_service),
    current_user: UserModel = Depends(get_current_superuser),
) -> User:
    """Create new user (superuser only)."""
    try:
        user = await user_service.create_user(
            email=user_create.email,
            username=user_create.username,
            password=user_create.password,
            full_name=user_create.full_name,
        )
        return User.model_validate(user)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists",
        )


@router.get("/", response_model=List[User])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    user_service: UserService = Depends(get_user_service),
    current_user: UserModel = Depends(get_current_superuser),
) -> List[User]:
    """Get list of users (superuser only)."""
    users = await user_service.get_users(skip=skip, limit=limit)
    return [User.model_validate(user) for user in users]


@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: UserModel = Depends(get_current_active_user),
) -> User:
    """Get current user information."""
    return User.model_validate(current_user)


@router.put("/me", response_model=User)
async def update_current_user(
    user_update: UserUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
) -> User:
    """Update current user information."""
    try:
        updated_user = await user_service.update_user(
            user=current_user,
            email=user_update.email,
            username=user_update.username,
            full_name=user_update.full_name,
            password=user_update.password,
        )
        return User.model_validate(updated_user)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists",
        )


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: UserModel = Depends(get_current_superuser),
) -> User:
    """Get user by ID (superuser only)."""
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return User.model_validate(user)


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user: UserModel = Depends(get_current_superuser),
) -> User:
    """Update user by ID (superuser only)."""
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    try:
        updated_user = await user_service.update_user(
            user=user,
            email=user_update.email,
            username=user_update.username,
            full_name=user_update.full_name,
            password=user_update.password,
        )
        return User.model_validate(updated_user)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists",
        )


@router.delete("/{user_id}", response_model=Message)
async def deactivate_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: UserModel = Depends(get_current_superuser),
) -> Message:
    """Deactivate user by ID (superuser only)."""
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await user_service.deactivate_user(user)
    return Message(message="User deactivated successfully")
