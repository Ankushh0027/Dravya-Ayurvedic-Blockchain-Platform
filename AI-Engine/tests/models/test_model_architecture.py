import pytest
import torch

from src.models.plant_classifier import PlantClassifier


def test_plant_classifier_instantiation():
    model = PlantClassifier(num_classes=10, architecture="efficientnet_b0", pretrained=False)
    assert model.num_classes == 10
    assert model.architecture_name == "efficientnet_b0"
    assert isinstance(model, torch.nn.Module)


def test_plant_classifier_forward_tensor_shape():
    num_classes = 5
    batch_size = 2
    model = PlantClassifier(num_classes=num_classes, architecture="efficientnet_b0", pretrained=False)
    
    # Input tensor (B, C, H, W)
    x = torch.randn(batch_size, 3, 224, 224)
    logits = model(x)
    
    assert logits.shape == (batch_size, num_classes)


def test_plant_classifier_predict_proba():
    num_classes = 4
    batch_size = 3
    model = PlantClassifier(num_classes=num_classes, architecture="efficientnet_b0", pretrained=False)
    
    x = torch.randn(batch_size, 3, 224, 224)
    probs = model.predict_proba(x)
    
    assert probs.shape == (batch_size, num_classes)
    # Check probabilities sum to ~1.0 for each item in batch
    row_sums = probs.sum(dim=1).detach().numpy()
    for s in row_sums:
        assert abs(s - 1.0) < 1e-4


def test_resnet_backbone_fallback():
    model = PlantClassifier(num_classes=3, architecture="resnet18", pretrained=False)
    assert model.architecture_name == "resnet18"
    x = torch.randn(1, 3, 224, 224)
    logits = model(x)
    assert logits.shape == (1, 3)
