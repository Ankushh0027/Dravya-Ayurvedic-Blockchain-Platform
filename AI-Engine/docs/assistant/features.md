# Dravya — Key Features & Capabilities

## 1. Implemented Core Capabilities
- **Visual AI Herb Classification**: Identifies 82 medicinal plant species from RGB field photos with 98.67% accuracy in sub-50ms inference.
- **Botanical Taxonomy Harmonization**: Resolves multi-lingual vernacular names, trade names, and synonyms to authoritative binomial nomenclature.
- **Deterministic Batch Management**: Generates reproducible, collisions-resistant Batch IDs based on species, farmer, date, and weight.
- **Unit Normalization Engine**: Automatically normalizes diverse harvest measurements (grams, tonnes, quintals, pounds) into canonical kilograms (kg).
- **Blockchain Traceability Anchoring**: Builds tamper-evident JSON records with SHA-256 payload digests anchored to Hyperledger Fabric.
- **Multi-Role Stakeholder Dashboards**: Tailored UI workflows for Farmers/Producers, Verification Authorities, Testing Laboratories, Logistics Distributors, and Platform Administrators.
- **Public QR Verification**: Instant verification portal (`/verify`) allowing consumers to validate the full seed-to-shelf provenance journey.
- **Dravya AI Copilot**: Intelligent, context-aware natural language assistant answering live inventory/batch data questions and project architecture knowledge.

## 2. Planned Extensions (Future Scope)
- **Out-of-Distribution (OOD) Hard Thresholding**: Rejecting non-plant image uploads (e.g. random objects) via confidence bounding ($\tau = 0.65$).
- **Grad-CAM Visual Explainability**: Heatmap overlays highlighting specific leaf venation and morphological feature activations.
- **IoT Environmental Telemetry**: Direct integration with solar soil moisture and humidity sensors during cultivation.
