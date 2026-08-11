# Dravya AI — Combined Dataset Species Inventory & Feasibility Report (v2)

**Generated:** 2026-08-09 06:46:04 UTC  
**Status:** Read-Only Inventory Completed  

---

## Executive Summary

| Key Metric | Value |
|---|---|
| **Total Raw Scanned Images** | **42,062** |
| **Total Raw Class Folders** | **331** |
| **Estimated Unique Species** | **180** |
| **Species Across Multiple Datasets** | **73** |
| **Species in Only One Dataset** | **107** |
| **Species with 100+ Images** | **103** |
| **Species with 300+ Images** | **44** |
| **Species with 500+ Images** | **28** |
| **Low-Data Species (<100 images)** | **77** |
| **Taxonomy Conflicts / Unresolved** | **14** |
| **Overall Class Imbalance Ratio** | **35.82:1** |
| **Recommended First-Model Species Count** | **91** |

---

## Core Feasibility Assessment & Answers to Key Questions

### 1. How many total species are available?
Across all three datasets, **180 candidate species** have been identified after safe normalization and botanical taxonomy grouping of the 331 raw class folders.

### 2. How many are realistically usable for training?
Of the 180 candidate species, **91 species** meet the production quality threshold of having at least **100 valid images** and unambiguous botanical taxonomy.

### 3. How many images are available per species?
- **300+ Images:** 44 species (High representation)
- **100–300 Images:** 59 species (Moderate representation)
- **50–100 Images:** 72 species (Requires data augmentation/sourcing)
- **<50 Images:** 5 species (Severe data deficiency)

### 4. How many species can reasonably be included in the first large model?
We recommend starting with **91 high-confidence species** that have >=100 images and clear botanical mappings. This balances model accuracy, class balance, and evaluation benchmark reliability.

### 5. Which species require additional data?
The **77 low-data species** (<100 images) require targeted dataset expansion before inclusion in core production models.

### 6. Which classes have taxonomy conflicts?
- **Vigna / Phaseolus spp. (Beans):** Raw class combines multiple plant genera.
- **Spinach1:** Ambiguous common name (Spinacia oleracea vs Amaranthus dubius).
- **Insulin / Caricature:** Vernacular common names without verified botanical binomials.

### 7. Which classes should NOT yet be included?
- **Non-Plant / Corrupt Classes:** `leafs` (generic non-aligned sample folder in CIMPd).
- **Unresolved Vernaculars:** `Badipala`, `Chakte`, `Ganigale`, `Kambajala`, `Kasambruga`, `Kepala` (require expert botanical review).

---

## Per-Dataset Breakdown Summary

| Dataset ID | Root Path | Images | Classes | Corrupt | Non-Image Files |
|---|---|---|---|---|---|
| `CIMPd` | `C:\Datasets\CIMPd` | 8,592 | 42 | 0 | 0 |
| `Kaggle` | `C:\Datasets\Kaggle` | 12,845 | 120 | 0 | 4 |
| `Hugging_Face` | `C:\Datasets\Hugging_Face` | 20,625 | 169 | 0 | 4 |

---

## Exact Duplicate Summary (Read-Only Scan)
- **Total Exact Duplicate Images:** 25,610
- **Within-Dataset Duplicate Images:** 2
- **Cross-Dataset Duplicate Images:** 25,608

---

## Top 20 Species by Image Count

| Candidate Canonical Species | Scientific Name | Total Images | Datasets | Status |
|---|---|---|---|---|
| **Murraya koenigii (Curry Leaf)** | *Murraya koenigii* | 1,397 | CIMPd, Hugging_Face, Kaggle | `APPROVED_HARMONIZED` |
| **Ocimum sanctum (Holy Basil/Tulsi)** | *Ocimum sanctum* | 1,306 | CIMPd, Hugging_Face, Kaggle | `APPROVED_HARMONIZED` |
| **Rosa spp. (Rose)** | *Rosa spp.* | 1,142 | CIMPd, Hugging_Face, Kaggle | `APPROVED_HARMONIZED` |
| **Solanum nigrum (Makoy/Black Nightshade)** | *Solanum nigrum* | 1,115 | CIMPd, Hugging_Face, Kaggle | `APPROVED_HARMONIZED` |
| **Mentha spp. (Mint)** | *Mentha spp.* | 940 | CIMPd, Hugging_Face, Kaggle | `APPROVED_HARMONIZED` |
| **Saraca asoca (Ashoka)** | *Saraca asoca* | 894 | CIMPd, Hugging_Face, Kaggle | `APPROVED_HARMONIZED` |
| **Plectranthus amboinicus (Doddapatre/Indian Borage)** | *Plectranthus amboinicus* | 891 | Hugging_Face, Kaggle | `APPROVED_HARMONIZED` |
| **Piper betle (Betel Leaf)** | *Piper betle* | 851 | Hugging_Face, Kaggle | `APPROVED_HARMONIZED` |
| **Lantana camara (Lantana)** | *Lantana camara* | 821 | CIMPd, Hugging_Face, Kaggle | `APPROVED_HARMONIZED` |
| **Psidium guajava (Guava)** | *Psidium guajava* | 794 | CIMPd, Hugging_Face, Kaggle | `APPROVED_HARMONIZED` |
| **Hibiscus rosa-sinensis (Hibiscus)** | *Hibiscus rosa-sinensis* | 768 | CIMPd, Hugging_Face, Kaggle | `APPROVED_HARMONIZED` |
| **Citrus limon (Lemon)** | *Citrus limon* | 766 | CIMPd, Hugging_Face, Kaggle | `APPROVED_HARMONIZED` |
| **Tinospora cordifolia (Giloy/Amrita)** | *Tinospora cordifolia* | 665 | Hugging_Face, Kaggle | `APPROVED_HARMONIZED` |
| **Bambusoideae (Bamboo)** | *Bambusoideae* | 630 | CIMPd, Hugging_Face, Kaggle | `APPROVED_HARMONIZED` |
| **Annona squamosa (Custard Apple)** | *Annona squamosa* | 622 | CIMPd | `APPROVED_HARMONIZED` |
| **Azadirachta indica (Neem)** | *Azadirachta indica* | 616 | Hugging_Face, Kaggle | `APPROVED_HARMONIZED` |
| **Artocarpus heterophyllus (Jackfruit)** | *Artocarpus heterophyllus* | 573 | CIMPd, Hugging_Face, Kaggle | `APPROVED_HARMONIZED` |
| **Ricinus communis (Castor)** | *Ricinus communis* | 572 | Hugging_Face, Kaggle | `APPROVED_HARMONIZED` |
| **Pongamia pinnata (Honge/Karanja)** | *Pongamia pinnata* | 572 | Hugging_Face, Kaggle | `APPROVED_HARMONIZED` |
| **Mangifera indica (Mango)** | *Mangifera indica* | 560 | Hugging_Face, Kaggle | `APPROVED_HARMONIZED` |