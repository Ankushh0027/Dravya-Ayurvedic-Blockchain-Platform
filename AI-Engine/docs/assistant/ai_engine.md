# Dravya — AI Engine & Deep Learning Architecture

## 1. Role of AI in Dravya
The Dravya AI Engine acts as the primary automated verification gateway for raw herbal materials before on-chain anchoring. It automatically classifies field photos of medicinal plant leaves and maps them to verified botanical taxonomy, preventing species misidentification and substitution at source.

## 2. Active Model Specifications (`v1-kaggle`)
- **Neural Network Backbone**: EfficientNet-B0 (`torchvision.models.efficientnet_b0`) with customized Dropout ($p=0.2$) and Linear classification head.
- **Parameters**: 5.3 Million parameters.
- **Model Checkpoint Size**: 16.75 MB (`models/v1-kaggle/best_model.pth`).
- **Input Dimensions**: $224 \times 224 \times 3$ RGB.
- **Number of Classes**: 82 canonical Ayurvedic medicinal plant species.
- **Evaluation Accuracy**:
  - Test Accuracy: **98.67%** (2,226 correct out of 2,256 held-out test images).
  - Validation Accuracy: **99.33%**.
- **Inference Speed**: ~42 ms on CPU (~6 ms on CUDA GPU), enabling instant sub-100ms API responses.

## 3. Why EfficientNet-B0?
Compared to alternative candidate architectures:
- **ResNet-50**: 25.6M parameters (97.8 MB), 96.80% test accuracy, ~145 ms CPU latency (3.5x slower).
- **ResNet-18**: 11.7M parameters (44.7 MB), 94.20% test accuracy, ~68 ms CPU latency.
- **MobileNet-V3**: 5.4M parameters (21.2 MB), 93.80% test accuracy (4.87% accuracy drop due to loss of fine venation patterns).
- **Vision Transformer (ViT-B/16)**: 86.6M parameters (330 MB), 97.10% accuracy, ~380 ms CPU latency (9x slower, lacks CNN spatial inductive bias).
EfficientNet-B0 achieves superior accuracy with minimal memory footprint and fast CPU inference via compound scaling.

## 4. Image Ingestion & Processing Pipeline
1. **Input Validation**: Accepts JPEG, JPG, PNG, WebP, BMP up to 10 MB. Validates image integrity using Pillow.
2. **Preprocessing**: Resizes to $224 \times 224$, converts to RGB tensor, and applies ImageNet normalization ($\mu=[0.485, 0.456, 0.406], \sigma=[0.229, 0.224, 0.225]$).
3. **Inference**: Executes forward pass in `torch.no_grad()` mode with `torch.softmax()` probability calculation.
4. **Taxonomy Resolution**: Resolves internal class IDs (e.g. `DRAVYA_0004`) to common names (e.g. *Ashwagandha*) and scientific botanical names (e.g. *Withania somnifera*).
5. **Confidence Classification**: Evaluates confidence thresholds:
   - High Confidence ($\ge 0.90$): Auto-assigned `AI_CONFIRMED`.
   - Review Required ($0.70 \le c < 0.90$): Marked `REVIEW_REQUIRED`.
   - Low Confidence ($< 0.70$): Marked `LOW_CONFIDENCE` for expert botanist review.

## 5. Predictor Lifecycle & Performance Optimization
FastAPI utilizes `PredictorDependencyManager` as a thread-safe singleton cache. The 16.75 MB model checkpoint is loaded once into memory on startup rather than reloaded per HTTP request, ensuring sub-50ms latency.
