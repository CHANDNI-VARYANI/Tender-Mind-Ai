# Design Document — AI-based Tender Evaluation System (ATES)

## 1. Overview

This document describes the software architecture of the AI-based Tender Evaluation System (ATES). The system automates the evaluation of procurement tenders through a modular, pipeline-oriented architecture inspired by the Model-Component-Pipeline (MCP) pattern. Each capability is encapsulated in an independently deployable module with a well-defined interface contract. Modules communicate through asynchronous message passing and synchronous API calls depending on latency requirements.

The architecture prioritizes:

- **Auditability**: Every state transition is recorded on an immutable blockchain audit trail.
- **Security**: All artifacts are cryptographically hashed and signed; data is encrypted at rest and in transit.
- **Modularity**: Each module can be scaled, replaced, or upgraded independently.
- **Human oversight**: Automated decisions below confidence thresholds are escalated to human reviewers.
- **Reproducibility**: Identical inputs produce identical outputs across all deterministic modules.

---

## 2. System Architecture

### 2.1 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ATES — System Boundary                               │
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │  Document    │    │  OCR Engine  │    │  NLP         │                  │
│  │  Ingestion   │───▶│  (Module 1)  │───▶│  Processor   │                  │
│  │  Gateway     │    │              │    │  (Module 2)  │                  │
│  └──────────────┘    └──────────────┘    └──────┬───────┘                  │
│                                                 │                           │
│                                                 ▼                           │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │  Eligibility │◀───│  Semantic    │◀───│  Semantic    │                  │
│  │  Classifier  │    │  Match Report│    │  Matcher     │                  │
│  │  (Module 4)  │    │              │    │  (Module 3)  │                  │
│  └──────┬───────┘    └──────────────┘    └──────────────┘                  │
│         │                                                                   │
│         ▼                                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │  Review      │    │  Evaluation  │    │  Admin       │                  │
│  │  Interface   │───▶│  Report Gen  │    │  Dashboard   │                  │
│  │  (Module 7)  │    │              │    │  (Module 8)  │                  │
│  └──────────────┘    └──────┬───────┘    └──────────────┘                  │
│                             │                                               │
│         ┌───────────────────┼───────────────────┐                          │
│         ▼                   ▼                   ▼                           │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │  Crypto      │    │  Audit Chain │    │  Pipeline    │                  │
│  │  Service     │    │  (Module 5)  │    │  Orchestrator│                  │
│  │  (Module 6)  │    │  (Blockchain)│    │  (Module 9)  │                  │
│  └──────────────┘    └──────────────┘    └──────────────┘                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Pipeline Execution Flow

```
Upload ──▶ [OCR Engine] ──▶ Document Object
                                  │
                                  ▼
                         [NLP Processor] ──▶ Clause Compliance Results
                                  │
                                  ▼
                         [Semantic Matcher] ──▶ Semantic Match Report
                                  │
                                  ▼
                         [Eligibility Classifier] ──▶ Classification Result
                                  │
                    ┌─────────────┴──────────────┐
                    │ Confidence < 0.75?          │
                   YES                           NO
                    │                             │
                    ▼                             ▼
           [Review Interface]          [Report Generator]
                    │                             │
                    ▼                             ▼
           [Report Generator] ──▶ Signed Evaluation Report
                    │
                    ▼
           [Audit Chain] ◀── All stages write Audit Entries
```

---

## 3. Module Specifications

### 3.1 Module 1 — OCR Engine

**Responsibility**: Accept raw Tender documents in multiple formats and produce normalized, machine-readable Document Objects for downstream processing.

**Internal Components**:

| Component | Role |
|---|---|
| Format Detector | Identifies file type (PDF, DOCX, XLSX, image) and routes to the appropriate extractor |
| PDF Extractor | Extracts text and tables from native PDF documents using embedded text streams |
| Image OCR Processor | Applies optical character recognition to scanned pages and image-format documents |
| Office Document Parser | Extracts structured content from DOCX and XLSX files |
| Table Reconstructor | Rebuilds row-column structure from extracted table regions |
| Document Normalizer | Produces a canonical Document Object from all extractor outputs |
| Hash Generator | Computes SHA-256 Document_Hash for the original file and the Document Object |

**Inputs**:
- Raw document file (binary)
- Document metadata (uploader identity, RFP reference, upload timestamp)

**Outputs**:
- Document Object (see Section 4.1)
- Document_Hash pair (original file hash, Document Object hash)
- Extraction status (Success / Failure with error code)

**Performance Targets**:
- Extraction latency: ≤ 60 seconds per page
- OCR character accuracy: ≥ 95% on standard printed fonts
- Concurrent document capacity: ≥ 20 simultaneous documents

**Error Handling**:
- Corrupt or unreadable files: return `ERR_CORRUPT_DOCUMENT`
- Password-protected files: return `ERR_PROTECTED_DOCUMENT`
- Unsupported format: return `ERR_UNSUPPORTED_FORMAT`
- All errors are propagated to the Pipeline Orchestrator and recorded in the Audit Chain

