import React from 'react';
import clsx from 'clsx';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: '🔍 API Governance',
    icon: '🔍',
    description: (
      <>
        Automatically validate API specifications against governance rules.
        AI-powered corrections and compliance reporting with vector DB-powered pattern matching.
      </>
    ),
    link: '/docs/api-governance/overview',
  },
  {
    title: '📊 GraphQL Validator',
    icon: '📊',
    description: (
      <>
        Validate GraphQL schemas, perform smart linting, and generate centralized supergraph
        documentation with LLM-enhanced descriptions.
      </>
    ),
    link: '/docs/graphql-validator/overview',
  },
  {
    title: '📈 Log Classifier',
    icon: '📈',
    description: (
      <>
        Real-time log classification with pattern matching, continuous learning,
        and severity-based alerting. Integrates with DataDog, Splunk, and CloudWatch.
      </>
    ),
    link: '/docs/log-classifier/overview',
  },
];

function Feature({icon, title, description, link}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <div className={styles.featureIcon}>{icon}</div>
      </div>
      <div className="text--center padding-horiz--md">
        <h3>{title}</h3>
        <p>{description}</p>
        <a href={link} className="button button--primary button--sm">
          Learn More →
        </a>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
        
        <div className="row margin-top--lg">
          <div className="col">
            <h2 className="text--center">Why Multi-RAG?</h2>
            <div className="row margin-top--md">
              <div className="col col--3">
                <div className={styles.featureCard}>
                  <h3>🤖 AI-Powered</h3>
                  <p>Leverages GPT-4 and advanced embeddings for intelligent automation</p>
                </div>
              </div>
              <div className="col col--3">
                <div className={styles.featureCard}>
                  <h3>🔄 Continuous Learning</h3>
                  <p>Automatically improves from new data and patterns</p>
                </div>
              </div>
              <div className="col col--3">
                <div className={styles.featureCard}>
                  <h3>⚡ Real-Time</h3>
                  <p>Sub-second response times with efficient vector search</p>
                </div>
              </div>
              <div className="col col--3">
                <div className={styles.featureCard}>
                  <h3>📈 Scalable</h3>
                  <p>Kubernetes-ready with auto-scaling capabilities</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
