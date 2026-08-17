# Dravya — Technology Stack

## 1. Multi-Tier Technology Breakdown

| Subsystem | Technology | Purpose / Details |
| :--- | :--- | :--- |
| **Frontend Web App** | Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS | High-performance responsive web dashboard for all roles with server-side rendering and client state management via Zustand & React Query. |
| **Backend REST API** | Node.js, Express.js, TypeScript | Core business logic, JWT authentication, user management, inspection assignments, and REST routing. |
| **Primary Database** | PostgreSQL, Prisma ORM | Relational persistence for users, batches, farm profiles, lab tests, and audit logs. |
| **AI Inference Engine** | Python 3.12, FastAPI, PyTorch 2.13, Pillow, Pydantic v2 | Deep learning plant classification (EfficientNet-B0), batch validation, duplicate audits, and Dravya AI Copilot. |
| **Blockchain Network** | Hyperledger Fabric | Enterprise permissioned distributed ledger for cryptographic state proofs and immutable provenance anchoring. |
| **Containerization** | Docker, Docker Compose | Production container packaging and microservice orchestration. |
| **Quality & Testing** | PyTest (Python, 270+ tests), Jest/React Testing Library | Comprehensive unit, integration, and API contract test coverage. |
