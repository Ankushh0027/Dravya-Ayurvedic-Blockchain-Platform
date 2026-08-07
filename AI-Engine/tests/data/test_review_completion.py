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
from src.data.taxonomy_review import (
    TaxonomyReviewEngine,
    ReviewDecision,
    ReviewDecisionAction,
    atomic_json_write
)
from src.data.review_completion import HumanReviewCompletionAnalyzer

def create_completion_test_env(tmp_path):
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    p1_id = generate_canonical_plant_id("Saraca asoca")
    p1 = CanonicalPlant(canonical_plant_id=p1_id, canonical_name="Ashoka", scientific_name="Saraca asoca")

    p2_id = generate_canonical_plant_id("Azadirachta indica")
    p2 = CanonicalPlant(canonical_plant_id=p2_id, canonical_name="Neem", scientific_name="Azadirachta indica")

    tax_path = reports_dir / "canonical_taxonomy_v1.json"
    atomic_json_write(tax_path, {"taxonomy_version": "v1", "plants": [p1.to_dict(), p2.to_dict()]})

    # Group 1: Saraca asoca (2 mappings, 1 approved, 1 unreviewed -> Pending Group)
    m1 = TaxonomyMapping(
        mapping_id="map_v1_00001",
        source_dataset="CIMPd",
        original_class_name="Ashok.H",
        normalized_name="ashok",
        health_condition="Healthy",
        candidate_canonical_plant_id=p1_id,
        approved_canonical_plant_id=p1_id,
        confidence="HIGH",
        match_reason="Exact match",
        mapping_status=MappingStatus.APPROVED,
        reviewer="botanist_01",
        evidence="Flora monograph verification"
    )

    m2 = TaxonomyMapping(
        mapping_id="map_v1_00002",
        source_dataset="Kaggle",
        original_class_name="Ashok.U",
        normalized_name="ashok",
        health_condition="Unhealthy",
        candidate_canonical_plant_id=p1_id,
        confidence="HIGH",
        match_reason="Exact match",
        mapping_status=MappingStatus.UNREVIEWED
    )

    # Group 2: Azadirachta indica (1 mapping, rejected -> Fully Reviewed Group)
    m3 = TaxonomyMapping(
        mapping_id="map_v1_00003",
        source_dataset="Hugging_Face",
        original_class_name="neem_leaf",
        normalized_name="neem leaf",
        health_condition="Unknown",
        candidate_canonical_plant_id=p2_id,
        confidence="HIGH",
        match_reason="Exact match",
        mapping_status=MappingStatus.REJECTED,
        reviewer="botanist_01",
        evidence="Non-botanical artifacts in folder"
    )

    map_path = reports_dir / "taxonomy_mapping_review_v1.json"
    atomic_json_write(map_path, {"taxonomy_version": "v1", "mappings": [m1.to_dict(), m2.to_dict(), m3.to_dict()]})

    # Create dummy dataset directory for Ashok.H
    cimpd_root = tmp_path / "CIMPd"
    ashok_dir = cimpd_root / "Ashok.H"
    ashok_dir.mkdir(parents=True, exist_ok=True)
    (ashok_dir / "img1.jpg").write_bytes(b"dummy image content 123")

    roots = {"CIMPd": cimpd_root}

    return reports_dir, p1_id, p2_id, roots

def test_analyze_completion_readiness_metrics(tmp_path):
    reports_dir, p1_id, p2_id, roots = create_completion_test_env(tmp_path)
    analyzer = HumanReviewCompletionAnalyzer(version="v1", reports_dir=str(reports_dir), dataset_roots=roots)
    report = analyzer.analyze_completion_readiness()

    assert report["taxonomy_version"] == "v1"
    assert report["total_mappings"] == 3
    assert report["approved_count"] == 1
    assert report["rejected_count"] == 1
    assert report["unreviewed_count"] == 1
    assert report["pending_count"] == 1
    assert report["reviewed_count"] == 2
    assert report["completion_readiness_status"] == "READY_FOR_PARTIAL_DATASET"
    assert report["fully_reviewed_groups_count"] == 1
    assert report["pending_groups_count"] == 1

def test_fully_reviewed_vs_pending_group_classification(tmp_path):
    reports_dir, p1_id, p2_id, roots = create_completion_test_env(tmp_path)
    analyzer = HumanReviewCompletionAnalyzer(version="v1", reports_dir=str(reports_dir), dataset_roots=roots)
    report = analyzer.analyze_completion_readiness()

    statuses = {g["canonical_plant_id"]: g for g in report["group_statuses"]}
    assert statuses[p1_id]["is_fully_reviewed"] is False
    assert statuses[p1_id]["pending_count"] == 1

    assert statuses[p2_id]["is_fully_reviewed"] is True
    assert statuses[p2_id]["pending_count"] == 0

