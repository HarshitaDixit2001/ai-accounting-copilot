# AI Accounting Copilot

An end-to-end AI accounting assistant built with **Python, FastAPI, Retrieval-Augmented Generation (RAG), local LLM inference, deterministic accounting logic, automated evaluation, observability, auditability, data governance, and production-readiness controls**.

The project demonstrates how to build an AI application beyond a basic LLM wrapper — from **API design and retrieval through evaluation, reliability, governance, monitoring, and production-oriented deployment**.

---

## Overview

AI Accounting Copilot helps users answer accounting questions and explain financial transactions using a domain-specific accounting knowledge base.

The system combines:

- FastAPI REST APIs
- Local LLM inference through Ollama
- Retrieval-Augmented Generation (RAG)
- Local text embeddings
- Evidence-based response generation
- Retrieval confidence signals
- Deterministic accounting logic
- Structured journal-entry generation
- Automated AI evaluation
- Quality gates
- Human feedback collection
- Request-level observability
- RAG performance metrics
- Business outcome metrics
- AI audit logging
- Sensitive-data redaction
- Configurable audit retention
- Health and readiness checks
- Environment-based configuration
- Production startup configuration
- Docker deployment artifacts

The architecture is designed around a simple principle:

> **AI systems should be grounded, evaluated, observable, reliable, governable, and operationally ready — not just capable of generating text.**

---

# Key Capabilities

## 1. Grounded Accounting RAG

The application uses Retrieval-Augmented Generation to answer accounting questions using a domain-specific knowledge base.

The RAG pipeline:

1. Receives an accounting question.
2. Validates the request.
3. Generates an embedding for the query.
4. Retrieves relevant accounting knowledge.
5. Measures retrieval similarity.
6. Applies an evidence-sufficiency gate.
7. Abstains when sufficient evidence is unavailable.
8. Builds a grounded prompt from retrieved evidence.
9. Generates a response using the local LLM.
10. Returns the answer together with source information.

This prevents the application from blindly generating accounting answers when the knowledge base does not provide sufficient evidence.

---

## 2. Accounting Intelligence

The accounting intelligence layer combines **generative AI with deterministic application logic**.

For supported transaction patterns, the system can produce structured accounting information such as:

```text
Transaction:
Rent paid in cash ₹25000

Journal Entry:

Debit:  Rent Expense   ₹25000
Credit: Cash           ₹25000
```

The application can:

- Explain accounting concepts
- Explain financial transactions
- Extract transaction amounts
- Classify supported transaction patterns
- Generate structured journal-entry information
- Return retrieval sources
- Return retrieval confidence

Deterministic logic is intentionally used where predictable accounting behavior is more appropriate than relying entirely on an LLM.

---

# Architecture

```text
                         Client
                           |
                           v
                    +-------------+
                    |   FastAPI   |
                    |     API     |
                    +------+------+
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
        Request       Accounting      Health /
        Logging      Intelligence    Readiness
        & Metrics          |
                            v
                       RAG Service
                            |
                 +----------+----------+
                 |                     |
                 v                     v
          RAG Retriever           Ollama LLM
                 |                 qwen3:8b
                 v
          Knowledge Base
                 |
                 v
       Local Embeddings
       
                 |
                 v
             SQLite
             Database
```

Cross-cutting capabilities operate across the application:

```text
Evaluation
     |
Feedback
     |
Observability
     |
Auditability
     |
Data Governance
     |
Security
     |
Reliability
     |
Configuration
     |
Production Readiness
```

---

# Core AI Workflow

```text
User Request
     |
     v
API Validation
     |
     v
Request ID
     |
     v
RAG Retrieval
     |
     v
Evidence Sufficiency Check
     |
     +---- insufficient evidence ----> Safe Abstention
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
     +----> Sources
     |
     +----> Confidence
     |
     +----> Evaluation
     |
     +----> Audit Record
     |
     +----> Metrics
     |
     v
Client
```

---

# Example

### User Question

```text
How do I record rent paid in cash?
```

### Expected Accounting Treatment

```text
Debit: Rent Expense
Credit: Cash
```

The application returns the generated accounting response together with retrieved evidence and a retrieval confidence signal.

