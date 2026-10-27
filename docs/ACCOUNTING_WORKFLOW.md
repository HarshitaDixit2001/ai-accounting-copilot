# Accounting Copilot — Workflow and Validation Rules

## 1. Purpose

AI Accounting Copilot is a local-first accounting assistance application that combines deterministic transaction rules, retrieval-augmented generation (RAG), large language model (LLM) responses, response evaluation, and audit logging.

The application provides accounting explanations and transaction guidance. It should not be treated as an autonomous accounting approval or posting system.

This document distinguishes implemented functionality from recommended controls that have not yet been verified in the codebase.

## 2. Existing Accounting Workflow

### Accounting concept questions

1. The API accepts a question through `POST /accounting/intelligence`.
2. Pydantic validates that the prompt is a string with at least one character.
3. The RAG service retrieves up to five relevant knowledge-base chunks.
4. An evidence gate checks whether at least one meaningful term from the question occurs in the retrieved text.
5. If the evidence gate fails, the system abstains and returns an insufficient-evidence message without calling the LLM.
6. If the gate passes, the system builds a prompt containing the question and retrieved context.
7. Ollama generates an answer using the configured local model.
8. The response includes the answer, retrieved sources, and a retrieval-similarity-based confidence signal.
9. The API evaluates the response and records an audit entry containing the request ID, question, response, sources, and evaluator score.

### Transaction explanations

1. The API accepts a transaction description through `POST /accounting/transaction/explain`.
2. Pydantic validates that the description is a string with at least one character.
3. The RAG/LLM pipeline generates an accounting explanation or abstains if its evidence gate fails.
4. A separate deterministic rule attempts to classify the transaction.
5. The current rule recognizes descriptions containing both "rent" and "cash".
6. When matched, it creates a proposed journal entry with Rent Expense debited and Cash credited, using the extracted amount.
7. When no rule matches, the journal entry is `null`.
8. The API evaluates the response and records an audit entry.

The deterministic rule and the RAG/LLM pipeline are separate operations. A generated explanation does not establish that a transaction has been correctly classified.

### Transaction record management

The separate transaction API supports creating, listing, and retrieving stored transaction records.

- `POST /transactions` creates a transaction record.
- `GET /transactions` lists transaction records.
- `GET /transactions/{transaction_id}` retrieves a record by ID.

The creation service persists the supplied transaction fields through the repository layer. This workflow is distinct from the transaction-explanation endpoint.

## 3. Deterministic Rules and Validation

### Transaction classification rule

The implemented rule checks whether the lowercased transaction description contains both "rent" and "cash".

When both terms are present, the proposed entry is:

- Debit: Rent Expense
- Credit: Cash
- Amount: Extracted amount

Other descriptions return no deterministic journal entry.

This is a narrow, hard-coded rule, not a trained machine-learning classifier. It does not currently demonstrate general-purpose accounting classification.

### Amount extraction

The `extract_amount()` function uses a regular expression to extract a number, with optional currency markers such as ₹, Rs., or INR. Commas are removed before conversion to a floating-point number.

If no amount is found, the function returns `0.0`.

**Known limitation:** The current classification rule can create a journal entry with an amount of zero if the description matches the rent-and-cash rule but no amount can be extracted. The explanation request does not itself require a positive amount.

### Request validation

| Endpoint or model | Implemented validation |
|---|---|
| `AccountingIntelligenceRequest` | Prompt has a minimum length of one character |
| `TransactionExplanationRequest` | Description has a minimum length of one character |
| `TransactionRequest` | Amount must be greater than zero |
| `InvoiceRequest` | Amount must be greater than zero |
| `JournalEntryLine` | Account is a string; amount is a float |
| `JournalEntry` | Contains description, debit line, and credit line |

The shown request models do not establish comprehensive validation of transaction types, currency, date, accounting period, duplicate transactions, or extracted amounts.

## 4. RAG and LLM Functionality

The RAG pipeline:

- Retrieves up to five relevant knowledge-base chunks.
- Checks for at least one meaningful term shared between the question and retrieved text.
- Constructs a context-grounded prompt.
- Calls the configured Ollama-backed generation service when the evidence gate passes.
- Returns source names, chunk IDs, similarity scores, and source content.
- Records retrieval time, LLM generation time, and abstention events.

The evidence gate is a lightweight lexical check. A matching term does not guarantee that the retrieved documents entail or fully support the generated answer.

The returned confidence value is calculated from the strongest retrieved similarity score and bounded between zero and one. It is a retrieval signal, not a calibrated probability that the answer is correct, complete, or safe.

## 5. Evaluation, Monitoring, and Auditability

The accounting API invokes `evaluate_accounting_response()` for the generated or abstained response.

The API also records business outcome metrics and calls `record_ai_audit()` with the request ID, question, response, sources, and evaluator score.

The RAG service records retrieval duration, LLM duration, and whether the evidence gate caused an abstention.

These mechanisms support observability and traceability. An evaluator score or audit record does not, by itself, establish correctness or constitute human approval.

## 6. Human Review and Escalation

The code reviewed for this document does not establish an implemented human approval workflow for uncertain classifications or proposed journal entries.

For responsible accounting use, human review should be required before a proposed entry is accepted for operational use when:

- No deterministic classification rule matches.
- The amount is missing, zero, malformed, or ambiguous.
- Retrieved evidence is insufficient or conflicting.
- The proposed accounting treatment is material, unusual, or outside the documented rules.
- The response or evidence has not met the organization's acceptance criteria.

A future review workflow should record the reviewer, decision, timestamp, reason for approval or rejection, and any corrected classification.

Until that workflow exists, these are recommended controls rather than implemented capabilities.

## 7. Known Limitations and Recommended Improvements

1. Require a valid, positive amount before creating a proposed journal entry.
2. Return an explicit classification status such as `classified`, `unclassified`, or `needs_review`.
3. Separate retrieval confidence from answer correctness and accounting-rule validation.
4. Evaluate whether retrieved evidence supports the answer rather than relying only on term overlap.
5. Add regression tests for missing amounts, ambiguous descriptions, unsupported questions, and incorrect classifications.
6. Add a documented human-review workflow before operational acceptance of uncertain entries.
7. Validate transaction types and other required business fields against explicit rules.
8. Ensure that audit records and evaluation results can be traced to the relevant request and knowledge-base evidence.

## 8. Architecture Summary

The current application combines:

- **Deterministic logic:** amount extraction and the narrow rent-paid-in-cash classification rule.
- **RAG:** knowledge-base retrieval and a lexical evidence gate.
- **LLM generation:** context-based accounting explanations through Ollama.
- **Evaluation:** response scoring and abstention identification.
- **Observability:** retrieval and generation timing, business metrics, and audit records.
- **Persistence:** separate transaction-record management endpoints.

This hybrid architecture provides a foundation for a more robust accounting assistant, while explicit validation, calibrated quality measures, and human approval remain important areas for improvement.