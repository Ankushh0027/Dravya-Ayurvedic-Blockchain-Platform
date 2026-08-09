import argparse
import csv
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from PIL import Image

from src.inference.predictor import PlantPredictor

logger = logging.getLogger("dravya_batch_predictor")


class BatchPlantPredictor:
    """
    Batch Inference Processor for Dravya AI Engine.
    Executes high-throughput plant identification across directories of images
    or manifest lists, exporting structured JSON or CSV reports.
    """

    SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

    def __init__(
        self,
        version: Optional[str] = None,
        device: Optional[str] = None,
        models_dir: Optional[Union[str, Path]] = None,
    ):
        self.predictor = PlantPredictor(version=version, device=device, models_dir=models_dir)

    def scan_image_files(self, input_dir: Union[str, Path], recursive: bool = True) -> List[Path]:
        """
        Scans input directory for supported image files.
        """
        dir_path = Path(input_dir)
        if not dir_path.exists() or not dir_path.is_dir():
            raise FileNotFoundError(f"Input directory does not exist: {dir_path}")

        pattern = "**/*" if recursive else "*"
        image_files = [
            p for p in dir_path.glob(pattern)
            if p.is_file() and p.suffix.lower() in self.SUPPORTED_EXTENSIONS
        ]
        image_files.sort()
        return image_files

    def predict_batch(
        self,
        image_paths: List[Union[str, Path]],
        top_k: int = 5,
        show_progress: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Executes model inference over a sequence of image file paths.
        """
        results = []
        total = len(image_paths)

        for idx, img_path in enumerate(image_paths, 1):
            path_obj = Path(img_path)
            try:
                pred = self.predictor.predict(path_obj, top_k=top_k)
                record = {
                    "file_path": str(path_obj.resolve()),
                    "file_name": path_obj.name,
                    "status": "SUCCESS",
                    "class_id": pred.get("class_id"),
                    "species_name": pred.get("species_name"),
                    "scientific_name": pred.get("scientific_name"),
                    "confidence": pred.get("confidence", 0.0),
                    "top_k": pred.get("top_k", []),
                    "model_version": pred.get("model_version"),
                }
            except Exception as e:
                logger.error(f"Failed inference on {path_obj}: {e}")
                record = {
                    "file_path": str(path_obj.resolve()),
                    "file_name": path_obj.name,
                    "status": "ERROR",
                    "error": str(e),
                    "class_id": None,
                    "species_name": "UNKNOWN",
                    "scientific_name": None,
                    "confidence": 0.0,
                    "top_k": [],
                    "model_version": self.predictor.version,
                }

            results.append(record)

            if show_progress and (idx % 10 == 0 or idx == total):
                print(f"Processed [{idx}/{total}] images...")

        return results

    def export_results(
        self,
        results: List[Dict[str, Any]],
        output_path: Union[str, Path],
        format_type: str = "json",
    ) -> Path:
        """
        Exports batch prediction records to JSON or CSV format.
        """
        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        if format_type.lower() == "csv":
            with open(out_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "file_name",
                        "status",
                        "class_id",
                        "species_name",
                        "scientific_name",
                        "confidence",
                        "file_path",
                        "error",
                    ],
                )
                writer.writeheader()
                for r in results:
                    writer.writerow({
                        "file_name": r.get("file_name"),
                        "status": r.get("status"),
                        "class_id": r.get("class_id"),
                        "species_name": r.get("species_name"),
                        "scientific_name": r.get("scientific_name"),
                        "confidence": r.get("confidence"),
                        "file_path": r.get("file_path"),
                        "error": r.get("error", ""),
                    })
        else:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "total_images": len(results),
                        "model_version": self.predictor.version,
                        "results": results,
                    },
                    f,
                    indent=2,
                )

        logger.info(f"Exported batch prediction results to {out_path}")
        return out_path


def main():
    parser = argparse.ArgumentParser(description="Dravya AI Batch Inference CLI")
    parser.add_argument("--input-dir", type=str, required=True, help="Directory containing images")
    parser.add_argument("--output", type=str, required=True, help="Output file path (.json or .csv)")
    parser.add_argument("--format", type=str, choices=["json", "csv"], default="json", help="Export format")
    parser.add_argument("--version", type=str, default=None, help="Model version (defaults to active model)")
    parser.add_argument("--top-k", type=int, default=5, help="Number of top candidates")
    parser.add_argument("--device", type=str, default=None, help="Inference device (cpu or cuda)")

    args = parser.parse_args()

    batch_pred = BatchPlantPredictor(version=args.version, device=args.device)
    files = batch_pred.scan_image_files(args.input_dir)
    print(f"Found {len(files)} image files in {args.input_dir}")

    if not files:
        print("No image files found. Exiting.")
        sys.exit(0)

    results = batch_pred.predict_batch(files, top_k=args.top_k)
    out_file = batch_pred.export_results(results, args.output, format_type=args.format)
    print(f"Done! Results written to {out_file}")


if __name__ == "__main__":
    main()