**Audit Events Emitted**:
- `DOCUMENT_UPLOADED` — on receipt of file
- `OCR_EXTRACTION_STARTED` — on processing start
- `OCR_EXTRACTION_COMPLETED` — on successful Document Object creation
- `OCR_EXTRACTION_FAILED` — on error

---

### 3.2 Module 2 — NLP Processor

**Responsibility**: Parse the active Eligibility Ruleset and evaluate each clause against the content of a Document Object, producing per-clause compliance results with confidence scores.

**Internal Components**:

| Component | Role |
|---|---|
| Ruleset Parser | Loads and parses the versioned Eligibility Ruleset into structured rule objects |
| Clause Extractor | Identifies and extracts relevant document sections for each eligibility clause |
| Compliance Evaluator | Applies NLP classification models to determine clause compliance |
| Confidence Scorer | Assigns a Confidence_Score [0.0, 1.0] to each compliance determination |
| Escalation Detector | Flags clauses with Confidence_Score < 0.70 for human review |
| Language Adapter | Selects the appropriate language model for English, French, or Arabic rulesets |

**Inputs**:
- Document Object (from OCR Engine)
- Eligibility Ruleset (versioned, from Admin Dashboard configuration)

**Outputs**:
- NLP Compliance Result set (per-clause: Compliant / Non-Compliant / Insufficient_Evidence + Confidence_Score)
- List of flagged clauses requiring human review
- References to examined document sections for each clause

**Performance Targets**:
- Processing latency: ≤ 120 seconds per Tender
- Supported languages: English, French, Arabic

**Error Handling**:
- Missing Ruleset version: return `ERR_RULESET_NOT_FOUND` to Pipeline Orchestrator
- Model inference failure: retry up to 2 times, then return `ERR_NLP_INFERENCE_FAILED`

**Audit Events Emitted**:
- `NLP_EVALUATION_STARTED`
- `NLP_EVALUATION_COMPLETED`
- `NLP_CLAUSE_FLAGGED` — for each low-confidence clause
- `NLP_EVALUATION_FAILED`

---

### 3.3 Module 3 — Semantic Matcher

**Responsibility**: Compute semantic similarity scores between Tender content and RFP criteria using vector-space embedding models, producing a Semantic Match Report.

**Internal Components**:

| Component | Role |
|---|---|
| Embedding Model Registry | Manages domain-specific and language-specific embedding models |
| Document Vectorizer | Converts Tender sections into high-dimensional embedding vectors |
| Criteria Vectorizer | Converts RFP criteria into embedding vectors |
| Similarity Calculator | Computes cosine similarity between Tender and criteria vectors |
| Score Aggregator | Applies criterion weights from the Eligibility Ruleset to compute the aggregate weighted score |
| Gap Analyzer | Identifies Tender excerpts and unmatched criteria for scores below 0.50 |

**Inputs**:
- Document Object (from OCR Engine)
- RFP criteria set with weights (from Eligibility Ruleset)
- Domain category and language configuration

**Outputs**:
- Semantic Match Report (see Section 4.3)
- Per-criterion similarity scores [0.0, 1.0]
- Aggregate weighted score [0.0, 1.0]
- Gap analysis entries for low-scoring criteria

**Performance Targets**:
- Processing latency: ≤ 90 seconds per Tender
- Score determinism: identical inputs must produce identical scores

**Embedding Model Selection**:
- Models are selected per RFP category (construction, IT services, healthcare, general)
- Multilingual RFPs use language-aligned cross-lingual embedding models
- Model versions are pinned per Eligibility Ruleset version to ensure reproducibility

**Audit Events Emitted**:
- `SEMANTIC_MATCHING_STARTED`
- `SEMANTIC_MATCHING_COMPLETED`
- `SEMANTIC_MATCHING_FAILED`

---

### 3.4 Module 4 — Eligibility Classifier

**Responsibility**: Combine NLP compliance results and semantic scores to produce a definitive, auditable classification of each Bidder as Eligible, Conditionally_Eligible, or Ineligible.

**Internal Components**:

| Component | Role |
|---|---|
| Classification Engine | Applies deterministic classification rules to compliance and score inputs |
| Confidence Aggregator | Computes an overall Confidence_Score for the Classification Result |
| Escalation Router | Routes low-confidence results to the Review Interface |
| Rationale Builder | Constructs a structured rationale record from all contributing inputs |

**Classification Logic**:

```
IF any mandatory clause == Non-Compliant
  → Ineligible (regardless of aggregate score)

ELSE IF any mandatory clause == Insufficient_Evidence AND no mandatory clause == Non-Compliant
  → Conditionally_Eligible (list flagged clauses)

ELSE IF all mandatory clauses == Compliant AND aggregate_score >= RFP_threshold
  → Eligible

ELSE
  → Ineligible (score below threshold)

IF overall_confidence < 0.75
  → Escalate to Review Interface (mandatory human action)
```

**Inputs**:
- NLP Compliance Result set
- Semantic Match Report
- RFP classification thresholds (from Eligibility Ruleset)

**Outputs**:
- Classification Result (see Section 4.4)
- Escalation flag and reason (if applicable)

