# Dravya — System Architecture & Component Interactions

## 1. High-Level Architecture Overview
Dravya is designed as a modern multi-tier microservice and distributed ledger ecosystem comprising four core subsystems:

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Frontend Layer                    │
│      Next.js 16 • React 19 • TypeScript • Tailwind CSS      │
│  (Farmer Portal, Verifier, Lab, Distributor, Admin, Verify) │
└──────────────┬───────────────────────────────┬──────────────┘
               │ REST / JSON                   │ Multipart Form
               ▼                               ▼
┌──────────────────────────────┐ ┌────────────────────────────┐
│      Node.js / Express       │ │      Dravya AI Engine      │
│        Backend Server        │ │     FastAPI Microservice   │
│ • Prisma ORM & PostgreSQL    │ │ • PyTorch EfficientNet-B0  │
│ • Authentication & Sessions  │ │ • Botanical Taxonomy Engine│
│ • Workflow State Machine     │ │ • Batch & Traceability API │
│ • QR & Document Generation   │ │ • Dravya AI Copilot Engine │
└──────────────┬───────────────┘ └─────────────┬──────────────┘
               │ SHA-256 Hashes                │ Traceability
               ▼                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Hyperledger Fabric Blockchain               │
│ • Smart Contracts / Chaincode • Cryptographic State Proofs  │
│ • Immutable Batch Lifecycle & Inspection Anchors             │
└─────────────────────────────────────────────────────────────┘
```

## 2. Component Roles
1. **Client Frontend (`/client`)**: Role-based web interface for Producers/Farmers, Verification Authorities, AYUSH-certified Testing Labs, Logistics Distributors, Admins, and Public Verification (`/verify`).
2. **Backend API Server (`/server`)**: Handles user authentication (JWT), relational persistence (PostgreSQL with Prisma), workflow coordination, inspection lot assignments, lab test approvals, and distributor handoffs.
3. **AI Engine (`/AI-Engine`)**: Python/FastAPI microservice executing high-speed plant taxonomy inference, SHA-256 duplicate auditing, botanical review queues, model versioning, in-memory batch & inventory aggregation, and natural language AI Copilot chat.
4. **Blockchain Layer (`/blockchain`)**: Hyperledger Fabric network hosting smart contracts that store immutable state hashes, guaranteeing tamper detection across all five supply chain phases.
