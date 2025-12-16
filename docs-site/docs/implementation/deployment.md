---
sidebar_position: 3
title: Deployment Guide
---

# Deployment Guide

This guide covers deploying the Multi-RAG AI Automation Platform to various environments.

## Prerequisites

- Docker and Docker Compose
- Kubernetes cluster (for production)
- Domain name and SSL certificates
- Cloud provider account (AWS, GCP, or Azure)

## Development Deployment

### Local Docker Compose

The simplest way to run the entire stack locally:

```bash
# Start all services
docker-compose up -d

# Check service health
docker-compose ps

# View logs
docker-compose logs -f api-gateway

# Stop all services
docker-compose down
```

### Environment Configuration

Create `.env` file from template:

```bash
cp .env.example .env
# Edit .env with your configuration
```

Key environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `PINECONE_API_KEY`: Pinecone API key (or use ChromaDB locally)
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string

## Staging Deployment

### AWS ECS Deployment

1. **Build and push Docker images**:

```bash
# Build images
docker build -t multi-rag/api-governance:latest services/api-governance
docker build -t multi-rag/graphql-validator:latest services/graphql-validator
docker build -t multi-rag/log-classifier:latest services/log-classifier

# Tag for ECR
docker tag multi-rag/api-governance:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/api-governance:latest

# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/api-governance:latest
```

2. **Deploy with ECS**:

```bash
# Create task definitions
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Create or update service
aws ecs create-service --cluster multi-rag-cluster --service-name api-governance --task-definition api-governance:1 --desired-count 2
```

## Production Deployment

### Kubernetes Deployment

#### 1. Create Kubernetes Resources

**Namespace**:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: multi-rag
```

**ConfigMap**:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: multi-rag-config
  namespace: multi-rag
data:
  ENVIRONMENT: "production"
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
  RETRIEVAL_TOP_K: "20"
```

**Secrets**:
```bash
kubectl create secret generic multi-rag-secrets \
  --from-literal=OPENAI_API_KEY=<your-key> \
  --from-literal=PINECONE_API_KEY=<your-key> \
  --from-literal=DATABASE_URL=<your-url> \
  -n multi-rag
```

**Deployment**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-governance
  namespace: multi-rag
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-governance
  template:
    metadata:
      labels:
        app: api-governance
    spec:
      containers:
      - name: api-governance
        image: <your-registry>/api-governance:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: multi-rag-config
        - secretRef:
            name: multi-rag-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

**Service**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: api-governance
  namespace: multi-rag
spec:
  selector:
    app: api-governance
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

**Ingress**:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: multi-rag-ingress
  namespace: multi-rag
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.multirag.com
    secretName: multirag-tls
  rules:
  - host: api.multirag.com
    http:
      paths:
      - path: /api/v1/governance
        pathType: Prefix
        backend:
          service:
            name: api-governance
            port:
              number: 80
      - path: /api/v1/graphql
        pathType: Prefix
        backend:
          service:
            name: graphql-validator
            port:
              number: 80
      - path: /api/v1/logs
        pathType: Prefix
        backend:
          service:
            name: log-classifier
            port:
              number: 80
```

#### 2. Deploy to Kubernetes

```bash
# Apply all configurations
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/deployments/
kubectl apply -f k8s/services/
kubectl apply -f k8s/ingress.yaml

# Verify deployments
kubectl get pods -n multi-rag
kubectl get services -n multi-rag
kubectl get ingress -n multi-rag

# Check logs
kubectl logs -f deployment/api-governance -n multi-rag
```

#### 3. Set Up Auto-Scaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-governance-hpa
  namespace: multi-rag
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-governance
  minReplicas: 3
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

### Database Setup

#### PostgreSQL (RDS/Cloud SQL)

```bash
# Create database
psql -h <db-host> -U admin -d postgres -c "CREATE DATABASE multirag;"

# Run migrations
alembic upgrade head

# Verify
psql -h <db-host> -U admin -d multirag -c "\dt"
```

#### Vector Database (Pinecone)

```python
import pinecone

# Initialize Pinecone
pinecone.init(api_key="your-key", environment="us-east-1")

# Create indexes
pinecone.create_index(
    "api-governance-rules",
    dimension=3072,
    metric="cosine"
)

