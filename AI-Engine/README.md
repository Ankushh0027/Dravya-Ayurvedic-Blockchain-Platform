# Dravya AI Engine

> Enterprise-grade Computer Vision and Botanical Taxonomy Classification Engine for Ayurvedic Medicinal Plant Species.

---

## Overview

**Dravya AI Engine** is a PyTorch and FastAPI-powered microservice designed for visual identification and botanical authentication of Ayurvedic medicinal plants. It serves as the automated verification gateway before raw herb batch metadata is recorded on the Dravya Blockchain ledger.

- **Primary Goal:** Prevent species substitution and adulteration in raw drug supply chains (e.g. *Saraca asoca* vs *Polyalthia longifolia*).
- **Inputs:** Digital RGB field photos of medicinal plant leaves, foliage, or specimens (JPEG, PNG, WebP, BMP up to 10 MB).
- **Outputs:** Structured JSON payload returning canonical species name, scientific taxonomy, class ID, softmax confidence score, and top-5 candidates.
- **Active Model Version:** `v1-kaggle` (PyTorch EfficientNet-B0 fine-tuned on **82 species**, achieving **98.67% test accuracy** across 2,256 held-out test images).

---

## Role in the Dravya System

```
Farmer / Herb Collector (Uploads Field Photo)
                     ↓
        Dravya Web & Mobile Platform
                     ↓
   Dravya AI Engine API (POST /predict)
                     ↓
  [Validation -> EfficientNet-B0 Inference]
                     ↓
         JSON Prediction Payload
                     ↓
 ┌───────────────────┴───────────────────┐
 ▼                                       ▼
[High Confidence >= 85%]        [Low Confidence / Flagged]
 │                                       │
 ▼                                       ▼
Auto-Passed to Blockchain       Government Botanist Verification Queue
 │                                       │
 └───────────────────┬───────────────────┘
                     ↓
        Dravya Blockchain Ledger
 (Stores Image SHA-256 Hash + Model Signature)
```

---

## Key Features

- <span style="color:green">**[IMPLEMENTED]**</span> **Production FastAPI Server:** Multi-format validation, 10MB size limit, Pillow decode verification, and thread-safe singleton model injection (`src/api/app.py`).
- <span style="color:green">**[IMPLEMENTED]**</span> **Active Deep Learning Classifier (`v1-kaggle`):** EfficientNet-B0 architecture with 5.3M parameters, 16.75 MB weight size, and 98.67% verified test accuracy.
- <span style="color:green">**[IMPLEMENTED]**</span> **SHA-256 Duplicate Audit Engine:** Scans multi-source datasets in read-only mode to prevent train/test data leakage (`src/data/duplicate_audit_v3.py`).
- <span style="color:green">**[IMPLEMENTED]**</span> **Human-in-the-Loop Botanical Review:** CLI queue engine with persistent session state and append-only audit logging (`src/data/taxonomy_review_queue.py`).
- <span style="color:green">**[IMPLEMENTED]**</span> **Model Promotion & Quality Gate:** Automatic version pointer (`models/active_model.json`) with rollback capabilities (`src/evaluation/model_promotion.py`).
- <span style="color:green">**[IMPLEMENTED]**</span> **Automated PyTest Suite:** 159 unit and integration tests covering data pipelines, models, inference, and API endpoints (`tests/`).
- <span style="color:orange">**[PLANNED]**</span> **Out-of-Distribution (OOD) Hard Thresholding:** Rejecting non-plant images via confidence cutoffs ($\tau = 0.65$).
- <span style="color:orange">**[PLANNED]**</span> **Grad-CAM Visual Explainability:** Heatmap overlays showing leaf vein feature activations.

---

## Repository Architecture

```
AI-Engine/
├── .gitignore                         # Git ignore specification
├── .env.example                       # Environment variables template
├── Dockerfile                         # Production Docker container definition
├── docker-compose.yml                 # Local & server orchestration setup
├── pyproject.toml                     # Python build metadata
├── requirements.txt                   # Dependency locks
├── verify_v1_kaggle.py                # System verification script
├── configs/
│   └── config.yaml                    # System configuration
├── docs/
│   ├── AI_ENGINE_COMPLETE_REPORT.md   # 50-Section Master Technical Report
│   ├── AI_ENGINE_QUICK_REFERENCE.md   # 2-Page Executive Quick Reference
│   └── AI_ENGINE_WALKTHROUGH.md       # Developer Onboarding Walkthrough
├── models/
│   ├── active_model.json              # Active model version pointer
│   └── v1-kaggle/                     # Production model checkpoint & mappings
├── reports/
│   ├── AI_ENGINE_PRINTABLE_PDF_REPORT.html  # Printable A4 PDF Report
│   ├── AI_ENGINE_SLIDE_PRESENTATION.html    # Interactive Slide Presentation Deck
│   ├── dataset_analysis/              # Dataset inventory & audit reports
│   └── model_evaluation/             # Model promotion & evaluation logs
├── src/
│   ├── api/                           # FastAPI routes, schemas, dependencies
│   ├── data/                          # Inventory, duplicate audit, taxonomy
│   ├── evaluation/                    # Quality gate & model promotion logic
│   ├── inference/                     # Predictor engine & batch predictor
│   ├── models/                        # PyTorch model architectures
│   └── training/                      # Training loops & dataset loaders
└── tests/                             # 159 automated PyTest unit tests
```

