import re
import hashlib
from enum import Enum
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

class MappingStatus(str, Enum):
    UNREVIEWED = "UNREVIEWED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

def generate_canonical_plant_id(name_str: str) -> str:
    """
    Generates a 100% deterministic, stable canonical plant ID from a plant name.
    Uses normalized slug and deterministic SHA-256 hash suffix.
    Example: 'Saraca asoca' -> 'PLANT-SARACA-ASOCA-4B8F7A'
    """
    if not name_str or not name_str.strip():
        raise ValueError("Plant name string cannot be empty for canonical ID generation.")
    
    clean_str = name_str.strip().lower()
    clean_str = re.sub(r'[\s_\-\.\,]+', ' ', clean_str).strip()
    
    # Generate 6-char hex hash digest for deterministic uniqueness
    hash_digest = hashlib.sha256(clean_str.encode('utf-8')).hexdigest()[:6].upper()
    
    # Convert name to uppercase slug
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', clean_str).strip('-').upper()
    if not slug:
        slug = "UNKNOWN"
        
    return f"PLANT-{slug}-{hash_digest}"

@dataclass
class CanonicalPlant:
    canonical_plant_id: str
    canonical_name: str
    common_name: Optional[str] = None
    scientific_name: Optional[str] = None
    aliases: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    taxonomy_version: str = "v1"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class TaxonomyMapping:
    mapping_id: str
    source_dataset: str
    original_class_name: str
    normalized_name: str
    candidate_canonical_plant_id: Optional[str] = None
    approved_canonical_plant_id: Optional[str] = None
    health_condition: str = "Unknown"  # Healthy, Unhealthy, Unknown
    confidence: str = "LOW"            # HIGH, MEDIUM, LOW
    mapping_status: MappingStatus = MappingStatus.UNREVIEWED
    match_reason: Optional[str] = None
    evidence: Optional[str] = None
    reviewer: Optional[str] = None
    reviewed_at: Optional[str] = None
    mapping_version: str = "v1"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["mapping_status"] = self.mapping_status.value if isinstance(self.mapping_status, MappingStatus) else str(self.mapping_status)
        return d
