import io
import json
import numpy as np
from PIL import Image
import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.api.dependencies import get_predictor_manager
from src.models.config import ModelConfig
from src.models.plant_classifier import PlantClassifier
from src.models.version_manager import ModelVersionManager
from src.training.dataset import DravyaDataset
from src.training.trainer import ModelTrainer
from torch.utils.data import DataLoader


@pytest.fixture
def mock_active_model_setup(tmp_path):
    """
    Fixture creating a synthetic, fast, lightweight model checkpoint and setting it active.
    Prevents loading real 48MB weights during API unit tests.
    """
    models_dir = tmp_path / "models"
    output_dir = tmp_path / "reports_eval"
    models_dir.mkdir()
    output_dir.mkdir()

    version_id = "v1-api-test"
    records = [
        {"canonical_name": "Saraca asoca", "mapping_status": "APPROVED", "sha256": "s1"},
        {"canonical_name": "Clerodendrum splendens", "mapping_status": "APPROVED", "sha256": "s2"},
    ]

    dataset = DravyaDataset(records=records)
    config = ModelConfig(models_dir=str(models_dir), model_version=version_id, epochs=1, batch_size=2)
    model = PlantClassifier(num_classes=2, pretrained=False)
    loader = DataLoader(dataset, batch_size=2)

    trainer = ModelTrainer(
        model=model,
        config=config,
        class_to_idx=dataset.class_to_idx,
        idx_to_class=dataset.idx_to_class,
        train_loader=loader,
        val_loader=loader,
    )
    trainer.train()

    vm = ModelVersionManager(models_dir=models_dir)
    vm.set_active_version(version_id)

    # Configure dependency manager
    manager = get_predictor_manager()
    manager.set_models_dir(models_dir)
    manager.clear_cache()

    yield models_dir, version_id

    # Reset
    manager.clear_cache()
    manager.set_models_dir(None)


@pytest.fixture
def client(mock_active_model_setup):
    app = create_app()
    return TestClient(app)


@pytest.fixture
def synthetic_png_bytes():
    arr = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
    pil_img = Image.fromarray(arr)
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    return buf.getvalue()
