from typing import Dict, Any, Optional
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    import torchvision.models as models
    BaseModule = nn.Module
except ImportError:
    torch = None
    nn = None
    F = None
    models = None
    BaseModule = object


class PlantClassifier(BaseModule):
    """
    Production-oriented Image Classification Architecture for Dravya AI.
    Wraps EfficientNet (or configurable backbone) with a customized output classifier head
    matching the number of classes loaded from the canonical dataset manifest.
    """

    def __init__(
        self,
        num_classes: int,
        architecture: str = "efficientnet_b0",
        pretrained: bool = False,
        dropout_rate: float = 0.2,
    ):
        super().__init__()
        self.num_classes = num_classes
        self.architecture_name = architecture.lower()
        self.dropout_rate = dropout_rate

        # Instantiate backbone
        self.backbone, self.in_features = self._build_backbone(
            self.architecture_name, pretrained
        )

        # Build custom classification head
        self.classifier = nn.Sequential(
            nn.Dropout(p=self.dropout_rate),
            nn.Linear(self.in_features, self.num_classes),
        )

        # Replace classification head on backbone if needed
        self._attach_classifier()

    def _build_backbone(
        self, arch: str, pretrained: bool
    ) -> tuple[nn.Module, int]:
        weights = "DEFAULT" if pretrained else None

        if arch == "efficientnet_b0":
            model = models.efficientnet_b0(weights=weights)
            in_features = model.classifier[1].in_features
            model.classifier = nn.Identity()
            return model, in_features
        elif arch == "efficientnet_b1":
            model = models.efficientnet_b1(weights=weights)
            in_features = model.classifier[1].in_features
            model.classifier = nn.Identity()
            return model, in_features
        elif arch == "efficientnet_b2":
            model = models.efficientnet_b2(weights=weights)
            in_features = model.classifier[1].in_features
            model.classifier = nn.Identity()
            return model, in_features
        elif arch == "resnet18":
            model = models.resnet18(weights=weights)
            in_features = model.fc.in_features
            model.fc = nn.Identity()
            return model, in_features
        elif arch == "resnet34":
            model = models.resnet34(weights=weights)
            in_features = model.fc.in_features
            model.fc = nn.Identity()
            return model, in_features
        else:
            # Fallback to efficientnet_b0 if unknown
            model = models.efficientnet_b0(weights=weights)
            in_features = model.classifier[1].in_features
            model.classifier = nn.Identity()
            return model, in_features

    def _attach_classifier(self) -> None:
        # Classifier is handled as self.classifier on extracted features
        pass

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        features = self.backbone(x)
        logits = self.classifier(features)
        return logits

    def predict_proba(self, x: torch.Tensor) -> torch.Tensor:
        logits = self.forward(x)
        return F.softmax(logits, dim=-1)
