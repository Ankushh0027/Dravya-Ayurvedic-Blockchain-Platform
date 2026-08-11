# Dravya AI — Candidate Training Class Selection & Taxonomy Feasibility Report (v2)

**Generated:** 2026-08-09 06:53:51 UTC  
**Pipeline Status:** Candidate Selection Complete  

---

## Dataset & Selection Summary

| Key Metric | Value |
|---|---|
| **Total Raw Scanned Images** | **42,062** |
| **Estimated Unique Candidate Species** | **180** |
| **Total Candidate Classes** | **180** |
| **APPROVED Classes (Training Eligible)** | **94** |
| **NEEDS REVIEW Classes (Excluded from v1)** | **85** |
| **REJECTED Classes (Non-Plant/Junk)** | **1** |
| **Classes with 100+ Images** | **103** |
| **Classes with 300+ Images** | **44** |
| **Taxonomy Conflicts** | **11** |
| **FINAL RECOMMENDED TRAINING CLASS COUNT** | **94** |
| **READY FOR CANONICAL DATASET V2** | **NO** |

---

## Approved Training Classes (Selected for First Model)

| Class ID | Species Name | Scientific Name | Images | Sources | Status |
|---|---|---|---|---|---|
| `DRAVYA_0001` | **Murraya koenigii (Curry Leaf)** | *Murraya koenigii* | 1,397 | CIMPd, Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0002` | **Ocimum sanctum (Holy Basil/Tulsi)** | *Ocimum sanctum* | 1,306 | CIMPd, Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0003` | **Rosa spp. (Rose)** | *Rosa spp.* | 1,142 | CIMPd, Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0004` | **Solanum nigrum (Makoy/Black Nightshade)** | *Solanum nigrum* | 1,115 | CIMPd, Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0005` | **Mentha spp. (Mint)** | *Mentha spp.* | 940 | CIMPd, Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0006` | **Saraca asoca (Ashoka)** | *Saraca asoca* | 894 | CIMPd, Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0007` | **Plectranthus amboinicus (Doddapatre/Indian Borage)** | *Plectranthus amboinicus* | 891 | Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0008` | **Piper betle (Betel Leaf)** | *Piper betle* | 851 | Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0009` | **Lantana camara (Lantana)** | *Lantana camara* | 821 | CIMPd, Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0010` | **Psidium guajava (Guava)** | *Psidium guajava* | 794 | CIMPd, Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0011` | **Hibiscus rosa-sinensis (Hibiscus)** | *Hibiscus rosa-sinensis* | 768 | CIMPd, Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0012` | **Citrus limon (Lemon)** | *Citrus limon* | 766 | CIMPd, Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0013` | **Tinospora cordifolia (Giloy/Amrita)** | *Tinospora cordifolia* | 665 | Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0014` | **Bambusoideae (Bamboo)** | *Bambusoideae* | 630 | CIMPd, Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0015` | **Annona squamosa (Custard Apple)** | *Annona squamosa* | 622 | CIMPd | `APPROVED` |
| `DRAVYA_0016` | **Azadirachta indica (Neem)** | *Azadirachta indica* | 616 | Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0017` | **Artocarpus heterophyllus (Jackfruit)** | *Artocarpus heterophyllus* | 573 | CIMPd, Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0018` | **Ricinus communis (Castor)** | *Ricinus communis* | 572 | Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0019` | **Pongamia pinnata (Honge/Karanja)** | *Pongamia pinnata* | 572 | Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0020` | **Mangifera indica (Mango)** | *Mangifera indica* | 560 | Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0021` | **Aegle marmelos (Bael)** | *Aegle marmelos* | 559 | CIMPd | `APPROVED` |
| `DRAVYA_0022` | **Aloe vera** | *Aloe barbadensis* | 559 | Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0023` | **Jasminum spp. (Jasmine)** | *Jasminum spp.* | 543 | Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0024` | **Carica papaya (Papaya)** | *Carica papaya* | 520 | CIMPd, Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0025` | **Calotropis gigantea (Crown Flower/Ekka)** | *Calotropis gigantea* | 520 | Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0026` | **Nyctanthes arbor-tristis (Harsingar/Parijat)** | *Nyctanthes arbor-tristis* | 509 | CIMPd | `APPROVED` |
| `DRAVYA_0027` | **Bauhinia variegata (Kachnar)** | *Bauhinia variegata* | 508 | CIMPd | `APPROVED` |
| `DRAVYA_0028` | **Bacopa monnieri (Brahmi)** | *Bacopa monnieri* | 500 | Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0029` | **Clerodendrum splendens** | *Clerodendrum splendens* | 492 | CIMPd | `APPROVED` |
| `DRAVYA_0030` | **Nerium oleander (Oleander)** | *Nerium oleander* | 470 | Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0032` | **Salvia splendens (Scarlet Sage)** | *Salvia splendens* | 462 | CIMPd | `APPROVED` |
| `DRAVYA_0033` | **Lawsonia inermis (Henna)** | *Lawsonia inermis* | 453 | Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0034` | **Punica granatum (Pomegranate)** | *Punica granatum* | 446 | Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0035` | **Phyllanthus emblica (Amla)** | *Phyllanthus emblica* | 426 | Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0036` | **Tropaeolum majus (Nasturtium)** | *Tropaeolum majus* | 424 | CIMPd | `APPROVED` |
| `DRAVYA_0037` | **Basella alba (Malabar Spinach)** | *Basella alba* | 395 | Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0038` | **Manilkara zapota (Sapota/Chikoo)** | *Manilkara zapota* | 380 | Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0039` | **Tagetes spp. (Marigold)** | *Tagetes spp.* | 372 | CIMPd, Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0040` | **Cardiospermum halicacabum (Balloon Vine)** | *Cardiospermum halicacabum* | 368 | Hugging_Face, Kaggle | `APPROVED` |
| `DRAVYA_0041` | **Tamarindus indica (Tamarind)** | *Tamarindus indica* | 352 | Hugging_Face, Kaggle | `APPROVED` |
| ... | *(And 54 more approved species)* | | | | |

---

## Excluded & Review Classes Explanation

| Class ID | Species Name | Images | Review Status | Rationale for Exclusion |
|---|---|---|---|---|
| `DRAVYA_0031` | Chamaecostus cuspidatus (Insulin Plant) | 470 | `NEEDS_REVIEW` | Taxonomy conflict or unresolved vernacular name requiring expert review. |
| `DRAVYA_0056` | Vigna / Phaseolus spp. (Beans) | 194 | `NEEDS_REVIEW` | Taxonomy conflict or unresolved vernacular name requiring expert review. |
| `DRAVYA_0068` | Erythrina variegata (Badipala) | 152 | `NEEDS_REVIEW` | Taxonomy conflict or unresolved vernacular name requiring expert review. |
| `DRAVYA_0069` | Graptophyllum pictum (Caricature Plant) | 152 | `NEEDS_REVIEW` | Taxonomy conflict or unresolved vernacular name requiring expert review. |
| `DRAVYA_0070` | Unresolved Kepala Leaf | 152 | `NEEDS_REVIEW` | Taxonomy conflict or unresolved vernacular name requiring expert review. |
| `DRAVYA_0073` | Unresolved Ganigale Leaf | 150 | `NEEDS_REVIEW` | Taxonomy conflict or unresolved vernacular name requiring expert review. |
| `DRAVYA_0087` | Unresolved Chakte Leaf | 136 | `NEEDS_REVIEW` | Taxonomy conflict or unresolved vernacular name requiring expert review. |
| `DRAVYA_0090` | Unspecified Spinach Variety | 134 | `NEEDS_REVIEW` | Taxonomy conflict or unresolved vernacular name requiring expert review. |
| `DRAVYA_0098` | Unresolved Kambajala Leaf | 118 | `NEEDS_REVIEW` | Taxonomy conflict or unresolved vernacular name requiring expert review. |
| `DRAVYA_0104` | Citron Lime (Herelikai) | 99 | `NEEDS_REVIEW` | Insufficient image count (99 images < 100 minimum threshold). |
| `DRAVYA_0105` | Citron Lime (Herelikai)-Citrus Medica (Citron) Or Citrus Aurantiifolia (Lime) | 99 | `NEEDS_REVIEW` | Insufficient image count (99 images < 100 minimum threshold). |
| `DRAVYA_0106` | Clitoria ternatea (Butterfly Pea) | 98 | `NEEDS_REVIEW` | Insufficient image count (98 images < 100 minimum threshold). |
| `DRAVYA_0107` | Unresolved Kasambruga Leaf | 96 | `NEEDS_REVIEW` | Taxonomy conflict or unresolved vernacular name requiring expert review. |
| `DRAVYA_0108` | Onion | 92 | `NEEDS_REVIEW` | Insufficient image count (92 images < 100 minimum threshold). |
| `DRAVYA_0109` | Pumpkin | 92 | `NEEDS_REVIEW` | Insufficient image count (92 images < 100 minimum threshold). |
| `DRAVYA_0110` | Onion-Allium Cepa | 92 | `NEEDS_REVIEW` | Insufficient image count (92 images < 100 minimum threshold). |
| `DRAVYA_0111` | Pumpkin-Cucurbita Pepo | 92 | `NEEDS_REVIEW` | Insufficient image count (92 images < 100 minimum threshold). |
| `DRAVYA_0112` | Nelavembu | 90 | `NEEDS_REVIEW` | Insufficient image count (90 images < 100 minimum threshold). |
| `DRAVYA_0113` | Nelavembu-Andrographis Paniculata | 90 | `NEEDS_REVIEW` | Insufficient image count (90 images < 100 minimum threshold). |
| `DRAVYA_0114` | Amaranthus tricolor (Red Amaranth) | 89 | `NEEDS_REVIEW` | Insufficient image count (89 images < 100 minimum threshold). |
| `DRAVYA_0115` | Acalypha reptans (Dwarf Copperleaf) | 88 | `NEEDS_REVIEW` | Insufficient image count (88 images < 100 minimum threshold). |
| `DRAVYA_0116` | Hemidesmus indicus (Anantamul) | 84 | `NEEDS_REVIEW` | Insufficient image count (84 images < 100 minimum threshold). |
| `DRAVYA_0117` | Lagos Spinach_Celosia Argentea | 84 | `NEEDS_REVIEW` | Insufficient image count (84 images < 100 minimum threshold). |
| `DRAVYA_0118` | Celery_Apium Graveolens | 82 | `NEEDS_REVIEW` | Insufficient image count (82 images < 100 minimum threshold). |
| `DRAVYA_0119` | Jatropha gossypiifolia (Bellyache Bush) | 81 | `NEEDS_REVIEW` | Insufficient image count (81 images < 100 minimum threshold). |
| `DRAVYA_0120` | Mustard_Brassica Juncea | 80 | `NEEDS_REVIEW` | Insufficient image count (80 images < 100 minimum threshold). |
| `DRAVYA_0121` | Malabar_Spinach | 79 | `NEEDS_REVIEW` | Insufficient image count (79 images < 100 minimum threshold). |
| `DRAVYA_0122` | Acalypha wilkesiana (Red Copperleaf) | 79 | `NEEDS_REVIEW` | Insufficient image count (79 images < 100 minimum threshold). |
| `DRAVYA_0123` | Curcuma longa (Turmeric) | 78 | `NEEDS_REVIEW` | Insufficient image count (78 images < 100 minimum threshold). |
| `DRAVYA_0124` | Mountain Knotgrass_Aerva Lanata | 78 | `NEEDS_REVIEW` | Insufficient image count (78 images < 100 minimum threshold). |
| `DRAVYA_0125` | Punarnava_Boerhavia Diffusa | 76 | `NEEDS_REVIEW` | Insufficient image count (76 images < 100 minimum threshold). |
| `DRAVYA_0126` | Pomoegranate | 75 | `NEEDS_REVIEW` | Insufficient image count (75 images < 100 minimum threshold). |
| `DRAVYA_0127` | Acorus calamus (Vacha/Sweet Flag) | 75 | `NEEDS_REVIEW` | Insufficient image count (75 images < 100 minimum threshold). |
| `DRAVYA_0128` | Carissa carandas (Karanda) | 74 | `NEEDS_REVIEW` | Insufficient image count (74 images < 100 minimum threshold). |
| `DRAVYA_0129` | Nalta Jute_Corchorus Olitorius | 73 | `NEEDS_REVIEW` | Insufficient image count (73 images < 100 minimum threshold). |
| `DRAVYA_0130` | Mucuna pruriens (Kaunch/Velvet Bean) | 72 | `NEEDS_REVIEW` | Insufficient image count (72 images < 100 minimum threshold). |
| `DRAVYA_0131` | Purple Fruited Pea Eggplant_Solanum Trilobatum | 70 | `NEEDS_REVIEW` | Insufficient image count (70 images < 100 minimum threshold). |
| `DRAVYA_0132` | Abutilon indicum (Country Mallow) | 69 | `NEEDS_REVIEW` | Insufficient image count (69 images < 100 minimum threshold). |
| `DRAVYA_0133` | Andrographis paniculata (Kalmegh/Green Chireta) | 69 | `NEEDS_REVIEW` | Insufficient image count (69 images < 100 minimum threshold). |
| `DRAVYA_0134` | Lambs Quarters_Chenopodium Album | 69 | `NEEDS_REVIEW` | Insufficient image count (69 images < 100 minimum threshold). |
| `DRAVYA_0135` | Panicled Foldwing_Dicliptera Paniculata | 68 | `NEEDS_REVIEW` | Insufficient image count (68 images < 100 minimum threshold). |
| `DRAVYA_0136` | Amaranthus tristis (Siru Keerai) | 68 | `NEEDS_REVIEW` | Insufficient image count (68 images < 100 minimum threshold). |
| `DRAVYA_0137` | Artemisia indica (Indian Wormwood) | 67 | `NEEDS_REVIEW` | Insufficient image count (67 images < 100 minimum threshold). |
| `DRAVYA_0138` | Parijatha | 66 | `NEEDS_REVIEW` | Insufficient image count (66 images < 100 minimum threshold). |
| `DRAVYA_0139` | Senna auriculata (Avaram) | 66 | `NEEDS_REVIEW` | Insufficient image count (66 images < 100 minimum threshold). |
| `DRAVYA_0140` | Cissus quadrangularis (Hadjod) | 66 | `NEEDS_REVIEW` | Insufficient image count (66 images < 100 minimum threshold). |
| `DRAVYA_0141` | Ziziphus mauritiana (Indian Jujube/Ber) | 66 | `NEEDS_REVIEW` | Insufficient image count (66 images < 100 minimum threshold). |
| `DRAVYA_0142` | Rosary Pea_Abrus Precatorius | 66 | `NEEDS_REVIEW` | Insufficient image count (66 images < 100 minimum threshold). |
| `DRAVYA_0143` | Passiflora foetida (Stinking Passionflower) | 66 | `NEEDS_REVIEW` | Insufficient image count (66 images < 100 minimum threshold). |
| `DRAVYA_0144` | Diodia teres (Shaggy Button Weed) | 65 | `NEEDS_REVIEW` | Insufficient image count (65 images < 100 minimum threshold). |
| `DRAVYA_0145` | Centella asiatica (Gotu Kola/Indian Pennywort) | 64 | `NEEDS_REVIEW` | Insufficient image count (64 images < 100 minimum threshold). |
| `DRAVYA_0146` | Lettuce Tree_Pisonia Grandis | 64 | `NEEDS_REVIEW` | Insufficient image count (64 images < 100 minimum threshold). |
| `DRAVYA_0147` | Land Caltrops (Bindii)_Tribulus Cistoides | 63 | `NEEDS_REVIEW` | Insufficient image count (63 images < 100 minimum threshold). |
| `DRAVYA_0148` | Peepal Tree_Ficus Religiosa | 63 | `NEEDS_REVIEW` | Insufficient image count (63 images < 100 minimum threshold). |
| `DRAVYA_0149` | Oleander_Nerium Oleander | 62 | `NEEDS_REVIEW` | Insufficient image count (62 images < 100 minimum threshold). |
| `DRAVYA_0150` | Amaranthus dubius (Chinese Spinach) | 60 | `NEEDS_REVIEW` | Insufficient image count (60 images < 100 minimum threshold). |
| `DRAVYA_0151` | Tridax procumbens (Coatbuttons) | 60 | `NEEDS_REVIEW` | Insufficient image count (60 images < 100 minimum threshold). |
| `DRAVYA_0152` | Sida rhombifolia (Common Wireweed) | 60 | `NEEDS_REVIEW` | Insufficient image count (60 images < 100 minimum threshold). |
| `DRAVYA_0153` | Kokilaksha_Asteracantha Longifolia | 59 | `NEEDS_REVIEW` | Insufficient image count (59 images < 100 minimum threshold). |
| `DRAVYA_0154` | Purple Tephrosia_Tephrosia Purpurea | 59 | `NEEDS_REVIEW` | Insufficient image count (59 images < 100 minimum threshold). |
| `DRAVYA_0155` | Commelina benghalensis (Dayflower) | 58 | `NEEDS_REVIEW` | Insufficient image count (58 images < 100 minimum threshold). |
| `DRAVYA_0156` | Santalum album (Sandalwood) | 58 | `NEEDS_REVIEW` | Insufficient image count (58 images < 100 minimum threshold). |
| `DRAVYA_0157` | Datura metel (Indian Thornapple) | 57 | `NEEDS_REVIEW` | Insufficient image count (57 images < 100 minimum threshold). |
| `DRAVYA_0158` | Marsilea minuta (Water Clover) | 57 | `NEEDS_REVIEW` | Insufficient image count (57 images < 100 minimum threshold). |
| `DRAVYA_0159` | Cissus sicyoides (Trellis Vine) | 57 | `NEEDS_REVIEW` | Insufficient image count (57 images < 100 minimum threshold). |
| `DRAVYA_0160` | Tabernaemontana divaricata (Crape Jasmine) | 56 | `NEEDS_REVIEW` | Insufficient image count (56 images < 100 minimum threshold). |
| `DRAVYA_0161` | Muntingia calabura (Jamaica Cherry) | 56 | `NEEDS_REVIEW` | Insufficient image count (56 images < 100 minimum threshold). |
| `DRAVYA_0162` | Syzygium jambos (Rose Apple) | 56 | `NEEDS_REVIEW` | Insufficient image count (56 images < 100 minimum threshold). |
| `DRAVYA_0163` | Mexican Prickly Poppy_Argemone Mexicana | 55 | `NEEDS_REVIEW` | Insufficient image count (55 images < 100 minimum threshold). |
| `DRAVYA_0164` | Cleome viscosa (Spiderwisp) | 55 | `NEEDS_REVIEW` | Insufficient image count (55 images < 100 minimum threshold). |
| `DRAVYA_0165` | Ipomoea aquatica (Water Spinach) | 55 | `NEEDS_REVIEW` | Insufficient image count (55 images < 100 minimum threshold). |
| `DRAVYA_0166` | Night Blooming Cereus_Epiphyllum Oxypetalum | 54 | `NEEDS_REVIEW` | Insufficient image count (54 images < 100 minimum threshold). |
| `DRAVYA_0167` | Prickly Chaff Flower_Achyranthes Aspera | 54 | `NEEDS_REVIEW` | Insufficient image count (54 images < 100 minimum threshold). |
| `DRAVYA_0168` | Hibiscus sabdariffa (Roselle/Gongura) | 53 | `NEEDS_REVIEW` | Insufficient image count (53 images < 100 minimum threshold). |
| `DRAVYA_0169` | Madras Pea Pumpkin_Sesbania Grandiflora | 53 | `NEEDS_REVIEW` | Insufficient image count (53 images < 100 minimum threshold). |
| `DRAVYA_0170` | Senna alexandrina (Tinnevelly Senna) | 53 | `NEEDS_REVIEW` | Insufficient image count (53 images < 100 minimum threshold). |
| `DRAVYA_0171` | Malabar_Nut | 51 | `NEEDS_REVIEW` | Insufficient image count (51 images < 100 minimum threshold). |
| `DRAVYA_0172` | Coccinia grandis (Ivy Gourd) | 51 | `NEEDS_REVIEW` | Insufficient image count (51 images < 100 minimum threshold). |
| `DRAVYA_0173` | Malabar_Nut-Justicia Adhatoda | 51 | `NEEDS_REVIEW` | Insufficient image count (51 images < 100 minimum threshold). |
| `DRAVYA_0174` | Rasna_Alpinia Galanga | 50 | `NEEDS_REVIEW` | Insufficient image count (50 images < 100 minimum threshold). |
| `DRAVYA_0175` | Ficus auriculata (Roxburgh Fig) | 50 | `NEEDS_REVIEW` | Insufficient image count (50 images < 100 minimum threshold). |
| `DRAVYA_0176` | Pea-Pisum Sativum | 47 | `NEEDS_REVIEW` | Insufficient image count (47 images < 100 minimum threshold). |
| `DRAVYA_0177` | Raddish | 40 | `NEEDS_REVIEW` | Insufficient image count (40 images < 100 minimum threshold). |
| `DRAVYA_0178` | Raddish-Raphanus Sativus | 40 | `NEEDS_REVIEW` | Insufficient image count (40 images < 100 minimum threshold). |
| `DRAVYA_0179` | Syzygium cumini (Jamun) | 39 | `NEEDS_REVIEW` | Insufficient image count (39 images < 100 minimum threshold). |
| `DRAVYA_0180` | Unspecified Leaf Samples | 11 | `REJECTED` | Non-plant / corrupt junk images folder. |

---

## Taxonomy Conflicts Analysis & Recommendations (11 Conflicts)

| Conflict ID | Raw Class / Source | Candidate Species | Images | Classification | Recommended Action |
|---|---|---|---|---|---|
| `CONF_001` | `Beans-Vigna spp. (Genus) or Phaseolus spp. (Genus) / Beans` (Hugging_Face, Kaggle) | Vigna / Phaseolus spp. (Beans) | 194 | `DO_NOT_MERGE` | Exclude from v1 model until images are separated by genus via expert botanical review. |
| `CONF_002` | `Spinach1` (Hugging_Face, Kaggle) | Unspecified Spinach Variety | 180 | `NEEDS_HUMAN_REVIEW` | Hold in review queue; exclude from initial production model. |
| `CONF_003` | `leafs` (CIMPd) | Unspecified Leaf Samples | 11 | `DO_NOT_MERGE` | Reject permanently and exclude from all training manifests. |
| `CONF_004` | `Insulin` (Hugging_Face, Kaggle) | Chamaecostus cuspidatus (Insulin Plant) | 156 | `NEEDS_HUMAN_REVIEW` | Map to Chamaecostus cuspidatus upon expert botanical review confirmation. |
| `CONF_005` | `Caricature` (Hugging_Face, Kaggle) | Graptophyllum pictum (Caricature Plant) | 152 | `NEEDS_HUMAN_REVIEW` | Require botanical verification before canonical ID assignment. |
| `CONF_006` | `Badipala` (Hugging_Face, Kaggle) | Erythrina variegata (Badipala) | 152 | `NEEDS_HUMAN_REVIEW` | Hold in review queue; verify leaf morphology against Erythrina species. |
| `CONF_007` | `Chakte` (Hugging_Face, Kaggle) | Unresolved Chakte Leaf | 140 | `DO_NOT_MERGE` | Exclude from v1 model until taxonomic consensus is achieved. |
| `CONF_008` | `Ganigale` (Hugging_Face, Kaggle) | Unresolved Ganigale Leaf | 150 | `DO_NOT_MERGE` | Exclude from v1 dataset build. |
| `CONF_009` | `Kambajala` (Hugging_Face, Kaggle) | Unresolved Kambajala Leaf | 142 | `DO_NOT_MERGE` | Exclude from v1 dataset build. |
| `CONF_010` | `Kasambruga` (Hugging_Face, Kaggle) | Unresolved Kasambruga Leaf | 148 | `DO_NOT_MERGE` | Exclude from v1 dataset build. |
| `CONF_011` | `Kepala` (Hugging_Face, Kaggle) | Unresolved Kepala Leaf | 144 | `DO_NOT_MERGE` | Exclude from v1 dataset build. |

---

## Class Image Imbalance Statistics (Approved Classes)

| Metric | Value |
|---|---|
| **Minimum Class Images** | 101 |
| **Maximum Class Images** | 1,397 |
| **Mean Class Images** | 374.95 |
| **Median Class Images** | 288.0 |
| **Overall Class Imbalance Ratio** | **13.83:1** |

---

## Read-Only Safety Affirmation
- Raw dataset folders (`CIMPd`, `Hugging_Face`, `Kaggle`) remain 100% untouched.
- Zero images copied or transformed.
- Existing model, API, and training code unchanged.