"""
Deterministic and collision-resistant Batch ID generation for Dravya AI Engine.
"""
import hashlib
import re
from typing import Optional


def extract_herb_prefix(herb_name: str) -> str:
    """
    Extracts a 3-letter uppercase prefix code from a herb species name.
    Example: 'Ashwagandha' -> 'ASH', 'Tulsi' -> 'TUL', 'Aloe Vera' -> 'ALO'.
    """
    clean_name = re.sub(r"[^a-zA-Z]", "", herb_name.strip()).upper()
    if len(clean_name) >= 3:
        return clean_name[:3]
    elif len(clean_name) > 0:
        return clean_name.ljust(3, "X")
    return "HRB"


def format_harvest_date_digits(harvest_date: str) -> str:
    """
    Normalizes harvest date string into YYYYMMDD format.
    Accepts 'YYYY-MM-DD', 'YYYY/MM/DD', or 'YYYYMMDD'.
    """
    digits = re.sub(r"[^\d]", "", harvest_date.strip())
    if len(digits) == 8:
        return digits
    raise ValueError(f"Invalid harvest_date format '{harvest_date}'. Expected YYYY-MM-DD.")


def generate_batch_id(
    herb_species: str,
    farmer_id: str,
    harvest_date: str,
    quantity_kg: float,
    prefix: str = "DRAVYA",
    nonce: Optional[str] = None,
) -> str:
    """
    Generates a deterministic, collision-resistant, URL-safe Batch ID.
    Format: DRAVYA-<HERB_PREFIX>-<YYYYMMDD>-<HEX_SUFFIX_6>

    Parameters:
    -----------
    herb_species: Herb common or canonical species name.
    farmer_id: Farmer reference identifier (non-sensitive ID).
    harvest_date: Harvest date string in YYYY-MM-DD format.
    quantity_kg: Normalized quantity in kg.
    prefix: ID namespace prefix (default 'DRAVYA').
    nonce: Optional discriminator string for creating distinct batches with identical parameters.

    Returns:
    --------
    Formatted Batch ID string (e.g. 'DRAVYA-ASH-20260810-A1B2C3').
    """
    herb_code = extract_herb_prefix(herb_species)
    date_code = format_harvest_date_digits(harvest_date)

    # Compute SHA-256 digest over normalized input fields (excluding any PII)
    raw_payload = "|".join([
        herb_species.strip().lower(),
        farmer_id.strip(),
        date_code,
        f"{float(quantity_kg):.4f}",
        nonce.strip() if nonce else "",
    ]).encode("utf-8")

    digest = hashlib.sha256(raw_payload).hexdigest().upper()
    suffix = digest[:6]

    return f"{prefix}-{herb_code}-{date_code}-{suffix}"
