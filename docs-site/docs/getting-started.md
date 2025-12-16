---
sidebar_position: 2
---

# Getting Started

This guide will help you get the Multi-RAG AI Automation Platform up and running on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** 18+ and npm
- **Python** 3.11+
- **Docker** and Docker Compose
- **Git**

### API Keys Required

You'll need API keys for:
- **OpenAI API** (for GPT-4 and embeddings)
- **Pinecone** (for vector database) - or use ChromaDB locally

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/multi-rag-mcp.git
cd multi-rag-mcp
```

### 2. Set Up Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
# LLM Configuration
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview

# Vector Database
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=us-east-1

# Or use ChromaDB locally
CHROMA_HOST=localhost
CHROMA_PORT=8000
```

### 3. Start Infrastructure Services

Start PostgreSQL, Redis, ChromaDB, Kafka, and other services:

```bash
docker-compose up -d
```

Verify all services are running:

```bash
docker-compose ps
```

You should see:
- ✅ postgres (port 5432)
- ✅ redis (port 6379)
- ✅ chromadb (port 8000)
- ✅ kafka (port 9092)
- ✅ elasticsearch (port 9200)

### 4. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Run Database Migrations

```bash
# Create database tables
alembic upgrade head
```

### 6. Start the API Server

```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Quick Test

### Test API Governance Service

```bash
# Upload a governance specification
curl -X POST "http://localhost:8000/api/v1/governance/ingest" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@governance-rules.pdf"

# Validate an API specification
curl -X POST "http://localhost:8000/api/v1/governance/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "specification": {
      "openapi": "3.0.0",
      "paths": {
        "/userProfile": {
          "get": {
            "summary": "Get user profile"
          }
        }
      }
    }
  }'
```

### Test GraphQL Validator

```bash
# Validate a GraphQL schema
curl -X POST "http://localhost:8000/api/v1/graphql/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "schema": "type Query { user(id: ID!): User } type User { id: ID! name: String! }"
  }'
```

### Test Log Classifier

```bash
# Send a log entry for classification
curl -X POST "http://localhost:8000/api/v1/logs/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2025-12-15T10:30:00Z",
    "level": "ERROR",
    "service": "api-gateway",
    "message": "Failed to connect to database: Connection timeout after 5000 ms",
    "environment": "production"
  }'
```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/unit/api_governance/
pytest tests/integration/

# With coverage report
pytest --cov=services --cov-report=html
open htmlcov/index.html
```

### Code Quality

```bash
# Format code
black services/
ruff check services/ --fix

# Type checking
mypy services/

# Run pre-commit hooks
pre-commit run --all-files
```

### Hot Reload Development

The FastAPI server automatically reloads when you change Python files. For frontend/docs:

```bash
# In docs-site directory
npm start
```

## Accessing Services

Once everything is running:

| Service | URL | Description |
|---------|-----|-------------|
| API Server | http://localhost:8000 | Main API |
| API Docs | http://localhost:8000/docs | Interactive API documentation |
| Documentation Site | http://localhost:3000 | This documentation |
| Kibana | http://localhost:5601 | Log visualization |
| Prometheus | http://localhost:9090 | Metrics |
| Grafana | http://localhost:3000 | Dashboards |

## Troubleshooting

### Common Issues

#### Port Already in Use

If a port is already in use:

```bash
# Find process using port
lsof -i :8000  # or any port number

# Kill process
kill -9 <PID>
```

#### Docker Services Not Starting

```bash
# Check logs
docker-compose logs postgres
docker-compose logs redis

# Restart services
docker-compose restart

# Clean start
docker-compose down -v
docker-compose up -d
```

#### OpenAI API Rate Limits

If you hit rate limits:
- Use a higher tier API key
- Implement request queuing
- Add retry logic with exponential backoff

#### Vector DB Connection Issues

For ChromaDB:
```bash
# Check if ChromaDB is running
curl http://localhost:8000/api/v1/heartbeat

# Restart ChromaDB
docker-compose restart chromadb
```

For Pinecone:
- Verify API key is correct
- Check Pinecone environment/region
- Ensure index is created

## Next Steps

Now that you have the platform running:

1. **Explore the Architecture**: Learn about the [system architecture](/docs/architecture/overview)
2. **Try Each Service**: Follow the service-specific guides
   - [API Governance Guide](/docs/api-governance/overview)
   - [GraphQL Validator Guide](/docs/graphql-validator/overview)
   - [Log Classifier Guide](/docs/log-classifier/overview)
3. **Configure for Production**: See [Deployment Guide](/docs/implementation/deployment)
4. **Review Best Practices**: Check [Best Practices](/docs/guides/best-practices)

## Resources

- [Implementation Roadmap](/docs/implementation/roadmap)
- [API Reference](/docs/api-reference/authentication)
- [Configuration Guide](/docs/guides/configuration)
- [Troubleshooting Guide](/docs/guides/troubleshooting)

---

**Need help?** Check the [Troubleshooting Guide](/docs/guides/troubleshooting) or open an issue on GitHub.
