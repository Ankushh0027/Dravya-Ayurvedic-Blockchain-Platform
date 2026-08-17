# Dravya — Complete Supply Chain Workflow

## 1. Five-Phase Supply Chain Journey

```
[Phase 1: Registration] ──> [Phase 2: Harvest & AI ID] ──> [Phase 3: Lab Testing] ──> [Phase 4: Distribution] ──> [Phase 5: Public QR Verify]
    (Producer & Farm           (AI Camera Batch Ingestion      (Heavy Metals, Pesticides,    (Custody Transfer, GPS,      (Consumer / Regulator
     Verification)               & Field Lot Inspection)         Active Compounds Cert)       Logistics Tracking)          Tamper Integrity Check)
```

### Phase 1: Registration & Initial Verification
1. **Producer Submission**: The herb grower/producer registers on Dravya and submits farm location and cultivation details.
2. **Verification Assignment**: The Admin assigns a regional Verification Authority.
3. **Authority Approval & Anchor**: The Authority inspects the farm physically, verifies land records, and approves the Producer. The profile hash is anchored on the blockchain.

### Phase 2: Cultivation & Harvest (Batch Creation)
4. **AI Identification & Batch Creation**: The producer takes a field photo of the harvested herb foliage. The Dravya AI Engine identifies the species (*Ashwagandha* / *Withania somnifera* with 98.67% accuracy), computes confidence, normalizes harvest weight into kilograms, and generates a deterministic Batch ID.
5. **Lot Inspection**: A Verification Authority physically inspects the harvested lot, validates physical parameters, and signs off.
6. **Blockchain Anchor**: The inspection hash is anchored on Hyperledger Fabric.

### Phase 3: Laboratory Testing
7. **Lab Assignment**: The Admin assigns the batch to an AYUSH-certified laboratory.
8. **Quality Testing**: The lab conducts analytical chemistry tests (Heavy Metals, Pesticide Residues, Microbial Contamination, and Active Phytochemical Compounds).
9. **Certificate of Analysis (CoA)**: The lab generates a signed test report. The test data and CoA hash are anchored to the blockchain, updating the batch status to `QUALITY_APPROVED`.

### Phase 4: Distribution & Logistics
10. **Distributor Handoff**: The batch is transferred to an authorized logistics partner.
11. **Dispatch & Delivery**: Custody transfer and delivery milestones are tracked and digitally signed.
12. **QR Code Generation**: The platform generates the final Traceability QR Code for packaging.

### Phase 5: Public Verification & Tamper Detection
13. **Consumer QR Scan**: Any consumer, doctor, or regulatory auditor scans the product QR code on `/verify` to see the complete unalterable timeline (farmer name, harvest location, AI confidence score, lab certificate, and transit history).
14. **Tamper Detection**: The system cross-checks the current record against the blockchain hash. If any database record was modified without authorization, a tamper alarm is triggered.
