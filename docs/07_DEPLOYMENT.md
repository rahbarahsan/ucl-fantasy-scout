# Deployment Guide

## Overview

This guide covers deploying UCL Fantasy Scout to production using Docker, Docker Compose, and cloud services.

---

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- A domain name (optional, for HTTPS)
- Anthropic or Google API keys
- Git

---

## Local Docker Deployment

### Build Images

```bash
# Build all services
docker compose build

# Build specific service
docker compose build backend
docker compose build frontend
```

### Run Services

```bash
# Start all services (detached)
docker compose up -d

# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Stop services
docker compose down
```

**Services:**
- Frontend: http://localhost (port 80)
- Backend: http://localhost:8000
- Health check: http://localhost:8000/health

### First-Time Setup

1. **Create `.env` in project root:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with production values:**
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   GEMINI_API_KEY=AIza...
   ENCRYPTION_SECRET=your-32-char-secret-key-here!!!
   ENVIRONMENT=production
   LOG_LEVEL=INFO
   ```

3. **Start containers:**
   ```bash
   docker compose up -d
   ```

4. **Verify health:**
   ```bash
   curl http://localhost:8000/health
   ```

---

## Docker Compose Architecture

**File:** `docker-compose.yml`

```yaml
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - ENCRYPTION_SECRET=${ENCRYPTION_SECRET}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    environment:
      - VITE_API_BASE=http://backend:8000
    depends_on:
      - backend
```

---

## Dockerfiles

### Backend Dockerfile

**File:** `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Optimization:** Uses `slim` base image, multi-stage builds optional for V2

### Frontend Dockerfile

**File:** `frontend/Dockerfile`

```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Runtime stage
FROM nginx:alpine

COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

**Optimization:** Multi-stage build (only dist copied to nginx)

---

## Environment Configuration

### Development

```env
ENVIRONMENT=development
LOG_LEVEL=DEBUG
ANTHROPIC_API_KEY=sk-ant-dev-key
GEMINI_API_KEY=test-key
ENCRYPTION_SECRET=dev-secret-32-chars-minimum!
```

### Production

```env
ENVIRONMENT=production
LOG_LEVEL=INFO
ANTHROPIC_API_KEY=sk-ant-production-key
GEMINI_API_KEY=production-key
ENCRYPTION_SECRET=prod-secret-32-chars-minimum!
```

---

## Cloud Deployment

### AWS ECS (Elastic Container Service)

**Prerequisites:**
- AWS account
- ECR (Elastic Container Registry) created
- IAM role for ECS tasks

**Steps:**

1. **Push images to ECR:**
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
   
   docker tag ucl-fantasy-scout-backend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/ucl-fantasy-scout-backend:latest
   docker push <account>.dkr.ecr.us-east-1.amazonaws.com/ucl-fantasy-scout-backend:latest
   ```

2. **Create ECS task definition:**
   ```json
   {
     "family": "ucl-fantasy-scout",
     "containerDefinitions": [
       {
         "name": "backend",
         "image": "<account>.dkr.ecr.us-east-1.amazonaws.com/ucl-fantasy-scout-backend:latest",
         "portMappings": [{ "containerPort": 8000 }],
         "environment": [
           { "name": "ENVIRONMENT", "value": "production" }
         ],
         "secrets": [
           { "name": "ANTHROPIC_API_KEY", "valueFrom": "arn:aws:secretsmanager:..." }
         ]
       }
     ]
   }
   ```

3. **Create ECS service with ALB (Application Load Balancer):**
   - Route `/api/*` to backend
   - Route `/` to frontend

### Google Cloud Run

**Setup:**

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# Authenticate
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID
```

**Deploy Backend:**

```bash
# Build and push
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/ucl-fantasy-scout-backend ./backend

# Deploy
gcloud run deploy ucl-fantasy-scout-backend \
  --image gcr.io/YOUR_PROJECT_ID/ucl-fantasy-scout-backend \
  --platform managed \
  --region us-central1 \
  --set-env-vars ANTHROPIC_API_KEY=sk-ant-...,ENCRYPTION_SECRET=... \
  --allow-unauthenticated
```

**Deploy Frontend:**

```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/ucl-fantasy-scout-frontend ./frontend

gcloud run deploy ucl-fantasy-scout-frontend \
  --image gcr.io/YOUR_PROJECT_ID/ucl-fantasy-scout-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Heroku (Legacy)

If using Heroku (note: paid tier now required):

```bash
# Login
heroku login

# Create app
heroku create ucl-fantasy-scout

# Set environment
heroku config:set ANTHROPIC_API_KEY=sk-ant-...

# Deploy from git
git push heroku main
```

---

## Reverse Proxy Setup (nginx)

**For local production-like testing:**

