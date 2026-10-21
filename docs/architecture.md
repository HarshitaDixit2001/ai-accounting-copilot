# AI Accounting Copilot — System Architecture

## 1. Purpose

AI Accounting Copilot is an AI-assisted accounting platform designed to answer accounting questions, explain financial transactions, retrieve grounded accounting knowledge, and generate structured accounting intelligence.

The system is designed as an end-to-end AI application rather than a simple LLM wrapper.

The architecture focuses on:

- Grounded AI responses
- Deterministic accounting behavior where appropriate
- Evaluation
- Reliability
- Observability
- Security and governance
- Production readiness

---

## 2. High-Level Architecture

```text
                         +------------------+
                         |      Client      |
                         +--------+---------+
                                  |
                                  v
                         +------------------+
                         |     FastAPI      |
                         |      API        |
                         +--------+---------+
                                  |
              +-------------------+-------------------+
              |                   |                   |
              v                   v                   v
       Request Middleware   Accounting APIs    Health / Metrics
              |                   |
              |                   v
              |          +---------------------+
              |          | Accounting          |
              |          | Intelligence        |
              |          +----------+----------+
              |                     |
              |                     v
              |          +---------------------+
              |          |    RAG Service      |
              |          +----------+----------+
              |                     |
              |          +----------+----------+
              |          |                     |
              |          v                     v
              |   +-------------+       +-------------+
              |   | Retriever   |       | Ollama LLM  |
              |   +------+------+       | qwen3:8b    |
              |          |              +-------------+
              |          v
              |   +-------------+
              |   | Knowledge   |
              |   | Base        |
              |   +-------------+
              |
              v
       +----------------+
       | Metrics / Logs |
       +----------------+

              +----------------+
              | SQLite Database|
              +----------------+
```

---

## 3. Application Layers

### API Layer

The API layer is implemented using FastAPI.

Responsibilities include:

- Request validation
- HTTP routing
- Response serialization
- Error handling
- Health checks
- Readiness checks
- Metrics exposure

Main API areas include:

```text
/accounting
/llm
/invoice
/transaction
/journal-entry
/health
/ready
/metrics
```

---

## 4. Accounting Intelligence Layer

The accounting intelligence service provides structured accounting behavior on top of the RAG and LLM components.

The service can:

1. Accept an accounting question or transaction description.
2. Query the RAG assistant.
3. Calculate retrieval confidence.
4. Extract transaction amounts.
5. Classify supported transaction patterns.
6. Generate structured journal-entry information.

For supported transaction patterns, deterministic logic is used.

Example:

```text
Input:
Rent paid in cash ₹25000

Output:

Debit:
Rent Expense — ₹25000

Credit:
Cash — ₹25000
```

This approach reduces dependence on unconstrained LLM generation for structured accounting behavior.

---

## 5. RAG Architecture

The RAG pipeline consists of:

```text
User Question
      |
      v
Retriever
      |
      v
Relevant Knowledge Chunks
      |
      v
Evidence Gate
      |
      +---- insufficient evidence ----> Abstain
      |
      v
Context Construction
      |
      v
Accounting Prompt
      |
      v
Ollama LLM
      |
      v
Grounded Response + Sources
```

### Retrieval

The retriever searches the accounting knowledge base using locally generated embeddings.

The system retrieves the top relevant chunks.

Each retrieved chunk contains metadata such as:

- Source
- Chunk ID
- Similarity
- Content

### Evidence Gate

Before sending retrieved content to the LLM, the system checks whether the retrieved evidence contains meaningful terms related to the user's question.

If evidence is insufficient, the system abstains.

Example:

```text
The provided accounting knowledge does not contain enough information
to answer this question.
```

This provides a basic grounding control against unsupported responses.

---

## 6. Prompt Construction

The RAG prompt instructs the model to:

- Use the provided accounting context as the primary source of truth.
- Answer using retrieved evidence.
- Avoid unsupported accounting facts.
- Avoid inventing financial data.
- Clearly identify Debit and Credit for journal entries.
- Abstain when the context does not contain sufficient information.
- Avoid revealing internal instructions.