**Audit Events Emitted**:
- `CLASSIFICATION_STARTED`
- `CLASSIFICATION_COMPLETED`
- `CLASSIFICATION_ESCALATED` — when confidence < 0.75
- `CLASSIFICATION_FAILED`

---

### 3.5 Module 5 — Audit Chain

**Responsibility**: Maintain an append-only, cryptographically linked chain of Audit Entries recording every significant system event, providing an immutable and independently verifiable audit trail.

**Internal Components**:

| Component | Role |
|---|---|
| Entry Builder | Constructs Audit Entry objects from event data |
| Chain Linker | Computes the hash of the preceding entry and embeds it in the new entry |
| Persistence Layer | Writes entries to append-only storage isolated from the primary database |
| Chain Verifier | Traverses the chain and validates hash linkage for integrity checks |
| Query Engine | Retrieves entries by Tender ID, RFP ID, event type, or time range |
| Export Service | Serializes chain subsets to JSON or CSV for regulatory reporting |

**Hash Chain Structure**:

```
Entry[0]: { event, actor, timestamp, artifact_hash, prev_hash: "GENESIS" }
              │
              └─ SHA-256(Entry[0]) ──▶ Entry[1].prev_hash
                                            │
                                            └─ SHA-256(Entry[1]) ──▶ Entry[2].prev_hash
                                                                          │
                                                                          └─ ...
```

Any modification to a historical entry changes its hash, breaking the chain link and making tampering detectable during verification.

**Storage Requirements**:
- Append-only storage (no UPDATE or DELETE operations permitted at the storage layer)
- Physically and logically separated from the primary application database
- Replicated to at least two geographically distinct storage nodes

**Performance Targets**:
- Entry write latency: ≤ 500ms
- Query response for chains up to 100,000 entries: ≤ 5 seconds
- Chain integrity verification: ≤ 60 seconds for 100,000 entries

**Audit Events Emitted**: The Audit Chain does not emit events to itself. All other modules write to it.

---

### 3.6 Module 6 — Crypto Service

**Responsibility**: Provide all cryptographic operations for the system including document hashing, digital signing, signature verification, symmetric encryption/decryption, and key lifecycle management.

**Internal Components**:

| Component | Role |
|---|---|
| Hash Engine | Computes SHA-256 digests for documents and structured artifacts |
| Signing Service | Signs artifacts using asymmetric keys (RSA-4096 or ECDSA P-384) |
| Verification Service | Verifies digital signatures and returns verification status |
| Encryption Service | Encrypts/decrypts data at rest using AES-256-GCM |
| TLS Enforcer | Enforces TLS 1.3 minimum for all inter-module and external communications |
| Key Manager | Interfaces with the Key Management Service (KMS) for key retrieval and rotation |
| HSM Adapter | Optional adapter for Hardware Security Module integration in production |

**Key Management Architecture**:

```
┌─────────────────────────────────────────────────────┐
│                  Key Management Service              │
│                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  Signing    │  │  Encryption │  │  Key        │ │
│  │  Key Pair   │  │  Master Key │  │  Rotation   │ │
│  │  (per ATES  │  │  (AES-256)  │  │  Scheduler  │ │
│  │  instance)  │  │             │  │             │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │  HSM (optional, production deployments)     │   │
│  │  Private keys never leave HSM boundary      │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

**Key Storage Rules**:
- Private keys MUST NOT be stored in application configuration files or environment variables
- In production, private keys MUST reside in HSM or a dedicated KMS (e.g., AWS KMS, HashiCorp Vault)
- Key rotation events MUST trigger re-signing of all artifacts signed with the retired key
- All key operations MUST be logged to the Audit Chain

**Cryptographic Standards**:

| Operation | Algorithm |
|---|---|
| Document hashing | SHA-256 |
| Digital signing | RSA-4096 or ECDSA P-384 |
| Symmetric encryption (at rest) | AES-256-GCM |
| Transport security | TLS 1.3 minimum |
| Key derivation | PBKDF2 or Argon2id |

**Audit Events Emitted**:
- `ARTIFACT_HASHED`
- `ARTIFACT_SIGNED`
- `SIGNATURE_VERIFIED`
- `SIGNATURE_VERIFICATION_FAILED`
- `KEY_ROTATED`
- `ARTIFACT_RESIGNED` — on key rotation

---

### 3.7 Module 7 — Review Interface

**Responsibility**: Provide Human Reviewers with a structured workspace to inspect automated evaluation results, annotate findings, override decisions with justification, request re-processing, and approve final Evaluation Reports.

**Internal Components**:

| Component | Role |
|---|---|
| Review Queue Manager | Manages assignment and prioritization of Tenders requiring human review |
| Notification Service | Delivers review assignments to reviewers within 60 seconds of escalation |
| Evaluation Viewer | Presents consolidated Document Object, NLP results, Semantic Match Report, and Classification Result |
| Annotation Engine | Stores free-text reviewer annotations (up to 2,000 characters) per clause |
| Override Controller | Validates and records classification overrides with mandatory justification |
| Re-processing Trigger | Initiates re-processing of a Tender through selected pipeline modules |
| Approval Workflow | Manages the approval state machine and triggers Evaluation Report generation |
| RBAC Enforcer | Enforces role-based access control limiting reviewers to their assigned queue |
| Concurrency Manager | Handles optimistic locking to prevent data conflicts across concurrent reviewers |

**Review State Machine**:

```
PENDING_REVIEW
     │
     ▼
