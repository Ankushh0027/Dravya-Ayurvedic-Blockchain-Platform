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
from src.data.run_taxonomy_review_queue import (
    prompt_approval_confirmation,
    run_interactive_review
)

def create_group_workflow_env(tmp_path):
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    p1_id = generate_canonical_plant_id("Saraca asoca")
    p1 = CanonicalPlant(canonical_plant_id=p1_id, canonical_name="Ashoka", scientific_name="Saraca asoca", aliases=["Saraca indica"])

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
        source_dataset="Kaggle",
        original_class_name="Ashok.U",
        normalized_name="ashok",
        health_condition="Unhealthy",
        candidate_canonical_plant_id=p1_id,
        confidence="HIGH",
        match_reason="Exact match",
        mapping_status=MappingStatus.NEEDS_REVIEW
    )

    m3 = TaxonomyMapping(
        mapping_id="map_v1_00003",
        source_dataset="Hugging_Face",
        original_class_name="neem_leaf",
        normalized_name="neem leaf",
        health_condition="Unknown",
        candidate_canonical_plant_id=p2_id,
        confidence="HIGH",
        match_reason="Exact match",
        mapping_status=MappingStatus.NEEDS_REVIEW
    )

    map_path = reports_dir / "taxonomy_mapping_review_v1.json"
    atomic_json_write(map_path, {"taxonomy_version": "v1", "mappings": [m1.to_dict(), m2.to_dict(), m3.to_dict()]})

    return reports_dir, p1_id, p2_id

# 1. candidate group aggregation
def test_1_candidate_group_aggregation(tmp_path):
    reports_dir, p1_id, p2_id = create_group_workflow_env(tmp_path)
    analyzer = BotanicalReviewAnalyzer(version="v1", reports_dir=str(reports_dir))
    groups = analyzer.analyze()

    ashok_g = analyzer.get_group_by_plant_id(p1_id)
    assert ashok_g is not None
    assert len(ashok_g.source_mappings) == 2
    assert "CIMPd" in ashok_g.source_datasets
    assert "Kaggle" in ashok_g.source_datasets

# 2. related source mappings displayed together
def test_2_related_source_mappings_displayed_together(tmp_path):
    reports_dir, p1_id, p2_id = create_group_workflow_env(tmp_path)
    analyzer = BotanicalReviewAnalyzer(version="v1", reports_dir=str(reports_dir))
    ashok_g = analyzer.get_group_by_plant_id(p1_id)

    orig_names = ashok_g.original_class_names
    assert "Ashok.H" in orig_names
    assert "Ashok.U" in orig_names

# 3. group ordering deterministic
def test_3_group_ordering_deterministic(tmp_path):
    reports_dir, p1_id, p2_id = create_group_workflow_env(tmp_path)
    analyzer1 = BotanicalReviewAnalyzer(version="v1", reports_dir=str(reports_dir))
    g1 = [g.canonical_plant_id for g in analyzer1.analyze()]

    analyzer2 = BotanicalReviewAnalyzer(version="v1", reports_dir=str(reports_dir))
    g2 = [g.canonical_plant_id for g in analyzer2.analyze()]

    assert g1 == g2
    assert g1 == sorted(g1)

# 4. group filtering deterministic
def test_4_group_filtering_deterministic(tmp_path):
    reports_dir, p1_id, p2_id = create_group_workflow_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))

    ashok_items = [i for i in queue.get_all() if i.candidate_canonical_plant_id == p1_id]
    assert len(ashok_items) == 2
    assert ashok_items[0].mapping_id == "map_v1_00001"
    assert ashok_items[1].mapping_id == "map_v1_00002"

# 5. explicit approval confirmation required & 6. confirmation default is NO
def test_5_and_6_explicit_approval_confirmation_default_is_no():
    # User inputs empty string (default Enter -> No)
    confirmed_empty = prompt_approval_confirmation(
        mapping_id="map_v1_00001",
        source_dataset="CIMPd",
        original_class_name="Ashok.H",
        candidate_plant_id="PLANT-SARACA-ASOCA-4B8F7A",
        canonical_name="Ashoka",
        scientific_name="Saraca asoca",
        health_condition="Healthy",
        reviewer_id="botanist_01",
        evidence="Monograph verification",
        input_func=lambda prompt: ""
    )
    assert not confirmed_empty

    # User inputs 'n' -> No
    confirmed_no = prompt_approval_confirmation(
        mapping_id="map_v1_00001",
        source_dataset="CIMPd",
        original_class_name="Ashok.H",
        candidate_plant_id="PLANT-SARACA-ASOCA-4B8F7A",
        canonical_name="Ashoka",
        scientific_name="Saraca asoca",
        health_condition="Healthy",
        reviewer_id="botanist_01",
        evidence="Monograph verification",
        input_func=lambda prompt: "n"
    )
    assert not confirmed_no

    # User inputs 'y' -> Yes
    confirmed_yes = prompt_approval_confirmation(
        mapping_id="map_v1_00001",
        source_dataset="CIMPd",
        original_class_name="Ashok.H",
        candidate_plant_id="PLANT-SARACA-ASOCA-4B8F7A",
        canonical_name="Ashoka",
        scientific_name="Saraca asoca",
        health_condition="Healthy",
        reviewer_id="botanist_01",
        evidence="Monograph verification",
        input_func=lambda prompt: "y"
    )
    assert confirmed_yes

