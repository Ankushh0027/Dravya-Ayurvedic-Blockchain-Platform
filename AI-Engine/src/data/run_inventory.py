import os
import sys

# Ensure C:\Dravya-AI-Engine is in Python path when executing script directly
sys.path.insert(0, os.path.abspath(r"C:\Dravya-AI-Engine"))

from src.data import DATASET_PATHS, InventoryScanner, ManifestGenerator

def main():
    print("Starting Dravya AI Dataset Inventory Scan...\n")

    inventories = []
    for ds_id, root_path in DATASET_PATHS.items():
        print(f"Scanning dataset '{ds_id}' at '{root_path}'...")
        scanner = InventoryScanner(dataset_id=ds_id, root_path=root_path)
        inv = scanner.scan()
        inventories.append(inv)
        print(f"-> {ds_id}: {inv['total_images']:,} images found across {inv['total_apparent_classes']} class folders.")

    generator = ManifestGenerator()
    json_file = generator.export_json(inventories)
    csv_file = generator.export_csv(inventories)
    summary_str = generator.format_terminal_summary(inventories)

    print("\n" + summary_str)
    print(f"\nGenerated Artifacts:")
    print(f" - Machine-readable JSON: {json_file}")
    print(f" - Class distribution CSV: {csv_file}")

if __name__ == "__main__":
    main()
