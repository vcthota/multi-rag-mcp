// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require('prism-react-renderer').themes.github;
const darkCodeTheme = require('prism-react-renderer').themes.dracula;

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Multi-RAG AI Automation Platform',
  tagline: 'Unified AI automation for API governance, GraphQL validation, and log classification',
  favicon: 'img/favicon.ico',

  // Set the production url of your site here
  url: 'https://your-domain.com',
  // Set the /<baseUrl>/ pathname under which your site is served
  baseUrl: '/',

  // GitHub pages deployment config.
  organizationName: 'your-org',
  projectName: 'multi-rag-mcp',

  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/your-org/multi-rag-mcp/tree/main/docs-site/',
        },
        blog: {
          showReadingTime: true,
          editUrl: 'https://github.com/your-org/multi-rag-mcp/tree/main/docs-site/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      image: 'img/social-card.png',
      navbar: {
        title: 'Multi-RAG Platform',
        logo: {
          alt: 'Multi-RAG Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Documentation',
          },
          {
            to: '/docs/api-governance/overview',
            label: 'API Governance',
            position: 'left',
          },
          {
            to: '/docs/graphql-validator/overview',
            label: 'GraphQL Validator',
            position: 'left',
          },
          {
            to: '/docs/log-classifier/overview',
            label: 'Log Classifier',
            position: 'left',
          },
          {
            href: 'https://github.com/your-org/multi-rag-mcp',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Documentation',
            items: [
              {
                label: 'Getting Started',
                to: '/docs/getting-started',
              },
              {
                label: 'Architecture',
                to: '/docs/architecture/overview',
              },
              {
                label: 'Implementation',
                to: '/docs/implementation/roadmap',
              },
            ],
          },
          {
            title: 'Services',
            items: [
              {
                label: 'API Governance',
                to: '/docs/api-governance/overview',
              },
              {
                label: 'GraphQL Validator',
                to: '/docs/graphql-validator/overview',
              },
              {
                label: 'Log Classifier',
                to: '/docs/log-classifier/overview',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/your-org/multi-rag-mcp',
              },
              {
                label: 'API Reference',
                to: '/docs/api-reference',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Multi-RAG AI Automation Platform. Built with Docusaurus.`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
        additionalLanguages: ['bash', 'python', 'javascript', 'typescript', 'json', 'yaml', 'graphql', 'sql'],
      },
      // algolia: {
      //   // Optional: Add Algolia search if needed
      //   appId: 'YOUR_APP_ID',
      //   apiKey: 'YOUR_API_KEY',
      //   indexName: 'multi-rag-docs',
      // },
    }),
};

module.exports = config;