For supported transaction patterns, the accounting intelligence layer can additionally return structured journal-entry information.

---

# Safety-Oriented Abstention

A core design principle is that the system should not confidently answer questions when the available accounting evidence is insufficient.

If the retrieval layer cannot provide adequate supporting evidence, the system can return:

```text
The provided accounting knowledge does not contain enough information to answer this question.
```

This creates an explicit **abstention path** instead of treating every question as answerable.

The abstention behavior is also included in the automated evaluation system.

---

# AI Evaluation

The project contains a repeatable evaluation pipeline using a representative accounting test dataset.

The evaluation dataset covers:

- Accounting concepts
- Financial transactions
- Expected keywords
- Expected sources
- Supported questions
- Unsupported questions
- Safe-abstention scenarios

The evaluation measures:

- Pass rate
- Keyword coverage
- Source correctness
- Grounding
- Completeness
- Evaluator score
- Quality-gate status

The application also contains a deterministic response evaluator that checks:

- Response presence
- Source availability
- Accounting terminology
- Grounding in retrieved sources
- Question relevance
- Safe abstention behavior
- Unsupported-claim prevention

The evaluator produces a score that can be tracked as an operational quality signal.

### Latest evaluation result

```text
Pass Rate:    1.000
Source Score: 1.000
Quality Gate: Passed
```

The evaluation system provides a repeatable mechanism for detecting regressions when retrieval, prompts, accounting logic, or model behavior change.

---

# Human Feedback

The application supports collecting user feedback on AI responses.

Feedback includes:

- Request ID
- Rating
- Optional written feedback
- Timestamp

Supported feedback metrics include:

```text
Total Feedback
Positive Feedback
Negative Feedback
Positive Feedback Rate
```

This creates a feedback loop between AI behavior and real user judgment.

---

# Observability

The application includes request-level and AI-specific observability.

Tracked signals include:

- Request count
- Request duration
- Slow requests
- RAG retrieval latency
- LLM generation latency
- RAG request count
- RAG abstention count
- Evaluator scores
- User feedback
- Accounting questions answered
- Accounting questions safely abstained
- Transaction explanations

Each request is assigned a request ID for correlation across application operations.

Example request metadata:

```text
request_id
HTTP method
path
status code
duration
```

User prompt bodies are deliberately not logged by request middleware.

---

# Business Metrics

The system tracks application-level business outcomes in addition to technical metrics.

Current business signals include:

```text
Accounting Questions Answered
Accounting Questions Abstained
Transaction Explanations
Total Accounting Questions
Overall Answer Rate
```

This separates:

```text
System Performance
        +
AI Quality
        +
User Feedback
        +
Business Outcomes
```

into measurable operational signals.

---

# AI Auditability

Accounting intelligence requests can be recorded in an AI audit log.

Audit records contain:

- Request ID
- User question
- AI response
- Retrieved sources
- Evaluator score
- Timestamp

Audit records are stored in SQLite and can be retrieved through a protected audit API.

The audit layer provides traceability for understanding what the system received, what it generated, what evidence was used, and how the response was evaluated.

---

# Data Governance

The project includes basic data-governance controls for AI audit records.

Implemented controls include:

- API-key protection for audit-log access
- Email redaction before audit storage
- Indian phone-number redaction before audit storage
- Configurable audit retention
- Controlled access to operational AI records
- Environment-based secrets/configuration

Example:

```text
john@example.com
```

is stored as:

```text
[REDACTED_EMAIL]
```

Sensitive configuration is kept in `.env` rather than source code.

---

# Security Controls

The application includes:

- Pydantic request validation
- Maximum prompt-length enforcement
- Safe error responses
- Request correlation IDs
- RAG evidence gating
- Safe abstention
- Environment-based configuration
- Protected audit API
- Configurable metrics exposure
- Sensitive-data redaction
- Separation of `.env` and `.env.example`

The project does not claim to be a complete enterprise security platform. These controls represent the security and governance foundation implemented in the current application.

---

# Reliability and Readiness

The application provides two operational endpoints.

## Health

```text
GET /health
```

Used as a lightweight liveness check.

Example:

