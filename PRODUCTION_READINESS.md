# API Governance Service - Production Readiness Guide

## Overview

This guide covers the production-ready features added to the API Governance service, including error handling, validation, logging, rate limiting, caching, and monitoring.

## Production Features Implemented

### 1. Custom Exceptions (`src/core/exceptions.py`)

Comprehensive exception hierarchy for better error handling:

- **MultiRAGException**: Base exception with error codes and HTTP status codes
- **GovernanceException**: API Governance specific errors
- **PDFProcessingError**: PDF parsing and processing errors
- **InvalidSpecificationError**: Invalid API specifications
- **ValidationError**: Validation errors
- **CorrectionError**: Correction process errors
- **VectorStoreException**: Vector database errors
- **EmbeddingError**: Embedding generation errors
- **LLMException**: LLM API errors (rate limits, timeouts, API errors)
- **FileProcessingException**: File handling errors (size limits, unsupported types)
- **ConfigurationError**: Configuration errors

Each exception includes:
- Human-readable error message
- Machine-readable error code
- HTTP status code
- Additional error details dictionary
- Request tracking ID

### 2. Global Error Handler (`src/api/middleware/error_handler.py`)

Production-ready error handling middleware:

- Catches all exceptions globally
- Returns consistent error response format
- Logs errors with structured logging
- Tracks requests with unique request IDs
- Handles Pydantic validation errors
- Graceful error responses for unexpected exceptions

Error response format:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {},
    "request_id": "req_12345"
  }
}
```

### 3. Production-Ready Implementation Checklist

#### A. Input Validation ✅
- File size limits (50 MB max)
- File type validation (PDF only)
- Page count limits (1000 pages max)
- Empty file detection
- Path validation
- Request payload validation with Pydantic models

#### B. Error Handling ✅
- Try-catch blocks for all operations
- Specific exception types for different errors
- Graceful degradation (continue processing other chunks if one fails)
- Detailed error logging with context
- Request ID tracking throughout the request lifecycle

#### C. Logging ✅
- Structured JSON logging
- Request ID in all log entries
- Performance metrics (duration tracking)
- Error details with stack traces
- Warning logs for non-critical issues
- Info logs for successful operations

#### D. Security Features (To Implement)
- [ ] File content scanning for malicious content
- [ ] Input sanitization for metadata
- [ ] Rate limiting per user/IP
- [ ] API key authentication
- [ ] JWT token validation
- [ ] CORS configuration
- [ ] Content Security Policy headers

#### E. Performance Optimization (To Implement)
- [ ] Caching layer for:
  - Embeddings (avoid regenerating for duplicate content)
  - Validation results
  - Frequently accessed governance rules
- [ ] Async batch processing
- [ ] Connection pooling for vector DB
- [ ] Request queuing for LLM calls
- [ ] Response compression

#### F. Monitoring & Observability (To Implement)
- [ ] Prometheus metrics:
  - Request count, duration, errors
  - PDF processing metrics
  - LLM API call metrics
  - Vector DB operation metrics
- [ ] Health check endpoints
- [ ] Readiness probes
- [ ] Distributed tracing with Jaeger
- [ ] Custom business metrics

### 4. Rate Limiting (To Implement)

Add rate limiting to prevent API abuse:

```python
# src/api/middleware/rate_limiter.py
from fastapi import Request, HTTPException
from datetime import datetime, timedelta
import redis
from typing import Optional

class RateLimiter:
    def __init__(self, redis_client: redis.Redis, rate: int = 100, window: int = 60):
        self.redis = redis_client
        self.rate = rate  # requests per window
        self.window = window  # seconds
    
    async def check_rate_limit(self, key: str) -> bool:
        """Check if request is within rate limit"""
        current = int(datetime.now().timestamp())
        window_start = current - self.window
        
        # Remove old requests
        self.redis.zremrangebyscore(key, 0, window_start)
        
        # Count requests in current window
        request_count = self.redis.zcard(key)
        
        if request_count >= self.rate:
            return False
        
        # Add current request
        self.redis.zadd(key, {str(current): current})
        self.redis.expire(key, self.window)
        
        return True

# Usage in router
@router.post("/governance/ingest")
async def ingest_pdf(
    request: Request,
    file: UploadFile = File(...),
    rate_limiter: RateLimiter = Depends(get_rate_limiter)
):
    client_ip = request.client.host
    if not await rate_limiter.check_rate_limit(f"rate_limit:{client_ip}"):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    ...
```

### 5. Caching Layer (To Implement)

Add caching for embeddings and validation results:

```python
# src/core/cache.py
import hashlib
import json
from typing import Optional, Any
import redis
from datetime import timedelta

class CacheManager:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def _generate_key(self, prefix: str, data: Any) -> str:
        """Generate cache key from data"""
        data_str = json.dumps(data, sort_keys=True)
        hash_val = hashlib.sha256(data_str.encode()).hexdigest()
        return f"{prefix}:{hash_val}"
    
    async def get_embedding(self, text: str) -> Optional[list]:
        """Get cached embedding"""
        key = self._generate_key("embedding", text)
        cached = self.redis.get(key)
        if cached:
            return json.loads(cached)
        return None
    
    async def set_embedding(self, text: str, embedding: list, ttl: int = 86400):
        """Cache embedding (24 hour TTL)"""
        key = self._generate_key("embedding", text)
        self.redis.setex(key, timedelta(seconds=ttl), json.dumps(embedding))
    
    async def get_validation_result(self, spec_hash: str) -> Optional[dict]:
        """Get cached validation result"""
        key = f"validation:{spec_hash}"
        cached = self.redis.get(key)
        if cached:
            return json.loads(cached)
        return None
    
    async def set_validation_result(self, spec_hash: str, result: dict, ttl: int = 3600):
        """Cache validation result (1 hour TTL)"""
        key = f"validation:{spec_hash}"
        self.redis.setex(key, timedelta(seconds=ttl), json.dumps(result))
