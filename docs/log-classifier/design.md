# Real-Time Log Classification System - Detailed Design

## Overview
AI-powered log classification system that learns patterns from real-time logs, performs intelligent pattern matching using vector DB, and builds severity-based alerting rules.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                  Real-Time Log Ingestion Layer                       │
│              (DataDog / Splunk / CloudWatch / Custom)                │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Log Classification Service                        │
└─────────────────────────────────────────────────────────────────────┘
        │                          │                          │
        ▼                          ▼                          ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│   Pattern     │         │   Real-Time   │         │   Alerting    │
│   Matcher     │         │  Classifier   │         │    Engine     │
└───────────────┘         └───────────────┘         └───────────────┘
        │                          │                          │
        └──────────────────────────┼──────────────────────────┘
                                   ▼
                         ┌───────────────────┐
                         │   Vector DB       │
                         │  (Log Patterns &  │
                         │   Severity Rules) │
                         └───────────────────┘
```

## Component Details

### 1. Log Ingestion Pipeline

**Purpose**: Receive and preprocess logs from various sources in real-time

**Data Sources**:
- DataDog API / Webhook
- Splunk HEC (HTTP Event Collector)
- AWS CloudWatch Logs
- Elasticsearch
- Custom log shippers (Filebeat, Fluentd)
- Direct HTTP/WebSocket endpoints

**Implementation**:
```python
class LogIngestionPipeline:
    """
    Receives and preprocesses logs from multiple sources
    """
    
    def __init__(self, kafka_producer, redis_cache):
        self.kafka = kafka_producer
        self.redis = redis_cache
        self.parsers = self.load_log_parsers()
    
    async def ingest_log(self, raw_log: dict, source: str) -> ProcessedLog:
        # Normalize log format
        normalized = self.normalize_log(raw_log, source)
        
        # Extract structured fields
        parsed = self.parse_log(normalized)
        
        # Enrich with metadata
        enriched = await self.enrich_log(parsed)
        
        # Send to processing queue
        await self.kafka.send('logs.raw', enriched)
        
        return enriched
    
    def normalize_log(self, raw_log: dict, source: str) -> dict:
        """
        Normalize different log formats to standard structure
        """
        parser = self.parsers.get(source)
        return {
            "timestamp": parser.extract_timestamp(raw_log),
            "level": parser.extract_level(raw_log),
            "message": parser.extract_message(raw_log),
            "service": parser.extract_service(raw_log),
            "host": parser.extract_host(raw_log),
            "metadata": parser.extract_metadata(raw_log),
            "source": source,
            "raw": raw_log
        }
```

**Log Normalization**:
```python
class StandardLogFormat(BaseModel):
    """
    Standardized log format across all sources
    """
    log_id: str
    timestamp: datetime
    level: str  # DEBUG, INFO, WARN, ERROR, CRITICAL
    message: str
    service: str
    host: str
    environment: str  # dev, staging, prod
    trace_id: Optional[str]
    span_id: Optional[str]
    user_id: Optional[str]
    request_id: Optional[str]
    metadata: Dict[str, Any]
    source: str  # datadog, splunk, cloudwatch
    raw: dict
