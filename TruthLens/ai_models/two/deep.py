import tensorflow as tf
import tensorflow_hub as hub
import os

# Assuming settings is not available in this file, let's set the path directly
MODEL_CACHE_PATH = "../../model_cache"  # Update this to match your settings.MODEL_CACHE_PATH
os.makedirs(MODEL_CACHE_PATH, exist_ok=True)

# Define the model path
model_path = os.path.join(MODEL_CACHE_PATH, "deepfake_model.h5")

# Use a pre-trained image classification model from TensorFlow Hub
mobilenet_url = "https://tfhub.dev/google/tf2-preview/mobilenet_v2/feature_vector/4"  # Feature vector version


def create_model():
    # Create the model using Keras Functional API instead of Sequential
    inputs = tf.keras.Input(shape=(256, 256, 3))

    # Use hub.KerasLayer as a layer in the functional API
    feature_extractor = hub.KerasLayer(mobilenet_url, trainable=False)(inputs)

    # Add dense layer for classification
    outputs = tf.keras.layers.Dense(1, activation='sigmoid')(feature_extractor)

    # Create the model
    model = tf.keras.Model(inputs=inputs, outputs=outputs)

    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )

    return model


# Create and save the model
try:
    model = create_model()
    model.save(model_path)
    print(f"Model saved to {model_path}")
except Exception as e:
    print(f"Error creating model: {e}")