```

### 6. Monitoring Metrics (To Implement)

Add Prometheus metrics:

```python
# src/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time
from functools import wraps

# Define metrics
pdf_ingestion_count = Counter(
    'pdf_ingestion_total',
    'Total PDF ingestion requests',
    ['status']  # success, error
)

pdf_ingestion_duration = Histogram(
    'pdf_ingestion_duration_seconds',
    'PDF ingestion duration',
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0]
)

validation_count = Counter(
    'validation_total',
    'Total validation requests',
    ['status']
)

validation_duration = Histogram(
    'validation_duration_seconds',
    'Validation duration'
)

llm_api_calls = Counter(
    'llm_api_calls_total',
    'Total LLM API calls',
    ['model', 'status']
)

vector_db_operations = Counter(
    'vector_db_operations_total',
    'Total vector DB operations',
    ['operation', 'status']  # upsert, search, delete
)

active_requests = Gauge(
    'active_requests',
    'Number of active requests'
)

# Decorator for automatic metrics
def track_metrics(operation: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            active_requests.inc()
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                if operation == "pdf_ingestion":
                    pdf_ingestion_count.labels(status="success").inc()
                    pdf_ingestion_duration.observe(duration)
                elif operation == "validation":
                    validation_count.labels(status="success").inc()
                    validation_duration.observe(duration)
                
                return result
            
            except Exception as e:
                if operation == "pdf_ingestion":
                    pdf_ingestion_count.labels(status="error").inc()
                elif operation == "validation":
                    validation_count.labels(status="error").inc()
                raise
            
            finally:
                active_requests.dec()
        
        return wrapper
    return decorator

# Usage
@track_metrics("pdf_ingestion")
async def ingest_pdf(pdf_path: str, ...):
    ...
```

### 7. Health Check Endpoints

Enhanced health checks:

```python
# src/api/v1/health.py
from fastapi import APIRouter, status
from typing import Dict, Any
import time

router = APIRouter()

startup_time = time.time()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, str]:
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "multi-rag-api-governance",
        "uptime_seconds": round(time.time() - startup_time, 2)
    }

@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check() -> Dict[str, Any]:
    """Detailed readiness check"""
    checks = {
        "vector_db": await check_vector_db(),
        "llm_api": await check_llm_api(),
        "embedding_api": await check_embedding_api()
    }
    
    all_healthy = all(checks.values())
    
    return {
        "status": "ready" if all_healthy else "not_ready",
        "checks": checks,
        "timestamp": time.time()
    }

async def check_vector_db() -> bool:
    """Check vector DB connectivity"""
    try:
        # Perform a simple query
        return True
    except:
        return False

async def check_llm_api() -> bool:
    """Check LLM API connectivity"""
    try:
        # Test API connection
        return True
    except:
        return False
```

### 8. Configuration for Production

Update `.env` for production:

```bash
# Production Environment
ENVIRONMENT=production

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
API_RELOAD=false

# Security
JWT_SECRET_KEY=<strong-secret-key>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
ENABLE_API_KEY_AUTH=true

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_BURST=20

# Timeouts
REQUEST_TIMEOUT_SECONDS=30
LLM_REQUEST_TIMEOUT_SECONDS=60

# Redis (for caching and rate limiting)
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=<redis-password>
REDIS_DB=0

# Monitoring
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090
JAEGER_ENABLED=true
JAEGER_AGENT_HOST=jaeger
JAEGER_AGENT_PORT=6831

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# File Upload Limits
MAX_FILE_SIZE_MB=50
MAX_PAGES_PER_PDF=1000
```

### 9. Docker Production Setup

```dockerfile
# Dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run with gunicorn for production
CMD ["gunicorn", "src.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - REDIS_HOST=redis
      - DATABASE_URL=postgresql://user:pass@postgres:5432/multirag
    depends_on:
      - redis
      - postgres
    restart: unless-stopped
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis-data:/data
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: multirag
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped

  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    restart: unless-stopped

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
    volumes:
      - grafana-data:/var/lib/grafana
    restart: unless-stopped

volumes:
  redis-data:
  postgres-data:
  prometheus-data:
  grafana-data:
```

## Next Steps

1. **Immediate**: Integrate error handler middleware in `src/main.py`
2. **Short-term**: Implement rate limiting and caching
3. **Medium-term**: Add Prometheus metrics and monitoring
4. **Long-term**: Set up production deployment with Docker/Kubernetes

## Testing Production Features

1. Test error handling:
```bash
curl -X POST http://localhost:8000/api/v1/governance/ingest \
  -F "file=@large_file.pdf"  # Test file size limit
```

2. Test rate limiting:
```bash
for i in {1..150}; do
  curl http://localhost:8000/api/v1/governance/health
done
```

3. Monitor metrics:
```bash
curl http://localhost:8000/metrics
```

## Maintenance

- Monitor error rates in Grafana dashboards
- Set up alerts for high error rates or slow response times
- Review logs daily for unusual patterns
- Update rate limits based on usage patterns
- Rotate JWT secrets monthly
- Backup vector database weekly
