import os
import sys
import json
import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple

try:
    from PIL import Image
except ImportError:
    Image = None

from src.data.paths import (
    get_dataset_paths,
    get_reports_dir,
    SUPPORTED_IMAGE_EXTENSIONS,
)
from src.data.deduplication import ExactDuplicateDetector


def normalize_string(s: str) -> str:
    """Normalize string by lowercasing, removing extra whitespace, and standardizing separators."""
    if not s:
        return ""
    cleaned = s.lower().replace("_", " ").replace("-", " ").replace(".", " ").replace(",", " ")
    return " ".join(cleaned.split())


def parse_raw_class_info(dataset_id: str, raw_class_name: str) -> Dict[str, Any]:
    """
    Parses raw dataset folder name into leaf folder, health condition, and candidate names.
    """
    normalized_path_str = raw_class_name.replace("/", os.sep).replace("\\", os.sep)
    leaf_folder_name = os.path.basename(normalized_path_str)

    health_condition = "Unknown"
    plant_name_raw = leaf_folder_name

    # Handle CIMPd health condition suffixes
    if dataset_id == "CIMPd" or leaf_folder_name.endswith(".H") or leaf_folder_name.endswith(".U") or leaf_folder_name.endswith(",U"):
        if leaf_folder_name.endswith(".H"):
            health_condition = "Healthy"
            plant_name_raw = leaf_folder_name[:-2]
        elif leaf_folder_name.endswith(".U") or leaf_folder_name.endswith(",U"):
            health_condition = "Unhealthy"
            plant_name_raw = leaf_folder_name[:-2]

    # Handle Kaggle nested folder prefix if present
    if plant_name_raw.startswith("Medicinal Leaf dataset\\") or plant_name_raw.startswith("Medicinal Leaf dataset/"):
        plant_name_raw = plant_name_raw.split("\\")[-1].split("/")[-1]
    if plant_name_raw.startswith("Medicinal plant dataset\\") or plant_name_raw.startswith("Medicinal plant dataset/"):
        plant_name_raw = plant_name_raw.split("\\")[-1].split("/")[-1]

    common_name_candidate = plant_name_raw
    scientific_name_candidate = None

    # Try extracting binomial scientific name
    for sep in ["_", "-", ":"]:
        if sep in plant_name_raw:
            parts = [p.strip() for p in plant_name_raw.split(sep) if p.strip()]
            if len(parts) >= 2:
                for idx in range(1, len(parts)):
                    words = parts[idx].split()
                    if len(words) >= 2 and words[0][0].isupper():
                        common_name_candidate = " ".join(parts[:idx])
                        scientific_name_candidate = " ".join(words[:2])
                        break

    return {
        "dataset_id": dataset_id,
        "raw_class_name": raw_class_name,
        "leaf_folder_name": leaf_folder_name,
        "plant_name_raw": plant_name_raw,
        "health_condition": health_condition,
        "common_name_candidate": common_name_candidate,
        "scientific_name_candidate": scientific_name_candidate,
        "normalized_name": normalize_string(plant_name_raw),
    }


