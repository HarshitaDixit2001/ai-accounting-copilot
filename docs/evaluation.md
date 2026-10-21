# AI Accounting Copilot — Evaluation

## 1. Evaluation Objective

The AI Accounting Copilot is evaluated using a representative accounting question set covering:

- Accounting concepts
- Transaction interpretation
- Journal-entry generation
- Retrieval quality
- Source correctness
- Unsupported questions
- Abstention behavior

The evaluation is designed to verify that the system:

1. Produces useful accounting responses.
2. Retrieves relevant accounting knowledge.
3. Grounds responses in the retrieved knowledge base.
4. Identifies unsupported questions instead of inventing information.
5. Produces deterministic journal-entry structure for supported transaction patterns.

---

## 2. Evaluation Dataset

The evaluation dataset contains 8 representative cases.

| ID | Category | Example |
|---|---|---|
| accounting_001 | Accounting concept | What is a journal entry? |
| accounting_002 | Transaction | Rent paid in cash ₹25000 |
| accounting_003 | Transaction | Rent paid in cash ₹5000 |
| accounting_004 | Accounting concept | What is a debit? |
| accounting_005 | Accounting concept | What is a credit? |
| accounting_006 | Accounting concept | What is depreciation expense? |
| accounting_007 | Unsupported | Cryptocurrency staking rewards |
| accounting_008 | Unsupported | Complex foreign currency derivative |

The dataset intentionally includes both answerable and unsupported questions.

This allows the evaluation to measure not only answer quality but also the system's ability to abstain when the knowledge base does not contain sufficient evidence.

---

## 3. Evaluation Metrics

### Pass Rate

Measures the percentage of evaluation cases that satisfy the required evaluation conditions.

### Keyword Score

Measures whether expected accounting concepts or values appear in the generated response.

Examples include:

- Debit
- Credit
- Rent Expense
- Cash
- Transaction amount
- Depreciation

### Source Score

Measures whether the retrieved sources match the expected knowledge-base sources for the evaluation case.

### Grounding Score

Measures whether the generated answer is supported by the retrieved accounting context.

This is implemented as a lightweight grounding heuristic rather than a full semantic or LLM-based judge.

### Completeness Score

Measures whether the response contains the important information expected for the evaluation case.

---

## 4. Evaluation Results

The final evaluation produced the following results:

| Metric | Result |
|---|---:|
| Pass Rate | 1.000 |
| Keyword Score | 0.917 |
| Source Score | 1.000 |
| Grounding Score | 0.613 |
| Completeness Score | 0.812 |
| Quality Gate | Passed |

The evaluation quality gate passed.

---

## 5. Interpretation

### Pass Rate

A pass rate of 1.000 indicates that all evaluation cases satisfied the defined pass conditions.

### Keyword Score

The keyword score of 0.917 indicates strong coverage of the expected accounting concepts and transaction information.

The remaining gap indicates that keyword matching should not be treated as a complete measure of response quality.

### Source Score

The source score of 1.000 indicates that the system retrieved the expected knowledge-base sources for the evaluation cases.

This provides evidence that the RAG retrieval pipeline is selecting relevant accounting material.

### Grounding Score

The grounding score of 0.613 indicates that the current lightweight grounding heuristic provides useful evidence but should not be interpreted as a definitive semantic grounding measurement.

A production system could replace this heuristic with a stronger evaluator using:

- LLM-based judging
- Human review
- Representative production examples
- Claim-level verification
- Golden-answer comparison

### Completeness Score

The completeness score of 0.812 indicates that the system generally includes the important information expected by the evaluation dataset.

Further improvement would require a larger and more diverse evaluation dataset.

---

## 6. Unsupported Question Evaluation

Unsupported questions are an important part of the evaluation.

For example:

> What is the accounting treatment for cryptocurrency staking rewards?

and:

> How should a company account for a complex foreign currency derivative?

are intentionally outside the supplied accounting knowledge.

The system is expected to respond:

> The provided accounting knowledge does not contain enough information to answer this question.

The RAG service uses an evidence gate before calling the LLM.

If sufficient evidence is not detected, the system abstains instead of generating an unsupported answer.

This provides a basic defense against hallucination.

---

## 7. Retrieval and Generation Evaluation

The RAG pipeline follows this evaluation-relevant flow:

```text
User Question
      |
      v
Embedding / Retrieval
      |
      v
Relevant Accounting Chunks
      |
      v
Evidence Sufficiency Check
      |
      +------ Insufficient Evidence ------> Abstain
      |
      v
Prompt Construction
      |
      v
Local LLM Generation
      |
      v
Response + Sources
```

The evaluation therefore measures multiple stages rather than treating the LLM output as the only component of system quality.

---

## 8. Deterministic Accounting Logic

The system combines generative AI with deterministic accounting logic.

For supported rent transactions containing both `rent` and `cash`, the application can produce a structured journal entry:

```text
Debit:  Rent Expense
Credit: Cash
```

The transaction amount is extracted from the user description.

This design intentionally separates:

- Natural-language explanation
- Retrieval
- Deterministic transaction classification
- Structured accounting output

This reduces reliance on the LLM for deterministic accounting structure.

---

## 9. Evaluation Limitations

The current evaluation is intentionally lightweight and suitable for a local portfolio implementation.

Known limitations include:

1. The evaluation dataset contains only 8 cases.
2. Keyword matching is not equivalent to semantic correctness.
3. The grounding score is a heuristic.
4. There is no human evaluation workflow yet.
5. There is no production traffic dataset.
6. Retrieval confidence is based on similarity rather than calibrated probability.
7. The deterministic classifier currently covers a limited transaction pattern.
8. Local LLM latency can be high depending on available hardware.

These limitations are documented rather than hidden.

---

## 10. Production Evaluation Evolution

A production deployment would expand evaluation into a continuous evaluation system.

A mature evaluation pipeline could include:

```text
Representative Dataset
        |
        v
Automated Evaluation
        |
        +---- Retrieval Metrics
        |
        +---- Answer Quality
        |
        +---- Grounding
        |
        +---- Safety / Abstention
        |
        +---- Latency
        |
        +---- Cost
        |
        v
Human Review
        |
        v
Production Signals
        |
        v
Evaluation Dashboard
        |
        v
Regression Detection
```

Evaluation datasets should be expanded using representative customer workflows and difficult edge cases.

Changes to prompts, retrieval logic, models, or accounting rules should be evaluated against the existing dataset before deployment.

---

## 11. Engineering Decision

The current evaluation passed its quality gate, so additional tuning was intentionally deferred.

This avoids optimizing individual evaluation cases without evidence that the change improves the overall system.

Future improvements should be driven by:

- New representative examples
- Evaluation failures
- Production signals
- Human feedback
- Retrieval failures
- Hallucination or abstention failures
- Latency and operational requirements

---

## 12. Summary

The AI Accounting Copilot uses a measurable evaluation approach rather than relying only on subjective inspection.

The current implementation demonstrates:

- Representative evaluation data
- Automated evaluation
- Retrieval evaluation
- Source verification
- Grounding measurement
- Completeness measurement
- Unsupported-question handling
- Quality gates
- Deterministic accounting logic
- Documented evaluation limitations
- A path toward continuous production evaluation

The final evaluation passed the defined quality gate with a **1.000 pass rate** and **1.000 source score**.