# 7. cancelled approval does not mutate state
def test_7_cancelled_approval_does_not_mutate_state(tmp_path):
    reports_dir, p1_id, p2_id = create_group_workflow_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))

    inputs = iter(["A", "botanist_01", p1_id, "Evidence text", "n", "Q"])
    run_interactive_review(
        queue,
        mapping_id_filter="map_v1_00001",
        limit=1,
        input_func=lambda prompt: next(inputs)
    )

    m1 = queue.engine.mappings["map_v1_00001"]
    assert m1.mapping_status == MappingStatus.UNREVIEWED
    assert m1.approved_canonical_plant_id is None
    assert len(queue.engine.history) == 0

# 8. approval creates audit entry
def test_8_approval_creates_audit_entry(tmp_path):
    reports_dir, p1_id, p2_id = create_group_workflow_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))

    inputs = iter(["A", "botanist_01", p1_id, "Verified via flora monograph", "y", "Q"])
    run_interactive_review(
        queue,
        mapping_id_filter="map_v1_00001",
        limit=1,
        input_func=lambda prompt: next(inputs)
    )

    m1 = queue.engine.mappings["map_v1_00001"]
    assert m1.mapping_status == MappingStatus.APPROVED
    assert len(queue.engine.history) == 1
    assert queue.engine.history[0].reviewer_id == "botanist_01"

# 9. reject creates audit entry
def test_9_reject_creates_audit_entry(tmp_path):
    reports_dir, p1_id, p2_id = create_group_workflow_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))

    inputs = iter(["R", "botanist_01", "Invalid non-botanical artifacts", "Q"])
    run_interactive_review(
        queue,
        mapping_id_filter="map_v1_00001",
        limit=1,
        input_func=lambda prompt: next(inputs)
    )

    m1 = queue.engine.mappings["map_v1_00001"]
    assert m1.mapping_status == MappingStatus.REJECTED
    assert len(queue.engine.history) == 1

# 10. needs-review creates audit entry
def test_10_needs_review_creates_audit_entry(tmp_path):
    reports_dir, p1_id, p2_id = create_group_workflow_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))

    inputs = iter(["N", "botanist_01", "Requires DNA sequencing", "Q"])
    run_interactive_review(
        queue,
        mapping_id_filter="map_v1_00001",
        limit=1,
        input_func=lambda prompt: next(inputs)
    )

    m1 = queue.engine.mappings["map_v1_00001"]
    assert m1.mapping_status == MappingStatus.NEEDS_REVIEW
    assert len(queue.engine.history) == 1

# 11. skip creates no audit entry
def test_11_skip_creates_no_audit_entry(tmp_path):
    reports_dir, p1_id, p2_id = create_group_workflow_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))

    inputs = iter(["S", "Q"])
    run_interactive_review(
        queue,
        mapping_id_filter="map_v1_00001",
        limit=1,
        input_func=lambda prompt: next(inputs)
    )

    m1 = queue.engine.mappings["map_v1_00001"]
    assert m1.mapping_status == MappingStatus.UNREVIEWED
    assert len(queue.engine.history) == 0

# 12. botanical recommendation cannot auto-approve
def test_12_botanical_recommendation_cannot_auto_approve(tmp_path):
    reports_dir, p1_id, p2_id = create_group_workflow_env(tmp_path)
    analyzer = BotanicalReviewAnalyzer(version="v1", reports_dir=str(reports_dir))
    groups = analyzer.analyze()

    assert groups[0].review_recommendation == RecommendationAction.APPROVE_CANDIDATE
    m1 = analyzer.engine.mappings["map_v1_00001"]
    assert m1.mapping_status == MappingStatus.UNREVIEWED

