import os
import sys
import time
import zipfile
from pathlib import Path
from typing import List, Set, Dict, Any

PROJECT_ROOT = Path(r"C:\Dravya\Dravya-Ayurvedic-Blockchain-Platform\AI-Engine")

EXCLUDED_DIR_NAMES: Set[str] = {
    "__pycache__",
    ".pytest_cache",
    ".git",
    ".venv",
    "v1-smoke",
    "v2-smoke",
    "CIMPd",
    "Kaggle",
    "Hugging_Face",
    ".idea",
    ".vscode"
}

EXCLUDED_EXTENSIONS: Set[str] = {
    ".pyc",
    ".pyo",
    ".pyd",
}

def should_exclude_path(p: Path) -> bool:
    for part in p.parts:
        if part in EXCLUDED_DIR_NAMES:
            return True
    if p.suffix in EXCLUDED_EXTENSIONS:
        return True
    return False

def create_zip_archive(
    archive_name: str,
    target_rel_path: str,
    is_file: bool = False,
    compression: int = zipfile.ZIP_DEFLATED
) -> Dict[str, Any]:
    zip_output_path = PROJECT_ROOT / archive_name
    target_abs_path = PROJECT_ROOT / target_rel_path

    if not target_abs_path.exists():
        raise FileNotFoundError(f"Target path does not exist: {target_abs_path}")

    print(f"\n==========================================================================")
    print(f"Creating Archive: {archive_name}")
    print(f"Target Path:    {target_rel_path}")
    print(f"Output File:    {zip_output_path}")
    print(f"==========================================================================")

    start_time = time.time()
    file_count = 0
    total_bytes = 0

    with zipfile.ZipFile(zip_output_path, "w", compression=compression) as zf:
        if is_file:
            arcname = target_abs_path.name
            zf.write(target_abs_path, arcname=arcname)
            file_count = 1
            total_bytes = target_abs_path.stat().st_size
        else:
            for root, dirs, files in os.walk(target_abs_path):
                # Filter subdirectories in-place
                dirs[:] = [d for d in dirs if d not in EXCLUDED_DIR_NAMES]
                
                for f in files:
                    file_path = Path(root) / f
                    if should_exclude_path(file_path):
                        continue

                    rel_path = file_path.relative_to(PROJECT_ROOT)
                    zf.write(file_path, arcname=str(rel_path))
                    file_count += 1
                    total_bytes += file_path.stat().st_size

    elapsed = round(time.time() - start_time, 2)
    compressed_bytes = zip_output_path.stat().st_size
    compressed_mb = round(compressed_bytes / (1024 * 1024), 2)
    compressed_gb = round(compressed_bytes / (1024 * 1024 * 1024), 3)

    # Verification: Test ZIP integrity
    print("Testing archive integrity...")
    with zipfile.ZipFile(zip_output_path, "r") as zf:
        corrupt = zf.testzip()
        if corrupt is not None:
            raise RuntimeError(f"Archive test failed! Corrupt file found: {corrupt}")

        infolist = zf.infolist()
        top_level_dirs = sorted(list(set(Path(item.filename).parts[0] for item in infolist)))

    print(f"-> Archive Created Successfully in {elapsed}s.")
    print(f"-> File Count:  {file_count:,}")
    print(f"-> Archive Size: {compressed_mb:,.2f} MB ({compressed_gb:.3f} GB / {compressed_bytes:,} bytes)")
    print(f"-> Top-Level Structure: {top_level_dirs}")

    return {
        "archive_name": archive_name,
        "zip_path": str(zip_output_path),
        "file_count": file_count,
        "size_bytes": compressed_bytes,
        "size_mb": compressed_mb,
        "size_gb": compressed_gb,
        "elapsed_seconds": elapsed,
        "top_level_structure": top_level_dirs
    }

def main():
    print("==========================================================================")
    print("      DRAVYA AI ENGINE — KAGGLE COMPONENT PACKAGING RUNNER              ")
    print("==========================================================================")

    results = []

    # 1. dravya_src.zip (Include src/)
    r1 = create_zip_archive(
        archive_name="dravya_src.zip",
        target_rel_path="src",
        compression=zipfile.ZIP_DEFLATED
    )
    results.append(r1)

    # 2. dravya_configs.zip (Include configs/)
    r2 = create_zip_archive(
        archive_name="dravya_configs.zip",
        target_rel_path="configs",
        compression=zipfile.ZIP_DEFLATED
    )
    results.append(r2)

    # 3. canonical_dataset_v2.zip (Include datasets/final/canonical_v2/)
    r3 = create_zip_archive(
        archive_name="canonical_dataset_v2.zip",
        target_rel_path=r"datasets\final\canonical_v2",
        compression=zipfile.ZIP_STORED  # Preserve raw JPEG/PNG without recompression overhead
    )
    results.append(r3)

    # 4. dravya_reports.zip (Include reports/dataset_analysis/)
    r4 = create_zip_archive(
        archive_name="dravya_reports.zip",
        target_rel_path=r"reports\dataset_analysis",
        compression=zipfile.ZIP_DEFLATED
    )
    results.append(r4)

    # 5. requirements.zip (Include requirements.txt)
    r5 = create_zip_archive(
        archive_name="requirements.zip",
        target_rel_path="requirements.txt",
        is_file=True,
        compression=zipfile.ZIP_DEFLATED
    )
    results.append(r5)

    print("\n==========================================================================")
    print("              KAGGLE ZIP PACKAGING SUMMARY REPORT                         ")
    print("==========================================================================")
    print(f"{'Archive Name':<25} | {'File Count':<12} | {'Size (MB)':<12} | {'Top-Level Structure'}")
    print("-" * 80)
    for r in results:
        top_str = "/, ".join(r["top_level_structure"])
        print(f"{r['archive_name']:<25} | {r['file_count']:<12,} | {r['size_mb']:<12,.2f} | {top_str}")
    print("==========================================================================")

if __name__ == "__main__":
    main()
