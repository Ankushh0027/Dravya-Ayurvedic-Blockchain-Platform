# Dravya — Project Overview & Problem Statement

## 1. What is Dravya?
**Dravya** is an enterprise-grade, AI-powered botanical authentication and blockchain-anchored traceability platform for the Ayurvedic and herbal medicine supply chain. It provides end-to-end transparency, authenticity verification, and quality assurance from the source herb collector (farmer/producer) to the end consumer and regulatory authorities (AYUSH).

## 2. Problem Statement
The global Ayurvedic and herbal industry faces severe challenges:
1. **Species Adulteration & Accidental Substitution**: Visually similar plant species are frequently substituted, either accidentally due to lack of botanical expertise or intentionally for economic gain (e.g., substituting genuine *Saraca asoca* (Ashoka bark) with *Polyalthia longifolia* (False Ashoka), or adulterating *Withania somnifera* (Ashwagandha)).
2. **Lack of Supply Chain Provenance**: Herbal raw materials pass through multiple unverified middlemen and traders with paper-based receipts, creating opaque supply chains where origin, harvest date, and geographical source cannot be verified.
3. **Quality & Safety Risks**: Contamination with heavy metals, pesticide residues, microbial pathogens, and improper moisture levels compromises therapeutic efficacy and consumer safety.
4. **Data Tampering & Fraud**: Centralized databases and paper lab certificates can be altered or forged after testing.

## 3. Core Objectives
- **Automate Botanical Identification**: Use deep learning computer vision at the point of harvest to classify medicinal plant species with high statistical confidence.
- **Enforce Immutable Provenance**: Anchor batch creation, lot inspection, lab quality certificates, and distribution handoffs to a permissioned blockchain ledger (Hyperledger Fabric).
- **Prevent Data Tampering**: Use cryptographic SHA-256 payload hashing and on-chain verification so any modification to off-chain data (e.g. database tampering) is instantly detected.
- **Empower Farmers & Consumers**: Provide farmers with digital batch identity and fair recognition, and enable consumers/regulators to verify complete seed-to-shelf traceability via public QR scanning.
