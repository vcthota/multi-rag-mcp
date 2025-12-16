/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */

// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    {
      type: 'doc',
      id: 'intro',
      label: 'Introduction',
    },
    {
      type: 'doc',
      id: 'getting-started',
      label: 'Getting Started',
    },
    {
      type: 'category',
      label: 'Architecture',
      collapsed: false,
      items: [
        'architecture/overview',
        'architecture/decision',
        'architecture/explained',
        'architecture/visual-comparison',
      ],
    },
    {
      type: 'category',
      label: 'API Governance',
      collapsed: false,
      items: [
        'api-governance/overview',
      ],
    },
    {
      type: 'category',
      label: 'GraphQL Validator',
      collapsed: false,
      items: [
        'graphql-validator/overview',
      ],
    },
    {
      type: 'category',
      label: 'Log Classifier',
      collapsed: false,
      items: [
        'log-classifier/overview',
      ],
    },
    {
      type: 'category',
      label: 'Implementation',
      collapsed: false,
      items: [
        'implementation/roadmap',
        'implementation/production-complete',
        'implementation/test-results',
        'implementation/database-schema',
        'implementation/deployment',
      ],
    },
  ],
};

module.exports = sidebars;