IN_REVIEW (reviewer opens Tender)
     │
     ├──▶ ANNOTATED (reviewer adds annotations)
     │
     ├──▶ OVERRIDDEN (reviewer overrides classification)
     │         │
     │         ▼
     │    OVERRIDE_RECORDED (Audit Chain write confirmed)
     │
     ├──▶ REPROCESSING_REQUESTED
     │         │
     │         ▼
     │    [Returns to pipeline, then back to PENDING_REVIEW]
     │
     └──▶ APPROVED (reviewer approves)
               │
               ▼
         REPORT_GENERATION_TRIGGERED
```

**Override Requirements**:
- Reviewer must select an override reason from a predefined list
- Reviewer must provide justification text of at least 50 characters
- Override is written to Audit Chain before Classification Result is updated
- Original automated result is preserved in the Audit Chain permanently

**Concurrency**:
- Supports ≥ 50 concurrent Human Reviewers
- Optimistic locking on Tender review records prevents conflicting updates
- Conflict resolution: last-write-wins with full audit trail of all writes

**Audit Events Emitted**:
- `REVIEW_ASSIGNED`
- `REVIEW_OPENED`
- `ANNOTATION_ADDED`
- `CLASSIFICATION_OVERRIDDEN` — includes original result, override value, reason, justification
- `REPROCESSING_REQUESTED`
- `REVIEW_APPROVED`

---

### 3.8 Module 8 — Admin Dashboard

**Responsibility**: Provide system administrators with centralized configuration management, real-time operational monitoring, user and role management, Eligibility Ruleset lifecycle management, and reporting capabilities.

**Internal Components**:

| Component | Role |
|---|---|
| Monitoring Aggregator | Collects and aggregates health metrics from all modules every ≤ 30 seconds |
| Alert Engine | Detects module unavailability and surfaces alerts within 30 seconds |
| User Manager | CRUD operations for user accounts and role assignments |
| Ruleset Manager | Create, version, activate, and deactivate Eligibility Rulesets |
| Threshold Configurator | Manages per-module processing thresholds without system restart |
| Report Generator | Produces operational reports for configurable date ranges |
| Audit Chain Inspector | Triggers and displays results of Audit Chain integrity checks |
| MFA Enforcer | Enforces multi-factor authentication for all administrator sessions |

**Monitored Metrics per Module**:

| Metric | Refresh Interval |
|---|---|
| Module availability (up/down) | ≤ 30 seconds |
| Average processing latency | ≤ 30 seconds |
| Error rate (errors/minute) | ≤ 30 seconds |
| Queue depth (pending items) | ≤ 30 seconds |
| Active Tender count by pipeline stage | ≤ 30 seconds |

**Eligibility Ruleset Lifecycle**:

```
DRAFT ──▶ REVIEW ──▶ ACTIVE
                        │
                        ▼
                   SUPERSEDED (when a new version is activated)
                        │
                        ▼
                   ARCHIVED (after retention period)
