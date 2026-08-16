# Dravya Phase F: 22-Step SIH Demo Flow

This document details the exact sequence of events for the final SIH Prototype demonstration.

## Part 1: Registration & Initial Verification
1. **Producer Login**: Log in as `producer@dravya.in`.
2. **Producer Profile**: Producer submits their farm details for verification.
3. **Admin Assignment**: Admin assigns a Verification Authority to the Producer.
4. **Authority Login**: Log in as `verifier@dravya.in`.
5. **Authority Approval**: Authority visits the farm, verifies details, and approves the Producer.
6. **Blockchain Anchor**: The system automatically hashes the Verification Profile and anchors it to Hyperledger Fabric.

## Part 2: Cultivation & Harvest (Batch Creation)
7. **Producer Batch Creation**: Producer creates a new Batch of *Ashwagandha* (or another herb) and inputs cultivation methods and harvest date.
8. **Admin Lot Inspection Assignment**: Admin assigns the Verification Authority to inspect the harvested lot.
9. **Authority Inspection**: Authority physically inspects the lot and approves the quantity and quality.
10. **Blockchain Anchor**: The Batch Inspection record is anchored to Fabric.

## Part 3: Laboratory Testing
11. **Admin Lab Assignment**: Admin assigns the Batch to an AYUSH-certified Laboratory (`lab@dravya.in`).
12. **Lab Login**: Log in as `lab@dravya.in`.
13. **Quality Testing**: Lab conducts tests (Heavy Metals, Pesticides, Active Compounds) and enters results.
14. **Lab Report Generation**: Lab generates the final signed PDF/report.
15. **Blockchain Anchor**: The Quality Test and Lab Report are anchored to Fabric. The batch status changes to `QUALITY_APPROVED`.

## Part 4: Distribution & Logistics
16. **Admin Distributor Assignment**: Admin assigns the batch to a logistics partner (`distributor@dravya.in`).
17. **Distributor Login**: Log in as `distributor@dravya.in`.
18. **Receive Batch**: Distributor receives the batch from the Producer.
19. **Dispatch Batch**: Distributor dispatches the batch towards the final destination.
20. **Deliver Batch**: Distributor marks the batch as delivered.
21. **QR Generation**: Admin generates the final Traceability QR Code for the Batch.

## Part 5: Public Verification & Tamper Detection (The Wow Factor)
22. **Public QR Scan**: A consumer (or judge) scans the QR code or enters it at `/verify`. They see the complete timeline.
23. **Tamper Attack (Simulated)**: An attacker hacks the PostgreSQL database and changes the Lab Test results from `FAIL` to `PASS`, or alters the harvest date.
24. **Blockchain Integrity Check**: The consumer scans the QR code again. The system fetches the DB hash, compares it with the Hyperledger Fabric hash, detects the mismatch, and displays a **CRITICAL WARNING: Data Tampered**.