pinecone.create_index(
    "graphql-schemas",
    dimension=3072,
    metric="cosine"
)

pinecone.create_index(
    "log-patterns",
    dimension=3072,
    metric="cosine"
)
```

## Documentation Site Deployment

### Deploy to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to docs-site
cd docs-site

# Deploy
vercel
```

### Deploy to Netlify

```bash
# Build the site
cd docs-site
npm run build

# Deploy with Netlify CLI
netlify deploy --prod --dir=build
```

### Deploy to GitHub Pages

```bash
# Configure docusaurus.config.js
# Set organizationName and projectName

# Deploy
cd docs-site
GIT_USER=<your-github-username> npm run deploy
```

## Monitoring & Logging

### Prometheus & Grafana

```yaml
# Prometheus ServiceMonitor
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: multi-rag-metrics
  namespace: multi-rag
spec:
  selector:
    matchLabels:
      app: api-governance
  endpoints:
  - port: metrics
    path: /metrics
```

### ELK Stack

```bash
# Forward logs to Elasticsearch
kubectl apply -f k8s/fluentd-daemonset.yaml

# Access Kibana
kubectl port-forward svc/kibana 5601:5601 -n logging
```

## CI/CD Pipeline

### GitHub Actions

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v1
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v1
    
    - name: Build and push Docker image
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        IMAGE_TAG: ${{ github.sha }}
      run: |
        docker build -t $ECR_REGISTRY/api-governance:$IMAGE_TAG services/api-governance
        docker push $ECR_REGISTRY/api-governance:$IMAGE_TAG
    
    - name: Deploy to Kubernetes
      run: |
        aws eks update-kubeconfig --name multi-rag-cluster --region us-east-1
        kubectl set image deployment/api-governance api-governance=$ECR_REGISTRY/api-governance:$IMAGE_TAG -n multi-rag
```

## Health Checks

```python
# Add health check endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/ready")
async def readiness_check():
    # Check dependencies
    db_healthy = await check_database()
    redis_healthy = await check_redis()
    vector_db_healthy = await check_vector_db()
    
    if db_healthy and redis_healthy and vector_db_healthy:
        return {"status": "ready"}
    return JSONResponse(
        status_code=503,
        content={"status": "not ready"}
    )
```

## Rollback Strategy

```bash
# List deployment history
kubectl rollout history deployment/api-governance -n multi-rag

# Rollback to previous version
kubectl rollout undo deployment/api-governance -n multi-rag

# Rollback to specific revision
kubectl rollout undo deployment/api-governance -n multi-rag --to-revision=2
```

## Backup & Disaster Recovery

```bash
# PostgreSQL backup
pg_dump -h <db-host> -U admin multirag > backup_$(date +%Y%m%d).sql

# Restore
psql -h <db-host> -U admin multirag < backup_20251215.sql

# Vector DB backup (Pinecone)
# Use Pinecone backup API or export vectors
```

## Performance Tuning

- **Connection Pooling**: Configure appropriate pool sizes
- **Caching**: Use Redis for hot data
- **CDN**: Serve static assets via CloudFront/CloudFlare
- **Load Balancing**: Use ALB/NLB with health checks
- **Database Indexing**: Ensure proper indexes on frequently queried columns

## Security Checklist

- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Use secrets management (Vault/AWS Secrets Manager)
- [ ] Enable audit logging
- [ ] Set up rate limiting
- [ ] Configure CORS properly
- [ ] Regular security updates
- [ ] Penetration testing

## Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n multi-rag

# Check logs
kubectl logs <pod-name> -n multi-rag

# Get events
kubectl get events -n multi-rag --sort-by='.lastTimestamp'
```

### High Memory Usage

```bash
# Check resource usage
kubectl top pods -n multi-rag

# Increase memory limits
kubectl set resources deployment/api-governance -n multi-rag --limits=memory=4Gi
```

## Cost Optimization

- Use spot instances for non-critical workloads
- Implement auto-scaling based on metrics
- Use reserved instances for predictable workloads
- Monitor and optimize LLM API usage
- Use appropriate storage tiers

---

For more deployment options and advanced configurations, see the [Infrastructure as Code](https://github.com/your-org/multi-rag-mcp/tree/main/infrastructure) directory.