```json
{
  "status": "healthy",
  "service": "AI Accounting Copilot",
  "version": "0.1.0",
  "environment": "development"
}
```

## Readiness

```text
GET /ready
```

The readiness endpoint checks:

- Database availability
- Ollama availability

Example successful response:

```json
{
  "status": "ready",
  "service": "AI Accounting Copilot",
  "version": "0.1.0",
  "environment": "production",
  "database": "available",
  "ollama": "available"
}
```

If a required dependency is unavailable, the endpoint returns a non-ready response rather than incorrectly reporting that the service is operational.

---

# Main API Endpoints

| Endpoint | Purpose |
|---|---|
| `POST /accounting/rag` | Grounded accounting question answering |
| `POST /accounting/intelligence` | Accounting concept explanation |
| `POST /accounting/transaction/explain` | Transaction explanation and structured accounting intelligence |
| `POST /feedback` | Record user feedback |
| `GET /metrics` | Application and RAG metrics |
| `GET /metrics/feedback` | Feedback metrics |
| `GET /metrics/quality` | AI quality and business metrics |
| `GET /metrics/summary` | Consolidated operational, quality, feedback, and business metrics |
| `GET /audit/logs` | Protected AI audit-log access |
| `POST /llm/generate` | Local LLM generation |
| `GET /health` | Liveness check |
| `GET /ready` | Dependency readiness check |

Audit-log access requires the configured audit API key.

---

# Technology Stack

| Area | Technology |
|---|---|
| Language | Python |
| API | FastAPI |
| LLM | Ollama / qwen3:8b |
| Embeddings | nomic-embed-text |
| RAG | Custom retrieval pipeline |
| Database | SQLite |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Testing | pytest |
| Server | Uvicorn |
| Configuration | python-dotenv / environment variables |
| Deployment | Docker artifacts + production startup script |

The system is **local-first** and does not require a paid hosted LLM API.

---

# Local-First AI Architecture

The application uses Ollama for local LLM inference.

This provides:

- No paid API dependency
- Local model execution
- Local development
- Reproducible AI experimentation
- Greater control over application data flow

Current model:

```text
qwen3:8b
```

Embedding model:

```text
nomic-embed-text
```

This architecture makes the project suitable for development and demonstration without requiring a commercial model API key.

---

# Project Structure

```text
ai-accounting-copilot/
│
├── app/
│   ├── api/
│   │   └── routes/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── prompts/
│   ├── rag/
│   └── services/
│
├── data/
├── knowledge_base/
├── evals/
├── tests/
├── agents/
├── tools/
├── docs/
│
├── Dockerfile
├── .dockerignore
├── .env.example
├── start_production.ps1
├── requirements.txt
└── README.md
```

---

# Running Locally

## 1. Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

## 2. Make sure Ollama is running

Verify that the required models are available:

```powershell
ollama list
```

The project expects:

```text
qwen3:8b
nomic-embed-text
```

## 3. Start the FastAPI application

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

---

# Frontend Dashboard

The project includes a React and TypeScript dashboard built with Vite, providing a user interface for accounting assistance, transaction workflows, knowledge-base access, AI evaluation metrics, monitoring, audit and safety information, and application settings.

## Frontend Technology Stack

- React
- TypeScript
- Vite
- REST API integration
- CSS

## Run the Frontend Locally

Open a second PowerShell terminal while the FastAPI backend is running.

### 1. Navigate to the frontend directory

```powershell
cd "D:\AI Projects\ai-accounting-copilot\frontend"
```

### 2. Install dependencies

```powershell
npm install
```

### 3. Configure the API URL

Create a `.env` file inside the `frontend` directory with the following setting:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

This configures the frontend to communicate with the local FastAPI backend.

### 4. Start the development server

```powershell
npm run dev
```

Open the local URL printed by Vite in the terminal.

Keep the backend and frontend running in separate terminals.

## Production Build

To verify that the frontend compiles for production:

```powershell
npm run build
```

The generated production assets are written to `frontend/dist/`. This generated directory is excluded from version control.

# Production-Style Local Startup

The repository includes:

```text
start_production.ps1
```

Run:

```powershell
.\start_production.ps1
```

