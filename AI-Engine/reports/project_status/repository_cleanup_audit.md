# DRAVYA AI ENGINE — SAFE REPOSITORY CLEANUP & UNUSED FILE AUDIT REPORT

**Date:** 2026-08-11  
**Target Repository:** Dravya AI Engine (`c:\Dravya\Dravya-Ayurvedic-Blockchain-Platform\AI-Engine`)  
**Audit Purpose:** Perform a comprehensive dependency/usage audit, identify generated/obsolete files, and safely reduce repository size and complexity while maintaining 100% production functionality and test coverage.

---

## 1. REPOSITORY METRICS SUMMARY

| Metric | Before Cleanup | After Proposed Cleanup | Difference |
|---|---|---|---|
| **Total Python Files** | 109 files | 106 files | -3 files |
| **Approximate Python LOC** | ~15,200 LOC | ~15,035 LOC | -165 LOC |
| **Generated Zip Archives** | 6 archives (856.4 MB) | 0 archives (0 MB) | -856.4 MB |
| **Temporary Checkpoints** | 2 files (97.2 MB) | 0 files (0 MB) | -97.2 MB |
| **Total Disk Space Reclaimed** | ~953.6 MB | 0 MB | **~953.6 MB Reclaimed** |
| **Test Files Retained** | 40 / 40 tests (100%) | 40 / 40 tests (100%) | 0 tests removed |
| **Production Architecture** | **100% PRESERVED** | **100% PRESERVED** | **ZERO BREAKING CHANGES** |

---

## 2. FILE CLASSIFICATION SUMMARY

Every file in the repository was analyzed across CLI references, imports, dynamic loading, configuration, test coverage, and documentation references:

- **Category A — REQUIRED (Production Core):**  
  FastAPI server (`src/api/`), PyTorch Classifier (`src/models/plant_classifier.py`), Inference Engine (`src/inference/predictor.py`), Active Version Manager (`src/models/version_manager.py`), Active Production Model (`models/v1-kaggle/`). **All Retained.**

- **Category B — DEVELOPMENT SUPPORT (Data Pipeline, Training, Verification):**  
  Dataset inventory, deduplication, taxonomy review, preprocessing, dataset builder, model quality gate, trainer CLI, and Kaggle verification (`verify_v1_kaggle.py`). **All Retained.**

- **Category C — DOCUMENTATION & SOURCE-OF-TRUTH REPORTS:**  
  All 46 dataset analysis JSON/CSV/MD reports, model promotion audit logs (`promotions.json`), HTML printable reports, walkthroughs, and architecture docs. **All Retained.**

- **Category D — GENERATED / RECREATABLE (Deletion Candidates):**  
  Temporary zip archives (`*.zip`), temporary CPU smoke checkpoints (`models/v1-smoke/*.pth`), Pytest cache (`.pytest_cache/`), and Python bytecode caches (`__pycache__/`). **Targeted for Safe Cleanup.**

- **Category E — OBSOLETE / UNUSED (Deletion Candidates):**  
  Obsolete single-use debug scripts with 0 imports/references and empty packages. **Targeted for Deletion.**

---

## 3. PROPOSED DELETION LIST & REASONING

### A. Obsolete / Unused Source Files (Category E)

1. **`src/data/audit_taxonomy_135.py`**
   - **Reason:** Temporary diagnostic script created to investigate a specific issue ("Why physical_inventory_v3.py reported APPROVED CLASSES FOUND: 10"). No references in production code, CLI, tests, configs, or documentation. Superseded by `physical_inventory_v3.py` and `combined_inventory_v2.py`.
   - **Safe to Delete:** YES

2. **`src/training/create_torch_pth.py`**
   - **Reason:** Mock `.pth` generator script using zero-byte padding. Superseded by real PyTorch state_dict checkpoint building in `build_smoke_checkpoint.py` and `trainer.py`. No references in production, CLI, tests, configs, or documentation.
   - **Safe to Delete:** YES

3. **`src/audit/__init__.py`** (and directory `src/audit/`)
   - **Reason:** Empty package directory containing a 3-byte empty `__init__.py` created in an earlier phase. Zero imports or references anywhere in the repository (`src.audit`).
   - **Safe to Delete:** YES

### B. Generated Zip Packaging Archives (Category D)

4. **`canonical_dataset_v2.zip`** (907 bytes)
   - **Reason:** Temporary packaging zip artifact created by `create_kaggle_zips.py`. Ignored by `.gitignore`. Recreatable via script.
   - **Safe to Delete:** YES

5. **`dravya_canonical_v1_optimized.zip`** (853,990,606 bytes = ~854 MB)
   - **Reason:** Large temporary packaging zip artifact created by `create_optimized_kaggle_dataset.py`. Ignored by `.gitignore`. Recreatable via script.
   - **Safe to Delete:** YES

6. **`dravya_configs.zip`** (632 bytes)
   - **Reason:** Temporary packaging zip artifact created by `create_kaggle_zips.py`. Ignored by `.gitignore`. Recreatable via script.
   - **Safe to Delete:** YES

7. **`dravya_reports.zip`** (1,703,627 bytes)
   - **Reason:** Temporary packaging zip artifact created by `create_kaggle_zips.py`. Ignored by `.gitignore`. Recreatable via script.
   - **Safe to Delete:** YES

8. **`dravya_src.zip`** (125,187 bytes)
   - **Reason:** Temporary packaging zip artifact created by `create_kaggle_zips.py`. Ignored by `.gitignore`. Recreatable via script.
   - **Safe to Delete:** YES

9. **`requirements.zip`** (472 bytes)
   - **Reason:** Temporary packaging zip artifact created by `create_kaggle_zips.py`. Ignored by `.gitignore`. Recreatable via script.
   - **Safe to Delete:** YES

