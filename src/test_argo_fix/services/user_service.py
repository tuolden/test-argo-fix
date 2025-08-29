"""User service for business logic."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.logging import get_logger
from ..models.user import User
from ..utils.security import get_password_hash, verify_password

logger = get_logger(__name__)


class UserService:
    """Service for user operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(
        self,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None,
        is_superuser: bool = False,
    ) -> User:
        """Create a new user."""
        logger.info("Creating new user username=%s email=%s", username, email)

        hashed_password = get_password_hash(password)
        user = User(
            email=email,
            username=username,
            full_name=full_name,
            hashed_password=hashed_password,
            is_superuser=is_superuser,
        )

        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)

        logger.info("User created successfully user_id=%s", user.id)
        return user

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_users(
        self, skip: int = 0, limit: int = 100, active_only: bool = True
    ) -> List[User]:
        """Get list of users."""
        query = select(User).offset(skip).limit(limit)

        if active_only:
            # Use SQLAlchemy's is_ comparator to avoid style/lint issues
            query = query.where(User.is_active.is_(True))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user by username and password."""
        user = await self.get_user_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    async def update_user(
        self,
        user: User,
        email: Optional[str] = None,
        username: Optional[str] = None,
        full_name: Optional[str] = None,
        password: Optional[str] = None,
    ) -> User:
        """Update user information."""
        logger.info("Updating user user_id=%s", user.id)

        if email is not None:
            user.email = email
        if username is not None:
            user.username = username
        if full_name is not None:
            user.full_name = full_name
        if password is not None:
            user.hashed_password = get_password_hash(password)

        await self.session.flush()
        await self.session.refresh(user)

        logger.info("User updated successfully user_id=%s", user.id)
        return user

    async def deactivate_user(self, user: User) -> User:
        """Deactivate user account."""
        logger.info("Deactivating user user_id=%s", user.id)

        user.is_active = False
        await self.session.flush()
        await self.session.refresh(user)

        logger.info("User deactivated successfully user_id=%s", user.id)
        return user