```nginx
server {
    listen 80;
    server_name localhost;

    # Frontend
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend health
    location /health {
        proxy_pass http://backend:8000/health;
    }
}
```

---

## SSL/TLS Certificate

### Let's Encrypt (Free)

Using `certbot`:

```bash
# Install
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com

# Auto-renew
sudo systemctl enable certbot.timer
```

**Configure nginx for HTTPS:**

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # ... rest of config
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## Monitoring & Logging

### Health Checks

Backend includes health endpoint:

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "ok",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

Configure in load balancer to hit `/health` every 30 seconds.

### Logging

**Backend logs:**
```bash
docker compose logs backend
```

**Structured logs (JSON):**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "info",
  "module": "pipeline",
  "event": "analysis_complete",
  "matchday": 6,
  "player_count": 11
}
```

### Metrics (Optional)

For production, add Prometheus metrics:

```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

Metrics at: `http://localhost:8000/metrics`

---

## Scaling

### Horizontal Scaling

**Docker Swarm:**

```bash
docker swarm init
docker service create --name backend -p 8000:8000 ucl-fantasy-scout-backend
docker service scale backend=3
```

**Kubernetes (Advanced):**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ucl-fantasy-scout-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: ucl-fantasy-scout-backend:latest
        ports:
        - containerPort: 8000
```

### Caching

For high-traffic deployments, add Redis:

```python
from fastapi_cache2 import FastAPICache2
from fastapi_cache2.backends.redis import RedisBackend

FastAPICache2.init(RedisBackend(url="redis://cache:6379"), prefix="fastapi-cache")

@cached(expire=3600)
async def get_cached_fixtures():
    # Cached for 1 hour
    pass
```

---

## Database Persistence (Future)

For squad history feature:

```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD: password
      POSTGRES_DB: ucl_fantasy
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Then connect backend:
```python
from sqlalchemy import create_engine

engine = create_engine("postgresql://user:pass@postgres:5432/ucl_fantasy")
```

---

## Backup & Recovery

### Database Backup

```bash
# PostgreSQL dump
docker exec postgres-container pg_dump -U user database > backup.sql

# Restore
docker exec -i postgres-container psql -U user database < backup.sql
```

### Configuration Backup

```bash
# Backup .env
cp .env .env.backup

# Backup Docker volumes
docker run --rm -v postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup.tar.gz -C /data .
```

---

## Troubleshooting Deployment

| Issue | Solution |
|-------|----------|
| Container won't start | Check logs: `docker compose logs backend` |
| API returns 500 | Check environment variables: `docker compose config` |
| Port already in use | Change port in `docker-compose.yml` or kill process |
| Network errors | Ensure backend healthy: `curl http://localhost:8000/health` |
| SSL certificate error | Verify cert files exist: `ls /etc/letsencrypt/live/` |
| High API latency | Increase timeout, check rate limiting, scale replicas |

---

## Security Considerations

1. **Never commit `.env`** — Use `.env.example` with placeholders
2. **Use environment secrets** — AWS Secrets Manager, Google Secret Manager, etc
3. **Enable HTTPS** — Always use TLS in production
4. **Firewall rules** — Restrict backend to internal traffic only
5. **API key rotation** — Regularly update keys
6. **Rate limiting** — Already enabled (10 req/min per IP)
7. **CORS** — Restrict to known origins
8. **Input validation** — Image validation, JSON schema validation on all inputs

---

## Performance Optimization

### Backend

```bash
# Use gunicorn for multi-worker setup
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

### Frontend

```bash
# Serve with gzip compression
gzip_types text/css application/javascript text/javascript image/svg+xml;
gzip_min_length 1024;
```

### Caching

- Static assets: Cache-Control: max-age=31536000 (1 year)
- API responses: Cache-Control: no-cache (revalidate each request)

---

## Continuous Deployment (CD)

### GitHub Actions to Docker Hub

**File:** `.github/workflows/release.yml`

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v2
      - uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      - uses: docker/build-push-action@v4
        with:
          push: true
          tags: |
            yourname/ucl-fantasy-scout:latest
            yourname/ucl-fantasy-scout:${{ github.ref_name }}
```

Push tag to trigger:
```bash
git tag v1.0.0
git push origin v1.0.0
```

---

## Rollback

```bash
# View deployment history
docker image ls

# Rollback to previous version
docker compose down
docker pull ucl-fantasy-scout-backend:v1.0.0
docker compose up -d
```

---

## Checklist

- [ ] All environment variables set in production
- [ ] SSL certificate installed and configured
- [ ] Health checks enabled in load balancer
- [ ] Error logging configured
- [ ] Backups automated
- [ ] API keys rotated
- [ ] Rate limiting active
- [ ] CORS configured
- [ ] Database persistence setup (if needed)
- [ ] CDN configured for static assets (optional)
