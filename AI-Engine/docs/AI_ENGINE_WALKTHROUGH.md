# Dravya AI Engine — Developer Walkthrough & Practical Guide

> **Developer Walkthrough & Hands-On Guide**  
> **Repository:** `Dravya-Ayurvedic-Blockchain-Platform/AI-Engine`  
> **Audience:** Developers onboarding to the codebase  

---

## 1. Welcome to Dravya AI Engine

This document provides a step-by-step walkthrough of the Dravya AI Engine codebase. After completing this 20-minute guide, you will understand how the data pipeline, PyTorch model, FastAPI server, and testing infrastructure operate together.

---

## 2. Setting Up Your Development Environment

### Prerequisites
- Python 3.12 or Python 3.13 installed
- Git installed
- Powershell / Windows Terminal (or Linux/macOS shell)

### Setup Steps

```powershell
# 1. Navigate to AI-Engine root
cd C:\Dravya\Dravya-Ayurvedic-Blockchain-Platform\AI-Engine

# 2. Activate existing virtual environment (.venv)
.\.venv\Scripts\activate

# 3. Verify Python packages
pip list
```

---

## 3. Step-by-Step Codebase Exploration

### Step 1: Verify the Active Production Model
Inspect `models/active_model.json` to see which model version is currently serving production requests:
```powershell
Get-Content models/active_model.json
```
*Outputs: `"active_version": "v1-kaggle"`*

Now view the model metadata and evaluation report:
```powershell
Get-Content models/v1-kaggle/model_metadata.json
Get-Content models/v1-kaggle/evaluation_report.json
```

---

### Step 2: Run System Verification Script
Execute the root verification script `verify_v1_kaggle.py`. This script automatically tests:
1. Active model JSON loading
2. Model weight checkpoint existence (`best_model.pth`, 16.75 MB)
3. `PlantPredictor` initialization and dummy RGB inference
4. FastAPI `GET /health` and `POST /predict` endpoints via `TestClient`

```powershell
python verify_v1_kaggle.py
```

Expected Output:
```text
============================================================
DRAVYA AI ENGINE - KAGGLE MODEL (v1-kaggle) VERIFICATION
============================================================
[✓] Active Model Configured: v1-kaggle
[✓] Checkpoint size: 15.98 MB
[✓] Number of plant classes: 82
[✓] Architecture: efficientnet_b0
[✓] Trained device: cuda
[✓] Kaggle Test Accuracy: 98.67% (2226/2256 test images)

--- Testing PlantPredictor ---
[✓] Predictor loaded successfully on device: cpu
[✓] Prediction successful!
    - Top Predicted Class: Aloe vera
    - Top Confidence Score: 0.9845

--- Testing FastAPI API Endpoints ---
[✓] GET /health returned 200 OK
[✓] POST /predict returned 200 OK

============================================================
ALL VERIFICATION CHECKS PASSED PERFECTLY!
============================================================
```

---

### Step 3: Run the Automated Unit Test Suite
The codebase includes 159 tests covering data ingestion, duplicate auditing, PyTorch model loading, inference, and FastAPI validation.

```powershell
pytest -o pythonpath=. -v tests/
```

To run a specific module test (e.g., API routes):
```powershell
pytest -o pythonpath=. -v tests/api/test_prediction.py
```

---

### Step 4: Start and Interact with Live FastAPI Server
Launch Uvicorn in reload mode:
```powershell
uvicorn src.api.app:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser and navigate to:
- **Interactive OpenAPI Swagger Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check Endpoint:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- **HTML System Report:** [http://127.0.0.1:8000/report](http://127.0.0.1:8000/report)

---

### Step 5: Test Python Inference Client
You can run inference programmatically in Python using `PlantPredictor`:

```python
from PIL import Image
import numpy as np
from src.inference.predictor import PlantPredictor

# Initialize predictor (loads active version v1-kaggle by default)
predictor = PlantPredictor()

# Load an image
image = Image.open("datasets/sample_images/test.jpg")

# Run prediction
result = predictor.predict(image, top_k=5)

print(f"Predicted Species: {result['species_name']}")
print(f"Scientific Name:  {result['scientific_name']}")
print(f"Confidence:       {result['confidence'] * 100:.2f}%")
```

---

## 4. Understanding Key Source Code Modules

### 1. `src/api/app.py`
FastAPI application factory. Configures global middleware, CORS, docs URLs (`/docs`, `/redoc`), and leak-proof exception handlers that intercept unhandled exceptions and format them safely.

### 2. `src/api/routes/prediction.py`
Contains the `POST /predict` endpoint handler. Performs strict HTTP validation:
- Check content-type header against allowed list (`JPEG`, `PNG`, `WebP`, `BMP`)
- Check file size against 10 MB limit (`HTTP 413`)
- Execute PIL `verify()` and `convert("RGB")` to detect corrupted images (`HTTP 400`)
- Invokes `PlantPredictor` dependency to execute PyTorch forward pass

### 3. `src/inference/predictor.py`
Core inference engine:
- Reads `models/active_model.json` to identify active model directory
- Loads `class_mapping.json` (82 species) and taxonomy resolution maps
- Instantiates `PlantClassifier` architecture and loads state dict from `best_model.pth`
- Applies `get_transforms(image_size=224, is_training=False)`
- Computes `predict_proba()` and extracts Top-K candidates via `torch.topk()`

### 4. `src/models/plant_classifier.py`
PyTorch module wrapping `torchvision.models.efficientnet_b0`. Replaces standard ImageNet classifier head with custom Dropout (0.2) and Linear layer matching the 82 canonical classes.

---

## 5. Summary of Development Workflow

```
[Edit Code / Feature Branch]
             ↓
[Run Unit Tests: pytest -o pythonpath=. -v tests/]
             ↓
[Run Verification Script: python verify_v1_kaggle.py]
             ↓
[Test FastAPI Local Server: uvicorn src.api.app:app --reload]
             ↓
[Commit & Push]
```
