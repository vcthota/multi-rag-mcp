# Multi-RAG Documentation Site - Quick Start

To get the documentation site running locally:

## 1. Install Dependencies

```bash
cd docs-site
npm install
```

## 2. Start Development Server

```bash
npm start
```

The site will open at http://localhost:3000

## 3. Build for Production

```bash
npm run build
```

## 4. Deploy

Choose your deployment method:

### Vercel (Recommended)
```bash
npm install -g vercel
vercel
```

### Netlify
```bash
npm run build
netlify deploy --prod --dir=build
```

### GitHub Pages
```bash
GIT_USER=<your-username> npm run deploy
```

## Documentation Structure

All documentation files are in the `docs/` directory with the following structure:

```
docs/
├── intro.md                          # Home page
├── getting-started.md                # Quick start guide
├── architecture/
│   └── overview.md                   # System architecture
├── api-governance/
│   └── overview.md                   # API Governance design
├── graphql-validator/
│   └── overview.md                   # GraphQL Validator design
├── log-classifier/
│   └── overview.md                   # Log Classifier design
└── implementation/
    ├── roadmap.md                    # Implementation roadmap
    ├── database-schema.md            # Database schemas
    └── deployment.md                 # Deployment guide
```

All original markdown files from `/docs` have been migrated to `/docs-site/docs` with proper Docusaurus frontmatter.

For more details, see `/docs-site/README.md`
