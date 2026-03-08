# EMSI ClassFlow Backend - Deployment Guide

A comprehensive guide for deploying the EMSI ClassFlow API to production environments.

---

## Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Local Production Testing](#local-production-testing)
3. [Cloud Deployment Options](#cloud-deployment-options)
4. [Database Setup](#database-setup)
5. [Environment Configuration](#environment-configuration)
6. [Security Best Practices](#security-best-practices)
7. [Monitoring & Logging](#monitoring--logging)
8. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

Before deploying to production:

- [ ] All tests passing (`pytest`)
- [ ] No debug logging enabled
- [ ] Database migrations created with Alembic
- [ ] Environment variables configured
- [ ] CORS origins restricted
- [ ] Error messages don't leak sensitive info
- [ ] Database backups configured
- [ ] API documentation accessed (/docs)
- [ ] Health check endpoint working
- [ ] All endpoints tested with production data

---

## Local Production Testing

### 1. Build Production Requirements

```bash
# Create frozen requirements for production
pip freeze > requirements-prod.txt
```

### 2. Test with Production Settings

Update `app/database.py`:
```python
# Change from
engine = create_engine(DATABASE_URL, echo=False)

# To
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=0,
    echo=False
)
```

### 3. Run Production Server

```bash
# Using uvicorn directly (production mode)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --loop uvloop

# Or use Gunicorn (recommended for production)
pip install gunicorn uvloop
gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 app.main:app
```

### 4. Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Create room
curl -X POST http://localhost:8000/rooms \
  -H "Content-Type: application/json" \
  -d '{"name":"A101","capacity":30,"floor":1,"type":"classroom"}'

# List rooms
curl http://localhost:8000/rooms
```

---

## Cloud Deployment Options

### Option 1: Render (Recommended for Beginners)

**Pros**: Easy setup, free tier available, automatic deploys from Git

**Steps**:

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: EMSI ClassFlow Backend"
   git remote add origin https://github.com/YOUR_USERNAME/EmsiClassFlowBackEnd.git
   git push -u origin main
   ```

2. **Create Render Account**:
   - Go to https://render.com
   - Sign up with GitHub

3. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Select your GitHub repository
   - Settings:
     - **Name**: emsi-classflow-backend
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app`
     - **Instance Type**: Starter ($7/month)

4. **Add PostgreSQL Database**:
   - Click "New +" → "PostgreSQL"
   - Connect to your Web Service
   - Get connection string from Render dashboard

5. **Set Environment Variables**:
   - In Render dashboard, go to Environment
   - Add: `DATABASE_URL: postgresql://...`

6. **Deploy**:
   - Render automatically deploys on git push
   - Check deployment status in dashboard

**API URL**: `https://emsi-classflow-backend.onrender.com`

---

### Option 2: Railway

**Pros**: Generous free tier, simple interface

**Steps**:

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Create Project**:
   ```bash
   railway init
   ```

3. **Add PostgreSQL**:
   ```bash
   railway add
   # Select PostgreSQL
   ```

4. **Deploy**:
   ```bash
   railway up
   ```

5. **Configure**:
   - Railway automatically sets `DATABASE_URL`
   - App runs on `https://[project-name].up.railway.app`

---

### Option 3: AWS (Elastic Beanstalk)

**Pros**: Scalable, enterprise-grade

**Requirements**: AWS Account

**Steps**:

1. **Install EB CLI**:
   ```bash
   pip install awsebcli
   ```

2. **Create requirements-prod.txt**:
   ```bash
   pip freeze > requirements-prod.txt
   ```

3. **Initialize EB Application**:
   ```bash
   eb init -p python-3.9 emsi-classflow-api
   ```

4. **Create `.ebextensions/python.config`**:
   ```yaml
   option_settings:
     aws:elasticbeanstalk:container:python:
       WSGIPath: app.main:app
       ProxyBaseUrl: "/"
   ```

5. **Deploy**:
   ```bash
   eb create emsi-production
   eb deploy
   ```

6. **Configure Database**:
   - Use AWS RDS for PostgreSQL
   - Set environment variable: `DATABASE_URL`

---

### Option 4: Heroku (Legacy but Still Available)

```bash
# Install Heroku CLI
# Create Procfile:
web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app

# Create runtime.txt:
python-3.9.16

# Deploy
git push heroku main
```

---

### Option 5: Docker Deployment

**1. Create `Dockerfile`**:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn uvloop

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run application
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "app.main:app"]
```

**2. Create `.dockerignore`**:

```
__pycache__
.git
.gitignore
.env
venv
.DS_Store
.pytest_cache
*.pyc
```

**3. Build & Run**:

```bash
# Build image
docker build -t emsi-classflow:latest .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@host:5432/db" \
  emsi-classflow:latest

# Or use docker-compose:
```

**4. Docker Compose (`docker-compose.yml`)**:

```yaml
version: '3.8'

services:
  db:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: emsi_classflow
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: your_secure_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:your_secure_password@db:5432/emsi_classflow
    depends_on:
      - db
    command: >
      sh -c "python -m alembic upgrade head &&
             gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app"

volumes:
  postgres_data:
```

**Run with Docker Compose**:
```bash
docker-compose up -d
```

---

## Database Setup

### PostgreSQL on Cloud

**For Render**:
```bash
# Render creates DB automatically
# Copy connection string from Render dashboard
# Format: postgresql://user:password@host:5432/dbname
```

**For Railway**:
```bash
# Railway creates DB automatically
# Connection string in $DATABASE_URL environment variable
```

**For AWS RDS**:
```bash
# Create RDS instance
# Security group: Allow inbound on port 5432 from EB instances
# Connection: postgresql://master:password@rds-host:5432/emsi_classflow
```

### Database Migrations

For production, use Alembic:

```bash
# Install Alembic
pip install alembic

# Initialize
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head

# In deployment, add to startup:
# alembic upgrade head && gunicorn ...
```

---

## Environment Configuration

### Required Environment Variables

```env
# Database (REQUIRED)
DATABASE_URL=postgresql://user:password@host:5432/emsi_classflow

# Server
DEBUG=False
LOG_LEVEL=INFO

# Security
CORS_ORIGINS=https://frontend.com,https://app.example.com
SECRET_KEY=your-super-secret-key-change-this

# Optional: Email notifications (if implementing later)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Security Best Practices for Environment Variables

**Do NOT**:
- Hardcode secrets in code
- Commit `.env` files to git
- Use same secrets for multiple environments

**Do**:
- Use secret management service
- Use strong, unique passwords
- Rotate secrets regularly
- Log which variables are set (not their values)

---

## Security Best Practices

### 1. Update CORS Configuration

In `app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

# PRODUCTION
allowed_origins = [
    "https://emsi.edu.et",
    "https://app.emsi.edu.et",
    "https://portal.emsi.edu.et"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### 2. Add Authentication

```python
# After implementing JWT:
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthCredentials = Depends(security)):
    # Verify JWT token
    # Extract user_id from token
    # Return user_id
    pass
```

### 3. Add Rate Limiting

```bash
pip install slowapi
```

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/reservations")
@limiter.limit("10/minute")
async def create_reservation(...):
    pass
```

### 4. Enable HTTPS

- All cloud providers automatically provide SSL/TLS
- Redirect HTTP to HTTPS

### 5. SQL Injection Prevention

- Already protected by SQLAlchemy ORM ✅
- Never use string concatenation for queries

### 6. Hide Error Details

```python
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    # Don't expose internal error details in production
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

---

## Monitoring & Logging

### 1. Add Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@app.post("/reservations")
async def create_reservation(...):
    logger.info(f"Creating reservation for user {user_id}")
    try:
        # ...
    except Exception as e:
        logger.error(f"Failed to create reservation: {e}")
        raise
```

### 2. Add Monitoring

**Using Sentry** (Error tracking):

```bash
pip install sentry-sdk
```

```python
import sentry_sdk

sentry_sdk.init(
    dsn="https://your-sentry-dsn@sentry.io/project",
    traces_sample_rate=0.1
)
```

**Prometheus Metrics**:

```bash
pip install prometheus-fastapi-instrumentator
```

```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)

# Access metrics at: /metrics
```

### 3. Health Checks

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "database": "connected"  # Add DB check
    }
```

### 4. Structured Logging

```python
import json

def log_event(event_type: str, data: dict):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event": event_type,
        "data": data
    }
    print(json.dumps(log_entry))
```

---

## Troubleshooting

### Issue: Database Connection Refused

**Solution**:
```bash
# Check database URL
echo $DATABASE_URL

# Verify database is running
# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

### Issue: Migrations Not Applied

**Solution**:
```bash
# Check migration status
alembic current

# Apply all pending migrations
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt"
```

### Issue: 502 Bad Gateway

**Solution**:
- Check application logs
- Verify environment variables
- Test locally: `uvicorn app.main:app --reload`
- Check database connectivity

### Issue: Slow Queries

**Solution**:
```python
# Enable query logging
engine = create_engine(DATABASE_URL, echo=True)

# Check slow queries
# Use SQL EXPLAIN
EXPLAIN ANALYZE SELECT * FROM reservations WHERE room_id = 1;
```

### Issue: High Memory Usage

**Solution**:
```python
# Reduce worker count
gunicorn -w 2 ...

# Enable connection pooling
from sqlalchemy.pool import QueuePool
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=5
)
```

---

## Performance Optimization

### 1. Database Indexes

```sql
-- Already configured in models
-- Room queries
CREATE INDEX idx_room_name ON rooms(name);

-- Reservation queries
CREATE INDEX idx_reservation_room_date 
  ON reservations(room_id, date, status);

-- Student queries
CREATE INDEX idx_exam_student ON exams(student_id);
CREATE INDEX idx_document_student ON document_requests(student_id);
```

### 2. Connection Pooling

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,           # Connection pool size
    max_overflow=10,        # Overflow connections
    pool_recycle=3600,      # Recycle connections
    pool_pre_ping=True      # Test connections before use
)
```

### 3. Caching

```bash
pip install aioredis fastapi-cache2
```

```python
from fastapi_cache2 import FastAPICache
from fastapi_cache2.backends.redis import RedisBackend

