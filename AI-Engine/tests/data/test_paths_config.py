import os
import pytest
from pathlib import Path

from src.data.paths import (
    get_project_root,
    get_external_dataset_root,
    get_reports_dir,
    get_dataset_paths,
    load_config,
    PROJECT_ROOT,
)
from src.data.manifest import ManifestGenerator
from src.data.taxonomy_review import atomic_json_write


def test_project_root_resolution():
    root = get_project_root()
    assert isinstance(root, Path)
    assert root.exists()
    assert (root / "configs" / "config.yaml").exists()


def test_default_paths_use_pathlib_and_relative_fallbacks():
    dataset_root = get_external_dataset_root()
    reports_dir = get_reports_dir()

    assert isinstance(dataset_root, Path)
    assert isinstance(reports_dir, Path)
    assert dataset_root.is_absolute()
    assert reports_dir.is_absolute()

    paths = get_dataset_paths()
    assert "CIMPd" in paths
    assert "Hugging_Face" in paths
    assert "Kaggle" in paths
    assert isinstance(paths["CIMPd"], Path)


def test_env_var_overrides(monkeypatch, tmp_path):
    custom_dataset = tmp_path / "custom_datasets"
    custom_reports = tmp_path / "custom_reports"

    monkeypatch.setenv("DRAVYA_DATASET_ROOT", str(custom_dataset))
    monkeypatch.setenv("DRAVYA_REPORTS_DIR", str(custom_reports))

    assert get_external_dataset_root() == custom_dataset
    assert get_reports_dir() == custom_reports

    custom_paths = get_dataset_paths()
    assert custom_paths["CIMPd"] == custom_dataset / "CIMPd"


def test_automatic_directory_creation_at_runtime(tmp_path):
    target_reports = tmp_path / "nested" / "output" / "reports"
    assert not target_reports.exists()

    generator = ManifestGenerator(output_dir=target_reports)
    assert target_reports.exists()

    test_file = target_reports / "test_state.json"
    atomic_json_write(test_file, {"status": "OK"})
    assert test_file.exists()