```

### 2. Pattern Matcher

**Purpose**: Match incoming logs against known patterns in vector DB

**Process Flow**:
```
Incoming Log → Feature Extraction → Embedding Generation → 
Vector Search → Pattern Matching → Confidence Scoring
```

**Implementation**:
```python
class LogPatternMatcher:
    """
    Matches logs against known patterns using vector similarity
    """
    
    def __init__(self, vector_db, embedding_model, threshold=0.85):
        self.vector_db = vector_db
        self.embedding_model = embedding_model
        self.similarity_threshold = threshold
    
    async def match_pattern(self, log: StandardLogFormat) -> MatchResult:
        # Extract key features
        features = self.extract_features(log)
        
        # Generate embedding
        log_embedding = await self.embedding_model.encode(features)
        
        # Search for similar patterns
        similar_patterns = await self.vector_db.search(
            embedding=log_embedding,
            filter={
                "level": log.level,
                "service": log.service,
                "environment": log.environment
            },
            top_k=5
        )
        
        # Find best match
        best_match = self.find_best_match(similar_patterns, log)
        
        if best_match and best_match.similarity > self.similarity_threshold:
            return MatchResult(
                matched=True,
                pattern=best_match.pattern,
                similarity=best_match.similarity,
                severity=best_match.pattern.severity,
                classification=best_match.pattern.classification
            )
        
        # No match found - needs real-time classification
        return MatchResult(matched=False, requires_llm=True)
    
    def extract_features(self, log: StandardLogFormat) -> str:
        """
        Extract meaningful features from log for matching
        """
        # Tokenize and clean message
        cleaned_message = self.clean_log_message(log.message)
        
        # Extract error codes, stack traces, patterns
        error_codes = self.extract_error_codes(log.message)
        keywords = self.extract_keywords(log.message)
        
        # Combine features
        features = f"""
        Level: {log.level}
        Service: {log.service}
        Message: {cleaned_message}
        Error Codes: {error_codes}
        Keywords: {keywords}
        """
        
        return features
    
    def clean_log_message(self, message: str) -> str:
        """
        Remove dynamic parts (IDs, timestamps, IPs) to find pattern
        """
        # Replace UUIDs
        message = re.sub(
            r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            '<UUID>',
            message
        )
        
        # Replace IPs
        message = re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', '<IP>', message)
        
        # Replace numbers
        message = re.sub(r'\b\d+\b', '<NUM>', message)
        
        # Replace timestamps
        message = re.sub(
            r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}',
            '<TIMESTAMP>',
            message
        )
        
        return message
```

### 3. Real-Time Classifier

**Purpose**: Classify logs that don't match existing patterns using LLM

**Process Flow**:
```
Unmatched Log → LLM Classification → Pattern Extraction → 
Severity Assignment → Vector DB Storage → Pattern Learning
```

**Implementation**:
```python
class RealTimeLogClassifier:
    """
    Classifies unknown logs using LLM and learns new patterns
    """
    
    def __init__(self, llm, vector_db, embedding_model):
        self.llm = llm
        self.vector_db = vector_db
        self.embedding_model = embedding_model
    
    async def classify_log(self, log: StandardLogFormat) -> Classification:
        # Retrieve similar historical logs
        context_logs = await self.get_context_logs(log)
        
        # Generate classification with LLM
        classification = await self.llm_classify(log, context_logs)
        
        # Extract pattern from classification
        pattern = self.extract_pattern(log, classification)
        
        # Store new pattern in vector DB
        await self.store_pattern(pattern)
        
        # Update pattern statistics
        await self.update_pattern_stats(pattern)
        
        return classification
    
    async def llm_classify(
        self, 
        log: StandardLogFormat,
        context: List[StandardLogFormat]
    ) -> Classification:
        """
        Use LLM to classify log and determine severity
        """
        
        prompt = f"""
        You are a log analysis expert. Analyze this log entry and provide:
        1. Classification (error type, issue category)
        2. Severity (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        3. Root cause analysis
        4. Recommended action
        5. Similar pattern description
        
        Log Entry:
        Timestamp: {log.timestamp}
        Level: {log.level}
        Service: {log.service}
        Message: {log.message}
        Metadata: {log.metadata}
        
        Similar Historical Logs:
        {self.format_context_logs(context)}
        
        Provide response in JSON format:
        {{
            "classification": "...",
            "category": "...",
            "severity": "...",
            "root_cause": "...",
            "action": "...",
            "pattern_template": "...",
            "alert_required": true/false,
            "tags": [...]
        }}
        """
        
        response = await self.llm.generate(prompt)
        return Classification.parse_obj(response)
