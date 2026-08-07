import os
import pytest
from src.data.taxonomy import (
    CanonicalPlant,
    TaxonomyMapping,
    MappingStatus,
    generate_canonical_plant_id
)
from src.data.taxonomy_validator import TaxonomyValidator
from src.data.taxonomy_manager import TaxonomyManager

def test_canonical_id_stability():
    # 1 & 11. Canonical ID generator is 100% deterministic and stable
    id1 = generate_canonical_plant_id("Saraca asoca")
    id2 = generate_canonical_plant_id("Saraca asoca")
    id3 = generate_canonical_plant_id(" Saraca   asoca  ")
    
    assert id1 == id2 == id3
    assert id1.startswith("PLANT-SARACA-ASOCA-")
    
    with pytest.raises(ValueError):
        generate_canonical_plant_id("")

def test_mapping_status_and_candidate_vs_approved_distinction():
    # 2 & 3 & 4. Candidate != Approved, Unapproved mappings must NOT have approved_canonical_plant_id
    m_unreviewed = TaxonomyMapping(
        mapping_id="map_001",
        source_dataset="CIMPd",
        original_class_name="Ashok.H",
        normalized_name="ashok",
        candidate_canonical_plant_id="PLANT-ASHOK-123456",
        approved_canonical_plant_id=None,
        health_condition="Healthy",
        mapping_status=MappingStatus.UNREVIEWED
    )
    
    assert m_unreviewed.candidate_canonical_plant_id == "PLANT-ASHOK-123456"
    assert m_unreviewed.approved_canonical_plant_id is None
    assert m_unreviewed.mapping_status == MappingStatus.UNREVIEWED
    
    # Validation passes for valid unapproved mapping
    errors = TaxonomyValidator.validate_taxonomy_mappings([m_unreviewed])
    assert len(errors) == 0

    # Validation fails if unapproved mapping has an approved_canonical_plant_id
    invalid_m = TaxonomyMapping(
        mapping_id="map_002",
        source_dataset="CIMPd",
        original_class_name="Ashok.H",
        normalized_name="ashok",
        candidate_canonical_plant_id="PLANT-ASHOK-123456",
        approved_canonical_plant_id="PLANT-ASHOK-123456",
        health_condition="Healthy",
        mapping_status=MappingStatus.UNREVIEWED
    )
    errors_invalid = TaxonomyValidator.validate_taxonomy_mappings([invalid_m])
    assert len(errors_invalid) == 1
    assert "cannot have approved_canonical_plant_id" in errors_invalid[0]

def test_no_automatic_merges_and_health_condition_separation(tmp_path):
    # Setup mock harmonization JSON
    mock_json_content = {
        "scan_timestamp": "2026-08-02T12:00:00Z",
        "datasets": ["CIMPd"],
        "total_classes_analyzed": 3,
        "class_entries": [
            {
                "source_dataset": "CIMPd",
                "original_class_name": "Tulsi.H",
                "image_count": 100,
                "source_path": "/CIMPd/Tulsi.H",
                "canonical_plant_id": None,
                "canonical_common_name": "Tulsi",
                "canonical_scientific_name": None,
                "health_condition": "Healthy",
                "candidate_matches": []
            },
            {
                "source_dataset": "CIMPd",
                "original_class_name": "Tulsi.U",
                "image_count": 50,
                "source_path": "/CIMPd/Tulsi.U",
                "canonical_plant_id": None,
                "canonical_common_name": "Tulsi",
                "canonical_scientific_name": None,
                "health_condition": "Unhealthy",
                "candidate_matches": []
            },
            {
                "source_dataset": "CIMPd",
                "original_class_name": "leafs",
                "image_count": 20,
                "source_path": "/CIMPd/leafs",
                "canonical_plant_id": None,
                "canonical_common_name": "leafs",
                "canonical_scientific_name": None,
                "health_condition": "Unknown",
                "candidate_matches": []
            }
        ]
    }
    
    json_path = tmp_path / "class_harmonization_analysis.json"
    with open(json_path, "w", encoding="utf-8") as f:
        import json
        json.dump(mock_json_content, f)

    mgr = TaxonomyManager(version="v1", reports_dir=str(tmp_path))
    plants, mappings = mgr.build_from_harmonization_json(str(json_path))

    assert len(mappings) == 3

    # 4 & 5. Original class names preserved, approved_canonical_plant_id is None (no auto-merge)
    for m in mappings:
        assert m.approved_canonical_plant_id is None
        assert m.mapping_status in (MappingStatus.UNREVIEWED, MappingStatus.NEEDS_REVIEW)
        assert m.original_class_name in ["Tulsi.H", "Tulsi.U", "leafs"]

    # 6. Health condition separated from plant identity
    tulsi_h = next(m for m in mappings if m.original_class_name == "Tulsi.H")
    tulsi_u = next(m for m in mappings if m.original_class_name == "Tulsi.U")
    leafs = next(m for m in mappings if m.original_class_name == "leafs")

    assert tulsi_h.health_condition == "Healthy"
    assert tulsi_u.health_condition == "Unhealthy"
    # 10. Unknown health condition preserved
    assert leafs.health_condition == "Unknown"

    # Both Tulsi.H and Tulsi.U point to candidate plant identity 'PLANT-TULSI-...'
    assert tulsi_h.candidate_canonical_plant_id == tulsi_u.candidate_canonical_plant_id