```

- Only one Ruleset version may be ACTIVE per RFP at any time
- Activation events are recorded in the Audit Chain with administrator identity and previous version reference
- Deactivated Rulesets are retained for audit purposes and cannot be deleted

**Configurable Thresholds** (no restart required):
- NLP Confidence_Score escalation threshold (default: 0.70)
- Classification Confidence_Score escalation threshold (default: 0.75)
- Aggregate score pass threshold per RFP
- Maximum end-to-end pipeline processing time
- OCR retry count and backoff parameters

**Operational Reports**:
- Tender volume by RFP, date range, and classification outcome
- Classification distribution (Eligible / Conditionally_Eligible / Ineligible)
- Average processing time per module and end-to-end
- Reviewer workload and override frequency
- Audit Chain integrity check history

**Audit Events Emitted**:
- `ADMIN_LOGIN`
- `USER_CREATED` / `USER_UPDATED` / `USER_DEACTIVATED`
- `RULESET_CREATED` / `RULESET_ACTIVATED` / `RULESET_DEACTIVATED`
- `THRESHOLD_UPDATED`
- `AUDIT_CHAIN_INTEGRITY_CHECK_TRIGGERED`

---

### 3.9 Module 9 — Pipeline Orchestrator

**Responsibility**: Coordinate the end-to-end execution of the evaluation pipeline for each Tender, managing sequencing, retry logic, error handling, timeout enforcement, and status reporting.

**Internal Components**:

| Component | Role |
|---|---|
| Job Scheduler | Accepts new Tender processing jobs and places them in the persistent queue |
| Stage Sequencer | Executes pipeline stages in the defined order, passing outputs as inputs |
| Retry Manager | Implements exponential backoff retry logic for failed stages |
| Timeout Monitor | Tracks elapsed time per Tender and enforces the configurable maximum |
| Status API | Exposes current pipeline stage, elapsed time, and error details per Document_ID |
| Failure Handler | Marks Tenders as Processing_Failed and notifies the Admin Dashboard |
| Persistent Queue | Durable job queue that survives system restarts |

**Pipeline Stage Sequence**:

```
Stage 1: OCR_Engine.extract(document)
Stage 2: NLP_Processor.evaluate(document_object, ruleset)
Stage 3: Semantic_Matcher.score(document_object, criteria)
Stage 4: Eligibility_Classifier.classify(nlp_results, semantic_report)
Stage 5 (conditional): Review_Interface.assign(classification_result)  [if escalated]
Stage 6: ReportGenerator.generate(classification_result, review_outcome)
```

Stages 2 and 3 may execute in parallel if the NLP Processor and Semantic Matcher are both ready and the Document Object is available.

**Retry Policy**:
- Maximum retries per stage: 3
- Backoff: 2^attempt seconds (2s, 4s, 8s)
- After 3 failures: mark Tender as `Processing_Failed`, notify Admin Dashboard, record in Audit Chain

**Timeout Policy**:
- Configurable maximum end-to-end time (default: 30 minutes)
- On timeout: escalate Tender to Review Interface with reason `PIPELINE_TIMEOUT`

**Persistent Queue Requirements**:
- Queue state persists across planned and unplanned system restarts
- No Tender job is lost during downtime
- Queue supports at-least-once delivery semantics with idempotent stage handlers

**Audit Events Emitted**:
- `PIPELINE_STARTED`
- `STAGE_STARTED` / `STAGE_COMPLETED` / `STAGE_FAILED` / `STAGE_RETRIED`
- `PIPELINE_COMPLETED`
- `PIPELINE_FAILED`
- `PIPELINE_TIMEOUT_ESCALATED`

---

## 4. Data Models

### 4.1 Document Object

The Document Object is the canonical, normalized representation of a Tender document produced by the OCR Engine. It is the primary data artifact passed between pipeline modules.

```
DocumentObject {
  document_id:        string          // Unique identifier assigned by OCR Engine
  rfp_reference:      string          // RFP this Tender is submitted against
  bidder_id:          string          // Submitting Bidder identifier
  upload_timestamp:   ISO8601         // UTC timestamp of original upload
  original_file_hash: string          // SHA-256 of the original uploaded file
  object_hash:        string          // SHA-256 of this Document Object
  source_format:      enum            // PDF | DOCX | XLSX | PNG | JPEG | TIFF
  pages: [
    {
      page_number:    integer
      text_blocks: [
        {
          block_id:   string
          content:    string          // Extracted text
          bbox:       BoundingBox     // Position on page (for image-sourced pages)
          confidence: float           // OCR confidence [0.0, 1.0] (image pages only)
        }
      ]
      tables: [
        {
          table_id:   string
          rows: [
            { cells: [string] }
          ]
        }
      ]
    }
  ]
  metadata: {
    language_detected:  string        // ISO 639-1 language code
    page_count:         integer
    extraction_model:   string        // OCR model version used
    extraction_duration_ms: integer
  }
}
```

---

### 4.2 Eligibility Ruleset

The Eligibility Ruleset is a versioned, machine-readable specification of the evaluation criteria for a given RFP.

```
EligibilityRuleset {
  ruleset_id:         string
  rfp_reference:      string
  version:            string          // Semantic version e.g. "2.1.0"
  status:             enum            // DRAFT | REVIEW | ACTIVE | SUPERSEDED | ARCHIVED
  language:           string          // ISO 639-1 primary language
  domain_category:    string          // e.g. "construction", "it_services", "healthcare"
  score_threshold:    float           // Minimum aggregate score for Eligible classification
  created_by:         string          // Administrator identity
  activated_at:       ISO8601 | null
  clauses: [
    {
      clause_id:      string
      clause_text:    string          // Human-readable clause description
      is_mandatory:   boolean         // Mandatory clauses trigger Ineligible on Non-Compliant
      evaluation_hints: [string]      // Keywords/phrases to guide NLP evaluation
    }
  ]
  criteria: [
    {
      criterion_id:   string
      criterion_text: string
      weight:         float           // Contribution to aggregate score (weights sum to 1.0)
      domain_model:   string          // Embedding model identifier for this criterion
    }
  ]
}
```

---

### 4.3 Semantic Match Report

```
SemanticMatchReport {
  report_id:          string
  document_id:        string
  ruleset_id:         string
  ruleset_version:    string
  generated_at:       ISO8601
  aggregate_score:    float           // Weighted aggregate [0.0, 1.0]
  criterion_scores: [
    {
      criterion_id:   string
      score:          float           // [0.0, 1.0]
      tender_excerpt: string | null   // Relevant Tender text (populated if score < 0.50)
      gap_note:       string | null   // Unmatched criterion description (if score < 0.50)
    }
  ]
  embedding_models_used: [string]     // Model identifiers used for reproducibility
}
```

---

### 4.4 Classification Result

```
ClassificationResult {
  result_id:              string
  document_id:            string
  bidder_id:              string
  rfp_reference:          string
  classification:         enum        // Eligible | Conditionally_Eligible | Ineligible
  confidence_score:       float       // [0.0, 1.0]
  is_escalated:           boolean
  escalation_reason:      string | null
  aggregate_score:        float
  mandatory_clause_results: [
    {
      clause_id:          string
      result:             enum        // Compliant | Non_Compliant | Insufficient_Evidence
      confidence:         float
    }
  ]
  rationale:              string      // Structured explanation of classification decision
  automated_at:           ISO8601
  human_review: {
    reviewer_id:          string | null
    reviewed_at:          ISO8601 | null
    override_applied:     boolean
    override_reason:      string | null
    override_justification: string | null
    annotations: [
      {
        clause_id:        string
        annotation_text:  string
        annotated_at:     ISO8601
      }
    ]
  }
}
```

---

### 4.5 Audit Entry

```
AuditEntry {
  entry_id:           string          // Monotonically increasing identifier
  event_type:         string          // e.g. "OCR_EXTRACTION_COMPLETED"
  actor_id:           string          // System module ID or Human Reviewer/Admin ID
  actor_type:         enum            // SYSTEM | HUMAN_REVIEWER | ADMINISTRATOR
  timestamp:          ISO8601         // UTC
  tender_id:          string | null   // Associated Tender (if applicable)
  rfp_reference:      string | null
  artifact_hash:      string | null   // SHA-256 of associated artifact
  event_payload:      object          // Event-specific structured data
  prev_entry_hash:    string          // SHA-256 of preceding AuditEntry (or "GENESIS")
  entry_hash:         string          // SHA-256 of this AuditEntry (computed on write)
}
```

---

### 4.6 Evaluation Report

```
EvaluationReport {
  report_id:              string
  document_id:            string
  bidder_id:              string
  bidder_name:            string
  rfp_reference:          string
  generated_at:           ISO8601
  approved_by:            string      // Human Reviewer ID or "AUTOMATED"
  classification:         enum        // Eligible | Conditionally_Eligible | Ineligible
  confidence_score:       float
  aggregate_score:        float
  clause_results:         [...]       // From ClassificationResult
  criterion_scores:       [...]       // From SemanticMatchReport
  reviewer_annotations:   [...]       // From ClassificationResult.human_review
  override_record:        object | null
  report_hash:            string      // SHA-256 of report content
  digital_signature:      string      // Base64-encoded signature
  signing_key_id:         string      // Key identifier for signature verification
  available_formats:      [enum]      // PDF | JSON
  retention_expires_at:   ISO8601     // 7 years from generation date
}
```

---

## 5. Inter-Module Communication Contracts

### 5.1 Communication Patterns

| Interaction | Pattern | Rationale |
|---|---|---|
| Document upload → OCR Engine | Synchronous REST | Immediate acknowledgment required |
| OCR Engine → Pipeline Orchestrator | Async message (queue) | Decouples extraction from downstream |
| Pipeline Orchestrator → NLP Processor | Async message (queue) | Enables retry and backoff |
| Pipeline Orchestrator → Semantic Matcher | Async message (queue) | Parallel execution with NLP |
| NLP + Semantic → Eligibility Classifier | Async message (queue) | Waits for both results |
| Eligibility Classifier → Review Interface | Async message (queue) | Conditional escalation |
| Any module → Audit Chain | Async fire-and-forget | Non-blocking audit writes |
| Any module → Crypto Service | Synchronous RPC | Blocking hash/sign operations |
| Admin Dashboard → all modules | Synchronous REST | Configuration reads/writes |
| Status queries → Pipeline Orchestrator | Synchronous REST | Real-time status polling |

### 5.2 Module Interface Contracts

#### OCR Engine Interface

```
POST /ocr/extract
  Request:  { file: binary, metadata: DocumentMetadata }
  Response: { document_id: string, status: "ACCEPTED" | "REJECTED", error?: ErrorObject }

