import os
import json
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau

# -------------------------------------------------------------------------
# 1. Hardware Check & Memory Configuration
# -------------------------------------------------------------------------
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    print(f"[INFO] GPU detected: {gpus}")
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)
else:
    print("[INFO] No GPU found or running on Windows CPU mode. Proceeding with CPU.")

# -------------------------------------------------------------------------
# 2. Dataset Path Configuration
# -------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset", "plantvillage dataset", "color")

if not os.path.exists(DATASET_DIR):
    raise FileNotFoundError(f"Directory not found: '{DATASET_DIR}'")

IMG_HEIGHT = 224
IMG_WIDTH = 224
IMG_SIZE = (IMG_HEIGHT, IMG_WIDTH)
BATCH_SIZE = 16  # Reduced to avoid memory spikes on CPU
EPOCHS = 10

# -------------------------------------------------------------------------
# 3. Data Loading & Streaming Pipeline (RAM-Safe)
# -------------------------------------------------------------------------
print("\n[INFO] Loading training dataset...")
train_ds = tf.keras.utils.image_dataset_from_directory(
    DATASET_DIR,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="categorical",
    shuffle=True
)

print("\n[INFO] Loading validation dataset...")
val_ds = tf.keras.utils.image_dataset_from_directory(
    DATASET_DIR,
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="categorical",
    shuffle=False
)

class_names = train_ds.class_names
num_classes = len(class_names)
print(f"\n[INFO] Total classes found: {num_classes}")

classes_file_path = os.path.join(BASE_DIR, "classes.json")
with open(classes_file_path, "w") as f:
    json.dump(class_names, f, indent=4)
print(f"[INFO] Saved class names to '{classes_file_path}'")

# REMOVED .cache() to prevent RAM overflow on 43k+ images
AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.prefetch(buffer_size=AUTOTUNE)

# -------------------------------------------------------------------------
# 4. Model Architecture (Transfer Learning via MobileNetV2)
# -------------------------------------------------------------------------
data_augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal_and_vertical"),
    layers.RandomRotation(0.2),
    layers.RandomZoom(0.15),
], name="data_augmentation")

base_model = MobileNetV2(
    input_shape=(IMG_HEIGHT, IMG_WIDTH, 3),
    include_top=False,
    weights="imagenet"
)
base_model.trainable = False  # Freeze pretrained backbone

inputs = layers.Input(shape=(IMG_HEIGHT, IMG_WIDTH, 3))
x = data_augmentation(inputs)
x = tf.keras.applications.mobilenet_v2.preprocess_input(x)
x = base_model(x, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.3)(x)
outputs = layers.Dense(num_classes, activation="softmax")(x)

model = models.Model(inputs, outputs, name="PlantDiseaseClassifier")

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# -------------------------------------------------------------------------
# 5. Training Callbacks & Fitting
# -------------------------------------------------------------------------
best_model_path = os.path.join(BASE_DIR, "best_plant_model.keras")

callbacks = [
    EarlyStopping(
        monitor="val_loss",
        patience=3,
        restore_best_weights=True,
        verbose=1
    ),
    ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.2,
        patience=2,
        min_lr=1e-6,
        verbose=1
    ),
    ModelCheckpoint(
        filepath=best_model_path,
        monitor="val_accuracy",
        save_best_only=True,
        verbose=1
    )
]

print("\n--- Starting Training ---")
history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS,
    callbacks=callbacks
)

# -------------------------------------------------------------------------
# 6. Export to TFLite (Optimized for Mobile Apps)
# -------------------------------------------------------------------------
print("\n[INFO] Converting trained model to TensorFlow Lite (.tflite)...")
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

tflite_path = os.path.join(BASE_DIR, "plant_disease_model.tflite")
with open(tflite_path, "wb") as f:
    f.write(tflite_model)

print("\n" + "=" * 55)
print("TRAINING & EXPORT COMPLETE!")
print(f"1. Saved Keras Model : {best_model_path}")
print(f"2. Saved TFLite Model: {tflite_path}")
print(f"3. Saved Class Labels: {classes_file_path}")
print("=" * 55)