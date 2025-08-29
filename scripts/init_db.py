#!/usr/bin/env python3
"""Database initialization script."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from test_argo_fix.core.config import get_settings
from test_argo_fix.core.database import init_db
from test_argo_fix.core.logging import get_logger, setup_logging
from test_argo_fix.services.user_service import UserService
from test_argo_fix.core.database import get_async_session_context

logger = get_logger(__name__)


async def create_superuser():
    """Create initial superuser account."""
    settings = get_settings()
    
    async with get_async_session_context() as session:
        service = UserService(session)
        
        # Check if superuser already exists
        existing = await service.get_user_by_username("admin")
        if existing:
            logger.info("Superuser already exists", username="admin")
            return
        
        # Create superuser
        user = await service.create_user(
            email="admin@example.com",
            username="admin",
            password="admin123",
            full_name="System Administrator",
            is_superuser=True,
        )
        
        logger.info(
            "Superuser created successfully",
            user_id=user.id,
            username=user.username,
        )
        print(f"✅ Superuser created: {user.username}")
        print("⚠️  Please change the default password!")


async def main():
    """Initialize database and create superuser."""
    settings = get_settings()
    setup_logging(settings.log_level)
    
    logger.info("Initializing database...")
    
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized successfully")
        
        # Create superuser
        await create_superuser()
        
        logger.info("Database initialization completed")
        print("✅ Database initialization completed successfully!")
        
    except Exception as e:
        logger.error("Database initialization failed", error=str(e))
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
