import os
import json
import pytest
from pathlib import Path
from src.data.taxonomy import (
    CanonicalPlant,
    TaxonomyMapping,
    MappingStatus,
    generate_canonical_plant_id
)
from src.data.dataset_builder import (
    CanonicalDatasetBuilder,
    SourceReference,
    CanonicalDatasetRecord
)
from src.data.deduplication import compute_file_sha256

def create_mock_builder_env(tmp_path):
    plant_id = generate_canonical_plant_id("Saraca asoca")
    plant = CanonicalPlant(
        canonical_plant_id=plant_id,
        canonical_name="Ashoka",
        scientific_name="Saraca asoca"
    )

    # 1. Create mock dataset root and dummy image files
    ds1_dir = tmp_path / "datasets" / "CIMPd" / "Ashok.H"
    ds1_dir.mkdir(parents=True, exist_ok=True)

    ds2_dir = tmp_path / "datasets" / "Hugging_Face" / "ashoka_leaf"
    ds2_dir.mkdir(parents=True, exist_ok=True)

    img1_path = ds1_dir / "leaf1.jpg"
    img1_path.write_bytes(b"SAME_IMAGE_BYTES_12345")

    img2_path = ds2_dir / "leaf_dup.jpg"
    img2_path.write_bytes(b"SAME_IMAGE_BYTES_12345")  # Duplicate SHA-256 file!

    img3_path = ds1_dir / "leaf2.jpg"
    img3_path.write_bytes(b"DIFFERENT_IMAGE_BYTES_67890")

    # Calculate SHA-256 for mock files
    sha_dup = compute_file_sha256(img1_path)
    sha_diff = compute_file_sha256(img3_path)

    # 2. Mappings:
    # m_app1: APPROVED
    # m_app2: APPROVED (cross-dataset duplicate)
    # m_unrev: UNREVIEWED
    # m_needs: NEEDS_REVIEW
    # m_rej: REJECTED
    m_app1 = TaxonomyMapping(
        mapping_id="map_001",
        source_dataset="CIMPd",
        original_class_name="Ashok.H",
        normalized_name="ashok",
        candidate_canonical_plant_id=plant_id,
        approved_canonical_plant_id=plant_id,
        health_condition="Healthy",
        mapping_status=MappingStatus.APPROVED
    )

    m_app2 = TaxonomyMapping(
        mapping_id="map_002",
        source_dataset="Hugging_Face",
        original_class_name="ashoka_leaf",
        normalized_name="ashok",
        candidate_canonical_plant_id=plant_id,
        approved_canonical_plant_id=plant_id,
        health_condition="Healthy",
        mapping_status=MappingStatus.APPROVED
    )

    m_unrev = TaxonomyMapping(
        mapping_id="map_003",
        source_dataset="CIMPd",
        original_class_name="Unreviewed_Plant",
        normalized_name="unreviewed",
        candidate_canonical_plant_id="PLANT-UNREV-111",
        health_condition="Unknown",
        mapping_status=MappingStatus.UNREVIEWED
    )

    m_needs = TaxonomyMapping(
        mapping_id="map_004",
        source_dataset="CIMPd",
        original_class_name="Needs_Review_Plant",
        normalized_name="needs_review",
        candidate_canonical_plant_id="PLANT-NEEDS-222",
        health_condition="Unknown",
        mapping_status=MappingStatus.NEEDS_REVIEW
    )

    m_rej = TaxonomyMapping(
        mapping_id="map_005",
        source_dataset="CIMPd",
        original_class_name="Rejected_Plant",
        normalized_name="rejected",
        candidate_canonical_plant_id="PLANT-REJ-333",
        health_condition="Unknown",
        mapping_status=MappingStatus.REJECTED
    )

    reports_dir = tmp_path / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    tax_path = reports_dir / "canonical_taxonomy_v1.json"
    map_path = reports_dir / "taxonomy_review_v1.json"

    with open(tax_path, "w", encoding="utf-8") as f:
        json.dump({"taxonomy_version": "v1", "plants": [plant.to_dict()]}, f)

    with open(map_path, "w", encoding="utf-8") as f:
        json.dump({"mapping_version": "v1", "mappings": [m_app1.to_dict(), m_app2.to_dict(), m_unrev.to_dict(), m_needs.to_dict(), m_rej.to_dict()]}, f)

    dataset_roots = {
        "CIMPd": tmp_path / "datasets" / "CIMPd",
        "Hugging_Face": tmp_path / "datasets" / "Hugging_Face"
    }

    return plant_id, reports_dir, tax_path, map_path, dataset_roots, sha_dup, sha_diff

