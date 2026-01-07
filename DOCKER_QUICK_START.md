# 🚀 Docker Deployment - Quick Reference

## 📦 Files Created

### Core Docker Files
- ✅ `Dockerfile` - Backend API service (FastAPI)
- ✅ `Dockerfile.client` - Frontend UI service (Streamlit)
- ✅ `docker-compose.api-governance.yml` - Orchestration configuration
- ✅ `.dockerignore` - Files to exclude from build context
- ✅ `.env.docker` - Environment variables template

### Configuration Files
- ✅ `nginx/nginx.conf` - Reverse proxy configuration
- ✅ `deploy.sh` - Automated deployment script
- ✅ `DOCKER_DEPLOYMENT_GUIDE.md` - Complete deployment documentation

---

## ⚡ Quick Start (3 Steps)

### Step 1: Setup Environment
```bash
# Copy environment template
cp .env.docker .env

# Edit and add your OpenAI API key
nano .env
# Set: OPENAI_API_KEY=sk-your-actual-key-here
```

### Step 2: Deploy
```bash
# Option A: Using deployment script (recommended)
./deploy.sh
# Then select option 1

# Option B: Using Docker Compose directly
docker-compose -f docker-compose.api-governance.yml build
docker-compose -f docker-compose.api-governance.yml up -d
```

### Step 3: Access Services
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **UI**: http://localhost:8501

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│      Nginx (Optional Proxy)         │
│           Port 80/443               │
└──────────────┬──────────────────────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
┌─────────────┐  ┌─────────────┐
│  Backend    │  │   Client    │
│  (FastAPI)  │◄─┤ (Streamlit) │
│  Port 8000  │  │  Port 8501  │
└──────┬──────┘  └─────────────┘
       │
       ▼
┌─────────────┐
│    Redis    │
│  Port 6379  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  ChromaDB   │
│ (Persistent)│
└─────────────┘
```

---

## 🎯 Service Details

### 1. API Governance Backend
- **Container**: `api-governance-backend`
- **Port**: 8000
- **Purpose**: REST API for validation & correction
- **Health**: http://localhost:8000/health

### 2. Streamlit Client
- **Container**: `api-governance-client`
- **Port**: 8501
- **Purpose**: Web UI
- **Health**: http://localhost:8501/_stcore/health

### 3. Redis (Optional)
- **Container**: `api-governance-redis`
- **Port**: 6379
- **Purpose**: Caching & rate limiting

---

## 📝 Common Commands

```bash
# Build images
docker-compose -f docker-compose.api-governance.yml build

# Start services
docker-compose -f docker-compose.api-governance.yml up -d

# Stop services
docker-compose -f docker-compose.api-governance.yml down

# View logs
docker-compose -f docker-compose.api-governance.yml logs -f

# Check status
docker-compose -f docker-compose.api-governance.yml ps

# Restart service
docker-compose -f docker-compose.api-governance.yml restart api-governance

# Clean up
docker-compose -f docker-compose.api-governance.yml down -v
```

---

## 🧪 Testing Deployment

```bash
# Test backend health
curl http://localhost:8000/health

# Test validation endpoint
curl -X POST "http://localhost:8000/api/v1/governance/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "spec_content": "{\"openapi\":\"3.0.0\",\"info\":{\"title\":\"Test\",\"version\":\"1.0.0\"},\"paths\":{}}",
    "spec_format": "json"
  }'

# Test UI (open in browser)
open http://localhost:8501
```

---

## 🔍 Monitoring

```bash
# View all logs
docker-compose -f docker-compose.api-governance.yml logs -f

# View specific service logs
docker-compose -f docker-compose.api-governance.yml logs -f api-governance

# Check resource usage
docker stats

# Check health of all services
docker-compose -f docker-compose.api-governance.yml ps
```

---

## 🔧 Troubleshooting

### Service won't start
```bash
# Check logs
docker-compose -f docker-compose.api-governance.yml logs api-governance

# Verify environment
docker-compose -f docker-compose.api-governance.yml config

# Rebuild
docker-compose -f docker-compose.api-governance.yml build --no-cache
```

### Can't connect to API
```bash
# Check if port is available
lsof -i :8000

# Test from inside container
docker exec api-governance-backend curl http://localhost:8000/health

# Check network
docker network inspect api-governance-network
```

### ChromaDB data not persisting
```bash
# Check volume
docker volume ls | grep chroma
docker volume inspect <volume-name>

# Verify mount
docker exec api-governance-backend ls -la /app/data/chroma
```

---

## 🌟 Production Considerations

### Before Production Deployment:

1. **Security**
   - [ ] Change all default passwords
   - [ ] Set strong `SECRET_KEY` and `JWT_SECRET_KEY`
   - [ ] Enable HTTPS (SSL certificates)
   - [ ] Configure firewall rules
   - [ ] Enable rate limiting

2. **Performance**
   - [ ] Enable Redis caching
   - [ ] Configure resource limits
   - [ ] Set up monitoring (Prometheus/Grafana)
   - [ ] Configure log rotation

3. **Reliability**
   - [ ] Set up automated backups
   - [ ] Configure health checks
   - [ ] Set up alerting
   - [ ] Document disaster recovery

4. **Compliance**
   - [ ] Review security policies
   - [ ] Enable audit logging
   - [ ] Data retention policies
   - [ ] GDPR/compliance requirements

---

## 📊 Environment Variables

### Required
```env
OPENAI_API_KEY=sk-xxx          # Your OpenAI API key
```

### Recommended
```env
ENVIRONMENT=production         # Environment name
LOG_LEVEL=INFO                # Logging level
CORS_ORIGINS=https://...      # Allowed origins
ENABLE_RATE_LIMITING=true     # Enable rate limiting
```

### Optional
```env
REDIS_URL=redis://redis:6379/0
LLM_MODEL=gpt-4-turbo
CHUNK_SIZE=1000
TOP_K_RULES=20
```

---

## 📚 Additional Resources

- **Full Documentation**: See `DOCKER_DEPLOYMENT_GUIDE.md`
- **API Documentation**: http://localhost:8000/docs (when running)
- **Docker Docs**: https://docs.docker.com/
- **Docker Compose Docs**: https://docs.docker.com/compose/

---

## 🎯 Next Steps

After deployment:

1. ✅ Verify all services are healthy
2. ✅ Test validation endpoint with sample data
3. ✅ Access Streamlit UI and test workflows
4. ✅ Run data ingestion to populate ChromaDB
5. ✅ Set up monitoring and logging
6. ✅ Configure backups
7. ✅ Review security settings

---

**Need Help?** Check `DOCKER_DEPLOYMENT_GUIDE.md` for detailed instructions and troubleshooting.
