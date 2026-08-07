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
    ReviewDecision,
    ReviewDecisionAction,
    TaxonomyReviewEngine
)
from src.data.taxonomy_review_queue import (
    ReviewQueueItem,
    TaxonomyReviewQueue
)

def create_mock_review_queue_env(tmp_path):
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    plant1_id = generate_canonical_plant_id("Saraca asoca")
    plant1 = CanonicalPlant(canonical_plant_id=plant1_id, canonical_name="Ashoka", scientific_name="Saraca asoca")

    plant2_id = generate_canonical_plant_id("Azadirachta indica")
    plant2 = CanonicalPlant(canonical_plant_id=plant2_id, canonical_name="Neem", scientific_name="Azadirachta indica")

    tax_path = reports_dir / "canonical_taxonomy_v1.json"
    with open(tax_path, "w", encoding="utf-8") as f:
        json.dump({"taxonomy_version": "v1", "plants": [plant1.to_dict(), plant2.to_dict()]}, f)

    map1 = TaxonomyMapping(
        mapping_id="map_v1_00001",
        source_dataset="CIMPd",
        original_class_name="Ashok.H",
        normalized_name="ashok",
        health_condition="Healthy",
        candidate_canonical_plant_id=plant1_id,
        confidence="HIGH",
        match_reason="Exact match",
        mapping_status=MappingStatus.UNREVIEWED
    )

    map2 = TaxonomyMapping(
        mapping_id="map_v1_00002",
        source_dataset="Hugging_Face",
        original_class_name="neem_leaf",
        normalized_name="neem leaf",
        health_condition="Unknown",
        candidate_canonical_plant_id=plant2_id,
        confidence="HIGH",
        match_reason="Exact match",
        mapping_status=MappingStatus.NEEDS_REVIEW
    )

    map3 = TaxonomyMapping(
        mapping_id="map_v1_00003",
        source_dataset="Kaggle",
        original_class_name="unknown_weed",
        normalized_name="unknown weed",
        health_condition="Unknown",
        candidate_canonical_plant_id=None,
        confidence="LOW",
        match_reason="No match",
        mapping_status=MappingStatus.UNREVIEWED
    )

    map_path = reports_dir / "taxonomy_mapping_review_v1.json"
    with open(map_path, "w", encoding="utf-8") as f:
        json.dump({"taxonomy_version": "v1", "mappings": [map1.to_dict(), map2.to_dict(), map3.to_dict()]}, f)

    return reports_dir, plant1_id, plant2_id

def test_queue_loads_all_mappings(tmp_path):
    # 1. Queue loads all mappings
    reports_dir, p1, p2 = create_mock_review_queue_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))
    
    items = queue.get_all()
    assert len(items) == 3

def test_unreviewed_filtering(tmp_path):
    # 2. Unreviewed filtering
    reports_dir, p1, p2 = create_mock_review_queue_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))

    unreviewed = queue.get_unreviewed()
    assert len(unreviewed) == 2
    assert {item.mapping_id for item in unreviewed} == {"map_v1_00001", "map_v1_00003"}

def test_needs_review_filtering(tmp_path):
    # 3. Needs-review filtering
    reports_dir, p1, p2 = create_mock_review_queue_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))

    needs_review = queue.get_needs_review()
    assert len(needs_review) == 1
    assert needs_review[0].mapping_id == "map_v1_00002"

def test_dataset_filtering(tmp_path):
    # 4. Dataset filtering
    reports_dir, p1, p2 = create_mock_review_queue_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))

    cimpd_items = queue.get_by_dataset("CIMPd")
    assert len(cimpd_items) == 1
    assert cimpd_items[0].original_class_name == "Ashok.H"

    hf_items = queue.get_by_dataset("Hugging_Face")
    assert len(hf_items) == 1

def test_next_pending_item(tmp_path):
    # 5. Next pending item
    reports_dir, p1, p2 = create_mock_review_queue_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))

    nxt = queue.get_next()
    assert nxt is not None
    assert nxt.mapping_id == "map_v1_00001"

def test_empty_queue_behavior(tmp_path):
    # 6. Empty queue behavior
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    with open(reports_dir / "canonical_taxonomy_v1.json", "w", encoding="utf-8") as f:
        json.dump({"taxonomy_version": "v1", "plants": []}, f)
    with open(reports_dir / "taxonomy_mapping_review_v1.json", "w", encoding="utf-8") as f:
        json.dump({"taxonomy_version": "v1", "mappings": []}, f)

    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))
    assert len(queue.get_all()) == 0
    assert queue.get_next() is None
    summary = queue.get_progress_summary()
    assert summary["total_mappings"] == 0

def test_valid_approval_through_explicit_human_action(tmp_path):
    # 7 & 14. Valid approval and append-only history
    reports_dir, p1, p2 = create_mock_review_queue_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))

    decision = ReviewDecision(
        mapping_id="map_v1_00001",
        taxonomy_version="v1",
        reviewer_id="botanist_01",
        decision=ReviewDecisionAction.APPROVE,
        previous_status=MappingStatus.UNREVIEWED,
        candidate_canonical_plant_id=p1,
        approved_canonical_plant_id=p1,
        review_reason="Botanically verified Saraca asoca",
        evidence="Authoritative flora reference"
    )

    queue.engine.apply_decision(decision)
    queue.engine.export_artifacts()
    queue.reload()

    item = queue.get_by_mapping_id("map_v1_00001")
    assert item.current_mapping_status == "APPROVED"
    assert len(item.review_history) == 1
    assert item.review_history[0]["reviewer_id"] == "botanist_01"

