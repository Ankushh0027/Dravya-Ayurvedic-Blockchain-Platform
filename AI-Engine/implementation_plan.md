# Dravya AI Engine Implementation Plan

## Completed Phases
- **Dataset Inventory Layer:** Deep directory scanner for raw datasets (`C:\Datasets\CIMPd`, `C:\Datasets\Hugging_Face`, `C:\Datasets\Kaggle`) discovering 42,062 image files across 331 apparent class folders.
- **Duplicate Detection / SHA-256 Hashing:** Streaming SHA-256 hash calculator and cross-dataset duplicate grouping engine preserving source provenance.
- **Taxonomy Harmonization Analysis:** String normalization, candidate match generator, and botanical taxonomy mapping analysis.
- **Canonical Taxonomy Mapping Layer:** Deterministic canonical plant entity generation (`generate_canonical_plant_id`), candidate vs approved distinction, and health condition decoupling.
- **Taxonomy Validation Layer:** Validation of canonical plant entities, mapping status invariants, and duplicate approval prevention.
- **Human Review Workflow Engine:** Audit-logged decision engine (`TaxonomyReviewEngine`) enforcing explicit `reviewer_id` and non-empty `evidence`/`review_reason`.
- **Canonical Dataset Manifest-First Builder:** Manifest generator (`CanonicalDatasetBuilder`) with SHA-256 deduplication and safety gate (`BLOCKED / NO_APPROVED_MAPPINGS`).
- **Canonical Dataset Quality Gate:** 14+ pre-training quality check suite (`DatasetQualityGate`) returning `BLOCKED` when 0 approved mappings exist.
- **Human Taxonomy Review Queue Engine:** Filterable queue engine (`TaxonomyReviewQueue`) exposing pending items, dataset/status/mapping-id filters, per-reviewer metrics, and summary progress metrics.
- **Evidence-Driven Botanical Review Analyzer:** Botanical evidence analyzer (`BotanicalReviewAnalyzer`) producing grouping reports (`reports/dataset_analysis/taxonomy_botanical_review_v1.json`) and non-binding candidate recommendations (`APPROVE_CANDIDATE`, `NEEDS_BOTANICAL_REVIEW`, `REJECT_CANDIDATE`).
- **Explicit Human Taxonomy Approval Workflow:** Complete human approval layer with atomic JSON state writes, malformed history validation, 15-field item renderer, deterministic batching (`--limit N`), and strict approval safety guarantees.
- **Canonical Dataset Builder Readiness & Dry-Run Engine:** Builder readiness engine producing dry-run reports (`reports/dataset_analysis/canonical_dataset_readiness_v1.json`).
- **Candidate-Group Review Workflow & Approval Preview Confirmation:** Candidate-group review interface (`--candidate-group PLANT-ID`, `--groups`), mandatory approval preview confirmation (`CONFIRM APPROVE? [y/N]`), default NO safety, and candidate-group progress metrics.
- **Human Review Session Safety & Resumability:** Persistent session state layer (`TaxonomyReviewSession`, `ReviewSessionManager`), reviewer isolation, `--resume`/`--pause`/`--abandon` CLI flags, atomic session JSON exports (`review_sessions_v1.json`), and crash recovery.
- **First Real Human Taxonomy Review Session:** Interactive review session (`session_v1_001` / `reviewer_001`) resulting in 4 explicit human approved mappings (`map_v1_00007`, `map_v1_00008`, `map_v1_00009`, `map_v1_00010`).
- **Human Review Completion & Dataset Generation Readiness Layer:** Completion & readiness analyzer (`HumanReviewCompletionAnalyzer`), fully reviewed candidate group classification (`FULLY_REVIEWED_GROUP`), read-only SHA-256 audit, deterministic next-group recommendations, and artifact export (`human_review_completion_readiness_v1.json`).

## Current Phase
- **Controlled Human Botanical Taxonomy Review Execution:** Real human review session active. Current real state: `APPROVED` = 4, `REJECTED` = 0, `NEEDS_REVIEW` = 231, `UNREVIEWED` = 96, `Pending` = 327. Fully reviewed candidate groups = 1 (`PLANT-CLERODENDRUM-SPLENDENS-0FC371`). Dataset Builder Readiness = `READY_FOR_PARTIAL_DATASET` (`APPROVED_MAPPINGS_AVAILABLE`).

## Next Phase
- **Continued Human Review Batches & Next Candidate Group Session:** Continued interactive human taxonomy review for high-confidence candidate plant groups (e.g. `PLANT-ALOEVERA-E8FA3C`, `PLANT-AMARANTHUS-GREEN-3330EE`, `PLANT-GUAVA-0E2715`, `PLANT-NEEM-0D12E4`).
- **Approved Mapping → Canonical Dataset Manifest Generation:** Generate canonical dataset manifest (`canonical_dataset_manifest_v1.json`) from approved mappings when human review reaches desired milestone or completion.
- **Quality Gate PASS Evaluation:** Transition Quality Gate evaluation from `BLOCKED` to `PASS`.

## Future Phases
- **Preprocessing Pipeline:** Deterministic train/validation/test split generation, leak-proof image resizing (224x224), mean/std normalization, and augmentation policy implementation.
- **Dataset Versioning:** Export versioned dataset manifests and splits.
- **EfficientNet Baseline Training:** Baseline model training on processed Dravya AI dataset splits.
- **Vision Transformer (ViT) Baseline:** ViT model training and comparative benchmarking.
- **Model Evaluation & Metrics:** Confusion matrix analysis, per-species precision/recall, and health condition classification metrics.
- **Experiment Tracking:** Logging hyperparameter configs, loss curves, and evaluation metrics.
- **Model Registry & Versioning:** Serialization and registration of trained models.
- **Inference Pipeline:** Production inference API for plant identification and health status diagnosis.
- **Rollback & State Recovery:** Production state rollback mechanism.
