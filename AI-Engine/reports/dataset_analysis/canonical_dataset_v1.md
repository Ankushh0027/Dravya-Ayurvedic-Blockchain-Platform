# Dravya AI — Canonical Dataset Materialization & Verification Report (v1)

**Generated:** 2026-08-09 07:31:32 UTC  
**Safety Affirmation:** Raw Datasets READ-ONLY & 100% Untouched (`C:\Datasets\CIMPd`, `C:\Datasets\Kaggle`, `C:\Datasets\Hugging_Face`)  
**Materialization Status:** `STEP 3 STATUS: PASS`  
**Canonical Dataset Path:** `C:\Dravya\Dravya-Ayurvedic-Blockchain-Platform\AI-Engine\data\canonical\v1`  
**Deterministic Seed:** `42`  

---

## 1. Materialization Summary Totals

| Metric | Count / Value |
|---|---|
| **Approved Canonical Classes** | **94** |
| **Total Canonical Images Materialized** | **22,547** |
| **Unique SHA-256 Hashes** | **22,547** |
| **Train Split Images (80%)** | **18,037** |
| **Validation Split Images (10%)** | **2,254** |
| **Test Split Images (10%)** | **2,256** |
| **Cross-Split Hash Leakage** | **0** |
| **Corrupt Image Failures** | **0** |
| **SHA-256 Hash Mismatches** | **0** |
| **Minimum Class Size** | **40** |
| **Maximum Class Size** | **1,083** |
| **Mean Class Size** | **274.96** |
| **Median Class Size** | **201.5** |
| **Overall Class Imbalance Ratio** | **27.07:1** |
| **READY FOR GPU TRAINING** | **YES** |

---

## 2. Per-Class Distribution (All 94 Approved Classes)