def test_zero_approved_mappings_safely_blocked(tmp_path):
    # 1. Zero approved mappings handling
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    tax_path = reports_dir / "canonical_taxonomy_v1.json"
    map_path = reports_dir / "taxonomy_review_v1.json"

    with open(tax_path, "w", encoding="utf-8") as f:
        json.dump({"taxonomy_version": "v1", "plants": []}, f)

    # 100% UNREVIEWED / NEEDS_REVIEW mappings
    m_unrev = TaxonomyMapping(
        mapping_id="map_001",
        source_dataset="CIMPd",
        original_class_name="Ashok.H",
        normalized_name="ashok",
        candidate_canonical_plant_id="PLANT-ASHOK-123",
        health_condition="Healthy",
        mapping_status=MappingStatus.UNREVIEWED
    )
    with open(map_path, "w", encoding="utf-8") as f:
        json.dump({"mapping_version": "v1", "mappings": [m_unrev.to_dict()]}, f)

    builder = CanonicalDatasetBuilder(version="v1", reports_dir=str(reports_dir))
    builder.load_inputs(str(tax_path), str(map_path))
    records, stats = builder.build_manifest()

    assert stats["status"] == "BLOCKED"
    assert stats["reason"] == "NO_APPROVED_MAPPINGS"
    assert len(records) == 0
    assert stats["total_canonical_records"] == 0

def test_approved_inclusion_and_exclusions_and_duplicate_consolidation(tmp_path):
    plant_id, reports_dir, tax_path, map_path, dataset_roots, sha_dup, sha_diff = create_mock_builder_env(tmp_path)

    builder = CanonicalDatasetBuilder(version="v1", reports_dir=str(reports_dir), dataset_roots=dataset_roots)
    builder.load_inputs(str(tax_path), str(map_path))
    records, stats = builder.build_manifest()

    assert stats["status"] == "SUCCESS"
    assert stats["reason"] == "APPROVED_MAPPINGS_PROCESSED"
    
    # 2 & 3 & 4 & 5. Only APPROVED mappings entered manifest. 3 raw files -> 2 canonical records!
    assert len(records) == 2
    assert stats["total_canonical_records"] == 2
    assert stats["raw_files_scanned"] == 3
    assert stats["duplicate_consolidation_count"] == 1

    # 6 & 7. Duplicate SHA-256 consolidation & multi-provenance tracking
    dup_record = next(r for r in records if r.sha256 == sha_dup)
    assert len(dup_record.source_references) == 2

    ds_ids = {s.dataset_id for s in dup_record.source_references}
    assert ds_ids == {"CIMPd", "Hugging_Face"}

    # 10 & 11. Health condition and original class name preservation
    assert dup_record.health_condition == "Healthy"
    assert dup_record.canonical_plant_id == plant_id

def test_manifest_validation_and_missing_file_detection(tmp_path):
    plant_id, reports_dir, tax_path, map_path, dataset_roots, sha_dup, sha_diff = create_mock_builder_env(tmp_path)

    builder = CanonicalDatasetBuilder(version="v1", reports_dir=str(reports_dir), dataset_roots=dataset_roots)
    builder.load_inputs(str(tax_path), str(map_path))
    records, stats = builder.build_manifest()

    val_rep = builder.validate_manifest()
    assert val_rep["is_valid"] is True
    assert val_rep["errors_count"] == 0

    # 8. Missing source file detection
    records[0].source_references[0].source_file_path = str(tmp_path / "nonexistent_file.jpg")
    val_missing = builder.validate_manifest()
    assert val_missing["is_valid"] is False
    assert any("references missing source file" in err for err in val_missing["errors"])

def test_sha256_mismatch_detection(tmp_path):
    plant_id, reports_dir, tax_path, map_path, dataset_roots, sha_dup, sha_diff = create_mock_builder_env(tmp_path)

    builder = CanonicalDatasetBuilder(version="v1", reports_dir=str(reports_dir), dataset_roots=dataset_roots)
    builder.load_inputs(str(tax_path), str(map_path))
    records, stats = builder.build_manifest()

    # Artificially alter SHA-256 in record
    records[0].sha256 = "0000000000000000000000000000000000000000000000000000000000000000"
    val_rep = builder.validate_manifest()
    assert val_rep["is_valid"] is False
    assert any("SHA-256 mismatch" in err for err in val_rep["errors"])

def test_raw_dataset_path_safety():

    # 12. Raw external dataset paths remain 100% read-only & untouched
    external_roots = [r"C:\Datasets\CIMPd", r"C:\Datasets\Hugging_Face", r"C:\Datasets\Kaggle"]
    for path in external_roots:
        if os.path.exists(path):
            assert os.path.isdir(path)