```

**Pattern Extraction**:
```python
def extract_pattern(
    self, 
    log: StandardLogFormat, 
    classification: Classification
) -> LogPattern:
    """
    Extract reusable pattern from classified log
    """
    # Clean message to pattern template
    pattern_template = self.clean_log_message(log.message)
    
    # Extract regex pattern
    regex_pattern = self.generate_regex_pattern(pattern_template)
    
    # Create pattern object
    pattern = LogPattern(
        pattern_id=generate_uuid(),
        template=pattern_template,
        regex=regex_pattern,
        classification=classification.classification,
        category=classification.category,
        severity=classification.severity,
        service=log.service,
        environment=log.environment,
        first_seen=log.timestamp,
        last_seen=log.timestamp,
        occurrence_count=1,
        tags=classification.tags,
        alert_rule=self.create_alert_rule(classification)
    )
    
    return pattern
```

### 4. Alerting Engine

**Purpose**: Generate alerts based on severity and pattern frequency

**Alert Types**:
1. **Immediate Alerts**: CRITICAL and ERROR with specific patterns
2. **Threshold Alerts**: Frequency-based (e.g., > 10 errors/minute)
3. **Anomaly Alerts**: Unusual patterns or spike detection
4. **Trend Alerts**: Increasing error rates over time

**Implementation**:
```python
class AlertingEngine:
    """
    Generates alerts based on log patterns and severity
    """
    
    def __init__(self, vector_db, notification_service):
        self.vector_db = vector_db
        self.notifier = notification_service
        self.alert_rules = self.load_alert_rules()
    
    async def process_log_for_alerts(
        self, 
        log: StandardLogFormat,
        classification: Classification
    ):
        # Check immediate alert rules
        if self.should_alert_immediately(log, classification):
            await self.send_immediate_alert(log, classification)
        
        # Update pattern frequency
        await self.update_frequency_metrics(log, classification)
        
        # Check threshold-based rules
        if await self.threshold_exceeded(log, classification):
            await self.send_threshold_alert(log, classification)
        
        # Check for anomalies
        if await self.detect_anomaly(log, classification):
            await self.send_anomaly_alert(log, classification)
    
    def should_alert_immediately(
        self, 
        log: StandardLogFormat,
        classification: Classification
    ) -> bool:
        """
        Determine if immediate alert is required
        """
        # CRITICAL always alerts
        if classification.severity == "CRITICAL":
            return True
        
        # Check if classification requires alert
        if classification.alert_required:
            return True
        
        # Check custom alert rules
        for rule in self.alert_rules:
            if rule.matches(log, classification):
                return True
        
        return False
```

**Alert Rule Configuration**:
```python
class AlertRule(BaseModel):
    rule_id: str
    name: str
    description: str
    severity_levels: List[str]  # [ERROR, CRITICAL]
    services: List[str]  # Filter by service
    categories: List[str]  # Filter by category
    threshold: Optional[int]  # Occurrences per time window
    time_window: Optional[int]  # Minutes
    notification_channels: List[str]  # slack, email, pagerduty
    enabled: bool
    
    def matches(
        self, 
        log: StandardLogFormat, 
        classification: Classification
    ) -> bool:
        if classification.severity not in self.severity_levels:
            return False
        
        if self.services and log.service not in self.services:
            return False
        
        if self.categories and classification.category not in self.categories:
            return False
        
        return True