The prompt is constructed by:

```text
Question
   +
Retrieved Context
   |
   v
Accounting RAG Prompt
```

---

## 7. Local LLM Architecture

The application uses Ollama for local model inference.

Configured model:

```text
qwen3:8b
```

Configured endpoint:

```text
http://localhost:11434
```

Using a local model provides:

- No dependency on paid hosted API keys
- Local development
- Greater control over data flow
- Reproducible development environments
- Lower external service dependency

A tradeoff is increased local inference latency compared with hosted model infrastructure.

---

## 8. Embeddings

The RAG system uses:

```text
nomic-embed-text:latest
```

for local embedding generation.

The embedding pipeline is:

```text
Knowledge Documents
        |
        v
     Chunking
        |
        v
    Embeddings
        |
        v
 Retrieval Index
```

At query time:

```text
User Question
      |
      v
Question Embedding
      |
      v
Similarity Search
      |
      v
Top-K Knowledge Chunks
```

---

## 9. Database Architecture

The application uses:

```text
SQLite
+
SQLAlchemy
```

The database stores application accounting data including entities such as:

- Invoices
- Accounting transactions
- Journal entries

The database is accessed through the application's database layer rather than directly from API handlers.

---

## 10. Reliability Architecture

Reliability is supported through several mechanisms.

### Request IDs

Each request receives an `X-Request-ID`.

If the client does not provide one, the application generates one.

The same ID is returned in the response headers and included in application logs.

This allows a request to be traced across the application.

### Global Error Handling

Unhandled exceptions are converted into safe API responses.

The response contains:

```text
error
message
request_id
```

Internal exception details are not exposed to the client.

### Health

The health endpoint confirms that the application process is running.

```text
GET /health
```

### Readiness

The readiness endpoint checks critical dependencies:

```text
Database
Ollama
```

```text
GET /ready
```

If a dependency is unavailable, the endpoint returns HTTP 503.

---

## 11. Observability Architecture

The application provides both request-level and RAG-level metrics.

### Request Metrics

Tracked metrics include:

- Request count
- Total duration
- Average duration
- Slow request count

### RAG Metrics

Tracked metrics include:

- RAG request count
- Average retrieval duration
- Average LLM duration
- Abstention count

Example flow:

```text
HTTP Request
     |
     v
Request Middleware
     |
     +---- request timing
     |
     v
RAG Service
     |
     +---- retrieval timing
     |
     +---- LLM timing
     |
     +---- abstention tracking
```

Metrics exposure is controlled through configuration.

---

## 12. Security and Governance

The system includes several application-level controls.

### Input Validation

API requests enforce constraints such as:

- Non-empty prompts
- Maximum prompt length
- Structured request schemas

### Configuration Security

Environment-specific configuration is stored outside application code.

The repository provides:

```text
.env.example
```

while the actual:

```text
.env
```

is excluded from source control and Docker builds.

### Logging Controls

The request middleware logs request metadata but does not log user prompt bodies.

### Safe Error Handling

Internal exception information is not returned directly to clients.

### Evidence Gating

The RAG system can abstain when retrieved evidence is insufficient.

---

## 13. Evaluation Architecture

The project includes an evaluation dataset containing representative accounting tasks.

Evaluation categories include:

- Accounting concepts
- Transactions
- Unsupported questions

Each case can define:

```text
Question
Expected Keywords
Expected Sources
Category
```

The evaluation pipeline measures:

- Pass rate
- Keyword coverage
- Source correctness
- Grounding
- Completeness

A quality gate determines whether the current system behavior meets the configured evaluation criteria.

This provides a repeatable mechanism for evaluating changes to:

- Retrieval
- Prompting
- Model behavior
- Accounting logic

---

## 14. Production Architecture

The application is designed to run behind an ASGI server.

Production startup:

```text
Uvicorn
   |
   v
app.main:app
```

Production artifacts include:

```text
Dockerfile
.dockerignore
.env.example
start_production.ps1
```

The Docker image is designed to install Python dependencies and copy the application, knowledge base, and data required by the service.

Sensitive local files such as `.env` and the SQLite database are excluded from the Docker build context.

