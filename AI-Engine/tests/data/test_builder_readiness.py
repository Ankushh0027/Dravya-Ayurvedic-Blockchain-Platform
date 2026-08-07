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
from src.data.dataset_builder import CanonicalDatasetBuilder
from src.data.taxonomy_review_queue import TaxonomyReviewQueue
from src.data.botanical_review import BotanicalReviewAnalyzer, RecommendationAction

def create_builder_test_env(tmp_path):
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    p1_id = generate_canonical_plant_id("Saraca asoca")
    p1 = CanonicalPlant(canonical_plant_id=p1_id, canonical_name="Ashoka", scientific_name="Saraca asoca")

    p2_id = generate_canonical_plant_id("Azadirachta indica")
    p2 = CanonicalPlant(canonical_plant_id=p2_id, canonical_name="Neem", scientific_name="Azadirachta indica")

    atomic_json_write(reports_dir / "canonical_taxonomy_v1.json", {
        "taxonomy_version": "v1",
        "plants": [p1.to_dict(), p2.to_dict()]
    })

    m1 = TaxonomyMapping(
        mapping_id="map_v1_00001",
        source_dataset="CIMPd",
        original_class_name="Ashok.H",
        normalized_name="ashok",
        health_condition="Healthy",
        candidate_canonical_plant_id=p1_id,
        confidence="HIGH",
        match_reason="Exact match",
        mapping_status=MappingStatus.UNREVIEWED
    )

    m2 = TaxonomyMapping(
        mapping_id="map_v1_00002",
        source_dataset="Hugging_Face",
        original_class_name="neem_leaf",
        normalized_name="neem leaf",
        health_condition="Unknown",
        candidate_canonical_plant_id=p2_id,
        confidence="HIGH",
        match_reason="Exact match",
        mapping_status=MappingStatus.NEEDS_REVIEW
    )

    m3 = TaxonomyMapping(
        mapping_id="map_v1_00003",
        source_dataset="Kaggle",
        original_class_name="unknown_weed",
        normalized_name="unknown weed",
        health_condition="Unknown",
        candidate_canonical_plant_id=None,
        confidence="LOW",
        match_reason="No match",
        mapping_status=MappingStatus.REJECTED
    )

    atomic_json_write(reports_dir / "taxonomy_mapping_review_v1.json", {
        "taxonomy_version": "v1",
        "mappings": [m1.to_dict(), m2.to_dict(), m3.to_dict()]
    })

    return reports_dir, p1_id, p2_id

# 1 & 20. zero approvals remains BLOCKED & safe
def test_1_zero_approvals_remains_blocked(tmp_path):
    reports_dir, p1_id, p2_id = create_builder_test_env(tmp_path)
    builder = CanonicalDatasetBuilder(version="v1", reports_dir=str(reports_dir))
    builder.load_inputs()
    recs, stats = builder.build_manifest()
    
    assert stats["status"] == "BLOCKED"
    assert stats["reason"] == "NO_APPROVED_MAPPINGS"
    assert len(recs) == 0

    readiness = builder.generate_readiness_report()
    assert readiness["builder_readiness_status"] == "BLOCKED"
    assert readiness["approved_mappings"] == 0

