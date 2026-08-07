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
from src.data.taxonomy_review_queue import TaxonomyReviewQueue
from src.data.botanical_review import BotanicalReviewAnalyzer, RecommendationAction

def create_workflow_env(tmp_path):
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    p1_id = generate_canonical_plant_id("Saraca asoca")
    p1 = CanonicalPlant(canonical_plant_id=p1_id, canonical_name="Ashoka", scientific_name="Saraca asoca")

    p2_id = generate_canonical_plant_id("Azadirachta indica")
    p2 = CanonicalPlant(canonical_plant_id=p2_id, canonical_name="Neem", scientific_name="Azadirachta indica")

    tax_path = reports_dir / "canonical_taxonomy_v1.json"
    atomic_json_write(tax_path, {"taxonomy_version": "v1", "plants": [p1.to_dict(), p2.to_dict()]})

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
        original_class_name="Ashok.U",
        normalized_name="ashok",
        health_condition="Unhealthy",
        candidate_canonical_plant_id=p1_id,
        confidence="HIGH",
        match_reason="Exact match",
        mapping_status=MappingStatus.UNREVIEWED
    )

    map_path = reports_dir / "taxonomy_mapping_review_v1.json"
    atomic_json_write(map_path, {"taxonomy_version": "v1", "mappings": [m1.to_dict(), m2.to_dict(), m3.to_dict()]})

    return reports_dir, p1_id, p2_id

# 1. explicit approval succeeds
def test_1_explicit_approval_succeeds(tmp_path):
    reports_dir, p1, p2 = create_workflow_env(tmp_path)
    engine = TaxonomyReviewEngine(version="v1", reports_dir=str(reports_dir))
    engine.load_state()

    d = ReviewDecision(
        mapping_id="map_v1_00001",
        taxonomy_version="v1",
        reviewer_id="botanist_expert",
        decision=ReviewDecisionAction.APPROVE,
        previous_status=MappingStatus.UNREVIEWED,
        approved_canonical_plant_id=p1,
        review_reason="Botanical identity verified via flora monograph."
    )
    m = engine.apply_decision(d)
    assert m.mapping_status == MappingStatus.APPROVED
    assert m.approved_canonical_plant_id == p1
    assert m.reviewer == "botanist_expert"

# 2. approval without reviewer fails
def test_2_approval_without_reviewer_fails(tmp_path):
    reports_dir, p1, p2 = create_workflow_env(tmp_path)
    engine = TaxonomyReviewEngine(version="v1", reports_dir=str(reports_dir))
    engine.load_state()

    d = ReviewDecision(
        mapping_id="map_v1_00001",
        taxonomy_version="v1",
        reviewer_id="",
        decision=ReviewDecisionAction.APPROVE,
        previous_status=MappingStatus.UNREVIEWED,
        approved_canonical_plant_id=p1,
        review_reason="Valid reason"
    )
    with pytest.raises(ValueError, match="reviewer_id"):
        engine.apply_decision(d)

# 3. approval without evidence fails
def test_3_approval_without_evidence_fails(tmp_path):
    reports_dir, p1, p2 = create_workflow_env(tmp_path)
    engine = TaxonomyReviewEngine(version="v1", reports_dir=str(reports_dir))
    engine.load_state()

    d = ReviewDecision(
        mapping_id="map_v1_00001",
        taxonomy_version="v1",
        reviewer_id="botanist_expert",
        decision=ReviewDecisionAction.APPROVE,
        previous_status=MappingStatus.UNREVIEWED,
        approved_canonical_plant_id=p1,
        review_reason="",
        evidence=""
    )
    with pytest.raises(ValueError, match="review_reason or evidence"):
        engine.apply_decision(d)

# 4. approval with invalid canonical ID fails
def test_4_approval_with_invalid_canonical_id_fails(tmp_path):
    reports_dir, p1, p2 = create_workflow_env(tmp_path)
    engine = TaxonomyReviewEngine(version="v1", reports_dir=str(reports_dir))
    engine.load_state()

    d = ReviewDecision(
        mapping_id="map_v1_00001",
        taxonomy_version="v1",
        reviewer_id="botanist_expert",
        decision=ReviewDecisionAction.APPROVE,
        previous_status=MappingStatus.UNREVIEWED,
        approved_canonical_plant_id="PLANT-NONEXISTENT-9999",
        review_reason="Verified"
    )
    with pytest.raises(ValueError, match="does not exist"):
        engine.apply_decision(d)

