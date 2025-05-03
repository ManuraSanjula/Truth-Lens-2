import tensorflow as tf
import os

# Check TensorFlow version
print(f"TensorFlow version: {tf.__version__}")

# Set paths
MODEL_CACHE_PATH = "../../model_cache"
os.makedirs(MODEL_CACHE_PATH, exist_ok=True)
model_path = os.path.join(MODEL_CACHE_PATH, "deepfake_model.h5")


def create_model():
    """Create a simpler CNN model for deepfake detection with better compatibility"""
    # Don't use the Input layer directly - let Sequential create it implicitly
    model = tf.keras.Sequential()

    # First conv block
    model.add(tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same',
                                     input_shape=(256, 256, 3)))
    model.add(tf.keras.layers.MaxPooling2D((2, 2)))

    # Second conv block
    model.add(tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same'))
    model.add(tf.keras.layers.MaxPooling2D((2, 2)))

    # Third conv block
    model.add(tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same'))
    model.add(tf.keras.layers.MaxPooling2D((2, 2)))

    # Flatten and dense layers
    model.add(tf.keras.layers.Flatten())
    model.add(tf.keras.layers.Dense(128, activation='relu'))
    model.add(tf.keras.layers.Dropout(0.5))
    model.add(tf.keras.layers.Dense(1, activation='sigmoid'))

    # Compile model
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )

    return model


# Create and save the model
try:
    model = create_model()
    model.summary()

    # Save model in a compatible format
    model.save(model_path, save_format='h5')
    print(f"Model saved to {model_path}")

    # Verify model can be loaded
    test_load = tf.keras.models.load_model(model_path)
    print("Model successfully loaded as a test")
except Exception as e:
    print(f"Error creating/saving model: {e}")