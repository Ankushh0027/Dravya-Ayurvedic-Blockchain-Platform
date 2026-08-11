from typing import List, Dict, Any, Tuple, Optional, Set

from src.data.taxonomy import CanonicalPlant, TaxonomyMapping, MappingStatus

class TaxonomyValidator:
    """
    Validates taxonomy integrity, mapping status rules, and review constraints.
    """

    @staticmethod
    def validate_canonical_plants(plants: List[CanonicalPlant]) -> List[str]:
        """
        Validates that canonical plant IDs are unique and well-formed.
        """
        errors = []
        seen_ids: Dict[str, CanonicalPlant] = {}

        for plant in plants:
            pid = plant.canonical_plant_id
            if not pid:
                errors.append(f"CanonicalPlant missing canonical_plant_id: {plant}")
                continue

            if pid in seen_ids:
                prev = seen_ids[pid]
                if prev.canonical_name != plant.canonical_name:
                    errors.append(f"Duplicate canonical_plant_id '{pid}' with conflicting names: '{prev.canonical_name}' vs '{plant.canonical_name}'")
            else:
                seen_ids[pid] = plant

        return errors

    @staticmethod
    def validate_taxonomy_mappings(mappings: List[TaxonomyMapping], valid_plant_ids: Optional[set] = None) -> List[str]:
        """
        Validates mapping status rules and constraints.
        """
        errors = []
        seen_approved: Dict[Tuple[str, str], str] = {}

        for m in mappings:
            # Check original_class_name preservation
            if not m.original_class_name:
                errors.append(f"Mapping missing original_class_name: {m}")

            # Check status rules
            status = m.mapping_status if isinstance(m.mapping_status, MappingStatus) else MappingStatus(m.mapping_status)

            if status == MappingStatus.APPROVED:
                if not m.approved_canonical_plant_id:
                    errors.append(f"APPROVED mapping '{m.source_dataset}:{m.original_class_name}' lacks approved_canonical_plant_id.")
                elif valid_plant_ids is not None and m.approved_canonical_plant_id not in valid_plant_ids:
                    errors.append(f"APPROVED mapping '{m.source_dataset}:{m.original_class_name}' points to nonexistent canonical plant '{m.approved_canonical_plant_id}'.")

                key = (m.source_dataset, m.original_class_name)
                if key in seen_approved:
                    errors.append(f"Duplicate APPROVED mapping for '{key[0]}:{key[1]}'")
                else:
                    seen_approved[key] = m.approved_canonical_plant_id
            else:
                # UNREVIEWED, NEEDS_REVIEW, REJECTED must NOT have approved_canonical_plant_id
                if m.approved_canonical_plant_id is not None:
                    errors.append(f"Unapproved mapping '{m.source_dataset}:{m.original_class_name}' with status '{status.value}' cannot have approved_canonical_plant_id.")

            # Validate health condition is separate from plant identity
            if m.health_condition not in ("Healthy", "Unhealthy", "Unknown"):
                errors.append(f"Invalid health_condition '{m.health_condition}' for '{m.source_dataset}:{m.original_class_name}'")

        return errors

    @classmethod
    def validate_full_system(cls, plants: List[CanonicalPlant], mappings: List[TaxonomyMapping]) -> Dict[str, Any]:
        """
        Performs full validation check and returns structured validation report.
        """
        plant_errors = cls.validate_canonical_plants(plants)
        valid_plant_ids = {p.canonical_plant_id for p in plants if p.canonical_plant_id}
        mapping_errors = cls.validate_taxonomy_mappings(mappings, valid_plant_ids=valid_plant_ids)
        all_errors = plant_errors + mapping_errors


        approved_count = sum(1 for m in mappings if (m.mapping_status if isinstance(m.mapping_status, MappingStatus) else MappingStatus(m.mapping_status)) == MappingStatus.APPROVED)
        unreviewed_count = sum(1 for m in mappings if (m.mapping_status if isinstance(m.mapping_status, MappingStatus) else MappingStatus(m.mapping_status)) == MappingStatus.UNREVIEWED)
        needs_review_count = sum(1 for m in mappings if (m.mapping_status if isinstance(m.mapping_status, MappingStatus) else MappingStatus(m.mapping_status)) == MappingStatus.NEEDS_REVIEW)
        rejected_count = sum(1 for m in mappings if (m.mapping_status if isinstance(m.mapping_status, MappingStatus) else MappingStatus(m.mapping_status)) == MappingStatus.REJECTED)

        return {
            "is_valid": len(all_errors) == 0,
            "total_canonical_plants": len(plants),
            "total_mappings": len(mappings),
            "approved_mappings_count": approved_count,
            "unreviewed_mappings_count": unreviewed_count,
            "needs_review_mappings_count": needs_review_count,
            "rejected_mappings_count": rejected_count,
            "errors_count": len(all_errors),
            "errors": all_errors
        }
