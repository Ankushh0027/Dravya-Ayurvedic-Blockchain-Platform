import os
import pytest
import tempfile
import json
from src.data import InventoryScanner, ManifestGenerator

def test_missing_dataset_path():
    scanner = InventoryScanner("non_existent", r"C:\Path\That\Does\Not\Exist\12345")
    with pytest.raises(FileNotFoundError):
        scanner.scan()

def test_image_extension_and_nested_structure(tmp_path):
    # Setup mock dataset structure:
    # tmp_path/
    #   class_a.H/
    #     img1.jpg
    #     img2.png
    #     notes.txt
    #   class_b.U/
    #     img3.webp
    #     archive.zip
    #   nested_collection/
    #     sub_class/
    #       img4.bmp
    #   empty_class/
    
    class_a = tmp_path / "class_a.H"
    class_a.mkdir()
    (class_a / "img1.jpg").write_text("fake img 1")
    (class_a / "img2.png").write_text("fake img 2")
    (class_a / "notes.txt").write_text("fake notes")

    class_b = tmp_path / "class_b.U"
    class_b.mkdir()
    (class_b / "img3.webp").write_text("fake img 3")
    (class_b / "archive.zip").write_text("fake zip")

    nested = tmp_path / "nested_collection" / "sub_class"
    nested.mkdir(parents=True)
    (nested / "img4.bmp").write_text("fake img 4")

    empty_dir = tmp_path / "empty_class"
    empty_dir.mkdir()

    scanner = InventoryScanner("test_ds", str(tmp_path))
    res = scanner.scan()

    assert res["dataset_id"] == "test_ds"
    assert res["total_images"] == 4
    assert res["total_files"] == 6 # 4 images + 1 txt + 1 zip

    # Extension breakdown
    exts = res["image_extensions"]
    assert exts.get(".jpg") == 1
    assert exts.get(".png") == 1
    assert exts.get(".webp") == 1
    assert exts.get(".bmp") == 1

    # Class names preserving exact folder names including .H and .U
    class_counts = res["image_count_per_class"]
    assert "class_a.H" in class_counts
    assert class_counts["class_a.H"] == 2
    assert "class_b.U" in class_counts
    assert class_counts["class_b.U"] == 1
    
    # Nested directory class key
    nested_key = os.path.join("nested_collection", "sub_class")
    assert nested_key in class_counts
    assert class_counts[nested_key] == 1

    # Empty directory detection
    assert "empty_class" in res["empty_class_directories"]

    # Non-image files and archives
    assert any("notes.txt" in f for f in res["non_image_files"])
    assert any("archive.zip" in f for f in res["archive_files"])

def test_manifest_generator(tmp_path):
    mock_inv = {
        "dataset_id": "mock_ds",
        "source": "mock_source",
        "root_path": "/mock/path",
        "total_files": 2,
        "total_images": 2,
        "image_extensions": {".jpg": 2},
        "total_apparent_classes": 1,
        "class_names": ["species_a"],
        "image_count_per_class": {"species_a": 2},
        "empty_class_directories": [],
        "non_image_files": [],
        "archive_files": [],
        "scan_timestamp": "2026-08-02T12:00:00Z"
    }

    generator = ManifestGenerator(output_dir=str(tmp_path))
    json_path = generator.export_json([mock_inv])
    csv_path = generator.export_csv([mock_inv])
    summary_text = generator.format_terminal_summary([mock_inv])

    assert os.path.exists(json_path)
    assert os.path.exists(csv_path)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert len(data["inventories"]) == 1
        assert data["inventories"][0]["dataset_id"] == "mock_ds"

    with open(csv_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "mock_ds,species_a,2" in content

    assert "DRAVYA AI DATASET INVENTORY SUMMARY" in summary_text
