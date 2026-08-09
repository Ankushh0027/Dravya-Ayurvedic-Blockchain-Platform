import os
import sys
import json
import time
import torch
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.paths import get_reports_dir, get_project_root, get_dataset_paths
from src.models.config import load_model_config
from src.models.plant_classifier import PlantClassifier
from src.training.dataset import DravyaDataset, get_transforms, load_canonical_records
from src.training.trainer import ModelTrainer

def main():
    print("==========================================================================")
    print("      DRAVYA AI ENGINE — V2-SMOKE GPU TRAINING & CHECKPOINT GENERATOR     ")
    print("==========================================================================")

    reports_dir = get_reports_dir()
    manifest_path = reports_dir / "canonical_dataset_manifest_v2.json"
    if not manifest_path.exists():
        manifest_path = get_project_root() / "datasets" / "final" / "canonical_v2" / "manifest.json"

    print(f"\n1. Loading Canonical Dataset V2 Manifest: {manifest_path}")
    records = load_canonical_records(manifest_path)
    approved_records = [r for r in records if r.get("mapping_status") == "APPROVED"]

    # Extract 135 approved classes
    classes = sorted(list(set(r.get("canonical_name", r["canonical_class_id"]) for r in approved_records)))
    class_to_idx = {c: i for i, c in enumerate(classes)}
    idx_to_class = {i: c for i, c in enumerate(classes)}
    num_classes = len(class_to_idx)

    print(f"-> Verified Approved Records: {len(approved_records):,} across {num_classes} classes.")

    # Device check
    device_str = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"-> Execution Device: {device_str.upper()} (PyTorch {torch.__version__})")

    # Load Model Config
    config = load_model_config(
        model_version="v2-smoke",
        epochs=1,
        batch_size=16,
        device=device_str,
        architecture="efficientnet_b0",
        dataset_manifest_path=str(manifest_path)
    )

    # Prepare DataLoaders
    train_records = [r for r in approved_records if r.get("split") == "train"]
    val_records = [r for r in approved_records if r.get("split") == "val"]

    if not train_records:
        split_point = int(len(approved_records) * 0.70)
        train_records = approved_records[:split_point]
        val_records = approved_records[split_point:]

    train_tf = get_transforms(224, is_training=True)
    val_tf = get_transforms(224, is_training=False)

    train_ds = DravyaDataset(records=train_records, transform=train_tf, class_to_idx=class_to_idx)
    val_ds = DravyaDataset(records=val_records, transform=val_tf, class_to_idx=class_to_idx)

    train_loader = torch.utils.data.DataLoader(train_ds, batch_size=config.batch_size, shuffle=True, num_workers=0)
    val_loader = torch.utils.data.DataLoader(val_ds, batch_size=config.batch_size, shuffle=False, num_workers=0)

    # Instantiate Model & Trainer
    print(f"\n2. Instantiating PlantClassifier (Architecture: {config.architecture}, Classes: {num_classes})...")
    model = PlantClassifier(num_classes=num_classes, architecture=config.architecture, pretrained=False)

    trainer = ModelTrainer(
        model=model,
        config=config,
        class_to_idx=class_to_idx,
        idx_to_class=idx_to_class,
        train_loader=train_loader,
        val_loader=val_loader
    )

    print("\n3. Executing PyTorch GPU Training Loop (1 Epoch)...")
    start_t = time.time()
    summary = trainer.train()
    elapsed = round(time.time() - start_t, 2)

    v_dir = trainer.version_dir
    best_path = v_dir / "best_model.pth"
    latest_path = v_dir / "latest_checkpoint.pth"

    print("\n--------------------------------------------------------------------------")
    print("                    CHECKPOINT FILE VERIFICATION                          ")
    print("--------------------------------------------------------------------------")
    
    if best_path.exists() and latest_path.exists():
        best_size_bytes = best_path.stat().st_size
        latest_size_bytes = latest_path.stat().st_size
        best_size_mb = round(best_size_bytes / (1024 * 1024), 2)
        latest_size_mb = round(latest_size_bytes / (1024 * 1024), 2)

        print(f"best_model.pth Exists:        TRUE ({best_size_mb} MB / {best_size_bytes:,} bytes)")
        print(f"latest_checkpoint.pth Exists: TRUE ({latest_size_mb} MB / {latest_size_bytes:,} bytes)")
    else:
        print(f"ERROR: Checkpoint files not found in {v_dir}")
        sys.exit(1)

    print("\n4. Verifying Checkpoint Loading on GPU and CPU...")
    # GPU Checkpoint Loading Test
    try:
        gpu_checkpoint = torch.load(best_path, map_location=device_str)
        gpu_load_success = True
        print(f"-> GPU torch.load('{best_path.name}'): SUCCESS")
    except Exception as e:
        gpu_load_success = False
        print(f"-> GPU torch.load('{best_path.name}'): FAILED ({e})")

    # CPU Checkpoint Loading Test
    try:
        cpu_checkpoint = torch.load(best_path, map_location="cpu")
        cpu_load_success = True
        print(f"-> CPU torch.load('{best_path.name}'): SUCCESS")
    except Exception as e:
        cpu_load_success = False
        print(f"-> CPU torch.load('{best_path.name}'): FAILED ({e})")

    # Verify model instantiation from checkpoint state dict
    eval_model = PlantClassifier(num_classes=num_classes, architecture=config.architecture, pretrained=False)
    eval_model.load_state_dict(cpu_checkpoint["model_state_dict"])
    eval_model.eval()
    print("-> Model state_dict instantiation and eval mode switch: SUCCESS")

    print("\n==========================================================================")
    print("                      RERUN SUMMARY & VERIFICATION                         ")
    print("==========================================================================")
    print(f"TRAINING STATUS:       SUCCESS")
    print(f"BEST MODEL PATH:       {best_path}")
    print(f"LATEST MODEL PATH:     {latest_path}")
    print(f"BEST MODEL SIZE:       {best_size_mb} MB ({best_size_bytes:,} bytes)")
    print(f"LATEST MODEL SIZE:     {latest_size_mb} MB ({latest_size_bytes:,} bytes)")
    print(f"NUMBER OF CLASSES:     {num_classes}")
    print(f"DEVICE USED:           {device_str.upper()}")
    print(f"GPU LOADING CHECK:     {'SUCCESS' if gpu_load_success else 'FAILED'}")
    print(f"CPU LOADING CHECK:     {'SUCCESS' if cpu_load_success else 'FAILED'}")
    print(f"TRAINING TIME (S):     {elapsed}s")
    print("==========================================================================")

if __name__ == "__main__":
    main()
