# 🚀 test_argo_fix

**Test project for Argo fix**

Production-ready FastAPI application with authentication, testing, and automated deployment.

## ⚡ Quick Start

```bash
# 1. Setup environment
python -m venv venv && source venv/bin/activate
pip install -e .[dev]

# 2. Configure database
cp .env.example .env
# Edit .env with your database settings

# 3. Initialize and run
python scripts/init_db.py
python scripts/run_dev.py
```

**🌐 Access your API**: http://localhost:8080  
**📖 API Docs**: http://localhost:8080/api/v1/docs

## ✨ What's Included

- **FastAPI REST API** with PostgreSQL and JWT authentication
- **Complete test suite** (unit + integration tests)  
- **Docker containerization** with development stack
- **Kubernetes manifests** for staging and production
- **CI/CD pipeline** with GitHub Actions
- **API documentation** auto-generated from code

## 🐳 Docker Development

```bash
# Start full stack (app + database)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop stack  
docker-compose down
```

## 🔐 Default Admin Account

- **Username**: `admin`  
- **Password**: `admin123`

**⚠️ Change this password in production!**

## 🌐 API Endpoints

- **Login**: `POST /api/v1/auth/login`
- **User Profile**: `GET /api/v1/users/me`
- **Create User**: `POST /api/v1/users/` (admin only)
- **Health Check**: `GET /health`

**📖 Full API docs**: http://localhost:8080/api/v1/docs

## 🔧 Development Commands

```bash
# Run tests
pytest

# Format code  
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Run pre-commit hooks
pre-commit run --all-files
```

## ☸️ Kubernetes Deployment

**⚠️ Prerequisites**: GitHub repo + secrets configured (see template docs)

```bash
# Deploy to production only
kubectl apply -k k8s/production/

# GitOps with Argo CD (production)
kubectl apply -f k8s/argocd-production.yaml
```

## 📁 Project Structure

- **`src/test_argo_fix/`** - Application source code
- **`tests/`** - Unit and integration tests
- **`k8s/`** - Kubernetes deployment manifests
- **`scripts/`** - Development utilities
- **`docs/`** - Additional documentation

---

**Built with ❤️ using the Python FastAPI Template System**
