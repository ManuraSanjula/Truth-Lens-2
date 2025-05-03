import os
import tensorflow as tf
from tf_keras.models import Sequential
from tf_keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tf_keras.preprocessing.image import ImageDataGenerator
from tf_keras.callbacks import ModelCheckpoint, EarlyStopping

# 1. Configure your dataset paths
DATASET_DIR = os.path.join('data', 'deepfake_dataset')  # Update this to your actual dataset path
TRAIN_DIR = os.path.join(DATASET_DIR, 'train')
VALIDATION_DIR = os.path.join(DATASET_DIR, 'validation')

# Create directories if they don't exist
os.makedirs(TRAIN_DIR, exist_ok=True)
os.makedirs(VALIDATION_DIR, exist_ok=True)


# 2. Verify dataset structure
# Your dataset should be organized like this:
# data/
#   deepfake_dataset/
#     train/
#       real/
#         image1.jpg, image2.jpg, ...
#       fake/
#         image1.jpg, image2.jpg, ...
#     validation/
#       real/
#         image1.jpg, image2.jpg, ...
#       fake/
#         image1.jpg, image2.jpg, ...

def create_model(input_shape=(256, 256, 3)):
    """Create a CNN model for deepfake detection"""
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        MaxPooling2D(2, 2),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D(2, 2),
        Conv2D(128, (3, 3), activation='relu'),
        MaxPooling2D(2, 2),
        Flatten(),
        Dense(512, activation='relu'),
        Dropout(0.5),
        Dense(1, activation='sigmoid')
    ])

    model.compile(optimizer='adam',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])
    return model


def train_model():
    # Setup data generators with augmentation
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

    validation_datagen = ImageDataGenerator(rescale=1. / 255)

    # Create generators
    train_generator = train_datagen.flow_from_directory(
        TRAIN_DIR,
        target_size=(256, 256),
        batch_size=32,
        class_mode='binary',
        classes=['real', 'fake']  # Assuming your folders are named 'real' and 'fake'
    )

    validation_generator = validation_datagen.flow_from_directory(
        VALIDATION_DIR,
        target_size=(256, 256),
        batch_size=32,
        class_mode='binary',
        classes=['real', 'fake']
    )

    # Create model
    model = create_model()

    # Callbacks
    checkpoint = ModelCheckpoint(
        'best_deepfake_model.h5',
        monitor='val_accuracy',
        save_best_only=True,
        mode='max'
    )

    early_stopping = EarlyStopping(
        monitor='val_loss',
        patience=5,
        restore_best_weights=True
    )

    # Train model
    history = model.fit(
        train_generator,
        steps_per_epoch=train_generator.samples // train_generator.batch_size,
        epochs=30,
        validation_data=validation_generator,
        validation_steps=validation_generator.samples // validation_generator.batch_size,
        callbacks=[checkpoint, early_stopping]
    )

    # Save final model
    model.save('deepfake_model.h5')
    print("Training complete. Model saved as 'deepfake_model.h5'")


if __name__ == '__main__':
    # Verify dataset exists
    if not os.path.exists(TRAIN_DIR) or not os.path.exists(VALIDATION_DIR):
        print(f"Error: Dataset directories not found at {DATASET_DIR}")
        print("Please ensure your dataset is organized as:")
        print("data/deepfake_dataset/train/real/")
        print("data/deepfake_dataset/train/fake/")
        print("data/deepfake_dataset/validation/real/")
        print("data/deepfake_dataset/validation/fake/")
    else:
        train_model()