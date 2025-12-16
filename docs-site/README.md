# Multi-RAG Documentation Site

This directory contains the Docusaurus-based documentation website for the Multi-RAG AI Automation Platform.

## Installation

```bash
npm install
```

## Local Development

```bash
npm start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

## Build

```bash
npm run build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.

## Deployment

### Using GitHub Pages

```bash
GIT_USER=<Your GitHub username> npm run deploy
```

### Using Vercel

1. Push your code to GitHub
2. Import your repository in Vercel
3. Vercel will automatically detect Docusaurus and deploy

### Using Netlify

1. Push your code to GitHub
2. Connect your repository to Netlify
3. Set build command: `npm run build`
4. Set publish directory: `build`

## Project Structure

```
docs-site/
├── docs/                          # Documentation pages (markdown)
│   ├── intro.md
│   ├── getting-started.md
│   ├── architecture/
│   ├── api-governance/
│   ├── graphql-validator/
│   ├── log-classifier/
│   ├── implementation/
│   ├── api-reference/
│   └── guides/
├── src/
│   ├── components/                # React components
│   ├── css/                       # Custom CSS
│   └── pages/                     # Custom pages
├── static/                        # Static assets (images, files)
│   └── img/
├── docusaurus.config.js          # Docusaurus configuration
├── sidebars.js                   # Sidebar configuration
└── package.json
```

## Configuration

- **docusaurus.config.js**: Main configuration file
- **sidebars.js**: Navigation sidebar structure
- **src/css/custom.css**: Custom styling

## Documentation Guidelines

### Adding a New Page

1. Create a markdown file in the appropriate `docs/` subdirectory
2. Add frontmatter:
```markdown
---
sidebar_position: 1
title: Your Page Title
---

# Your Page Title

Your content here...
```

3. Update `sidebars.js` if needed

### Code Blocks

Use code blocks with language specification:

\```python
def hello_world():
    print("Hello, World!")
\```

### Admonitions

Use admonitions for notes, tips, warnings:

```markdown
:::note
This is a note
:::

:::tip
This is a tip
:::

:::warning
This is a warning
:::

:::danger
This is dangerous
:::
```

## Learn More

- [Docusaurus Documentation](https://docusaurus.io/)
- [Markdown Features](https://docusaurus.io/docs/markdown-features)
- [Deployment](https://docusaurus.io/docs/deployment)
