import os
import cv2
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split


# Constants
IMG_SIZE = (256, 256)
DATASET_PATH = "dataset/"  # Folder with "real" and "fake" subfolders
MODEL_PATH = "deepfake_model.h5"


def load_data():
    X, y = [], []

    for label, folder in enumerate(["real", "fake"]):
        folder_path = os.path.join(DATASET_PATH, folder)
        for img_name in os.listdir(folder_path):
            img_path = os.path.join(folder_path, img_name)
            img = cv2.imread(img_path)
            img = cv2.resize(img, IMG_SIZE)
            X.append(img)
            y.append(label)  # 0=real, 1=fake

    X = np.array(X) / 255.0  # Normalize
    y = to_categorical(y, num_classes=2)  # One-hot encoding
    return train_test_split(X, y, test_size=0.2, random_state=42)


def build_model():
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(*IMG_SIZE, 3)),
        MaxPooling2D((2, 2)),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Flatten(),
        Dense(64, activation='relu'),
        Dense(2, activation='softmax')  # 2 classes: real/fake
    ])

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model


if __name__ == "__main__":
    X_train, X_test, y_train, y_test = load_data()
    model = build_model()
    model.fit(X_train, y_train, epochs=10, validation_data=(X_test, y_test))
    model.save(MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")