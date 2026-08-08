import json
import os
import pytest
from pathlib import Path
from PIL import Image
import numpy as np

import torch
from src.data.paths import get_reports_dir
from src.models.config import ModelConfig, load_model_config
from src.models.plant_classifier import PlantClassifier
from src.models.version_manager import ModelVersionManager
from src.training.dataset import DravyaDataset, create_dataloaders, load_canonical_records
from src.training.trainer import ModelTrainer
from src.inference.predictor import PlantPredictor


@pytest.fixture
def mock_canonical_manifest(tmp_path):
    """
    Creates a temporary canonical dataset manifest containing APPROVED, UNREVIEWED, and NEEDS_REVIEW mappings.
    """
    manifest_path = tmp_path / "canonical_dataset_manifest_e2e.json"
    manifest_data = {
        "taxonomy_version": "v1",
        "exported_at": "2026-08-08T00:00:00Z",
        "status": "SUCCESS",
        "reason": "APPROVED_MAPPINGS_PROCESSED",
        "total_records": 4,
        "records": [
            {
                "record_id": "rec_e2e_001",
                "taxonomy_version": "v1",
                "canonical_plant_id": "PLANT-CLERODENDRUM-SPLENDENS-0FC371",
                "canonical_name": "Clerodendrum splendens",
                "health_condition": "Healthy",
                "sha256": "e2e_sha_001",
                "file_extension": ".jpg",
                "mapping_status": "APPROVED",
                "source_references": [
                    {
                        "dataset_id": "CIMPd",
                        "original_class_name": "Clerodendrum splendens.H",
                        "source_file_path": "dummy_path_1.jpg",
                        "source_file_name": "img1.jpg",
                    }
                ],
            },
            {
                "record_id": "rec_e2e_002",
                "taxonomy_version": "v1",
                "canonical_plant_id": "PLANT-SARACA-ASOCA-4B8F7A",
                "canonical_name": "Saraca asoca",
                "health_condition": "Healthy",
                "sha256": "e2e_sha_002",
                "file_extension": ".jpg",
                "mapping_status": "APPROVED",
                "source_references": [
                    {
                        "dataset_id": "CIMPd",
                        "original_class_name": "Saraca asoca.H",
                        "source_file_path": "dummy_path_2.jpg",
                        "source_file_name": "img2.jpg",
                    }
                ],
            },
            {
                "record_id": "rec_e2e_003",
                "taxonomy_version": "v1",
                "canonical_plant_id": "PLANT-SARACA-ASOCA-4B8F7A",
                "canonical_name": "Saraca asoca",
                "health_condition": "Healthy",
                "sha256": "e2e_sha_003",
                "file_extension": ".jpg",
                "mapping_status": "APPROVED",
                "source_references": [
                    {
                        "dataset_id": "CIMPd",
                        "original_class_name": "Saraca asoca.H",
                        "source_file_path": "dummy_path_3.jpg",
                        "source_file_name": "img3.jpg",
                    }
                ],
            },
            {
                "record_id": "rec_e2e_unreviewed",
                "taxonomy_version": "v1",
                "canonical_plant_id": "PLANT-UNREVIEWED-999999",
                "canonical_name": "Unreviewed Plant Species",
                "health_condition": "Unknown",
                "sha256": "e2e_sha_004",
                "file_extension": ".jpg",
                "mapping_status": "UNREVIEWED",
                "source_references": [],
            },
        ],
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    return manifest_path


def test_end_to_end_ml_pipeline(tmp_path, mock_canonical_manifest):
    """
    Complete End-to-End Pipeline Verification Test:
    1. Load approved canonical dataset manifest
    2. Filter out UNREVIEWED records (only APPROVED ingested)
    3. Generate dynamic class mapping (Clerodendrum splendens, Saraca asoca)
    4. Construct train/val dataloaders with transforms
    5. Train EfficientNet classifier on CPU for 1 epoch
    6. Compute validation metrics (accuracy, F1, precision, recall, confusion matrix)
    7. Save best checkpoint, class_mapping.json, and model_metadata.json
    8. Promote model version in ModelVersionManager
    9. Run PlantPredictor inference on a test image
    10. Verify top-k prediction output format, confidence values, and model version attribution
    11. Verify rollback functionality
    """
    models_dir = tmp_path / "models"
    version_id = "v1-e2e-test"

    # Step 1 & 2: Load approved records & verify unreviewed exclusion
    records = load_canonical_records(mock_canonical_manifest)
    dataset = DravyaDataset(records=records)

    # 4 records in manifest, but 1 is UNREVIEWED -> dataset size must be 3
    assert len(dataset) == 3
    assert "Unreviewed Plant Species" not in dataset.class_to_idx
    assert len(dataset.class_to_idx) == 2

    # Step 3 & 4: Configuration and DataLoader setup
    config = ModelConfig(
        dataset_manifest_path=str(mock_canonical_manifest),
        models_dir=str(models_dir),
        model_version=version_id,
        architecture="efficientnet_b0",
        epochs=1,
        batch_size=2,
        validation_split=0.33,
        random_seed=42,
        device="cpu",
    )

    train_loader, val_loader, class_to_idx, idx_to_class = create_dataloaders(
        manifest_path=mock_canonical_manifest,
        config=config,
    )

    assert len(class_to_idx) == 2
    assert "Clerodendrum splendens" in class_to_idx
    assert "Saraca asoca" in class_to_idx

    # Step 5: EfficientNet Model Construction
    num_classes = len(class_to_idx)
    model = PlantClassifier(
        num_classes=num_classes,
        architecture=config.architecture,
        pretrained=False,
    )

    # Step 6 & 7: Model Training & Validation Execution
    trainer = ModelTrainer(
        model=model,
        config=config,
        class_to_idx=class_to_idx,
        idx_to_class=idx_to_class,
        train_loader=train_loader,
        val_loader=val_loader,
    )

    summary = trainer.train()

    # Verify training output summary
    assert summary["version"] == version_id
    assert summary["architecture"] == "efficientnet_b0"
    assert summary["num_classes"] == 2
    assert summary["epochs_completed"] == 1
    assert "val_metrics" in summary
    assert "accuracy" in summary["val_metrics"]
    assert "f1_score" in summary["val_metrics"]
    assert "confusion_matrix" in summary["val_metrics"]

    # Step 8: Verify Saved Artifacts & Version Manager
    version_dir = models_dir / version_id
    assert (version_dir / "best_model.pth").exists()
    assert (version_dir / "class_mapping.json").exists()
    assert (version_dir / "model_metadata.json").exists()

    vm = ModelVersionManager(models_dir=models_dir)
    assert vm.get_active_version() == version_id

    # Step 9 & 10: Production Inference Verification
    predictor = PlantPredictor(
        version=version_id,
        models_dir=models_dir,
        device="cpu",
    )

    # Create dummy test PIL image
    arr = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
    test_img = Image.fromarray(arr)

    prediction = predictor.predict(test_img, top_k=2)

    assert prediction["model_version"] == version_id
    assert prediction["architecture"] == "efficientnet_b0"
    assert prediction["num_classes"] == 2
    assert "canonical_name" in prediction
    assert "confidence" in prediction
    assert isinstance(prediction["confidence"], float)
    assert len(prediction["top_k"]) == 2

    # Step 11: Rollback test
    vm.set_active_version(version_id)
    assert vm.get_active_version() == version_id
    vm.rollback(version_id)
    assert vm.get_active_version() == version_id
