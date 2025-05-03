import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os
import matplotlib.pyplot as plt


def create_deepfake_model(input_shape=(256, 256, 3)):
    """Create a CNN model for deepfake detection"""
    model = Sequential([
        # First convolutional block
        Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        MaxPooling2D(2, 2),

        # Second convolutional block
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D(2, 2),

        # Third convolutional block
        Conv2D(128, (3, 3), activation='relu'),
        MaxPooling2D(2, 2),

        # Fourth convolutional block
        Conv2D(128, (3, 3), activation='relu'),
        MaxPooling2D(2, 2),

        # Flatten the output and add dense layers
        Flatten(),
        Dropout(0.5),  # Helps prevent overfitting
        Dense(512, activation='relu'),
        Dropout(0.5),
        Dense(1, activation='sigmoid')  # Binary classification: real or fake
    ])

    # Compile the model
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )

    return model


def train_deepfake_model(train_dir, validation_dir, model_save_path, batch_size=32, epochs=20):
    """Train the deepfake detection model on a dataset of real and fake images"""

    # Data augmentation for training
    train_datagen = ImageDataGenerator(
        rescale=1. / 255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )

    # Only rescaling for validation
    validation_datagen = ImageDataGenerator(rescale=1. / 255)

    # Flow training images in batches using the generator
    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(256, 256),
        batch_size=batch_size,
        class_mode='binary'  # binary labels: 0 for real, 1 for fake
    )

    # Flow validation images in batches
    validation_generator = validation_datagen.flow_from_directory(
        validation_dir,
        target_size=(256, 256),
        batch_size=batch_size,
        class_mode='binary'
    )

    # Create the model
    model = create_deepfake_model()

    # Use early stopping to prevent overfitting
    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=3,
        restore_best_weights=True
    )

    # Train the model
    history = model.fit(
        train_generator,
        steps_per_epoch=train_generator.samples // batch_size,
        epochs=epochs,
        validation_data=validation_generator,
        validation_steps=validation_generator.samples // batch_size,
        callbacks=[early_stopping]
    )

    # Save the model
    model.save(model_save_path)

    # Return the training history and model
    return history, model


def plot_training_history(history):
    """Plot training & validation accuracy and loss"""
    acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']
    loss = history.history['loss']
    val_loss = history.history['val_loss']

    epochs_range = range(len(acc))

    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(epochs_range, acc, label='Training Accuracy')
    plt.plot(epochs_range, val_acc, label='Validation Accuracy')
    plt.legend()
    plt.title('Training and Validation Accuracy')

    plt.subplot(1, 2, 2)
    plt.plot(epochs_range, loss, label='Training Loss')
    plt.plot(epochs_range, val_loss, label='Validation Loss')
    plt.legend()
    plt.title('Training and Validation Loss')
    plt.show()


if __name__ == "__main__":
    # Define data directories
    train_dir = "path/to/training/data"  # Should have 'real' and 'fake' subdirectories
    validation_dir = "path/to/validation/data"  # Should have 'real' and 'fake' subdirectories
    model_save_path = "deepfake_model.h5"

    # Train the model
    history, model = train_deepfake_model(train_dir, validation_dir, model_save_path)

    # Plot the training history
    plot_training_history(history)

    # Evaluate the model on the validation set
    validation_datagen = ImageDataGenerator(rescale=1. / 255)
    validation_generator = validation_datagen.flow_from_directory(
        validation_dir,
        target_size=(256, 256),
        batch_size=32,
        class_mode='binary'
    )

    # Evaluate the model
    loss, accuracy = model.evaluate(validation_generator)
    print(f"Validation Accuracy: {accuracy:.4f}")
    print(f"Validation Loss: {loss:.4f}")