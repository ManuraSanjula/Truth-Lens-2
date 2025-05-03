import tensorflow as tf
import numpy as np
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define paths
MODEL_CACHE_PATH = "../../model_cache"
os.makedirs(MODEL_CACHE_PATH, exist_ok=True)


def create_deepfake_detection_model(input_shape=(256, 256, 3)):
    """
    Create a CNN model for deepfake detection

    Args:
        input_shape: Shape of input images (height, width, channels)

    Returns:
        Compiled TensorFlow model
    """
    # Create a more sophisticated model than the emergency fallback
    inputs = tf.keras.layers.Input(shape=input_shape)

    # First convolutional block
    x = tf.keras.layers.Conv2D(64, (3, 3), padding='same', activation='relu')(inputs)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.MaxPooling2D(pool_size=(2, 2))(x)
    x = tf.keras.layers.Dropout(0.2)(x)

    # Second convolutional block
    x = tf.keras.layers.Conv2D(128, (3, 3), padding='same', activation='relu')(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.MaxPooling2D(pool_size=(2, 2))(x)
    x = tf.keras.layers.Dropout(0.3)(x)

    # Third convolutional block
    x = tf.keras.layers.Conv2D(256, (3, 3), padding='same', activation='relu')(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.MaxPooling2D(pool_size=(2, 2))(x)
    x = tf.keras.layers.Dropout(0.4)(x)

    # Fourth convolutional block with residual connection
    shortcut = x
    x = tf.keras.layers.Conv2D(256, (3, 3), padding='same', activation='relu')(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Conv2D(256, (3, 3), padding='same')(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.add([x, shortcut])
    x = tf.keras.layers.Activation('relu')(x)
    x = tf.keras.layers.MaxPooling2D(pool_size=(2, 2))(x)

    # Feature extraction
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dense(512, activation='relu')(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Dropout(0.5)(x)

    # Classification head
    outputs = tf.keras.layers.Dense(1, activation='sigmoid')(x)

    # Create model
    model = tf.keras.Model(inputs=inputs, outputs=outputs)

    # Compile model
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
        loss='binary_crossentropy',
        metrics=['accuracy', tf.keras.metrics.AUC(), tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
    )

    return model


def train_model(model, train_data, validation_data=None, epochs=10, batch_size=32):
    """
    Train the deepfake detection model

    Args:
        model: The model to train
        train_data: Training data generator or dataset
        validation_data: Validation data generator or dataset
        epochs: Number of training epochs
        batch_size: Batch size for training

    Returns:
        Training history
    """
    # Define callbacks
    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            filepath=os.path.join(MODEL_CACHE_PATH, 'deepfake_model.h5'),
            monitor='val_accuracy',
            save_best_only=True,
            mode='max'
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.2,
            patience=3,
            min_lr=1e-6
        )
    ]

    # Train the model
    history = model.fit(
        train_data,
        validation_data=validation_data,
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks
    )

    return history


def create_data_generators(train_dir, validation_dir, target_size=(256, 256), batch_size=32):
    """
    Create data generators for training and validation

    Args:
        train_dir: Directory containing training images
        validation_dir: Directory containing validation images
        target_size: Image dimensions to resize to
        batch_size: Batch size for generators

    Returns:
        train_generator, validation_generator
    """
    # Data augmentation for training
    train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
        rescale=1. / 255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )

    # Just rescaling for validation
    validation_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
        rescale=1. / 255
    )

    # Create generators
    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=target_size,
        batch_size=batch_size,
        class_mode='binary'
    )

    validation_generator = validation_datagen.flow_from_directory(
        validation_dir,
        target_size=target_size,
        batch_size=batch_size,
        class_mode='binary'
    )

    return train_generator, validation_generator


def save_model_multiple_formats(model):
    """
    Save the model in multiple formats for compatibility

    Args:
        model: The model to save
    """
    logger.info("Saving model in multiple formats...")

    # Save in Keras H5 format
    try:
        model_path = os.path.join(MODEL_CACHE_PATH, "deepfake_model.h5")
        model.save(model_path)
        logger.info(f"Model saved in H5 format to {model_path}")
    except Exception as e:
        logger.error(f"Failed to save in H5 format: {e}")

    # Save weights separately
    try:
        weights_path = os.path.join(MODEL_CACHE_PATH, "deepfake.weights.h5")
        model.save_weights(weights_path)
        logger.info(f"Model weights saved to {weights_path}")
    except Exception as e:
        logger.error(f"Failed to save weights: {e}")

    # Try Keras format (for newer TF versions)
    try:
        keras_path = os.path.join(MODEL_CACHE_PATH, "deepfake_model.keras")
        model.save(keras_path)
        logger.info(f"Model saved in Keras format to {keras_path}")
    except Exception as e:
        logger.error(f"Failed to save in Keras format: {e}")

    # Save in TensorFlow SavedModel format
    try:
        tf_path = os.path.join(MODEL_CACHE_PATH, "deepfake_saved_model")
        tf.saved_model.save(model, tf_path)
        logger.info(f"Model saved in TensorFlow format to {tf_path}")
    except Exception as e:
        logger.error(f"Failed to save in TensorFlow format: {e}")


def evaluate_model(model, test_data):
    """
    Evaluate the model on test data

    Args:
        model: The trained model
        test_data: Test data generator or dataset

    Returns:
        Evaluation metrics
    """
    logger.info("Evaluating model on test data...")
    results = model.evaluate(test_data)

    metrics_names = model.metrics_names
    evaluation_results = dict(zip(metrics_names, results))

    for metric, value in evaluation_results.items():
        logger.info(f"{metric}: {value:.4f}")

    return evaluation_results


def predict_sample(model, image_path):
    """
    Make a prediction on a sample image

    Args:
        model: The trained model
        image_path: Path to the image file

    Returns:
        Prediction result (probability of being fake)
    """
    # Load and preprocess the image
    img = tf.keras.preprocessing.image.load_img(image_path, target_size=(256, 256))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = img_array / 255.0  # Normalize
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension

    # Make prediction
    prediction = model.predict(img_array)[0][0]

    # Interpret result
    result = {
        "image_path": image_path,
        "deepfake_probability": float(prediction),
        "is_likely_fake": prediction > 0.5,
        "confidence": abs(prediction - 0.5) * 2  # Scale to 0-1 confidence
    }

    return result


if __name__ == "__main__":
    # Create the model
    model = create_deepfake_detection_model()
    model.summary()

    # If we have data paths, we could train the model
    # train_dir = "path/to/training/data"
    # validation_dir = "path/to/validation/data"
    # if os.path.exists(train_dir) and os.path.exists(validation_dir):
    #     train_generator, validation_generator = create_data_generators(train_dir, validation_dir)
    #     history = train_model(model, train_generator, validation_generator)

    # Otherwise, just save the untrained model for the DeepfakeDetector class to use
    save_model_multiple_formats(model)

    logger.info("Model creation completed successfully!")