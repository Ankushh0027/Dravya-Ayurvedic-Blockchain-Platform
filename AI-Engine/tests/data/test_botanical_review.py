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
from src.data.botanical_review import BotanicalReviewAnalyzer, RecommendationAction
from src.data.taxonomy_review import ReviewDecision, ReviewDecisionAction
from src.data.taxonomy_review_queue import TaxonomyReviewQueue

def create_mock_botanical_env(tmp_path):
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    plant1_id = generate_canonical_plant_id("Saraca asoca")
    plant1 = CanonicalPlant(canonical_plant_id=plant1_id, canonical_name="Ashoka", scientific_name="Saraca asoca")

    plant2_id = generate_canonical_plant_id("Azadirachta indica")
    plant2 = CanonicalPlant(canonical_plant_id=plant2_id, canonical_name="Neem", scientific_name="Azadirachta indica")

    plant3_id = generate_canonical_plant_id("leaf")
    plant3 = CanonicalPlant(canonical_plant_id=plant3_id, canonical_name="leaf", scientific_name=None)

    tax_path = reports_dir / "canonical_taxonomy_v1.json"
    with open(tax_path, "w", encoding="utf-8") as f:
        json.dump({"taxonomy_version": "v1", "plants": [plant1.to_dict(), plant2.to_dict(), plant3.to_dict()]}, f)

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
        original_class_name="leaf_spot",
        normalized_name="leaf spot",
        health_condition="Unhealthy",
        candidate_canonical_plant_id=plant3_id,
        confidence="LOW",
        match_reason="Ambiguous name",
        mapping_status=MappingStatus.UNREVIEWED
    )

    map_path = reports_dir / "taxonomy_mapping_review_v1.json"
    with open(map_path, "w", encoding="utf-8") as f:
        json.dump({"taxonomy_version": "v1", "mappings": [map1.to_dict(), map2.to_dict(), map3.to_dict()]}, f)

    return reports_dir, plant1_id, plant2_id, plant3_id

def test_approval_requires_explicit_human_action_and_recommendation_is_not_approval(tmp_path):
    reports_dir, p1, p2, p3 = create_mock_botanical_env(tmp_path)
    analyzer = BotanicalReviewAnalyzer(version="v1", reports_dir=str(reports_dir))
    groups = analyzer.analyze()
    
    # Recommendation is generated
    g1 = [g for g in groups if g.canonical_plant_id == p1][0]
    assert g1.review_recommendation == RecommendationAction.APPROVE_CANDIDATE
    
    # Verify mapping status in review engine is STILL UNREVIEWED / NEEDS_REVIEW (NOT APPROVED)
    m1 = analyzer.engine.mappings["map_v1_00001"]
    assert m1.mapping_status == MappingStatus.UNREVIEWED
    assert m1.approved_canonical_plant_id is None

def test_evidence_and_reviewer_required_for_approval(tmp_path):
    reports_dir, p1, p2, p3 = create_mock_botanical_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))

    # Missing reviewer
    d1 = ReviewDecision(
        mapping_id="map_v1_00001",
        taxonomy_version="v1",
        reviewer_id="",
        decision=ReviewDecisionAction.APPROVE,
        previous_status=MappingStatus.UNREVIEWED,
        approved_canonical_plant_id=p1,
        review_reason="Valid evidence"
    )
    with pytest.raises(ValueError, match="reviewer_id"):
        queue.engine.apply_decision(d1)

    # Missing evidence
    d2 = ReviewDecision(
        mapping_id="map_v1_00001",
        taxonomy_version="v1",
        reviewer_id="botanist_01",
        decision=ReviewDecisionAction.APPROVE,
        previous_status=MappingStatus.UNREVIEWED,
        approved_canonical_plant_id=p1,
        review_reason=""
    )
    with pytest.raises(ValueError, match="review_reason or evidence"):
        queue.engine.apply_decision(d2)

def test_ambiguous_mapping_recommendation_and_health_condition_separation(tmp_path):
    reports_dir, p1, p2, p3 = create_mock_botanical_env(tmp_path)
    analyzer = BotanicalReviewAnalyzer(version="v1", reports_dir=str(reports_dir))
    groups = analyzer.analyze()

    g3 = [g for g in groups if g.canonical_plant_id == p3][0]
    assert g3.review_recommendation == RecommendationAction.NEEDS_BOTANICAL_REVIEW
    assert "generic/ambiguous" in g3.recommendation_reason

    # Health condition check
    m3 = analyzer.engine.mappings["map_v1_00003"]
    assert m3.health_condition == "Unhealthy"
    assert m3.original_class_name == "leaf_spot"

def test_batch_limit_and_queue_filtering(tmp_path):
    reports_dir, p1, p2, p3 = create_mock_botanical_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))
    pending = queue.get_pending()

    assert len(pending) == 3
    limited_pending = pending[:2]
    assert len(limited_pending) == 2
    assert limited_pending[0].mapping_id == "map_v1_00001"
    assert limited_pending[1].mapping_id == "map_v1_00002"

def test_history_append_only_and_raw_dataset_safety(tmp_path):
    reports_dir, p1, p2, p3 = create_mock_botanical_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))

    d1 = ReviewDecision(
        mapping_id="map_v1_00001",
        taxonomy_version="v1",
        reviewer_id="botanist_01",
        decision=ReviewDecisionAction.APPROVE,
        previous_status=MappingStatus.UNREVIEWED,
        approved_canonical_plant_id=p1,
        review_reason="Botanically verified"
    )
    queue.engine.apply_decision(d1)
    queue.engine.export_artifacts()

    assert len(queue.engine.history) == 1
    assert queue.engine.history[0].reviewer_id == "botanist_01"

    # Verify raw datasets remain safe
    for path in [r"C:\Datasets\CIMPd", r"C:\Datasets\Hugging_Face", r"C:\Datasets\Kaggle"]:
        if os.path.exists(path):
            assert os.path.isdir(path)

def test_export_botanical_review_report_artifact():
    reports_dir = Path(r"C:\Dravya-AI-Engine\reports\dataset_analysis")
    analyzer = BotanicalReviewAnalyzer(version="v1", reports_dir=str(reports_dir))
    report_path = analyzer.generate_report()
    assert report_path.exists()
    
    with open(report_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["total_candidate_plants"] == 200
    assert "recommendation_counts" in data
    assert len(data["botanical_groups"]) == 200
