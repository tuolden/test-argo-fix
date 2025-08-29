#!/usr/bin/env python3
"""Development server runner with Redis environment support."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Try to load environment from Redis
try:
    from redis_env import RedisEnvLoader
    loader = RedisEnvLoader(verbose=False)
    env_vars = loader.get_environment(use_redis=True)
    
    # Set environment variables
    for key, value in env_vars.items():
        os.environ.setdefault(key, value)
    print(f"✅ Loaded {len(env_vars)} environment variables from Redis")
    
except ImportError:
    print("⚠️  Redis environment loader not available, using .env fallback")
    # Load from .env file
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())
except Exception as e:
    print(f"⚠️  Could not load Redis environment: {e}")
    print("⚠️  Make sure Redis cluster is available and port-forward is active")

import uvicorn

from test_argo_fix.core.config import get_settings


def main():
    """Run development server."""
    settings = get_settings()
    
    # Override settings for development
    os.environ.setdefault("DEBUG", "true")
    os.environ.setdefault("LOG_LEVEL", "DEBUG")
    
    uvicorn.run(
        "test_argo_fix.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        reload_dirs=["src"],
        log_level="debug",
        access_log=True,
    )


if __name__ == "__main__":
    main()
