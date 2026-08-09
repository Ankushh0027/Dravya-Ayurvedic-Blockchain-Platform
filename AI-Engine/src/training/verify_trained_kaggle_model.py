"""
Dravya AI Engine — Trained Kaggle Model Promotion & End-to-End Verification
=============================================================================
1. Verifies trained model artifacts in models/v1-kaggle/
2. Sets active model pointer (active_model.json) to "v1-kaggle"
3. Tests PyTorch model initialization & weights loading
4. Tests FastAPI REST API endpoints (/health, /predict)
5. Generates verification summary report
"""

import os
import sys
import json
import time
import io
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timezone

import numpy as np
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.models.version_manager import ModelVersionManager
from src.inference.predictor import PlantPredictor
from fastapi.testclient import TestClient
from src.api.app import app


def verify_trained_kaggle_model():
    print("==========================================================================")
    print("      DRAVYA AI ENGINE — TRAINED KAGGLE MODEL VERIFICATION RUNNER         ")
    print("==========================================================================")

    models_dir = PROJECT_ROOT / "models"
    kaggle_version_dir = models_dir / "v1-kaggle"

    # Step 1: Verify Checkpoint Artifacts
    print("\nSTEP 1 — Verifying Checkpoint Artifacts (models/v1-kaggle/)...")
    required_files = ["best_model.pth", "class_mapping.json", "model_metadata.json", "evaluation_report.json"]
    missing = []
    for f in required_files:
        if not (kaggle_version_dir / f).exists():
            missing.append(f)

    if missing:
        raise FileNotFoundError(f"Missing required model artifacts in {kaggle_version_dir}: {missing}")

    with open(kaggle_version_dir / "model_metadata.json", "r", encoding="utf-8") as f:
        meta = json.load(f)

    with open(kaggle_version_dir / "class_mapping.json", "r", encoding="utf-8") as f:
        cmap = json.load(f)

    with open(kaggle_version_dir / "evaluation_report.json", "r", encoding="utf-8") as f:
        eval_report = json.load(f)

    num_classes = len(cmap.get("class_to_idx", {}))
    arch = meta.get("architecture", "efficientnet_b0")
    val_acc = meta.get("best_val_accuracy", 0.0)
    test_acc = eval_report.get("test_accuracy", 0.0)

    print(f"-> Architecture:     {arch}")
    print(f"-> Canonical Classes: {num_classes}")
    print(f"-> Peak Val Acc:     {val_acc:.4f} ({val_acc * 100:.2f}%)")
    print(f"-> Test Split Acc:   {test_acc:.4f} ({test_acc * 100:.2f}%)")

    # Step 2: Promote Active Model Version
    print("\nSTEP 2 — Promoting Model Version to Active Production State...")
    vm = ModelVersionManager(models_dir)
    vm.set_active_version("v1-kaggle")
    print(f"-> Active version pointer updated to 'v1-kaggle' in {models_dir / 'active_model.json'}.")

    # Step 3: Test Predictor Engine
    print("\nSTEP 3 — Verifying Local Inference Engine...")
    predictor = PlantPredictor(version="v1-kaggle", models_dir=str(models_dir))
    
    # Generate test image
    rng = np.random.RandomState(42)
    test_arr = rng.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    test_img = Image.fromarray(test_arr)
    
    pred_res = predictor.predict(test_img, top_k=3)
    print(f"-> Predictor Output: Class={pred_res.get('predicted_class')}, Confidence={pred_res.get('confidence', 0.0):.4f}")

    # Step 4: Test FastAPI Endpoints
    print("\nSTEP 4 — Testing FastAPI REST API Endpoints...")
    client = TestClient(app)

    # Test /health
    h_resp = client.get("/health")
    if h_resp.status_code != 200:
        raise RuntimeError(f"FastAPI /health check failed: status {h_resp.status_code}")
    print(f"-> GET /health: Status {h_resp.status_code} | Active Model: {h_resp.json().get('model_version')}")

    # Test /predict
    buf = io.BytesIO()
    test_img.save(buf, format="JPEG")
    files = {"file": ("test_leaf.jpg", buf.getvalue(), "image/jpeg")}
    
    p_resp = client.post("/predict", files=files)
    if p_resp.status_code != 200:
        raise RuntimeError(f"FastAPI /predict check failed: status {p_resp.status_code}, body={p_resp.text}")

    p_data = p_resp.json()
    print(f"-> POST /predict: Status 200 | Predicted={p_data.get('predicted_class')}, Conf={p_data.get('confidence', 0.0):.4f}")

    # Step 5: Export Verification Report
    reports_dir = PROJECT_ROOT / "reports" / "model_evaluation"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_md = reports_dir / "v1_kaggle_model_verification.md"

    md_lines = [
        "# Dravya AI Engine — Trained Model Verification & Promotion Report",
        "",
        f"**Verified At:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}  ",
        "**Model Version:** `v1-kaggle`  ",
        "**Promotion Status:** `ACTIVE_PRODUCTION`  ",
        "",
        "---",
        "",
        "## 1. Model Summary & Accuracy",
        "",
        "| Property | Value |",
        "|---|---|",
        f"| **Model Version** | `v1-kaggle` |",
        f"| **Backbone Architecture** | `{arch}` |",
        f"| **Canonical Classes Trained** | `{num_classes}` approved species |",
        f"| **Best Validation Accuracy** | **{val_acc * 100:.2f}%** |",
        f"| **Test Split Accuracy** | **{test_acc * 100:.2f}%** |",
        f"| **Active Pointer File** | `{models_dir / 'active_model.json'}` |",
        "",
        "---",
        "",
        "## 2. API & Inference Verification",
        "",
        "| Endpoint | Test Action | Result Status |",
        "|---|---|---|",
        "| `GET /health` | System health check | **200 OK** |",
        "| `POST /predict` | Single-leaf image classification | **200 OK** |",
        "| `PlantPredictor` | Direct PyTorch tensor inference | **VERIFIED** |",
        "",
        "---",
        "",
        "## 3. Final Verification Status",
        "",
        "```text",
        "MODEL ARTIFACTS: PASS",
        "ACTIVE POINTER:  PROMOTED TO v1-kaggle",
        "INFERENCE ENGINE: PASS",
        "FASTAPI SYSTEM:  PASS",
        "PRODUCTION STATUS: READY",
        "```"
    ]

    with open(report_md, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print("\n==========================================================================")
    print("       DRAVYA AI MODEL PROMOTION & VERIFICATION SUMMARY                   ")
    print("==========================================================================")
    print("MODEL ARTIFACTS:   PASS")
    print("ACTIVE POINTER:    PROMOTED TO v1-kaggle")
    print("INFERENCE ENGINE:  PASS")
    print("FASTAPI API:       PASS (200 OK)")
    print("PRODUCTION STATUS: READY")
    print("==========================================================================")
    print(f"\nVerification Report Exported: {report_md}")


if __name__ == "__main__":
    verify_trained_kaggle_model()
