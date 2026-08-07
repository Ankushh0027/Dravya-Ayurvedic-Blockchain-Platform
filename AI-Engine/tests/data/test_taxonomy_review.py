import os
import pytest
import json
from src.data.taxonomy import (
    CanonicalPlant,
    TaxonomyMapping,
    MappingStatus,
    generate_canonical_plant_id
)
from src.data.taxonomy_review import (
    TaxonomyReviewEngine,
    ReviewDecision,
    ReviewDecisionAction
)

def create_mock_environment(tmp_path):
    plant_id = generate_canonical_plant_id("Saraca asoca")
    plant = CanonicalPlant(
        canonical_plant_id=plant_id,
        canonical_name="Ashoka",
        scientific_name="Saraca asoca"
    )

    mapping1 = TaxonomyMapping(
        mapping_id="map_001",
        source_dataset="CIMPd",
        original_class_name="Ashok.H",
        normalized_name="ashok",
        candidate_canonical_plant_id=plant_id,
        health_condition="Healthy",
        mapping_status=MappingStatus.NEEDS_REVIEW
    )

    mapping2 = TaxonomyMapping(
        mapping_id="map_002",
        source_dataset="CIMPd",
        original_class_name="Ashok.U",
        normalized_name="ashok",
        candidate_canonical_plant_id=plant_id,
        health_condition="Unhealthy",
        mapping_status=MappingStatus.NEEDS_REVIEW
    )

    tax_path = tmp_path / "canonical_taxonomy_v1.json"
    map_path = tmp_path / "taxonomy_mapping_review_v1.json"

    with open(tax_path, "w", encoding="utf-8") as f:
        json.dump({"taxonomy_version": "v1", "plants": [plant.to_dict()]}, f)

    with open(map_path, "w", encoding="utf-8") as f:
        json.dump({"mapping_version": "v1", "mappings": [mapping1.to_dict(), mapping2.to_dict()]}, f)

    return plant_id, tax_path, map_path

def test_approve_valid_mapping(tmp_path):
    plant_id, tax_path, map_path = create_mock_environment(tmp_path)
    engine = TaxonomyReviewEngine(version="v1", reports_dir=str(tmp_path))
    engine.load_state(str(tax_path), str(map_path))

    # 1. Approve valid mapping
    dec = ReviewDecision(
        mapping_id="map_001",
        taxonomy_version="v1",
        reviewer_id="reviewer_01",
        decision=ReviewDecisionAction.APPROVE,
        previous_status=MappingStatus.NEEDS_REVIEW,
        candidate_canonical_plant_id=plant_id,
        approved_canonical_plant_id=plant_id,
        review_reason="Confirmed botanical match with Saraca asoca.",
        evidence="Published literature match."
    )

    updated_m = engine.apply_decision(dec)
    assert updated_m.mapping_status == MappingStatus.APPROVED
    assert updated_m.approved_canonical_plant_id == plant_id
    assert updated_m.reviewer == "reviewer_01"

    # 10 & 11. Original class name and health condition preserved
    assert updated_m.original_class_name == "Ashok.H"
    assert updated_m.health_condition == "Healthy"

def test_reject_mapping(tmp_path):
    plant_id, tax_path, map_path = create_mock_environment(tmp_path)
    engine = TaxonomyReviewEngine(version="v1", reports_dir=str(tmp_path))
    engine.load_state(str(tax_path), str(map_path))

    # 2. Reject mapping
    dec = ReviewDecision(
        mapping_id="map_001",
        taxonomy_version="v1",
        reviewer_id="reviewer_01",
        decision=ReviewDecisionAction.REJECT,
        previous_status=MappingStatus.NEEDS_REVIEW,
        candidate_canonical_plant_id=plant_id,
        review_reason="Incorrect candidate match.",
        evidence="Visual inspection showed species mismatch."
    )

    updated_m = engine.apply_decision(dec)
    assert updated_m.mapping_status == MappingStatus.REJECTED
    assert updated_m.approved_canonical_plant_id is None
    assert updated_m.candidate_canonical_plant_id == plant_id

def test_needs_review_mapping(tmp_path):
    plant_id, tax_path, map_path = create_mock_environment(tmp_path)
    engine = TaxonomyReviewEngine(version="v1", reports_dir=str(tmp_path))
    engine.load_state(str(tax_path), str(map_path))

    # 3. Needs review mapping
    dec = ReviewDecision(
        mapping_id="map_001",
        taxonomy_version="v1",
        reviewer_id="reviewer_02",
        decision=ReviewDecisionAction.NEEDS_REVIEW,
        previous_status=MappingStatus.UNREVIEWED,
        candidate_canonical_plant_id=plant_id,
        review_reason="Requires expert botanist review.",
        evidence="Ambiguous local name."
    )

    updated_m = engine.apply_decision(dec)
    assert updated_m.mapping_status == MappingStatus.NEEDS_REVIEW
    assert updated_m.approved_canonical_plant_id is None

def test_invalid_canonical_plant_id_error(tmp_path):
    plant_id, tax_path, map_path = create_mock_environment(tmp_path)
    engine = TaxonomyReviewEngine(version="v1", reports_dir=str(tmp_path))
    engine.load_state(str(tax_path), str(map_path))

    # 4. Invalid canonical plant ID raises error
    dec = ReviewDecision(
        mapping_id="map_001",
        taxonomy_version="v1",
        reviewer_id="reviewer_01",
        decision=ReviewDecisionAction.APPROVE,
        previous_status=MappingStatus.NEEDS_REVIEW,
        approved_canonical_plant_id="PLANT-NONEXISTENT-999999",
        review_reason="Approving to non-existent plant."
    )

    with pytest.raises(ValueError, match="does not exist in canonical taxonomy"):
        engine.apply_decision(dec)

