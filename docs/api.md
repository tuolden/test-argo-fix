# API Documentation

This document provides comprehensive documentation for the test_argo_fix REST API.

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Base URL and Versioning](#base-url-and-versioning)
- [Common Response Formats](#common-response-formats)
- [Error Handling](#error-handling)
- [Endpoints](#endpoints)
- [Examples](#examples)

## Overview

test_argo_fix provides a RESTful API built with FastAPI, featuring:

- **OpenAPI/Swagger** documentation at `/api/v1/docs`
- **ReDoc** documentation at `/api/v1/redoc`
- **JSON** request/response format
- **JWT-based** authentication
- **Comprehensive** error handling
- **Request validation** with Pydantic

## Authentication

The API uses JWT (JSON Web Token) based authentication.

### Getting an Access Token

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=your_username&password=your_password
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using the Access Token

Include the token in the Authorization header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token Expiration

- **Default expiration**: 30 minutes
- **Configurable** via `ACCESS_TOKEN_EXPIRE_MINUTES` environment variable
- **No refresh tokens**: Client must re-authenticate when token expires

## Base URL and Versioning

- **Base URL**: `http://localhost:8080` (development)
- **API Version**: `/api/v1`
- **Full Base URL**: `http://localhost:8080/api/v1`

## Common Response Formats

### Success Response

```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

### List Response

```json
[
  {
    "id": 1,
    "email": "user1@example.com",
    "username": "user1"
  },
  {
    "id": 2,
    "email": "user2@example.com",
    "username": "user2"
  }
]
```

### Message Response

```json
{
  "message": "Operation completed successfully"
}
```

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message",
  "code": "ERROR_CODE",
  "type": "validation_error"
}
```

### HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| `200` | Success |
| `201` | Created |
| `400` | Bad Request |
| `401` | Unauthorized |
| `403` | Forbidden |
| `404` | Not Found |
| `422` | Validation Error |
| `500` | Internal Server Error |

### Common Error Examples

#### Validation Error (422)
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### Authentication Error (401)
```json
{
  "detail": "Could not validate credentials"
}
```

#### Permission Error (403)
```json
{
  "detail": "Not enough permissions"
}
```

#### Not Found Error (404)
```json
{
  "detail": "User not found"
}
```

## Endpoints

### Health Check

#### Check Application Health

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "test_argo_fix"
}
```

### Authentication Endpoints

#### Login

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=string&password=string
```

**Parameters:**
- `username` (string, required): Username or email
- `password` (string, required): User password

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

**Errors:**
- `401`: Invalid credentials
- `400`: Inactive user

### User Management Endpoints

#### Get Current User Information

```http
GET /api/v1/users/me
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

**Errors:**
- `401`: Invalid or missing token

#### Update Current User

```http
PUT /api/v1/users/me
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "new@example.com",
  "username": "newusername",
  "full_name": "New Full Name",
  "password": "newpassword"
}
```

**Parameters (all optional):**
- `email` (string): New email address
- `username` (string): New username
- `full_name` (string): New full name
- `password` (string): New password

**Response:**
```json
{
  "id": 1,
  "email": "new@example.com",
  "username": "newusername",
  "full_name": "New Full Name",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:01Z"
}
```

**Errors:**
- `400`: Username or email already exists
- `401`: Invalid or missing token

### Admin Endpoints (Superuser Only)

#### Create User

```http
POST /api/v1/users/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "password",
  "full_name": "Full Name"
}
```

**Parameters:**
- `email` (string, required): User email address
- `username` (string, required): Username
- `password` (string, required): User password
- `full_name` (string, optional): Full name
- `is_active` (boolean, optional): Active status (default: true)

**Response:**
```json
{
  "id": 2,
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

**Errors:**
- `400`: Username or email already exists
- `403`: Not enough permissions

#### List Users

```http
GET /api/v1/users/?skip=0&limit=100
Authorization: Bearer <admin_token>
```

**Query Parameters:**
- `skip` (integer, optional): Number of users to skip (default: 0)
- `limit` (integer, optional): Maximum number of users to return (default: 100)

**Response:**
```json
[
  {
    "id": 1,
    "email": "admin@example.com",
    "username": "admin",
    "full_name": "Administrator",
    "is_active": true,
    "is_superuser": true,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  },
  {
    "id": 2,
    "email": "user@example.com",
    "username": "user",
    "full_name": "Regular User",
    "is_active": true,
    "is_superuser": false,
    "created_at": "2023-01-01T00:00:01Z",
    "updated_at": "2023-01-01T00:00:01Z"
  }
]
```

**Errors:**
- `403`: Not enough permissions

#### Get User by ID

```http
GET /api/v1/users/{user_id}
Authorization: Bearer <admin_token>
```

**Path Parameters:**
- `user_id` (integer, required): User ID

**Response:**
```json
{
  "id": 2,
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

**Errors:**
- `404`: User not found
- `403`: Not enough permissions

#### Update User by ID

```http
PUT /api/v1/users/{user_id}
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "email": "updated@example.com",
  "full_name": "Updated Name"
}
```

**Path Parameters:**
- `user_id` (integer, required): User ID

**Body Parameters (all optional):**
- `email` (string): New email address
- `username` (string): New username
- `full_name` (string): New full name
- `password` (string): New password

**Response:**
```json
{
  "id": 2,
  "email": "updated@example.com",
  "username": "username",
  "full_name": "Updated Name",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:01Z"
}
```

**Errors:**
- `404`: User not found
- `400`: Username or email already exists
- `403`: Not enough permissions

#### Deactivate User

```http
DELETE /api/v1/users/{user_id}
Authorization: Bearer <admin_token>
```

**Path Parameters:**
- `user_id` (integer, required): User ID

**Response:**
```json
{
  "message": "User deactivated successfully"
}
```

**Errors:**
- `404`: User not found
- `403`: Not enough permissions

**Note:** This endpoint deactivates the user (sets `is_active: false`) rather than permanently deleting them.

## Examples

### Complete User Workflow

#### 1. Admin Login

```bash
curl -X POST "http://localhost:8080/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=admin123"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 2. Create New User

```bash
curl -X POST "http://localhost:8080/api/v1/users/" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
     -H "Content-Type: application/json" \
     -d '{
       "email": "newuser@example.com",
       "username": "newuser",
       "password": "securepassword",
       "full_name": "New User"
     }'
```

#### 3. New User Login

```bash
curl -X POST "http://localhost:8080/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=newuser&password=securepassword"
```

#### 4. Get User Profile

```bash
curl -X GET "http://localhost:8080/api/v1/users/me" \
     -H "Authorization: Bearer <user_token>"
```

#### 5. Update Profile

```bash
curl -X PUT "http://localhost:8080/api/v1/users/me" \
     -H "Authorization: Bearer <user_token>" \
     -H "Content-Type: application/json" \
     -d '{
       "full_name": "Updated User Name"
     }'
```

### Python Client Example

```python
import httpx

class {{PROJECT_NAME.title()}}Client:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.client = httpx.Client(base_url=base_url)
        self.token = None
    
    def login(self, username: str, password: str) -> bool:
        """Login and store access token."""
        response = self.client.post(
            "/api/v1/auth/login",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            self.client.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
            return True
        return False
    
    def get_current_user(self):
        """Get current user information."""
        response = self.client.get("/api/v1/users/me")
        response.raise_for_status()
        return response.json()
    
    def create_user(self, email: str, username: str, password: str, 
                   full_name: str = None):
        """Create a new user (admin only)."""
        data = {
            "email": email,
            "username": username,
            "password": password
        }
        if full_name:
            data["full_name"] = full_name
        
        response = self.client.post("/api/v1/users/", json=data)
        response.raise_for_status()
        return response.json()
    
    def get_users(self, skip: int = 0, limit: int = 100):
        """Get list of users (admin only)."""
        response = self.client.get(
            "/api/v1/users/",
            params={"skip": skip, "limit": limit}
        )
        response.raise_for_status()
        return response.json()

# Usage example
client = {{PROJECT_NAME.title()}}Client()

# Login
if client.login("admin", "admin123"):
    print("Logged in successfully")
    
    # Get current user
    user = client.get_current_user()
    print(f"Current user: {user['username']}")
    
    # Create new user
    new_user = client.create_user(
        email="test@example.com",
        username="testuser",
        password="testpass",
        full_name="Test User"
    )
    print(f"Created user: {new_user['id']}")
    
    # List users
    users = client.get_users()
    print(f"Total users: {len(users)}")
```

### JavaScript/TypeScript Client Example

```typescript
class {{PROJECT_NAME.charAt(0).toUpperCase() + PROJECT_NAME.slice(1)}}Client {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string = 'http://localhost:8080') {
    this.baseURL = baseURL;
  }

  async login(username: string, password: string): Promise<boolean> {
    const response = await fetch(`${this.baseURL}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`,
    });

    if (response.ok) {
      const data = await response.json();
      this.token = data.access_token;
      return true;
    }
    return false;
  }

  async getCurrentUser() {
    const response = await fetch(`${this.baseURL}/api/v1/users/me`, {
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch user');
    }

    return response.json();
  }

  async createUser(userData: {
    email: string;
    username: string;
    password: string;
    full_name?: string;
  }) {
    const response = await fetch(`${this.baseURL}/api/v1/users/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      throw new Error('Failed to create user');
    }

    return response.json();
  }
}