class CombinedInventoryAnalyzer:
    """
    Combined Dataset Species Inventory & Feasibility Analyzer (v2) for Dravya AI.
    Executes Phases 1, 2, 3, and 4 while strictly treating raw dataset files as read-only.
    """

    def __init__(self, dataset_paths: Optional[Dict[str, Path]] = None, reports_dir: Optional[Path] = None):
        self.dataset_paths = dataset_paths or get_dataset_paths()
        self.reports_dir = reports_dir or get_reports_dir()
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def run_phase1_inventory(self) -> Dict[str, Any]:
        """
        Phase 1: Individual & Combined Dataset Inventory Scan & Image Integrity Analysis.
        """
        per_dataset_results = {}
        total_raw_images = 0
        total_raw_files = 0
        total_corrupt_images = 0
        total_non_image_files = 0
        all_file_extensions: Dict[str, int] = {}
        all_raw_classes = set()

        for ds_id, root_path in self.dataset_paths.items():
            abs_root = Path(root_path).resolve()
            if not abs_root.exists():
                print(f"WARNING: Root path for {ds_id} not found: {abs_root}")
                continue

            ds_total_files = 0
            ds_total_images = 0
            ds_corrupt_images = 0
            ds_non_image_files = 0
            ds_extensions: Dict[str, int] = {}
            ds_class_counts: Dict[str, int] = {}
            ds_invalid_files: List[str] = []

            for dirpath, _, filenames in os.walk(abs_root):
                rel_dir = os.path.relpath(dirpath, abs_root)
                if rel_dir == ".":
                    continue

                class_name = rel_dir
                img_in_dir = 0

                for f in filenames:
                    ds_total_files += 1
                    ext = os.path.splitext(f)[1].lower()
                    rel_file_path = os.path.join(rel_dir, f)

                    if ext in SUPPORTED_IMAGE_EXTENSIONS:
                        ds_total_images += 1
                        img_in_dir += 1
                        ds_extensions[ext] = ds_extensions.get(ext, 0) + 1
                        all_file_extensions[ext] = all_file_extensions.get(ext, 0) + 1

                        # Image Readability / Corruption Check
                        abs_file = os.path.join(dirpath, f)
                        if Image:
                            try:
                                with Image.open(abs_file) as img:
                                    img.verify()
                            except Exception:
                                ds_corrupt_images += 1
                                ds_invalid_files.append(rel_file_path)
                    else:
                        ds_non_image_files += 1
                        ds_invalid_files.append(rel_file_path)

                if img_in_dir > 0:
                    ds_class_counts[class_name] = img_in_dir
                    all_raw_classes.add(f"{ds_id}::{class_name}")

            per_dataset_results[ds_id] = {
                "dataset_id": ds_id,
                "root_path": str(abs_root),
                "total_files": ds_total_files,
                "total_images": ds_total_images,
                "total_classes": len(ds_class_counts),
                "corrupt_images_count": ds_corrupt_images,
                "non_image_files_count": ds_non_image_files,
                "file_extensions": ds_extensions,
                "class_image_counts": ds_class_counts,
                "invalid_or_non_image_files": ds_invalid_files,
            }

            total_raw_images += ds_total_images
            total_raw_files += ds_total_files
            total_corrupt_images += ds_corrupt_images
            total_non_image_files += ds_non_image_files

        # Run SHA-256 Deduplication Scan safely
        duplicate_results = {}
        try:
            detector = ExactDuplicateDetector({ds: str(p) for ds, p in self.dataset_paths.items() if p.exists()})
            duplicate_results = detector.scan()
        except Exception as e:
            print(f"Warning: Exact duplicate detection encountered an issue: {e}")
            duplicate_results = {
                "total_duplicate_files": 0,
                "within_dataset_duplicate_files_count": 0,
                "cross_dataset_duplicate_files_count": 0,
                "duplicate_groups_count": 0,
            }

        return {
            "per_dataset": per_dataset_results,
            "combined_totals": {
                "total_raw_files": total_raw_files,
                "total_raw_images": total_raw_images,
                "total_raw_classes": len(all_raw_classes),
                "total_corrupt_images": total_corrupt_images,
                "total_non_image_files": total_non_image_files,
                "file_extensions": all_file_extensions,
                "duplicate_summary": {
                    "total_exact_duplicates": duplicate_results.get("total_duplicate_files", 0),
                    "within_dataset_duplicates": duplicate_results.get("within_dataset_duplicate_files_count", 0),
                    "cross_dataset_duplicates": duplicate_results.get("cross_dataset_duplicate_files_count", 0),
                    "duplicate_groups_count": duplicate_results.get("duplicate_groups_count", 0),
                },
            },
        }

    def run_phase2_harmonization(self, phase1_data: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Phase 2: Taxonomy Harmonization Analysis & Candidate Species Mapping.
        """
        parsed_classes: List[Dict[str, Any]] = []

        for ds_id, ds_info in phase1_data["per_dataset"].items():
            class_counts = ds_info["class_image_counts"]
            for raw_class, img_count in class_counts.items():
                parsed = parse_raw_class_info(ds_id, raw_class)
                parsed["image_count"] = img_count
                parsed_classes.append(parsed)

        # Botanical & Vernacular Taxonomy Mapping Dictionary
        # Maps normalized string patterns -> (Canonical Species Name, Scientific Name, Taxon Category, Status)
        taxonomy_dictionary = {
            # Aloevera / Aloe barbadensis
            "aloevera": ("Aloe vera", "Aloe barbadensis", "Succulent", "APPROVED_HARMONIZED"),
            "aloevera aloe barbadensis": ("Aloe vera", "Aloe barbadensis", "Succulent", "APPROVED_HARMONIZED"),
            # Amaranthus species
            "amaranthus green amaranthus viridis": ("Amaranthus viridis (Green Amaranth)", "Amaranthus viridis", "Leafy Herb", "APPROVED_HARMONIZED"),
            "arive dantu amaranthus viridis": ("Amaranthus viridis (Green Amaranth)", "Amaranthus viridis", "Leafy Herb", "APPROVED_HARMONIZED"),
            "amaranthus red amaranthus tricolor": ("Amaranthus tricolor (Red Amaranth)", "Amaranthus tricolor", "Leafy Herb", "APPROVED_HARMONIZED"),
            "chinese spinach amaranthus dubius": ("Amaranthus dubius (Chinese Spinach)", "Amaranthus dubius", "Leafy Herb", "APPROVED_HARMONIZED"),
            "giant pigweed amaranthus titan": ("Amaranthus titan (Giant Pigweed)", "Amaranthus titan", "Herb", "APPROVED_HARMONIZED"),
            "siru keerai amaranthus tristis": ("Amaranthus tristis (Siru Keerai)", "Amaranthus tristis", "Leafy Herb", "APPROVED_HARMONIZED"),
            # Amla / Phyllanthus emblica
            "amla": ("Phyllanthus emblica (Amla)", "Phyllanthus emblica", "Tree", "APPROVED_HARMONIZED"),
            "amla phyllanthus emlica linn": ("Phyllanthus emblica (Amla)", "Phyllanthus emblica", "Tree", "APPROVED_HARMONIZED"),
            # Amruthaballi / Giloy / Tinospora cordifolia
            "amruthaballi": ("Tinospora cordifolia (Giloy/Amrita)", "Tinospora cordifolia", "Climbing Shrub", "APPROVED_HARMONIZED"),
            "amruta balli tinospora cordifolia": ("Tinospora cordifolia (Giloy/Amrita)", "Tinospora cordifolia", "Climbing Shrub", "APPROVED_HARMONIZED"),
            "heart leaved moonseed tinospora cordifolia": ("Tinospora cordifolia (Giloy/Amrita)", "Tinospora cordifolia", "Climbing Shrub", "APPROVED_HARMONIZED"),
            # Arali / Nerium oleander
            "arali": ("Nerium oleander (Oleander)", "Nerium oleander", "Shrub", "APPROVED_HARMONIZED"),
            "arali nerium oleander": ("Nerium oleander (Oleander)", "Nerium oleander", "Shrub", "APPROVED_HARMONIZED"),
            # Ashok / Saraca asoca
            "ashok": ("Saraca asoca (Ashoka)", "Saraca asoca", "Tree", "APPROVED_HARMONIZED"),
            "ashoka": ("Saraca asoca (Ashoka)", "Saraca asoca", "Tree", "APPROVED_HARMONIZED"),
            "ashoka saraca asoca": ("Saraca asoca (Ashoka)", "Saraca asoca", "Tree", "APPROVED_HARMONIZED"),
            "seethaashoka saraca asoca": ("Saraca asoca (Ashoka)", "Saraca asoca", "Tree", "APPROVED_HARMONIZED"),
            "seethaashoka": ("Saraca asoca (Ashoka)", "Saraca asoca", "Tree", "APPROVED_HARMONIZED"),
            # Ashwagandha / Withania somnifera
            "ashwagandha": ("Withania somnifera (Ashwagandha)", "Withania somnifera", "Herb", "APPROVED_HARMONIZED"),
            "ashwagandha withania somnifera": ("Withania somnifera (Ashwagandha)", "Withania somnifera", "Herb", "APPROVED_HARMONIZED"),
            # Asthma plant / Euphorbia hirta
            "astma weed": ("Euphorbia hirta (Asthma Weed)", "Euphorbia hirta", "Herb", "APPROVED_HARMONIZED"),
            "asthma plant euphorbia hirta": ("Euphorbia hirta (Asthma Weed)", "Euphorbia hirta", "Herb", "APPROVED_HARMONIZED"),
            # Avocado / Persea americana
            "avacado persea americana": ("Persea americana (Avocado)", "Persea americana", "Tree", "APPROVED_HARMONIZED"),
            # Avaram / Senna auriculata
            "avaram senna auriculata": ("Senna auriculata (Avaram)", "Senna auriculata", "Shrub", "APPROVED_HARMONIZED"),
            # Balloon Vine / Cardiospermum halicacabum
            "balloon vine": ("Cardiospermum halicacabum (Balloon Vine)", "Cardiospermum halicacabum", "Climber", "APPROVED_HARMONIZED"),
            "balloon vine cardiospermum halicacabum": ("Cardiospermum halicacabum (Balloon Vine)", "Cardiospermum halicacabum", "Climber", "APPROVED_HARMONIZED"),
            "cardiospermum halicacabum": ("Cardiospermum halicacabum (Balloon Vine)", "Cardiospermum halicacabum", "Climber", "APPROVED_HARMONIZED"),
            # Bamboo
            "bamboo": ("Bambusoideae (Bamboo)", "Bambusoideae", "Grass/Tree", "APPROVED_HARMONIZED"),
            "bamboo bambusoideae": ("Bambusoideae (Bamboo)", "Bambusoideae", "Grass/Tree", "APPROVED_HARMONIZED"),
            # Barleria
            "barlaria": ("Barleria (Barlaria)", "Barleria spp.", "Shrub", "APPROVED_HARMONIZED"),
            # Basale / Basella alba
            "basale basella alba": ("Basella alba (Malabar Spinach)", "Basella alba", "Climbing Vine", "APPROVED_HARMONIZED"),
            # Bel / Bael / Aegle marmelos
            "bel": ("Aegle marmelos (Bael)", "Aegle marmelos", "Tree", "APPROVED_HARMONIZED"),
            # Betel / Piper betle
            "betel": ("Piper betle (Betel Leaf)", "Piper betle", "Vine", "APPROVED_HARMONIZED"),
            "betel piper betle": ("Piper betle (Betel Leaf)", "Piper betle", "Vine", "APPROVED_HARMONIZED"),
            "betel nut areca catechu": ("Areca catechu (Betel Nut)", "Areca catechu", "Palm Tree", "APPROVED_HARMONIZED"),
            # Brahmi / Bacopa monnieri
            "bhrami": ("Bacopa monnieri (Brahmi)", "Bacopa monnieri", "Herb", "APPROVED_HARMONIZED"),
            "brahmi bacopa monnieri": ("Bacopa monnieri (Brahmi)", "Bacopa monnieri", "Herb", "APPROVED_HARMONIZED"),
            # Bhringraj / Eclipta prostrata
            "bringaraja": ("Eclipta prostrata (Bhringraj)", "Eclipta prostrata", "Herb", "APPROVED_HARMONIZED"),
            "bringaraja eclipta prostrata": ("Eclipta prostrata (Bhringraj)", "Eclipta prostrata", "Herb", "APPROVED_HARMONIZED"),
            # Butterfly Pea / Clitoria ternatea
            "butterfly pea clitoria ternatea": ("Clitoria ternatea (Butterfly Pea)", "Clitoria ternatea", "Vine", "APPROVED_HARMONIZED"),
            # Castor / Ricinus communis
            "castor": ("Ricinus communis (Castor)", "Ricinus communis", "Shrub/Tree", "APPROVED_HARMONIZED"),
            "castor ricinus communis": ("Ricinus communis (Castor)", "Ricinus communis", "Shrub/Tree", "APPROVED_HARMONIZED"),
            # Catharanthus roseus / Sadabahar
            "catharanthus": ("Catharanthus roseus (Sadabahar)", "Catharanthus roseus", "Shrub", "APPROVED_HARMONIZED"),
            # Chilly / Capsicum spp
            "chilly": ("Capsicum spp. (Chilli)", "Capsicum spp.", "Herb", "APPROVED_HARMONIZED"),
            "chilly capsicum spp (genus)": ("Capsicum spp. (Chilli)", "Capsicum spp.", "Herb", "APPROVED_HARMONIZED"),
            # Clerodendrum splendens
            "clerodendrum splendens": ("Clerodendrum splendens", "Clerodendrum splendens", "Vine", "APPROVED_HARMONIZED"),
            # Coffee / Coffea spp
            "coffee": ("Coffea spp. (Coffee)", "Coffea spp.", "Shrub", "APPROVED_HARMONIZED"),
            "coffee coffea spp (genus)": ("Coffea spp. (Coffee)", "Coffea spp.", "Shrub", "APPROVED_HARMONIZED"),
            # Coriander / Coriandrum sativum
            "coriender": ("Coriandrum sativum (Coriander)", "Coriandrum sativum", "Herb", "APPROVED_HARMONIZED"),
            "coriander coriandrum sativum": ("Coriandrum sativum (Coriander)", "Coriandrum sativum", "Herb", "APPROVED_HARMONIZED"),
            # Curry Leaf / Murraya koenigii
            "curry": ("Murraya koenigii (Curry Leaf)", "Murraya koenigii", "Tree", "APPROVED_HARMONIZED"),
            "curry leaf": ("Murraya koenigii (Curry Leaf)", "Murraya koenigii", "Tree", "APPROVED_HARMONIZED"),
            "curry leaf murraya koenigii": ("Murraya koenigii (Curry Leaf)", "Murraya koenigii", "Tree", "APPROVED_HARMONIZED"),
            # Custard Apple / Annona squamosa
            "custardapple": ("Annona squamosa (Custard Apple)", "Annona squamosa", "Tree", "APPROVED_HARMONIZED"),
            "custard apple": ("Annona squamosa (Custard Apple)", "Annona squamosa", "Tree", "APPROVED_HARMONIZED"),
            # Doddapatre / Plectranthus amboinicus / Indian Borage
            "doddpathre": ("Plectranthus amboinicus (Doddapatre/Indian Borage)", "Plectranthus amboinicus", "Herb", "APPROVED_HARMONIZED"),
            "doddapatre plectanthus amboinicus": ("Plectranthus amboinicus (Doddapatre/Indian Borage)", "Plectranthus amboinicus", "Herb", "APPROVED_HARMONIZED"),
            # Drumstick / Moringa oleifera
            "drumstick": ("Moringa oleifera (Drumstick/Moringa)", "Moringa oleifera", "Tree", "APPROVED_HARMONIZED"),
            "drumstick moringa oleifera": ("Moringa oleifera (Drumstick/Moringa)", "Moringa oleifera", "Tree", "APPROVED_HARMONIZED"),
            # Ekka / Calotropis gigantea
            "ekka": ("Calotropis gigantea (Crown Flower/Ekka)", "Calotropis gigantea", "Shrub", "APPROVED_HARMONIZED"),
            "ekka calotropis gigantea": ("Calotropis gigantea (Crown Flower/Ekka)", "Calotropis gigantea", "Shrub", "APPROVED_HARMONIZED"),
            "crown flower calotropis gigantea": ("Calotropis gigantea (Crown Flower/Ekka)", "Calotropis gigantea", "Shrub", "APPROVED_HARMONIZED"),
            # Eucalyptus
            "eucalyptus": ("Eucalyptus spp. (Eucalyptus)", "Eucalyptus spp.", "Tree", "APPROVED_HARMONIZED"),
            "eucalyptus eucalyptus spp (genus)": ("Eucalyptus spp. (Eucalyptus)", "Eucalyptus spp.", "Tree", "APPROVED_HARMONIZED"),
            # Ginger / Zingiber officinale
            "ginger": ("Zingiber officinale (Ginger)", "Zingiber officinale", "Herb", "APPROVED_HARMONIZED"),
            "ginger zingiber officinale": ("Zingiber officinale (Ginger)", "Zingiber officinale", "Herb", "APPROVED_HARMONIZED"),
            # Globe Amaranth / Gomphrena globosa
            "globe amarnath": ("Gomphrena globosa (Globe Amaranth)", "Gomphrena globosa", "Herb", "APPROVED_HARMONIZED"),
            "globe amarnath gomphrena globosa": ("Gomphrena globosa (Globe Amaranth)", "Gomphrena globosa", "Herb", "APPROVED_HARMONIZED"),
            # Guava / Psidium guajava
            "guava": ("Psidium guajava (Guava)", "Psidium guajava", "Tree", "APPROVED_HARMONIZED"),
            "gauva psidium guajava": ("Psidium guajava (Guava)", "Psidium guajava", "Tree", "APPROVED_HARMONIZED"),
            # Harshingar / Parijat / Nyctanthes arbor-tristis
            "harsingar": ("Nyctanthes arbor-tristis (Harsingar/Parijat)", "Nyctanthes arbor-tristis", "Tree", "APPROVED_HARMONIZED"),
            "harshingar": ("Nyctanthes arbor-tristis (Harsingar/Parijat)", "Nyctanthes arbor-tristis", "Tree", "APPROVED_HARMONIZED"),
            # Henna / Lawsonia inermis
            "henna": ("Lawsonia inermis (Henna)", "Lawsonia inermis", "Shrub", "APPROVED_HARMONIZED"),
            "henna lausonia inermis": ("Lawsonia inermis (Henna)", "Lawsonia inermis", "Shrub", "APPROVED_HARMONIZED"),
            # Hibiscus / Hibiscus rosa-sinensis
            "hibiscus": ("Hibiscus rosa-sinensis (Hibiscus)", "Hibiscus rosa-sinensis", "Shrub", "APPROVED_HARMONIZED"),
            "hibiscus hibiscus rosa sinensis": ("Hibiscus rosa-sinensis (Hibiscus)", "Hibiscus rosa-sinensis", "Shrub", "APPROVED_HARMONIZED"),
            # Honge / Pongamia pinnata / Milletia pinnata
            "honge": ("Pongamia pinnata (Honge/Karanja)", "Pongamia pinnata", "Tree", "APPROVED_HARMONIZED"),
            "honge milletia": ("Pongamia pinnata (Honge/Karanja)", "Pongamia pinnata", "Tree", "APPROVED_HARMONIZED"),
            "indian beech pongamia pinnata": ("Pongamia pinnata (Honge/Karanja)", "Pongamia pinnata", "Tree", "APPROVED_HARMONIZED"),
            # Jackfruit / Artocarpus heterophyllus
            "jackfruit": ("Artocarpus heterophyllus (Jackfruit)", "Artocarpus heterophyllus", "Tree", "APPROVED_HARMONIZED"),
            "jack fruit": ("Artocarpus heterophyllus (Jackfruit)", "Artocarpus heterophyllus", "Tree", "APPROVED_HARMONIZED"),
            "jackfruit artocarpus heterophyllus": ("Artocarpus heterophyllus (Jackfruit)", "Artocarpus heterophyllus", "Tree", "APPROVED_HARMONIZED"),
            # Jasmine / Jasminum spp
            "jasmine": ("Jasminum spp. (Jasmine)", "Jasminum spp.", "Shrub/Vine", "APPROVED_HARMONIZED"),
            "jasmine jasmium": ("Jasminum spp. (Jasmine)", "Jasminum spp.", "Shrub/Vine", "APPROVED_HARMONIZED"),
            "crape jasmine tabernaemontana divaricata": ("Tabernaemontana divaricata (Crape Jasmine)", "Tabernaemontana divaricata", "Shrub", "APPROVED_HARMONIZED"),
            # Kachnar / Bauhinia variegata
            "kachnar": ("Bauhinia variegata (Kachnar)", "Bauhinia variegata", "Tree", "APPROVED_HARMONIZED"),
            # Lantana / Lantana camara
            "lantana": ("Lantana camara (Lantana)", "Lantana camara", "Shrub", "APPROVED_HARMONIZED"),
            "lantana lantana camara": ("Lantana camara (Lantana)", "Lantana camara", "Shrub", "APPROVED_HARMONIZED"),
            # Lemon / Citrus limon
            "lemon": ("Citrus limon (Lemon)", "Citrus limon", "Tree", "APPROVED_HARMONIZED"),
            "lemon citrus limon": ("Citrus limon (Lemon)", "Citrus limon", "Tree", "APPROVED_HARMONIZED"),
            "lemon grass cymbopogon citratus": ("Cymbopogon citratus (Lemongrass)", "Cymbopogon citratus", "Grass", "APPROVED_HARMONIZED"),
            "lemon grass": ("Cymbopogon citratus (Lemongrass)", "Cymbopogon citratus", "Grass", "APPROVED_HARMONIZED"),
            "lemongrass": ("Cymbopogon citratus (Lemongrass)", "Cymbopogon citratus", "Grass", "APPROVED_HARMONIZED"),
            # Makoy / Solanum nigrum
            "makoy": ("Solanum nigrum (Makoy/Black Nightshade)", "Solanum nigrum", "Herb", "APPROVED_HARMONIZED"),
            "ganike solanum nigrum": ("Solanum nigrum (Makoy/Black Nightshade)", "Solanum nigrum", "Herb", "APPROVED_HARMONIZED"),
            # Marigold / Tagetes spp
            "marigold": ("Tagetes spp. (Marigold)", "Tagetes spp.", "Herb", "APPROVED_HARMONIZED"),
            "marigold tagetes spp (genus)": ("Tagetes spp. (Marigold)", "Tagetes spp.", "Herb", "APPROVED_HARMONIZED"),
            # Mint / Mentha spp
            "mint": ("Mentha spp. (Mint)", "Mentha spp.", "Herb", "APPROVED_HARMONIZED"),
            "mint mentha": ("Mentha spp. (Mint)", "Mentha spp.", "Herb", "APPROVED_HARMONIZED"),
            "mexican mint plectranthus amboinicus (also known as cuban oregano)": ("Plectranthus amboinicus (Doddapatre/Indian Borage)", "Plectranthus amboinicus", "Herb", "APPROVED_HARMONIZED"),
            "malabar catmint plectranthus amboinicus": ("Plectranthus amboinicus (Doddapatre/Indian Borage)", "Plectranthus amboinicus", "Herb", "APPROVED_HARMONIZED"),
            # Nasturtium / Tropaeolum majus
            "nasturtium": ("Tropaeolum majus (Nasturtium)", "Tropaeolum majus", "Herb", "APPROVED_HARMONIZED"),
            # Papaya / Carica papaya
            "papaya": ("Carica papaya (Papaya)", "Carica papaya", "Tree", "APPROVED_HARMONIZED"),
            # Rose / Rosa spp & Rose Apple
            "rose": ("Rosa spp. (Rose)", "Rosa spp.", "Shrub", "APPROVED_HARMONIZED"),
            "rose rosa": ("Rosa spp. (Rose)", "Rosa spp.", "Shrub", "APPROVED_HARMONIZED"),
            "rose1": ("Rosa spp. (Rose)", "Rosa spp.", "Shrub", "APPROVED_HARMONIZED"),
            "rose apple syzygium jambos": ("Syzygium jambos (Rose Apple)", "Syzygium jambos", "Tree", "APPROVED_HARMONIZED"),
            # Scarlet Sage / Salvia splendens
            "scarlet sage": ("Salvia splendens (Scarlet Sage)", "Salvia splendens", "Herb", "APPROVED_HARMONIZED"),
            # Tulsi / Ocimum sanctum / Ocimum tenuiflorum
            "tulsi": ("Ocimum sanctum (Holy Basil/Tulsi)", "Ocimum sanctum", "Herb", "APPROVED_HARMONIZED"),
            "tulasi": ("Ocimum sanctum (Holy Basil/Tulsi)", "Ocimum sanctum", "Herb", "APPROVED_HARMONIZED"),
            "holy basil ocimum sanctum": ("Ocimum sanctum (Holy Basil/Tulsi)", "Ocimum sanctum", "Herb", "APPROVED_HARMONIZED"),
            "tulasi ocimum sanctum ocimum sanctum (also known as holy basil)": ("Ocimum sanctum (Holy Basil/Tulsi)", "Ocimum sanctum", "Herb", "APPROVED_HARMONIZED"),
            "sweet basil ocimum basilicum": ("Ocimum basilicum (Sweet Basil)", "Ocimum basilicum", "Herb", "APPROVED_HARMONIZED"),
            # Mango / Mangifera indica
            "mango": ("Mangifera indica (Mango)", "Mangifera indica", "Tree", "APPROVED_HARMONIZED"),
            "mango mangifera indica": ("Mangifera indica (Mango)", "Mangifera indica", "Tree", "APPROVED_HARMONIZED"),
            # Neem / Azadirachta indica
            "neem": ("Azadirachta indica (Neem)", "Azadirachta indica", "Tree", "APPROVED_HARMONIZED"),
            "neem azadirachta indica": ("Azadirachta indica (Neem)", "Azadirachta indica", "Tree", "APPROVED_HARMONIZED"),
            # Noni / Morinda citrifolia
            "noni": ("Morinda citrifolia (Noni)", "Morinda citrifolia", "Tree", "APPROVED_HARMONIZED"),
            "noni morinda citrifolia": ("Morinda citrifolia (Noni)", "Morinda citrifolia", "Tree", "APPROVED_HARMONIZED"),
            # Parijata / Nyctanthes arbor-tristis
            "parijata": ("Nyctanthes arbor-tristis (Harsingar/Parijat)", "Nyctanthes arbor-tristis", "Tree", "APPROVED_HARMONIZED"),
            "parijata nyctanthes arbor tristis": ("Nyctanthes arbor-tristis (Harsingar/Parijat)", "Nyctanthes arbor-tristis", "Tree", "APPROVED_HARMONIZED"),
            # Peppermint / Mentha piperita
            "peppermint": ("Mentha piperita (Peppermint)", "Mentha piperita", "Herb", "APPROVED_HARMONIZED"),
            "peppermint mentha piperita": ("Mentha piperita (Peppermint)", "Mentha piperita", "Herb", "APPROVED_HARMONIZED"),
            # Pomegranate / Punica granatum
            "pomegranate": ("Punica granatum (Pomegranate)", "Punica granatum", "Shrub/Tree", "APPROVED_HARMONIZED"),
            "pomegranate punica granatum": ("Punica granatum (Pomegranate)", "Punica granatum", "Shrub/Tree", "APPROVED_HARMONIZED"),
            # Radish / Raphanus sativus
            "radish": ("Raphanus sativus (Radish)", "Raphanus sativus", "Herb", "APPROVED_HARMONIZED"),
            "radish raphanus sativus": ("Raphanus sativus (Radish)", "Raphanus sativus", "Herb", "APPROVED_HARMONIZED"),
            # Tamarind / Tamarindus indica
            "tamarind": ("Tamarindus indica (Tamarind)", "Tamarindus indica", "Tree", "APPROVED_HARMONIZED"),
            "tamarind tamarindus indica": ("Tamarindus indica (Tamarind)", "Tamarindus indica", "Tree", "APPROVED_HARMONIZED"),
            # Taro / Colocasia esculenta
            "taro colocasia esculenta": ("Colocasia esculenta (Taro)", "Colocasia esculenta", "Herb", "APPROVED_HARMONIZED"),
            # Turmeric / Curcuma longa
            "turmeric": ("Curcuma longa (Turmeric)", "Curcuma longa", "Herb", "APPROVED_HARMONIZED"),
            "turmeric curcuma longa": ("Curcuma longa (Turmeric)", "Curcuma longa", "Herb", "APPROVED_HARMONIZED"),
            # Water Spinach / Ipomoea aquatica
            "water spinach ipomoea aquatica": ("Ipomoea aquatica (Water Spinach)", "Ipomoea aquatica", "Aquatic Herb", "APPROVED_HARMONIZED"),
            # Wood Sorrel / Oxalis spp
            "wood sorel oxalis spp": ("Oxalis spp. (Wood Sorrel)", "Oxalis spp.", "Herb", "APPROVED_HARMONIZED"),
            # Fenugreek / Trigonella foenum-graecum
            "fenugreek leaves trigonella foenum graecum": ("Trigonella foenum-graecum (Fenugreek)", "Trigonella foenum-graecum", "Herb", "APPROVED_HARMONIZED"),
            "trigonella foenum graecum (fenugreek)": ("Trigonella foenum-graecum (Fenugreek)", "Trigonella foenum-graecum", "Herb", "APPROVED_HARMONIZED"),
            # Centella asiatica / Gotu Kola / Indian Pennywort
            "indian pennywort centella asiatica": ("Centella asiatica (Gotu Kola/Indian Pennywort)", "Centella asiatica", "Herb", "APPROVED_HARMONIZED"),
            # Artemisia indica / Indian Wormwood
            "indian wormwood artemisia indica": ("Artemisia indica (Indian Wormwood)", "Artemisia indica", "Herb", "APPROVED_HARMONIZED"),
            # Coccinia grandis / Ivy Gourd
            "ivy gourd coccinia grandis": ("Coccinia grandis (Ivy Gourd)", "Coccinia grandis", "Vine", "APPROVED_HARMONIZED"),
            # Jamun / Syzygium cumini
            "jamun syzygium cumini": ("Syzygium cumini (Jamun)", "Syzygium cumini", "Tree", "APPROVED_HARMONIZED"),
            # Carissa carandas / Karanda
            "karanda carissa carandas": ("Carissa carandas (Karanda)", "Carissa carandas", "Shrub", "APPROVED_HARMONIZED"),
            # Muntingia calabura / Jamaica Cherry / Gasagase
            "jamaica cherry gasagase muntingia calabura": ("Muntingia calabura (Jamaica Cherry)", "Muntingia calabura", "Tree", "APPROVED_HARMONIZED"),
            "gasagase grewia asiatica": ("Grewia asiatica (Phalsa/Gasagase)", "Grewia asiatica", "Shrub", "APPROVED_HARMONIZED"),
            "gasagase": ("Grewia asiatica (Phalsa/Gasagase)", "Grewia asiatica", "Shrub", "APPROVED_HARMONIZED"),
            # Passiflora foetida / Stinking Passionflower
            "stinking passionflower passiflora foetida": ("Passiflora foetida (Stinking Passionflower)", "Passiflora foetida", "Vine", "APPROVED_HARMONIZED"),
            # Passiflora edulis / Passion fruit
            "passion fruit passiflora edulis": ("Passiflora edulis (Passion Fruit)", "Passiflora edulis", "Vine", "APPROVED_HARMONIZED"),
            # Santalum album / Sandalwood
            "sandalwood santalum album": ("Santalum album (Sandalwood)", "Santalum album", "Tree", "APPROVED_HARMONIZED"),
            # Manilkara zapota / Sapota / Chikoo
            "sapota manikara zapota": ("Manilkara zapota (Sapota/Chikoo)", "Manilkara zapota", "Tree", "APPROVED_HARMONIZED"),
            # Sida rhombifolia / Common Wireweed
            "common wireweed sida rhombifolia": ("Sida rhombifolia (Common Wireweed)", "Sida rhombifolia", "Herb", "APPROVED_HARMONIZED"),
            # Ruta graveolens / Common Rue
            "common rue(naagdalli) ruta graveolens": ("Ruta graveolens (Common Rue)", "Ruta graveolens", "Herb", "APPROVED_HARMONIZED"),
            "common rue(naagdalli)": ("Ruta graveolens (Common Rue)", "Ruta graveolens", "Herb", "APPROVED_HARMONIZED"),
            # Abutilon indicum / Country Mallow
            "country mallow abutilon indicum": ("Abutilon indicum (Country Mallow)", "Abutilon indicum", "Shrub", "APPROVED_HARMONIZED"),
            # Acalypha species
            "dwarf copperleaf (green) acalypha reptans": ("Acalypha reptans (Dwarf Copperleaf)", "Acalypha reptans", "Herb", "APPROVED_HARMONIZED"),
            "dwarf copperleaf (red) acalypha wilkesiana": ("Acalypha wilkesiana (Red Copperleaf)", "Acalypha wilkesiana", "Shrub", "APPROVED_HARMONIZED"),
            "indian copperleaf acalypha indica": ("Acalypha indica (Indian Copperleaf)", "Acalypha indica", "Herb", "APPROVED_HARMONIZED"),
            # Digera muricata / False Amaranth
            "false amarnath digera muricata": ("Digera muricata (False Amaranth)", "Digera muricata", "Herb", "APPROVED_HARMONIZED"),
            # Pelargonium spp / Geranium
            "geranium pelargonium spp (genus)": ("Pelargonium spp. (Geranium)", "Pelargonium spp.", "Herb", "APPROVED_HARMONIZED"),
            # Hibiscus sabdariffa / Gongura
            "gongura hibiscus sabdariffa": ("Hibiscus sabdariffa (Roselle/Gongura)", "Hibiscus sabdariffa", "Shrub", "APPROVED_HARMONIZED"),
            # Andrographis paniculata / Green Chireta / Kalmegh
            "green chireta andrographis paniculata": ("Andrographis paniculata (Kalmegh/Green Chireta)", "Andrographis paniculata", "Herb", "APPROVED_HARMONIZED"),
            # Ziziphus mauritiana / Indian Jujube / Ber
            "indian jujube ziziphus mauritiana": ("Ziziphus mauritiana (Indian Jujube/Ber)", "Ziziphus mauritiana", "Tree", "APPROVED_HARMONIZED"),
            # Hemidesmus indicus / Anantamul / Indian Sarsaparilla
            "indian sarsaparilla hemidesmus indicus": ("Hemidesmus indicus (Anantamul)", "Hemidesmus indicus", "Shrub/Climber", "APPROVED_HARMONIZED"),
            # Urtica dioica / Indian Stinging Nettle
            "indian stinging nettle urtica dioica subsp gracilis": ("Urtica dioica (Stinging Nettle)", "Urtica dioica", "Herb", "APPROVED_HARMONIZED"),
            # Datura metel / Indian Thornapple
            "indian thornapple datura metel": ("Datura metel (Indian Thornapple)", "Datura metel", "Shrub", "APPROVED_HARMONIZED"),
            # Tribulus terrestris / Gokhru
            "big caltrops tribulus terrestris": ("Tribulus terrestris (Gokhru)", "Tribulus terrestris", "Herb", "APPROVED_HARMONIZED"),
            "black honey shrub tribulus terrestris": ("Tribulus terrestris (Gokhru)", "Tribulus terrestris", "Herb", "APPROVED_HARMONIZED"),
            # Cissus quadrangularis / Hadjod
            "bristly wild grape cissus quadrangularis": ("Cissus quadrangularis (Hadjod)", "Cissus quadrangularis", "Vine", "APPROVED_HARMONIZED"),
            # Cissus sicyoides / Trellis Vine
            "trellis vine cissus sicyoides": ("Cissus sicyoides (Trellis Vine)", "Cissus sicyoides", "Vine", "APPROVED_HARMONIZED"),
            # Cinnamomum camphora / Camphor
            "camphor cinnamomum camphora": ("Cinnamomum camphora (Camphor Tree)", "Cinnamomum camphora", "Tree", "APPROVED_HARMONIZED"),
            # Physalis peruviana / Cape Gooseberry
            "cape gooseberry physalis peruviana": ("Physalis peruviana (Cape Gooseberry)", "Physalis peruviana", "Shrub", "APPROVED_HARMONIZED"),
            # Commelina benghalensis / Benghal Dayflower
            "benghal dayflower commelina benghalensis": ("Commelina benghalensis (Dayflower)", "Commelina benghalensis", "Herb", "APPROVED_HARMONIZED"),
            # Jatropha gossypiifolia / Bellyache Bush
            "bellyache bush (green) jatropha gossypiifolia": ("Jatropha gossypiifolia (Bellyache Bush)", "Jatropha gossypiifolia", "Shrub", "APPROVED_HARMONIZED"),
            # Vigna spp / Phaseolus spp / Beans
            "beans vigna spp (genus) or phaseolus spp (genus)": ("Vigna / Phaseolus spp. (Beans)", "Vigna / Phaseolus spp.", "Herb/Vine", "TAXONOMY_CONFLICT_MULTI_GENUS"),
            "beans": ("Vigna / Phaseolus spp. (Beans)", "Vigna / Phaseolus spp.", "Herb/Vine", "TAXONOMY_CONFLICT_MULTI_GENUS"),
            # Acorus calamus / Sweet Flag / Vacha
            "sweet flag acorus calamus": ("Acorus calamus (Vacha/Sweet Flag)", "Acorus calamus", "Herb", "APPROVED_HARMONIZED"),
            # Tridax procumbens / Coatbuttons
            "coatbuttons tridax procumbens": ("Tridax procumbens (Coatbuttons)", "Tridax procumbens", "Herb", "APPROVED_HARMONIZED"),
            # Solanum lycopersicum / Tomato
            "tomato solanum lycopersicum": ("Solanum lycopersicum (Tomato)", "Solanum lycopersicum", "Herb", "APPROVED_HARMONIZED"),
            # Senna angustifolia / Tinnevelly Senna
            "tinnevelly senna cassia angustifolia (also known as senna)": ("Senna alexandrina (Tinnevelly Senna)", "Senna alexandrina", "Shrub", "APPROVED_HARMONIZED"),
            # Cleome viscosa / Spiderwisp
            "spiderwisp cleome viscosa": ("Cleome viscosa (Spiderwisp)", "Cleome viscosa", "Herb", "APPROVED_HARMONIZED"),
            # Sarcostemma acidum / Somlata
            "square stalked vine sarcostemma acidum": ("Sarcostemma acidum (Somlata)", "Sarcostemma acidum", "Shrub", "APPROVED_HARMONIZED"),
            # Mucuna pruriens / Velvet Bean / Kaunch
            "velvet bean mucuna pruriens": ("Mucuna pruriens (Kaunch/Velvet Bean)", "Mucuna pruriens", "Climber", "APPROVED_HARMONIZED"),
            # Diodia teres / Shaggy Button Weed
            "shaggy button weed diodia teres": ("Diodia teres (Shaggy Button Weed)", "Diodia teres", "Herb", "APPROVED_HARMONIZED"),
            # Marsilea minuta / Small Water Clover
            "small water clover marsilea minuta": ("Marsilea minuta (Water Clover)", "Marsilea minuta", "Fern", "APPROVED_HARMONIZED"),
            # Ficus auriculata / Roxburgh Fig
            "roxburgh fig ficus auriculata": ("Ficus auriculata (Roxburgh Fig)", "Ficus auriculata", "Tree", "APPROVED_HARMONIZED"),

            # Generic / Ambiguous / Unresolved vernaculars
            "leafs": ("Unspecified Leaf Samples", "Unknown", "Junk", "INVALID_NON_PLANT"),
            "spinach1": ("Unspecified Spinach Variety", "Spinacia / Amaranthus spp.", "Herb", "AMBIGUOUS_GENERIC_NAME"),
            "insulin": ("Chamaecostus cuspidatus (Insulin Plant)", "Chamaecostus cuspidatus", "Herb", "UNRESOLVED_VERNACULAR"),
            "caricature": ("Graptophyllum pictum (Caricature Plant)", "Graptophyllum pictum", "Shrub", "UNRESOLVED_VERNACULAR"),
            "badipala": ("Erythrina variegata (Badipala)", "Erythrina variegata", "Tree", "UNRESOLVED_VERNACULAR"),
            "chakte": ("Unresolved Chakte Leaf", "Unknown", "Herb", "UNRESOLVED_VERNACULAR"),
            "ganigale": ("Unresolved Ganigale Leaf", "Unknown", "Herb", "UNRESOLVED_VERNACULAR"),
            "kambajala": ("Unresolved Kambajala Leaf", "Unknown", "Herb", "UNRESOLVED_VERNACULAR"),
            "kasambruga": ("Unresolved Kasambruga Leaf", "Unknown", "Herb", "UNRESOLVED_VERNACULAR"),
            "kepala": ("Unresolved Kepala Leaf", "Unknown", "Herb", "UNRESOLVED_VERNACULAR"),
            "kamakasturi": ("Ocimum basilicum var. pilosum (Kamakasturi)", "Ocimum basilicum", "Herb", "UNRESOLVED_VERNACULAR"),
            "sampige": ("Magnolia champaca (Sampige)", "Magnolia champaca", "Tree", "UNRESOLVED_VERNACULAR"),
            "seethapala": ("Annona squamosa (Custard Apple/Seethapala)", "Annona squamosa", "Tree", "APPROVED_HARMONIZED"),
            "tecoma": ("Tecoma spp.", "Tecoma spp.", "Shrub", "UNRESOLVED_VERNACULAR"),
            "thumbe": ("Leucas aspera (Thumbe)", "Leucas aspera", "Herb", "UNRESOLVED_VERNACULAR"),
            "kohlrabi": ("Brassica oleracea var. gongylodes (Kohlrabi)", "Brassica oleracea", "Vegetable", "SINGLE_DATASET_UNIQUE"),
        }

        candidate_species_map: Dict[str, Dict[str, Any]] = {}
        mapping_records: List[Dict[str, Any]] = []

        for p in parsed_classes:
            norm_name = p["normalized_name"]
            ds_id = p["dataset_id"]
            raw_class = p["raw_class_name"]
            img_count = p["image_count"]

            # Match in dictionary or fallback
            dict_match = taxonomy_dictionary.get(norm_name)
            if not dict_match:
                # Substring/prefix fallbacks for Kaggle folder variations
                for dict_key, info in taxonomy_dictionary.items():
                    if dict_key in norm_name or norm_name in dict_key:
                        dict_match = info
                        break

            if dict_match:
                canon_species, sci_name, taxon_cat, status = dict_match
            else:
                canon_species = p["plant_name_raw"].title()
                sci_name = p["scientific_name_candidate"] or "Unknown"
                taxon_cat = "Herb/Plant"
                status = "SINGLE_DATASET_UNIQUE"

            # Aggregate into candidate species map
            if canon_species not in candidate_species_map:
                candidate_species_map[canon_species] = {
                    "candidate_canonical_name": canon_species,
                    "scientific_name": sci_name,
                    "taxon_category": taxon_cat,
                    "status": status,
                    "total_images": 0,
                    "datasets_present": set(),
                    "raw_classes": [],
                    "cimpd_healthy_images": 0,
                    "cimpd_unhealthy_images": 0,
                }

            spec_entry = candidate_species_map[canon_species]
            spec_entry["total_images"] += img_count
            spec_entry["datasets_present"].add(ds_id)
            spec_entry["raw_classes"].append({
                "dataset_id": ds_id,
                "raw_class_name": raw_class,
                "health_condition": p["health_condition"],
                "image_count": img_count,
            })

            if ds_id == "CIMPd":
                if p["health_condition"] == "Healthy":
                    spec_entry["cimpd_healthy_images"] += img_count
                elif p["health_condition"] == "Unhealthy":
                    spec_entry["cimpd_unhealthy_images"] += img_count

            mapping_records.append({
                "dataset_id": ds_id,
                "raw_class_name": raw_class,
                "normalized_class_name": norm_name,
                "candidate_canonical_species": canon_species,
                "scientific_name": sci_name,
                "image_count": img_count,
                "health_condition": p["health_condition"],
                "mapping_status": status,
            })

        # Format datasets_present as sorted list for JSON serializability
        candidate_species_list = []
        for spec_name, spec_info in candidate_species_map.items():
            spec_info["datasets_present"] = sorted(list(spec_info["datasets_present"]))
            spec_info["dataset_count"] = len(spec_info["datasets_present"])
            candidate_species_list.append(spec_info)

        return mapping_records, candidate_species_list

    def run_phase3_statistics(
        self,
        phase1_data: Dict[str, Any],
        candidate_species: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Phase 3: Combined Species Statistics Calculation.
        """
        total_raw_classes = phase1_data["combined_totals"]["total_raw_classes"]
        total_raw_images = phase1_data["combined_totals"]["total_raw_images"]
        estimated_unique_species = len(candidate_species)

        multi_dataset_species = [s for s in candidate_species if s["dataset_count"] > 1]
        single_dataset_species = [s for s in candidate_species if s["dataset_count"] == 1]

        species_under_50 = [s for s in candidate_species if s["total_images"] < 50]
        species_under_100 = [s for s in candidate_species if s["total_images"] < 100]
        species_100_to_300 = [s for s in candidate_species if 100 <= s["total_images"] < 300]
        species_300_plus = [s for s in candidate_species if s["total_images"] >= 300]
        species_500_plus = [s for s in candidate_species if s["total_images"] >= 500]

        # Valid usable species (excluding invalid non-plant & taxonomy conflicts)
        usable_species = [s for s in candidate_species if s["status"] not in ("INVALID_NON_PLANT", "TAXONOMY_CONFLICT_MULTI_GENUS")]
        usable_images = [s["total_images"] for s in usable_species]
        max_imgs = max(usable_images) if usable_images else 0
        min_imgs = min(usable_images) if usable_images else 1
        imbalance_ratio = round(max_imgs / min_imgs, 2) if min_imgs > 0 else 0.0

        taxonomy_conflicts = [s for s in candidate_species if s["status"] in ("TAXONOMY_CONFLICT_MULTI_GENUS", "UNRESOLVED_VERNACULAR", "AMBIGUOUS_GENERIC_NAME")]

        # Recommendation for first large model (usable species with 100+ images)
        recommended_first_model_species = [s for s in usable_species if s["total_images"] >= 100 and s["status"] != "UNRESOLVED_VERNACULAR"]

        return {
            "total_raw_images": total_raw_images,
            "total_raw_classes": total_raw_classes,
            "estimated_unique_species": estimated_unique_species,
            "species_across_multiple_datasets_count": len(multi_dataset_species),
            "species_single_dataset_count": len(single_dataset_species),
            "species_under_50_count": len(species_under_50),
            "species_under_100_count": len(species_under_100),
            "species_100_to_300_count": len(species_100_to_300),
            "species_300_plus_count": len(species_300_plus),
            "species_500_plus_count": len(species_500_plus),
            "overall_imbalance_ratio": imbalance_ratio,
            "max_species_images": max_imgs,
            "min_species_images": min_imgs,
            "taxonomy_conflicts_count": len(taxonomy_conflicts),
            "recommended_first_model_class_count": len(recommended_first_model_species),
        }

    def generate_reports(
        self,
        phase1_data: Dict[str, Any],
        mapping_records: List[Dict[str, Any]],
        candidate_species: List[Dict[str, Any]],
        stats: Dict[str, Any],
    ) -> Dict[str, Path]:
        """
        Phase 4: Generate JSON, CSV, and Markdown feasibility artifacts.
        """
        json_path = self.reports_dir / "combined_species_inventory_v2.json"
        csv_path = self.reports_dir / "combined_species_inventory_v2.csv"
        md_path = self.reports_dir / "combined_species_inventory_v2.md"

        # 1. Generate JSON Report
        json_payload = {
            "metadata": {
                "project": "Dravya AI Engine",
                "report_version": "v2",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "dataset_paths": {k: str(v) for k, v in self.dataset_paths.items()},
            },
            "summary_statistics": stats,
            "dataset_inventories": phase1_data["per_dataset"],
            "combined_inventory_totals": phase1_data["combined_totals"],
            "candidate_species_inventory": candidate_species,
            "raw_class_mappings": mapping_records,
        }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_payload, f, indent=2, ensure_ascii=False)

        # 2. Generate CSV Report
        fieldnames = [
            "candidate_canonical_name",
            "scientific_name",
            "taxon_category",
            "total_images",
            "dataset_count",
            "datasets_present",
            "status",
            "cimpd_healthy_images",
            "cimpd_unhealthy_images",
            "raw_classes_count",
        ]

        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for s in sorted(candidate_species, key=lambda x: x["total_images"], reverse=True):
                writer.writerow({
                    "candidate_canonical_name": s["candidate_canonical_name"],
                    "scientific_name": s["scientific_name"],
                    "taxon_category": s["taxon_category"],
                    "total_images": s["total_images"],
                    "dataset_count": s["dataset_count"],
                    "datasets_present": ", ".join(s["datasets_present"]),
                    "status": s["status"],
                    "cimpd_healthy_images": s["cimpd_healthy_images"],
                    "cimpd_unhealthy_images": s["cimpd_unhealthy_images"],
                    "raw_classes_count": len(s["raw_classes"]),
                })

        # 3. Generate Markdown Feasibility Report
        md_lines = [
            "# Dravya AI — Combined Dataset Species Inventory & Feasibility Report (v2)",
            "",
            f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}  ",
            f"**Status:** Read-Only Inventory Completed  ",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            "| Key Metric | Value |",
            "|---|---|",
            f"| **Total Raw Scanned Images** | **{stats['total_raw_images']:,}** |",
            f"| **Total Raw Class Folders** | **{stats['total_raw_classes']}** |",
            f"| **Estimated Unique Species** | **{stats['estimated_unique_species']}** |",
            f"| **Species Across Multiple Datasets** | **{stats['species_across_multiple_datasets_count']}** |",
            f"| **Species in Only One Dataset** | **{stats['species_single_dataset_count']}** |",
            f"| **Species with 100+ Images** | **{stats['species_100_to_300_count'] + stats['species_300_plus_count']}** |",
            f"| **Species with 300+ Images** | **{stats['species_300_plus_count']}** |",
            f"| **Species with 500+ Images** | **{stats['species_500_plus_count']}** |",
            f"| **Low-Data Species (<100 images)** | **{stats['species_under_100_count']}** |",
            f"| **Taxonomy Conflicts / Unresolved** | **{stats['taxonomy_conflicts_count']}** |",
            f"| **Overall Class Imbalance Ratio** | **{stats['overall_imbalance_ratio']}:1** |",
            f"| **Recommended First-Model Species Count** | **{stats['recommended_first_model_class_count']}** |",
            "",
            "---",
            "",
            "## Core Feasibility Assessment & Answers to Key Questions",
            "",
            "### 1. How many total species are available?",
            f"Across all three datasets, **{stats['estimated_unique_species']} candidate species** have been identified after safe normalization and botanical taxonomy grouping of the {stats['total_raw_classes']} raw class folders.",
            "",
            "### 2. How many are realistically usable for training?",
            f"Of the {stats['estimated_unique_species']} candidate species, **{stats['recommended_first_model_class_count']} species** meet the production quality threshold of having at least **100 valid images** and unambiguous botanical taxonomy.",
            "",
            "### 3. How many images are available per species?",
            "- **300+ Images:** " + str(stats['species_300_plus_count']) + " species (High representation)",
            "- **100–300 Images:** " + str(stats['species_100_to_300_count']) + " species (Moderate representation)",
            "- **50–100 Images:** " + str(stats['species_under_100_count'] - stats['species_under_50_count']) + " species (Requires data augmentation/sourcing)",
            "- **<50 Images:** " + str(stats['species_under_50_count']) + " species (Severe data deficiency)",
            "",
            "### 4. How many species can reasonably be included in the first large model?",
            f"We recommend starting with **{stats['recommended_first_model_class_count']} high-confidence species** that have >=100 images and clear botanical mappings. This balances model accuracy, class balance, and evaluation benchmark reliability.",
            "",
            "### 5. Which species require additional data?",
            f"The **{stats['species_under_100_count']} low-data species** (<100 images) require targeted dataset expansion before inclusion in core production models.",
            "",
            "### 6. Which classes have taxonomy conflicts?",
            "- **Vigna / Phaseolus spp. (Beans):** Raw class combines multiple plant genera.",
            "- **Spinach1:** Ambiguous common name (Spinacia oleracea vs Amaranthus dubius).",
            "- **Insulin / Caricature:** Vernacular common names without verified botanical binomials.",
            "",
            "### 7. Which classes should NOT yet be included?",
            "- **Non-Plant / Corrupt Classes:** `leafs` (generic non-aligned sample folder in CIMPd).",
            "- **Unresolved Vernaculars:** `Badipala`, `Chakte`, `Ganigale`, `Kambajala`, `Kasambruga`, `Kepala` (require expert botanical review).",
            "",
            "---",
            "",
            "## Per-Dataset Breakdown Summary",
            "",
            "| Dataset ID | Root Path | Images | Classes | Corrupt | Non-Image Files |",
            "|---|---|---|---|---|---|",
        ]

        for ds_id, ds_info in phase1_data["per_dataset"].items():
            md_lines.append(
                f"| `{ds_id}` | `{ds_info['root_path']}` | {ds_info['total_images']:,} | {ds_info['total_classes']} | {ds_info['corrupt_images_count']} | {ds_info['non_image_files_count']} |"
            )

        md_lines.extend([
            "",
            "---",
            "",
            "## Exact Duplicate Summary (Read-Only Scan)",
            f"- **Total Exact Duplicate Images:** {phase1_data['combined_totals']['duplicate_summary']['total_exact_duplicates']:,}",
            f"- **Within-Dataset Duplicate Images:** {phase1_data['combined_totals']['duplicate_summary']['within_dataset_duplicates']:,}",
            f"- **Cross-Dataset Duplicate Images:** {phase1_data['combined_totals']['duplicate_summary']['cross_dataset_duplicates']:,}",
            "",
            "---",
            "",
            "## Top 20 Species by Image Count",
            "",
            "| Candidate Canonical Species | Scientific Name | Total Images | Datasets | Status |",
            "|---|---|---|---|---|",
        ])

        top_species = sorted(candidate_species, key=lambda x: x["total_images"], reverse=True)[:20]
        for s in top_species:
            md_lines.append(
                f"| **{s['candidate_canonical_name']}** | *{s['scientific_name']}* | {s['total_images']:,} | {', '.join(s['datasets_present'])} | `{s['status']}` |"
            )

        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

        return {
            "json": json_path,
            "csv": csv_path,
            "md": md_path,
        }

    def print_terminal_summary(self, stats: Dict[str, Any]):
        """
        Prints exact concise summary block to terminal as requested.
        """
        print("\n" + "=" * 60)
        print("     DRAVYA AI COMBINED DATASET INVENTORY SUMMARY (v2)")
        print("=" * 60)
        print(f"TOTAL RAW IMAGES: {stats['total_raw_images']:,}")
        print(f"TOTAL RAW CLASSES: {stats['total_raw_classes']}")
        print(f"ESTIMATED UNIQUE SPECIES: {stats['estimated_unique_species']}")
        print(f"SPECIES ACROSS MULTIPLE DATASETS: {stats['species_across_multiple_datasets_count']}")
        print(f"SPECIES WITH 100+ IMAGES: {stats['species_100_to_300_count'] + stats['species_300_plus_count']}")
        print(f"SPECIES WITH 300+ IMAGES: {stats['species_300_plus_count']}")
        print(f"SPECIES WITH 500+ IMAGES: {stats['species_500_plus_count']}")
        print(f"LOW-DATA SPECIES: {stats['species_under_100_count']}")
        print(f"TAXONOMY CONFLICTS: {stats['taxonomy_conflicts_count']}")
        print(f"RECOMMENDED FIRST-MODEL CLASS COUNT: {stats['recommended_first_model_class_count']}")
        print("=" * 60 + "\n")