---

## 15. Request Lifecycle

A typical accounting RAG request follows this lifecycle:

```text
Client
  |
  v
FastAPI
  |
  v
Request Middleware
  |
  +--> Request ID
  +--> Request Timing
  |
  v
Request Validation
  |
  v
RAG Service
  |
  v
Retriever
  |
  v
Evidence Gate
  |
  +---- insufficient ----> Abstain
  |
  v
Prompt Construction
  |
  v
Ollama
  |
  v
Generated Response
  |
  v
Sources + Response
  |
  v
Client
```

---

## 16. Key Engineering Decisions

### Local-first AI

A local LLM was selected to avoid dependence on paid external API services during development.

### RAG instead of unrestricted generation

Accounting responses should be grounded in known accounting information rather than relying entirely on model knowledge.

### Deterministic logic for structured accounting

Where predictable journal-entry behavior is required, deterministic application logic is used alongside AI-generated explanations.

### Evaluation as a first-class component

The system includes a representative evaluation dataset and measurable quality criteria.

### Observability from the application layer

Latency, request behavior, and RAG behavior are measured explicitly to support operational debugging.

### Readiness separate from liveness

The `/health` endpoint answers whether the application is running.

The `/ready` endpoint answers whether required dependencies are available.

This separation supports deployment and operational monitoring.

---

## 17. Current Limitations

The current system is intentionally designed as a portfolio-scale implementation.

Known limitations include:

- SQLite is appropriate for local and demonstration workloads but is not the final choice for high-scale production workloads.
- Ollama local inference can have significant latency depending on hardware.
- Retrieval confidence is currently based on similarity rather than a calibrated probability.
- The evidence gate uses a lightweight deterministic heuristic.
- The accounting classifier currently supports a limited set of deterministic transaction patterns.
- Metrics are process-local rather than backed by a distributed monitoring system.

These limitations provide clear future paths for scaling the architecture.

---

## 18. Future Production Evolution

For a larger production deployment, the architecture could evolve toward:

```text
                         Load Balancer
                              |
                              v
                    Multiple API Instances
                              |
             +----------------+----------------+
             |                                 |
             v                                 v
      Production Database              Distributed Cache
             |
             v
      Vector Database
             |
             v
       Model Serving Layer
             |
             v
      Observability Stack
```

Potential improvements include:

- PostgreSQL
- Dedicated vector database
- Distributed metrics
- Centralized logging
- Model-serving infrastructure
- Horizontal API scaling
- Authentication and authorization
- More advanced evaluation graders
- Human feedback loops
- Calibrated confidence scoring
- More comprehensive accounting rule coverage

---

## 19. Architecture Goal

The core architectural goal is to build an AI system that is not merely capable of generating answers, but can also be:

**Grounded → Evaluated → Observable → Reliable → Secure → Deployable**

This provides a foundation for moving an AI application from prototype development toward production-oriented engineering.

## Production AI Architecture

The current system extends the core RAG architecture with evaluation, auditability, governance, observability, and business-impact measurement.

### End-to-End Request Flow

```text
                         User
                           |
                           v
                    FastAPI API Layer
                           |
                           v
                  Request ID Middleware
                           |
                           v
                 Accounting Intelligence
                           |
                           v
                    RAG Service
                     /        \
                    v          v
             Retriever       Evidence Gate
                    |          |
                    v          v
              Knowledge Base  |
                    \          /
                     \        /
                      v      v
                     Prompt
                       |
                       v
                  Local Ollama
                    qwen3:8b
                       |
                       v
                  AI Response
                       |
                       v
                  AI Evaluator
                       |
             +---------+---------+
             |                   |
             v                   v
       Quality Metrics       Audit Service
                                 |
                                 v
                          Audit Database
                                 |
                                 v
                         Protected Audit API
```

### Supporting Operational Layer

```text
                 AI Accounting Copilot
                         |
        +----------------+----------------+
        |                |                |
        v                v                v
   Request Metrics   RAG Metrics     Business Metrics
        |                |                |
        |                |                |
        v                v                v
   Request count    Retrieval time    Questions answered
   Latency          LLM time          Questions abstained
   Slow requests    Abstention rate   Transaction explanations
                                        Answer rate

                         |
                         v
                  Quality Metrics
                         |
              +----------+----------+
              |                     |
              v                     v
        Evaluator Scores       User Feedback
```