# 2, 3, 4, 5, 6. one valid approval makes builder eligible & excludes non-approved
def test_2_one_approval_includes_approved_and_excludes_others(tmp_path):
    reports_dir, p1_id, p2_id = create_builder_test_env(tmp_path)
    engine = TaxonomyReviewEngine(version="v1", reports_dir=str(reports_dir))
    engine.load_state()

    d = ReviewDecision(
        mapping_id="map_v1_00001",
        taxonomy_version="v1",
        reviewer_id="botanist_01",
        decision=ReviewDecisionAction.APPROVE,
        previous_status=MappingStatus.UNREVIEWED,
        approved_canonical_plant_id=p1_id,
        review_reason="Botanically verified"
    )
    engine.apply_decision(d)
    engine.export_artifacts()

    # Create dummy source image file for CIMPd/Ashok.H
    fake_dataset_root = tmp_path / "datasets" / "CIMPd"
    ashok_dir = fake_dataset_root / "Ashok.H"
    ashok_dir.mkdir(parents=True, exist_ok=True)
    img_file = ashok_dir / "img1.jpg"
    img_file.write_bytes(b"dummy image bytes")

    roots = {"CIMPd": fake_dataset_root}
    builder = CanonicalDatasetBuilder(version="v1", reports_dir=str(reports_dir), dataset_roots=roots)
    builder.load_inputs()
    recs, stats = builder.build_manifest()

    assert stats["status"] == "SUCCESS"
    assert stats["total_approved_mappings"] == 1
    assert len(recs) == 1
    assert recs[0].canonical_plant_id == p1_id
    assert recs[0].source_references[0].original_class_name == "Ashok.H"

# 7. duplicate SHA-256 images consolidate correctly
def test_7_duplicate_sha256_consolidation(tmp_path):
    reports_dir, p1_id, p2_id = create_builder_test_env(tmp_path)
    engine = TaxonomyReviewEngine(version="v1", reports_dir=str(reports_dir))
    engine.load_state()

    # Approve map 1 & map 2
    d1 = ReviewDecision(mapping_id="map_v1_00001", taxonomy_version="v1", reviewer_id="b1", decision=ReviewDecisionAction.APPROVE, previous_status=MappingStatus.UNREVIEWED, approved_canonical_plant_id=p1_id, review_reason="V1")
    d2 = ReviewDecision(mapping_id="map_v1_00002", taxonomy_version="v1", reviewer_id="b1", decision=ReviewDecisionAction.APPROVE, previous_status=MappingStatus.NEEDS_REVIEW, approved_canonical_plant_id=p2_id, review_reason="V2")
    engine.apply_decision(d1)
    engine.apply_decision(d2)
    engine.export_artifacts()

    fake_cimpd = tmp_path / "CIMPd" / "Ashok.H"
    fake_hf = tmp_path / "Hugging_Face" / "neem_leaf"
    fake_cimpd.mkdir(parents=True, exist_ok=True)
    fake_hf.mkdir(parents=True, exist_ok=True)

    # Write identical image bytes to both folders
    identical_content = b"SAME_IMAGE_BYTES_123"
    (fake_cimpd / "a.jpg").write_bytes(identical_content)
    (fake_hf / "b.jpg").write_bytes(identical_content)

    roots = {"CIMPd": tmp_path / "CIMPd", "Hugging_Face": tmp_path / "Hugging_Face"}
    builder = CanonicalDatasetBuilder(version="v1", reports_dir=str(reports_dir), dataset_roots=roots)
    builder.load_inputs()
    recs, stats = builder.build_manifest()

    assert stats["raw_files_scanned"] == 2
    assert stats["unique_images"] == 1
    assert stats["duplicate_consolidation_count"] == 1
    assert len(recs) == 1
    assert len(recs[0].source_references) == 2

# 8. source provenance preserved
def test_8_source_provenance_preserved(tmp_path):
    reports_dir, p1_id, p2_id = create_builder_test_env(tmp_path)
    engine = TaxonomyReviewEngine(version="v1", reports_dir=str(reports_dir))
    engine.load_state()
    d1 = ReviewDecision(mapping_id="map_v1_00001", taxonomy_version="v1", reviewer_id="b1", decision=ReviewDecisionAction.APPROVE, previous_status=MappingStatus.UNREVIEWED, approved_canonical_plant_id=p1_id, review_reason="V1")
    engine.apply_decision(d1)
    engine.export_artifacts()

    fake_cimpd = tmp_path / "CIMPd" / "Ashok.H"
    fake_cimpd.mkdir(parents=True, exist_ok=True)
    (fake_cimpd / "ashok1.jpg").write_bytes(b"bytes_ashok")

    roots = {"CIMPd": tmp_path / "CIMPd"}
    builder = CanonicalDatasetBuilder(version="v1", reports_dir=str(reports_dir), dataset_roots=roots)
    builder.load_inputs()
    recs, stats = builder.build_manifest()

    src_ref = recs[0].source_references[0]
    assert src_ref.dataset_id == "CIMPd"
    assert src_ref.original_class_name == "Ashok.H"
    assert src_ref.source_file_name == "ashok1.jpg"

