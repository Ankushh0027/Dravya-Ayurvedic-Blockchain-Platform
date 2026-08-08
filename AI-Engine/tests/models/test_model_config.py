import os
import pytest
from pathlib import Path

from src.models.config import ModelConfig, load_model_config


def test_default_model_config():
    config = load_model_config()
    assert config.architecture == "efficientnet_b0"
    assert config.image_size == 224
    assert config.batch_size == 16
    assert config.epochs == 5
    assert config.learning_rate == 0.001
    assert config.validation_split == 0.2
    assert config.random_seed == 42
    assert config.model_version == "v1"
    assert config.device in ["cpu", "cuda"]


def test_custom_override_model_config():
    config = load_model_config(
        architecture="efficientnet_b1",
        batch_size=32,
        epochs=10,
        learning_rate=0.0005,
        model_version="v2",
    )
    assert config.architecture == "efficientnet_b1"
    assert config.batch_size == 32
    assert config.epochs == 10
    assert config.learning_rate == 0.0005
    assert config.model_version == "v2"


def test_env_var_override_config(monkeypatch):
    monkeypatch.setenv("DRAVYA_MODEL_ARCH", "resnet18")
    monkeypatch.setenv("DRAVYA_BATCH_SIZE", "64")
    monkeypatch.setenv("DRAVYA_MODEL_VERSION", "v3-test")

    config = load_model_config()
    assert config.architecture == "resnet18"
    assert config.batch_size == 64
    assert config.model_version == "v3-test"


def test_config_to_dict():
    config = ModelConfig(architecture="efficientnet_b0", batch_size=8)
    d = config.to_dict()
    assert d["architecture"] == "efficientnet_b0"
    assert d["batch_size"] == 8
