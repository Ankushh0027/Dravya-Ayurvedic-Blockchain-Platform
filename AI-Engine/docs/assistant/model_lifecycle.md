# Dravya — Model Lifecycle, Versioning & Data Governance

## 1. Model Registry & Version Management
The Dravya AI Engine implements strict version control and promotion gates for deep learning models:
- **Active Model Pointer (`models/active_model.json`)**: Authoritative JSON file designating the current promoted model version (e.g. `v1-kaggle`).
- **Version Isolation (`models/<version_id>/`)**: Each version maintains its own checkpoint (`best_model.pth`), canonical class mapping (`class_mapping.json`), and model metadata (`model_metadata.json`).

## 2. Quality Gate & Promotion Workflow
Before any candidate model checkpoint is promoted to production:
1. **Pre-Training Data Audit**: SHA-256 duplicate auditing (`src/data/duplicate_audit_v3.py`) ensures 0% data leakage across train, validation, and test splits.
2. **Human-in-the-Loop Botanical Review**: CLI queue (`src/data/taxonomy_review_queue.py`) requires expert approval of all raw source class mappings.
3. **Automated Evaluation Gate**: Candidate models must exceed minimum accuracy thresholds ($\ge 95.0\%$ overall test accuracy, $\ge 90.0\%$ per-class minimum recall).
4. **Atomic Pointer Promotion**: `ModelPromoter` updates `active_model.json` atomically and logs promotion history to `reports/model_evaluation/promotion_history.json`.
5. **Instant Rollback**: If runtime degradation is detected, `ModelPromoter.rollback_promotion()` reverts the active version pointer to the prior stable release without container redeployment.