```

**Severity-Based Vector DB**:
```json
{
  "pattern_id": "pattern-uuid",
  "template": "Failed to connect to database: Connection timeout after <NUM> ms",
  "regex": "Failed to connect to database: Connection timeout after \\d+ ms",
  "classification": "Database Connection Error",
  "category": "infrastructure",
  "severity": "CRITICAL",
  "service": "api-gateway",
  "environment": "production",
  "first_seen": "2025-12-14T10:00:00Z",
  "last_seen": "2025-12-14T14:30:00Z",
  "occurrence_count": 156,
  "alert_rule": {
    "immediate": true,
    "threshold": 5,
    "time_window": 5,
    "channels": ["pagerduty", "slack"]
  },
  "root_cause": "Database connection pool exhaustion",
  "recommended_action": "Scale database connections or investigate connection leaks",
  "tags": ["database", "timeout", "critical"],
  "related_patterns": ["pattern-uuid-2", "pattern-uuid-3"]
}
```

### 5. Pattern Learning & Training

**Purpose**: Continuously improve pattern matching from real-time data

**Training Pipeline**:
```
Historical Logs → Feature Engineering → Pattern Clustering → 
Embedding Training → Model Update → Vector DB Refresh
```

**Implementation**:
```python
class PatternLearningEngine:
    """
    Learns and improves log patterns from historical data
    """
    
    def __init__(self, vector_db, embedding_model):
        self.vector_db = vector_db
        self.embedding_model = embedding_model
    
    async def train_from_historical_logs(
        self,
        start_date: datetime,
        end_date: datetime
    ):
        # Fetch historical logs
        logs = await self.fetch_historical_logs(start_date, end_date)
        
        # Cluster similar logs
        clusters = self.cluster_logs(logs)
        
        # Extract patterns from clusters
        patterns = []
        for cluster in clusters:
            pattern = self.extract_cluster_pattern(cluster)
            patterns.append(pattern)
        
        # Generate embeddings for patterns
        embeddings = await self.generate_pattern_embeddings(patterns)
        
        # Store in vector DB
        await self.bulk_store_patterns(patterns, embeddings)
        
        # Generate training report
        return self.generate_training_report(patterns)
    
    def cluster_logs(self, logs: List[StandardLogFormat]) -> List[LogCluster]:
        """
        Cluster similar logs using DBSCAN or HDBSCAN
        """
        # Extract features
        features = [self.extract_features(log) for log in logs]
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(features)
        
        # Cluster
        clusterer = HDBSCAN(min_cluster_size=5)
        cluster_labels = clusterer.fit_predict(embeddings)
        
        # Group logs by cluster
        clusters = defaultdict(list)
        for log, label in zip(logs, cluster_labels):
            if label != -1:  # Ignore noise
                clusters[label].append(log)
        
        return [LogCluster(logs=logs) for logs in clusters.values()]
```

### 6. API Endpoints

**REST API**:
```yaml
POST /api/v1/logs/ingest
  - Body: Log entry
  - Returns: Ingestion ID

POST /api/v1/logs/classify
  - Body: Log entry
  - Returns: Classification result

GET /api/v1/logs/patterns
  - Query: service, severity, date_range
  - Returns: List of patterns

GET /api/v1/logs/patterns/{pattern_id}
  - Returns: Pattern details

POST /api/v1/logs/train
  - Body: Training configuration
  - Returns: Training job ID

GET /api/v1/logs/alerts
  - Query: severity, service, time_range
  - Returns: List of alerts

POST /api/v1/logs/alert-rules
  - Body: Alert rule configuration
  - Returns: Rule ID

GET /api/v1/logs/analytics
  - Query: service, metric_type
  - Returns: Analytics data
```

**WebSocket API** (Real-Time):
```yaml
WS /api/v1/logs/stream
  - Subscribe to real-time log classifications
  - Receive: Classification results as they happen

WS /api/v1/alerts/stream
  - Subscribe to real-time alerts
  - Receive: Alert notifications
```

## Data Models

### Log Pattern
```python
class LogPattern(BaseModel):
    pattern_id: str
    template: str  # Normalized message template
    regex: str  # Regex for matching
    classification: str
    category: str
    severity: str
    service: str
    environment: str
    first_seen: datetime
    last_seen: datetime
    occurrence_count: int
    alert_rule: Optional[AlertRule]
    root_cause: Optional[str]
    recommended_action: Optional[str]
    tags: List[str]
    related_patterns: List[str]
    embedding: List[float]
```

### Classification Result
```python
class Classification(BaseModel):
    classification_id: str
    log_id: str
    timestamp: datetime
    matched_pattern: Optional[str]
    similarity_score: Optional[float]
    classification: str
    category: str
    severity: str
    root_cause: str
    recommended_action: str
    alert_required: bool
    confidence: float
    processing_time_ms: int
    used_llm: bool  # Whether LLM was used
```

## Processing Workflow

### Complete Real-Time Classification Flow
```
1. Log received from source (DataDog/Splunk)
   ↓
2. Normalize to standard format
   ↓
3. Extract features and generate embedding
   ↓