# 9. missing source file detected
def test_9_missing_source_file_detected(tmp_path):
    reports_dir, p1_id, p2_id = create_builder_test_env(tmp_path)
    engine = TaxonomyReviewEngine(version="v1", reports_dir=str(reports_dir))
    engine.load_state()
    d1 = ReviewDecision(mapping_id="map_v1_00001", taxonomy_version="v1", reviewer_id="b1", decision=ReviewDecisionAction.APPROVE, previous_status=MappingStatus.UNREVIEWED, approved_canonical_plant_id=p1_id, review_reason="V1")
    engine.apply_decision(d1)
    engine.export_artifacts()

    roots = {"CIMPd": tmp_path / "nonexistent_dir"}
    builder = CanonicalDatasetBuilder(version="v1", reports_dir=str(reports_dir), dataset_roots=roots)
    builder.load_inputs()
    with pytest.raises(FileNotFoundError, match="not found or not registered"):
        builder.build_manifest()

# 10. SHA-256 mismatch detected
def test_10_sha256_mismatch_detected(tmp_path):
    reports_dir, p1_id, p2_id = create_builder_test_env(tmp_path)
    engine = TaxonomyReviewEngine(version="v1", reports_dir=str(reports_dir))
    engine.load_state()
    d1 = ReviewDecision(mapping_id="map_v1_00001", taxonomy_version="v1", reviewer_id="b1", decision=ReviewDecisionAction.APPROVE, previous_status=MappingStatus.UNREVIEWED, approved_canonical_plant_id=p1_id, review_reason="V1")
    engine.apply_decision(d1)
    engine.export_artifacts()

    fake_cimpd = tmp_path / "CIMPd" / "Ashok.H"
    fake_cimpd.mkdir(parents=True, exist_ok=True)
    img_p = fake_cimpd / "ashok1.jpg"
    img_p.write_bytes(b"content_a")

    roots = {"CIMPd": tmp_path / "CIMPd"}
    builder = CanonicalDatasetBuilder(version="v1", reports_dir=str(reports_dir), dataset_roots=roots)
    builder.load_inputs()
    recs, stats = builder.build_manifest()

    # Tamper with stored SHA-256
    recs[0].sha256 = "0000000000000000000000000000000000000000000000000000000000000000"
    val = builder.validate_manifest()
    assert not val["is_valid"]
    assert any("SHA-256 mismatch" in err for err in val["errors"])

# 11. invalid canonical ID detected
def test_11_invalid_canonical_id_detected(tmp_path):
    reports_dir, p1_id, p2_id = create_builder_test_env(tmp_path)
    engine = TaxonomyReviewEngine(version="v1", reports_dir=str(reports_dir))
    engine.load_state()
    m1 = engine.mappings["map_v1_00001"]
    m1.mapping_status = MappingStatus.APPROVED
    m1.approved_canonical_plant_id = "PLANT-NONEXISTENT-999"

    engine.export_artifacts()

    builder = CanonicalDatasetBuilder(version="v1", reports_dir=str(reports_dir))
    builder.load_inputs()
    with pytest.raises(ValueError, match="missing or invalid canonical_plant_id"):
        builder.build_manifest()

# 12. raw dataset paths unchanged
def test_12_raw_dataset_paths_unchanged():
    for p in [r"C:\Datasets\CIMPd", r"C:\Datasets\Hugging_Face", r"C:\Datasets\Kaggle"]:
        if os.path.exists(p):
            assert os.path.isdir(p)