def test_deterministic_next_recommendations_ordering(tmp_path):
    reports_dir, p1_id, p2_id, roots = create_completion_test_env(tmp_path)
    analyzer = HumanReviewCompletionAnalyzer(version="v1", reports_dir=str(reports_dir), dataset_roots=roots)
    report = analyzer.analyze_completion_readiness()

    next_recs = report["next_recommended_review_groups"]
    assert len(next_recs) == 1
    assert next_recs[0]["canonical_plant_id"] == p1_id

def test_read_only_sha256_audit_verification(tmp_path):
    reports_dir, p1_id, p2_id, roots = create_completion_test_env(tmp_path)
    analyzer = HumanReviewCompletionAnalyzer(version="v1", reports_dir=str(reports_dir), dataset_roots=roots)
    report = analyzer.analyze_completion_readiness()

    assert report["approved_source_files_scanned"] == 1
    assert report["approved_unique_images_sha256_count"] == 1
    audit_entry = report["approved_mappings_audit"][0]
    assert audit_entry["mapping_id"] == "map_v1_00001"
    assert audit_entry["class_directory_exists"] is True

def test_health_condition_separation_assertion(tmp_path):
    reports_dir, p1_id, p2_id, roots = create_completion_test_env(tmp_path)
    analyzer = HumanReviewCompletionAnalyzer(version="v1", reports_dir=str(reports_dir), dataset_roots=roots)
    report = analyzer.analyze_completion_readiness()

    m1_audit = report["approved_mappings_audit"][0]
    assert m1_audit["health_condition"] == "Healthy"
    assert m1_audit["approved_canonical_plant_id"] == p1_id
    assert "Healthy" not in p1_id

def test_raw_datasets_immutability_verification(tmp_path):
    reports_dir, p1_id, p2_id, roots = create_completion_test_env(tmp_path)
    analyzer = HumanReviewCompletionAnalyzer(version="v1", reports_dir=str(reports_dir), dataset_roots=roots)
    report = analyzer.analyze_completion_readiness()

    assert report["raw_datasets_immutability_verified"] is True

def test_no_auto_approval_assertion(tmp_path):
    reports_dir, p1_id, p2_id, roots = create_completion_test_env(tmp_path)
    analyzer = HumanReviewCompletionAnalyzer(version="v1", reports_dir=str(reports_dir), dataset_roots=roots)
    report = analyzer.analyze_completion_readiness()

    # Unreviewed mapping remains unreviewed
    unrev = analyzer.engine.mappings["map_v1_00002"]
    assert unrev.mapping_status == MappingStatus.UNREVIEWED
    assert unrev.approved_canonical_plant_id is None

def test_atomic_readiness_artifact_export(tmp_path):
    reports_dir, p1_id, p2_id, roots = create_completion_test_env(tmp_path)
    analyzer = HumanReviewCompletionAnalyzer(version="v1", reports_dir=str(reports_dir), dataset_roots=roots)
    analyzer.analyze_completion_readiness()

    artifact_p = reports_dir / "human_review_completion_readiness_v1.json"
    assert artifact_p.exists()
    assert not (reports_dir / "human_review_completion_readiness_v1.json.tmp").exists()

def test_version_isolation_completion_analyzer(tmp_path):
    reports_dir, p1_id, p2_id, roots = create_completion_test_env(tmp_path)
    a1 = HumanReviewCompletionAnalyzer(version="v1", reports_dir=str(reports_dir), dataset_roots=roots)
    a2 = HumanReviewCompletionAnalyzer(version="v2", reports_dir=str(reports_dir), dataset_roots=roots)

    a1.analyze_completion_readiness()
    with pytest.raises(FileNotFoundError):
        a2.analyze_completion_readiness()

def test_export_real_completion_readiness_artifact():
    real_reports_dir = Path(r"C:\Dravya-AI-Engine\reports\dataset_analysis")
    analyzer = HumanReviewCompletionAnalyzer(version="v1", reports_dir=str(real_reports_dir))
    report = analyzer.analyze_completion_readiness()

    artifact_p = real_reports_dir / "human_review_completion_readiness_v1.json"
    assert artifact_p.exists()
    assert report["total_mappings"] == 331
    assert report["approved_count"] == 4
    assert report["pending_count"] == 327
    assert report["completion_readiness_status"] == "READY_FOR_PARTIAL_DATASET"
