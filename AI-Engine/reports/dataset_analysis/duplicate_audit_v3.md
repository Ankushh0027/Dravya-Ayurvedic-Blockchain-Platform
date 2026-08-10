# Dravya AI Engine — Step 2 Read-Only Duplicate & Data-Leakage Audit Report (v3)

**Audited At:** 2026-08-09 07:15:48 UTC  
**Safety Affirmation:** Raw Datasets READ-ONLY & 100% Untouched (`C:\Datasets\CIMPd`, `C:\Datasets\Kaggle`, `C:\Datasets\Hugging_Face`)  
**Audit Decision:** `STEP 2 STATUS: PASS`  

---

## 1. Global SHA-256 Duplicate Statistics

| Metric | Count | Description |
|---|---|---|
| **Total Physical Image Files** | **42,062** | Total files cataloged in Step 1 physical scan |
| **Unique SHA-256 Hashes** | **29,161** | Distinct image content hashes across all datasets |
| **Duplicate SHA-256 Hash Groups** | **12,709** | Hashes appearing in $\ge 2$ physical image files |
| **Files Belonging to Duplicate Groups** | **25,610** | Total physical files with non-unique content |
| **Redundant Duplicate Instances** | **12,901** | Total extra physical copies eligible for deduplication |

---

## 2. Within-Dataset Duplicate Breakdown

| Dataset Source | Total Images | Unique Hashes | Duplicate Groups | Duplicate Files | Redundant Instances |
|---|---|---|---|---|---|
| **CIMPd** | 8,592 | 8,592 | 0 | 0 | 0 |
| **Kaggle** | 12,845 | 12,747 | 98 | 196 | 98 |
| **Hugging_Face** | 20,625 | 20,530 | 95 | 190 | 95 |

---

## 3. Cross-Dataset Duplicate Matrix

| Dataset Combination | Duplicate Hash Groups | Total Files | Redundant Copies |
|---|---|---|---|
| **CIMPd (Internal Only)** | 0 | 0 | 0 |
| **Kaggle (Internal Only)** | 1 | 2 | 1 |
| **Hugging_Face (Internal Only)** | 0 | 0 | 0 |
| **CIMPd ↔ Kaggle** | 0 | 0 | 0 |
| **CIMPd ↔ Hugging_Face** | 0 | 0 | 0 |
| **Kaggle ↔ Hugging_Face** | 12,708 | 25,608 | 12,900 |
| **CIMPd ↔ Kaggle ↔ Hugging_Face** | 0 | 0 | 0 |

---

## 4. Class-Level & Species Conflict Analysis

| Conflict Type | Duplicate Group Count | Description / Handling Policy |
|---|---|---|
| **Cross-Class Conflicts** | **12,708** | Duplicate image found across multiple raw folders; assigned to canonical representative |
| **Cross-Species Conflicts** | **1,963** | Duplicate image mapped to different species; held in review queue before split |
| **Cross-Status Conflicts** | **220** | Duplicate image present in both APPROVED and NEEDS_REVIEW/REJECTED species |

---

## 5. Top 5 Largest Duplicate Groups

| Group ID | SHA-256 (Truncated) | Files | Datasets | Mapped Species | Canonical Representative Path |
|---|---|---|---|---|---|
| `DUP_00528` | `dc7de80f86dd...` | 4 | Hugging_Face, Kaggle | Erythrina variegata (Badipala) | `Badipala\1180.jpg` |
| `DUP_00529` | `f0cb6ec716cb...` | 4 | Hugging_Face, Kaggle | Erythrina variegata (Badipala) | `Badipala\1184.jpg` |
| `DUP_00598` | `a3aeac76bb7d...` | 4 | Hugging_Face, Kaggle | Cardiospermum halicacabum (Balloon Vine) | `Cardiospermum halicacabum\1324.jpg` |
| `DUP_00986` | `8562cad407d2...` | 4 | Hugging_Face, Kaggle | Bacopa monnieri (Brahmi) | `Brahmi-Bacopa monnieri\2212.jpg` |
| `DUP_00989` | `49e370dce05b...` | 4 | Hugging_Face, Kaggle | Bacopa monnieri (Brahmi) | `Brahmi-Bacopa monnieri\2220.jpg` |

---

## 6. Deterministic Data Leakage & Representative Selection Policies

### A. Leakage-Safe Dataset Split Policy (Group-Level Atomic Splitting)
- **Rule:** Every SHA-256 duplicate group is treated as an indivisible atomic unit.
- **Enforcement:** During dataset materialization, split assignment (`train`, `val`, `test`) is computed on the **SHA-256 hash group level** rather than individual image file paths.
- **Guarantee:** All physical copies sharing a SHA-256 hash will be assigned to the exact same dataset split, guaranteeing **0 cross-split leakage**.

### B. Canonical Representative Selection Policy
When redundant exact duplicates exist across raw dataset folders, the canonical representative image record is chosen reproducibly using the following hierarchy:
1. **Dataset Priority:** `CIMPd` (Priority 0) > `Hugging_Face` (Priority 1) > `Kaggle` (Priority 2).
2. **Image Resolution:** Higher pixel resolution (`width * height`).
3. **Lexicographical Path Order:** Ascending order of `relative_path` as a tie-breaker.

### C. Near-Duplicate Hashing Status
- **Current Scope:** Step 2 evaluates exact SHA-256 hash matching.
- **Future Scope:** Perceptual hashing (`pHash`) and visual embeddings similarity clustering are designated for future post-materialization pipeline releases.

---

## 7. Step 2 Quality Gate & Audit Decision
```text
INVENTORY RECONCILIATION: PASS (42,062 / 42,062 physical files verified)
SHA-256 INTEGRITY:       PASS (0 missing or corrupt hashes)
CROSS-DATASET MATRIX:     PASS (All combinations identified)
DATA LEAKAGE POLICY:      DEFINED (Group-level atomic split)
REPRESENTATIVE POLICY:    DEFINED (CIMPd > Hugging_Face > Kaggle + Resolution)
RAW DATASET INTEGRITY:    TOUCHED = NO (100% READ-ONLY)
STEP 2 STATUS:            PASS
```