GET /ocr/status/{document_id}
  Response: { document_id, status: "PROCESSING" | "COMPLETED" | "FAILED", document_object?: DocumentObject }
```

#### NLP Processor Interface

```
Message: NLPEvaluationRequest {
  document_id:    string
  document_object: DocumentObject
  ruleset_id:     string
  ruleset_version: string
}

Message: NLPEvaluationResult {
  document_id:    string
  clause_results: [ClauseResult]
  flagged_clauses: [string]
  status:         "COMPLETED" | "FAILED"
  error?:         ErrorObject
}
```

#### Semantic Matcher Interface

```
Message: SemanticMatchRequest {
  document_id:    string
  document_object: DocumentObject
  ruleset_id:     string
  ruleset_version: string
}

Message: SemanticMatchResponse {
  document_id:    string
  report:         SemanticMatchReport
  status:         "COMPLETED" | "FAILED"
  error?:         ErrorObject
}
```

#### Eligibility Classifier Interface

```
Message: ClassificationRequest {
  document_id:      string
  nlp_results:      NLPEvaluationResult
  semantic_report:  SemanticMatchReport
  ruleset_id:       string
}

Message: ClassificationResponse {
  document_id:      string
  result:           ClassificationResult
  status:           "COMPLETED" | "ESCALATED" | "FAILED"
}
```

#### Audit Chain Interface

```
POST /audit/entry
  Request:  AuditEntry (without entry_hash and prev_entry_hash — computed by Audit Chain)
  Response: { entry_id: string, entry_hash: string }