The production-style startup configuration uses:

```text
ENVIRONMENT=production
```

and starts Uvicorn on:

```text
0.0.0.0:8000
```

Docker is not required for the current local development environment. Docker artifacts are included to provide deployment portability.

---

# Environment Configuration

Configuration is environment-based.

Example `.env` values:

```text
APP_NAME=AI Accounting Copilot
APP_VERSION=0.1.0
ENVIRONMENT=production
DATABASE_URL=sqlite:///./accounting.db
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
RAG_SIMILARITY_THRESHOLD=0.45
EXPOSE_METRICS=false
MAX_PROMPT_LENGTH=5000
AUDIT_API_KEY=change-this-to-a-strong-random-key
AUDIT_RETENTION_DAYS=90
```

Secrets and environment-specific configuration should not be committed to source control.

The repository provides `.env.example` as a configuration template.

---

# Evaluation and Operational Metrics

The project exposes multiple layers of system signals.

### Technical signals

```text
Request count
Request latency
Slow requests
RAG retrieval latency
LLM generation latency
RAG abstentions
```

### AI quality signals

```text
Evaluator score
Evaluation count
Source correctness
Grounding
Completeness
```

### Human feedback signals

```text
Positive feedback
Negative feedback
Positive feedback rate
```

### Business signals

```text
Accounting questions answered
Accounting questions abstained
Transaction explanations
Overall answer rate
```

This provides a foundation for evaluating the application across more than model output alone.

---

# Testing

Run the complete test suite:

```powershell
pytest
```

The test suite covers:

- Accounting intelligence
- Transaction explanations
- Database behavior
- API routes
- Invoice operations
- Transaction operations
- Journal entries
- LLM integration
- RAG chunking
- RAG embeddings
- RAG loading
- RAG retrieval
- RAG service behavior
- Evaluation
- Feedback
- Metrics
- Audit logging
- Audit API security
- Data governance
- Audit retention
- Health and readiness

### Latest full regression

```text
102 passed, 0 failed
```

The current suite contains **102 automated tests**.

---

# Production Validation

The production-oriented configuration has been smoke-tested.

Verified:

```text
GET /health
200 OK
```

and:

```text
GET /ready

status: ready
database: available
ollama: available
```

The RAG workflow was also tested using:

```text
POST /accounting/rag
```

with:

```text
How do I record rent paid in cash?
```

The application successfully returned a grounded accounting response through the production startup configuration.

---

# Engineering Decisions

## Local-First AI

Ollama is used instead of a paid hosted model API.

This allows the complete AI workflow to run locally without requiring a paid API key.

## Grounded Generation

RAG retrieval and an evidence gate are used to reduce unsupported accounting responses.

## Deterministic Accounting Logic

Structured accounting behavior is implemented with deterministic application logic where appropriate.

This improves predictability for supported transaction patterns.

## Evaluation Before Optimization

The project includes a repeatable evaluation dataset and quality gate so changes to retrieval and model behavior can be measured systematically.

## Observability

Request-level and RAG-level metrics make latency, slow requests, and abstentions measurable.

## Human Feedback

User feedback is captured as an additional quality signal rather than relying exclusively on automated evaluation.

## Auditability

AI requests can be recorded with their sources and evaluator scores, creating traceability for AI behavior.

## Data Governance

Sensitive information is redacted before audit storage, and audit access is protected.

## Environment-Based Configuration

Application configuration and secrets are separated from source code.

## Production-Oriented Design

The system includes health checks, readiness checks, structured logging, metrics, configuration management, deployment artifacts, automated testing, and operational controls.

---

# Enterprise AI Readiness

The project intentionally goes beyond a basic RAG demo and implements several capabilities relevant to production AI systems.

### Evaluation

- Representative evaluation dataset
- Automated evaluator
- Quality gates
- Source and grounding checks
- Safe-abstention evaluation
- Evaluator score tracking

### Human Feedback

- User feedback collection
- Positive/negative feedback tracking
- Feedback rate metrics

### Auditability

- AI audit records
- Request correlation
- Source tracking
- Evaluator-score tracking
- Protected audit API

### Data Governance

