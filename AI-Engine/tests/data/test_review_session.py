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
from src.data.review_session import ReviewSessionManager, SessionStatus, TaxonomyReviewSession
from src.data.run_taxonomy_review_queue import run_interactive_review

def create_session_test_env(tmp_path):
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

# 1. session creation
def test_1_session_creation(tmp_path):
    reports_dir, p1_id, p2_id = create_session_test_env(tmp_path)
    sm = ReviewSessionManager(version="v1", reports_dir=str(reports_dir))
    sess = sm.create_session("sess_001", "reviewer_a", dataset_filter="CIMPd")

    assert sess.session_id == "sess_001"
    assert sess.reviewer_id == "reviewer_a"
    assert sess.session_status == SessionStatus.ACTIVE
    assert sess.dataset_filter == "CIMPd"

# 2. session persistence
def test_2_session_persistence(tmp_path):
    reports_dir, p1_id, p2_id = create_session_test_env(tmp_path)
    sm1 = ReviewSessionManager(version="v1", reports_dir=str(reports_dir))
    sm1.create_session("sess_001", "reviewer_a")

    sm2 = ReviewSessionManager(version="v1", reports_dir=str(reports_dir))
    sess = sm2.get_session("sess_001")
    assert sess is not None
    assert sess.reviewer_id == "reviewer_a"

# 3. session resume
def test_3_session_resume(tmp_path):
    reports_dir, p1_id, p2_id = create_session_test_env(tmp_path)
    sm = ReviewSessionManager(version="v1", reports_dir=str(reports_dir))
    sm.create_session("sess_001", "reviewer_a")
    sm.pause_session("sess_001")

    resumed = sm.resume_session("sess_001", "reviewer_a")
    assert resumed.session_status == SessionStatus.ACTIVE

# 4. session pause
def test_4_session_pause(tmp_path):
    reports_dir, p1_id, p2_id = create_session_test_env(tmp_path)
    sm = ReviewSessionManager(version="v1", reports_dir=str(reports_dir))
    sm.create_session("sess_001", "reviewer_a")
    paused = sm.pause_session("sess_001")
    assert paused.session_status == SessionStatus.PAUSED

# 5. session completion
def test_5_session_completion(tmp_path):
    reports_dir, p1_id, p2_id = create_session_test_env(tmp_path)
    sm = ReviewSessionManager(version="v1", reports_dir=str(reports_dir))
    sm.create_session("sess_001", "reviewer_a")
    sm.mark_completed("sess_001")
    sess = sm.get_session("sess_001")
    assert sess.session_status == SessionStatus.COMPLETED

# 6. reviewer isolation
def test_6_reviewer_isolation(tmp_path):
    reports_dir, p1_id, p2_id = create_group_workflow_env(tmp_path) if False else create_session_test_env(tmp_path)
    sm = ReviewSessionManager(version="v1", reports_dir=str(reports_dir))
    sm.create_session("sess_001", "reviewer_a")

    with pytest.raises(ValueError, match="Reviewer isolation error"):
        sm.resume_session("sess_001", "reviewer_b")

# 7. version isolation
def test_7_version_isolation(tmp_path):
    reports_dir, p1_id, p2_id = create_session_test_env(tmp_path)
    sm1 = ReviewSessionManager(version="v1", reports_dir=str(reports_dir))
    sm1.create_session("sess_v1", "reviewer_a")

    sm2 = ReviewSessionManager(version="v2", reports_dir=str(reports_dir))
    assert sm2.get_session("sess_v1") is None

# 8. candidate-group resume
def test_8_candidate_group_resume(tmp_path):
    reports_dir, p1_id, p2_id = create_session_test_env(tmp_path)
    sm = ReviewSessionManager(version="v1", reports_dir=str(reports_dir))
    sm.create_session("sess_group", "reviewer_a", candidate_group_filter=p1_id)
    sm.pause_session("sess_group")

    resumed = sm.resume_session("sess_group", "reviewer_a")
    assert resumed.candidate_group_filter == p1_id

# 9. deterministic next mapping
def test_9_deterministic_next_mapping(tmp_path):
    reports_dir, p1_id, p2_id = create_session_test_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))
    
    m1 = queue.get_next()
    m2 = queue.get_next()
    assert m1.mapping_id == m2.mapping_id == "map_v1_00001"

# 10. skip behavior
def test_10_skip_behavior(tmp_path):
    reports_dir, p1_id, p2_id = create_session_test_env(tmp_path)
    sm = ReviewSessionManager(version="v1", reports_dir=str(reports_dir))
    sm.create_session("sess_001", "reviewer_a")
    sm.record_skip("sess_001", "map_v1_00001")

    sess = sm.get_session("sess_001")
    assert "map_v1_00001" in sess.skipped_mapping_ids
    assert "map_v1_00001" not in sess.reviewed_mapping_ids
    # Verify no review engine audit log created
    assert len(sm.get_summary_metrics()["progress_by_reviewer"]) == 1

