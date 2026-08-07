# Dravya AI Engine

Dravya AI is an enterprise-grade artificial intelligence engine designed for robust data processing, taxonomy harmonization, auditable human review, leak-proof dataset creation, model training, evaluation, and real-time inference.

---

## 🏛️ End-to-End Production Data Pipeline Architecture

```text
Raw Datasets (Immutable C:\Datasets)
    ↓
1. Dataset Inventory Scanner
    ↓
2. Duplicate Detection / SHA-256
    ↓
3. Taxonomy Harmonization Analysis
    ↓
4. Canonical Taxonomy Mapping (v1)
    ↓
5. Evidence-Driven Botanical Review Analyzer
    ↓
6. Candidate-Group Human Review Queue Engine & CLI
    ↓
7. Persistent Resumable Human Review Session Layer
    ↓
8. Explicit Human Taxonomy Approval Protocol (2-Step Preview Confirmation)
    ↓
9. Real Human Taxonomy Review Execution (4 APPROVED Mappings)
    ↓
10. Human Review Completion & Dataset Generation Readiness Layer
    ↓
11. Canonical Dataset Builder Readiness Engine (READY_FOR_PARTIAL_DATASET State)
    ↓
12. Pre-Training Canonical Dataset Quality Gate
    ↓
Future: Canonical Dataset Generation Manifest Export
    ↓
Future: Preprocessing & Deterministic Splitter
    ↓
Future: Model Training
    ↓
Future: Evaluation & Metrics
    ↓
Future: Model Registry & Versioning
```

---

## 📊 Current Real Project Status Metrics

* **Taxonomy Mappings:** 331
* **Candidate Plant Groups:** 200
* **Approved Mappings (Human):** 4 *(Explicitly approved: map_v1_00007, map_v1_00008, map_v1_00009, map_v1_00010)*
* **Rejected Mappings:** 0
* **NEEDS_REVIEW Mappings:** 231
* **UNREVIEWED Mappings:** 96
* **Pending Mappings:** 327 (98.79%)
* **Reviewed Mappings:** 4 (1.21%)
* **Fully Reviewed Candidate Groups:** 1 (`PLANT-CLERODENDRUM-SPLENDENS-0FC371`)
* **Pending Candidate Groups:** 199
* **Approved Source Images Scanned:** 1,092 images (read-only SHA-256 verified)
* **Dataset Builder Readiness:** `READY_FOR_PARTIAL_DATASET` (`APPROVED_MAPPINGS_AVAILABLE`)
* **Raw Datasets State:** `100% READ-ONLY` (`C:\Datasets\CIMPd`, `C:\Datasets\Hugging_Face`, `C:\Datasets\Kaggle` untouched)
* **Python Runtime:** Python 3.13.9 (`.venv`)
* **Automated Unit Tests:** 159 passed out of 159 (`pytest -o pythonpath=. -v tests/data`)

---

## 🛡️ Core Pipeline Architecture & Safety Guarantees

### 1. Data Safety & Immutability
All raw dataset files under `C:\Datasets\CIMPd`, `C:\Datasets\Hugging_Face`, and `C:\Datasets\Kaggle` are **100% read-only and immutable**. Dravya AI Engine code will **never** rename, move, delete, resize, overwrite, convert, or physically copy files within raw dataset directories. No raw images are copied, moved, or modified by the current pipeline.

### 2. Candidate-Group Workflow & Health Condition Decoupling
* **Candidate-Group Review Convenience:** Related source mappings across datasets (e.g. `Ashok.H`, `Ashok.U`, `ashok`) are grouped under candidate canonical plant identities (`PLANT-SARACA-ASOCA-4B8F7A`) for holistic botanical review.
* **Strict Individual Decision Requirement:** Grouping is a display convenience only. Grouping **NEVER** auto-approves mappings. Every mapping requires an explicit human review decision.
* **Health Condition Separation:** Health conditions (`Healthy`, `Unhealthy`, `Unknown`) remain strictly decoupled from plant identity and are **never** embedded in `canonical_plant_id`.