def test_duplicate_approved_mapping_prevention():
    # 7. Validation prevents duplicate APPROVED mappings for same source class
    m1 = TaxonomyMapping(
        mapping_id="map_001",
        source_dataset="CIMPd",
        original_class_name="Ashok.H",
        normalized_name="ashok",
        approved_canonical_plant_id="PLANT-ASHOK-123456",
        health_condition="Healthy",
        mapping_status=MappingStatus.APPROVED
    )
    m2 = TaxonomyMapping(
        mapping_id="map_002",
        source_dataset="CIMPd",
        original_class_name="Ashok.H",
        normalized_name="ashok",
        approved_canonical_plant_id="PLANT-ASHOK-999999",
        health_condition="Healthy",
        mapping_status=MappingStatus.APPROVED
    )
    
    errors = TaxonomyValidator.validate_taxonomy_mappings([m1, m2])
    assert len(errors) == 1
    assert "Duplicate APPROVED mapping" in errors[0]

def test_nonexistent_canonical_plant_id_prevention():
    # 10. APPROVED mapping pointing to nonexistent canonical plant is caught by validator
    plant = CanonicalPlant(
        canonical_plant_id="PLANT-EXISTENT-123456",
        canonical_name="Existent Plant"
    )
    mapping = TaxonomyMapping(
        mapping_id="map_999",
        source_dataset="CIMPd",
        original_class_name="Ashok.H",
        normalized_name="ashok",
        approved_canonical_plant_id="PLANT-NONEXISTENT-999999",
        health_condition="Healthy",
        mapping_status=MappingStatus.APPROVED
    )
    val_res = TaxonomyValidator.validate_full_system([plant], [mapping])
    assert val_res["is_valid"] is False
    assert any("points to nonexistent canonical plant" in err for err in val_res["errors"])

def test_versioning_and_future_dataset_compatibility(tmp_path):

    # 8 & 9. Supports arbitrary taxonomy version strings and future dataset source names
    plant = CanonicalPlant(
        canonical_plant_id=generate_canonical_plant_id("Future Plant Species"),
        canonical_name="Future Plant Species",
        taxonomy_version="v2_experimental"
    )
    
    mapping = TaxonomyMapping(
        mapping_id="map_v2_00001",
        source_dataset="Future_Dataset_2027",
        original_class_name="Species_A",
        normalized_name="species a",
        candidate_canonical_plant_id=plant.canonical_plant_id,
        mapping_status=MappingStatus.UNREVIEWED,
        mapping_version="v2_experimental"
    )

    val_res = TaxonomyValidator.validate_full_system([plant], [mapping])
    assert val_res["is_valid"] is True
    assert val_res["total_canonical_plants"] == 1
    assert val_res["total_mappings"] == 1