- Sensitive-data redaction
- Audit retention policy
- API-key-protected audit access
- Environment-based configuration

### Reliability

- Health checks
- Readiness checks
- Dependency validation
- Safe abstention
- Automated regression testing

### Observability

- Request metrics
- Latency metrics
- RAG metrics
- LLM metrics
- Slow-request tracking
- Abstention tracking

### Business Measurement

- Accounting questions answered
- Accounting questions abstained
- Transaction explanations
- Overall answer rate

These capabilities demonstrate the engineering considerations required when moving AI applications from experimentation toward production environments.

---

# Known Limitations

This is a portfolio-scale production-oriented system rather than a deployed enterprise accounting platform.

Current limitations include:

- SQLite is used for local persistence.
- Ollama provides local model inference rather than managed model serving.
- Retrieval confidence is based on similarity signals and is not a calibrated probability.
- The evaluator is deterministic and heuristic-based rather than a full LLM-as-a-judge system.
- Deterministic transaction classification currently covers a limited set of supported patterns.
- The current deployment artifacts are production-oriented but have not been validated as a multi-node production deployment.
- The project does not claim real enterprise customer adoption or production traffic.

These limitations are intentional and documented so that future production evolution can be evaluated explicitly.

---

# Future Production Evolution

A larger production deployment could evolve toward:

```text
SQLite
   ↓
PostgreSQL

Local Retrieval
   ↓
Managed / Distributed Vector Infrastructure

Single Application
   ↓
Scalable Service Architecture

Local Ollama
   ↓
Managed Model Serving / Model Gateway

Basic Metrics
   ↓
Centralized Observability Platform

Single-Tenant Application
   ↓
Multi-Tenant Isolation

Local Audit Storage
   ↓
Enterprise Audit / Compliance Infrastructure
```

Additional production evolution could include:

- Distributed tracing
- Centralized logging
- Advanced model evaluation
- LLM-as-a-judge evaluation
- Human review workflows
- Multi-tenant authorization
- Role-based access control
- Rate limiting
- Secrets management
- Scalable vector infrastructure
- Model routing
- Cost attribution
- Continuous evaluation
- CI/CD deployment
- Production alerting
- Data lifecycle management

---

# Project Status

| Area | Status |
|---|---|
| Foundation | Complete |
| Accounting Core | Complete |
| Local LLM Integration | Complete |
| RAG | Complete |
| Accounting Intelligence | Complete |
| AI Evaluation | Complete |
| Human Feedback | Complete |
| Reliability & Observability | Complete |
| Auditability | Complete |
| Data Governance | Complete |
| Business Metrics | Complete |
| Security Controls | Complete |
| Productionization | Complete |
| Automated Testing | Complete |

### Current regression status

```text
102 passed
0 failed
```

---

# What This Project Demonstrates

This project demonstrates practical experience with:

- Python backend engineering
- FastAPI API development
- AI application architecture
- Local LLM integration
- Retrieval-Augmented Generation
- Embeddings
- Grounded generation
- Evidence-based abstention
- Deterministic AI-assisted workflows
- Structured accounting intelligence
- Automated evaluation
- Quality gates
- Human feedback loops
- AI observability
- Reliability engineering
- Auditability
- Data governance
- Input validation
- Safe error handling
- Health and readiness checks
- Environment-based configuration
- Business outcome metrics
- Production deployment preparation
- Automated regression testing

The project demonstrates an engineering workflow of:

```text
Prototype
   ↓
Build
   ↓
Ground
   ↓
Evaluate
   ↓
Measure
   ↓
Add Feedback
   ↓
Add Reliability
   ↓
Add Governance
   ↓
Prepare for Production
```

---

# Portfolio Context

AI Accounting Copilot was built as an engineering demonstration of how an AI system can be developed from an initial prototype into a **measurable, observable, grounded, and production-oriented application**.

The emphasis is not only on generating useful AI responses, but also on:

```text
Model Behavior
+
Retrieval Quality
+
Evaluation
+
Reliability
+
Observability
+
Security
+
Governance
+
Business Outcomes
```

This makes the project representative of the broader engineering lifecycle involved in building applied AI systems.

---

# License

This project is intended as a portfolio and engineering demonstration project.