GET /audit/entries?tender_id={id}&rfp={ref}&from={ts}&to={ts}
  Response: { entries: [AuditEntry], total: integer }

POST /audit/verify
  Response: { status: "PASS" | "FAIL", first_inconsistency_index?: integer }

GET /audit/export?format=json|csv&tender_id={id}
  Response: file download
```

#### Crypto Service Interface

```
POST /crypto/hash
  Request:  { artifact: object | binary }
  Response: { hash: string }

POST /crypto/sign
  Request:  { artifact_hash: string, artifact_type: string }
  Response: { signature: string, key_id: string }

POST /crypto/verify
  Request:  { artifact_hash: string, signature: string, key_id: string }
  Response: { valid: boolean, status: "VALID" | "INVALID" | "KEY_NOT_FOUND" }

POST /crypto/encrypt
  Request:  { data: binary, context: string }
  Response: { ciphertext: binary, key_version: string }

POST /crypto/decrypt
  Request:  { ciphertext: binary, key_version: string, context: string }
  Response: { data: binary }
```

#### Pipeline Orchestrator Status API

```
GET /pipeline/status/{document_id}
  Response: {
    document_id:    string,
    current_stage:  string,
    elapsed_ms:     integer,
    status:         "PROCESSING" | "COMPLETED" | "FAILED" | "ESCALATED",
    error?:         ErrorObject
  }
```

---

## 6. Deployment Architecture

### 6.1 Containerized Microservices

Each module is deployed as an independent containerized service. The deployment model follows a microservices architecture with the following characteristics:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Container Orchestration Layer                 │
│                    (e.g., Kubernetes)                           │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  ocr-engine  │  │ nlp-processor│  │sem-matcher   │         │
│  │  (1-N pods)  │  │  (1-N pods)  │  │  (1-N pods)  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  eligibility │  │  audit-chain │  │crypto-service│         │
│  │  -classifier │  │  (1-3 pods)  │  │  (1-N pods)  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │review-iface  │  │admin-dashboard│ │  pipeline-   │         │
│  │  (1-N pods)  │  │  (1-3 pods)  │  │ orchestrator │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Message Broker (e.g., Apache Kafka / RabbitMQ)          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Primary DB  │  │  Audit Store │  │  Object      │         │
│  │  (App data)  │  │  (Append-    │  │  Storage     │         │
│  │              │  │   only)      │  │  (Documents) │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 Scaling Strategy

| Module | Scaling Trigger | Scaling Unit |
|---|---|---|
| OCR Engine | Queue depth > 10 | Horizontal pod scaling |
| NLP Processor | Queue depth > 5 | Horizontal pod scaling |
| Semantic Matcher | Queue depth > 5 | Horizontal pod scaling |
| Eligibility Classifier | Queue depth > 10 | Horizontal pod scaling |
| Crypto Service | CPU > 70% | Horizontal pod scaling |
| Audit Chain | Write latency > 1s | Vertical scaling + read replicas |
| Review Interface | Active reviewer sessions | Horizontal pod scaling |
| Pipeline Orchestrator | Fixed 2-3 replicas | Leader election for job scheduling |

### 6.3 Data Storage Separation

| Data Type | Storage | Isolation |
|---|---|---|
| Document Objects | Object storage (encrypted) | Separate bucket/container |
| Application state | Primary relational database | Standard HA cluster |
| Audit Chain entries | Append-only database | Physically separate instance |
| Cryptographic keys | KMS / HSM | External to application cluster |
| Evaluation Reports | Object storage (encrypted) | Separate bucket with 7-year retention |
| Embedding models | Model registry | Read-only volume mounts |

---

## 7. Security Architecture

### 7.1 Defense-in-Depth Layers

```
Layer 1: Network
  - TLS 1.3 for all inter-module and external communications
  - Network policies restricting inter-pod communication to defined routes
  - API gateway with rate limiting and request validation at the ingress

Layer 2: Authentication and Authorization
  - Service-to-service: mutual TLS (mTLS) with short-lived certificates
  - Human users: JWT-based authentication with MFA for administrators
  - RBAC: role-based access control enforced at the Review Interface and Admin Dashboard
  - Principle of least privilege: each module has access only to its required resources

Layer 3: Data Protection
  - At rest: AES-256-GCM encryption for all documents and artifacts
  - In transit: TLS 1.3 minimum
  - Key management: dedicated KMS, HSM for production private keys
  - No secrets in configuration files or environment variables

Layer 4: Integrity
  - SHA-256 hashing of all documents and artifacts at creation
  - Digital signatures on all Evaluation Reports
  - Blockchain hash chain for tamper-evident audit trail
  - Signature verification before serving any signed artifact

Layer 5: Auditability
  - Immutable append-only Audit Chain for all system events
  - Audit Chain stored separately from application data
  - Chain integrity verification available on demand
  - All cryptographic operations logged