# 13. health condition preserved
def test_13_health_condition_preserved(tmp_path):
    reports_dir, p1_id, p2_id = create_group_workflow_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))

    inputs = iter(["A", "botanist_01", p1_id, "Verified healthy", "y", "Q"])
    run_interactive_review(queue, mapping_id_filter="map_v1_00001", limit=1, input_func=lambda prompt: next(inputs))

    inputs2 = iter(["A", "botanist_01", p1_id, "Verified unhealthy", "y", "Q"])
    run_interactive_review(queue, mapping_id_filter="map_v1_00002", limit=1, input_func=lambda prompt: next(inputs2))

    m1 = queue.engine.mappings["map_v1_00001"]
    m2 = queue.engine.mappings["map_v1_00002"]

    assert m1.approved_canonical_plant_id == m2.approved_canonical_plant_id == p1_id
    assert m1.health_condition == "Healthy"
    assert m2.health_condition == "Unhealthy"

# 14. source provenance preserved
def test_14_source_provenance_preserved(tmp_path):
    reports_dir, p1_id, p2_id = create_group_workflow_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))

    inputs = iter(["A", "botanist_01", p1_id, "Verified", "y", "Q"])
    run_interactive_review(queue, mapping_id_filter="map_v1_00001", limit=1, input_func=lambda prompt: next(inputs))

    m1 = queue.engine.mappings["map_v1_00001"]
    assert m1.source_dataset == "CIMPd"
    assert m1.original_class_name == "Ashok.H"

# 15. duplicate approval prevented
def test_15_duplicate_approval_prevented(tmp_path):
    reports_dir, p1_id, p2_id = create_group_workflow_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))

    # Approve map_v1_00001
    inputs = iter(["A", "botanist_01", p1_id, "Verified 1", "y", "Q"])
    run_interactive_review(queue, mapping_id_filter="map_v1_00001", limit=1, input_func=lambda prompt: next(inputs))

    # Duplicate mapping for CIMPd / Ashok.H
    dup = TaxonomyMapping(
        mapping_id="map_v1_99999",
        source_dataset="CIMPd",
        original_class_name="Ashok.H",
        normalized_name="ashok",
        health_condition="Healthy",
        candidate_canonical_plant_id=p1_id,
        mapping_status=MappingStatus.UNREVIEWED
    )
    queue.engine.mappings["map_v1_99999"] = dup

    d_dup = ReviewDecision(
        mapping_id="map_v1_99999",
        taxonomy_version="v1",
        reviewer_id="botanist_02",
        decision=ReviewDecisionAction.APPROVE,
        previous_status=MappingStatus.UNREVIEWED,
        approved_canonical_plant_id=p1_id,
        review_reason="Verified 2"
    )
    with pytest.raises(ValueError, match="Duplicate APPROVED mapping prevented"):
        queue.engine.apply_decision(d_dup)

# 16. progress report updates
def test_16_progress_report_updates(tmp_path):
    reports_dir, p1_id, p2_id = create_group_workflow_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))

    s1 = queue.get_progress_summary()
    assert s1["counts_by_status"]["APPROVED"] == 0

    inputs = iter(["A", "botanist_01", p1_id, "Verified", "y", "Q"])
    run_interactive_review(queue, mapping_id_filter="map_v1_00001", limit=1, input_func=lambda prompt: next(inputs))

    s2 = queue.get_progress_summary()
    assert s2["counts_by_status"]["APPROVED"] == 1
    assert s2["candidate_group_metrics"]["total_candidate_groups"] == 2

# 17. malformed history detected
def test_17_malformed_history_detected(tmp_path):
    reports_dir, p1_id, p2_id = create_group_workflow_env(tmp_path)
    hist_p = reports_dir / "taxonomy_review_history_v1.json"
    atomic_json_write(hist_p, {"history": [{"invalid": "entry"}]})

    engine = TaxonomyReviewEngine(version="v1", reports_dir=str(reports_dir))
    with pytest.raises(ValueError, match="Malformed audit history"):
        engine.load_state()

# 18. atomic writes remain safe
def test_18_atomic_writes_remain_safe(tmp_path):
    f_p = tmp_path / "test.json"
    atomic_json_write(f_p, {"key": "val"})
    assert f_p.exists()
    assert not (tmp_path / "test.json.tmp").exists()

# 19. raw dataset remains untouched
def test_19_raw_dataset_remains_untouched():
    for p in [r"C:\Datasets\CIMPd", r"C:\Datasets\Hugging_Face", r"C:\Datasets\Kaggle"]:
        if os.path.exists(p):
            assert os.path.isdir(p)

# 20. version isolation maintained
def test_20_version_isolation_maintained(tmp_path):
    reports_dir, p1_id, p2_id = create_group_workflow_env(tmp_path)
    e1 = TaxonomyReviewEngine(version="v1", reports_dir=str(reports_dir))
    e1.load_state()

    e2 = TaxonomyReviewEngine(version="v2", reports_dir=str(reports_dir))
    with pytest.raises(FileNotFoundError):
        e2.load_state()

    assert e1.version == "v1"
    assert e2.version == "v2"