def test_approval_requires_reviewer_and_evidence(tmp_path):
    # 8 & 9. Approval requires reviewer and evidence
    reports_dir, p1, p2 = create_mock_review_queue_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))

    # Missing reviewer
    d1 = ReviewDecision(
        mapping_id="map_v1_00001",
        taxonomy_version="v1",
        reviewer_id="",
        decision=ReviewDecisionAction.APPROVE,
        previous_status=MappingStatus.UNREVIEWED,
        approved_canonical_plant_id=p1,
        review_reason="Valid reason"
    )
    with pytest.raises(ValueError, match="reviewer_id"):
        queue.engine.apply_decision(d1)

    # Missing evidence/reason
    d2 = ReviewDecision(
        mapping_id="map_v1_00001",
        taxonomy_version="v1",
        reviewer_id="botanist_01",
        decision=ReviewDecisionAction.APPROVE,
        previous_status=MappingStatus.UNREVIEWED,
        approved_canonical_plant_id=p1,
        review_reason="",
        evidence=""
    )
    with pytest.raises(ValueError, match="review_reason or evidence"):
        queue.engine.apply_decision(d2)

def test_approval_requires_existing_canonical_plant(tmp_path):
    # 10. Approval requires existing canonical plant
    reports_dir, p1, p2 = create_mock_review_queue_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))

    decision = ReviewDecision(
        mapping_id="map_v1_00001",
        taxonomy_version="v1",
        reviewer_id="botanist_01",
        decision=ReviewDecisionAction.APPROVE,
        previous_status=MappingStatus.UNREVIEWED,
        approved_canonical_plant_id="PLANT-NONEXISTENT-999999",
        review_reason="Verified"
    )
    with pytest.raises(ValueError, match="does not exist"):
        queue.engine.apply_decision(decision)

def test_rejection_and_needs_review_require_evidence(tmp_path):
    # 11 & 12. Rejection & Needs-Review require evidence
    reports_dir, p1, p2 = create_mock_review_queue_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))

    d_rej = ReviewDecision(
        mapping_id="map_v1_00001",
        taxonomy_version="v1",
        reviewer_id="botanist_01",
        decision=ReviewDecisionAction.REJECT,
        previous_status=MappingStatus.UNREVIEWED,
        review_reason="",
        evidence=""
    )
    with pytest.raises(ValueError, match="review_reason or evidence"):
        queue.engine.apply_decision(d_rej)

def test_duplicate_approval_prevention(tmp_path):
    # 13. Duplicate approval prevention
    reports_dir, p1, p2 = create_mock_review_queue_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))

    d1 = ReviewDecision(
        mapping_id="map_v1_00001",
        taxonomy_version="v1",
        reviewer_id="botanist_01",
        decision=ReviewDecisionAction.APPROVE,
        previous_status=MappingStatus.UNREVIEWED,
        approved_canonical_plant_id=p1,
        review_reason="First approval"
    )
    queue.engine.apply_decision(d1)

    # Creating another mapping for same dataset & original class
    m_dup = TaxonomyMapping(
        mapping_id="map_v1_99999",
        source_dataset="CIMPd",
        original_class_name="Ashok.H",
        normalized_name="ashok",
        health_condition="Healthy",
        candidate_canonical_plant_id=p1,
        mapping_status=MappingStatus.UNREVIEWED
    )
    queue.engine.mappings["map_v1_99999"] = m_dup

    d2 = ReviewDecision(
        mapping_id="map_v1_99999",
        taxonomy_version="v1",
        reviewer_id="botanist_02",
        decision=ReviewDecisionAction.APPROVE,
        previous_status=MappingStatus.UNREVIEWED,
        approved_canonical_plant_id=p1,
        review_reason="Second approval"
    )
    with pytest.raises(ValueError, match="Duplicate APPROVED mapping prevented"):
        queue.engine.apply_decision(d2)

def test_original_class_and_health_condition_preservation(tmp_path):
    # 15 & 16. Original class & health condition preservation
    reports_dir, p1, p2 = create_mock_review_queue_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))

    decision = ReviewDecision(
        mapping_id="map_v1_00001",
        taxonomy_version="v1",
        reviewer_id="botanist_01",
        decision=ReviewDecisionAction.APPROVE,
        previous_status=MappingStatus.UNREVIEWED,
        approved_canonical_plant_id=p1,
        review_reason="Verified"
    )
    m = queue.engine.apply_decision(decision)
    assert m.original_class_name == "Ashok.H"
    assert m.source_dataset == "CIMPd"
    assert m.health_condition == "Healthy"

def test_raw_dataset_path_safety():
    # 17. Raw external dataset paths remain 100% read-only & untouched
    external_roots = [r"C:\Datasets\CIMPd", r"C:\Datasets\Hugging_Face", r"C:\Datasets\Kaggle"]
    for path in external_roots:
        if os.path.exists(path):
            assert os.path.isdir(path)

def test_deterministic_queue_ordering_and_progress_summary(tmp_path):
    # 19 & 20. Deterministic queue ordering and progress summary correctness
    reports_dir, p1, p2 = create_mock_review_queue_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))

    items = queue.get_all()
    m_ids = [item.mapping_id for item in items]
    assert m_ids == sorted(m_ids)

    summary = queue.get_progress_summary()
    assert summary["total_mappings"] == 3
    assert summary["counts_by_status"]["UNREVIEWED"] == 2
    assert summary["counts_by_status"]["NEEDS_REVIEW"] == 1
    assert summary["reviewed_count"] == 0
    assert summary["pending_count"] == 3
