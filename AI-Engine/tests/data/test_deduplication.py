import os
import pytest
import tempfile
import hashlib
from src.data.deduplication import ExactDuplicateDetector, compute_file_sha256

def test_identical_and_different_files(tmp_path):
    # Create two identical files and one different file
    content1 = b"Identical image binary content payload 12345"
    content2 = b"Different image binary content payload 67890"

    file_a = tmp_path / "img_a.jpg"
    file_b = tmp_path / "img_b.jpg"
    file_c = tmp_path / "img_c.jpg"

    file_a.write_bytes(content1)
    file_b.write_bytes(content1)
    file_c.write_bytes(content2)

    hash_a = compute_file_sha256(str(file_a))
    hash_b = compute_file_sha256(str(file_b))
    hash_c = compute_file_sha256(str(file_c))

    # 1. Identical files produce the same hash
    assert hash_a == hash_b
    # 2. Different files produce different hashes
    assert hash_a != hash_c

def test_duplicate_grouping_within_and_cross_dataset(tmp_path):
    # Setup mock dataset structure:
    # ds1_root/
    #   class_1/img1.jpg (content_x)
    #   class_1/img2.jpg (content_x) -> within-dataset duplicate in ds1
    # ds2_root/
    #   class_2/img3.jpg (content_x) -> cross-dataset duplicate with ds1
    #   class_2/img4.jpg (content_y) -> unique image

    ds1_path = tmp_path / "ds1"
    ds2_path = tmp_path / "ds2"

    (ds1_path / "class_1").mkdir(parents=True)
    (ds2_path / "class_2").mkdir(parents=True)

    content_x = b"Shared image binary payload X"
    content_y = b"Unique image binary payload Y"

    f1 = ds1_path / "class_1" / "img1.jpg"
    f2 = ds1_path / "class_1" / "img2.jpg"
    f3 = ds2_path / "class_2" / "img3.jpg"
    f4 = ds2_path / "class_2" / "img4.jpg"

    f1.write_bytes(content_x)
    f2.write_bytes(content_x)
    f3.write_bytes(content_x)
    f4.write_bytes(content_y)

    dataset_dict = {
        "ds1": str(ds1_path),
        "ds2": str(ds2_path)
    }

    detector = ExactDuplicateDetector(dataset_dict)
    res = detector.scan()

    # 3. Duplicate grouping works
    assert res["total_images_scanned"] == 4
    assert res["unique_hashes"] == 2
    assert res["duplicate_groups_count"] == 1
    assert res["total_duplicate_files"] == 3

    group = res["duplicate_groups"][0]
    assert group["file_count"] == 3
    # 4. Cross-dataset duplicates correctly identified
    assert group["is_cross_dataset"] is True
    assert set(group["datasets_involved"]) == {"ds1", "ds2"}

def test_within_dataset_duplicate_only(tmp_path):
    ds_path = tmp_path / "ds_single"
    (ds_path / "class_a").mkdir(parents=True)

    content_z = b"Single dataset duplicate payload Z"
    (ds_path / "class_a" / "img1.jpg").write_bytes(content_z)
    (ds_path / "class_a" / "img2.jpg").write_bytes(content_z)

    detector = ExactDuplicateDetector({"ds_single": str(ds_path)})
    res = detector.scan()

    assert res["duplicate_groups_count"] == 1
    # 5. Within-dataset duplicate correctly identified
    assert res["within_dataset_duplicate_groups_count"] == 1
    assert res["cross_dataset_duplicate_groups_count"] == 0
    group = res["duplicate_groups"][0]
    assert group["is_cross_dataset"] is False

def test_missing_path_handling():
    detector = ExactDuplicateDetector({"invalid": r"C:\Path\NonExistent\12345"})
    # 6. Missing paths are handled safely with FileNotFoundError
    with pytest.raises(FileNotFoundError):
        detector.scan()

def test_paths_and_files_remain_unchanged(tmp_path):
    ds_path = tmp_path / "ds_check"
    (ds_path / "class_x").mkdir(parents=True)
    img_file = ds_path / "class_x" / "test.png"
    img_content = b"Binary test PNG data"
    img_file.write_bytes(img_content)

    detector = ExactDuplicateDetector({"ds_check": str(ds_path)})
    res = detector.scan()

    # 7. Original dataset paths and files remain completely unchanged
    assert img_file.exists()
    assert img_file.read_bytes() == img_content

def test_chunked_streaming_hashing(tmp_path):
    # 8. Large-file hashing uses chunked reading
    large_file = tmp_path / "large_image.bmp"
    # Write 300KB file
    data = b"X" * (300 * 1024)
    large_file.write_bytes(data)

    # Compute hash with small 64KB chunk size
    hash_chunked = compute_file_sha256(str(large_file), chunk_size=65536)
    hash_expected = hashlib.sha256(data).hexdigest()

    assert hash_chunked == hash_expected
