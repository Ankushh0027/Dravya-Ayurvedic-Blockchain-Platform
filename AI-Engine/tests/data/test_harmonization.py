import os
import pytest
from src.data.harmonization import ClassHarmonizationAnalyzer, parse_class_name

def test_normalization_preserves_original_names():
    orig_cimpd = "Ashok.H"
    parsed_cimpd = parse_class_name("CIMPd", orig_cimpd)
    assert parsed_cimpd["original_class_name"] == "Ashok.H"
    assert parsed_cimpd["normalized_common"] == "ashok"

    orig_hf = "Aloevera-Aloe barbadensis"
    parsed_hf = parse_class_name("Hugging_Face", orig_hf)
    assert parsed_hf["original_class_name"] == "Aloevera-Aloe barbadensis"
    assert parsed_hf["normalized_common"] == "aloevera"
    assert parsed_hf["normalized_scientific"] == "aloe barbadensis"

def test_cimpd_health_condition_extraction():
    parsed_h = parse_class_name("CIMPd", "Bel.H")
    assert parsed_h["health_condition"] == "Healthy"
    assert parsed_h["plant_name_candidate"] == "Bel"

    parsed_u = parse_class_name("CIMPd", "Bel.U")
    assert parsed_u["health_condition"] == "Unhealthy"
    assert parsed_u["plant_name_candidate"] == "Bel"

    parsed_comma = parse_class_name("CIMPd", "Makoy,U")
    assert parsed_comma["health_condition"] == "Unhealthy"
    assert parsed_comma["plant_name_candidate"] == "Makoy"

def test_candidate_detection_and_no_automatic_merge():
    mock_inventories = [
        {
            "dataset_id": "CIMPd",
            "root_path": r"C:\Datasets\CIMPd",
            "image_count_per_class": {
                "Ashok.H": 100,
                "Ashok.U": 50
            }
        },
        {
            "dataset_id": "Hugging_Face",
            "root_path": r"C:\Datasets\Hugging_Face",
            "image_count_per_class": {
                "Ashoka-Saraca asoca": 200
            }
        },
        {
            "dataset_id": "Kaggle",
            "root_path": r"C:\Datasets\Kaggle",
            "image_count_per_class": {
                "Medicinal Leaf dataset\\Ashoka": 150
            }
        }
    ]

    analyzer = ClassHarmonizationAnalyzer(mock_inventories)
    results = analyzer.analyze()

    assert results["total_classes_analyzed"] == 4
    assert results["cimpd_health_classes_count"] == 2

    # Check that canonical_plant_id remains None (no automatic merge)
    for entry in results["class_entries"]:
        assert entry["canonical_plant_id"] is None
        assert entry["mapping_status"] == "UNREVIEWED"
        assert entry["original_class_name"] in ["Ashok.H", "Ashok.U", "Ashoka-Saraca asoca", "Medicinal Leaf dataset\\Ashoka"]

    # Candidate matches present
    matches = results["candidate_matches"]
    assert len(matches) > 0
    reasons = set(m["candidate_reason"] for m in matches)
    assert any(r in reasons for r in ["CIMPd_health_suffix_match", "possible_name_similarity", "exact_normalized_name"])

def test_scientific_name_candidate_detection():
    mock_inventories = [
        {
            "dataset_id": "ds1",
            "root_path": "/ds1",
            "image_count_per_class": {"Amla-Phyllanthus emlica": 10}
        },
        {
            "dataset_id": "ds2",
            "root_path": "/ds2",
            "image_count_per_class": {"Phyllanthus emlica": 20}
        }
    ]

    analyzer = ClassHarmonizationAnalyzer(mock_inventories)
    results = analyzer.analyze()

    matches = results["candidate_matches"]
    assert len(matches) == 1
    assert matches[0]["candidate_reason"] in ["scientific_name_match", "exact_normalized_name", "possible_name_similarity"]

def test_unknown_and_missing_names_safety():
    parsed = parse_class_name("ds_unknown", "")
    assert parsed["original_class_name"] == ""
    assert parsed["normalized_common"] == ""

    parsed_none = parse_class_name("ds_unknown", "UnknownClassFolder")
    assert parsed_none["health_condition"] == "Unknown"
    assert parsed_none["scientific_name_candidate"] is None
