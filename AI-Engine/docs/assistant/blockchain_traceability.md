# Dravya — Blockchain & Traceability Architecture

## 1. Role of Blockchain in Dravya
Dravya uses a permissioned distributed ledger (Hyperledger Fabric) to provide immutable provenance and cryptographic tamper detection across the Ayurvedic supply chain. Blockchain guarantees that once a batch inspection, quality test, or custody transfer is recorded, it cannot be silently edited or deleted by any single party.

## 2. Traceability Payload & Deterministic Batch IDs
- **Deterministic Batch ID**: Unique format `DRAVYA-{HERB_CODE}-{YYYYMMDD}-{HASH}` (e.g. `DRAVYA-ASH-20260810-346DA7`) derived deterministically from species, farmer, harvest date, and quantity.
- **Traceability Record**: Contains:
  - Batch metadata & botanical taxonomy (common, canonical, scientific names).
  - Origin identity (farmer ID, farmer name).
  - Quantity metrics (normalized kg value and original units).
  - AI identification snapshot (predicted species, confidence score, model version).
  - Verification status (`AI_CONFIRMED`, `AI_PREDICTED`, `FIELD_VERIFIED`, `QUALITY_APPROVED`).
  - Canonical timestamps (harvest date, creation timestamp).
  - `payload_hash`: Cryptographic 64-character SHA-256 integrity hash of the canonical JSON payload.

## 3. Dual-Layer Integrity & Tamper Detection
1. **Off-Chain Database**: Stores full operational data, images, and user records in PostgreSQL for high-speed querying.
2. **On-Chain Anchor**: Each milestone event records the cryptographic hash (`payload_hash`) on Hyperledger Fabric.
3. **Public Verification Check (`/verify`)**: When a consumer or auditor scans the batch QR code:
   - The platform dynamically recalculates the SHA-256 hash from current database records.
   - It fetches the authoritative on-chain hash from Hyperledger Fabric.
   - If the hashes match, the batch is marked **Verified & Authentic**.
   - If any field in the database was tampered with (e.g. lab result changed from `FAIL` to `PASS` or harvest date modified), the hash comparison fails immediately, displaying a **CRITICAL WARNING: Data Tampered**.
