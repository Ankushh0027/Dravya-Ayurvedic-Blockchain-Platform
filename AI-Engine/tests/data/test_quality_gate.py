import os
import json
import pytest
from pathlib import Path
from PIL import Image

from src.data.taxonomy import (
    CanonicalPlant,
    TaxonomyMapping,
    MappingStatus,
    generate_canonical_plant_id
)
from src.data.dataset_builder import (
    CanonicalDatasetRecord,
    SourceReference
)
from src.data.quality_gate import (
    DatasetQualityGate,
    QualityGateStatus,
    CheckStatus
)
from src.data.deduplication import compute_file_sha256

def create_mock_quality_gate_env(tmp_path, num_images=10, create_unapproved=False, corrupt_img=False, sha_mismatch=False, missing_file=False):
    plant_id = generate_canonical_plant_id("Saraca asoca")
    plant = CanonicalPlant(
        canonical_plant_id=plant_id,
        canonical_name="Ashoka",
        scientific_name="Saraca asoca"
    )

    ds_dir = tmp_path / "datasets" / "CIMPd" / "Ashok.H"
    ds_dir.mkdir(parents=True, exist_ok=True)

    records = []
    sha_map = {}

    for i in range(1, num_images + 1):
        fname = f"leaf_{i:03d}.jpg"
        fpath = ds_dir / fname

        if corrupt_img and i == 1:
            fpath.write_bytes(b"NOT_A_REAL_IMAGE_DATA")
        else:
            # Create a real 10x10 RGB image with PIL
            img = Image.new("RGB", (100, 100), color=(0, 255, 0))
            img.save(fpath)

        sha = compute_file_sha256(fpath)
        if sha_mismatch and i == 1:
            sha = "0000000000000000000000000000000000000000000000000000000000000000"

        src_ref = SourceReference(
            dataset_id="CIMPd",
            original_class_name="Ashok.H",
            source_file_path=str(fpath if not (missing_file and i == 1) else tmp_path / "missing.jpg"),
            source_file_name=fname
        )

        rec = CanonicalDatasetRecord(
            record_id=f"rec_v1_{i:05d}",
            taxonomy_version="v1",
            canonical_plant_id=plant_id,
            canonical_name="Ashoka",
            scientific_name="Saraca asoca",
            health_condition="Healthy",
            sha256=sha,
            file_extension=".jpg",
            source_references=[src_ref]
        )
        records.append(rec)

    reports_dir = tmp_path / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = reports_dir / "canonical_dataset_manifest_v1.json"
    taxonomy_path = reports_dir / "canonical_taxonomy_v1.json"
    mapping_path = reports_dir / "taxonomy_review_v1.json"

    with open(taxonomy_path, "w", encoding="utf-8") as f:
        json.dump({"taxonomy_version": "v1", "plants": [plant.to_dict()]}, f)

    m_status = MappingStatus.UNREVIEWED if create_unapproved else MappingStatus.APPROVED
    app_pid = plant_id if m_status == MappingStatus.APPROVED else None

    mapping = TaxonomyMapping(
        mapping_id="map_001",
        source_dataset="CIMPd",
        original_class_name="Ashok.H",
        normalized_name="ashok",
        candidate_canonical_plant_id=plant_id,
        approved_canonical_plant_id=app_pid,
        health_condition="Healthy",
        mapping_status=m_status
    )

    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump({"mapping_version": "v1", "mappings": [mapping.to_dict()]}, f)

    manifest_content = {
        "taxonomy_version": "v1",
        "exported_at": "2026-08-02T12:00:00Z",
        "status": "SUCCESS",
        "reason": "APPROVED_MAPPINGS_PROCESSED",
        "total_records": len(records),
        "records": [r.to_dict() for r in records]
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_content, f)

    return reports_dir, manifest_path, taxonomy_path, mapping_path

def test_missing_manifest_handling(tmp_path):
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    gate = DatasetQualityGate(version="v1", reports_dir=str(reports_dir))
    res = gate.evaluate_quality_gate(str(reports_dir / "nonexistent_manifest.json"))
    
    assert res.status == QualityGateStatus.BLOCKED
    assert res.reason == "MANIFEST_FILE_NOT_FOUND"