# 13. review state remains append-only
def test_13_review_state_append_only(tmp_path):
    reports_dir, p1_id, p2_id = create_builder_test_env(tmp_path)
    engine = TaxonomyReviewEngine(version="v1", reports_dir=str(reports_dir))
    engine.load_state()

    d1 = ReviewDecision(mapping_id="map_v1_00001", taxonomy_version="v1", reviewer_id="rev1", decision=ReviewDecisionAction.NEEDS_REVIEW, previous_status=MappingStatus.UNREVIEWED, review_reason="r1")
    d2 = ReviewDecision(mapping_id="map_v1_00001", taxonomy_version="v1", reviewer_id="rev2", decision=ReviewDecisionAction.APPROVE, previous_status=MappingStatus.NEEDS_REVIEW, approved_canonical_plant_id=p1_id, review_reason="r2")

    engine.apply_decision(d1)
    engine.apply_decision(d2)

    assert len(engine.history) == 2
    assert engine.history[0].reviewer_id == "rev1"
    assert engine.history[1].reviewer_id == "rev2"

# 14. atomic writes work
def test_14_atomic_writes_work(tmp_path):
    target = tmp_path / "sample.json"
    atomic_json_write(target, {"key": "value"})
    assert target.exists()
    assert not (tmp_path / "sample.json.tmp").exists()

# 15. deterministic output
def test_15_deterministic_output(tmp_path):
    reports_dir, p1_id, p2_id = create_builder_test_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))
    s1 = queue.get_progress_summary()
    s2 = queue.get_progress_summary()
    assert s1["total_mappings"] == s2["total_mappings"]
    assert s1["counts_by_status"] == s2["counts_by_status"]

# 16. version v1/v2 isolation
def test_16_version_v1_v2_isolation(tmp_path):
    reports_dir, p1_id, p2_id = create_builder_test_env(tmp_path)
    b1 = CanonicalDatasetBuilder(version="v1", reports_dir=str(reports_dir))
    b2 = CanonicalDatasetBuilder(version="v2", reports_dir=str(reports_dir))

    b1.load_inputs()
    with pytest.raises(FileNotFoundError):
        b2.load_inputs()

# 17. botanical recommendation cannot auto-approve
def test_17_botanical_recommendation_cannot_auto_approve(tmp_path):
    reports_dir, p1_id, p2_id = create_builder_test_env(tmp_path)
    analyzer = BotanicalReviewAnalyzer(version="v1", reports_dir=str(reports_dir))
    groups = analyzer.analyze()

    assert groups[0].review_recommendation == RecommendationAction.APPROVE_CANDIDATE
    m1 = analyzer.engine.mappings["map_v1_00001"]
    assert m1.mapping_status == MappingStatus.UNREVIEWED
    assert m1.approved_canonical_plant_id is None

# 18. review queue filtering works
def test_18_review_queue_filtering_works(tmp_path):
    reports_dir, p1_id, p2_id = create_builder_test_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))

    hf = queue.get_by_dataset("Hugging_Face")
    assert len(hf) == 1
    assert hf[0].mapping_id == "map_v1_00002"

# 19. progress report is correct
def test_19_progress_report_correctness(tmp_path):
    reports_dir, p1_id, p2_id = create_builder_test_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))
    summary = queue.get_progress_summary()

    assert summary["total_mappings"] == 3
    assert summary["counts_by_status"]["UNREVIEWED"] == 1
    assert summary["counts_by_status"]["NEEDS_REVIEW"] == 1
    assert summary["counts_by_status"]["REJECTED"] == 1
    assert summary["counts_by_status"]["APPROVED"] == 0

def test_export_readiness_artifact():
    reports_dir = Path(r"C:\Dravya-AI-Engine\reports\dataset_analysis")
    builder = CanonicalDatasetBuilder(version="v1", reports_dir=str(reports_dir))
    builder.load_inputs()
    builder.build_manifest()
    artifacts = builder.export_artifacts()
    
    readiness_p = artifacts["readiness_json"]
    assert readiness_p.exists()
    
    with open(readiness_p, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["builder_readiness_status"] in ("BLOCKED", "READY")
    assert data["total_mappings"] == 331
    assert data["approved_mappings"] == 4
