"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_health_check_async(async_client: AsyncClient):
    """Test health check endpoint with async client."""
    response = await async_client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_root_endpoint(client: TestClient):
    """Test root endpoint."""
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Hello World"


@pytest.mark.asyncio
async def test_root_endpoint_async(async_client: AsyncClient):
    """Test root endpoint with async client."""
    response = await async_client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Hello World"


@pytest.mark.asyncio
async def test_api_docs_accessible(async_client: AsyncClient):
    """Test that API documentation is accessible."""
    response = await async_client.get("/api/v1/docs")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
