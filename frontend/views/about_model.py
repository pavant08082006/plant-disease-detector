"""
About AI Model & Technical Architecture View.
Provides academic transparency on deep learning architecture, dataset specs, and limitations.
"""

import json
from pathlib import Path
import streamlit as st
from backend.utils.constants import METADATA_PATH, CLASSES_PATH


def render_about_model():
    """Renders academic architecture documentation and model metadata."""
    st.title("🔬 About the Deep Learning Model")
    st.write(
        "Technical specifications, training hyperparameters, and architectural design of the "
        "convolutional neural network powering plant disease identification."
    )

    # Load metadata
    metadata = {}
    if METADATA_PATH.exists():
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            metadata = json.load(f)

    # Key Specifications Grid
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Neural Architecture", "MobileNetV2", "Transfer Learning")
    k2.metric("Total Classes", "38 Classes", "14 Crops")
    k3.metric("Input Tensor", "224 × 224 × 3", "RGB Channel")
    k4.metric("Total Parameters", "2.40 Million", "48k Trainable")

    st.markdown("---")

    # Architecture Breakdown
    c_arch, c_data = st.columns([1, 1])

    with c_arch:
        st.subheader("🧠 Model Architecture & Layers")
        st.markdown("""
        The disease classifier leverages **MobileNetV2** as a frozen feature extractor, followed by an agronomic classification head:
        
        1. **Input Layer:** `(224, 224, 3)` RGB leaf image.
        2. **Data Augmentation:** `RandomFlip`, `RandomRotation(0.2)`, `RandomZoom(0.15)`.
        3. **Normalization:** Embedded `preprocess_input` mapping pixel intensities $[0, 255] \to [-1, 1]$.
        4. **Backbone:** Pretrained ImageNet MobileNetV2 with inverted residual bottleneck blocks (`trainable=False`).
        5. **Pooling:** `GlobalAveragePooling2D` collapsing spatial dimensions to 1280 feature maps.
        6. **Regularization:** `Dropout(0.3)` mitigating overfitting.
        7. **Dense Head:** `Dense(38, activation='softmax')` producing categorical probability distributions.
        """)

    with c_data:
        st.subheader("📚 Dataset & Training Pipeline")
        st.markdown(f"""
        - **Dataset Source:** PlantVillage Color Benchmark Dataset.
        - **Total Dataset Size:** 54,305 labeled leaf photographs.
        - **Validation Split:** 20% holdout validation ({metadata.get('total_images', 54305) * 0.2:.0f} images).
        - **Optimization:** Adam Optimizer ($\text{{lr}} = 10^{{-3}}$) with `ReduceLROnPlateau` and `EarlyStopping`.
        - **Loss Criterion:** Categorical Cross-Entropy.
        - **Deployment Exports:** Keras v3 format (`.keras`) & quantized TensorFlow Lite (`.tflite`).
        """)

    st.markdown("---")

    # Academic Notice & Real-World Limitations
    st.subheader("⚠️ Engineering Limitations & Future Scope")
    st.warning(
        """
        **Real-World Transferability Notice:**  
        The classifier was trained on the laboratory-standardized **PlantVillage** dataset, where leaves were photographed 
        against uniform gray/black paper backgrounds under studio lighting. 
        
        In real agricultural environments, background soil clutter, insect damage, dust, overlapping leaves, and varying 
        sunlight angles can introduce domain shift. Future iterations will incorporate field-captured in-situ datasets 
        and bounding-box leaf segmentation models (YOLOv8 / Mask R-CNN) to enhance field robustness.
        """
    )

    # Class Directory Viewer
    with st.expander("📋 View All 38 Recognized Disease Classes", expanded=False):
        if CLASSES_PATH.exists():
            with open(CLASSES_PATH, "r", encoding="utf-8") as f:
                classes = json.load(f)
            col_a, col_b = st.columns(2)
            mid = len(classes) // 2
            with col_a:
                for c in classes[:mid]:
                    st.write(f"• `{c}`")
            with col_b:
                for c in classes[mid:]:
                    st.write(f"• `{c}`")