// Usage
const client = new {{PROJECT_NAME.charAt(0).toUpperCase() + PROJECT_NAME.slice(1)}}Client();

client.login('admin', 'admin123').then(success => {
  if (success) {
    console.log('Logged in successfully');
    
    client.getCurrentUser().then(user => {
      console.log('Current user:', user.username);
    });
  }
});
```

## OpenAPI/Swagger Integration

The API automatically generates OpenAPI documentation. Access it at:

- **Interactive docs**: http://localhost:8080/api/v1/docs
- **ReDoc**: http://localhost:8080/api/v1/redoc
- **OpenAPI JSON**: http://localhost:8080/api/v1/openapi.json

### Customizing API Documentation

You can customize the OpenAPI documentation in your FastAPI app:

```python
from fastapi import FastAPI

app = FastAPI(
    title="test_argo_fix API",
    description="Test project for Argo fix",
    version="1.0.0",
    terms_of_service="https://example.com/terms/",
    contact={
        "name": "API Support",
        "url": "https://example.com/contact/",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)
```

## Rate Limiting

For production deployments, consider implementing rate limiting:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/v1/users/me")
@limiter.limit("100/minute")
def get_current_user(request: Request):
    # endpoint implementation
    pass
```

## CORS Configuration

CORS is configured to allow requests from specified origins:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
