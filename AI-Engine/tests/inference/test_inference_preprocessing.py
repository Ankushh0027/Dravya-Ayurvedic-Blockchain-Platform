import pytest
import numpy as np
from PIL import Image

import torch
from src.training.dataset import get_transforms


def test_inference_transform_shape_and_range():
    transform = get_transforms(image_size=224, is_training=False)

    # Create random 300x400 PIL image
    arr = np.random.randint(0, 256, (300, 400, 3), dtype=np.uint8)
    pil_img = Image.fromarray(arr)

    tensor = transform(pil_img)

    assert isinstance(tensor, torch.Tensor)
    assert tensor.shape == (3, 224, 224)
    # Check normalized values range (mean/std adjusted)
    assert tensor.min() < 0.0
    assert tensor.max() > 0.0


def test_inference_transform_custom_size():
    transform = get_transforms(image_size=256, is_training=False)

    arr = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    pil_img = Image.fromarray(arr)

    tensor = transform(pil_img)
    assert tensor.shape == (3, 256, 256)