### 3. Human Review Session Layer & Resumability (`src/data/review_session.py`)
* **Persistent Session State:** Manages long-running review sessions (`ACTIVE`, `PAUSED`, `COMPLETED`, `ABANDONED`) tracking reviewed mapping IDs, skipped mapping IDs, approved/rejected/needs-review IDs, and navigation state.
* **Reviewer Isolation Safety:** Prevents a reviewer from accessing or resuming another reviewer's active or paused session (`reviewer_id` mismatch raises explicit `ValueError`).
* **Candidate-Group & Filter Resume:** Resumes deterministically at the exact pending item/candidate-group where the reviewer paused.
* **Atomic Session Persistence:** Session artifacts (`reports/dataset_analysis/review_sessions_v1.json`) are persisted via atomic JSON writes (`.tmp` → target file) ensuring zero file corruption upon unexpected termination.

### 4. Human Review Completion & Readiness Analyzer (`src/data/review_completion.py`)
* **Completion Progress Tracking:** Evaluates reviewed vs pending mappings and calculates fully reviewed candidate plant groups vs pending candidate plant groups (`FULLY_REVIEWED_GROUP` classification).
* **Read-Only SHA-256 & Source Verification:** Audits approved mappings by scanning source image files and computing SHA-256 digests in 100% read-only mode.
* **Deterministic Next-Review Recommendations:** Prioritizes candidate plant groups with binomial scientific names, multi-source mappings, and pending items.

### 5. Explicit Approval Confirmation & Audit History (`src/data/taxonomy_review.py`, `src/data/run_taxonomy_review_queue.py`)
* **Mandatory Preview & Confirmation:** Every `APPROVE` action displays an explicit confirmation prompt (`CONFIRM APPROVE? [y/N]`) defaulting to **NO**. Approvals are only committed upon explicit `y`/`yes` response.
* **Mandatory Approval Inputs:** Approval requires valid `mapping_id`, non-empty `reviewer_id`, non-empty `evidence`/`review_reason`, and a valid existing `canonical_plant_id`.
* **Append-Only Audit History:** Every explicit decision appends an immutable record (`decision_id`, `mapping_id`, `reviewer_id`, `decision`, `previous_status`, `new_status`, `evidence`, `timestamp`) to `taxonomy_review_history_v1.json`. Historical records are never deleted or overwritten.

---

## 🛠️ CLI Usage Guide

### Review Completion & Readiness Report Command
```bash
# Export and display human review completion & dataset generation readiness report
python -m src.data.run_taxonomy_review_queue --version v1 --completion-readiness
```

### Review Session Commands
```bash
# Launch a new interactive review session for reviewer_001
python -m src.data.run_taxonomy_review_queue --version v1 --reviewer-id reviewer_001 --session-id session_v1_001 --interactive --limit 10

# Resume an existing paused review session deterministically
python -m src.data.run_taxonomy_review_queue --version v1 --reviewer-id reviewer_001 --session-id session_v1_001 --resume --interactive

# Pause an active review session
python -m src.data.run_taxonomy_review_queue --version v1 --session-id session_v1_001 --pause

# View global review sessions overview
python -m src.data.run_taxonomy_review_queue --version v1 --session-summary
```

---

## 🧪 Testing

Execute the complete automated unit test suite (159 passed tests):
```bash
pytest -o pythonpath=. -v tests/data
```

---

## 📁 Versioned Artifacts Summary

All generated report artifacts are saved under `reports/dataset_analysis/`:
* `human_review_completion_readiness_v1.json` (Completion & dataset generation readiness report)
* `review_sessions_v1.json` (Human review session persistence & status log)
* `canonical_dataset_readiness_v1.json` (Dataset builder readiness & dry-run report)
* `taxonomy_botanical_review_v1.json` (Evidence-driven botanical recommendations report)
* `taxonomy_review_progress_v1.json` (Human review progress, session metrics, & per-reviewer summary)
* `taxonomy_review_v1.json` (Latest human review mapping state)
* `taxonomy_review_history_v1.json` (Append-only review audit history)
* `canonical_taxonomy_v1.json` (Canonical plant entities v1)
* `canonical_dataset_manifest_v1.json` (Canonical dataset manifest v1)
* `canonical_dataset_quality_report_v1.json` (Pre-training quality gate report)