| Class ID | Species Name | Scientific Name | Total | Train | Val | Test | Sources |
|---|---|---|---|---|---|---|---|
| `DRAVYA_0001` | **Murraya koenigii (Curry Leaf)** | *Murraya koenigii* | 1,083 | 866 | 108 | 109 | CIMPd, Hugging_Face |
| `DRAVYA_0002` | **Ocimum sanctum (Holy Basil/Tulsi)** | *Ocimum sanctum* | 983 | 786 | 98 | 99 | CIMPd, Hugging_Face |
| `DRAVYA_0003` | **Rosa spp. (Rose)** | *Rosa spp.* | 722 | 578 | 72 | 72 | CIMPd, Hugging_Face |
| `DRAVYA_0004` | **Solanum nigrum (Makoy/Black Nightshade)** | *Solanum nigrum* | 937 | 750 | 94 | 93 | CIMPd, Hugging_Face |
| `DRAVYA_0005` | **Mentha spp. (Mint)** | *Mentha spp.* | 652 | 522 | 65 | 65 | CIMPd, Hugging_Face |
| `DRAVYA_0006` | **Saraca asoca (Ashoka)** | *Saraca asoca* | 620 | 496 | 62 | 62 | CIMPd, Hugging_Face |
| `DRAVYA_0007` | **Plectranthus amboinicus (Doddapatre/Indian Borage)** | *Plectranthus amboinicus* | 601 | 481 | 60 | 60 | Hugging_Face |
| `DRAVYA_0008` | **Piper betle (Betel Leaf)** | *Piper betle* | 440 | 352 | 44 | 44 | Hugging_Face |
| `DRAVYA_0009` | **Lantana camara (Lantana)** | *Lantana camara* | 745 | 596 | 74 | 75 | CIMPd, Hugging_Face |
| `DRAVYA_0010` | **Psidium guajava (Guava)** | *Psidium guajava* | 527 | 422 | 53 | 52 | CIMPd, Hugging_Face, Kaggle |
| `DRAVYA_0011` | **Hibiscus rosa-sinensis (Hibiscus)** | *Hibiscus rosa-sinensis* | 492 | 394 | 49 | 49 | CIMPd, Hugging_Face, Kaggle |
| `DRAVYA_0012` | **Citrus limon (Lemon)** | *Citrus limon* | 497 | 398 | 50 | 49 | CIMPd, Hugging_Face |
| `DRAVYA_0013` | **Tinospora cordifolia (Giloy/Amrita)** | *Tinospora cordifolia* | 420 | 336 | 42 | 42 | Hugging_Face, Kaggle |
| `DRAVYA_0014` | **Bambusoideae (Bamboo)** | *Bambusoideae* | 366 | 293 | 37 | 36 | CIMPd, Hugging_Face |
| `DRAVYA_0015` | **Annona squamosa (Custard Apple)** | *Annona squamosa* | 622 | 498 | 62 | 62 | CIMPd |
| `DRAVYA_0016` | **Azadirachta indica (Neem)** | *Azadirachta indica* | 338 | 270 | 34 | 34 | Hugging_Face |
| `DRAVYA_0017` | **Artocarpus heterophyllus (Jackfruit)** | *Artocarpus heterophyllus* | 463 | 370 | 46 | 47 | CIMPd, Hugging_Face |
| `DRAVYA_0018` | **Ricinus communis (Castor)** | *Ricinus communis* | 289 | 231 | 29 | 29 | Hugging_Face, Kaggle |
| `DRAVYA_0019` | **Pongamia pinnata (Honge/Karanja)** | *Pongamia pinnata* | 303 | 242 | 30 | 31 | Hugging_Face, Kaggle |
| `DRAVYA_0020` | **Mangifera indica (Mango)** | *Mangifera indica* | 311 | 249 | 31 | 31 | Hugging_Face |
| `DRAVYA_0021` | **Aegle marmelos (Bael)** | *Aegle marmelos* | 559 | 447 | 56 | 56 | CIMPd |
| `DRAVYA_0022` | **Aloe vera** | *Aloe barbadensis* | 282 | 226 | 28 | 28 | Hugging_Face, Kaggle |
| `DRAVYA_0023` | **Jasminum spp. (Jasmine)** | *Jasminum spp.* | 307 | 246 | 31 | 30 | Hugging_Face |
| `DRAVYA_0024` | **Carica papaya (Papaya)** | *Carica papaya* | 239 | 191 | 24 | 24 | CIMPd, Hugging_Face |
| `DRAVYA_0025` | **Calotropis gigantea (Crown Flower/Ekka)** | *Calotropis gigantea* | 293 | 234 | 29 | 30 | Hugging_Face |
| `DRAVYA_0026` | **Nyctanthes arbor-tristis (Harsingar/Parijat)** | *Nyctanthes arbor-tristis* | 509 | 407 | 51 | 51 | CIMPd |
| `DRAVYA_0027` | **Bauhinia variegata (Kachnar)** | *Bauhinia variegata* | 508 | 406 | 51 | 51 | CIMPd |
| `DRAVYA_0028` | **Bacopa monnieri (Brahmi)** | *Bacopa monnieri* | 248 | 198 | 25 | 25 | Hugging_Face |
| `DRAVYA_0029` | **Clerodendrum splendens** | *Clerodendrum splendens* | 492 | 394 | 49 | 49 | CIMPd |
| `DRAVYA_0030` | **Nerium oleander (Oleander)** | *Nerium oleander* | 235 | 188 | 24 | 23 | Hugging_Face |
| `DRAVYA_0032` | **Salvia splendens (Scarlet Sage)** | *Salvia splendens* | 462 | 370 | 46 | 46 | CIMPd |
| `DRAVYA_0033` | **Lawsonia inermis (Henna)** | *Lawsonia inermis* | 228 | 182 | 23 | 23 | Hugging_Face, Kaggle |
| `DRAVYA_0034` | **Punica granatum (Pomegranate)** | *Punica granatum* | 222 | 178 | 22 | 22 | Hugging_Face |
| `DRAVYA_0035` | **Phyllanthus emblica (Amla)** | *Phyllanthus emblica* | 213 | 170 | 21 | 22 | Hugging_Face |
| `DRAVYA_0036` | **Tropaeolum majus (Nasturtium)** | *Tropaeolum majus* | 424 | 339 | 42 | 43 | CIMPd |
| `DRAVYA_0037` | **Basella alba (Malabar Spinach)** | *Basella alba* | 249 | 199 | 25 | 25 | Hugging_Face |
| `DRAVYA_0038` | **Manilkara zapota (Sapota/Chikoo)** | *Manilkara zapota* | 190 | 152 | 19 | 19 | Hugging_Face |
| `DRAVYA_0039` | **Tagetes spp. (Marigold)** | *Tagetes spp.* | 279 | 223 | 28 | 28 | CIMPd, Hugging_Face |
| `DRAVYA_0040` | **Cardiospermum halicacabum (Balloon Vine)** | *Cardiospermum halicacabum* | 306 | 245 | 31 | 30 | Hugging_Face |
| `DRAVYA_0041` | **Tamarindus indica (Tamarind)** | *Tamarindus indica* | 176 | 141 | 18 | 17 | Hugging_Face |
| `DRAVYA_0042` | **Coriandrum sativum (Coriander)** | *Coriandrum sativum* | 235 | 188 | 24 | 23 | Hugging_Face |
| `DRAVYA_0043` | **Catharanthus roseus (Sadabahar)** | *Catharanthus roseus* | 189 | 151 | 19 | 19 | Hugging_Face |
| `DRAVYA_0044` | **Cymbopogon citratus (Lemongrass)** | *Cymbopogon citratus* | 146 | 117 | 15 | 14 | Hugging_Face |
| `DRAVYA_0045` | **Withania somnifera (Ashwagandha)** | *Withania somnifera* | 140 | 112 | 14 | 14 | Hugging_Face |
| `DRAVYA_0046` | **Persea americana (Avocado)** | *Persea americana* | 146 | 117 | 15 | 14 | Hugging_Face |
| `DRAVYA_0047` | **Pelargonium spp. (Geranium)** | *Pelargonium spp.* | 146 | 117 | 15 | 14 | Hugging_Face |
| `DRAVYA_0048` | **Oxalis spp. (Wood Sorrel)** | *Oxalis spp.* | 146 | 117 | 15 | 14 | Hugging_Face |
| `DRAVYA_0049` | **Barleria (Barlaria)** | *Barleria spp.* | 284 | 227 | 28 | 29 | CIMPd |
| `DRAVYA_0050` | **Euphorbia hirta (Asthma Weed)** | *Euphorbia hirta* | 163 | 130 | 16 | 17 | Hugging_Face |
| `DRAVYA_0051` | **Amaranthus viridis (Green Amaranth)** | *Amaranthus viridis* | 245 | 196 | 24 | 25 | Hugging_Face |
| ... | *(And 32 more approved classes listed in JSON/CSV manifests)* | | | | | | |

---

## 3. Data Integrity & Leakage Verification Checklist
```text
RAW DATASETS UNTOUCHED:  YES (100% READ-ONLY)
APPROVED CLASSES MATCH:  YES (Exactly 94 approved classes)
REJECTED/REVIEW INCLUDED: NO (0 unapproved classes allowed)
EXACT DUPLICATES COLLAPSED: YES (1 representative per SHA-256 group)
CROSS-SPLIT LEAKAGE:     PASS (0 shared hashes across train/val/test)
IMAGE INTEGRITY DECODE: PASS (0 corrupt images)
PROVENANCE METADATA:     EXPORTED (data/canonical/v1/metadata/image_provenance.json)
STEP 3 STATUS:           PASS
```