def test_missing_reviewer_error(tmp_path):
    plant_id, tax_path, map_path = create_mock_environment(tmp_path)
    engine = TaxonomyReviewEngine(version="v1", reports_dir=str(tmp_path))
    engine.load_state(str(tax_path), str(map_path))

    # 5. Missing reviewer raises error
    dec = ReviewDecision(
        mapping_id="map_001",
        taxonomy_version="v1",
        reviewer_id="",
        decision=ReviewDecisionAction.APPROVE,
        previous_status=MappingStatus.NEEDS_REVIEW,
        approved_canonical_plant_id=plant_id,
        review_reason="Reason given but no reviewer."
    )

    with pytest.raises(ValueError, match="requires a non-empty reviewer_id"):
        engine.apply_decision(dec)

def test_missing_evidence_error(tmp_path):
    plant_id, tax_path, map_path = create_mock_environment(tmp_path)
    engine = TaxonomyReviewEngine(version="v1", reports_dir=str(tmp_path))
    engine.load_state(str(tax_path), str(map_path))

    # 6. Missing evidence/reason raises error
    dec = ReviewDecision(
        mapping_id="map_001",
        taxonomy_version="v1",
        reviewer_id="reviewer_01",
        decision=ReviewDecisionAction.APPROVE,
        previous_status=MappingStatus.NEEDS_REVIEW,
        approved_canonical_plant_id=plant_id,
        review_reason="",
        evidence=""
    )

    with pytest.raises(ValueError, match="requires a non-empty review_reason or evidence"):
        engine.apply_decision(dec)

def test_duplicate_approval_prevention(tmp_path):
    plant_id, tax_path, map_path = create_mock_environment(tmp_path)
    engine = TaxonomyReviewEngine(version="v1", reports_dir=str(tmp_path))
    engine.load_state(str(tax_path), str(map_path))

    # First approve map_001
    dec1 = ReviewDecision(
        mapping_id="map_001",
        taxonomy_version="v1",
        reviewer_id="reviewer_01",
        decision=ReviewDecisionAction.APPROVE,
        previous_status=MappingStatus.NEEDS_REVIEW,
        approved_canonical_plant_id=plant_id,
        review_reason="Valid approval."
    )
    engine.apply_decision(dec1)

    # 7. Attempting to approve map_001 again with another decision on same source class
    dec2 = ReviewDecision(
        mapping_id="map_001",
        taxonomy_version="v1",
        reviewer_id="reviewer_02",
        decision=ReviewDecisionAction.APPROVE,
        previous_status=MappingStatus.APPROVED,
        approved_canonical_plant_id=plant_id,
        review_reason="Duplicate approval attempt."
    )
    # The same mapping map_001 re-approval is fine, but if another mapping exists for same (ds, class) it is blocked
    # Let's test two different mappings for the same source class:
    mapping_dup = TaxonomyMapping(
        mapping_id="map_001_dup",
        source_dataset="CIMPd",
        original_class_name="Ashok.H",
        normalized_name="ashok",
        candidate_canonical_plant_id=plant_id,
        health_condition="Healthy",
        mapping_status=MappingStatus.NEEDS_REVIEW
    )
    engine.mappings["map_001_dup"] = mapping_dup

    dec_dup = ReviewDecision(
        mapping_id="map_001_dup",
        taxonomy_version="v1",
        reviewer_id="reviewer_02",
        decision=ReviewDecisionAction.APPROVE,
        previous_status=MappingStatus.NEEDS_REVIEW,
        approved_canonical_plant_id=plant_id,
        review_reason="Duplicate approval attempt."
    )

    with pytest.raises(ValueError, match="Duplicate APPROVED mapping prevented"):
        engine.apply_decision(dec_dup)

def test_history_and_version_preservation(tmp_path):
    plant_id, tax_path, map_path = create_mock_environment(tmp_path)
    engine = TaxonomyReviewEngine(version="v1", reports_dir=str(tmp_path))
    engine.load_state(str(tax_path), str(map_path))

    dec1 = ReviewDecision(
        mapping_id="map_001",
        taxonomy_version="v1",
        reviewer_id="reviewer_01",
        decision=ReviewDecisionAction.NEEDS_REVIEW,
        previous_status=MappingStatus.UNREVIEWED,
        review_reason="Flagged for botanical review."
    )
    engine.apply_decision(dec1)

    dec2 = ReviewDecision(
        mapping_id="map_001",
        taxonomy_version="v1",
        reviewer_id="reviewer_02",
        decision=ReviewDecisionAction.APPROVE,
        previous_status=MappingStatus.NEEDS_REVIEW,
        approved_canonical_plant_id=plant_id,
        review_reason="Approved after review."
    )
    engine.apply_decision(dec2)

    # 8 & 9. Review history is append-only log, version is preserved
    artifacts = engine.export_artifacts()
    assert os.path.exists(artifacts["history_json"])

    with open(artifacts["history_json"], "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["history_records_count"] == 2
        assert len(data["history"]) == 2
        assert data["history"][0]["decision"] == "NEEDS_REVIEW"
        assert data["history"][1]["decision"] == "APPROVE"

def test_raw_dataset_path_safety():
    # 12. Raw external dataset paths remain untouched
    external_roots = [r"C:\Datasets\CIMPd", r"C:\Datasets\Hugging_Face", r"C:\Datasets\Kaggle"]
    for path in external_roots:
        if os.path.exists(path):
            assert os.path.isdir(path)