### C. Temporary Smoke Checkpoints (Category D)

10. **`models/v1-smoke/best_model.pth`** (48,597,304 bytes)
    - **Reason:** Temporary CPU smoke test weights generated during initial testing. Recreatable anytime via `python -m src.training.run_smoke_training`. Ignored by `.gitignore`. (Active model `models/v1-kaggle/best_model.pth` is fully preserved).
    - **Safe to Delete:** YES

11. **`models/v1-smoke/latest_checkpoint.pth`** (48,604,339 bytes)
    - **Reason:** Temporary CPU smoke test weights generated during initial testing. Recreatable anytime via `python -m src.training.run_smoke_training`. Ignored by `.gitignore`.
    - **Safe to Delete:** YES

### D. Temporary Caches (Category D)

12. **`.pytest_cache/`** (Directory)
    - **Reason:** Pytest cache artifact. Recreatable on next pytest execution. Ignored by `.gitignore`.
    - **Safe to Delete:** YES

13. **`__pycache__/`** (Directories across `src/` and `tests/`)
    - **Reason:** Python bytecode cache files. Recreatable automatically by Python interpreter. Ignored by `.gitignore`.
    - **Safe to Delete:** YES

---

## 4. PROTECTED COMPONENT AUDIT & CONFIRMATION

| Component Area | Status | Files Retained | Verification |
|---|---|---|---|
| `src/data/` | **PROTECTED** | 40 files | Dataset inventory, duplicate audit, taxonomy, review session, dataset builder |
| `src/models/` | **PROTECTED** | 4 files | `plant_classifier.py`, `config.py`, `version_manager.py` |
| `src/training/` | **PROTECTED** | 10 files | `dataset.py`, `trainer.py`, `metrics.py`, `run_smoke_training.py`, `run_v2_gpu_smoke.py`, `verify_trained_kaggle_model.py` |
| `src/evaluation/` | **PROTECTED** | 5 files | `evaluator.py`, `model_promotion.py`, `quality_gate.py`, `run_evaluation.py` |
| `src/inference/` | **PROTECTED** | 3 files | `predictor.py`, `batch_predictor.py` |
| `src/api/` | **PROTECTED** | 6 files | `app.py`, `dependencies.py`, `schemas.py`, `health.py`, `prediction.py` |
| `src/utils/` | **PROTECTED** | 1 file | `__init__.py` |
| `configs/` | **PROTECTED** | 1 file | `config.yaml` |
| `models/` | **PROTECTED** | Active Model `v1-kaggle` | `active_model.json`, `best_model.pth` (16.7MB), `class_mapping.json` |
| `tests/` | **PROTECTED** | 40 files | All test files preserved without modification |

---

## 5. GITIGNORE ENHANCEMENTS

The file `c:\Dravya\Dravya-Ayurvedic-Blockchain-Platform\AI-Engine\.gitignore` was updated to explicitly include `runs/` under generated operational logs:

```gitignore
# Generated Operational Reports & Logs
reports/generated/
*.log
logs/
runs/
```

This prevents future accidental commits of TensorBoard or training run outputs.

---

## 6. CONCLUSION & SAFETY DECLARATION

- **Zero Breaking Changes:** No active production code, CLI runner, test, configuration, or documentation reference was modified or broken.
- **Repository Integrity:** Production model `v1-kaggle` remains active and ready for REST API serving.
- **Cleanliness Achieved:** Identified ~953.6 MB of recreatable zip archives, temporary smoke weights, and obsolete Python files for removal.

---

## 7. FINAL CLEANUP RESULT

### Files Deleted & Reclaimed:

1. `src/data/audit_taxonomy_135.py` (97 lines, 4.0 KB) — Deleted
2. `src/training/create_torch_pth.py` (66 lines, 2.2 KB) — Deleted
3. `src/audit/__init__.py` & directory `src/audit/` (2 lines, 3 bytes) — Deleted
4. `canonical_dataset_v2.zip` (907 bytes) — Deleted
5. `dravya_canonical_v1_optimized.zip` (853,990,606 bytes = ~854 MB) — Deleted
6. `dravya_configs.zip` (632 bytes) — Deleted
7. `dravya_reports.zip` (1,703,627 bytes) — Deleted
8. `dravya_src.zip` (125,187 bytes) — Deleted
9. `requirements.zip` (472 bytes) — Deleted
10. `models/v1-smoke/best_model.pth` (48.6 MB) — Deleted
11. `models/v1-smoke/latest_checkpoint.pth` (48.6 MB) — Deleted
12. `.pytest_cache/` (Directory) — Deleted
13. `__pycache__/` (Bytecode cache subdirectories) — Deleted

### Actual Metrics & Test Results:
- **Python Files Before:** 109 files  
- **Python Files After Cleanup:** 106 files  
- **Python LOC Reduction:** -165 LOC (~15,200 -> ~15,035 LOC)  
- **Disk Space Freed:** ~953.6 MB  
- **Test Suite Results:** **213 PASSED, 1 SKIPPED (214 items collected)** in 69.15s  

### Protected Production Files:
`src/data/` (40 files), `src/models/` (4 files), `src/training/` (10 files), `src/evaluation/` (5 files), `src/inference/` (3 files), `src/api/` (6 files), `src/utils/` (1 file), `configs/` (1 file), `docs/` (3 files), `reports/dataset_analysis/` (46 files), `reports/model_evaluation/` (4 files) — **100% PRESERVED**

### Active Model:
`models/v1-kaggle/` — **PRESERVED** (`active_model.json`, `best_model.pth` 16.7MB, `class_mapping.json`, `evaluation_report.json`, `model_metadata.json`)

### Breaking Changes:
**NONE**

### GitHub Push:
**NOT PERFORMED**


