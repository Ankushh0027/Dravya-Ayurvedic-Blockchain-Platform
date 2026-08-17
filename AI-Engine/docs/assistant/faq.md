# Dravya — SIH Demo & Viva FAQ

## 1. Frequently Asked Questions

### Q: What is Dravya and why was it created?
**A**: Dravya is an AI-powered botanical identification and blockchain traceability platform designed to solve the critical problem of raw herb adulteration, accidental species substitution, and opaque supply chains in Ayurvedic medicine. It ensures complete authenticity from the farmer's harvest to the consumer.

### Q: What is the role of AI in Dravya?
**A**: The AI Engine uses a fine-tuned EfficientNet-B0 deep learning model (98.67% accuracy across 82 medicinal species) to identify plant species from field photos, resolve botanical taxonomy, evaluate confidence, and assign verification statuses (`AI_CONFIRMED` or `REVIEW_REQUIRED`).

### Q: What is the role of Blockchain in Dravya?
**A**: Dravya uses Hyperledger Fabric to record immutable cryptographic SHA-256 hashes of batch creation, authority lot inspections, laboratory test certificates, and distribution handoffs. This ensures that any subsequent unauthorized database edits trigger a tamper alert during public QR verification.

### Q: How does herb identification work?
**A**: When a farmer captures a leaf photo, the image is validated, resized to $224 \times 224$, normalized, and passed through EfficientNet-B0. The model outputs a softmax probability vector across 82 species, mapping the predicted class ID to its canonical common and scientific botanical names.

### Q: What is a deterministic Batch ID?
**A**: Batch IDs follow the format `DRAVYA-{HERB_CODE}-{YYYYMMDD}-{HASH}` (e.g. `DRAVYA-ASH-20260810-346DA7`), generated deterministically from species name, farmer ID, harvest date, and quantity to ensure collision resistance and auditability.

### Q: What is the complete supply chain workflow?
**A**: The 5-stage workflow consists of:
1. Producer Registration & Farm Inspection.
2. Herb Cultivation, Harvest & AI Identification.
3. Laboratory Analytical Quality Testing (Heavy Metals, Pesticides, Active Compounds).
4. Distribution & Logistics Tracking.
5. Public QR Verification & Tamper Detection at `/verify`.
