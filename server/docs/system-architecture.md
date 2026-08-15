# Dravya System Architecture & Integration Audit

**Date**: 2026-08-13
**Phase**: Full-System Integration Audit

## Overview
Dravya is a full-stack Ayurvedic supply chain platform built on an event-driven, blockchain-anchored architecture. It manages the entire lifecycle of medicinal herbs from cultivation by producers, inspection by verification authorities, quality testing by laboratories, and supply chain tracking by distributors, culminating in public QR code verification for consumers.

## Core Architectural Components

### 1. Database & Persistence Layer (Prisma + PostgreSQL)
- **Central Source of Truth**: All operational data (batches, users, verifications) is stored in a relational PostgreSQL database managed by Prisma.
- **Relational Integrity**: Strict schema relationships enforce that Quality Tests belong to Batches, Inspections belong to Batches, and Users are mapped by specific Roles.
- **State Machines**: Database enums govern strict state transitions (e.g. `PENDING` -> `ASSIGNED` -> `COMPLETED` -> `QUALITY_APPROVED` -> `DELIVERED`).

### 2. Application Layer (Express/Node.js)
- **Role-Based Access Control (RBAC)**: Enforced via robust middleware leveraging JWT tokens. Each role (Producer, Admin, Authority, Lab, Distributor) is cryptographically bound to specific API routes.
- **RESTful API Design**: Modularized routes and controllers for clean separation of concerns.
- **Event-Driven Services**: Specialized service classes (e.g., `BlockchainService`, `NotificationService`, `QRService`) are invoked by controllers upon significant state changes.

### 3. Blockchain & Trust Layer (Hyperledger Fabric)
- **Immutable Ledger**: The system achieves tamper-evident traceability by anchoring critical lifecycle events to a Hyperledger Fabric network.
- **Hashing**: `HashingService` calculates deterministic SHA-256 hashes of critical data payloads (e.g., `ProducerVerification`, `BatchInspection`, `QualityTest`).
- **Idempotent Anchoring**: `BlockchainService` ensures records are only anchored once via a `BlockchainRecord` table mapping.
- **Fabric Gateway**: The application communicates with the blockchain via the Fabric Gateway SDK (`fabric-connection.service.ts`) directly interfacing with the live local Hyperledger Fabric network nodes.

## 4. Consumer Verification System
- **Dynamic QR Generation**: QR codes are strictly generated **only** if all prerequisites are met (`isProducerApproved`, `isInspectionApproved`, `isTestPassed`).
- **Live Integrity Checks**: When a consumer scans a QR code, the system dynamically fetches the live data from the database, hashes it, and queries the blockchain for the originally anchored hash. Any discrepancy instantly flags the product as tampered.

## Integration Audit Findings

### Strengths
- The role-based separation is fully robust and functions successfully across 22 interconnected steps.
- The state transition logic correctly models real-world business workflows.
- The cryptographic hashing successfully catches database-level tampering by validating against the live immutable Fabric ledger.

### Future Considerations
- Transitioning the local CCaaS Fabric network configuration to a cloud-based multi-org Kubernetes deployment.
- Migrating temporary `authLimiter` overrides back to strict production rate limits.
- Extending public verification metrics to display lab reports natively inside the scanning application.
