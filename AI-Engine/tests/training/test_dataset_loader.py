import json
import pytest
from pathlib import Path

import torch
from src.training.dataset import (
    DravyaDataset,
    get_transforms,
    create_dataloaders,
    load_canonical_records,
)
from src.models.config import ModelConfig


@pytest.fixture
def sample_canonical_records():
    return [
        {
            "record_id": "rec_001",
            "taxonomy_version": "v1",
            "canonical_plant_id": "PLANT-CLERODENDRUM-SPLENDENS-0FC371",
            "canonical_name": "Clerodendrum splendens",
            "health_condition": "Healthy",
            "sha256": "sha256_001",
            "file_extension": ".jpg",
            "mapping_status": "APPROVED",
            "source_references": [
                {
                    "dataset_id": "CIMPd",
                    "original_class_name": "Clerodendrum splendens.H",
                    "source_file_path": "C:\\Datasets\\CIMPd\\Clerodendrum splendens.H\\img1.jpg",
                    "source_file_name": "img1.jpg",
                }
            ],
        },
        {
            "record_id": "rec_002",
            "taxonomy_version": "v1",
            "canonical_plant_id": "PLANT-SARACA-ASOCA-4B8F7A",
            "canonical_name": "Saraca asoca",
            "health_condition": "Healthy",
            "sha256": "sha256_002",
            "file_extension": ".jpg",
            "mapping_status": "APPROVED",
            "source_references": [
                {
                    "dataset_id": "CIMPd",
                    "original_class_name": "Saraca asoca.H",
                    "source_file_path": "C:\\Datasets\\CIMPd\\Saraca asoca.H\\img2.jpg",
                    "source_file_name": "img2.jpg",
                }
            ],
        },
    ]


def test_dataset_loader_approved_records_only(sample_canonical_records):
    # Add an unreviewed record
    unreviewed_record = {
        "record_id": "rec_003",
        "canonical_plant_id": "PLANT-UNKNOWN-123456",
        "canonical_name": "Unknown Plant",
        "mapping_status": "UNREVIEWED",
        "source_references": [],
    }
    records = sample_canonical_records + [unreviewed_record]

    dataset = DravyaDataset(records=records, transform=get_transforms(224, is_training=True))
    
    # Verify unreviewed record was excluded automatically
    assert len(dataset) == 2
    assert "Unknown Plant" not in dataset.class_to_idx


def test_dataset_item_shape(sample_canonical_records):
    dataset = DravyaDataset(records=sample_canonical_records, transform=get_transforms(224, is_training=True))
    img_tensor, label = dataset[0]
    
    assert isinstance(img_tensor, torch.Tensor)
    assert img_tensor.shape == (3, 224, 224)
    assert label in [0, 1]


def test_dataloaders_split(tmp_path, sample_canonical_records):
    # Write temporary manifest
    manifest_path = tmp_path / "test_manifest.json"
    manifest_data = {
        "taxonomy_version": "v1",
        "status": "SUCCESS",
        "total_records": len(sample_canonical_records),
        "records": sample_canonical_records,
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f)

    config = ModelConfig(
        dataset_manifest_path=str(manifest_path),
        batch_size=1,
        validation_split=0.5,
        random_seed=42,
    )

    train_loader, val_loader, class_to_idx, idx_to_class = create_dataloaders(
        manifest_path=manifest_path, config=config
    )

    assert len(class_to_idx) == 2
    assert len(train_loader) == 1
    assert len(val_loader) == 1


def test_dataloaders_small_dataset_edge_case(tmp_path, sample_canonical_records):
    # Manifest with 3 records (e.g. total_size=3, validation_split=0.2 -> val_size would be 0 without max(1, ...))
    records = sample_canonical_records + [
        {
            "record_id": "rec_003",
            "taxonomy_version": "v1",
            "canonical_plant_id": "PLANT-SARACA-ASOCA-4B8F7A",
            "canonical_name": "Saraca asoca",
            "health_condition": "Healthy",
            "sha256": "sha256_003",
            "file_extension": ".jpg",
            "mapping_status": "APPROVED",
            "source_references": [],
        }
    ]
    manifest_path = tmp_path / "small_manifest.json"
    manifest_data = {
        "taxonomy_version": "v1",
        "status": "SUCCESS",
        "total_records": len(records),
        "records": records,
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f)

    config = ModelConfig(
        dataset_manifest_path=str(manifest_path),
        batch_size=1,
        validation_split=0.2,  # 3 * 0.2 = 0.6 -> must round up/clamp to 1 so val_loader is non-empty
        random_seed=42,
    )

    train_loader, val_loader, class_to_idx, idx_to_class = create_dataloaders(
        manifest_path=manifest_path, config=config
    )

    assert len(train_loader.dataset) == 2
    assert len(val_loader.dataset) == 1
    assert len(class_to_idx) == 2

