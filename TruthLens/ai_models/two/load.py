import tensorflow as tf
import numpy as np
import os
from tf_keras.models import load_model

MODEL_CACHE_PATH = "../../model_cache"


def _load_model(self):
    """Load pre-trained deepfake detection model with fallbacks"""
    # Try different paths and formats
    model_path = os.path.join(MODEL_CACHE_PATH, "deepfake_model.h5")
    weights_path = os.path.join(MODEL_CACHE_PATH, "deepfake_weights.h5")
    saved_model_path = os.path.join(MODEL_CACHE_PATH, "deepfake_saved_model")

    # First try the standard H5 file
    if os.path.exists(model_path):
        try:
            return load_model(model_path)
        except Exception as e:
            print(f"Failed to load H5 model: {e}")

    # If that fails, try loading from SavedModel format
    if os.path.exists(saved_model_path):
        try:
            return load_model(saved_model_path)
        except Exception as e:
            print(f"Failed to load SavedModel: {e}")

    # If that fails, recreate the model and load weights
    if os.path.exists(weights_path):
        try:
            # Create a model with the same architecture
            model = tf.keras.Sequential([
                tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(256, 256, 3)),
                tf.keras.layers.MaxPooling2D(2, 2),
                tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
                tf.keras.layers.MaxPooling2D(2, 2),
                tf.keras.layers.Flatten(),
                tf.keras.layers.Dense(64, activation='relu'),
                tf.keras.layers.Dense(1, activation='sigmoid')
            ])

            model.compile(
                optimizer='adam',
                loss='binary_crossentropy',
                metrics=['accuracy']
            )

            # Load weights
            model.load_weights(weights_path)
            return model
        except Exception as e:
            print(f"Failed to load weights: {e}")

    raise FileNotFoundError("Deepfake model not found or could not be loaded")