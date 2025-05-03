import tensorflow as tf
import os

# Set the path directly
MODEL_CACHE_PATH = "../../model_cache"  # Update this to match your settings.MODEL_CACHE_PATH
os.makedirs(MODEL_CACHE_PATH, exist_ok=True)

# Define the model path
model_path = os.path.join(MODEL_CACHE_PATH, "deepfake_model.h5")


def create_simple_model():
    """Create a simple CNN model for deepfake detection"""
    model = tf.keras.Sequential([
        # Input layer
        tf.keras.layers.Input(shape=(256, 256, 3)),

        # First convolutional block
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D(2, 2),

        # Second convolutional block
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D(2, 2),

        # Third convolutional block
        tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D(2, 2),

        # Flatten and dense layers
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(1, activation='sigmoid')  # Binary classification (real/fake)
    ])

    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )

    return model


# Create and save the model
try:
    model = create_simple_model()
    model.save(model_path)
    print(f"Model saved to {model_path}")
except Exception as e:
    print(f"Error creating model: {e}")