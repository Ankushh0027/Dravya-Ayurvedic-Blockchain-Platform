import sys
from pathlib import Path
import json

# Ensure AI-Engine directory is in python path
ai_engine_dir = Path(__file__).resolve().parent
if str(ai_engine_dir) not in sys.path:
    sys.path.insert(0, str(ai_engine_dir))

from PIL import Image
import numpy as np

def run_verification():
    print("=" * 60)
    print("DRAVYA AI ENGINE - KAGGLE MODEL (v1-kaggle) VERIFICATION")
    print("=" * 60)

    # 1. Verify Active Model Config
    active_model_path = ai_engine_dir / "models" / "active_model.json"
    assert active_model_path.exists(), f"Active model json missing: {active_model_path}"
    with open(active_model_path, "r", encoding="utf-8") as f:
        active_config = json.load(f)
    active_version = active_config.get("active_version")
    print(f"[✓] Active Model Configured: {active_version}")

    # 2. Check Model Version Artifacts
    version_dir = ai_engine_dir / "models" / active_version
    checkpoint_path = version_dir / "best_model.pth"
    class_map_path = version_dir / "class_mapping.json"
    eval_report_path = version_dir / "evaluation_report.json"
    metadata_path = version_dir / "model_metadata.json"

    assert checkpoint_path.exists(), f"Checkpoint missing: {checkpoint_path}"
    assert class_map_path.exists(), f"Class mapping missing: {class_map_path}"
    assert eval_report_path.exists(), f"Eval report missing: {eval_report_path}"
    assert metadata_path.exists(), f"Metadata missing: {metadata_path}"

    with open(class_map_path, "r", encoding="utf-8") as f:
        class_map = json.load(f)
    num_classes = len(class_map.get("class_to_idx", {}))

    with open(eval_report_path, "r", encoding="utf-8") as f:
        eval_report = json.load(f)

    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    print(f"[✓] Checkpoint size: {checkpoint_path.stat().st_size / (1024*1024):.2f} MB")
    print(f"[✓] Number of plant classes: {num_classes}")
    print(f"[✓] Architecture: {metadata.get('architecture')}")
    print(f"[✓] Trained device: {metadata.get('device')}")
    print(f"[✓] Kaggle Test Accuracy: {eval_report.get('test_accuracy', 0)*100:.2f}% ({eval_report.get('correct_test_predictions')}/{eval_report.get('total_test_samples')} test images)")

    # 3. Test PlantPredictor
    print("\n--- Testing PlantPredictor ---")
    from src.inference.predictor import PlantPredictor
    predictor = PlantPredictor(version=active_version)
    print(f"[✓] Predictor loaded successfully on device: {predictor.device}")

    # Dummy test image (224x224 RGB)
    test_img = Image.fromarray(np.uint8(np.random.randint(0, 255, (224, 224, 3))))
    prediction = predictor.predict(test_img, top_k=5)
    
    print(f"[✓] Prediction successful!")
    print(f"    - Top Predicted Class: {prediction['canonical_name']}")
    print(f"    - Top Confidence Score: {prediction['confidence']}")
    print(f"    - Top 5 Predictions:")
    for pred in prediction['top_k']:
        print(f"        * {pred['class_name']}: {pred['confidence']:.4f}")

    # 4. Test FastAPI Server Endpoints
    print("\n--- Testing FastAPI API Endpoints ---")
    from fastapi.testclient import TestClient
    from src.api.app import create_app
    
    app = create_app()
    client = TestClient(app)

    # Test /health
    response = client.get("/health")
    assert response.status_code == 200, f"Health endpoint failed: {response.text}"
    health_data = response.json()
    print(f"[✓] GET /health returned 200 OK:")
    print(f"    - status: {health_data.get('status')}")
    print(f"    - active_model_version: {health_data.get('active_model_version')}")
    print(f"    - num_classes: {health_data.get('num_classes')}")

    # Test /predict endpoint
    import io
    img_byte_arr = io.BytesIO()
    test_img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)

    files = {"file": ("test.jpg", img_byte_arr, "image/jpeg")}
    response = client.post("/predict", files=files)
    assert response.status_code == 200, f"Predict endpoint failed: {response.text}"
    predict_data = response.json()
    print(f"[✓] POST /predict returned 200 OK:")
    print(f"    - canonical_name: {predict_data.get('canonical_name')}")
    print(f"    - confidence: {predict_data.get('confidence')}")
    print(f"    - model_version: {predict_data.get('model_version')}")

    print("\n" + "=" * 60)
    print("ALL VERIFICATION CHECKS PASSED PERFECTLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_verification()