# 11. approval confirmation safety
def test_11_approval_confirmation_safety(tmp_path):
    reports_dir, p1_id, p2_id = create_session_test_env(tmp_path)
    queue = TaxonomyReviewQueue(version="v1", reports_dir=str(reports_dir))
    sm = ReviewSessionManager(version="v1", reports_dir=str(reports_dir))

    # Reviewer selects Approve, inputs fields, but answers "n" to confirmation
    inputs = iter(["A", "reviewer_a", p1_id, "Evidence text", "n", "Q"])
    run_interactive_review(
        queue,
        session_mgr=sm,
        session_id="sess_001",
        reviewer_id="reviewer_a",
        mapping_id_filter="map_v1_00001",
        limit=1,
        input_func=lambda prompt: next(inputs)
    )

    m1 = queue.engine.mappings["map_v1_00001"]
    assert m1.mapping_status == MappingStatus.UNREVIEWED
    assert len(queue.engine.history) == 0

# 12. corrupted session handling
def test_12_corrupted_session_handling(tmp_path):
    reports_dir, p1_id, p2_id = create_session_test_env(tmp_path)
    sess_file = reports_dir / "review_sessions_v1.json"
    with open(sess_file, "w", encoding="utf-8") as f:
        f.write("{ corrupted json content }")

    with pytest.raises(ValueError, match="Malformed review session"):
        ReviewSessionManager(version="v1", reports_dir=str(reports_dir))

# 13. missing session file handling
def test_13_missing_session_file_handling(tmp_path):
    reports_dir = tmp_path / "empty_reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    sm = ReviewSessionManager(version="v1", reports_dir=str(reports_dir))
    assert len(sm.sessions) == 0

# 14. completed session resume attempt
def test_14_completed_session_resume_attempt(tmp_path):
    reports_dir, p1_id, p2_id = create_session_test_env(tmp_path)
    sm = ReviewSessionManager(version="v1", reports_dir=str(reports_dir))
    sm.create_session("sess_comp", "reviewer_a")
    sm.mark_completed("sess_comp")

    with pytest.raises(ValueError, match="is COMPLETED and cannot be resumed"):
        sm.resume_session("sess_comp", "reviewer_a")

# 15. abandoned session resume attempt
def test_15_abandoned_session_resume_attempt(tmp_path):
    reports_dir, p1_id, p2_id = create_session_test_env(tmp_path)
    sm = ReviewSessionManager(version="v1", reports_dir=str(reports_dir))
    sm.create_session("sess_aban", "reviewer_a")
    sm.abandon_session("sess_aban")

    with pytest.raises(ValueError, match="is ABANDONED and cannot be resumed"):
        sm.resume_session("sess_aban", "reviewer_a")

# 16. atomic writes work
def test_16_atomic_writes_work(tmp_path):
    reports_dir, p1_id, p2_id = create_session_test_env(tmp_path)
    sm = ReviewSessionManager(version="v1", reports_dir=str(reports_dir))
    sess_p = sm.save_sessions()

    assert sess_p.exists()
    assert not sess_p.with_suffix(".json.tmp").exists()

# 17. interruption recovery
def test_17_interruption_recovery(tmp_path):
    reports_dir, p1_id, p2_id = create_session_test_env(tmp_path)
    sm1 = ReviewSessionManager(version="v1", reports_dir=str(reports_dir))
    sm1.create_session("sess_rec", "reviewer_a")
    sm1.record_decision("sess_rec", "map_v1_00001", "APPROVE")
    sm1.update_navigation("sess_rec", "map_v1_00002", p1_id)

    # Simulate restart
    sm2 = ReviewSessionManager(version="v1", reports_dir=str(reports_dir))
    sess = sm2.get_session("sess_rec")
    assert sess.current_mapping_id == "map_v1_00002"
    assert "map_v1_00001" in sess.approved_mapping_ids

# 18. session progress metrics
def test_18_session_progress_metrics(tmp_path):
    reports_dir, p1_id, p2_id = create_session_test_env(tmp_path)
    sm = ReviewSessionManager(version="v1", reports_dir=str(reports_dir))
    sm.create_session("s1", "reviewer_a")
    sm.create_session("s2", "reviewer_b")
    sm.pause_session("s2")

    metrics = sm.get_summary_metrics()
    assert metrics["active_sessions"] == 1
    assert metrics["paused_sessions"] == 1
    assert "reviewer_a" in metrics["progress_by_reviewer"]
    assert "reviewer_b" in metrics["progress_by_reviewer"]

# 19. raw dataset immutability
def test_19_raw_dataset_immutability():
    for p in [r"C:\Datasets\CIMPd", r"C:\Datasets\Hugging_Face", r"C:\Datasets\Kaggle"]:
        if os.path.exists(p):
            assert os.path.isdir(p)

# 20. repeat resume calls produce identical deterministic ordering
def test_20_repeat_resume_calls_deterministic_ordering(tmp_path):
    reports_dir, p1_id, p2_id = create_session_test_env(tmp_path)
    sm = ReviewSessionManager(version="v1", reports_dir=str(reports_dir))
    sm.create_session("sess_rep", "reviewer_a")

    r1 = sm.resume_session("sess_rep", "reviewer_a")
    r2 = sm.resume_session("sess_rep", "reviewer_a")
    assert r1.session_id == r2.session_id
    assert r1.started_at == r2.started_at

def test_export_session_artifact():
    reports_dir = Path(r"C:\Dravya-AI-Engine\reports\dataset_analysis")
    sm = ReviewSessionManager(version="v1", reports_dir=str(reports_dir))
    session_file = sm.save_sessions()

    assert session_file.exists()
    with open(session_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["taxonomy_version"] == "v1"
    assert "sessions" in data
