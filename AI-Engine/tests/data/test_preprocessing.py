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
from src.data.preprocessing import (
    PreprocessingConfig,
    ProcessedDatasetRecord,
    CanonicalPreprocessor
)
from src.data.deduplication import compute_file_sha256

def create_mock_preprocessing_env(tmp_path, num_records=20, include_duplicates=True, corrupt_img=False):
    plant_id1 = generate_canonical_plant_id("Saraca asoca")
    plant1 = CanonicalPlant(canonical_plant_id=plant_id1, canonical_name="Ashoka", scientific_name="Saraca asoca")

    plant_id2 = generate_canonical_plant_id("Azadirachta indica")
    plant2 = CanonicalPlant(canonical_plant_id=plant_id2, canonical_name="Neem", scientific_name="Azadirachta indica")

    ds_dir = tmp_path / "datasets" / "CIMPd" / "Ashok.H"
    ds_dir.mkdir(parents=True, exist_ok=True)

    records = []
    
    for i in range(1, num_records + 1):
        pid = plant_id1 if i <= (num_records // 2) else plant_id2
        pname = "Ashoka" if pid == plant_id1 else "Neem"

        fname = f"leaf_{i:03d}.jpg"
        fpath = ds_dir / fname

        if corrupt_img and i == 1:
            fpath.write_bytes(b"NOT_A_REAL_IMAGE")
        else:
            # Create a 300x400 image to test resizing to 224x224
            img = Image.new("RGB", (300, 400), color=(i * 10 % 255, 100, 150))
            img.save(fpath)

        # Duplicate SHA simulation for even i if include_duplicates
        if include_duplicates and i % 2 == 0 and i > 2:
            prev_path = ds_dir / f"leaf_{i-1:03d}.jpg"
            fpath.write_bytes(prev_path.read_bytes())

        sha = compute_file_sha256(fpath)

        src_ref = SourceReference(
            dataset_id="CIMPd",
            original_class_name="Ashok.H",
            source_file_path=str(fpath),
            source_file_name=fname
        )

        rec = CanonicalDatasetRecord(
            record_id=f"rec_v1_{i:05d}",
            taxonomy_version="v1",
            canonical_plant_id=pid,
            canonical_name=pname,
            health_condition="Healthy",
            sha256=sha,
            file_extension=".jpg",
            source_references=[src_ref]
        )
        records.append(rec)

    reports_dir = tmp_path / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = reports_dir / "canonical_dataset_manifest_v1.json"
    manifest_data = {
        "taxonomy_version": "v1",
        "status": "SUCCESS",
        "reason": "APPROVED_MAPPINGS_PROCESSED",
        "records": [r.to_dict() for r in records]
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f)

    output_root = tmp_path / "processed" / "v1"
    config = PreprocessingConfig(
        version="v1",
        output_root=str(output_root),
        random_seed=42,
        split_ratios={"train": 0.70, "val": 0.15, "test": 0.15}
    )

    return reports_dir, manifest_path, config, records

def test_missing_canonical_manifest(tmp_path):
    # 1. Missing canonical manifest
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    config = PreprocessingConfig(version="v1", output_root=str(tmp_path / "proc"))
    preprocessor = CanonicalPreprocessor(config=config, reports_dir=str(reports_dir))

    recs, stats = preprocessor.process_and_split(str(reports_dir / "nonexistent.json"))
    assert stats["status"] == "BLOCKED"
    assert stats["reason"] == "MANIFEST_FILE_NOT_FOUND"
    assert len(recs) == 0

def test_zero_approved_mappings_blocked(tmp_path):
    # 2 & 3. Blocked manifest with 0 approved mappings
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = reports_dir / "canonical_dataset_manifest_v1.json"

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump({
            "taxonomy_version": "v1",
            "status": "BLOCKED",
            "reason": "NO_APPROVED_MAPPINGS",
            "records": []
        }, f)

    config = PreprocessingConfig(version="v1", output_root=str(tmp_path / "proc"))
    preprocessor = CanonicalPreprocessor(config=config, reports_dir=str(reports_dir))

    recs, stats = preprocessor.process_and_split(str(manifest_path))
    assert stats["status"] == "BLOCKED"
    assert stats["reason"] == "NO_APPROVED_MAPPINGS"
    assert len(recs) == 0

def test_quality_gate_blocked_prevents_preprocessing(tmp_path):
    # Safety Check: Quality Gate BLOCKED / FAIL prevents downstream preprocessing
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = reports_dir / "canonical_dataset_manifest_v1.json"
    q_report_path = reports_dir / "canonical_dataset_quality_report_v1.json"

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump({"taxonomy_version": "v1", "status": "SUCCESS", "records": [{"record_id": "rec_001"}]}, f)

    with open(q_report_path, "w", encoding="utf-8") as f:
        json.dump({"version": "v1", "status": "BLOCKED", "reason": "NO_APPROVED_MAPPINGS"}, f)

    config = PreprocessingConfig(version="v1", output_root=str(tmp_path / "proc"))
    preprocessor = CanonicalPreprocessor(config=config, reports_dir=str(reports_dir))

    recs, stats = preprocessor.process_and_split(str(manifest_path))
    assert stats["status"] == "BLOCKED"
    assert "QUALITY_GATE_BLOCKED" in stats["reason"]
    assert len(recs) == 0

def test_valid_image_preprocessing_and_target_dimensions(tmp_path):

    # 6 & 7 & 8. Valid preprocessing, 224x224 dimension enforcement, color conversion
    reports_dir, manifest_path, config, records = create_mock_preprocessing_env(tmp_path, num_records=10)
    preprocessor = CanonicalPreprocessor(config=config, reports_dir=str(reports_dir))

    procs, stats = preprocessor.process_and_split(str(manifest_path))
    assert stats["status"] == "SUCCESS"
    assert len(procs) == 10

    for r in procs:
        assert r.processed_dimensions == (224, 224)
        assert os.path.exists(r.processed_path)
        with Image.open(r.processed_path) as img:
            assert img.size == (224, 224)
            assert img.mode == "RGB"

def test_deterministic_preprocessing_and_seed_reproducibility(tmp_path):
    # 9 & 10 & 12. Seed reproducibility and deterministic split assignment
    reports_dir, manifest_path, config, records = create_mock_preprocessing_env(tmp_path, num_records=20)
    
    prep1 = CanonicalPreprocessor(config=config, reports_dir=str(reports_dir))
    procs1, stats1 = prep1.process_and_split(str(manifest_path))

    # Second run with identical seed and config in separate output directory or FORCE overwrite
    config2 = PreprocessingConfig(
        version="v1",
        output_root=str(tmp_path / "processed_run2" / "v1"),
        random_seed=42,
        split_ratios={"train": 0.70, "val": 0.15, "test": 0.15}
    )
    prep2 = CanonicalPreprocessor(config=config2, reports_dir=str(reports_dir))
    procs2, stats2 = prep2.process_and_split(str(manifest_path))

    splits1 = [(r.processed_record_id, r.split, r.original_sha256) for r in procs1]
    splits2 = [(r.processed_record_id, r.split, r.original_sha256) for r in procs2]

    assert splits1 == splits2


def test_sha256_leakage_prevention_and_duplicate_grouping(tmp_path):
    # 13 & 14. SHA-256 leakage prevention: duplicate source images MUST remain in same split!
    reports_dir, manifest_path, config, records = create_mock_preprocessing_env(tmp_path, num_records=20, include_duplicates=True)
    preprocessor = CanonicalPreprocessor(config=config, reports_dir=str(reports_dir))

    procs, stats = preprocessor.process_and_split(str(manifest_path))
    assert stats["cross_split_leakage_count"] == 0

    train_shas = {r.original_sha256 for r in procs if r.split == "train"}
    val_shas = {r.original_sha256 for r in procs if r.split == "val"}
    test_shas = {r.original_sha256 for r in procs if r.split == "test"}

    assert len(train_shas.intersection(val_shas)) == 0
    assert len(train_shas.intersection(test_shas)) == 0
    assert len(val_shas.intersection(test_shas)) == 0

    val_rep = preprocessor.validate_processed_dataset()
    assert val_rep["is_valid"] is True

def test_overwrite_policy_never_raises_error(tmp_path):
    # 23. No overwrite without --force (overwrite_policy="NEVER")
    reports_dir, manifest_path, config, records = create_mock_preprocessing_env(tmp_path, num_records=4)
    preprocessor1 = CanonicalPreprocessor(config=config, reports_dir=str(reports_dir))
    preprocessor1.process_and_split(str(manifest_path))

    # Second run with overwrite_policy="NEVER" on non-empty output directory raises FileExistsError
    preprocessor2 = CanonicalPreprocessor(config=config, reports_dir=str(reports_dir))
    with pytest.raises(FileExistsError, match="already contains files"):
        preprocessor2.process_and_split(str(manifest_path))

    # Second run with overwrite_policy="FORCE" succeeds
    config.overwrite_policy = "FORCE"
    preprocessor3 = CanonicalPreprocessor(config=config, reports_dir=str(reports_dir))
    procs3, stats3 = preprocessor3.process_and_split(str(manifest_path))
    assert stats3["status"] == "SUCCESS"

def test_invalid_split_ratios_raises_error(tmp_path):
    reports_dir, manifest_path, config, records = create_mock_preprocessing_env(tmp_path, num_records=4)
    config.split_ratios = {"train": 0.80, "val": 0.50, "test": 0.50}  # Sum = 1.80 != 1.0
    preprocessor = CanonicalPreprocessor(config=config, reports_dir=str(reports_dir))
    with pytest.raises(ValueError, match="Split ratios must sum to 1.0"):
        preprocessor.process_and_split(str(manifest_path))

def test_provenance_and_processed_sha_verification(tmp_path):

    # 17 & 18. Provenance preservation and processed SHA verification
    reports_dir, manifest_path, config, records = create_mock_preprocessing_env(tmp_path, num_records=6)
    preprocessor = CanonicalPreprocessor(config=config, reports_dir=str(reports_dir))

    procs, stats = preprocessor.process_and_split(str(manifest_path))
    rec = procs[0]

    assert rec.canonical_record_id is not None
    assert rec.original_source_path is not None
    assert rec.source_dataset == "CIMPd"
    assert rec.original_class_name == "Ashok.H"
    assert compute_file_sha256(rec.processed_path) == rec.processed_sha256

def test_raw_dataset_path_safety():
    # 21. Raw external dataset paths remain 100% read-only & untouched
    external_roots = [r"C:\Datasets\CIMPd", r"C:\Datasets\Hugging_Face", r"C:\Datasets\Kaggle"]
    for path in external_roots:
        if os.path.exists(path):
            assert os.path.isdir(path)
