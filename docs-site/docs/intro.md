---
sidebar_position: 1
slug: /
---

# Multi-RAG AI Automation Platform

Welcome to the **Multi-RAG AI Automation Platform** documentation! This platform consolidates three powerful AI-driven services into one unified solution.

## 🎯 What is Multi-RAG?

Multi-RAG is an AI automation platform that uses **Retrieval-Augmented Generation (RAG)** architecture to provide intelligent automation across three critical domains:

### 1. 🔍 API Governance Assistant
Automatically validates API specifications against governance rules and provides intelligent corrections.

- **PDF Governance Ingestion**: Upload governance specifications
- **Real-time Validation**: Validate OpenAPI/Swagger specs
- **Auto-Correction**: AI-powered specification fixes
- **Compliance Reporting**: Detailed violation reports

[Learn more →](/docs/api-governance/overview)

### 2. 📊 GraphQL Schema Validator
Validates GraphQL schemas, performs linting, and generates centralized supergraph documentation.

- **Schema Validation**: Syntax and semantic checks
- **Smart Linting**: Configurable rules with auto-fix
- **Federation Support**: Apollo Federation composition
- **Documentation Generation**: AI-enhanced docs

[Learn more →](/docs/graphql-validator/overview)

### 3. 📈 Real-Time Log Classifier
Intelligent log pattern matching with severity-based alerting and continuous learning.

- **Multi-Source Ingestion**: DataDog, Splunk, CloudWatch
- **Pattern Matching**: Vector similarity search
- **Real-Time Classification**: AI-powered classification
- **Smart Alerting**: Severity-based notifications

[Learn more →](/docs/log-classifier/overview)

## ✨ Key Features

- **🤖 AI-Powered**: Leverages GPT-4 and advanced embeddings
- **🔄 Continuous Learning**: Automatically improves from new data
- **⚡ Real-Time Processing**: Sub-second response times
- **📊 Vector Search**: Fast similarity matching with 85%+ accuracy
- **🔒 Secure**: JWT authentication, RBAC, encryption
- **📈 Scalable**: Kubernetes-ready, auto-scaling

## 🚀 Quick Start

Get started in minutes:

```bash
# Clone the repository
git clone <repo-url>
cd multi-rag-mcp

# Start development environment
docker-compose up -d

# Install dependencies
cd docs-site
npm install

# Start the documentation site
npm start
```

Visit `http://localhost:3000` to view the docs.

## 📚 Documentation Structure

<div className="container">
  <div className="row">
    <div className="col col--6">
      <h3>🏗️ Architecture</h3>
      <ul>
        <li><a href="/docs/architecture/overview">System Overview</a></li>
        <li><a href="/docs/architecture/technology-stack">Technology Stack</a></li>
        <li><a href="/docs/architecture/data-flow">Data Flow</a></li>
      </ul>
    </div>
    <div className="col col--6">
      <h3>🛠️ Implementation</h3>
      <ul>
        <li><a href="/docs/implementation/roadmap">Implementation Roadmap</a></li>
        <li><a href="/docs/implementation/database-schema">Database Schema</a></li>
        <li><a href="/docs/implementation/deployment">Deployment Guide</a></li>
      </ul>
    </div>
  </div>
  <div className="row">
    <div className="col col--6">
      <h3>🔌 API Reference</h3>
      <ul>
        <li><a href="/docs/api-reference/authentication">Authentication</a></li>
        <li><a href="/docs/api-reference/api-governance-api">API Governance API</a></li>
        <li><a href="/docs/api-reference/graphql-validator-api">GraphQL Validator API</a></li>
        <li><a href="/docs/api-reference/log-classifier-api">Log Classifier API</a></li>
      </ul>
    </div>
    <div className="col col--6">
      <h3>📖 Guides</h3>
      <ul>
        <li><a href="/docs/guides/quick-start">Quick Start Guide</a></li>
        <li><a href="/docs/guides/configuration">Configuration</a></li>
        <li><a href="/docs/guides/best-practices">Best Practices</a></li>
        <li><a href="/docs/guides/troubleshooting">Troubleshooting</a></li>
      </ul>
    </div>
  </div>
</div>

## 🛣️ Implementation Timeline

| Phase | Duration | Milestone |
|-------|----------|-----------|
| Foundation | Weeks 1-3 | Infrastructure setup |
| API Governance | Weeks 4-6 | Service MVP |
| GraphQL Validator | Weeks 7-9 | Service MVP |
| Log Classifier | Weeks 10-13 | Service MVP |
| Integration | Weeks 14-17 | Unified platform |
| Production | Weeks 18-22 | Launch |

[View full roadmap →](/docs/implementation/roadmap)

## 💡 Why Multi-RAG?

### Traditional Approach
- Manual API spec validation
- Static GraphQL linting
- Reactive log monitoring
- Separate tools for each task

### Multi-RAG Approach
- ✅ AI-powered automated validation
- ✅ Intelligent auto-correction
- ✅ Proactive pattern learning
- ✅ Unified platform with shared intelligence

## 🎓 Learning Path

### 1. Beginners
Start with these documents:
- [Getting Started](/docs/getting-started)
- [Architecture Overview](/docs/architecture/overview)
- [Quick Start Guide](/docs/guides/quick-start)

### 2. Developers
Deep dive into implementation:
- [Implementation Roadmap](/docs/implementation/roadmap)
- [API Reference](/docs/api-reference/authentication)
- Service-specific guides

### 3. Architects
Understand the system design:
- [System Architecture](/docs/architecture/overview)
- [Technology Stack](/docs/architecture/technology-stack)
- [Database Schema](/docs/implementation/database-schema)

## 🤝 Support

Need help? Here's how to get support:

- 📖 **Documentation**: You're here! Browse the docs
- 💬 **GitHub Issues**: Report bugs or request features
- 📧 **Email**: support@multirag.com
- 💡 **Community**: Join our Slack channel

## 📦 What's Next?

<div className="container">
  <div className="row">
    <div className="col col--4">
      <div className="card">
        <div className="card__header">
          <h3>🚀 Get Started</h3>
        </div>
        <div className="card__body">
          <p>Set up your development environment and run your first validation</p>
        </div>
        <div className="card__footer">
          <a href="/docs/getting-started" className="button button--primary button--block">Start Now</a>
        </div>
      </div>
    </div>
    <div className="col col--4">
      <div className="card">
        <div className="card__header">
          <h3>🏗️ Architecture</h3>
        </div>
        <div className="card__body">
          <p>Explore the system design, components, and data flows</p>
        </div>
        <div className="card__footer">
          <a href="/docs/architecture/overview" className="button button--secondary button--block">Learn More</a>
        </div>
      </div>
    </div>
    <div className="col col--4">
      <div className="card">
        <div className="card__header">
          <h3>📡 API Reference</h3>
        </div>
        <div className="card__body">
          <p>Complete API documentation with examples and code snippets</p>
        </div>
        <div className="card__footer">
          <a href="/docs/api-reference/authentication" className="button button--secondary button--block">View APIs</a>
        </div>
      </div>
    </div>
  </div>
</div>

---

**Ready to automate?** Start with the [Getting Started Guide](/docs/getting-started) →
