# Deployment Guide

This guide covers deployment options for test_argo_fix in various environments.

## Table of Contents

- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Cloud Deployments](#cloud-deployments)
- [Environment Configuration](#environment-configuration)
- [Monitoring and Maintenance](#monitoring-and-maintenance)

## Local Development

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+ (optional)
- Git

### Setup Steps

1. **Clone and install**:
   ```bash
   git clone https://github.com/tuolden/test_argo_fix.git
   cd test_argo_fix
   
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   pip install -e .[dev]
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Setup database**:
   ```bash
   # Using Docker
   docker run -d --name test_argo_fix-postgres \
     -e POSTGRES_USER=user \
     -e POSTGRES_PASSWORD=password \
     -e POSTGRES_DB=test_argo_fix \
     -p 5432:5432 postgres:15
   
   # Initialize database
   python scripts/init_db.py
   ```

4. **Run application**:
   ```bash
   python scripts/run_dev.py
   ```

## Docker Deployment

### Development with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

### Production with Docker

1. **Build production image**:
   ```bash
   docker build -t test_argo_fix:latest .
   ```

2. **Run with external database**:
   ```bash
   docker run -d \
     --name test_argo_fix \
     -p 8080:8080 \
     -e DATABASE_URL=postgresql://user:pass@host:5432/test_argo_fix \
     -e SECRET_KEY="your-production-secret" \
     -e DEBUG=false \
     test_argo_fix:latest
   ```

### Docker Compose Production

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  app:
    image: test_argo_fix:latest
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/test_argo_fix
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=false
      - LOG_LEVEL=INFO
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: test_argo_fix
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
```

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (k3s, minikube, EKS, GKE, AKS)
- kubectl configured
- Container registry access

### Quick Deploy

```bash
# Deploy to staging
kubectl apply -k k8s/staging/

# Deploy to production
kubectl apply -k k8s/production/
```

### Step-by-Step Deployment

1. **Create namespace**:
   ```bash
   kubectl create namespace test_argo_fix
   ```

2. **Configure secrets**:
   ```bash
   # Create database secret
   kubectl create secret generic test_argo_fix-secret \
     --from-literal=DATABASE_URL="postgresql://user:pass@postgres:5432/test_argo_fix" \
     --from-literal=SECRET_KEY="your-production-secret-key" \
     --from-literal=REDIS_URL="redis://redis:6379" \
     -n test_argo_fix
   ```

3. **Deploy database (if not external)**:
   ```bash
   # PostgreSQL deployment
   kubectl apply -f - <<EOF
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: postgres
     namespace: test_argo_fix
   spec:
     replicas: 1
     selector:
       matchLabels:
         app: postgres
     template:
       metadata:
         labels:
           app: postgres
       spec:
         containers:
         - name: postgres
           image: postgres:15
           env:
           - name: POSTGRES_USER
             value: "user"
           - name: POSTGRES_PASSWORD
             value: "password"
           - name: POSTGRES_DB
             value: "test_argo_fix"
           ports:
           - containerPort: 5432
           volumeMounts:
           - name: postgres-data
             mountPath: /var/lib/postgresql/data
         volumes:
         - name: postgres-data
           persistentVolumeClaim:
             claimName: postgres-pvc
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: postgres
     namespace: test_argo_fix
   spec:
     selector:
       app: postgres
     ports:
     - port: 5432
       targetPort: 5432
   ---
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata:
     name: postgres-pvc
     namespace: test_argo_fix
   spec:
     accessModes:
       - ReadWriteOnce
     resources:
       requests:
         storage: 10Gi
   EOF
   ```

4. **Deploy application**:
   ```bash
   kubectl apply -k k8s/production/
   ```

5. **Verify deployment**:
   ```bash
   kubectl get pods -n test_argo_fix
   kubectl logs -f deployment/test_argo_fix -n test_argo_fix
   ```

### Argo CD GitOps Deployment

1. **Install Argo CD**:
   ```bash
   kubectl create namespace argocd
   kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
   ```

2. **Deploy Argo CD applications**:
   ```bash
   kubectl apply -f k8s/argocd-staging.yaml
   kubectl apply -f k8s/argocd-production.yaml
   ```

3. **Access Argo CD UI**:
   ```bash
   kubectl port-forward svc/argocd-server -n argocd 8080:443
   # Get admin password
   kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
   ```

## Cloud Deployments

### AWS EKS

```bash
# Create EKS cluster
eksctl create cluster --name test_argo_fix --region us-west-2

# Deploy application
kubectl apply -k k8s/production/

# Setup ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/aws/deploy.yaml
```

### Google GKE

```bash
# Create GKE cluster
gcloud container clusters create test_argo_fix \
  --zone us-central1-a \
  --num-nodes 3

# Deploy application
kubectl apply -k k8s/production/
```

### Azure AKS

```bash
# Create AKS cluster
az aks create \
  --resource-group myResourceGroup \
  --name test_argo_fix \
  --node-count 3 \
  --enable-addons monitoring

# Deploy application
kubectl apply -k k8s/production/
```

## Environment Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | - | Yes |
| `SECRET_KEY` | JWT signing secret | - | Yes |
| `DEBUG` | Enable debug mode | `false` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `HOST` | Server host | `0.0.0.0` | No |
| `PORT` | Server port | `8080` | No |
| `ALLOWED_HOSTS` | CORS allowed origins | `["*"]` | No |
| `REDIS_URL` | Redis connection string | - | No |

### Configuration Management

#### Using ConfigMaps and Secrets

```bash
# ConfigMap for non-sensitive data
kubectl create configmap test_argo_fix-config \
  --from-literal=DEBUG=false \
  --from-literal=LOG_LEVEL=INFO \
  -n test_argo_fix

# Secret for sensitive data
kubectl create secret generic test_argo_fix-secret \
  --from-literal=DATABASE_URL="postgresql://..." \
  --from-literal=SECRET_KEY="..." \
  -n test_argo_fix
```

#### Using External Secret Management

For production environments, consider using:

- **AWS Secrets Manager** with External Secrets Operator
- **Azure Key Vault** with CSI Secret Store Driver
- **Google Secret Manager** with Secret Manager CSI driver
- **HashiCorp Vault** with Vault Agent

### Database Configuration

#### PostgreSQL Production Settings

```sql
-- Performance tuning
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';

-- Connection settings
ALTER SYSTEM SET max_connections = 100;
ALTER SYSTEM SET superuser_reserved_connections = 3;

SELECT pg_reload_conf();
```

#### Connection Pooling

For production, consider using PgBouncer:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pgbouncer
spec:
  template:
    spec:
      containers:
      - name: pgbouncer
        image: pgbouncer/pgbouncer:latest
        env:
        - name: DATABASES_HOST
          value: "postgres"
        - name: DATABASES_PORT
          value: "5432"
        - name: DATABASES_USER
          value: "user"
        - name: DATABASES_PASSWORD
          value: "password"
        - name: DATABASES_DBNAME
          value: "test_argo_fix"
        - name: POOL_MODE
          value: "transaction"
        - name: MAX_CLIENT_CONN
          value: "100"
```

## Monitoring and Maintenance

### Health Checks

The application provides several health check endpoints:

- `/health` - Basic health check
- `/health/db` - Database connectivity check
- `/health/redis` - Redis connectivity check

### Logging

Structured logging with different formats:

```python
# Development (console)
LOG_FORMAT=console

# Production (JSON)
LOG_FORMAT=json
```

### Metrics and Monitoring

#### Prometheus Integration

Add metrics endpoint:

```python
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('app_requests_total', 'Total requests')
REQUEST_LATENCY = Histogram('app_request_duration_seconds', 'Request latency')

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

#### Grafana Dashboard

Import dashboard for application metrics:

```json
{
  "dashboard": {
    "title": "test_argo_fix Dashboard",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(app_requests_total[5m])"
          }
        ]
      }
    ]
  }
}
```

### Backup and Recovery

#### Database Backups

```bash
# Create backup script
kubectl create job db-backup --from=cronjob/db-backup

# Manual backup
kubectl exec postgres-0 -- pg_dump -U user test_argo_fix > backup.sql

# Restore
kubectl exec -i postgres-0 -- psql -U user test_argo_fix < backup.sql
```

#### Automated Backups

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: db-backup
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: postgres-backup
            image: postgres:15
            command:
            - /bin/bash
            - -c
            - |
              pg_dump -h postgres -U user test_argo_fix | gzip > /backup/test_argo_fix-$(date +%Y%m%d).sql.gz
              find /backup -name "*.sql.gz" -mtime +7 -delete
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
```

### Scaling

#### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: test_argo_fix-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: test_argo_fix
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Security Considerations

1. **Network Policies**: Restrict pod-to-pod communication
2. **Pod Security Standards**: Enforce security contexts
3. **RBAC**: Limit service account permissions
4. **Image Security**: Scan images for vulnerabilities
5. **Secrets Management**: Use external secret stores
6. **TLS Encryption**: Enable TLS for all communications

### Troubleshooting

#### Common Issues

1. **Pod startup failures**:
   ```bash
   kubectl describe pod <pod-name> -n test_argo_fix
   kubectl logs <pod-name> -n test_argo_fix
   ```

2. **Database connection issues**:
   ```bash
   kubectl exec -it <app-pod> -n test_argo_fix -- python -c "
   from test_argo_fix.core.database import sync_engine
   print(sync_engine.execute('SELECT 1').scalar())
   "
   ```

3. **Ingress issues**:
   ```bash
   kubectl describe ingress test_argo_fix -n test_argo_fix
   kubectl logs -n ingress-nginx deployment/ingress-nginx-controller
   ```

#### Performance Tuning

1. **Database optimization**:
   - Analyze slow queries
   - Add appropriate indexes
   - Tune connection pool size

2. **Application optimization**:
   - Profile CPU and memory usage
   - Optimize database queries
   - Implement caching

3. **Kubernetes optimization**:
   - Right-size resource requests/limits
   - Use appropriate storage classes
   - Optimize networking
