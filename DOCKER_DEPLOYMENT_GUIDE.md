# 🐳 Docker Deployment Guide - API Governance Service

## 📋 Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Production Deployment](#production-deployment)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

### Required Software
- **Docker**: Version 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose**: Version 2.0+ ([Install Docker Compose](https://docs.docker.com/compose/install/))
- **Git**: For cloning the repository

### Required API Keys
- **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)

### System Requirements
- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 10GB free space
- **Ports**: 8000, 8501, 6379, 80 (optional: 443 for HTTPS)

---

## 🚀 Quick Start (Development)

### Step 1: Clone Repository
```bash
git clone <your-repo-url>
cd multi-rag-mcp
```

### Step 2: Configure Environment
```bash
# Copy environment template
cp .env.docker .env

# Edit .env file and add your OpenAI API key
nano .env  # or use your preferred editor
```

**Required: Update these values in `.env`:**
```env
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

### Step 3: Build and Run
```bash
# Build all services
docker-compose -f docker-compose.api-governance.yml build

# Start all services
docker-compose -f docker-compose.api-governance.yml up -d

# Check service status
docker-compose -f docker-compose.api-governance.yml ps
```

### Step 4: Verify Deployment
```bash
# Check API health
curl http://localhost:8000/health

# Check logs
docker-compose -f docker-compose.api-governance.yml logs -f api-governance
```

### Step 5: Access Services
- **API Backend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Streamlit UI**: http://localhost:8501
- **Redis**: localhost:6379

---

## 📦 Detailed Setup

### Architecture Overview
```
┌─────────────────────────────────────────────┐
│           Nginx (Port 80/443)               │
│         Reverse Proxy + Load Balancer       │
└───────────────┬─────────────────────────────┘
                │
        ┌───────┴────────┐
        │                │
        ▼                ▼
┌──────────────┐  ┌──────────────┐
│   Backend    │  │   Client     │
│   (FastAPI)  │  │ (Streamlit)  │
│   Port 8000  │  │  Port 8501   │
└──────┬───────┘  └──────────────┘
       │
       ▼
┌──────────────┐
│    Redis     │
│  Port 6379   │
└──────────────┘
       │
       ▼
┌──────────────┐
│   ChromaDB   │
│ (Local File) │
└──────────────┘
```

### Service Breakdown

#### 1. **API Governance Backend**
- **Container**: `api-governance-backend`
- **Image**: Custom (built from Dockerfile)
- **Port**: 8000
- **Purpose**: REST API for validation and correction
- **Dependencies**: Redis (optional), ChromaDB data

#### 2. **Streamlit Client**
- **Container**: `api-governance-client`
- **Image**: Custom (built from Dockerfile.client)
- **Port**: 8501
- **Purpose**: Web UI for API governance
- **Dependencies**: Backend API

#### 3. **Redis**
- **Container**: `api-governance-redis`
- **Image**: redis:7-alpine
- **Port**: 6379
- **Purpose**: Caching and rate limiting
- **Optional**: Can be disabled in development

#### 4. **Nginx** (Optional - Production)
- **Container**: `api-governance-nginx`
- **Image**: nginx:alpine
- **Ports**: 80, 443
- **Purpose**: Reverse proxy, SSL termination, load balancing

---

## 🔐 Environment Configuration

### Essential Variables

```env
# Required
OPENAI_API_KEY=sk-xxx                    # Your OpenAI API key
ENVIRONMENT=production                    # production|development|staging
LOG_LEVEL=INFO                           # DEBUG|INFO|WARNING|ERROR

# Vector Database
VECTOR_DB_TYPE=chromadb                  # chromadb|pinecone
CHROMA_PERSIST_DIRECTORY=/app/data/chroma

# API Settings
API_V1_PREFIX=/api/v1
CORS_ORIGINS=http://localhost:8501      # Comma-separated list
```

### Optional Variables

```env
# Rate Limiting (requires Redis)
ENABLE_RATE_LIMITING=true
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# LLM Configuration
LLM_MODEL=gpt-4-turbo
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=4000
```

---

## 🏭 Production Deployment

### Step 1: Prepare Environment

```bash
# Create production environment file
cp .env.docker .env.production

# Update with production values
nano .env.production
```

**Production Checklist:**
- ✅ Set `ENVIRONMENT=production`
- ✅ Use strong `SECRET_KEY` and `JWT_SECRET_KEY`
- ✅ Enable rate limiting: `ENABLE_RATE_LIMITING=true`
- ✅ Configure proper CORS origins
- ✅ Set appropriate log level: `LOG_LEVEL=WARNING`
- ✅ Review and update all sensitive credentials

### Step 2: Build Production Images

```bash
# Build with production optimizations
docker-compose -f docker-compose.api-governance.yml build --no-cache

# Tag images for registry
docker tag api-governance-backend:latest your-registry/api-governance-backend:v1.0.0
docker tag api-governance-client:latest your-registry/api-governance-client:v1.0.0
```

### Step 3: Deploy with Nginx

```bash
# Start all services including Nginx
docker-compose -f docker-compose.api-governance.yml --profile production up -d

# Verify all services are running
docker-compose -f docker-compose.api-governance.yml ps
```

### Step 4: Setup SSL/TLS (Optional)

```bash
# Create SSL directory
mkdir -p nginx/ssl

# Generate self-signed certificate (for testing)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem

# For production, use Let's Encrypt:
# certbot certonly --standalone -d your-domain.com
# cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
# cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem

# Restart Nginx
docker-compose -f docker-compose.api-governance.yml restart nginx
```

### Step 5: Verify Production Deployment

```bash
# Test API endpoint
curl https://your-domain.com/api/v1/governance/health

# Check all service logs
docker-compose -f docker-compose.api-governance.yml logs

# Monitor resource usage
docker stats
```

---

## 📊 Monitoring & Maintenance

### Health Checks

```bash
# Check all service health
docker-compose -f docker-compose.api-governance.yml ps

# Individual service health
curl http://localhost:8000/health        # Backend
curl http://localhost:8501/_stcore/health # Client

# Redis health
docker exec api-governance-redis redis-cli ping
```

### View Logs

```bash
# All services
docker-compose -f docker-compose.api-governance.yml logs -f

# Specific service
docker-compose -f docker-compose.api-governance.yml logs -f api-governance

# Last 100 lines
docker-compose -f docker-compose.api-governance.yml logs --tail=100 api-governance
```

### Backup Data

```bash
# Backup ChromaDB data
docker run --rm -v multi-rag-mcp_chroma_data:/data -v $(pwd)/backups:/backup \
  alpine tar czf /backup/chroma-backup-$(date +%Y%m%d).tar.gz -C /data .

# Backup Redis data
docker exec api-governance-redis redis-cli SAVE
docker cp api-governance-redis:/data/dump.rdb ./backups/redis-backup-$(date +%Y%m%d).rdb
```

### Update Deployment

```bash
# Pull latest code
git pull origin main

# Rebuild images
docker-compose -f docker-compose.api-governance.yml build

# Restart services with zero downtime
docker-compose -f docker-compose.api-governance.yml up -d --force-recreate
```

### Scale Services

```bash
# Scale backend service (if using load balancer)
docker-compose -f docker-compose.api-governance.yml up -d --scale api-governance=3

# Verify scaling
docker-compose -f docker-compose.api-governance.yml ps
```

---

## 🐛 Troubleshooting

### Issue 1: Container Won't Start

```bash
# Check container status
docker-compose -f docker-compose.api-governance.yml ps

# View container logs
docker-compose -f docker-compose.api-governance.yml logs api-governance

# Check for port conflicts
lsof -i :8000
lsof -i :8501

# Inspect container
docker inspect api-governance-backend
```

### Issue 2: OpenAI API Key Error

```bash
# Verify environment variable
docker exec api-governance-backend env | grep OPENAI

# Check .env file is loaded
docker-compose -f docker-compose.api-governance.yml config

# Restart with new environment
docker-compose -f docker-compose.api-governance.yml down
docker-compose -f docker-compose.api-governance.yml up -d
```

### Issue 3: ChromaDB Data Not Persisting

```bash
# Check volume exists
docker volume ls | grep chroma

# Inspect volume
docker volume inspect <volume-name>

# Verify mount point in container
docker exec api-governance-backend ls -la /app/data/chroma
```

### Issue 4: Service Communication Failure

```bash
# Check network
docker network ls
docker network inspect api-governance-network

# Test connectivity
docker exec api-governance-client ping api-governance
docker exec api-governance-backend ping redis

# Check DNS resolution
docker exec api-governance-client nslookup api-governance
```

### Issue 5: High Memory Usage

```bash
# Check resource usage
docker stats

# Limit memory for services (add to docker-compose.yml):
# deploy:
#   resources:
#     limits:
#       memory: 2G
#     reservations:
#       memory: 1G

# Restart with limits
docker-compose -f docker-compose.api-governance.yml up -d
```

---

## 🛠️ Common Commands Reference

```bash
# Start services
docker-compose -f docker-compose.api-governance.yml up -d

# Stop services
docker-compose -f docker-compose.api-governance.yml down

# Stop and remove volumes
docker-compose -f docker-compose.api-governance.yml down -v

# Rebuild and restart
docker-compose -f docker-compose.api-governance.yml up -d --build

# View logs
docker-compose -f docker-compose.api-governance.yml logs -f

# Execute command in container
docker exec -it api-governance-backend bash

# Check service status
docker-compose -f docker-compose.api-governance.yml ps

# Remove unused images
docker image prune -a

# Clean up everything
docker system prune -a --volumes
```

---

## 📝 Testing the Deployment

### 1. Test Backend API

```bash
# Health check
curl http://localhost:8000/health

# Test validation endpoint
curl -X POST "http://localhost:8000/api/v1/governance/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "spec_content": "{\"openapi\": \"3.0.0\", \"info\": {\"title\": \"Test\", \"version\": \"1.0.0\"}, \"paths\": {}}",
    "spec_format": "json"
  }'
```

### 2. Test Streamlit UI

```bash
# Open in browser
open http://localhost:8501

# Or check health
curl http://localhost:8501/_stcore/health
```

### 3. Test with Sample Data

```bash
# Run ingestion (from inside container)
docker exec -it api-governance-backend python run_ingestion.py

# Test retrieval
docker exec -it api-governance-backend python retrieve_rules.py "API versioning"
```

---

## 🔒 Security Best Practices

1. **Never commit `.env` files with real credentials**
2. **Use Docker secrets for sensitive data in production**
3. **Enable rate limiting with Redis**
4. **Use HTTPS in production (Nginx + SSL)**
5. **Regularly update base images**
6. **Run containers as non-root user**
7. **Scan images for vulnerabilities**: `docker scan api-governance-backend`
8. **Implement network policies**
9. **Use read-only file systems where possible**
10. **Enable Docker Content Trust**: `export DOCKER_CONTENT_TRUST=1`

---

## 📞 Support

For issues or questions:
- Check logs: `docker-compose logs`
- Review health checks: `/health` and `/_stcore/health`
- Inspect containers: `docker inspect <container-name>`
- Check GitHub issues or documentation

---

## 📄 License

See LICENSE file for details.

---

**Last Updated**: December 2025
