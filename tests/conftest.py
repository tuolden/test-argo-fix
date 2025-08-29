"""Test configuration and fixtures.

This version auto-detects the project package under src/ to avoid template
placeholder issues in environments that copy files without rendering.
"""

import asyncio
import importlib
import pathlib
import pkgutil
import sys
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient


def _detect_project_name() -> str:
    """Detect the project package name under src/ and add to sys.path."""
    src_dir = pathlib.Path(__file__).resolve().parents[1] / "src"
    sys.path.insert(0, str(src_dir))
    for m in pkgutil.iter_modules([str(src_dir)]):
        if not m.name.startswith("."):
            return m.name
    raise RuntimeError("Could not detect project package under src/")


_PROJECT = _detect_project_name()
_app_module = importlib.import_module(f"{_PROJECT}.main")
app = getattr(_app_module, "app")


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
