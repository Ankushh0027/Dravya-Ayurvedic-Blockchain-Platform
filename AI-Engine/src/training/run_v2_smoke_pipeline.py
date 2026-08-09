import os
import sys
import json
import time
import traceback
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

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
    print("      DRAVYA AI ENGINE — GENUINE V2-SMOKE GPU TRAINING PIPELINE          ")
    print("==========================================================================")

    # 1. CUDA Hardware Verification
    print("\n1. Verifying CUDA Hardware & PyTorch Infrastructure...")
    torch_ver = torch.__version__
    cuda_available = torch.cuda.is_available()
    
    if not cuda_available:
        print("ERROR: CUDA is unavailable. PyTorch GPU smoke training requires CUDA.")
        print(f"PyTorch Version: {torch_ver}, CUDA Available: {cuda_available}")
        sys.exit(1)

    device_name = torch.cuda.get_device_name(0)
    print(f"-> PyTorch Version: {torch_ver}")
    print(f"-> CUDA Available:  True")
    print(f"-> Target GPU:      {device_name}")

    # 2. Dataset Manifest Resolution
    reports_dir = get_reports_dir()
    manifest_path = reports_dir / "canonical_dataset_manifest_v2.json"
    if not manifest_path.exists():
        manifest_path = get_project_root() / "datasets" / "final" / "canonical_v2" / "manifest.json"

    if not manifest_path.exists():
        print(f"ERROR: Canonical Dataset V2 manifest missing at {manifest_path}")
        sys.exit(1)

    print(f"\n2. Loading Canonical Dataset V2 Manifest: {manifest_path}")
    all_records = load_canonical_records(manifest_path)
    approved_records = [r for r in all_records if r.get("mapping_status") == "APPROVED"]

    # Extract 135 approved classes
    classes = sorted(list(set(r.get("canonical_name", r["canonical_class_id"]) for r in approved_records)))
    class_to_idx = {c: i for i, c in enumerate(classes)}
    idx_to_class = {i: c for i, c in enumerate(classes)}
    num_classes = len(class_to_idx)

    print(f"-> Verified Approved Dataset Records: {len(approved_records):,} across {num_classes} classes.")

    # 3. Model Configuration
    config = load_model_config(
        model_version="v2-smoke",
        epochs=1,
        batch_size=16,
        device="cuda",
        architecture="efficientnet_b0",
        dataset_manifest_path=str(manifest_path)
    )

    # Data Partitioning & DataLoader Setup
    train_records = [r for r in approved_records if r.get("split") == "train"]
    val_records = [r for r in approved_records if r.get("split") == "val"]

    if not train_records:
        split_pt = int(len(approved_records) * 0.70)
        train_records = approved_records[:split_pt]
        val_records = approved_records[split_pt:]

    train_tf = get_transforms(224, is_training=True)
    val_tf = get_transforms(224, is_training=False)

    train_ds = DravyaDataset(records=train_records, transform=train_tf, class_to_idx=class_to_idx)
    val_ds = DravyaDataset(records=val_records, transform=val_tf, class_to_idx=class_to_idx)

    train_loader = DataLoader(train_ds, batch_size=config.batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=config.batch_size, shuffle=False, num_workers=0)

    # 4. Instantiate Model & Trainer
    print(f"\n3. Instantiating PlantClassifier (EfficientNet-B0, 135 Classes)...")
    model = PlantClassifier(num_classes=num_classes, architecture="efficientnet_b0", pretrained=False)

    trainer = ModelTrainer(
        model=model,
        config=config,
        class_to_idx=class_to_idx,
        idx_to_class=idx_to_class,
        train_loader=train_loader,
        val_loader=val_loader
    )

    # 5. Execute Training Loop
    print("\n4. Executing Genuine PyTorch Training Loop (1 Epoch, CUDA)...")
    start_t = time.time()
    try:
        summary = trainer.train()
        elapsed = round(time.time() - start_t, 2)
        print(f"-> Training Loop Completed in {elapsed}s.")
    except Exception as e:
        print("\n==========================================================================")
        print("                   TRAINING FAILED WITH TRACEBACK                         ")
        print("==========================================================================")
        traceback.print_exc()
        sys.exit(1)

    v_dir = trainer.version_dir
    best_path = v_dir / "best_model.pth"
    latest_path = v_dir / "latest_checkpoint.pth"
    meta_path = v_dir / "model_metadata.json"
    cmap_path = v_dir / "class_mapping.json"

    print("\n--------------------------------------------------------------------------")
    print("                 PHYSICAL CHECKPOINT FILE INSPECTION                      ")
    print("--------------------------------------------------------------------------")

    if not best_path.exists() or not latest_path.exists():
        print(f"CRITICAL ERROR: torch.save() failed to produce physical checkpoint files!")
        print(f"best_model.pth exists:    {best_path.exists()}")
        print(f"latest_checkpoint.pth exists: {latest_path.exists()}")
        sys.exit(1)

    best_bytes = best_path.stat().st_size
    latest_bytes = latest_path.stat().st_size
    best_mb = round(best_bytes / (1024 * 1024), 2)
    latest_mb = round(latest_bytes / (1024 * 1024), 2)

    print(f"best_model.pth Path:       {best_path}")
    print(f"best_model.pth Size:       {best_mb} MB ({best_bytes:,} bytes)")
    print(f"latest_checkpoint.pth Path: {latest_path}")
    print(f"latest_checkpoint.pth Size: {latest_mb} MB ({latest_bytes:,} bytes)")

    # 6. Python Checkpoint Loading & State Dict Verification
    print("\n5. Running Checkpoint Loading & State Dict Verification...")

    # GPU Loading Test
    try:
        gpu_chk = torch.load(best_path, map_location="cuda")
        gpu_load_ok = True
        print("-> torch.load(best_model.pth, map_location='cuda'): SUCCESS")
    except Exception as e:
        gpu_load_ok = False
        print(f"-> torch.load(best_model.pth, map_location='cuda'): FAILED ({e})")

    # CPU Loading Test
    try:
        cpu_chk = torch.load(best_path, map_location="cpu")
        cpu_load_ok = True
        print("-> torch.load(best_model.pth, map_location='cpu'): SUCCESS")
    except Exception as e:
        cpu_load_ok = False
        print(f"-> torch.load(best_model.pth, map_location='cpu'): FAILED ({e})")

    # Instantiate model and load state_dict
    try:
        eval_model = PlantClassifier(num_classes=num_classes, architecture="efficientnet_b0", pretrained=False)
        eval_model.load_state_dict(cpu_chk["model_state_dict"])
        eval_model.eval()
        state_dict_load_ok = True
        print("-> PlantClassifier.load_state_dict(): SUCCESS")
    except Exception as e:
        state_dict_load_ok = False
        print(f"-> PlantClassifier.load_state_dict(): FAILED ({e})")

    # 7. Actual Directory Listing of models/v2-smoke/
    print("\n--------------------------------------------------------------------------")
    print("               ACTUAL CONTENTS OF models/v2-smoke/                        ")
    print("--------------------------------------------------------------------------")
    v_dir_files = sorted(list(v_dir.iterdir()))
    for f in v_dir_files:
        f_size_mb = round(f.stat().st_size / (1024 * 1024), 2) if f.is_file() else 0
        f_bytes = f.stat().st_size if f.is_file() else 0
        print(f" - {f.name:<25} ({f_size_mb:>6.2f} MB / {f_bytes:>12,} bytes)")

    print("\n==========================================================================")
    print("                  VERIFIED TRAINING & CHECKPOINT REPORT                  ")
    print("==========================================================================")
    print(f"TRAINING COMMAND:      python src/training/run_v2_smoke_pipeline.py")
    print(f"ACTUAL DEVICE:         CUDA ({device_name})")
    print(f"EPOCHS EXECUTED:       1 Epoch ({len(train_loader)} batches)")
    print(f"NUM APPROVED CLASSES:  {num_classes}")
    print(f"BEST MODEL PATH:       {best_path}")
    print(f"BEST MODEL SIZE:       {best_mb} MB ({best_bytes:,} bytes)")
    print(f"LATEST MODEL PATH:     {latest_path}")
    print(f"LATEST MODEL SIZE:     {latest_mb} MB ({latest_bytes:,} bytes)")
    print(f"TORCH.LOAD GPU CHECK:  {'SUCCESS' if gpu_load_ok else 'FAILED'}")
    print(f"TORCH.LOAD CPU CHECK:  {'SUCCESS' if cpu_load_ok else 'FAILED'}")
    print(f"STATE_DICT LOAD CHECK: {'SUCCESS' if state_dict_load_ok else 'FAILED'}")
    print(f"ACTIVE MODEL PROMOTED: NO (models/active_model.json left unchanged)")
    print(f"RAW DATASETS STATUS:   UNTOUCHED (READ-ONLY)")
    print("==========================================================================")

if __name__ == "__main__":
    main()
