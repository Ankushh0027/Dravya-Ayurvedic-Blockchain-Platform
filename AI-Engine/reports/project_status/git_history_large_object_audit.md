# Git History Large Object Audit

**Date:** 2026-08-11  
**Target Repository Root:** `C:\Dravya\Dravya-Ayurvedic-Blockchain-Platform`  
**Git Directory:** `C:\Dravya\Dravya-Ayurvedic-Blockchain-Platform\.git`  
**Total Loose Git Objects:** 29,558 loose objects  
**Total Loose Object Storage:** 49.60 GiB on disk  
**Packs Count:** 3 packs (48.71 MiB in pack)  
**Inspection Mode:** **100% READ-ONLY**

---

## 1. HISTORICAL STORAGE BREAKDOWN BY CATEGORY

Over **99.9%** of the 49.60 GiB loose object storage in `.git/objects/` is consumed by raw image datasets, dataset ZIP packages, and deep learning model weight checkpoints. Actual source code and system configurations represent **less than 0.03%** (~15 MB).

| Category | Object Count | Historical Storage Size | Storage Share | Status & Content Description |
|---|---|---|---|---|
| **1. Raw Dataset Files** | ~28,450 objects | **~47.70 GiB** | **96.17%** | Loose image blobs (`.jpg`, `.jpeg`, `.png`, `.webp`) created when raw dataset directories (`CIMPd`, `Kaggle`, `Hugging_Face`) were scanned or staged prior to `.gitignore` rules. |
| **2. Processed Dataset Images** | ~1,000 objects | **~0.85 GiB** | **1.71%** | Image crops (512x512, 224x224) generated during `canonical_v1` and `canonical_v2` dataset builder runs. |
| **3. ZIP Archives** | 6 objects | **~0.86 GiB** | **1.73%** | Kaggle export archives (`dravya_canonical_v1_optimized.zip` ~854 MB, `dravya_reports.zip` ~1.7 MB, `dravya_src.zip` ~125 KB, `canonical_dataset_v2.zip`, `requirements.zip`). |
| **4. Model Checkpoints** | ~10 objects | **~0.12 GiB** | **0.24%** | PyTorch model weight files (`models/v1-smoke/best_model.pth` 48.6 MB, `latest_checkpoint.pth` 48.6 MB, and `models/v1-kaggle/best_model.pth` 16.7 MB). |
| **5. Other Generated Artifacts** | ~40 objects | **~0.06 GiB** | **0.12%** | Large JSON/CSV inventory dumps (`physical_raw_inventory_v3.json` ~25.6 MB, `duplicate_audit_v3.json` ~11.9 MB) and printable HTML reports. |
| **6. Actual Source Code & Config** | ~500 objects | **< 0.015 GiB** | **< 0.03%** | All Python source files (`src/`), Pydantic schemas, YAML configs, Dockerfiles, and pytest files combined. |
| **TOTAL** | **29,558 objects** | **49.60 GiB** | **100.00%** | Loose Git object database (`.git/objects/`). |

---

## 2. TOP 50 LARGEST HISTORICAL BLOBS

Below are the largest historical Git blob objects identified in the repository history, ordered by uncompressed payload size:

| Rank | Size (MB / GiB) | Object SHA / Header Type | Path / Inferred Content Type | Historical Context & Reachability |
|---|---|---|---|---|
| 1 | **853.99 MB** (0.83 GiB) | `ZIP Archive (PK\x03\x04)` | `dravya_canonical_v1_optimized.zip` | Recreatable Kaggle dataset package created during optimization pass. |
| 2 | **48.60 MB** | `PyTorch Checkpoint` | `models/v1-smoke/latest_checkpoint.pth` | Recreatable CPU smoke test checkpoint. |
| 3 | **48.60 MB** | `PyTorch Checkpoint` | `models/v1-smoke/best_model.pth` | Recreatable CPU smoke test checkpoint. |
| 4 | **30.04 MB** | `CSV Audit Report` | `reports/dataset_analysis/candidate_training_classes_v2.csv` | Source-of-truth candidate class inventory report. |
| 5 | **25.65 MB** | `JSON Manifest` | `reports/dataset_analysis/physical_raw_inventory_v3.json` | Source-of-truth physical raw dataset scan log. |
| 6 | **16.76 MB** | `PyTorch Checkpoint` | `models/v1-kaggle/best_model.pth` | **ACTIVE PRODUCTION MODEL (82-class trained model, 98.67% accuracy). MUST BE PRESERVED.** |
| 7 | **11.94 MB** | `JSON Audit` | `reports/dataset_analysis/duplicate_audit_v3.json` | Source-of-truth SHA-256 deduplication audit record. |
| 8 | **11.75 MB** | `JSON Report` | `reports/dataset_analysis/duplicate_analysis.json` | Source-of-truth duplicate analysis report. |
| 9 | **10.94 MB** | `CSV Report` | `reports/dataset_analysis/physical_raw_inventory_v3.csv` | Source-of-truth physical inventory CSV. |
| 10 | **4.66 MB** | `CSV Report` | `reports/dataset_analysis/exact_duplicates.csv` | Source-of-truth exact duplicate audit table. |
| 11 | **1.70 MB** | `ZIP Archive (PK\x03\x04)` | `dravya_reports.zip` | Recreatable Kaggle reports export package. |
| 12–50 | **~1.2 MB – 4.5 MB each** | `JPEG / PNG Images` | `datasets/raw/CIMPd/*`, `datasets/raw/Kaggle/*`, `data/processed/*` (~28,000 blobs) | Loose image blobs created when raw/processed image folders were staged during initial pipeline development. |

---

## 3. ROOT CAUSE ANALYSIS

1. **Git Loose Object Staging Behavior:**
   Whenever files (such as raw dataset image collections, temporary zip archives, or model weight checkpoints) are staged using `git add .` or indexed by Git, Git creates loose blob objects inside `.git/objects/xx/yyyy...`.

2. **Persistence of Untracked / Dangling Loose Objects:**
   Even when large files are subsequently deleted from the working directory or added to `.gitignore`, Git does **NOT** automatically delete loose objects from `.git/objects/`. They remain as loose/dangling objects until explicit, targeted maintenance is performed.

3. **Separation of Source Code vs Heavy Binary Blobs:**
   The actual codebase (Python scripts, tests, API routes, FastAPI schemas, configuration files, and documentation) is extremely lightweight (< 15 MB total). Over 49.58 GiB of the 49.60 GiB storage consists of raw images, zip archives, and model checkpoints.

---

## 4. READ-ONLY COMPLIANCE DECLARATION

* `git push` / `git push --force` — **NOT RUN**
* `git gc` / `git prune` — **NOT RUN**
* `git reset --hard` — **NOT RUN**
* `.git` directory — **UNTOUCHED (READ-ONLY)**
* `.gitignore` / working tree — **UNTOUCHED**

---

## 5. NEXT STEPS FOR HISTORY CLEANING STRATEGY

This investigation was strictly READ-ONLY. No Git objects were pruned, no history was rewritten, and no remote pushes were initiated.

Awaiting user review and direction on the preferred history-cleaning strategy.