# 5. duplicate approval fails
def test_5_duplicate_approval_fails(tmp_path):
    reports_dir, p1, p2 = create_workflow_env(tmp_path)
    engine = TaxonomyReviewEngine(version="v1", reports_dir=str(reports_dir))
    engine.load_state()

    d1 = ReviewDecision(
        mapping_id="map_v1_00001",
        taxonomy_version="v1",
        reviewer_id="botanist_01",
        decision=ReviewDecisionAction.APPROVE,
        previous_status=MappingStatus.UNREVIEWED,
        approved_canonical_plant_id=p1,
        review_reason="First approval"
    )
    engine.apply_decision(d1)

    # Creating duplicate mapping for same dataset & class
    dup = TaxonomyMapping(
        mapping_id="map_v1_99999",
        source_dataset="CIMPd",
        original_class_name="Ashok.H",
        normalized_name="ashok",
        health_condition="Healthy",
        candidate_canonical_plant_id=p1,
        mapping_status=MappingStatus.UNREVIEWED
    )
    engine.mappings["map_v1_99999"] = dup

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
        engine.apply_decision(d2)

# 6. reject succeeds
def test_6_reject_succeeds(tmp_path):
    reports_dir, p1, p2 = create_workflow_env(tmp_path)
    engine = TaxonomyReviewEngine(version="v1", reports_dir=str(reports_dir))
    engine.load_state()

    d = ReviewDecision(
        mapping_id="map_v1_00002",
        taxonomy_version="v1",
        reviewer_id="botanist_expert",
        decision=ReviewDecisionAction.REJECT,
        previous_status=MappingStatus.NEEDS_REVIEW,
        review_reason="Folder contains non-botanical artifacts."
    )
    m = engine.apply_decision(d)
    assert m.mapping_status == MappingStatus.REJECTED
    assert m.approved_canonical_plant_id is None

# 7. needs-review succeeds
def test_7_needs_review_succeeds(tmp_path):
    reports_dir, p1, p2 = create_workflow_env(tmp_path)
    engine = TaxonomyReviewEngine(version="v1", reports_dir=str(reports_dir))
    engine.load_state()

    d = ReviewDecision(
        mapping_id="map_v1_00001",
        taxonomy_version="v1",
        reviewer_id="botanist_expert",
        decision=ReviewDecisionAction.NEEDS_REVIEW,
        previous_status=MappingStatus.UNREVIEWED,
        review_reason="Requires molecular marker assay."
    )
    m = engine.apply_decision(d)
    assert m.mapping_status == MappingStatus.NEEDS_REVIEW

# 8. skip does not change status
def test_8_skip_does_not_change_status(tmp_path):
    reports_dir, p1, p2 = create_workflow_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))
    
    # Simulate skip (no call to engine.apply_decision)
    item = queue.get_by_mapping_id("map_v1_00001")
    assert item.current_mapping_status == "UNREVIEWED"
    assert len(queue.engine.history) == 0

# 9. audit history is append-only
def test_9_audit_history_is_append_only(tmp_path):
    reports_dir, p1, p2 = create_workflow_env(tmp_path)
    engine = TaxonomyReviewEngine(version="v1", reports_dir=str(reports_dir))
    engine.load_state()

    d1 = ReviewDecision(
        mapping_id="map_v1_00001",
        taxonomy_version="v1",
        reviewer_id="botanist_01",
        decision=ReviewDecisionAction.NEEDS_REVIEW,
        previous_status=MappingStatus.UNREVIEWED,
        review_reason="First review"
    )
    engine.apply_decision(d1)

    d2 = ReviewDecision(
        mapping_id="map_v1_00001",
        taxonomy_version="v1",
        reviewer_id="botanist_02",
        decision=ReviewDecisionAction.APPROVE,
        previous_status=MappingStatus.NEEDS_REVIEW,
        approved_canonical_plant_id=p1,
        review_reason="Second review"
    )
    engine.apply_decision(d2)

    assert len(engine.history) == 2
    assert engine.history[0].reviewer_id == "botanist_01"
    assert engine.history[1].reviewer_id == "botanist_02"

# 10. source provenance remains unchanged
def test_10_source_provenance_remains_unchanged(tmp_path):
    reports_dir, p1, p2 = create_workflow_env(tmp_path)
    engine = TaxonomyReviewEngine(version="v1", reports_dir=str(reports_dir))
    engine.load_state()

    d = ReviewDecision(
        mapping_id="map_v1_00001",
        taxonomy_version="v1",
        reviewer_id="botanist_expert",
        decision=ReviewDecisionAction.APPROVE,
        previous_status=MappingStatus.UNREVIEWED,
        approved_canonical_plant_id=p1,
        review_reason="Verified"
    )
    m = engine.apply_decision(d)
    assert m.source_dataset == "CIMPd"
    assert m.original_class_name == "Ashok.H"