```

### 7.2 Threat Model Summary

| Threat | Mitigation |
|---|---|
| Document tampering after upload | SHA-256 hash stored at upload; verified before each processing stage |
| Evaluation result manipulation | Digital signatures on Classification Results and Evaluation Reports |
| Audit trail falsification | Blockchain hash chain; append-only storage; physical separation |
| Unauthorized access to Tenders | RBAC; reviewers limited to assigned queue; mTLS between services |
| Key compromise | HSM for private keys; key rotation with re-signing; rotation logged |
| Replay attacks | Nonce and timestamp validation on all signed requests |
| Insider threat | Audit Chain records all human actions with identity; MFA for admins |
| Model poisoning | Embedding models are versioned and pinned; model registry is read-only |

---

## 8. Correctness Properties

This section defines the key correctness properties that should be verified for each module. These inform both automated testing strategy and manual review criteria.

### 8.1 OCR Engine

| Property | Type | Description |
|---|---|---|
| Hash consistency | Invariant | Document_Hash of the original file is identical on every re-computation from the same file |
| Extraction idempotence | Idempotence | Processing the same document twice produces identical Document Objects |
| Format rejection completeness | Error condition | Every unsupported or corrupt file returns a structured error; no silent failures |
| Table structure preservation | Invariant | Row count and column count in extracted tables match the source document |

### 8.2 NLP Processor

| Property | Type | Description |
|---|---|---|
| Ruleset version binding | Invariant | Every NLP result references the exact Ruleset version used; version never changes mid-evaluation |
| Confidence score range | Invariant | All Confidence_Scores are in [0.0, 1.0] |
| Escalation completeness | Invariant | Every clause with Confidence_Score < 0.70 appears in the flagged_clauses list |
| Missing ruleset error | Error condition | A missing Ruleset version always returns ERR_RULESET_NOT_FOUND; never produces a partial result |

### 8.3 Semantic Matcher

| Property | Type | Description |
|---|---|---|
| Score determinism | Invariant | Identical Document Object + Ruleset inputs always produce identical scores |
| Score range | Invariant | All per-criterion scores and aggregate score are in [0.0, 1.0] |
| Weight normalization | Invariant | Sum of criterion weights in any Eligibility Ruleset equals 1.0 |
| Gap analysis completeness | Invariant | Every criterion with score < 0.50 has a corresponding gap_note entry |

### 8.4 Eligibility Classifier

| Property | Type | Description |
|---|---|---|
| Mandatory Non-Compliant → Ineligible | Invariant | Any Non-Compliant mandatory clause always results in Ineligible, regardless of aggregate score |
| Classification exhaustiveness | Invariant | Every Classification Result is exactly one of Eligible, Conditionally_Eligible, Ineligible |
| Escalation threshold | Invariant | Every result with overall Confidence_Score < 0.75 has is_escalated == true |
| Rationale completeness | Invariant | Every Classification Result includes all contributing clause results and scores |

### 8.5 Audit Chain

| Property | Type | Description |
|---|---|---|
| Append-only | Invariant | No UPDATE or DELETE operations succeed on existing entries |
| Hash chain integrity | Invariant | For all entries i > 0: entry[i].prev_entry_hash == SHA-256(entry[i-1]) |
| Tamper detection | Round-trip | Modifying any historical entry causes chain verification to return FAIL |
| Entry completeness | Invariant | Every pipeline state transition produces exactly one Audit Entry |

### 8.6 Crypto Service

| Property | Type | Description |
|---|---|---|
| Hash determinism | Invariant | SHA-256(x) always equals SHA-256(x) for identical inputs |
| Sign-verify round-trip | Round-trip | verify(sign(hash, key), hash, key) always returns VALID |
| Tamper detection | Round-trip | verify(sign(hash, key), modified_hash, key) always returns INVALID |
| Encrypt-decrypt round-trip | Round-trip | decrypt(encrypt(data, key), key) == data for all valid data and keys |
| Integrity compromise propagation | Error condition | Any artifact with a failed signature verification is marked Integrity_Compromised before use |

### 8.7 Review Interface

| Property | Type | Description |
|---|---|---|
| Override audit precedence | Invariant | Audit Chain write always completes before Classification Result is updated on override |
| Justification minimum length | Invariant | No override is accepted with justification text shorter than 50 characters |
| Queue isolation | Invariant | A reviewer can never access a Tender not in their assigned queue |
| Concurrency safety | Invariant | Concurrent updates to the same Tender record never produce a silent data conflict |

### 8.8 Pipeline Orchestrator

| Property | Type | Description |
|---|---|---|
| No Tender loss | Invariant | Every Tender in the persistent queue is processed to completion or marked Processing_Failed |
| Retry bound | Invariant | No stage is retried more than 3 times before the Tender is marked Processing_Failed |
| Stage ordering | Invariant | Eligibility Classifier never starts before both NLP and Semantic Matcher have completed |
| Failure notification | Invariant | Every Processing_Failed Tender produces an Admin Dashboard alert and an Audit Chain entry |

---

## 9. Glossary Cross-Reference

All terms used in this design document are defined in the Glossary section of the Requirements Document (`requirements.md`). Module names, data model field names, and event type strings in this document use the exact terminology defined there to ensure consistency across the specification.

---

*End of Design Document*