---

## Dataset Policy & Local Setup

> **Dataset Safety Principle:** Raw dataset images (CIMPd, Hugging_Face, Kaggle) are **NEVER committed to Git**. Raw directories are ignored in `.gitignore`.

### Dataset Storage & Placement
Raw datasets should be placed locally in `datasets/raw/` or configured via environment variables:

```text
datasets/
├── raw/               # Read-only raw datasets (CIMPd, Hugging_Face, Kaggle)
├── processed/         # Cached preprocessed tensors
└── final/             # Canonical dataset manifests
```

To run dataset inventory and duplicate audits:
```powershell
# Run physical raw inventory scan
python -m src.data.physical_inventory_v3

# Run SHA-256 duplicate audit scan
python -m src.data.duplicate_audit_v3
```

---

## Model & Evaluation Metrics

### Production Checkpoint (`v1-kaggle`)
- **Architecture:** `efficientnet_b0` (PyTorch)
- **Input Size:** `224 x 224 x 3` (RGB)
- **Classes:** 82 Canonical Medicinal Species
- **Checkpoint Path:** `models/v1-kaggle/best_model.pth` (16.75 MB)
- **Test Set Evaluation:**
  - **Total Samples:** 2,256 images
  - **Correct Predictions:** 2,226 images
  - **Overall Accuracy:** **98.67%**
  - **Best Validation Accuracy:** **99.33%**

---

## Inference API Contract

### 1. `POST /predict`
Submits a plant image for classification.

- **Content-Type:** `multipart/form-data`
- **Field Name:** `file` or `image`
- **Max File Size:** 10 MB

#### Sample JSON Response (`200 OK`)
```json
{
  "model_version": "v1-kaggle",
  "class_id": "DRAVYA_0022",
  "predicted_class": "Aloe vera",
  "species_name": "Aloe vera",
  "scientific_name": "Aloe barbadensis",
  "confidence": 0.9845,
  "top_k": [
    {
      "class_id": "DRAVYA_0022",
      "class_name": "Aloe vera",
      "confidence": 0.9845
    },
    {
      "class_id": "DRAVYA_0014",
      "class_name": "Agave",
      "confidence": 0.0082
    }
  ]
}
```

### 2. `GET /health`
Returns system health and active model metadata.
```json
{
  "status": "healthy",
  "service": "dravya-ai-engine",
  "model_version": "v1-kaggle",
  "model_loaded": true
}
```

---

## Local Setup & Commands

```powershell
# 1. Activate virtual environment
.\.venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy environment configuration
copy .env.example .env

# 4. Run System Verification Script
python verify_v1_kaggle.py

# 5. Run Complete PyTest Suite (159 tests)
pytest -o pythonpath=. -v tests/

# 6. Start Live FastAPI Server
uvicorn src.api.app:app --host 127.0.0.1 --port 8000 --reload
```

Interactive Swagger API docs available at **http://127.0.0.1:8000/docs**.

---

## Production Roadmap

- **P0 (Critical Pre-Production):**
  - Out-of-distribution (OOD) unknown plant rejection threshold ($\tau = 0.65$).
  - API Key / Bearer token authentication middleware.
- **P1 (Post-Launch Enhancements):**
  - Grad-CAM heatmap visualization in API responses.
  - ONNX runtime quantization for faster CPU inference (~15 ms).
- **P2 (Advanced MLOps):**
  - Continuous data drift monitoring and automated retraining pipelines.

---

## SIH Pitch (Smart India Hackathon)

> "Dravya AI solves species adulteration in raw drug supply chains by providing 98.67% accurate visual identification across 82 Ayurvedic medicinal plant species. Powered by an EfficientNet-B0 backbone and FastAPI, it validates images in 45 milliseconds. High-confidence predictions expedite blockchain batch logging, while low-confidence samples route to authorized government botanists for manual verification."

---

## Technical Documentation Links

- **[AI_ENGINE_COMPLETE_REPORT.md](docs/AI_ENGINE_COMPLETE_REPORT.md):** 50-Section Master Architecture & Technical Specification.
- **[AI_ENGINE_QUICK_REFERENCE.md](docs/AI_ENGINE_QUICK_REFERENCE.md):** Executive 2-Page Quick Reference Cheat Sheet.
- **[AI_ENGINE_WALKTHROUGH.md](docs/AI_ENGINE_WALKTHROUGH.md):** Developer Hands-On Onboarding Walkthrough.
- **[AI_ENGINE_PRINTABLE_PDF_REPORT.html](reports/AI_ENGINE_PRINTABLE_PDF_REPORT.html):** Printable A4 PDF Report.
- **[AI_ENGINE_SLIDE_PRESENTATION.html](reports/AI_ENGINE_SLIDE_PRESENTATION.html):** Interactive Slide Presentation Deck.