@app.get("/rooms")
@cached(namespace="rooms", expire=600)
async def list_rooms(db: Session = Depends(get_db)):
    return db.query(Room).all()
```

### 4. Pagination

```python
@app.get("/reservations")
async def list_reservations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    reservations = db.query(Reservation)\
        .offset(skip)\
        .limit(limit)\
        .all()
    return reservations
```

---

## Continuous Integration/Deployment (CI/CD)

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run tests
        run: pytest
      
      - name: Deploy
        run: |
          # Push to deployment service
          # Example for Render: git push
          git push
```

---

## Backup Strategy

### Automated Backups

**For Render-managed PostgreSQL**:
- Automatic backups: 7 days retention

**For AWS RDS**:
```bash
# Manual backup
aws rds create-db-snapshot \
  --db-instance-identifier emsi-database \
  --db-snapshot-identifier emsi-backup-$(date +%Y-%m-%d)

# Automated: Enable automated backups in console
# Retention: 7-35 days
```

**Custom Backup Script**:
```bash
#!/bin/bash
pg_dump $DATABASE_URL > /backups/emsi_$(date +%Y%m%d_%H%M%S).sql
gzip /backups/emsi_*.sql
```

---

## Support Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/deployment/
- **Render Docs**: https://render.com/docs
- **Railway Docs**: https://docs.railway.app
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Gunicorn Docs**: https://docs.gunicorn.org/

---

## Deployment Summary

| Platform | Ease | Cost | Scalability |
|----------|------|------|-------------|
| Render | ⭐⭐⭐⭐⭐ | Free tier | Good |
| Railway | ⭐⭐⭐⭐⭐ | Free tier | Good |
| AWS | ⭐⭐⭐ | Pay-as-go | Excellent |
| Heroku | ⭐⭐⭐ | Paid | Good |
| Docker | ⭐⭐⭐⭐ | Variable | Excellent |

**Recommended**: Start with **Render** or **Railway** for ease, then migrate to AWS for scalability.

---

Your EMSI ClassFlow backend is ready for production deployment! 🚀
