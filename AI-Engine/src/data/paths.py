import os

EXTERNAL_DATASET_ROOT = r"C:\Datasets"

DATASET_PATHS = {
    "CIMPd": os.path.join(EXTERNAL_DATASET_ROOT, "CIMPd"),
    "Hugging_Face": os.path.join(EXTERNAL_DATASET_ROOT, "Hugging_Face"),
    "Kaggle": os.path.join(EXTERNAL_DATASET_ROOT, "Kaggle"),
}

SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
ARCHIVE_EXTENSIONS = {".zip", ".tar", ".gz", ".7z", ".rar", ".tgz"}
METADATA_EXTENSIONS = {".csv", ".json", ".jsonl", ".parquet", ".txt", ".xml"}