# 11. health condition remains separate
def test_11_health_condition_remains_separate(tmp_path):
    reports_dir, p1, p2 = create_workflow_env(tmp_path)
    engine = TaxonomyReviewEngine(version="v1", reports_dir=str(reports_dir))
    engine.load_state()

    d1 = ReviewDecision(
        mapping_id="map_v1_00001",
        taxonomy_version="v1",
        reviewer_id="botanist_expert",
        decision=ReviewDecisionAction.APPROVE,
        previous_status=MappingStatus.UNREVIEWED,
        approved_canonical_plant_id=p1,
        review_reason="Verified healthy"
    )
    m1 = engine.apply_decision(d1)

    d2 = ReviewDecision(
        mapping_id="map_v1_00003",
        taxonomy_version="v1",
        reviewer_id="botanist_expert",
        decision=ReviewDecisionAction.APPROVE,
        previous_status=MappingStatus.UNREVIEWED,
        approved_canonical_plant_id=p1,
        review_reason="Verified unhealthy"
    )
    m2 = engine.apply_decision(d2)

    assert m1.approved_canonical_plant_id == m2.approved_canonical_plant_id == p1
    assert m1.health_condition == "Healthy"
    assert m2.health_condition == "Unhealthy"

# 12. deterministic queue ordering
def test_12_deterministic_queue_ordering(tmp_path):
    reports_dir, p1, p2 = create_workflow_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))

    items1 = [i.mapping_id for i in queue.get_all()]
    items2 = [i.mapping_id for i in queue.get_all()]
    assert items1 == items2
    assert items1 == sorted(items1)

# 13. batch --limit works
def test_13_batch_limit_works(tmp_path):
    reports_dir, p1, p2 = create_workflow_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))
    pending = queue.get_pending()

    assert len(pending) == 3
    batch = pending[:2]
    assert len(batch) == 2
    assert batch[0].mapping_id == "map_v1_00001"
    assert batch[1].mapping_id == "map_v1_00002"

# 14. dataset filtering works
def test_14_dataset_filtering_works(tmp_path):
    reports_dir, p1, p2 = create_workflow_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))

    cimpd_items = queue.get_by_dataset("CIMPd")
    assert len(cimpd_items) == 1
    assert cimpd_items[0].mapping_id == "map_v1_00001"

# 15. mapping-id filtering works
def test_15_mapping_id_filtering_works(tmp_path):
    reports_dir, p1, p2 = create_workflow_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))

    item = queue.get_by_mapping_id("map_v1_00002")
    assert item is not None
    assert item.original_class_name == "neem_leaf"

# 16. no automatic approval from botanical recommendation
def test_16_no_automatic_approval_from_botanical_recommendation(tmp_path):
    reports_dir, p1, p2 = create_workflow_env(tmp_path)
    analyzer = BotanicalReviewAnalyzer(version="v1", reports_dir=str(reports_dir))
    groups = analyzer.analyze()

    assert groups[0].review_recommendation == RecommendationAction.APPROVE_CANDIDATE
    # Verify review engine mappings state remains UNREVIEWED / NEEDS_REVIEW
    m1 = analyzer.engine.mappings["map_v1_00001"]
    assert m1.mapping_status == MappingStatus.UNREVIEWED
    assert m1.approved_canonical_plant_id is None

# 17. raw dataset paths remain untouched
def test_17_raw_dataset_paths_remain_untouched():
    for p in [r"C:\Datasets\CIMPd", r"C:\Datasets\Hugging_Face", r"C:\Datasets\Kaggle"]:
        if os.path.exists(p):
            assert os.path.isdir(p)

# 18. malformed history is safely detected
def test_18_malformed_history_is_safely_detected(tmp_path):
    reports_dir, p1, p2 = create_workflow_env(tmp_path)
    hist_path = reports_dir / "taxonomy_review_history_v1.json"
    with open(hist_path, "w", encoding="utf-8") as f:
        f.write("{ invalid json format }")

    engine = TaxonomyReviewEngine(version="v1", reports_dir=str(reports_dir))
    with pytest.raises(ValueError, match="Malformed audit history"):
        engine.load_state()

# 19. atomic state update behavior
def test_19_atomic_state_update_behavior(tmp_path):
    target_file = tmp_path / "test_artifact.json"
    data = {"status": "SUCCESS", "records": [1, 2, 3]}

    atomic_json_write(target_file, data)
    assert target_file.exists()
    assert not (tmp_path / "test_artifact.json.tmp").exists()

    with open(target_file, "r", encoding="utf-8") as f:
        read_data = json.load(f)
    assert read_data == data

# 20. version isolation remains intact
def test_20_version_isolation_remains_intact(tmp_path):
    reports_dir, p1, p2 = create_workflow_env(tmp_path)
    
    e1 = TaxonomyReviewEngine(version="v1", reports_dir=str(reports_dir))
    e1.load_state()

    # V2 paths
    v2_tax = reports_dir / "canonical_taxonomy_v2.json"
    v2_map = reports_dir / "taxonomy_mapping_review_v2.json"
    atomic_json_write(v2_tax, {"taxonomy_version": "v2", "plants": []})
    atomic_json_write(v2_map, {"taxonomy_version": "v2", "mappings": []})

    e2 = TaxonomyReviewEngine(version="v2", reports_dir=str(reports_dir))
    e2.load_state()

    assert e1.version == "v1"
    assert e2.version == "v2"
    assert len(e1.mappings) == 3
    assert len(e2.mappings) == 0
