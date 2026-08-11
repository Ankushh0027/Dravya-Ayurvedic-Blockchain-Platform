import os
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from src.data.paths import (
    SUPPORTED_IMAGE_EXTENSIONS,
    ARCHIVE_EXTENSIONS,
    METADATA_EXTENSIONS
)

class InventoryScanner:
    """
    Recursively scans external dataset root paths to build an inventory of image files,
    class directories, non-image files, and archives without loading image contents.
    """

    def __init__(self, dataset_id: str, root_path: str, source: Optional[str] = None):
        self.dataset_id = dataset_id
        self.root_path = os.path.abspath(root_path)
        self.source = source or dataset_id

    def scan(self) -> Dict[str, Any]:
        """
        Executes filesystem scan and returns a structured inventory dictionary.
        """
        if not os.path.exists(self.root_path):
            raise FileNotFoundError(f"Dataset root path does not exist: {self.root_path}")

        total_files = 0
        total_images = 0
        image_extensions_found: Dict[str, int] = {}
        class_image_counts: Dict[str, int] = {}
        empty_class_directories: List[str] = []
        non_image_files: List[str] = []
        archive_files: List[str] = []

        # Track directories that have subdirectories vs directories that contain images
        dirs_with_subdirs = set()
        dirs_with_images = set()
        all_relative_dirs = set()

        for dirpath, dirnames, filenames in os.walk(self.root_path):
            rel_dir = os.path.relpath(dirpath, self.root_path)
            if rel_dir != ".":
                all_relative_dirs.add(rel_dir)

            if dirnames and rel_dir != ".":
                dirs_with_subdirs.add(rel_dir)

            dir_image_count = 0
            for f in filenames:
                total_files += 1
                rel_file_path = os.path.join(rel_dir, f) if rel_dir != "." else f
                ext = os.path.splitext(f)[1].lower()

                if ext in SUPPORTED_IMAGE_EXTENSIONS:
                    total_images += 1
                    dir_image_count += 1
                    image_extensions_found[ext] = image_extensions_found.get(ext, 0) + 1
                elif ext in ARCHIVE_EXTENSIONS:
                    archive_files.append(rel_file_path)
                    non_image_files.append(rel_file_path)
                else:
                    non_image_files.append(rel_file_path)

            if dir_image_count > 0:
                class_name = rel_dir if rel_dir != "." else "root"
                class_image_counts[class_name] = dir_image_count
                dirs_with_images.add(rel_dir)

        # Identify leaf directories with 0 images as empty class directories
        for rel_dir in all_relative_dirs:
            if rel_dir not in dirs_with_images and rel_dir not in dirs_with_subdirs:
                empty_class_directories.append(rel_dir)

        scan_timestamp = datetime.now(timezone.utc).isoformat()
        class_names = sorted(list(class_image_counts.keys()))

        return {
            "dataset_id": self.dataset_id,
            "source": self.source,
            "root_path": self.root_path,
            "total_files": total_files,
            "total_images": total_images,
            "image_extensions": image_extensions_found,
            "total_apparent_classes": len(class_names),
            "class_names": class_names,
            "image_count_per_class": class_image_counts,
            "empty_class_directories": sorted(empty_class_directories),
            "non_image_files": sorted(non_image_files),
            "archive_files": sorted(archive_files),
            "scan_timestamp": scan_timestamp
        }