def test_zero_approved_mappings_manifest_blocked(tmp_path):
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = reports_dir / "canonical_dataset_manifest_v1.json"

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump({
            "taxonomy_version": "v1",
            "status": "BLOCKED",
            "reason": "NO_APPROVED_MAPPINGS",
            "total_records": 0,
            "records": []
        }, f)

    gate = DatasetQualityGate(version="v1", reports_dir=str(reports_dir))
    res = gate.evaluate_quality_gate(str(manifest_path))

    assert res.status == QualityGateStatus.BLOCKED
    assert res.reason == "NO_APPROVED_MAPPINGS"

def test_valid_approved_dataset_passes(tmp_path):
    reports_dir, manifest_path, taxonomy_path, mapping_path = create_mock_quality_gate_env(tmp_path, num_images=10)
    gate = DatasetQualityGate(version="v1", reports_dir=str(reports_dir), min_samples_per_class=5)
    res = gate.evaluate_quality_gate(str(manifest_path), str(taxonomy_path), str(mapping_path))

    assert res.status == QualityGateStatus.PASS
    assert res.reason == "ALL_QUALITY_CHECKS_PASSED"

def test_unapproved_mapping_rejection(tmp_path):
    reports_dir, manifest_path, taxonomy_path, mapping_path = create_mock_quality_gate_env(tmp_path, create_unapproved=True)
    gate = DatasetQualityGate(version="v1", reports_dir=str(reports_dir))
    res = gate.evaluate_quality_gate(str(manifest_path), str(taxonomy_path), str(mapping_path))

    assert res.status == QualityGateStatus.FAIL
    assert any("NOT an APPROVED mapping" in err for err in res.errors)

def test_missing_source_file(tmp_path):
    reports_dir, manifest_path, taxonomy_path, mapping_path = create_mock_quality_gate_env(tmp_path, missing_file=True)
    gate = DatasetQualityGate(version="v1", reports_dir=str(reports_dir))
    res = gate.evaluate_quality_gate(str(manifest_path), str(taxonomy_path), str(mapping_path))

    assert res.status == QualityGateStatus.FAIL
    assert any("Missing source file" in err for err in res.errors)

def test_sha256_mismatch(tmp_path):
    reports_dir, manifest_path, taxonomy_path, mapping_path = create_mock_quality_gate_env(tmp_path, sha_mismatch=True)
    gate = DatasetQualityGate(version="v1", reports_dir=str(reports_dir))
    res = gate.evaluate_quality_gate(str(manifest_path), str(taxonomy_path), str(mapping_path))

    assert res.status == QualityGateStatus.FAIL
    assert any("SHA mismatch" in err for err in res.errors)

def test_corrupt_image(tmp_path):
    reports_dir, manifest_path, taxonomy_path, mapping_path = create_mock_quality_gate_env(tmp_path, corrupt_img=True)
    gate = DatasetQualityGate(version="v1", reports_dir=str(reports_dir))
    res = gate.evaluate_quality_gate(str(manifest_path), str(taxonomy_path), str(mapping_path))

    assert res.status == QualityGateStatus.FAIL
    assert any("Corrupt or unreadable image" in err for err in res.errors)

def test_minimum_sample_warning_and_fail_on_warning(tmp_path):
    reports_dir, manifest_path, taxonomy_path, mapping_path = create_mock_quality_gate_env(tmp_path, num_images=2)
    
    # 1. With min_samples_per_class=5 and fail_on_warning=False -> WARNING
    gate1 = DatasetQualityGate(version="v1", reports_dir=str(reports_dir), min_samples_per_class=5, fail_on_warning=False)
    res1 = gate1.evaluate_quality_gate(str(manifest_path), str(taxonomy_path), str(mapping_path))
    assert res1.status == QualityGateStatus.WARNING
    assert any("below threshold" in warn for warn in res1.warnings)

    # 2. With fail_on_warning=True -> FAIL
    gate2 = DatasetQualityGate(version="v1", reports_dir=str(reports_dir), min_samples_per_class=5, fail_on_warning=True)
    res2 = gate2.evaluate_quality_gate(str(manifest_path), str(taxonomy_path), str(mapping_path))
    assert res2.status == QualityGateStatus.FAIL

def test_raw_dataset_path_safety():
    external_roots = [r"C:\Datasets\CIMPd", r"C:\Datasets\Hugging_Face", r"C:\Datasets\Kaggle"]
    for path in external_roots:
        if os.path.exists(path):
            assert os.path.isdir(path)
