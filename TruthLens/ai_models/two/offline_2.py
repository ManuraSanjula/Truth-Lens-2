import tensorflow as tf
import os

# Set paths
MODEL_CACHE_PATH = "../../model_cache"
os.makedirs(MODEL_CACHE_PATH, exist_ok=True)
model_path = os.path.join(MODEL_CACHE_PATH, "deepfake_model.h5")


def create_model():
    """Create a custom CNN model for deepfake detection"""
    model = tf.keras.Sequential([
        # Input layer
        tf.keras.layers.Input(shape=(256, 256, 3)),

        # Convolutional blocks
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling2D(2, 2),

        tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling2D(2, 2),

        tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling2D(2, 2),

        tf.keras.layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling2D(2, 2),

        # Flatten and dense layers
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(512, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(1, activation='sigmoid')  # Binary classification (real/fake)
    ])

    # Compile the model
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )

    return model


# Create and save the model
try:
    model = create_model()
    model.summary()  # Print model architecture
    model.save(model_path)
    print(f"Model saved to {model_path}")
except Exception as e:
    print(f"Error creating model: {e}")