## Core AI Pipeline

The accounting intelligence workflow follows:

```text
User Question
     |
     v
Input Validation
     |
     v
Knowledge Retrieval
     |
     v
Evidence Sufficiency Check
     |
     +------ insufficient evidence ------> Safe Abstention
     |
     v
Context Construction
     |
     v
Grounded Prompt
     |
     v
Local LLM
     |
     v
Accounting Response
     |
     v
Deterministic Evaluation
     |
     +--------------------+
     |                    |
     v                    v
Quality Metrics       Audit Record
```

The evidence gate prevents the LLM from being called when the retrieved accounting knowledge does not provide sufficient evidence for the question.

Unsupported questions therefore produce an explicit abstention response instead of an unsupported accounting claim.

## Evaluation Architecture

The evaluator uses a deterministic rubric rather than relying solely on the LLM to judge itself.

Current checks include:

- response presence
- source availability
- accounting terminology
- grounding evidence
- question relevance
- safe abstention
- absence of unsupported claims for abstained responses

Evaluator scores are recorded as production-quality signals and associated with audit records.

This creates a separation between:

```text
AI generation
      |
      v
Independent evaluation
      |
      v
Quality signal
```

This separation makes the system easier to test and monitor.

## Human Feedback Loop

Users can submit feedback against an AI request.

```text
AI Response
     |
     v
User Feedback
     |
     v
Feedback Database
     |
     v
Feedback Metrics
     |
     v
Quality Monitoring
```

The system tracks:

- total feedback
- positive feedback
- negative feedback
- positive feedback rate

This provides a basic human-in-the-loop quality signal alongside deterministic evaluation.

## Auditability and Governance

Every accounting intelligence request can generate an audit record containing:

- request ID
- question
- response
- retrieved sources
- evaluator score
- timestamp

Audit records are stored separately from the transient API response.

The audit API is protected with an operator API key:

```text
GET /audit/logs
        |
        v
Audit API Key
        |
   +----+----+
   |         |
 invalid    valid
   |         |
   v         v
  403       Audit Logs
```

### Data Governance

Before questions and generated responses are persisted in audit records, common sensitive values are redacted.

Currently supported redaction includes:

- email addresses
- Indian phone numbers

Audit retention is configurable through:

```text
AUDIT_RETENTION_DAYS
```

Expired audit records can be removed through the audit retention service.

## Observability

The system uses structured request logging with request IDs.

Operational metrics include:

### Request Metrics

- request count
- total duration
- slow-request count

### RAG Metrics

- retrieval duration
- LLM generation duration
- RAG request count
- abstention count

### Quality Metrics

- average evaluator score
- evaluation count
- positive feedback rate

### Business Metrics

- accounting questions answered
- accounting questions abstained
- transaction explanations
- total accounting questions
- answer rate

The consolidated endpoint:

```text
GET /metrics/summary
```

provides a combined operational view.

## Health and Readiness

The service exposes separate health and readiness concepts.

```text
/health
    |
    +-- application status
    +-- version
    +-- environment


/ready
    |
    +-- database availability
    +-- Ollama availability
```

A readiness failure returns HTTP `503`, allowing deployment infrastructure to distinguish a running application from a service that is not ready to handle AI requests.

## Testing Architecture

The project uses automated tests across multiple layers:

```text
Unit Tests
    |
    +-- accounting logic
    +-- evaluator
    +-- data governance
    +-- audit service
    |
    v
API Tests
    |
    +-- accounting endpoints
    +-- feedback
    +-- metrics
    +-- health/readiness
    +-- audit API
    |
    v
Integration Tests
    |
    +-- accounting -> evaluator -> audit
    +-- business metrics
    |
    v
Full Regression Suite
```

The latest full regression run:

```text
102 passed
0 failed
```

This provides automated verification across the core AI, accounting, RAG, evaluation, governance, and operational layers.