4. Search vector DB for similar patterns
   ↓
5. Pattern match found? (similarity > 0.85)
   ├─ YES → Use cached classification
   │         - Apply severity
   │         - Update pattern stats
   │         - Check alert rules
   │         - Return result
   │
   └─ NO → Real-time LLM classification
             ↓
             - Call LLM with context
             - Extract new pattern
             - Generate embedding
             - Store in vector DB
             - Apply alert rules
             - Return result
   ↓
6. Send to appropriate channels
   - Store in Elasticsearch
   - Update metrics (Prometheus)
   - Trigger alerts (if needed)
   - Update dashboards
```

## Advanced Features

### 1. Anomaly Detection
```python
class AnomalyDetector:
    """
    Detects unusual log patterns or spikes
    """
    
    async def detect_anomaly(
        self, 
        log: StandardLogFormat,
        classification: Classification
    ) -> Optional[Anomaly]:
        
        # Get historical frequency
        historical_freq = await self.get_pattern_frequency(
            classification.pattern_id,
            lookback_hours=24
        )
        
        # Get current frequency
        current_freq = await self.get_pattern_frequency(
            classification.pattern_id,
            lookback_hours=1
        )
        
        # Statistical anomaly detection (Z-score)
        z_score = self.calculate_z_score(current_freq, historical_freq)
        
        if z_score > 3:  # 3 standard deviations
            return Anomaly(
                type="frequency_spike",
                pattern=classification.pattern_id,
                z_score=z_score,
                description=f"Pattern frequency increased by {z_score}σ"
            )
        
        return None
```

### 2. Root Cause Analysis
```python
async def analyze_root_cause(
    self,
    log: StandardLogFormat,
    related_logs: List[StandardLogFormat]
) -> RootCauseAnalysis:
    """
    Analyze related logs to determine root cause
    """
    
    prompt = f"""
    Analyze these related logs to determine the root cause:
    
    Primary Log: {log}
    
    Related Logs (time window ±5 minutes):
    {related_logs}
    
    Provide:
    1. Root cause
    2. Timeline of events
    3. Affected services
    4. Remediation steps
    """
    
    analysis = await self.llm.generate(prompt)
    return RootCauseAnalysis.parse_obj(analysis)
```

### 3. Pattern Evolution Tracking
```python
class PatternEvolutionTracker:
    """
    Tracks how log patterns change over time
    """
    
    async def track_pattern_evolution(
        self, 
        pattern_id: str
    ) -> EvolutionReport:
        
        # Get pattern history
        history = await self.get_pattern_history(pattern_id)
        
        # Analyze changes
        changes = self.analyze_changes(history)
        
        # Predict future occurrences
        prediction = self.predict_future_frequency(history)
        
        return EvolutionReport(
            pattern_id=pattern_id,
            changes=changes,
            frequency_trend=prediction,
            recommendations=self.generate_recommendations(changes)
        )
```

## Performance Optimizations

1. **Stream Processing**:
   - Apache Kafka for log streaming
   - Apache Flink for real-time processing
   - Redis for hot pattern cache

2. **Batch Optimization**:
   - Batch embedding generation
   - Bulk vector DB operations
   - Aggregated metrics

3. **Caching Strategy**:
   - L1: In-memory pattern cache (most frequent)
   - L2: Redis cache (recent patterns)
   - L3: Vector DB (all patterns)

4. **Sampling**:
   - Sample high-volume logs (e.g., DEBUG)
   - Full processing for ERROR/CRITICAL
   - Adaptive sampling based on load

## Integration Points

- **DataDog**: API + Webhooks
- **Splunk**: HEC + API
- **CloudWatch**: Logs API + Lambda
- **PagerDuty**: Alert integration
- **Slack**: Alert notifications
- **Elasticsearch**: Log storage
- **Grafana**: Dashboards
- **Prometheus**: Metrics

## Monitoring & Metrics

- Logs processed per second
- Pattern match rate (hit/miss ratio)
- LLM classification time
- Alert response time
- Pattern database size
- False positive rate
- Classification accuracy
